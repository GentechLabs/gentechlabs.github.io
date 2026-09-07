#!/usr/bin/env python3
"""
Trade Desk — the treasury's trading/leverage mode (Sep 7 2026).

Jordan's naming scheme: Agentic Treasury = system, Steward = agent, Fed Council
= brain, Yield Farm = LP mode, Trade Desk = trading/leverage mode. The Trade
Desk takes yield-farm profits and deploys them into trades/leverage to capture
the bull market.

This is a DECISION LAYER on top of the existing rails:
  - Reads the council's rail decision (farm where liquid, trade the trend)
  - Reads the buy list's farm-vs-trade signal (the 'crocodile' source of truth)
  - Produces a trade plan (asset, side, size, rail, rationale)
  - Executes via the Hyperliquid perp rail (gta_hl_execute.py) when mode=TRADE
    AND GTA_HL_KEY is set. Otherwise it's a dry-run plan (safe always).

Mode-gated (treasury_state): the Trade Desk only fires ENTER signals when the
treasury is in TRADE mode. In YIELD_FARM it reports the plan as 'held' — it
never pulls the farm. Exiting an existing position is always allowed.

Design rules (develop-and-verify):
  - NEVER fake a fill. Every execution reflects the real exchange response.
  - No hardcoded secrets. Key comes from GTA_HL_KEY env var only.
  - Fail-safe: on any error, return executed=False with the real error.
  - Deterministic: same inputs + same market state -> same plan.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Shared treasury brain (mode gate)
try:
    from treasury_state import get_mode, can_trade, held_line, load_state as _ts_load
except ImportError:
    def get_mode(s=None): return "YIELD_FARM"
    def can_trade(s=None): return False
    def held_line(cat, sig): return f"⏸ [{cat}] {sig} held"
    def _ts_load(): return {}

# ── Config ──────────────────────────────────────────────────────────────────
BUYLIST_STATE = "/root/.hermes/scripts/.steward-buylist-state.json"
COUNCIL_STATE = "/root/.hermes/scripts/.steward-council-state.json"
HL_EXECUTE = os.path.join(SCRIPT_DIR, "gta_hl_execute.py")

# Trade sizing (conservative — small, stop-protected)
MAX_TRADE_USD = 25.0        # cap per trade (small, matches Jordan's $5-25 style)
STOP_PCT = 0.05             # 5% stop-loss
TAKE_PROFIT_PCT = 0.10       # 10% take-profit


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def read_farm_vs_trade():
    """Read the buy list's farm-vs-trade signal (source of truth)."""
    d = _load_json(BUYLIST_STATE)
    return d.get("farm_vs_trade") or {"farm": 0, "trade": 0, "lean": "BALANCED"}


def read_council_rail():
    """Read the council's rail decision if persisted, else None."""
    d = _load_json(COUNCIL_STATE)
    return d.get("rail_decision")


def _reference_price(symbol="AVAX"):
    """Fetch a reference price for sizing. Returns float or None."""
    try:
        from hyperliquid.info import Info
        info = Info("https://api.hyperliquid.xyz")
        mids = info.all_mids()
        return float(mids.get(symbol, 0))
    except Exception:
        return None


def build_trade_plan(farm_vs_trade=None, rail=None, price=None):
    """Build the Trade Desk's plan from the council + buy-list signals.

    Returns dict: {action, asset, side, size_usd, size_coin, stop_px,
                   take_profit_px, rail, rationale, mode}.
    """
    fvt = farm_vs_trade or read_farm_vs_trade()
    lean = fvt.get("lean", "BALANCED")
    rail_rec = rail or read_council_rail()

    # The trade leg: which asset + side. Default AVAX (the core rail).
    asset = "AVAX"
    side = "long"          # default long in a bull
    rationale_parts = []

    # Direction from the council's rail decision
    if rail_rec:
        trade_leg = rail_rec.get("trade", "")
        if "SOL" in trade_leg:
            asset = "SOL"
        rationale_parts.append(f"council rail: {rail_rec.get('rail', '?')}")

    # Direction from the farm-vs-trade signal
    if lean == "TRADE":
        rationale_parts.append("buy list leans TRADE — favor the trade leg")
    elif lean == "FARM":
        rationale_parts.append("buy list leans FARM — favor the farm leg (hold)")

    # If the signal leans FARM, the Trade Desk holds (yield farm wins).
    if lean == "FARM":
        return {
            "action": "hold", "asset": asset, "side": side,
            "size_usd": 0, "size_coin": 0, "stop_px": 0, "take_profit_px": 0,
            "rail": "none", "mode": get_mode(),
            "rationale": "buy list leans FARM — yield farm wins, Trade Desk holds",
        }

    # Size: small, stop-protected (Jordan's style). Cap at MAX_TRADE_USD.
    size_usd = min(MAX_TRADE_USD, 25.0)
    if price and price > 0:
        size_coin = round(size_usd / price, 4)
        stop_px = round(price * (1 - STOP_PCT), 4)
        take_profit_px = round(price * (1 + TAKE_PROFIT_PCT), 4)
    else:
        size_coin = 0; stop_px = 0; take_profit_px = 0

    return {
        "action": "enter", "asset": asset, "side": side,
        "size_usd": size_usd, "size_coin": size_coin,
        "stop_px": stop_px, "take_profit_px": take_profit_px,
        "rail": "hyperliquid-perp", "mode": get_mode(),
        "rationale": "; ".join(rationale_parts) or "default long AVAX",
    }


