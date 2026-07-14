"""
ERC-8004 Credit Scoring API
Maps on-chain agent reputation to a credit score (300-850).
Uses: payment history, portfolio health, age, ERC-8004 registration count.
"""

import json
import os
from typing import Optional
from datetime import datetime, timezone

# ──────────────────────────────────────────────
#  Scoring Constants
# ──────────────────────────────────────────────

BASE_SCORE = 400
MAX_SCORE = 850

# Per-factor weights
PAYMENT_ON_TIME = 8       # per on-time payment
PAYMENT_DEFAULT = -25      # per default
PORTFOLIO_HEALTH_MAX = 150 # max contribution from portfolio
AGE_PER_MONTH = 15         # per month of activity (capped at 120)
REPUTATION_MULTIPLIER = 3  # per ERC-8004 registration count

# ──────────────────────────────────────────────
#  Types
# ──────────────────────────────────────────────

class AgentProfile:
    """On-chain agent data for credit scoring."""

    def __init__(
        self,
        agent_id: str,
        registration_count: int = 0,
        months_active: int = 0,
        on_time_payments: int = 0,
        defaults: int = 0,
        portfolio_tvl: float = 0.0,
        tvl_trend_30d: float = 0.0,  # positive = growing
        yield_stability: float = 0.5,  # 0.0 (volatile) to 1.0 (stable)
        protocol_count: int = 1,
    ):
        self.agent_id = agent_id
        self.registration_count = registration_count
        self.months_active = months_active
        self.on_time_payments = on_time_payments
        self.defaults = defaults
        self.portfolio_tvl = portfolio_tvl
        self.tvl_trend_30d = tvl_trend_30d
        self.yield_stability = yield_stability
        self.protocol_count = protocol_count


# ──────────────────────────────────────────────
#  Scoring Engine
# ──────────────────────────────────────────────

class CreditScorer:
    """Calculates credit scores from on-chain agent data."""

    def score(self, profile: AgentProfile) -> int:
        """Compute credit score (300-850)."""
        score = BASE_SCORE

        # 1. Payment history
        score += profile.on_time_payments * PAYMENT_ON_TIME
        score += profile.defaults * PAYMENT_DEFAULT

        # 2. Portfolio health (0-100)
        health = self._portfolio_health(profile)
        score += health

        # 3. Age factor (capped at 120)
        age_points = min(profile.months_active * AGE_PER_MONTH, 120)
        score += age_points

        # 4. Reputation multiplier
        score += profile.registration_count * REPUTATION_MULTIPLIER

        return max(BASE_SCORE, min(MAX_SCORE, score))

    def _portfolio_health(self, profile: AgentProfile) -> int:
        """Calculate portfolio health score (0-150)."""
        health = 0

        # TVL: ≥$50K = +80, ≥$10K = +60, ≥$1K = +30, <$1K = -10
        if profile.portfolio_tvl >= 50_000:
            health += 80
        elif profile.portfolio_tvl >= 10_000:
            health += 60
        elif profile.portfolio_tvl >= 1_000:
            health += 30
        else:
            health -= 10

        # TVL trend (30d): Growing = +30, Shrinking = -30
        if profile.tvl_trend_30d > 0.05:
            health += 30
        elif profile.tvl_trend_30d < -0.05:
            health -= 30

        # Yield stability: Consistent = +20, Volatile = -10
        if profile.yield_stability >= 0.7:
            health += 20
        elif profile.yield_stability < 0.3:
            health -= 10

        # Protocol diversification: 5+ = +30, 3-4 = +15, 1-2 = -10
        if profile.protocol_count >= 5:
            health += 30
        elif profile.protocol_count >= 3:
            health += 15
        else:
            health -= 10

        return max(0, min(150, health))

    def risk_tier(self, score: int) -> str:
        """Map score to risk tier."""
        if score >= 750:
            return "prime"
        elif score >= 650:
            return "near-prime"
        elif score >= 500:
            return "subprime"
        else:
            return "deep-subprime"

    def max_credit(self, score: int, collateral: float = 0.0) -> float:
        """Maximum credit line based on score + optional collateral."""
        base = 0.0
        if score >= 750:
            base = 10_000
        elif score >= 650:
            base = 5_000
        elif score >= 500:
            base = 1_000
        else:
            base = 100

        # Collateral multiplier (up to 2x)
        collateral_factor = 1.0 + min(collateral / base, 1.0) if base > 0 else 1.0
        return base * collateral_factor


# ──────────────────────────────────────────────
#  API Handler (for Workers deployment)
# ──────────────────────────────────────────────

scorer = CreditScorer()


def handle_score_request(body: dict) -> dict:
    """Handle a credit score request."""
    try:
        profile = AgentProfile(
            agent_id=body.get("agent_id", ""),
            registration_count=body.get("registration_count", 0),
            months_active=body.get("months_active", 0),
            on_time_payments=body.get("on_time_payments", 0),
            defaults=body.get("defaults", 0),
            portfolio_tvl=body.get("portfolio_tvl", 0.0),
            tvl_trend_30d=body.get("tvl_trend_30d", 0.0),
            yield_stability=body.get("yield_stability", 0.5),
            protocol_count=body.get("protocol_count", 1),
        )

        score = scorer.score(profile)
        tier = scorer.risk_tier(score)
        max_credit = scorer.max_credit(score, body.get("collateral", 0.0))

        return {
            "agent_id": profile.agent_id,
            "credit_score": score,
            "risk_tier": tier,
            "max_credit_usdc": round(max_credit, 2),
            "factors": {
                "payment_history": profile.on_time_payments * PAYMENT_ON_TIME + profile.defaults * PAYMENT_DEFAULT,
                "portfolio_health": scorer._portfolio_health(profile),
                "age": min(profile.months_active * AGE_PER_MONTH, 120),
                "reputation": profile.registration_count * REPUTATION_MULTIPLIER,
            },
        }
    except Exception as e:
        return {"error": str(e)}


# ──────────────────────────────────────────────
#  CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test cases
        test_cases = [
            AgentProfile("agent-001", registration_count=5, months_active=12,
                         on_time_payments=10, defaults=0, portfolio_tvl=25000,
                         tvl_trend_30d=0.1, yield_stability=0.8, protocol_count=6),
            AgentProfile("agent-002", registration_count=1, months_active=1,
                         on_time_payments=0, defaults=0, portfolio_tvl=500,
                         tvl_trend_30d=-0.2, yield_stability=0.2, protocol_count=1),
            AgentProfile("agent-003", registration_count=2, months_active=6,
                         on_time_payments=3, defaults=1, portfolio_tvl=5000,
                         tvl_trend_30d=0.0, yield_stability=0.5, protocol_count=3),
        ]

        for p in test_cases:
            s = scorer.score(p)
            t = scorer.risk_tier(s)
            mc = scorer.max_credit(s)
            print(f"{p.agent_id}: score={s}, tier={t}, max_credit=${mc:.2f}")
    else:
        # Read JSON from stdin
        body = json.loads(sys.stdin.read())
        result = handle_score_request(body)
        print(json.dumps(result, indent=2))
