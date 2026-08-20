#!/usr/bin/env python3
"""
Unichain Treasury Allocator — regime-driven stablecoin deployment engine.

Ports the Agentic Treasury's allocation_engine.py to the Unichain grant context
(build queue #37: "Innovation upon the DeFi Experience" / treasury & asset mgmt).

Given a market regime + live Unichain pool snapshot, recommends how idle USDC
should be allocated across Unichain DeFi venues (LP, lending, hold) with a
gas-aware cost check. Purely advisory — emits a recommendation, moves nothing.

Design mirrors the proven AAE allocation matrix so it stays consistent with the
rest of the Agentic Treasury stack while being Unichain-specific.
"""

import json
import os
import subprocess
import sys
from typing import Dict, Optional

# ── Unichain-specific strategy venues ───────────────────────────────────────
# Each maps to a real Unichain venue a treasury could deploy to.
VENUES = {
    "lp": "Uniswap v3 USDC/WETH LP",
    "lending": "Morpho / Aave on Unichain",
    "hold": "Idle USDC (native)",
}

# ── Allocation matrix (Unichain context) ────────────────────────────────────
# {regime: {venue: pct}} — sums to 100
UNICHAIN_ALLOCATION_MATRIX = {
    "BULL_TRENDING": {"lp": 50, "lending": 30, "hold": 20},
    "BEAR_TRENDING": {"lp": 10, "lending": 40, "hold": 50},
    "RANGE_BOUND": {"lp": 45, "lending": 35, "hold": 20},
    "HIGH_VOLATILITY": {"lp": 25, "lending": 35, "hold": 40},
    "ACCUMULATION": {"lp": 35, "lending": 35, "hold": 30},
    "PRICE_DISCOVERY": {"lp": 20, "lending": 40, "hold": 40},
    "UNKNOWN": {"lp": 30, "lending": 35, "hold": 35},
}

RISK_PROFILES = {
    "conservative": {"lp": -15, "lending": +5, "hold": +10},
    "balanced": {"lp": 0, "lending": 0, "hold": 0},
    "aggressive": {"lp": +15, "lending": -5, "hold": -10},
}

# Gas cost floor per venue (USD) — a treasury shouldn't rotate if the rebalance
# costs more than the expected edge. Unichain gas is cheap (sub-cent).
GAS_COST_USD = {"lp": 0.02, "lending": 0.01, "hold": 0.0}
MIN_DEPLOYMENT_USD = 5.0  # don't deploy below this (gas eats the yield)
MAX_SINGLE_VENUE = 70
MIN_SINGLE_VENUE = 5


def get_target_allocation(regime: str, risk_profile: str = "balanced") -> Dict[str, int]:
    """Return venue allocation percentages for a regime + risk profile."""
    base = UNICHAIN_ALLOCATION_MATRIX.get(regime, UNICHAIN_ALLOCATION_MATRIX["UNKNOWN"]).copy()
    adj = RISK_PROFILES.get(risk_profile, RISK_PROFILES["balanced"])
    out = {}
    for venue in base:
        out[venue] = max(MIN_SINGLE_VENUE, min(MAX_SINGLE_VENUE, base[venue] + adj.get(venue, 0)))
    # Normalize to 100
    total = sum(out.values())
    if total != 100:
        largest = max(out.items(), key=lambda kv: kv[1])[0]
        out[largest] += 100 - total
    return out


def compute_recommendation(
    regime: str,
    risk_profile: str = "balanced",
    idle_usdc: float = 0.0,
    pool_snapshot: Optional[Dict] = None,
) -> Dict:
    """Compute a deployment recommendation from regime + pool snapshot."""
    target = get_target_allocation(regime, risk_profile)

    if idle_usdc < MIN_DEPLOYMENT_USD:
        action = "HOLD"
        reason = (
            f"Idle USDC ${idle_usdc:.2f} < ${MIN_DEPLOYMENT_USD:.2f} minimum — "
            "gas costs would eat the yield."
        )
    else:
        pool_ok = bool(pool_snapshot is not None and pool_snapshot.get("price", 0) > 0)
        action = "DEPLOY" if pool_ok else "HOLD"
        if not pool_ok:
            reason = "Unichain pool snapshot unavailable — cannot confirm live venue."
        else:
            reason = (
                f"Regime {regime} ({risk_profile}) + live Unichain pool "
                f"(price ${pool_snapshot.get('price', 0):.6f})."
            )

    return {
        "chain": "unichain",
        "regime": regime,
        "risk_profile": risk_profile,
        "idle_usdc": idle_usdc,
        "target_allocation": target,
        "venues": VENUES,
        "gas_cost_usd": GAS_COST_USD,
        "min_deployment_usd": MIN_DEPLOYMENT_USD,
        "action": action,
        "reason": reason,
    }


def format_recommendation(rec: Dict) -> str:
    lines = [
        "🏦 UNICHAIN TREASURY ALLOCATOR",
        f"   Regime: {rec['regime']} | Risk: {rec['risk_profile']}",
        f"   Idle USDC: ${rec['idle_usdc']:.2f}",
        "",
        "Target allocation:",
    ]
    for venue, pct in rec["target_allocation"].items():
        lines.append(f"   {VENUES[venue]:34s} {pct:3d}%")
    lines.append("")
    lines.append(f"{'✅' if rec['action'] == 'DEPLOY' else '⏸️'} Action: {rec['action']}")
    lines.append(f"   {rec['reason']}")
    return "\n".join(lines)


def main() -> int:
    regime = sys.argv[1] if len(sys.argv) > 1 else "RANGE_BOUND"
    idle = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    risk = sys.argv[3] if len(sys.argv) > 3 else "balanced"
    # Optionally ingest a live pool snapshot from the reader.
    snapshot = None
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.run(
            [sys.executable, os.path.join(here, "unichain_pool_reader.py")],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode == 0:
            snapshot = json.loads(out.stdout)
    except Exception:  # noqa: BLE001
        snapshot = None

    rec = compute_recommendation(regime, risk, idle, snapshot)
    print(format_recommendation(rec))
    if snapshot:
        print(f"\n   Live pool: {snapshot['pool_address']} (${snapshot['price']:.6f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
