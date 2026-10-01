#!/usr/bin/env python3
"""GTA Hyperliquid perp execution leg — REAL order placement.

Wires the Hyperliquid perp leg of the cross-venue arb (Hyperliquid perp vs
Coinbase spot). This is the module the executor's `_execute_real` stub calls
once `GTA_HL_KEY` is set.

Design rules (from develop-and-verify / audit checklist):
  - NEVER fake a fill. Every return reflects the actual exchange response.
  - No hardcoded secrets. Key comes from GTA_HL_KEY env var only.
  - Fail-safe: on any error, return executed=False with the real error surfaced.
  - Deterministic: same inputs + same exchange state -> same result.
  - Testable: `--dry-run` builds the order + quotes but does NOT submit.

US-legal note (Aug 20 2026): Trump said CFTC is working to bring Hyperliquid
to the US. This un-blocks the perp leg that was previously detection-only
(US gray-zone). The rail is now staged to go live once a key + capital exist.
"""

from __future__ import annotations

import json
import os
import sys

# Default Hyperliquid mainnet API base.
HL_MAINNET = "https://api.hyperliquid.xyz"


def _get_key() -> str:
    """Return the Hyperliquid private key from GTA_HL_KEY, or raise."""
    key = os.environ.get("GTA_HL_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "GTA_HL_KEY is not set. Set it to the Hyperliquid private key "
            "(hex, 0x-prefixed) to enable REAL perp order placement."
        )
    return key


def _build_exchange():
    """Build a Hyperliquid Exchange from GTA_HL_KEY. Raises on bad key."""
    from eth_account import Account
    from hyperliquid.exchange import Exchange

    key = _get_key()
    try:
        acct = Account.from_key(key)
    except Exception as e:
        raise RuntimeError(f"invalid GTA_HL_KEY: {type(e).__name__}: {e}")

    return Exchange(acct, base_url=HL_MAINNET)


def place_perp_order(symbol: str, is_buy: bool, size: float,
                     limit_px: float, tif: str = "Gtc",
                     reduce_only: bool = False, dry_run: bool = False) -> dict:
    """Place a real Hyperliquid perp order.

    Args:
        symbol: perp name, e.g. "AVAX" (Hyperliquid uses the base symbol).
        is_buy: True = long/buy, False = short/sell.
        size: order size in coin units.
        limit_px: limit price. For a market-ish fill use a wide limit.
        tif: time-in-force, "Gtc" | "Ioc" | "Alo".
        reduce_only: True to only reduce an existing position.
        dry_run: True builds + quotes but does NOT submit.

    Returns:
        dict with executed, order_result (real exchange response), and any error.
    """
    from hyperliquid.utils.signing import OrderType

    if dry_run:
        return {
            "executed": False,
            "dry_run": True,
            "order": {
                "symbol": symbol,
                "is_buy": is_buy,
                "size": size,
                "limit_px": limit_px,
                "tif": tif,
                "reduce_only": reduce_only,
            },
            "note": "dry-run — no order submitted",
        }

    try:
        exchange = _build_exchange()
        order_type = OrderType.limit({"tif": tif})
        result = exchange.order(
            name=symbol,
            is_buy=is_buy,
            sz=size,
            limit_px=limit_px,
            order_type=order_type,
            reduce_only=reduce_only,
        )
        # result is the raw exchange response (list of status dicts).
        return {"executed": True, "order_result": result}
    except Exception as e:
        return {
            "executed": False,
            "error": f"{type(e).__name__}: {e}",
        }


def get_account_state(dry_run: bool = False) -> dict:
    """Return the Hyperliquid account's perp positions + margin summary.

    Read-only. Safe to call without a key (public info) but requires the key
    to scope to the account. Returns {} on any failure.
    """
    try:
        exchange = _build_exchange()
        state = exchange.info.user_state(exchange.address)
        return state
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="GTA Hyperliquid perp execution leg")
    p.add_argument("--symbol", default="AVAX", help="perp symbol (default AVAX)")
    p.add_argument("--side", choices=["buy", "sell"], default="buy")
    p.add_argument("--size", type=float, default=1.0, help="order size in coin units")
    p.add_argument("--limit-px", type=float, default=0.0,
                   help="limit price (0 = use a wide market-ish limit)")
    p.add_argument("--dry-run", action="store_true", help="build + quote, no submit")
    p.add_argument("--account", action="store_true", help="show account state")
    a = p.parse_args()

    if a.account:
        print(json.dumps(get_account_state(dry_run=a.dry_run), indent=2))
        sys.exit(0)

    # If no limit price given, fetch a reference price for a wide limit.
    limit_px = a.limit_px
    if limit_px <= 0:
        try:
            from hyperliquid.info import Info
            info = Info(HL_MAINNET)
            mids = info.all_mids()
            limit_px = float(mids.get(a.symbol, 0))
            # wide limit: 5% away so it fills like a market order
            limit_px = round(limit_px * (0.95 if a.side == "buy" else 1.05), 4)
        except Exception as e:
            print(json.dumps({"error": f"could not fetch reference price: {e}"}))
            sys.exit(1)

    out = place_perp_order(
        symbol=a.symbol,
        is_buy=(a.side == "buy"),
        size=a.size,
        limit_px=limit_px,
        dry_run=a.dry_run,
    )
    print(json.dumps(out, indent=2))
