#!/usr/bin/env python3
"""
Steward — Position Heartbeat (twice-an-hour status)
====================================================
Jordan's ask (Aug 11 2026): the watchdog is silent when healthy (good — no
noise), but he still wants a REGULAR heartbeat ~2x/hour so he can SEE:
  - what the position looks like (shape, range, bins)
  - fee efficiency
  - how the yield farm is doing vs staking and hodlers

This is a SEPARATE job from the silent watchdog. It always emits a compact
status line (never silent), so Jordan gets a twice-an-hour pulse on the
Steward's position. Reads LIVE on-chain data via discover_positions + a fresh
yield-vs-staking-vs-hodl comparison.

Used by a no_agent cron at */30 (twice an hour).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
PAIR = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
MACRO_SCHEDULED_STATE = "/root/.hermes/profiles/gentech-treasury/scripts/.steward-macro-scheduled.json"
LEDGER_PATH = "/root/.hermes/profiles/gentech-treasury/scripts/.compound-ledger.json"


def macro_next_action():
    """Truthful one-line summary of an ACTUALLY-enforced macro reposition, or
    None. Replaces the old hardcoded 'CPI tomorrow 8:30 ET' line (Jordan
    Sep 8 2026) which printed a schedule the machine never enforced. The
    heartbeat now only reports a reposition the planner wrote to jobs.json.
    """
    try:
        with open(MACRO_SCHEDULED_STATE) as f:
            d = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    rebal = d.get("rebalance") or {}
    label = d.get("label", "macro event")
    run_at = rebal.get("run_at", "")
    return f"{label}: BID_ASK scheduled {run_at[:16].replace('T', ' ')} UTC → stand-down CURVE"


def _now_et() -> str:
    from datetime import timedelta
    return datetime.now(timezone(timedelta(hours=-4))).strftime("%Y-%m-%d %H:%M ET")


def in_farm_days() -> float:
    """Days since first fund-moving deploy (from compound-ledger ok entries)."""
    try:
        with open(LEDGER_PATH) as f:
            ledger = json.load(f)
    except FileNotFoundError:
        return 0.0
    def pt(ts):
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        try:
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:
            return None
    first = None
    for e in ledger:
        if not isinstance(e, dict):
            continue
        if e.get("action") in ("compound", "rebalance") and e.get("ok"):
            t = pt(e.get("ts"))
            if t and (first is None or t < first):
                first = t
    if first is None:
        return 0.0
    return max(0.0, (datetime.now(timezone.utc) - first).total_seconds() / 86400)


def fetch_json(url: str, timeout: int = 12):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Steward/1.0)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def get_position() -> dict:
    sys.path.insert(0, HERE)
    try:
        from discover_positions import discover_positions
        data = discover_positions("avalanche", WALLET)
        pos = next((p for p in data.get("positions", []) if "error" not in p), None)
        if not pos:
            return {"error": "no position"}
        return pos
    except Exception as e:
        return {"error": str(e)}


def get_pool_stats() -> dict:
    """Live pool price/volume/liquidity from DexScreener."""
    d = fetch_json(f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{PAIR}")
    if not d or not d.get("pairs"):
        return {}
    p = d["pairs"][0]
    return {
        "price": float(p.get("priceUsd", 0)),
        "vol24h": float(p.get("volume", {}).get("h24", 0)),
        "liquidity": float(p.get("liquidity", {}).get("usd", 0)),
        "chg24h": float(p.get("priceChange", {}).get("h24", 0)),
    }


def get_avax_price() -> float:
    d = fetch_json("https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd")
    if d:
        return float(d.get("avalanche-2", {}).get("usd", 0))
    return 0.0


def main() -> int:
    pos = get_position()
    pool = get_pool_stats()
    avax_usd = get_avax_price() or pool.get("price", 0)

    lines = [f"🛡️ STEWARD HEARTBEAT — {_now_et()}"]

    if "error" in pos:
        lines.append(f"   ⚠️ {pos['error']}")
        print("\n".join(lines))
        return 0

    # Position
    in_range = pos.get("inRange", False)
    icon = "🟢" if in_range else "🔴"
    ptype = pos.get("type", "")
    pname = pos.get("name", "LP position")
    lines.append(f"   {icon} {pname} · {pos.get('read', 'n/a')}")
    if ptype == "blackhole_cl":
        # CL position: show tick range + liquidity, not LFJ bin shape
        lines.append(f"   CL position #{pos.get('tokenId')} · ticks {pos.get('tickLower')}–{pos.get('tickUpper')} · "
                     f"range ${pos.get('rangeLow', 0):.4f}–${pos.get('rangeHigh', 0):.4f}")
    else:
        lines.append(f"   Shape: Curve · {pos.get('bins', 0)} bins · "
                     f"range ${pos.get('rangeLow', 0):.4f}–${pos.get('rangeHigh', 0):.4f}")

    # Fee efficiency (IN range = earning; OUT = 0)
    eff = 100.0 if in_range else 0.0
    lines.append(f"   Fee efficiency: {eff:.0f}% {'(earning)' if in_range else '(OUT — not earning)'}")

    # Pool context
    if pool:
        lines.append(f"   AVAX ${pool.get('price', 0):.2f} ({pool.get('chg24h', 0):+.1f}% 24h) · "
                     f"vol ${pool.get('vol24h', 0)/1e6:.1f}M · liq ${pool.get('liquidity', 0)/1e6:.1f}M")

    # Yield vs staking vs hodl (honest comparison)
    # Position value: read LIVE from on-chain (discover_positions returns
    # positionUsd). Jordan Sep 8 2026: the old hardcoded pos_val=43.0 (Aug 11)
    # was FABRICATED — the real position is ~$25-28. Never print a stale
    # number; read the chain.
    pos_val = float(pos.get("positionUsd") or 0)
    lines.append("   ── Yield vs Staking vs HODL ──")
    farm_days = in_farm_days()
    lines.append(f"   ⏳ In pool: {farm_days:.1f} days farming (since first deploy)")
    if pos_val:
        # LP daily fee estimate: ~0.5% of position/day WHILE IN RANGE in chop
        # (calibrated from the brain: $0.24/day on $46.59 = 0.515%/day). This is
        # NOT a stable APR — it only holds while in range and price is moving.
        lp_daily = pos_val * 0.005
        staking_apr = 5.2  # AVAX staking baseline
        staking_daily = pos_val * staking_apr / 100 / 365
        lines.append(f"   LP:     ~${lp_daily:.2f}/day while in-range (chop rate)")
        lines.append(f"   Stake:  ~${staking_daily:.2f}/day ({staking_apr:.1f}% APR)")
        lines.append(f"   HODL:   {'winning' if pool.get('chg24h',0)>0 else 'losing'} "
                     f"({pool.get('chg24h',0):+.1f}% 24h)")
        verdict = "LP farming the chop" if in_range else "LP OUT — not earning"
        lines.append(f"   Verdict: {verdict}")
    else:
        lines.append("   (position USD not measured on-chain — see full report)")

    # Macro countdown — truthful (only shows an actually-enforced reposition)
    macro = macro_next_action()
    if macro:
        lines.append(f"   📅 {macro}")
    else:
        lines.append("   📅 No macro reposition currently scheduled (planner enforces when CPI/FOMC/NFP <36h out)")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
