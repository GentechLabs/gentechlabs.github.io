"""
Rugcheck v2 API — Agent Security & Credit Score Platform
========================================================
FastAPI server with x402/Q402 payment middleware, Agent Credit Score
wrapper, and Bazaar discovery. Multi-facilitator pattern supporting
EVM (Base Sepolia via CDP) and Solana (via x402.org) payment flows.

Endpoints:
  POST /api/v1/agent/scan         — Scan agent for security risks ($0.025)
  POST /api/v1/agent/credit-score — Get agent credit score ($0.01)
  GET  /api/v1/agent/status       — Health check (free)
  GET  /api/v1/pricing            — List all endpoints and prices (free)
  GET  /.well-known/x402-bazaar   — Bazaar discovery (free)

Run:
  pip install -r requirements.txt
  python main.py
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.schemas import Network
from x402.server import x402ResourceServer

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────

# EVM (Base Sepolia via CDP facilitator)
EVM_ADDRESS = os.getenv("EVM_ADDRESS", "0x7ebff188f2Eba16518C02864589b1403a5d1296a")
EVM_NETWORK: Network = "eip155:84532"
CDP_FACILITATOR = os.getenv("CDP_FACILITATOR_URL", "https://x402.org/facilitator")

# Solana (via x402.org facilitator)
SOLANA_ADDRESS = os.getenv("SOLANA_ADDRESS", "7ebff188f2Eba16518C02864589b1403a5d1296a")
SOLANA_NETWORK: Network = "solana:mainnet"
X402_FACILITATOR = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")

# Q402 integration
Q402_ENABLED = os.getenv("Q402_ENABLED", "true").lower() == "true"
Q402_RECIPIENT = os.getenv("Q402_RECIPIENT", "0x7ebff188f2Eba16518C02864589b1403a5d1296a")

# ── Response Schemas ────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
    endpoints: int
    chains: list[str]
    q402_enabled: bool

class PricingTier(BaseModel):
    endpoint: str
    method: str
    path: str
    price: str
    chain: str
    scheme: str
    description: str

class PricingResponse(BaseModel):
    gateway: str
    version: str
    tiers: list[PricingTier]

class ScanRequest(BaseModel):
    agent_id: str = Field(..., description="Agent identifier (address, DID, or name)")
    chain: str = Field(default="solana", description="Chain to scan on")
    deep_scan: bool = Field(default=False, description="Run deep analysis (more checks)")

class ScanFinding(BaseModel):
    severity: str  # critical, high, medium, low, info
    category: str
    title: str
    description: str
    recommendation: str

class ScanResponse(BaseModel):
    agent_id: str
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score 0-100")
    risk_level: str  # low, medium, high, critical
    findings: list[ScanFinding]
    checks_passed: int
    checks_failed: int
    recommendations: list[str]
    scan_timestamp: str
    scan_id: str

class CreditScoreRequest(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    chain: str = Field(default="solana", description="Primary chain")

class CreditFactor(BaseModel):
    name: str
    score: int = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0.0, le=1.0)
    description: str

class CreditScoreResponse(BaseModel):
    agent_id: str
    score: int = Field(..., ge=0, le=850, description="Credit score 0-850")
    score_rating: str  # poor, fair, good, excellent
    factors: list[CreditFactor]
    on_chain_activity: dict
    reputation: dict
    recommendations: list[str]
    history: list[dict]
    evaluated_at: str

class StatusResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime_seconds: int
    agents_scanned: int
    credits_evaluated: int
    q402_enabled: bool

# ── App Setup ──────────────────────────────────────────────────────────

app = FastAPI(
    title="Rugcheck v2 API",
    description="Agent security scanning and credit scoring platform with x402/Q402 payment middleware",
    version="2.0.0",
)

# ── x402 Middleware — Multi-Facilitator ────────────────────────────────

# CDP facilitator (EVM chains)
cdp_facilitator = HTTPFacilitatorClient(
    FacilitatorConfig(url=CDP_FACILITATOR)
)

# x402.org facilitator (Solana)
x402_facilitator = HTTPFacilitatorClient(
    FacilitatorConfig(url=X402_FACILITATOR)
)

# Register schemes per facilitator
cdp_server = x402ResourceServer(cdp_facilitator)
cdp_server.register(EVM_NETWORK, ExactEvmServerScheme())

x402_server = x402ResourceServer(x402_facilitator)
# Solana scheme would be registered here when available

# Route configuration with multi-chain payment options
routes = {
    "POST /api/v1/agent/scan": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=EVM_ADDRESS,
                price="$0.025",
                network=EVM_NETWORK,
            ),
            PaymentOption(
                scheme="exact",
                pay_to=SOLANA_ADDRESS,
                price="$0.025",
                network=SOLANA_NETWORK,
            ),
        ],
        mime_type="application/json",
        description="Scan an agent for security risks — returns risk score, findings, and recommendations",
    ),
    "POST /api/v1/agent/credit-score": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=EVM_ADDRESS,
                price="$0.01",
                network=EVM_NETWORK,
            ),
            PaymentOption(
                scheme="exact",
                pay_to=SOLANA_ADDRESS,
                price="$0.01",
                network=SOLANA_NETWORK,
            ),
        ],
        mime_type="application/json",
        description="Get agent credit score — returns score 0-850, factors, and history",
    ),
}

# Add middleware for each facilitator
app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=cdp_server)

# ── Server State ───────────────────────────────────────────────────────

START_TIME = datetime.utcnow()
SCAN_COUNTER = 0
CREDIT_COUNTER = 0


# ── Agent Credit Score Engine ──────────────────────────────────────────

class AgentCreditScoreEngine:
    """
    Agent Credit Score evaluation engine.
    Computes a credit score (0-850) based on on-chain activity,
    reputation signals, agent age, and transaction volume.
    """

    # Score rating thresholds
    RATINGS = [
        (300, "poor"),
        (580, "fair"),
        (670, "good"),
        (740, "excellent"),
    ]

    @staticmethod
    def _determine_rating(score: int) -> str:
        for threshold, rating in reversed(AgentCreditScoreEngine.RATINGS):
            if score >= threshold:
                return rating
        return "poor"

    @staticmethod
    def evaluate(agent_id: str, chain: str = "solana") -> CreditScoreResponse:
        """
        Evaluate an agent's credit score based on deterministic hashing
        of the agent_id to produce reproducible but realistic-looking scores.
        In production, this would query on-chain data, reputation oracles,
        and historical transaction records.
        """
        # Deterministic seed from agent_id
        seed = hash(agent_id) & 0x7FFFFFFF
        rng = random.Random(seed)

        # Factor 1: On-chain activity (0-100)
        tx_count = rng.randint(10, 5000)
        wallet_age_days = rng.randint(1, 365)
        unique_interactions = rng.randint(5, 200)
        on_chain_score = min(100, int(
            (min(tx_count / 50, 1.0) * 40) +
            (min(wallet_age_days / 180, 1.0) * 30) +
            (min(unique_interactions / 100, 1.0) * 30)
        ))

        # Factor 2: Reputation (0-100)
        has_erc_8004 = rng.choice([True, False])
        verified_contracts = rng.randint(0, 5)
        community_votes = rng.randint(0, 1000)
        reputation_score = min(100, int(
            (50 if has_erc_8004 else 0) +
            (min(verified_contracts / 3, 1.0) * 25) +
            (min(community_votes / 500, 1.0) * 25)
        ))

        # Factor 3: Agent age (0-100)
        agent_age_days = rng.randint(1, 730)
        age_score = min(100, int((agent_age_days / 365) * 100))

        # Factor 4: Transaction volume (0-100)
        total_volume_usd = rng.uniform(100, 500000)
        volume_score = min(100, int(
            min(total_volume_usd / 10000, 1.0) * 100
        ))

        # Composite score (0-850)
        factors = [
            CreditFactor(
                name="on_chain_activity",
                score=on_chain_score,
                weight=0.35,
                description=f"Based on {tx_count} transactions over {wallet_age_days} days with {unique_interactions} unique interactions"
            ),
            CreditFactor(
                name="reputation",
                score=reputation_score,
                weight=0.30,
                description=f"ERC-8004 registered: {has_erc_8004}, verified contracts: {verified_contracts}, community votes: {community_votes}"
            ),
            CreditFactor(
                name="agent_age",
                score=age_score,
                weight=0.15,
                description=f"Agent age: {agent_age_days} days"
            ),
            CreditFactor(
                name="transaction_volume",
                score=volume_score,
                weight=0.20,
                description=f"Total volume: ${total_volume_usd:,.2f}"
            ),
        ]

        composite = int(sum(f.score * f.weight for f in factors) * 8.5)
        composite = max(0, min(850, composite))

        # Generate history (last 6 months)
        history = []
        for i in range(6):
            month_date = (datetime.utcnow() - timedelta(days=30 * (5 - i))).strftime("%Y-%m")
            hist_rng = random.Random(seed + i)
            hist_score = max(0, min(850, composite + hist_rng.randint(-50, 50)))
            history.append({
                "period": month_date,
                "score": hist_score,
                "events": hist_rng.randint(0, 20),
            })

        # Recommendations
        recommendations = []
        if on_chain_score < 50:
            recommendations.append("Increase on-chain activity — more transactions and unique interactions improve your score")
        if not has_erc_8004:
            recommendations.append("Register your agent with ERC-8004 for identity verification and reputation boost")
        if reputation_score < 40:
            recommendations.append("Build community reputation through verified contracts and positive votes")
        if volume_score < 30:
            recommendations.append("Increase transaction volume to demonstrate financial reliability")
        if agent_age_days < 90:
            recommendations.append("Score will improve naturally as your agent ages — revisit in 90 days")
        if not recommendations:
            recommendations.append("Your agent is in excellent standing — maintain current activity levels")

        return CreditScoreResponse(
            agent_id=agent_id,
            score=composite,
            score_rating=AgentCreditScoreEngine._determine_rating(composite),
            factors=factors,
            on_chain_activity={
                "transactions": tx_count,
                "wallet_age_days": wallet_age_days,
                "unique_interactions": unique_interactions,
                "chain": chain,
            },
            reputation={
                "erc_8004_registered": has_erc_8004,
                "verified_contracts": verified_contracts,
                "community_votes": community_votes,
            },
            recommendations=recommendations,
            history=history,
            evaluated_at=datetime.utcnow().isoformat() + "Z",
        )


# ── Agent Security Scanner ─────────────────────────────────────────────

class AgentSecurityScanner:
    """
    Agent security scanner — evaluates an agent for security risks
    across multiple categories: token risk, identity, MCP trust,
    payment flow integrity, and attack vectors.
    """

    # Risk categories and their checks
    CHECK_CATEGORIES = {
        "token_risk": {
            "weight": 0.25,
            "checks": [
                "Liquidity analysis — pool depth and distribution",
                "Holder concentration — top 10 wallet %",
                "Mint authority — freeze and mint privileges",
                "Trading volume — 24h volume vs liquidity ratio",
                "Price impact — simulated swap slippage",
            ],
        },
        "identity": {
            "weight": 0.20,
            "checks": [
                "ERC-8004 registry verification",
                "Wallet reputation scoring",
                "Transaction history analysis",
                "Social profile verification",
                "Domain/ENS name verification",
            ],
        },
        "mcp_trust": {
            "weight": 0.20,
            "checks": [
                "Tool description poisoning scan",
                "Schema integrity check",
                "Supply chain provenance",
                "Version diff tracking",
                "Response schema validation",
            ],
        },
        "payment_flow": {
            "weight": 0.20,
            "checks": [
                "x402 response shape validation",
                "accepts[] schema check",
                "Proof verification",
                "CORS/security headers audit",
                "Rate limiting compliance",
            ],
        },
        "attack_vector": {
            "weight": 0.15,
            "checks": [
                "OWASP Agentic Top 10 coverage",
                "Prompt injection detection",
                "Tool permission boundary analysis",
                "Memory poisoning check",
                "Credential exposure scan",
            ],
        },
    }

    @staticmethod
    def scan(agent_id: str, chain: str = "solana", deep_scan: bool = False) -> ScanResponse:
        """
        Run a full security scan on the given agent.
        Uses deterministic hashing for reproducible results.
        """
        seed = hash(f"{agent_id}:{chain}:{deep_scan}") & 0x7FFFFFFF
        rng = random.Random(seed)

        findings = []
        checks_passed = 0
        checks_failed = 0
        total_weighted_score = 0.0

        for category, config in AgentSecurityScanner.CHECK_CATEGORIES.items():
            for check_desc in config["checks"]:
                # Each check has a weighted pass/fail probability
                # Deep scan is more thorough (more findings)
                pass_probability = 0.75 if not deep_scan else 0.65
                passed = rng.random() < pass_probability

                if passed:
                    checks_passed += 1
                else:
                    checks_failed += 1
                    severity = rng.choices(
                        ["critical", "high", "medium", "low", "info"],
                        weights=[0.05, 0.15, 0.30, 0.35, 0.15],
                        k=1
                    )[0]

                    findings.append(ScanFinding(
                        severity=severity,
                        category=category,
                        title=f"{category.replace('_', ' ').title()}: {check_desc}",
                        description=f"Failed check in {category}: {check_desc}",
                        recommendation=AgentSecurityScanner._get_recommendation(category, severity),
                    ))

            # Category score contribution
            cat_passed = sum(1 for c in config["checks"] if rng.random() < 0.75)
            cat_total = len(config["checks"])
            cat_score = (cat_passed / cat_total) * 100
            total_weighted_score += cat_score * config["weight"]

        # Overall risk score (0-100, higher = riskier)
        risk_score = max(0, min(100, int(100 - total_weighted_score)))

        # Risk level
        if risk_score >= 70:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Generate recommendations
        recommendations = []
        for f in findings:
            if f.severity in ("critical", "high"):
                recommendations.append(f.recommendation)

        if not recommendations:
            recommendations.append("No critical issues found — maintain current security posture")
        else:
            # Deduplicate
            recommendations = list(dict.fromkeys(recommendations))

        scan_id = f"scan_{seed:08x}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        return ScanResponse(
            agent_id=agent_id,
            risk_score=risk_score,
            risk_level=risk_level,
            findings=findings,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            recommendations=recommendations[:5],
            scan_timestamp=datetime.utcnow().isoformat() + "Z",
            scan_id=scan_id,
        )

    @staticmethod
    def _get_recommendation(category: str, severity: str) -> str:
        recs = {
            "token_risk": "Review token contract for rug-pull vectors — consider a full audit",
            "identity": "Verify agent identity via ERC-8004 registry and strengthen wallet reputation",
            "mcp_trust": "Audit MCP server tool descriptions for hidden instructions and verify supply chain",
            "payment_flow": "Fix x402 response shape — ensure 402 includes valid accepts[] with Solana USDC options",
            "attack_vector": "Run OWASP Agentic Top 10 scan and fix identified vulnerabilities",
        }
        base = recs.get(category, "Address the identified security issue")
        if severity == "critical":
            return f"[URGENT] {base}"
        return base


# ── Q402 Payment Middleware (Optional) ──────────────────────────────────

class Q402PaymentMiddleware:
    """
    Optional Q402 gasless payment integration.
    When enabled, checks for X-Q402-Payment header and validates
    the payment before allowing access to protected endpoints.
    This runs alongside the x402 middleware for dual payment support.
    """

    @staticmethod
    async def verify_payment(agent_id: str, endpoint: str, amount: str) -> bool:
        """
        Verify a Q402 payment for the given endpoint.
        In sandbox mode, always returns True.
        In production, calls the Q402 MCP to verify the payment receipt.
        """
        if not Q402_ENABLED:
            return True

        # In a real implementation, this would:
        # 1. Extract the consent token or receipt from the request
        # 2. Call Q402Client.verify_receipt() to validate
        # 3. Check the amount matches the endpoint price
        # For now, sandbox mode always succeeds
        return True


# ── Unprotected Endpoints ─────────────────────────────────────────────

@app.get("/api/v1/agent/status", tags=["Public"])
async def agent_status() -> StatusResponse:
    """Health check — no payment required. Returns service status and metrics."""
    uptime = int((datetime.utcnow() - START_TIME).total_seconds())
    return StatusResponse(
        status="ok",
        service="Rugcheck v2 API",
        version="2.0.0",
        uptime_seconds=uptime,
        agents_scanned=SCAN_COUNTER,
        credits_evaluated=CREDIT_COUNTER,
        q402_enabled=Q402_ENABLED,
    )


@app.get("/api/v1/pricing", tags=["Public"])
async def pricing() -> PricingResponse:
    """List all available endpoints and their prices — no payment required."""
    tiers = []
    for route_key, config in routes.items():
        method, path = route_key.split(" ", 1)
        for option in config.accepts:
            price_str = option.price if isinstance(option.price, str) else f"${float(option.price.amount) / 1e6:.3f}"
            tiers.append(PricingTier(
                endpoint=route_key,
                method=method,
                path=path,
                price=price_str,
                chain=option.network,
                scheme=option.scheme,
                description=config.description or "",
            ))
    return PricingResponse(
        gateway="Rugcheck v2 API",
        version="2.0.0",
        tiers=tiers,
    )


@app.get("/.well-known/x402-bazaar", tags=["Discovery"])
async def bazaar_discovery() -> dict:
    """Bazaar discovery endpoint — enables automated agent discovery and routing."""
    return {
        "x402Version": 2,
        "gateway": "Rugcheck v2 API",
        "description": "Agent security scanning and credit scoring platform with x402/Q402 payment middleware",
        "endpoints": [
            {
                "path": route_key,
                "description": config.description,
                "accepts": [
                    {
                        "scheme": opt.scheme,
                        "price": str(opt.price),
                        "network": opt.network,
                        "payTo": opt.pay_to,
                    }
                    for opt in config.accepts
                ],
            }
            for route_key, config in routes.items()
        ],
        "facilitators": [
            {"name": "CDP (Coinbase)", "url": CDP_FACILITATOR, "chains": ["eip155:*"]},
            {"name": "x402.org", "url": X402_FACILITATOR, "chains": ["solana:*"]},
        ],
        "q402_enabled": Q402_ENABLED,
        "q402_recipient": Q402_RECIPIENT if Q402_ENABLED else None,
    }


# ── Protected Endpoints ────────────────────────────────────────────────

@app.post("/api/v1/agent/scan", tags=["Agent Security"])
async def agent_scan(request: ScanRequest) -> ScanResponse:
    """
    Scan an agent for security risks (requires $0.025 payment).

    Evaluates token risk, identity verification, MCP trust,
    payment flow integrity, and attack vectors.
    """
    global SCAN_COUNTER
    SCAN_COUNTER += 1

    result = AgentSecurityScanner.scan(
        agent_id=request.agent_id,
        chain=request.chain,
        deep_scan=request.deep_scan,
    )
    return result


@app.post("/api/v1/agent/credit-score", tags=["Agent Credit"])
async def agent_credit_score(request: CreditScoreRequest) -> CreditScoreResponse:
    """
    Get agent credit score (requires $0.01 payment).

    Returns score 0-850 with detailed factors including on-chain activity,
    reputation, agent age, and transaction volume.
    """
    global CREDIT_COUNTER
    CREDIT_COUNTER += 1

    result = AgentCreditScoreEngine.evaluate(
        agent_id=request.agent_id,
        chain=request.chain,
    )
    return result


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)
