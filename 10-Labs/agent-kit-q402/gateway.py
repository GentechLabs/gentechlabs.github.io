"""
Agent Kit × Q402 Payment Gateway

The unified middleware that ties payment_module.py (spending) and
revenue_module.py (receiving) into a single agent-callable gateway.

New in v2: Enforcement + Audit Trail integration
- Enforcement: identity + policy checks BEFORE settlement
- Audit Trail: immutable receipt verification AFTER settlement

This is the x402 commerce layer:
- Agents pay for API access via Q402
- Your APIs verify payment receipts before serving
- Everything gets an audit trail
- Policy enforcement at every step

Architecture:
    Agent A  →  Enforcement  →  Q402 Payment  →  Trust Receipt  →  Audit Trail  →  API Response
                                  ↕                              ↕
                             Policy Check                  Receipt Verify
                             Identity Check                Immutable Log
                             Rate Limiting                 Compliance Query

Usage:
    from gateway import AgentPaymentGateway

    gateway = AgentPaymentGateway(config_path="config.yaml")

    # --- SELLING (revenue side) ---
    # Register your API for sale
    gateway.register_api(
        path="/v1/score/{mint}",
        price_usd=0.01,
        description="Token risk scoring"
    )

    # Verify incoming payment + serve (includes enforcement + audit)
    result = gateway.handle_request(
        receipt_id="rct_abc123",
        endpoint="/v1/score",
        payer="0x1234"
    )

    # --- BUYING (spending side) ---
    # Check if you can afford an API call (includes enforcement)
    can_afford = gateway.check_budget("/v1/score", 0.01)

    # Format payment command for agent to execute
    cmd = gateway.pay_for_api(
        endpoint="/v1/score",
        provider="0xabcd",
        amount=0.01
    )

    # --- REPORTING ---
    report = gateway.daily_summary()

    # --- AUDIT ---
    audit_entries = gateway.query_audit(payer="0x1234")
    receipt_status = gateway.check_receipt("rct_abc123")
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from payment_module import AgentPayment, PaymentPolicy
from revenue_module import AgentRevenue
from audit_trail import AuditTrail
from enforcement import EnforcementEngine, EnforcementPolicy


@dataclass
class APIRoute:
    """A registered API route with pricing."""
    path: str
    price_usd: float
    description: str
    provider: str  # address receiving payment
    chain: str = "base"
    token: str = "USDC"
    active: bool = True
    rate_limit_per_min: int = 60


class AgentPaymentGateway:
    """
    Unified payment gateway for agent-to-agent commerce.

    Combines:
    - Payment validation + policy enforcement (spending)
    - Receipt verification + revenue tracking (receiving)
    - Budget management
    - Audit trail (immutable settlement log)
    - Enforcement (identity + policy checks before settlement)

    The full flow:
    1. Agent requests to pay → enforcement checks identity, policy, limits
    2. If allowed → Q402 settlement happens
    3. Trust Receipt comes back → recorded to audit trail
    4. Audit trail verifies receipt format and logs immutably
    """

    def __init__(self, config_path: Optional[str] = None,
                 enable_enforcement: bool = True,
                 enable_audit_trail: bool = True):
        self.base_dir = Path(os.environ.get(
            "AGENT_KIT_AUDIT_DIR",
            os.path.expanduser("~/.hermes/profiles/gentech/audit")
        ))
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Initialize spending + revenue modules
        self.spending = AgentPayment()
        self.revenue = AgentRevenue()

        # Initialize enforcement engine
        self.enforcement = None
        if enable_enforcement:
            self.enforcement = EnforcementEngine(
                audit_dir=str(self.base_dir / "enforcement")
            )

        # Initialize audit trail
        self.audit_trail = None
        if enable_audit_trail:
            self.audit_trail = AuditTrail(
                audit_dir=str(self.base_dir / "trail")
            )

        # API routes registry
        self.routes_file = self.base_dir / "api_routes.json"
        self.routes: dict[str, APIRoute] = self._load_routes()

        # Gateway stats
        self.stats_file = self.base_dir / "gateway_stats.json"
        self.stats = self._load_stats()

        if config_path:
            self._load_config(config_path)

    def _load_config(self, path: str):
        """Load gateway config."""
        try:
            import yaml
            with open(path) as f:
                cfg = yaml.safe_load(f)

            if "routes" in cfg:
                for route_data in cfg["routes"]:
                    route = APIRoute(**route_data)
                    self.routes[route.path] = route
                self._save_routes()

            if "spending" in cfg:
                sp = cfg["spending"]
                if "daily_limit_usd" in sp:
                    self.spending.policy.daily_limit_usd = sp["daily_limit_usd"]
                if "per_tx_limit_usd" in sp:
                    self.spending.policy.per_tx_limit_usd = sp["per_tx_limit_usd"]
        except Exception as e:
            print(f"Warning: Could not load config: {e}")

    def _load_routes(self) -> dict[str, APIRoute]:
        if self.routes_file.exists():
            with open(self.routes_file) as f:
                data = json.load(f)
            return {k: APIRoute(**v) for k, v in data.items()}
        return {}

    def _save_routes(self):
        with open(self.routes_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.routes.items()}, f, indent=2)

    def _load_stats(self) -> dict:
        if self.stats_file.exists():
            with open(self.stats_file) as f:
                return json.load(f)
        return {
            "total_revenue_usd": 0.0,
            "total_spend_usd": 0.0,
            "total_requests_served": 0,
            "total_api_calls_made": 0,
            "start_date": datetime.now(timezone.utc).isoformat(),
        }

    def _save_stats(self):
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)

    # === ENFORCEMENT ===

    def register_agent(self, address: str, chain: str = "base",
                       credit_score: int = 0, reputation: float = 0.0) -> Optional[dict]:
        """Register an agent identity for enforcement."""
        if not self.enforcement:
            return None
        agent = self.enforcement.register_agent(address, chain, credit_score, reputation)
        return asdict(agent)

    def enforce_payment(self, agent_id: str, amount: float,
                        action: str = "pay", chain: str = "base",
                        token: str = "USDC", provider: str = "",
                        endpoint: str = "") -> dict:
        """
        Run enforcement checks before a payment.
        Returns {allowed, reason, checks_passed, checks_failed}
        """
        if not self.enforcement:
            return {"allowed": True, "reason": "Enforcement disabled", "checks_passed": [], "checks_failed": []}

        return self.enforcement.enforce_before_settlement(
            agent_id=agent_id,
            action=action,
            amount=amount,
            chain=chain,
            token=token,
            provider=provider,
            endpoint=endpoint,
        )

    # === REVENUE (selling APIs) ===

    def register_api(self, path: str, price_usd: float, description: str = "",
                     provider: str = "", chain: str = "base", token: str = "USDC") -> dict:
        """Register an API endpoint for sale to other agents."""
        route = APIRoute(
            path=path,
            price_usd=price_usd,
            description=description,
            provider=provider or os.environ.get("AGENT_ADDRESS", "0x0000"),
            chain=chain,
            token=token,
        )
        self.routes[path] = route
        self._save_routes()

        # Also register in revenue module
        self.revenue.register_endpoint(path, price_usd, description)

        return {
            "registered": True,
            "path": path,
            "price_usd": price_usd,
            "chain": chain,
            "token": token,
        }

    def handle_request(self, receipt_id: str, endpoint: str,
                       payer: str = "unknown") -> dict:
        """
        Handle an incoming API request with payment verification.

        Returns:
            {allowed: bool, reason: str, record_id: str}

        Flow:
            1. Check endpoint exists and is active
            2. Verify payment receipt (double-spend check)
            3. Check rate limit
            4. Log revenue
            5. Record to audit trail (if enabled)
        """
        # Check endpoint exists
        if endpoint not in self.routes:
            return {"allowed": False, "reason": f"Unknown endpoint: {endpoint}"}

        route = self.routes[endpoint]
        if not route.active:
            return {"allowed": False, "reason": f"Endpoint {endpoint} is inactive"}

        # Rate limit check
        if not self.revenue.check_rate_limit(payer, endpoint, route.rate_limit_per_min):
            return {"allowed": False, "reason": "Rate limit exceeded"}

        # Verify payment
        result = self.revenue.verify_payment(
            receipt_id=receipt_id,
            expected_amount=route.price_usd,
            endpoint=endpoint,
            payer=payer,
        )

        if result["verified"]:
            self.stats["total_requests_served"] += 1
            self._save_stats()

            # Record to audit trail
            if self.audit_trail:
                self.audit_trail.record_settlement(
                    payment_id=f"api_{receipt_id}",
                    receipt_id=receipt_id,
                    receipt_data={
                        "chain": route.chain,
                        "amount": route.price_usd,
                        "token": route.token,
                    },
                    chain=route.chain,
                    amount=route.price_usd,
                    token=route.token,
                    payer=payer,
                    provider=route.provider,
                    endpoint=endpoint,
                    memo=f"API request: {endpoint}",
                )

        return {
            "allowed": result["verified"],
            "reason": result["reason"],
            "record_id": result.get("record_id"),
            "endpoint": endpoint,
            "price_usd": route.price_usd,
        }

    # === SPENDING (buying APIs) ===

    def check_budget(self, endpoint: str, amount: float,
                     agent_id: str = "") -> dict:
        """Check if you can afford an API call (includes enforcement)."""
        route = self.routes.get(endpoint)
        if route:
            amount = route.price_usd

        # Run enforcement if agent_id provided
        enforcement_result = None
        if agent_id and self.enforcement:
            enforcement_result = self.enforce_payment(
                agent_id=agent_id, amount=amount, endpoint=endpoint
            )

        check = self.spending.validate(
            chain="base", token="USDC",
            to="0x0000",  # placeholder
            amount=amount, memo=f"API call: {endpoint}"
        )

        result = {
            "affordable": check["approved"],
            "amount_usd": amount,
            "daily_remaining": self.spending.policy.daily_limit_usd - self.spending.daily_total,
            "reason": check["reason"],
        }

        if enforcement_result:
            result["enforcement"] = {
                "allowed": enforcement_result["allowed"],
                "reason": enforcement_result["reason"],
            }
            result["affordable"] = check["approved"] and enforcement_result["allowed"]

        return result

    def pay_for_api(self, endpoint: str, provider: str, amount: float,
                    chain: str = "base", token: str = "USDC",
                    agent_id: str = "") -> dict:
        """
        Format a payment command for buying API access.
        Includes enforcement check if agent_id is provided.
        """
        # Enforcement check
        if agent_id and self.enforcement:
            enforcement = self.enforce_payment(
                agent_id=agent_id, amount=amount,
                action="pay", chain=chain, token=token,
                provider=provider, endpoint=endpoint,
            )
            if not enforcement["allowed"]:
                return {
                    "valid": False,
                    "command": None,
                    "amount_usd": amount,
                    "reason": f"Enforcement blocked: {enforcement['reason']}",
                    "enforcement": enforcement,
                }

        check = self.spending.validate(chain, token, provider, amount, f"API: {endpoint}")

        if check["approved"]:
            cmd = self.spending.format_pay_command(chain, token, provider, amount, f"API: {endpoint}")
            return {
                "valid": True,
                "command": cmd,
                "amount_usd": amount,
                "reason": check["reason"],
            }
        else:
            return {
                "valid": False,
                "command": None,
                "amount_usd": amount,
                "reason": check["reason"],
            }

    def record_settlement(self, payment_id: str, receipt_id: str,
                          receipt_data: dict, chain: str, amount: float,
                          payer: str, provider: str, endpoint: str,
                          token: str = "USDC", memo: str = "") -> Optional[dict]:
        """
        Record a Q402 settlement to the audit trail.
        Call this after Q402 confirms settlement.
        """
        if not self.audit_trail:
            return None

        entry = self.audit_trail.record_settlement(
            payment_id=payment_id,
            receipt_id=receipt_id,
            receipt_data=receipt_data,
            chain=chain,
            amount=amount,
            token=token,
            payer=payer,
            provider=provider,
            endpoint=endpoint,
            memo=memo,
        )
        return asdict(entry)

    # === AUDIT QUERIES ===

    def query_audit(self, payer: Optional[str] = None,
                    provider: Optional[str] = None,
                    endpoint: Optional[str] = None,
                    date: Optional[str] = None,
                    limit: int = 50) -> list[dict]:
        """Query the audit trail."""
        if not self.audit_trail:
            return []
        return self.audit_trail.query(
            payer=payer, provider=provider,
            endpoint=endpoint, date=date, limit=limit,
        )

    def check_receipt(self, receipt_id: str) -> Optional[dict]:
        """Check if a receipt has been recorded in the audit trail."""
        if not self.audit_trail:
            return None
        return self.audit_trail.get_receipt_status(receipt_id)

    # === REPORTING ===

    def daily_summary(self) -> dict:
        """Combined daily summary of spending + revenue + audit + enforcement."""
        spending = self.spending.get_daily_summary()
        revenue = self.revenue.daily_report()

        summary = {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "spending": spending,
            "revenue": revenue,
            "net": revenue["total_revenue"] - spending["total_spent"],
            "apis_registered": len(self.routes),
            "cumulative": {
                "total_revenue_usd": self.stats["total_revenue_usd"],
                "total_spend_usd": self.stats["total_spend_usd"],
                "requests_served": self.stats["total_requests_served"],
                "api_calls_made": self.stats["total_api_calls_made"],
            },
        }

        # Add audit trail summary
        if self.audit_trail:
            summary["audit"] = self.audit_trail.get_daily_summary()

        # Add enforcement summary
        if self.enforcement:
            summary["enforcement"] = self.enforcement.get_daily_summary()

        return summary

    def list_apis(self) -> list[dict]:
        """List all registered APIs with pricing."""
        return [asdict(route) for route in self.routes.values()]
