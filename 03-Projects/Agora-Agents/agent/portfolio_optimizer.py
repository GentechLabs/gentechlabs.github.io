#!/usr/bin/env python3
"""
Portfolio Optimizer — Allocation Engine for Adaptive Portfolio Manager

Takes regime classification + portfolio state → produces allocation decisions.
Uses OpenRouter LLM for nuanced decisions beyond simple rules.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

# ── Data ────────────────────────────────────────────────────────────────────

@dataclass
class AllocationDecision:
    """Structured output from the optimizer."""
    regime: str
    confidence: float
    allocations: Dict[str, float]  # token → weight (0.0-1.0)
    rationale: str
    risk_score: int  # 1-10 (1=low risk, 10=high risk)
    rebalance_urgency: str  # low | medium | high | critical
    yield_strategy: str  # none | conservative | moderate | aggressive

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ── Regime → Allocation Mapping ────────────────────────────────────────────

# Base allocation profiles per regime
REGIME_PROFILES = {
    "BULL_TRENDING": {
        "USDC": 0.20,       # Stable dry powder
        "USYC": 0.20,       # Yield on stables
        "RISK": 0.60,       # Risk assets (ETH, BTC, SOL, etc.)
        "risk_score": 7,
        "urgency": "high",
        "yield": "moderate",
        "description": "Aggressive growth — ride momentum",
    },
    "BEAR_TRENDING": {
        "USDC": 0.60,       # Capital preservation
        "USYC": 0.30,       # Yield on stables
        "RISK": 0.10,       # Minimal risk exposure
        "risk_score": 2,
        "urgency": "medium",
        "yield": "aggressive",
        "description": "Defensive — preserve capital, maximize yield",
    },
    "RANGE_BOUND": {
        "USDC": 0.30,       # Dry powder
        "USYC": 0.40,       # Yield farming
        "RISK": 0.30,       # Range-trading positions
        "risk_score": 4,
        "urgency": "low",
        "yield": "moderate",
        "description": "Balanced — farm yield, accumulate",
    },
    "HIGH_VOLATILITY": {
        "USDC": 0.70,       # Maximum safety
        "USYC": 0.25,       # Short-term yield
        "RISK": 0.05,       # Minimal exposure
        "risk_score": 1,
        "urgency": "critical",
        "yield": "conservative",
        "description": "Risk-off — ride out the storm",
    },
    "ACCUMULATION": {
        "USDC": 0.40,       # DCA reserves
        "USYC": 0.20,       # Yield while waiting
        "RISK": 0.40,       # DCA into positions
        "risk_score": 5,
        "urgency": "medium",
        "yield": "conservative",
        "description": "DCA mode — systematic accumulation",
    },
    "PRICE_DISCOVERY": {
        "USDC": 0.50,       # Wait for confirmation
        "USYC": 0.30,       # Yield while waiting
        "RISK": 0.20,       # Small exploratory positions
        "risk_score": 6,
        "urgency": "low",
        "yield": "moderate",
        "description": "Exploration — small bets, wide stops",
    },
}


def optimize_allocation(
    regime: str,
    confidence: float,
    current_portfolio: Optional[Dict[str, float]] = None,
    market_data: Optional[Dict[str, Any]] = None,
    use_llm: bool = False,
) -> AllocationDecision:
    """
    Produce an allocation decision based on regime and context.

    Args:
        regime: Current market regime (one of 6 regimes)
        confidence: Regime classification confidence (0-100)
        current_portfolio: Current allocation weights
        market_data: Additional market context
        use_llm: Whether to use LLM for nuanced decisions

    Returns:
        AllocationDecision with target weights and rationale
    """
    # Get base profile for regime
    profile = REGIME_PROFILES.get(regime, REGIME_PROFILES["RANGE_BOUND"])

    # Adjust allocations based on confidence
    # Low confidence → more conservative (more USDC)
    confidence_factor = confidence / 100.0  # 0.0 - 1.0

    allocations = {}
    for token, weight in profile.items():
        if token in ("risk_score", "urgency", "yield", "description"):
            continue
        # Scale risk assets by confidence, increase USDC for low confidence
        if token == "RISK":
            allocations[token] = weight * confidence_factor
        elif token == "USDC":
            # USDC gets the redistribution from reduced risk
            risk_reduction = weight * (1 - confidence_factor) if token == "RISK" else 0
            allocations[token] = weight + (profile.get("RISK", 0) * (1 - confidence_factor) * 0.5)
        else:
            allocations[token] = weight

    # Normalize to sum to 1.0
    total = sum(allocations.values())
    if total > 0:
        allocations = {k: round(v / total, 4) for k, v in allocations.items()}

    # Build rationale
    rationale = (
        f"Regime: {regime} (confidence: {confidence:.0f}%). "
        f"{profile['description']}. "
        f"Risk score: {profile['risk_score']}/10."
    )

    # Adjust urgency based on confidence
    urgency = profile["urgency"]
    if confidence < 50:
        urgency = "low"  # Don't act on uncertain signals

    return AllocationDecision(
        regime=regime,
        confidence=confidence,
        allocations=allocations,
        rationale=rationale,
        risk_score=profile["risk_score"],
        rebalance_urgency=urgency,
        yield_strategy=profile["yield"],
    )


class PortfolioOptimizer:
    """Wrapper for the allocation optimizer."""

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm

    def optimize(
        self,
        regime: str,
        confidence: float,
        current_portfolio: Optional[Dict[str, float]] = None,
        market_data: Optional[Dict[str, Any]] = None,
    ) -> AllocationDecision:
        return optimize_allocation(
            regime, confidence, current_portfolio, market_data, self.use_llm
        )


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: portfolio_optimizer.py <regime> <confidence>")
        print("Regimes: BULL_TRENDING, BEAR_TRENDING, RANGE_BOUND, HIGH_VOLATILITY, ACCUMULATION, PRICE_DISCOVERY")
        sys.exit(1)

    regime = sys.argv[1]
    confidence = float(sys.argv[2])

    decision = optimize_allocation(regime, confidence)
    print(decision.to_json())
