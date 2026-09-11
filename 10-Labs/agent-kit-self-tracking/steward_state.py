#!/usr/bin/env python3
"""
Steward — State Producer for the visual dashboard.
Writes steward-state.json (consumed by steward-dashboard.html) with the live
position + pool data. Called by the heartbeat cron so the dashboard always has
fresh data. Also emits the heartbeat text (kept for the Telegram pulse).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
PAIR = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
STATE_FILE = "/root/repos/gentechlabs.github.io/Treasury/steward-state.json"
# The macro scheduler writes this when it actually enforces a reposition.
MACRO_SCHEDULED_STATE = "/root/.hermes/profiles/gentech-treasury/scripts/.steward-macro-scheduled.json"


def macro_next_action():
    """Read the enforcement state. Return a truthful one-line summary of an
    ACTUALLY-scheduled macro reposition, or None if none is enforced.

    This kills the hardcoded 'CPI tomorrow → Bid-Ask at 7:45' line (Jordan
    Sep 8 2026). That line was printed every heartbeat whether or not any
    reposition was scheduled — it was noise, not instruction. Now the heartbeat
    only reports a reposition that the macro planner ACTUALLY wrote to
    jobs.json (verified via the scheduled-state file). If nothing is enforced,
    the heartbeat says exactly that instead of inventing a schedule.
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


def fetch_json(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Steward/1.0)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def get_position():
    sys.path.insert(0, HERE)
    try:
        from discover_positions import discover_positions
        data = discover_positions("avalanche", WALLET)
        pos = next((p for p in data.get("positions", []) if "error" not in p), None)
        if not pos:
            return {}
        return {
            "read": pos.get("read", ""),
            "shape": "curve",
            "bins": pos.get("bins", 0),
            "rangeLow": pos.get("rangeLow"),
            "rangeHigh": pos.get("rangeHigh"),
            "inRange": pos.get("inRange", False),
        }
    except Exception:
        return {}


