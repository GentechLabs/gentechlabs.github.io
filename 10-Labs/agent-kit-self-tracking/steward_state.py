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
STATE_FILE = "/root/ProtoJay4789.github.io/Treasury/steward-state.json"


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


def main():
    pos = get_position()
    pool = get_pool()
    # AAE regime-driven allocation (from regime_classifier ground truth, Aug 11)
    alloc = {
        "regime": "RANGE_BOUND",
        "lp": 40,
        "staking": 30,
        "hodl": 15,
        "lending": 15,
        "conf": 0.65,
    }
    state = {
        "updated": datetime.now(timezone(timedelta(hours=-4))).isoformat(),
        "position": pos,
        "pool": pool,
        "allocation": alloc,
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
    pos_val = 43.0
    lp_daily = pos_val * 0.005
    stake_daily = pos_val * 5.2 / 100 / 365
    lines.append("💰 **Yield vs Staking vs HODL**")
    lines.append(f"   • LP:     ~${lp_daily:.2f}/day while in-range (chop rate)")
    lines.append(f"   • Stake:  ~${stake_daily:.2f}/day (5.2% APR)")
    lines.append(f"   • HODL:   {'winning' if pool.get('chg24h', 0) > 0 else 'losing'} ({pool.get('chg24h', 0):+.1f}% 24h)")
    lines.append(f"   • Verdict: {'LP farming the chop' if in_range else 'LP OUT — not earning'}")
    lines.append("")
    lines.append("📅 **Next macro event**: CPI tomorrow 8:30 ET → Bid-Ask at 7:45 ET, Curve back 8/13")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
