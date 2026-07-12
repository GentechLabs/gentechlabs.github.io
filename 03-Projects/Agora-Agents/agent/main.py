#!/usr/bin/env python3
"""
Adaptive Portfolio Manager — Agent Entry Point
Agora Agents Hackathon (RFB 04)

Core loop:
1. Fetch on-chain data (prices, volumes, TVL)
2. Classify market regime (6 regimes)
3. AI agent decides allocation based on regime + portfolio state
4. Execute rebalance via Circle Gateway on Arc
5. Log results and emit events
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Local modules
from regime_classifier import RegimeClassifier, classify_current_market
from portfolio_optimizer import PortfolioOptimizer, AllocationDecision
from circle_client import CircleClient

# ── Config ──────────────────────────────────────────────────────────────────

CONFIG = {
    "poll_interval_seconds": 300,     # Check every 5 minutes
    "rebalance_cooldown_seconds": 3600,  # Min 1 hour between rebalances
    "min_regime_confidence": 60,      # Only rebalance if confidence > 60%
    "max_slippage_bps": 500,         # 5% max slippage
    "rpc_url": os.getenv("ARC_RPC_URL", "https://rpc.arc.network"),
    "chain_id": int(os.getenv("ARC_CHAIN_ID", "2368")),
    "private_key": os.getenv("AGENT_PRIVATE_KEY"),
    "portfolio_contract": os.getenv("PORTFOLIO_CONTRACT"),
    "oracle_contract": os.getenv("ORACLE_CONTRACT"),
    "usdc_address": os.getenv("USDC_ADDRESS"),
}

# ── Regime → Allocation Profiles ────────────────────────────────────────────

REGIME_PROFILES = {
    "BULL_TRENDING": {
        "risk_assets": 0.60,    # 60% in risk-on assets
        "yield": 0.20,          # 20% in USYC / staking
        "stable": 0.20,         # 20% USDC dry powder
        "rebalance_frequency": "aggressive",
        "description": "Growth mode — ride the trend with trailing stops",
    },
    "BEAR_TRENDING": {
        "risk_assets": 0.10,    # 10% minimal risk exposure
        "yield": 0.30,          # 30% yield on stables
        "stable": 0.60,         # 60% USDC safety
        "rebalance_frequency": "conservative",
        "description": "Defense mode — preserve capital, earn yield on stables",
    },
    "RANGE_BOUND": {
        "risk_assets": 0.30,    # 30% range-trading
        "yield": 0.40,          # 40% yield farming
        "stable": 0.30,         # 30% dry powder for breakouts
        "rebalance_frequency": "moderate",
        "description": "Accumulation mode — farm yield, wait for direction",
    },
    "HIGH_VOLATILITY": {
        "risk_assets": 0.05,    # 5% minimal exposure
        "yield": 0.25,          # 25% short-term yield
        "stable": 0.70,         # 70% capital preservation
        "rebalance_frequency": "reactive",
        "description": "Risk-off — minimize exposure, wait for clarity",
    },
    "ACCUMULATION": {
        "risk_assets": 0.40,    # 40% DCA into position
        "yield": 0.20,          # 20% yield
        "stable": 0.40,         # 40% dry powder for DCA
        "rebalance_frequency": "dca",
        "description": "DCA mode — systematic accumulation at lower prices",
    },
    "PRICE_DISCOVERY": {
        "risk_assets": 0.20,    # 20% small position
        "yield": 0.30,          # 30% yield
        "stable": 0.50,         # 50% wait for confirmation
        "rebalance_frequency": "cautious",
        "description": "Exploration — small positions, wide stops, wait for confirmation",
    },
}

# ── Agent State ─────────────────────────────────────────────────────────────

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.agora-portfolio-state.json")

def load_state() -> Dict[str, Any]:
    default = {
        "last_regime": None,
        "last_rebalance_time": 0,
        "total_rebalances": 0,
        "portfolio_value_usd": 0,
        "regime_history": [],
        "last_regime_change": None,
    }
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
            for k, v in default.items():
                state.setdefault(k, v)
            return state
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_state(state: Dict[str, Any]):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ── Main Loop ───────────────────────────────────────────────────────────────

def run_cycle(state: Dict[str, Any]) -> Dict[str, Any]:
    """Run one monitoring + decision cycle."""

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "regime": None,
        "confidence": 0,
        "action": "monitor",
        "details": {},
    }

    # 1. Classify current market regime
    try:
        regime_data = classify_current_market()
        result["regime"] = regime_data["regime"]
        result["confidence"] = regime_data["confidence"]
        result["details"]["regime"] = regime_data
    except Exception as e:
        result["error"] = f"Regime classification failed: {e}"
        return result

    # 2. Check if regime changed
    regime_changed = regime_data["regime"] != state.get("last_regime")
    result["details"]["regime_changed"] = regime_changed

    if regime_changed and state.get("last_regime"):
        result["details"]["prev_regime"] = state["last_regime"]
        state["last_regime_change"] = result["timestamp"]

    # 3. Check rebalance cooldown
    time_since_rebalance = time.time() - state.get("last_rebalance_time", 0)
    cooldown_met = time_since_rebalance >= CONFIG["rebalance_cooldown_seconds"]

    # 4. Decision: rebalance if regime changed + confidence high enough + cooldown met
    should_rebalance = (
        regime_changed
        and regime_data["confidence"] >= CONFIG["min_regime_confidence"]
        and cooldown_met
    )

    if should_rebalance:
        profile = REGIME_PROFILES.get(regime_data["regime"], REGIME_PROFILES["RANGE_BOUND"])

        result["action"] = "rebalance"
        result["details"]["target_allocation"] = profile
        result["details"]["reason"] = (
            f"Regime shifted {state.get('last_regime', 'UNKNOWN')} → {regime_data['regime']} "
            f"(confidence: {regime_data['confidence']}%)"
        )

        # Execute rebalance (Circle client)
        try:
            circle = CircleClient(CONFIG)
            tx_result = circle.rebalance(
                profile=profile,
                portfolio_contract=CONFIG["portfolio_contract"],
                max_slippage_bps=CONFIG["max_slippage_bps"],
            )
            result["details"]["tx_hash"] = tx_result.get("tx_hash")
            result["details"]["executed"] = True

            state["last_rebalance_time"] = time.time()
            state["total_rebalances"] += 1
        except Exception as e:
            result["details"]["tx_error"] = str(e)
            result["details"]["executed"] = False
            result["action"] = "rebalance_failed"

    else:
        reasons = []
        if not regime_changed:
            reasons.append("no regime change")
        if regime_data["confidence"] < CONFIG["min_regime_confidence"]:
            reasons.append(f"confidence too low ({regime_data['confidence']}% < {CONFIG['min_regime_confidence']}%)")
        if not cooldown_met:
            reasons.append(f"cooldown active ({time_since_rebalance:.0f}s < {CONFIG['rebalance_cooldown_seconds']}s)")

        result["action"] = "hold"
        result["details"]["hold_reasons"] = reasons

    # 5. Update state
    state["last_regime"] = regime_data["regime"]
    state["regime_history"].append({
        "timestamp": result["timestamp"],
        "regime": regime_data["regime"],
        "confidence": regime_data["confidence"],
    })
    # Keep last 100 regime observations
    state["regime_history"] = state["regime_history"][-100:]

    return result


def main():
    """Main entry point — runs the monitoring loop."""
    print(f"[Agora Portfolio Agent] Starting at {datetime.now(timezone.utc).isoformat()}")
    print(f"[Config] Poll: {CONFIG['poll_interval_seconds']}s | Chain: {CONFIG['chain_id']}")
    print(f"[Config] Min confidence: {CONFIG['min_regime_confidence']}%")
    print(f"[Config] Rebalance cooldown: {CONFIG['rebalance_cooldown_seconds']}s")

    state = load_state()

    while True:
        try:
            result = run_cycle(state)
            save_state(state)

            # Output structured result
            print(json.dumps(result, indent=2))

            # Log summary
            action = result["action"]
            regime = result.get("regime", "UNKNOWN")
            confidence = result.get("confidence", 0)

            if action == "rebalance":
                print(f"✅ REBALANCE EXECUTED → {regime} ({confidence}%)")
            elif action == "rebalance_failed":
                print(f"❌ REBALANCE FAILED → {regime} ({confidence}%)")
            else:
                print(f"👀 HOLD → {regime} ({confidence}%) — {result['details'].get('hold_reasons', [])}")

        except KeyboardInterrupt:
            print("\n[Agent] Stopped by user")
            break
        except Exception as e:
            print(f"[Agent] Cycle error: {e}", file=sys.stderr)

        time.sleep(CONFIG["poll_interval_seconds"])


if __name__ == "__main__":
    main()