def get_pool():
    d = fetch_json(f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{PAIR}")
    if not d or not d.get("pairs"):
        return {}
    p = d["pairs"][0]
    return {
        "price": float(p.get("priceUsd", 0)),
        "chg24h": float(p.get("priceChange", {}).get("h24", 0)),
        "vol24h": float(p.get("volume", {}).get("h24", 0)),
        "liquidity": float(p.get("liquidity", {}).get("usd", 0)),
    }


def get_regime():
    """Read the live regime from the regime classifier state (now BTC-based)."""
    for p in (
        os.path.expanduser("~/.hermes/scripts/.aae-regime-state.json"),
        "/root/.hermes/profiles/gentech-treasury/home/.hermes/scripts/.aae-regime-state.json",
        "/root/.hermes/scripts/.aae-regime-state.json",
    ):
        try:
            with open(p) as f:
                d = json.load(f)
            regime = d.get("regime", "RANGE_BOUND")
            conf = d.get("confidence", 0.5)
            # Map regime -> allocation (regime-driven treasury layers)
            alloc_map = {
                "BULL_TRENDING": {"lp": 30, "staking": 20, "hodl": 40, "lending": 10},
                "PRICE_DISCOVERY": {"lp": 25, "staking": 15, "hodl": 50, "lending": 10},
                "RANGE_BOUND": {"lp": 40, "staking": 30, "hodl": 15, "lending": 15},
                "ACCUMULATION": {"lp": 35, "staking": 25, "hodl": 30, "lending": 10},
                "HIGH_VOLATILITY": {"lp": 20, "staking": 20, "hodl": 40, "lending": 20},
                "BEAR_TRENDING": {"lp": 15, "staking": 20, "hodl": 45, "lending": 20},
            }
            a = alloc_map.get(regime, {"lp": 40, "staking": 30, "hodl": 15, "lending": 15})
            return {"regime": regime, "conf": conf, **a}
        except Exception:
            continue
    return {"regime": "RANGE_BOUND", "lp": 40, "staking": 30, "hodl": 15, "lending": 15, "conf": 0.65}


def _load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def get_operations():
    """Operating picture for the hub: rebalance history, compound activity,
    fee/tier progression, council verdict, and a live activity feed."""
    ops = {"rebalances": [], "compounds": [], "fees": {}, "council": {}, "activity": []}

    # Rebalance history — from silence state (recent rebalance attempts)
    silence = _load_json(
        "/root/.hermes/profiles/gentech-treasury/scripts/.steward-silence-state.json")
    if silence:
        for key in ("rebalance", "auto-deploy"):
            v = silence.get(key)
            if isinstance(v, dict):
                ops["rebalances"].append({
                    "type": key,
                    "since": v.get("since"),
                    "resolved": v.get("resolved", False),
                    "err": (v.get("err") or "")[:200],
                })

    # Compound activity — last 8 entries from the ledger
    ledger = _load_json(
        "/root/.hermes/profiles/gentech-treasury/scripts/.compound-ledger.json")
    if isinstance(ledger, list):
        for e in ledger[-8:]:
            ops["compounds"].append({
                "ts": e.get("ts"),
                "action": e.get("action"),
                "amount_usd": e.get("amount_usd"),
                "ok": e.get("ok"),
                "reasons": e.get("reasons", []),
            })

    # Fee / tier progression — from fee ledger + farm snapshot
    fee_ledger = _load_json(
        "/root/.hermes/profiles/gentech-treasury/scripts/.steward-fee-ledger.json")
    if isinstance(fee_ledger, dict):
        snaps = fee_ledger.get("snapshots", [])
        if snaps:
            ops["fees"]["last_total"] = snaps[-1].get("total_usd")
            ops["fees"]["last_price"] = snaps[-1].get("price_usd")
            ops["fees"]["snapshot_count"] = len(snaps)
    farm = _load_json(
        "/root/.hermes/profiles/gentech-treasury/scripts/.farm-snapshot.json")
    if farm:
        ops["fees"]["position_usd"] = farm.get("position_usd")
        ops["fees"]["price"] = farm.get("price")

    # Council verdict — from treasury-state.json
    tstate = _load_json("/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/treasury-state.json")
    if tstate:
        ops["council"] = {
            "mode": tstate.get("mode"),
            "regime": (tstate.get("regime") or {}).get("value"),
            "autonomy": (tstate.get("autonomy") or {}).get("granted"),
        }

    # Activity feed — merge rebalances + compounds into a chronological feed
    for r in ops["rebalances"]:
        ops["activity"].append({"kind": "rebalance", "type": r["type"],
                                "since": r["since"], "resolved": r["resolved"]})
    for c in ops["compounds"]:
        ops["activity"].append({"kind": "compound", "action": c["action"],
                                "ts": c["ts"], "amount_usd": c["amount_usd"],
                                "ok": c["ok"]})
    def _act_key(a):
        ts = a.get("ts")
        if isinstance(ts, (int, float)):
            return ts
        since = a.get("since")
        if since:
            try:
                from datetime import datetime, timezone
                return datetime.fromisoformat(since.replace("Z", "+00:00")).timestamp()
            except Exception:
                return 0.0
        return 0.0

    ops["activity"].sort(key=_act_key, reverse=True)
    ops["activity"] = ops["activity"][:12]
    return ops


def main():
    pos = get_position()
    pool = get_pool()
    # AAE regime-driven allocation (from regime_classifier ground truth, Aug 11)
    alloc = get_regime()
    # Operating picture for the hub (rebalances, compounds, fees, council, activity)
    ops = get_operations()
    state = {
        "updated": datetime.now(timezone(timedelta(hours=-4))).isoformat(),
        "position": pos,
        "pool": pool,
        "allocation": alloc,
        "operations": ops,
    }
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    # Also emit the heartbeat text (kept for the Telegram pulse)
    in_range = pos.get("inRange", False)
    icon = "🟢" if in_range else "🔴"
    lines = [
        f"🛡️ STEWARD HEARTBEAT — {datetime.now(timezone(timedelta(hours=-4))).strftime('%Y-%m-%d %H:%M ET')}",
        "",
        f"{icon} **Position**: {pos.get('read', 'n/a')}",
        f"   Shape: Curve · {pos.get('bins', 0)} bins · range ${pos.get('rangeLow', 0):.4f}–${pos.get('rangeHigh', 0):.4f}",
        f"   Fee efficiency: {100 if in_range else 0}% {'✅ earning' if in_range else '⚠️ OUT — not earning'}",
        "",
    ]
    if pool:
        lines.append(f"📊 **Market**: AVAX ${pool.get('price', 0):.2f} ({pool.get('chg24h', 0):+.1f}% 24h) · vol ${pool.get('vol24h', 0)/1e6:.1f}M · liq ${pool.get('liquidity', 0)/1e6:.1f}M")
        lines.append("")
    pos_val = float(pos.get("positionUsd") or 0)
    # Blackhole-aware yield estimate (Jordan Sep 10 2026): use the live vfat
    # fee/emissions split, not the old LFJ-era 0.5%/day chop. Staking baseline
    # is the real sAVAX/Benqi rate (3.77%), not the stale 5.2%. Labeled estimate.
    try:
        import vfat_blackhole
        bh = vfat_blackhole.fetch()
        if "error" in bh:
            fee_apr, bh_src = 26.9, "cached (vfat down)"
        else:
            fee_apr, bh_src = bh.get("fee_apr", 26.9), "vfat live"
    except Exception:
        fee_apr, bh_src = 26.9, "cached"
    lp_daily = pos_val * fee_apr / 100 / 365
    stake_daily = pos_val * 3.77 / 100 / 365
    lines.append("💰 **Yield vs Staking vs HODL**")
    lines.append(f"   • LP:     ~${lp_daily:.2f}/day ({fee_apr:.1f}% fee APR, {bh_src})")
    lines.append(f"   • Stake:  ~${stake_daily:.2f}/day (3.8% APR sAVAX)")
    lines.append(f"   • HODL:   {'winning' if pool.get('chg24h', 0) > 0 else 'losing'} ({pool.get('chg24h', 0):+.1f}% 24h)")
    lines.append(f"   • Verdict: {'LP farming the chop' if in_range else 'LP OUT — not earning'}")
    lines.append("")
    macro = macro_next_action()
    if macro:
        lines.append("")
        lines.append(f"📅 **Macro (enforced)**: {macro}")
    else:
        lines.append("")
        lines.append("📅 **Macro**: no reposition currently scheduled (planner enforces when a CPI/FOMC/NFP is <36h out)")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