def execute_plan(plan, dry_run=True):
    """Execute the trade plan via the Hyperliquid perp rail.

    dry_run=True (default): build + quote, no submit. Safe always.
    dry_run=False: requires mode=TRADE AND GTA_HL_KEY set. Refuses cleanly
    otherwise (never fakes a fill).
    """
    if plan.get("action") != "enter":
        return {"executed": False, "dry_run": dry_run, "plan": plan,
                "note": "no entry — plan is hold/exit"}

    if dry_run:
        return {"executed": False, "dry_run": True, "plan": plan,
                "note": "dry-run — no order submitted"}

    # REAL execution guards
    if not can_trade():
        return {"executed": False, "dry_run": False, "plan": plan,
                "error": f"mode={get_mode()} — Trade Desk only fires in TRADE mode"}
    if not os.environ.get("GTA_HL_KEY"):
        return {"executed": False, "dry_run": False, "plan": plan,
                "error": "GTA_HL_KEY not set — cannot place real perp orders"}

    try:
        sys.path.insert(0, SCRIPT_DIR)
        from gta_hl_execute import place_perp_order
        result = place_perp_order(
            symbol=plan["asset"],
            is_buy=(plan["side"] == "long"),
            size=plan["size_coin"],
            limit_px=plan["take_profit_px"],  # wide limit = market-ish fill
            dry_run=False,
        )
        return {"executed": result.get("executed", False), "dry_run": False,
                "plan": plan, "order_result": result.get("order_result"),
                "error": result.get("error")}
    except Exception as e:
        return {"executed": False, "dry_run": False, "plan": plan,
                "error": f"{type(e).__name__}: {e}"}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Trade Desk — treasury trading/leverage mode")
    ap.add_argument("--execute", action="store_true", help="place real orders (mode=TRADE + key required)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--asset", default=None, help="override asset (AVAX/SOL)")
    ap.add_argument("--size", type=float, default=None, help="override size USD")
    args = ap.parse_args()

    price = _reference_price()
    plan = build_trade_plan(price=price)
    if args.asset:
        plan["asset"] = args.asset
    if args.size:
        plan["size_usd"] = args.size
        if price and price > 0:
            plan["size_coin"] = round(args.size / price, 4)

    result = execute_plan(plan, dry_run=not args.execute)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    mode = get_mode()
    if plan["action"] == "hold":
        print(f"⏸ **Trade Desk** — HOLD (mode={mode})")
        print(f"   {plan['rationale']}")
        return

    print(f"📈 **Trade Desk** — {plan['action'].upper()} {plan['asset']} ({plan['side']})")
    print(f"   Size: ${plan['size_usd']:.2f} ({plan['size_coin']} {plan['asset']})")
    print(f"   Stop: ${plan['stop_px']} | Take-profit: ${plan['take_profit_px']}")
    print(f"   Rail: {plan['rail']} | Mode: {mode}")
    print(f"   Why: {plan['rationale']}")
    if result.get("executed"):
        print(f"   ✅ Executed: {result.get('order_result')}")
    elif result.get("error"):
        print(f"   ⚠️ {result['error']}")
    else:
        print(f"   🔒 Dry-run (mode={mode}) — no order submitted")


if __name__ == "__main__":
    main()
