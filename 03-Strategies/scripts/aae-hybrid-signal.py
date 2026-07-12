#!/usr/bin/env python3
"""
AAE Hybrid Strategy Signal — Unified Pipeline
Chains regime classifier + strategy returns + allocation engine into one signal.

Output: JSON signal + human-readable report for cron job consumption.

Usage:
  python3 aae-hybrid-signal.py                    # Full pipeline
  python3 aae-hybrid-signal.py --json             # JSON only
  python3 aae-hybrid-signal.py --regime BULL_TRENDING  # Override regime
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Add script directory to path for module imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Import our modules
from regime_classifier import run_classification
from strategy_returns import run_strategy_comparison, format_leaderboard
from allocation_engine import run_allocation_engine, format_allocation

# ── Config ──────────────────────────────────────────────────────────────────

POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
STATE_DIR = os.path.expanduser("~/.hermes/scripts")
SIGNAL_FILE = os.path.join(STATE_DIR, ".aae-hybrid-signal.json")

# Position config (from AAE monitor)
POSITION = {
    "total_usd": 134.94,
    "token0_amount": 3.446,
    "token1_amount": 103.38,
    "range_low": 9.75,
    "range_high": 10.01,
}


# ── Unified Pipeline ───────────────────────────────────────────────────────

def run_hybrid_signal(
    override_regime: Optional[str] = None,
    override_confidence: Optional[float] = None,
    risk_profile: str = "balanced",
) -> Dict[str, Any]:
    """
    Run the full hybrid strategy signal pipeline.

    1. Classify market regime
    2. Compare strategy returns
    3. Calculate allocation recommendation
    4. Generate unified signal
    """
    start_time = time.time()
    signal = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "pipeline": {},
    }

    # ── Step 1: Regime Classification ───────────────────────────────────
    try:
        regime_data = run_classification(POOL_ADDRESS)
        signal["pipeline"]["regime"] = {
            "status": "ok",
            "regime": regime_data.get("regime", "UNKNOWN"),
            "confidence": regime_data.get("confidence", 0),
            "prev_regime": regime_data.get("prev_regime"),
            "regime_changed": regime_data.get("regime_changed", False),
            "details": regime_data.get("details", {}),
            "price": regime_data.get("price"),
            "rsi_14": regime_data.get("rsi_14"),
            "atr_pct": regime_data.get("atr_pct"),
        }
    except Exception as e:
        signal["pipeline"]["regime"] = {"status": "error", "error": str(e)}
        regime_data = {"regime": "UNKNOWN", "confidence": 0}

    # Use override if provided
    regime = override_regime or regime_data.get("regime", "UNKNOWN")
    confidence = override_confidence or regime_data.get("confidence", 0.5)

    # ── Step 2: Strategy Returns ────────────────────────────────────────
    try:
        # Get fees from regime data if available (fallback to 0)
        fees_24h = 0.0  # Would come from AAE monitor in production
        price_change = regime_data.get("details", {}).get("momentum_7d", 0) or 0

        returns_data = run_strategy_comparison(
            position_value=POSITION["total_usd"],
            spot_value=0.0961,  # AVAX in wallet
            fees_24h=fees_24h,
            price_change_24h_pct=price_change * 100 if price_change else 0.5,
        )
        signal["pipeline"]["returns"] = {
            "status": "ok",
            "strategies": returns_data.get("strategies", {}),
            "leaderboard": returns_data.get("leaderboard", []),
            "avax_price": returns_data.get("avax_price"),
        }
    except Exception as e:
        signal["pipeline"]["returns"] = {"status": "error", "error": str(e)}
        returns_data = {}

    # ── Step 3: Allocation Engine ───────────────────────────────────────
    try:
        allocation_data = run_allocation_engine(
            regime=regime,
            regime_confidence=confidence,
            risk_profile=risk_profile,
            strategy_returns=returns_data.get("strategies"),
        )
        signal["pipeline"]["allocation"] = {
            "status": "ok",
            "action": allocation_data.get("action"),
            "action_reason": allocation_data.get("action_reason"),
            "current": allocation_data.get("current_allocation"),
            "target": allocation_data.get("target_allocation"),
            "rotation": allocation_data.get("rotation"),
            "can_rotate": allocation_data.get("can_rotate"),
            "cooldown_hours": allocation_data.get("cooldown_remaining_hours"),
        }
    except Exception as e:
        signal["pipeline"]["allocation"] = {"status": "error", "error": str(e)}
        allocation_data = {"action": "HOLD", "action_reason": "Error"}

    # ── Step 4: Unified Signal ──────────────────────────────────────────
    elapsed = time.time() - start_time

    # Determine alert level
    alert_level = "OK"
    if regime_data.get("regime_changed"):
        alert_level = "ALERT"
    if allocation_data.get("action") == "ROTATE":
        alert_level = "ACTION"
    if regime in ["HIGH_VOLATILITY", "BEAR_TRENDING"]:
        alert_level = "WARNING"

    signal["summary"] = {
        "regime": regime,
        "confidence": confidence,
        "alert_level": alert_level,
        "action": allocation_data.get("action", "HOLD"),
        "winner": returns_data.get("leaderboard", [{}])[0].get("strategy", "UNKNOWN") if returns_data.get("leaderboard") else "UNKNOWN",
        "avax_price": returns_data.get("avax_price"),
        "elapsed_seconds": round(elapsed, 2),
    }

    # Save signal
    os.makedirs(os.path.dirname(SIGNAL_FILE), exist_ok=True)
    with open(SIGNAL_FILE, "w") as f:
        json.dump(signal, f, indent=2)

    return signal


# ── Human-Readable Report ──────────────────────────────────────────────────

def format_hybrid_report(signal: Dict[str, Any]) -> str:
    """Format full hybrid signal as human-readable report."""
    lines = []
    summary = signal.get("summary", {})

    # Header
    alert_emoji = {"OK": "✅", "ALERT": "🔔", "ACTION": "🔄", "WARNING": "⚠️"}.get(summary.get("alert_level"), "❓")
    lines.append(f"{alert_emoji} AAE HYBRID SIGNAL — {signal.get('timestamp', '')[:19]}")
    lines.append(f"   Regime: {summary.get('regime', '?')} ({summary.get('confidence', 0):.0%})")
    lines.append(f"   AVAX: ${summary.get('avax_price', 0):.2f}")
    lines.append("")

    # Strategy Leaderboard
    pipeline = signal.get("pipeline", {})
    returns = pipeline.get("returns", {})
    if returns.get("status") == "ok" and returns.get("leaderboard"):
        lines.append("📊 STRATEGY LEADERBOARD:")
        for i, entry in enumerate(returns["leaderboard"], 1):
            medal = ["🥇", "🥈", "🥉", "4."][i-1] if i <= 4 else f"{i}."
            daily = entry.get("daily_return", 0)
            sign = "+" if daily >= 0 else ""
            lines.append(f"   {medal} {entry['strategy']:10s} {sign}${daily:.4f}/day  ({entry.get('apr', 0):.1f}% APR)")
        lines.append("")

    # Allocation
    alloc = pipeline.get("allocation", {})
    if alloc.get("status") == "ok":
        action = alloc.get("action", "HOLD")
        emoji = "🔄" if action == "ROTATE" else "⏸️"
        lines.append(f"{emoji} Allocation: {action}")

        if action == "ROTATE":
            lines.append("   Rotation needed:")
            for strat in ["LP", "HODL", "STAKING", "LENDING"]:
                key = strat.lower()
                curr = alloc.get("current", {}).get(key, 0)
                tgt = alloc.get("target", {}).get(key, 0)
                delta = tgt - curr
                sign = "+" if delta > 0 else ""
                lines.append(f"     {strat}: {curr}% → {tgt}% ({sign}{delta}%)")
        else:
            lines.append(f"   Reason: {alloc.get('action_reason', 'N/A')}")

    # Regime change warning
    regime_data = pipeline.get("regime", {})
    if regime_data.get("regime_changed"):
        lines.append("")
        lines.append(f"⚠️ REGIME SHIFT: {regime_data.get('prev_regime')} → {regime_data.get('regime')}")
        lines.append(f"   Confidence: {regime_data.get('confidence', 0):.0%}")

    lines.append("")
    lines.append(f"⚡ Pipeline: {summary.get('elapsed_seconds', 0):.1f}s")

    return "\n".join(lines)


# ── CLI Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AAE Hybrid Strategy Signal")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--regime", type=str, help="Override regime classification")
    parser.add_argument("--confidence", type=float, help="Override regime confidence")
    parser.add_argument("--risk", type=str, default="balanced",
                       choices=["conservative", "balanced", "aggressive"],
                       help="Risk profile")
    args = parser.parse_args()

    signal = run_hybrid_signal(
        override_regime=args.regime,
        override_confidence=args.confidence,
        risk_profile=args.risk,
    )

    if args.json:
        print(json.dumps(signal, indent=2))
    else:
        print(format_hybrid_report(signal))
