"""
DeFi Intelligence Risk Engine
Assesses agent portfolio risk for BNPL underwriting.
Uses: TVL trends, yield stability, protocol diversification, exposure risk.
"""

import json
import math
from typing import Optional
from dataclasses import dataclass, field

# ──────────────────────────────────────────────
#  Types
# ──────────────────────────────────────────────

@dataclass
class ProtocolPosition:
    name: str
    chain: str
    tvl_usdc: float
    tvl_trend_30d: float       # -1.0 to 1.0 (negative = shrinking)
    yield_apy: float            # current APY %
    yield_volatility: float     # 0.0 (stable) to 1.0 (wild)
    is_audited: bool = False
    has_insurance: bool = False

@dataclass
class AgentPortfolio:
    agent_id: str
    positions: list[ProtocolPosition] = field(default_factory=list)
    total_tvl: float = 0.0

    def __post_init__(self):
        self.total_tvl = sum(p.tvl_usdc for p in self.positions)


# ──────────────────────────────────────────────
#  Risk Engine
# ──────────────────────────────────────────────

class RiskEngine:
    """Assesses portfolio risk for BNPL underwriting."""

    RISK_SCORE_MIN = 0
    RISK_SCORE_MAX = 100  # 100 = lowest risk

    def assess(self, portfolio: AgentPortfolio) -> dict:
        """Full risk assessment."""
        if not portfolio.positions:
            return self._empty_assessment(portfolio.agent_id)

        scores = {
            "tvl_health": self._tvl_health(portfolio),
            "yield_stability": self._yield_stability(portfolio),
            "diversification": self._diversification(portfolio),
            "exposure_risk": self._exposure_risk(portfolio),
            "audit_quality": self._audit_quality(portfolio),
        }

        composite = int(sum(scores.values()) / len(scores))
        composite = max(self.RISK_SCORE_MIN, min(self.RISK_SCORE_MAX, composite))

        return {
            "agent_id": portfolio.agent_id,
            "composite_risk_score": composite,
            "risk_tier": self._tier(composite),
            "factors": scores,
            "position_count": len(portfolio.positions),
            "total_tvl_usdc": round(portfolio.total_tvl, 2),
            "max_recommended_credit": self._recommended_credit(composite, portfolio.total_tvl),
        }

    def _tvl_health(self, portfolio: AgentPortfolio) -> int:
        """Score TVL health (0-100)."""
        if portfolio.total_tvl >= 50_000:
            base = 80
        elif portfolio.total_tvl >= 10_000:
            base = 60
        elif portfolio.total_tvl >= 1_000:
            base = 40
        else:
            base = 20

        # Trend adjustment
        avg_trend = sum(p.tvl_trend_30d for p in portfolio.positions) / len(portfolio.positions)
        if avg_trend > 0.1:
            base += 15
        elif avg_trend < -0.1:
            base -= 20

        return max(0, min(100, base))

    def _yield_stability(self, portfolio: AgentPortfolio) -> int:
        """Score yield stability (0-100)."""
        if not portfolio.positions:
            return 0

        avg_volatility = sum(p.yield_volatility for p in portfolio.positions) / len(portfolio.positions)

        if avg_volatility <= 0.2:
            return 80
        elif avg_volatility <= 0.4:
            return 60
        elif avg_volatility <= 0.6:
            return 40
        else:
            return 20

    def _diversification(self, portfolio: AgentPortfolio) -> int:
        """Score protocol diversification (0-100)."""
        protocols = len(set(p.name for p in portfolio.positions))
        chains = len(set(p.chain for p in portfolio.positions))

        score = 0
        if protocols >= 5:
            score += 50
        elif protocols >= 3:
            score += 30
        else:
            score += 10

        if chains >= 3:
            score += 50
        elif chains >= 2:
            score += 30
        else:
            score += 10

        return score

    def _exposure_risk(self, portfolio: AgentPortfolio) -> int:
        """Score single-protocol exposure risk (0-100)."""
        if not portfolio.positions or portfolio.total_tvl == 0:
            return 50

        # Find largest position as % of total
        max_share = max(p.tvl_usdc for p in portfolio.positions) / portfolio.total_tvl

        if max_share <= 0.3:
            return 80
        elif max_share <= 0.5:
            return 60
        elif max_share <= 0.7:
            return 40
        else:
            return 20

    def _audit_quality(self, portfolio: AgentPortfolio) -> int:
        """Score audit/insurance quality (0-100)."""
        if not portfolio.positions:
            return 0

        audited = sum(1 for p in portfolio.positions if p.is_audited)
        insured = sum(1 for p in portfolio.positions if p.has_insurance)
        total = len(portfolio.positions)

        score = 0
        if audited / total >= 0.8:
            score += 50
        elif audited / total >= 0.5:
            score += 30
        else:
            score += 10

        if insured / total >= 0.5:
            score += 50
        elif insured / total >= 0.2:
            score += 30
        else:
            score += 10

        return score

    def _tier(self, score: int) -> str:
        if score >= 80:
            return "low-risk"
        elif score >= 50:
            return "medium-risk"
        else:
            return "high-risk"

    def _recommended_credit(self, risk_score: int, tvl: float) -> float:
        """Recommend max credit based on risk score and TVL."""
        factor = risk_score / 100.0  # 0.0 to 1.0
        return round(tvl * factor * 0.5, 2)  # 50% of risk-adjusted TVL

    def _empty_assessment(self, agent_id: str) -> dict:
        return {
            "agent_id": agent_id,
            "composite_risk_score": 0,
            "risk_tier": "unknown",
            "factors": {},
            "position_count": 0,
            "total_tvl_usdc": 0.0,
            "max_recommended_credit": 0.0,
            "error": "No positions to assess",
        }


