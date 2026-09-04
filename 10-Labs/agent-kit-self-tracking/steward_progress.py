#!/usr/bin/env python3
"""
Steward — Deposit Detection + Milestone Progress
=================================================
Detects NEW deposits to the treasury wallet and reports rank / progress /
estimated fees with the new capital. Productizes the D5 milestone/ranking
system (Scout→Raider→Warlord→Fisher→Sovereign) into the Agentic Treasury loop.

How it works:
  1. Persists a baseline of wallet value (native + stablecoins) between runs.
  2. On each run, compares current wallet value to the baseline.
  3. If value INCREASED meaningfully (> DEPOSIT_THRESHOLD_USD, or > threshold %
     to avoid noise from price drift), it's flagged as a NEW DEPOSIT.
  4. Recomputes the position + daily-fee estimate with the new capital, maps it
     to the D5 milestone tiers, and reports % progress to the next rank.

Modes:
  - --watchdog: quiet mode — print ONLY when a deposit is detected (for a cheap
    no_agent cron that stays silent until Jordan sends money).
  - default: full report (rank, progress, fees, deposit detected or not).

The deposit is detected by DELTA vs the last baseline, so it only fires when
actual new money arrives — not on ordinary price movement (price swings are
smoothed by requiring the delta to exceed a % threshold AND a $ floor).

Reuses: discover_positions (live balances + position), the D5 milestone tiers.
"""

from __future__ import annotations

import json
import os
import time
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# ── Paths / config ───────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE_FILE = os.path.join(HERE, ".steward-wallet-baseline.json")

# Milestone tiers — D5 daily-fee ranking (Jordan's system, canonical ladder
# from AAE DeFi Milestone: Untested→Scout→Raider→Warlord→Sovereign)
# Tier 0 = brand-new / untested (screams "new"), then the earned ranks.
MILESTONES = [
    {"tier": 0, "label": "Untested", "daily_fees": 0,   "unlocks": "First deposit — prove the engine"},
    {"tier": 1, "label": "Scout",    "daily_fees": 5,   "unlocks": "Entry strategies (CURVE)"},
    {"tier": 2, "label": "Raider",   "daily_fees": 20,  "unlocks": "SPOT + BIDIRECTIONAL shapes"},
    {"tier": 3, "label": "Warlord",  "daily_fees": 55,  "unlocks": "Multi-pool positions"},
    {"tier": 4, "label": "Sovereign","daily_fees": 200, "unlocks": "Custom strategy creation + mentorship"},
]
TIER_ICONS = {0: "🌱", 1: "🔭", 2: "⚔️", 3: "👑", 4: "🏰"}

# Deposit detection
DEPOSIT_FLOOR_USD = 1.0        # ignore deltas under $1 (noise)
DEPOSIT_MIN_PCT = 2.0          # delta must exceed 2% of baseline value
FEE_ESTIMATE_APR = 52.1        # annualized APR % from the live feed (52.1% observed)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: str, default=None) -> Optional[Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def read_wallet_value() -> Dict[str, Any]:
    """Live wallet value (native + stablecoins + LP) via discover_positions."""
    sys.path.insert(0, HERE)
    try:
        from discover_positions import discover_positions, _is_checksum_or_valid
        cfg = load_json(os.path.join(HERE, "treasury_config.json"), {}) or {}
        wallet = cfg.get("wallet") or os.environ.get("STEWARD_WALLET")
        if not isinstance(wallet, str) or not _is_checksum_or_valid(wallet):
            return {"error": "no valid wallet"}
        # Avalanche (LFJ rail)
        data = discover_positions("avalanche", wallet)
        if "error" in data:
            return {"error": data["error"]}
        # TOTAL treasury value = liquid + LP (Jordan, Sep 3 2026: a deposit
        # detector that can't see the LP misreads every rebalance as a
        # deposit — the 16:16 "+720%" false alarm; internal swaps between
        # USDC/WAVAX/LP are NOT deposits, they are the machine working).
        balances = data.get("balances", {})
        from discover_positions import fetch_asset_price
        avax_usd = fetch_asset_price("AVAX") or 0.0
        native = balances.get("AVAX", 0.0) or 0.0
        wavax = balances.get("WAVAX", 0.0) or 0.0
        value_usd = native * avax_usd          # native gas
        value_usd += wavax * avax_usd          # wrapped AVAX (same asset)
        for sym in ("USDC", "USDC_e", "USDT_e", "USDT"):
            value_usd += float(balances.get(sym, 0.0) or 0.0)
        # LP position value — chain truth from the reader
        pos = next((p for p in data.get("positions", []) if "error" not in p), None)
        if pos and isinstance(pos.get("positionUsd"), (int, float)):
            value_usd += float(pos["positionUsd"])
        return {
            "value_usd": round(value_usd, 2),
            "native_usd": round(native * avax_usd, 2),
            "stable_usd": round(float(balances.get("USDC", 0.0) or 0.0)
                                + float(balances.get("USDC_e", 0.0) or 0.0)
                                + float(balances.get("USDT_e", 0.0) or 0.0)
                                + float(balances.get("USDT", 0.0) or 0.0), 2),
            "avax_price": round(avax_usd, 4),
            "lp_usd": (round(float(pos["positionUsd"]), 2) if pos else 0.0),
            "lp_bins": (pos.get("bins", 0) if pos else 0),
            "in_range": (pos.get("inRange") if pos else False),
        }
    except Exception as e:
        return {"error": str(e)}


