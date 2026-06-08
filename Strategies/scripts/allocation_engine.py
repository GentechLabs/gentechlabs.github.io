#!/usr/bin/env python3
"""
Strategy Allocation Engine — AAE Hybrid Strategy Engine
Takes regime + strategy returns and recommends portfolio allocation.

Allocation is dynamic based on:
  - Market regime (from regime-classifier.py)
  - Strategy returns (from strategy-returns.py)
  - Risk profile (conservative/balanced/aggressive)
  - Current allocation (for drift detection)
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple

# ── Config ──────────────────────────────────────────────────────────────────

STATE_DIR = os.path.expanduser("~/.hermes/scripts")
ALLOCATION_STATE_FILE = os.path.join(STATE_DIR, ".aae-allocation-state.json")

# ── Allocation Matrix ──────────────────────────────────────────────────────
# Format: {regime: {strategy: allocation_pct}}
# All allocations sum to 100

ALLOCATION_MATRIX = {
    "BULL_TRENDING": {
        "lp": 15,
        "hodl": 60,
        "staking": 15,
        "lending": 10,
    },
    "BEAR_TRENDING": {
        "lp": 10,
        "hodl": 20,
        "staking": 50,
        "lending": 20,
    },
    "RANGE_BOUND": {
        "lp": 40,
        "hodl": 15,
        "staking": 30,
        "lending": 15,
    },
    "HIGH_VOLATILITY": {
        "lp": 25,
        "hodl": 30,
        "staking": 25,
        "lending": 20,
    },
    "ACCUMULATION": {
        "lp": 20,
        "hodl": 40,
        "staking": 25,
        "lending": 15,
    },
    "PRICE_DISCOVERY": {
        "lp": 10,
        "hodl": 70,
        "staking": 15,
        "lending": 5,
    },
    "UNKNOWN": {
        "lp": 25,
        "hodl": 25,
        "staking": 25,
        "lending": 25,
    },
}

# Risk profile adjustments
RISK_PROFILES = {
    "conservative": {
        "lp": -10,       # reduce LP (risky)
        "hodl": -5,
        "staking": +10,  # increase staking (safe)
        "lending": +5,   # increase lending (safe)
    },
    "balanced": {
        "lp": 0,
        "hodl": 0,
        "staking": 0,
        "lending": 0,
    },
    "aggressive": {
        "lp": +10,       # increase LP (higher yield potential)
        "hodl": +5,
        "staking": -10,  # reduce staking (low yield)
        "lending": -5,
    },
}

# Rotation thresholds
ROTATION_THRESHOLD_PCT = 20  # only rotate if delta > 20%
COOLDOWN_HOURS = 4           # min hours between rotations
MAX_SINGLE_ALLOCATION = 70   # max % in any single strategy
MIN_SINGLE_ALLOCATION = 5    # min % in any strategy


# ── Allocation Logic ───────────────────────────────────────────────────────

def get_target_allocation(
    regime: str,
    risk_profile: str = "balanced",
    strategy_returns: Optional[Dict] = None,
) -> Dict[str, int]:
    """
    Calculate target allocation based on regime + risk profile.

    Optionally adjusts based on strategy returns (if one strategy is
    significantly outperforming, tilt toward it).
    """
    # Base allocation from matrix
    base = ALLOCATION_MATRIX.get(regime, ALLOCATION_MATRIX["UNKNOWN"]).copy()

    # Apply risk profile adjustments
    adjustments = RISK_PROFILES.get(risk_profile, RISK_PROFILES["balanced"])
    adjusted = {}
    for strategy in base:
        adj = adjustments.get(strategy, 0)
        adjusted[strategy] = max(MIN_SINGLE_ALLOCATION, min(MAX_SINGLE_ALLOCATION, base[strategy] + adj))

    # Normalize to 100%
    total = sum(adjusted.values())
    if total != 100:
        diff = 100 - total
        # Distribute diff to the largest allocation
        largest = max(adjusted, key=adjusted.get)
        adjusted[largest] += diff

    return adjusted


def calculate_rotation(
    current_allocation: Dict[str, int],
    target_allocation: Dict[str, int],
) -> Dict[str, Any]:
    """
    Calculate what needs to rotate and whether it's significant enough.
    """
    deltas = {}
    needs_rotation = False
    max_delta = 0

    for strategy in target_allocation:
        current = current_allocation.get(strategy, 0)
        target = target_allocation[strategy]
        delta = target - current
        deltas[strategy] = {
            "current": current,
            "target": target,
            "delta": delta,
            "delta_pct": abs(delta),
        }
        max_delta = max(max_delta, abs(delta))
        if abs(delta) > ROTATION_THRESHOLD_PCT:
            needs_rotation = True

    return {
        "deltas": deltas,
        "needs_rotation": needs_rotation,
        "max_delta": max_delta,
        "threshold": ROTATION_THRESHOLD_PCT,
    }


def check_cooldown(last_rotation_time: Optional[str]) -> Tuple[bool, Optional[float]]:
    """Check if rotation cooldown has elapsed."""
    if not last_rotation_time:
        return True, None

    try:
        last = datetime.fromisoformat(last_rotation_time.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours_since = (now - last).total_seconds() / 3600

        if hours_since < COOLDOWN_HOURS:
            remaining = COOLDOWN_HOURS - hours_since
            return False, remaining
        return True, None
    except (ValueError, TypeError):
        return True, None


# ── Main Allocation Pipeline ───────────────────────────────────────────────

def run_allocation_engine(
    regime: str = "UNKNOWN",
    regime_confidence: float = 0.5,
    risk_profile: str = "balanced",
    current_allocation: Optional[Dict[str, int]] = None,
    strategy_returns: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Run full allocation engine pipeline.
    Returns recommendation with rotation details.
    """
    # Load previous state
    prev_state = {}
    try:
        with open(ALLOCATION_STATE_FILE) as f:
            prev_state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Default current allocation (even split if unknown)
    if current_allocation is None:
        current_allocation = prev_state.get("current_allocation", {
            "lp": 25, "hodl": 25, "staking": 25, "lending": 25
        })

    # Calculate target allocation
    target = get_target_allocation(regime, risk_profile, strategy_returns)

    # Calculate rotation
    rotation = calculate_rotation(current_allocation, target)

    # Check cooldown
    can_rotate, cooldown_remaining = check_cooldown(prev_state.get("last_rotation_time"))

    # Build result
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "regime": regime,
        "regime_confidence": regime_confidence,
        "risk_profile": risk_profile,
        "current_allocation": current_allocation,
        "target_allocation": target,
        "rotation": rotation,
        "can_rotate": can_rotate,
        "cooldown_remaining_hours": round(cooldown_remaining, 1) if cooldown_remaining else None,
        "action": "ROTATE" if (rotation["needs_rotation"] and can_rotate) else "HOLD",
        "action_reason": None,
    }

    # Set action reason
    if not rotation["needs_rotation"]:
        result["action_reason"] = f"Max allocation delta {rotation['max_delta']}% < threshold {ROTATION_THRESHOLD_PCT}%"
    elif not can_rotate:
        result["action_reason"] = f"Cooldown: {cooldown_remaining:.1f}h remaining"
    else:
        result["action_reason"] = f"Rotation needed: max delta {rotation['max_delta']}%"

    # Save state
    os.makedirs(os.path.dirname(ALLOCATION_STATE_FILE), exist_ok=True)
    save_state = {
        "current_allocation": target if result["action"] == "ROTATE" else current_allocation,
        "last_regime": regime,
        "last_rotation_time": datetime.now(timezone.utc).isoformat() if result["action"] == "ROTATE" else prev_state.get("last_rotation_time"),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "history": prev_state.get("history", [])[-20:],  # keep last 20 entries
    }
    # Add to history
    save_state["history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "regime": regime,
        "action": result["action"],
        "target": target,
    })

    with open(ALLOCATION_STATE_FILE, "w") as f:
        json.dump(save_state, f, indent=2)

    # Also save full result
    result_file = os.path.join(STATE_DIR, ".aae-allocation-result.json")
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ── Human-Readable Output ──────────────────────────────────────────────────