# ──────────────────────────────────────────────
#  API Handler
# ──────────────────────────────────────────────

engine = RiskEngine()


def handle_risk_request(body: dict) -> dict:
    """Handle a risk assessment request."""
    try:
        positions = []
        for p in body.get("positions", []):
            positions.append(ProtocolPosition(
                name=p.get("name", ""),
                chain=p.get("chain", ""),
                tvl_usdc=p.get("tvl_usdc", 0.0),
                tvl_trend_30d=p.get("tvl_trend_30d", 0.0),
                yield_apy=p.get("yield_apy", 0.0),
                yield_volatility=p.get("yield_volatility", 0.5),
                is_audited=p.get("is_audited", False),
                has_insurance=p.get("has_insurance", False),
            ))

        portfolio = AgentPortfolio(
            agent_id=body.get("agent_id", ""),
            positions=positions,
        )

        return engine.assess(portfolio)
    except Exception as e:
        return {"error": str(e)}


# ──────────────────────────────────────────────
#  CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test cases
        test_portfolios = [
            AgentPortfolio("whale-001", [
                ProtocolPosition("Aave", "ethereum", 20000, 0.05, 4.5, 0.15, True, True),
                ProtocolPosition("Compound", "ethereum", 15000, 0.08, 3.8, 0.1, True, True),
                ProtocolPosition("Uniswap", "arbitrum", 10000, 0.12, 8.2, 0.3, True, False),
                ProtocolPosition("Curve", "base", 8000, -0.02, 5.1, 0.2, True, True),
                ProtocolPosition("Aerodrome", "base", 5000, 0.15, 12.0, 0.4, False, False),
            ]),
            AgentPortfolio("degen-002", [
                ProtocolPosition("MemeSwap", "base", 500, -0.3, 50.0, 0.9, False, False),
            ]),
            AgentPortfolio("balanced-003", [
                ProtocolPosition("Aave", "ethereum", 5000, 0.03, 4.0, 0.15, True, True),
                ProtocolPosition("Curve", "arbitrum", 3000, 0.01, 3.5, 0.1, True, True),
            ]),
        ]

        for p in test_portfolios:
            result = engine.assess(p)
            print(f"\n{p.agent_id}:")
            print(f"  Risk Score: {result['composite_risk_score']}/100 ({result['risk_tier']})")
            print(f"  TVL: ${result['total_tvl_usdc']:,.2f}")
            print(f"  Max Credit: ${result['max_recommended_credit']:,.2f}")
            print(f"  Factors: {result['factors']}")
    else:
        body = json.loads(sys.stdin.read())
        result = handle_risk_request(body)
        print(json.dumps(result, indent=2))
