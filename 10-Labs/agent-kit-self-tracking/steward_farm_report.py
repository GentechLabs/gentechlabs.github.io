#!/usr/bin/env python3
"""Steward Farm Report — agentic yield-farming status with DeFi milestones.

The AAE LP Monitor reborn, chain-fed: every number comes from the chain or a
freshness-gated live feed. NOTHING is fabricated (pool-reader lesson).

  📊 Position   — discover_positions.py (on-chain): value, range, in/out, bins
  💰 Earnings   — position-value DELTA since last report (fees ± IL, measured)
  📈 Trajectory — pool-avg fee APY (LFJ published) applied to OUR position
  🏆 Milestone  — DeFi tier ladder: Untested→Scout→Raider→Warlord→Sovereign
  🧠 Allocation — predictor's sentiment call (60/40 pullback etc.)
  ⚙️ Compound   — engine's last action from the ledger

Silent-when-degraded: chain read failure prints a one-line failure — never a
report from stale data. Writes .farm-snapshot.json each run so the next run
can compute the measured delta.

Usage: python3 steward_farm_report.py
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
VAULT_DIR = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking"
SCRIPT_DIR = "/root/.hermes/profiles/gentech-treasury/scripts"
STATE_DIR = "/root/.hermes/scripts"
SNAPSHOT = os.path.join(SCRIPT_DIR, ".farm-snapshot.json")
LPFEED = "/root/.hermes/profiles/gentech/scripts/lp-fees-live.json"
STAKFEED = "/root/.hermes/profiles/gentech/scripts/staking-apr-live.json"
ALLOC = os.path.join(STATE_DIR, "allocation-signal.json")
LEDGER = os.path.join(SCRIPT_DIR, ".compound-ledger.json")

MILESTONES = [
    {"tier": 0, "label": "Untested",  "daily_fees": 0,   "icon": "🌱", "unlocks": "First deposit — prove the engine"},
    {"tier": 1, "label": "Scout",     "daily_fees": 5,   "icon": "🔭", "unlocks": "Entry strategies (CURVE)"},
    {"tier": 2, "label": "Raider",    "daily_fees": 20,  "icon": "⚔️", "unlocks": "SPOT + BIDIRECTIONAL shapes"},
    {"tier": 3, "label": "Warlord",   "daily_fees": 55,  "icon": "👑", "unlocks": "Multi-pool positions"},
    {"tier": 4, "label": "Sovereign", "daily_fees": 200, "icon": "🏰", "unlocks": "Custom strategy creation + mentorship"},
]


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def feed_age_h(feed):
    ts = feed.get("ts", 0)
    return (time.time() - ts) / 3600 if ts else 999


def build_report(pos, balances, pool_apy, staking_apr,
                 delta_usd, delta_hours,
                 fee_note, fee_daily=None, fee_apr=None, alloc=None, last_action=None):
    pos_usd = pos.get("positionUsd") or 0
    price = pos.get("livePriceUsd") or 0
    bins = pos.get("bins")
    active = pos.get("activeBin")
    in_range = pos.get("inRange")
    range_lo = pos.get("rangeLow") or 0
    range_hi = pos.get("rangeHigh") or 0

    # Range position bar (0-100% through the bin range)
    if range_hi > range_lo:
        frac = max(0.0, min(1.0, (price - range_lo) / (range_hi - range_lo)))
    else:
        frac = 0.5
    frac = locals().get("frac", 0.5)
    filled = int(frac * 10)
    bar = "▓" * filled + "░" * (10 - filled)

    idle_usd = balances.get("USDC", 0) + balances.get("WAVAX", 0) * price
    gas_avax = balances.get("AVAX", 0)

    # Milestone tier — chain-truth fee ledger ONLY (Jordan Sep 3: the old
    # abs(LP-delta)/hours math turned churn into a fake "measured" rate,
    # way off the real numbers). Ledger fees are drift-adjusted + churn-
    # guarded; pool-avg is the fallback, clearly labeled.
    tier_basis = fee_daily  # ledger-derived (None while accumulating)
    basis_label = "ledger measured (drift-adjusted)"
    if tier_basis is None and pool_apy:
        tier_basis = pos_usd * pool_apy / 100 / 365
        basis_label = "pool-avg estimate (fallback)"
    current = MILESTONES[0]
    for m in MILESTONES:
        if tier_basis is not None and tier_basis >= m["daily_fees"]:
            current = m
    idx = MILESTONES.index(current)
    nxt = MILESTONES[idx + 1] if idx + 1 < len(MILESTONES) else None

    L = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L.append(f"🌾 STEWARD FARM REPORT — {ts}")
    L.append("")
    L.append("📊 Position (on-chain)")
    L.append(f"  LFJ AVAX/USDC V2.2 · {bins} bins · active bin {active}")
    in_mark = "🟢 IN RANGE — earning fees" if in_range else "🔴 OUT OF RANGE"
    L.append(f"  Value: ${pos_usd:.2f} · Price ${price:.4f} · {in_mark}")
    L.append(f"  Range: ${range_lo:.4f}–${range_hi:.4f}  [{bar} {frac*100:.0f}%]")
    L.append(f"  Dry powder (deployable reserve): ${idle_usd:.2f} — held for pullback dips"
             f" · Gas: {gas_avax:.3f} AVAX (~${gas_avax*price:.2f})")
    L.append("")
    L.append("💰 Earnings — chain-truth fee ledger (drift-adjusted)")
    if isinstance(fee_daily, (int, float)):
        L.append(f"  Measured fees: ${fee_daily:+.4f}/day-equivalent ({fee_note})")
        if fee_apr is not None:
            L.append(f"  Compounded APR on current capital: {fee_apr:.2f}% (fees redeployed grow the base)")
    else:
        L.append(f"  Accumulating: {fee_note}")
    if delta_usd is not None:
        sign = "+" if delta_usd >= 0 else ""
        L.append(f"  LP value since last report: ${delta_usd:+.4f} over {delta_hours:.1f}h (fees ± IL ± churn)")
    if pool_apy:
        daily_est = pos_usd * pool_apy / 100 / 365
        L.append(f"  Pool-avg fee on OUR position: ~${daily_est:.4f}/day (pool avg {pool_apy:.2f}% APY, LFJ published)")
    else:
        L.append("  Fee estimate unavailable (stale feed) — nothing fabricated")
    if staking_apr:
        L.append(f"  Benchmark: sAVAX staking {staking_apr}% APY")
    L.append("")
    L.append("🏆 Milestone")
    if tier_basis is not None:
        L.append(f"  {current['icon']} Tier {current['tier']} — {current['label']} ({basis_label} ${tier_basis:.4f}/day)")
        if nxt:
            prog = min(100.0, tier_basis / nxt["daily_fees"] * 100) if nxt["daily_fees"] else 0
            pfilled = int(prog / 10)
            L.append(f"  Next: {nxt['label']} (${nxt['daily_fees']}/day)  {'▓'*pfilled}{'░'*(10-pfilled)} {prog:.0f}%")
            L.append(f"  Unlocks at {nxt['label']}: {nxt['unlocks']}")
    else:
        L.append(f"  {current['icon']} Tier 0 — Untested (earning measurement starting now)")
    L.append("")
    L.append("🧠 Intelligence")
    L.append(f"  Allocation call: {alloc.get('allocation_display', '50/50')} — {str(alloc.get('stance', 'neutral')).upper()} ({alloc.get('confidence', 0)}% conf)")
    if last_action:
        ok = last_action.get("ok")
        mark = "✅" if ok else ("🧪 dry-run" if last_action.get("dry_run") else "❌")
        amt = f" ${last_action['amount_usd']}" if last_action.get("amount_usd") else ""
        ago = (time.time() - last_action.get("ts", 0)) / 3600
        L.append(f"  Compound engine: last {last_action['action']}{amt} {mark} {ago:.0f}h ago")
    else:
        L.append("  Compound engine: no action yet (idle below $1 threshold)")
    return "\n".join(L)


def main():
    # ── Chain truth ─────────────────────────────────────────────────
    r = subprocess.run([sys.executable, os.path.join(VAULT_DIR, "discover_positions.py"),
                        "--wallet", WALLET, "--chain", "avalanche", "--json"],
                       capture_output=True, text=True, timeout=120)
    try:
        data = json.loads(r.stdout)
    except Exception:
        print("⚠️ Farm report unavailable: chain read failed — nothing fabricated")
        return 1
    positions = data.get("positions", [])
    balances = data.get("balances", {})
    if not positions:
        print("🌾 Farm report: no LP position — nothing to farm yet")
        return 0

    # ── Feeds (freshness-gated) ─────────────────────────────────────
    lpfeed = load(LPFEED)
    stakfeed = load(STAKFEED)
    pool_apy = lpfeed.get("apy") if lpfeed and feed_age_h(lpfeed) < 48 else None
    staking_apr = stakfeed.get("apr") if stakfeed and feed_age_h(stakfeed) < 48 else None

    # ── Measured earnings: chain-truth fee ledger (drift-adjusted) ──
    # Jordan Sep 3: fees must come from on-chain, with compounding effect.
    # The fee ledger measures drift-adjusted value deltas between sweeps.
    fee_led = load(os.path.join(SCRIPT_DIR, ".steward-fee-ledger.json"))
    fee_note = None
    fee_daily = None
    fee_apr = None
    fee_today = None
    try:
        sys.path.insert(0, VAULT_DIR)
        import steward_fee_ledger as _sfl
        _res = _sfl.run(dry_run=True)   # snapshot + measure, no pointer advance
        fw24 = _sfl.fees_since(time.time() - 86400,
                               _sfl.load()["snapshots"], _res["snapshot"])
        if fw24.get("fees_usd") is not None and fw24.get("window_h"):
            # measured fees over the window → per-day equivalent
            fee_daily = round(fw24["fees_usd"] / fw24["window_h"] * 24, 4)
            fee_note = fw24["note"]
        else:
            fee_note = fw24["note"]
        fee_apr = _res.get("compounded_apr_pct")
    except Exception as _fe:
        fee_note = f"ledger read failed: {_fe}"

    # legacy single-snapshot delta (kept as churn fallback)
    snap = load(SNAPSHOT)
    pos_usd = positions[0].get("positionUsd") or 0
    prev = snap.get("position_usd")
    delta_usd = None
    delta_hours = None
    if prev is not None:
        delta_usd = round(pos_usd - prev, 4)
        delta_hours = round((time.time() - snap.get("ts", time.time())) / 3600, 1)
    json.dump({"ts": time.time(), "position_usd": pos_usd, "price": positions[0].get("livePriceUsd")},
              open(SNAPSHOT, "w"), indent=2)

    alloc = load(ALLOC)
    led = load(LEDGER)
    last_action = next((e for e in reversed(led) if e.get("action") in ("compound", "rebalance")), None)

    print(build_report(positions[0], balances, pool_apy, staking_apr,
                       delta_usd, delta_hours, fee_note,
                       fee_daily=fee_daily, fee_apr=fee_apr,
                       alloc=alloc, last_action=last_action))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())