def format_allocation(result: Dict[str, Any]) -> str:
    """Format allocation recommendation as human-readable text."""
    lines = []
    lines.append("🧠 AAE ALLOCATION ENGINE")
    lines.append(f"   Regime: {result['regime']} (confidence: {result['regime_confidence']:.0%})")
    lines.append(f"   Risk Profile: {result['risk_profile']}")
    lines.append("")

    lines.append("Current → Target Allocation:")
    for strat in ["LP", "HODL", "STAKING", "LENDING"]:
        key = strat.lower()
        curr = result["current_allocation"].get(key, 0)
        tgt = result["target_allocation"].get(key, 0)
        delta = tgt - curr
        arrow = "→"
        sign = "+" if delta > 0 else ""
        lines.append(f"   {strat:10s} {curr:3d}% {arrow} {tgt:3d}%  ({sign}{delta}%)")

    lines.append("")
    action = result["action"]
    emoji = "🔄" if action == "ROTATE" else "⏸️"
    lines.append(f"{emoji} Action: {action}")
    lines.append(f"   Reason: {result['action_reason']}")

    if result.get("cooldown_remaining_hours"):
        lines.append(f"   Cooldown: {result['cooldown_remaining_hours']:.1f}h remaining")

    return "\n".join(lines)


# ── CLI Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    # Accept regime as argument, or load from state
    regime = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"
    confidence = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

    result = run_allocation_engine(
        regime=regime,
        regime_confidence=confidence,
    )

    print(format_allocation(result))
    print("\n--- JSON ---")
    print(json.dumps(result, indent=2))