def estimate_daily_fees(value_usd: float) -> float:
    """Daily fee estimate. Uses the brain's canonical volume-based figure from
    DeFi/defi-data.json (feeMilestones.currentDailyFees) when available — it
    reflects the LP position share of pool volume. Falls back to an APR-on-value
    approximation if the canonical feed is missing."""
    # Canonical source: AAE DeFi Milestone dashboard feed (already correct)
    for path in (
        "/root/vaults/gentech/DeFi/defi-data.json",
        "/root/repos/gentechlabs.github.io/DeFi/defi-data.json",
    ):
        try:
            with open(path) as f:
                data = json.load(f)
            fm = data.get("feeMilestones") or {}
            cf = fm.get("currentDailyFees")
            if isinstance(cf, (int, float)) and cf > 0:
                return round(float(cf), 4)
        except Exception:
            continue
    # Fallback: APR on the reported wallet value
    if value_usd <= 0:
        return 0.0
    return round(value_usd * (FEE_ESTIMATE_APR / 100.0) / 365.0, 4)


def rank_and_progress(daily_fees: float) -> Dict[str, Any]:
    """Map daily fees to D5 milestone tier + % progress to next rank."""
    current_tier = None
    next_tier = None
    for i, ms in enumerate(MILESTONES):
        if daily_fees >= ms["daily_fees"]:
            current_tier = ms
        else:
            next_tier = ms
            break

    if current_tier is None:
        label = "Untested"
        progress = round((daily_fees / MILESTONES[0]["daily_fees"]) * 100, 0) if MILESTONES[0]["daily_fees"] else 0
        rank_icon = "🌱"
    elif next_tier is None:
        label = current_tier["label"]
        progress = 100.0
        rank_icon = TIER_ICONS[current_tier["tier"]]
    else:
        label = current_tier["label"]
        base = current_tier["daily_fees"]
        target = next_tier["daily_fees"]
        progress = round(((daily_fees - base) / (target - base)) * 100, 0)
        rank_icon = TIER_ICONS[current_tier["tier"]]

    return {
        "rank": label,
        "rank_icon": rank_icon,
        "current_daily_fees": round(daily_fees, 4),
        "progress_pct": progress,
        "next_rank": next_tier["label"] if next_tier else "MAX",
        "next_target_daily_fees": next_tier["daily_fees"] if next_tier else None,
        "fees_to_next": round((next_tier["daily_fees"] - daily_fees), 4) if next_tier else 0.0,
        "unlocks": next_tier["unlocks"] if next_tier else None,
    }



def _machine_active_recently(hours: float = 2.0) -> bool:
    """True if the treasury machine executed a rebalance/deploy/compound
    within the last `hours` — during that window, value deltas are internal
    churn, not deposits (Jordan, Sep 3 2026: '+720% deposit' was machine
    churn misread as new money)."""
    import glob, json as _json
    stamps = [
        "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/.steward-last-rebalance.json",
    ]
    # auto-compound stamps + any last-action stamps in both script homes
    EXCLUDE = {".steward-wallet-baseline.json",      # this script's own output
               ".steward-silence-state.json",        # messaging state, not action
               ".steward-council-trigger-state.json"}  # council chatter
    for pat in ("/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/.steward-*.json",
                "/root/.hermes/profiles/gentech-treasury/scripts/.steward-*.json"):
        stamps.extend(s for s in glob.glob(pat)
                      if os.path.basename(s) not in EXCLUDE)
    cutoff = time.time() - hours * 3600
    for s in stamps:
        try:
            if os.path.getmtime(s) >= cutoff:
                return True
        except OSError:
            continue
    return False

def detect_deposit(current: Dict[str, float]) -> Dict[str, Any]:
    """Compare current wallet value to the persisted baseline. Detects deposits.

    Returns {detected, delta_usd, delta_pct, prior_value, new_value}.
    Also UPDATES the baseline so the next run measures fresh.
    """
    prior = load_json(BASELINE_FILE, {}) or {}
    prior_value = float(prior.get("value_usd", 0.0) or 0.0)
    current_value = float(current.get("value_usd", 0.0) or 0.0)

    result = {
        "prior_value": round(prior_value, 2),
        "new_value": round(current_value, 2),
        "delta_usd": round(current_value - prior_value, 2),
        "detected": False,
    }

    if current_value > 0 and prior_value > 0:
        delta = current_value - prior_value
        delta_pct = (delta / prior_value) * 100.0 if prior_value else 0.0
        # A deposit: value went UP beyond noise floor AND beyond price-drift %
        # AND the machine was quiet (no rebalance/deploy/compound in the last
        # 2h) — during machine activity, value deltas are internal churn.
        if (delta >= DEPOSIT_FLOOR_USD and delta_pct >= DEPOSIT_MIN_PCT
                and not _machine_active_recently(hours=2.0)):
            result["detected"] = True
            result["delta_pct"] = round(delta_pct, 1)

    # Always persist the new baseline (whether deposit or not) so the loop
    # measures fresh deltas next run.
    with open(BASELINE_FILE, "w") as f:
        json.dump({"value_usd": current_value, "ts": _now_iso(),
                   "native_usd": current.get("native_usd"),
                   "stable_usd": current.get("stable_usd")}, f, indent=2)

    return result


# ── Main ─────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Steward — deposit detection + milestone progress")
    ap.add_argument("--watchdog", action="store_true",
                    help="quiet mode: print ONLY when a deposit is detected")
    ap.add_argument("--reset", action="store_true",
                    help="reset the baseline (rebaseline current wallet value)")
    args = ap.parse_args()

    current = read_wallet_value()
    if "error" in current:
        print(f"⚠️ Steward progress: {current['error']}", file=sys.stderr)
        return 0 if args.watchdog else 1

    if args.reset:
        with open(BASELINE_FILE, "w") as f:
            json.dump({"value_usd": current.get("value_usd", 0.0),
                       "ts": _now_iso()}, f, indent=2)
        print(f"🛡️ Steward: baseline reset to ${current.get('value_usd', 0):.2f}")
        return 0

    deposit = detect_deposit(current)
    fees = estimate_daily_fees(deposit["new_value"])
    prog = rank_and_progress(fees)

    # ── WATCHDOG: only report on a real deposit ──────────────────────────
    if args.watchdog:
        if deposit["detected"]:
            print(f"🛡️ Steward: 📥 DEPOSIT DETECTED")
            print(f"   New wallet value: ${deposit['new_value']:.2f} "
                  f"(+${deposit['delta_usd']:.2f}, +{deposit.get('delta_pct', 0)}%)")
            print(f"   Rank: {prog['rank_icon']} {prog['rank']}")
            print(f"   Est. daily fees: ${prog['current_daily_fees']:.4f}/day")
            if prog["next_rank"] != "MAX":
                print(f"   Next: {prog['next_rank']} at ${prog['next_target_daily_fees']:.0f}/day "
                      f"({prog['progress_pct']:.0f}% there — ${prog['fees_to_next']:.4f}/day to go)")
            else:
                print(f"   🏆 Max rank achieved!")
            if prog.get("unlocks"):
                print(f"   Unlocks at next: {prog['unlocks']}")
        # else: silent (no deposit = nothing to say)
        return 0

    # ── Full report ──────────────────────────────────────────────────────
    print("=" * 52)
    print("🛡️  STEWARD — DEPOSIT & MILESTONE PROGRESS")
    print("=" * 52)
    print(f"  Wallet value: ${deposit['new_value']:.2f}")
    if deposit["detected"]:
        print(f"  📥 Deposit: +${deposit['delta_usd']:.2f} "
              f"(+{deposit.get('delta_pct', 0)}%) vs last baseline")
    else:
        print(f"  Deposit: none (baseline ${deposit['prior_value']:.2f})")
    print(f"  Est. daily fees: ${fees:.4f}/day")
    print(f"  Rank: {prog['rank_icon']} {prog['rank']}")
    print(f"  Progress to {prog['next_rank']}: {prog['progress_pct']:.0f}%")
    if prog["next_rank"] != "MAX":
        print(f"  Needed: ${prog['fees_to_next']:.4f}/day more "
              f"(target ${prog['next_target_daily_fees']:.0f}/day)")
        print(f"  Unlocks: {prog['unlocks']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
