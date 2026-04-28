#!/usr/bin/env python3
"""
LFJ On-Chain Position Reader
Fetches live AVAX price + computes position value from pool contract.
Output: JSON with position data for cron job consumption.

Pool: LFJ V2.2 AVAX/USDC (binStep 10, 5 bps)
Chain: Avalanche C-Chain
"""
import json
import math
import os
import sys
import time
import urllib.request
from typing import Optional

# ─── Config ───────────────────────────────────────────────────────────
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
RPC_URL = "https://api.avax.network/ext/bc/C/rpc"
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/avalanche/" + POOL_ADDRESS
CONFIG_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-aae-config.json")
POSITION_STATE = os.path.expanduser("~/.hermes/scripts/.lfj-position-state.json")

# AVAX/USDC token addresses (for ERC-20 balance checks)
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"

# ─── RPC Helpers ──────────────────────────────────────────────────────
def rpc_call(to: str, data: str, label: str = "") -> Optional[str]:
    """Raw eth_call — returns hex result or None on error."""
    payload = json.dumps({
        "jsonrpc": "2.0", "method": "eth_call",
        "params": [{"to": to, "data": data}, "latest"], "id": 1
    }).encode()
    req = urllib.request.Request(RPC_URL, data=payload,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
        if "error" in result:
            return None
        return result.get("result", "0x")
    except Exception:
        return None

# ─── Price Feed ──────────────────────────────────────────────────────
def fetch_price_dexscreener() -> Optional[float]:
    """Get AVAX price from DexScreener."""
    try:
        req = urllib.request.Request(DEXSCREENER_URL,
            headers={"User-Agent": "Gentech-Labs/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        pair = data.get("pairs", [{}])[0] if data.get("pairs") else {}
        price = float(pair.get("priceNative", 0))
        if price > 0:
            return price
    except Exception:
        pass
    return None

def fetch_price_onchain() -> Optional[float]:
    """Get AVAX price from pool's getSwapOut (1 AVAX → USDC)."""
    # getSwapOut(uint128,bool) with 1 AVAX (1e18) and swapForY=true
    data = ("0xe77366f8"
            "0000000000000000000000000000000000000000000000000de0b6b3a7640000"
            "0000000000000000000000000000000000000000000000000000000000000001")
    result = rpc_call(POOL_ADDRESS, data)
    if result and len(result) >= 130:
        amount_out = int(result[2 + 64:2 + 128], 16)
        price = amount_out / 1e6
        if price > 0:
            return price
    return None

def get_avax_price() -> dict:
    """Get AVAX price with fallback chain: DexScreener → on-chain."""
    price = fetch_price_dexscreener()
    if price:
        return {"price": price, "source": "dexscreener"}

    price = fetch_price_onchain()
    if price:
        return {"price": price, "source": "onchain"}

    return {"price": 0, "source": "unavailable"}

# ─── Pool State ──────────────────────────────────────────────────────
def get_active_bin() -> Optional[int]:
    """Get the current active bin ID from the pool."""
    result = rpc_call(POOL_ADDRESS, "0xdbe65edc")  # getActiveId()
    if result and result != "0x":
        return int(result, 16)
    return None

def get_bin_reserves() -> Optional[dict]:
    """Get total pool reserves via getReserves()."""
    result = rpc_call(POOL_ADDRESS, "0x0902f1ac")
    if result and len(result) >= 130:
        r0 = int(result[2:66], 16)
        r1 = int(result[66:130], 16)
        return {"avax": r0 / 1e18, "usdc": r1 / 1e6}
    return None

# ─── Position Math ───────────────────────────────────────────────────
def compute_position_value(config: dict, price: float) -> dict:
    """
    Compute position value from config token amounts + live price.
    For a concentrated liquidity position, the token amounts change with price.
    We use the config's current amounts as the base and compute value directly.
    """
    pos = config.get("position", {})
    token0_amount = pos.get("token0_amount", 0)  # AVAX
    token1_amount = pos.get("token1_amount", 0)  # USDC
    range_low = pos.get("range_low", 9.00)
    range_high = pos.get("range_high", 9.30)
    shape = pos.get("shape", "bid-ask")

    # Current value = AVAX * price + USDC
    avax_value = token0_amount * price
    usdc_value = token1_amount
    total_value = avax_value + usdc_value

    # Position within range (0% = bottom, 100% = top)
    if range_high > range_low:
        price_position = (price - range_low) / (range_high - range_low) * 100
    else:
        price_position = 50.0

    in_range = range_low <= price <= range_high

    # Token split percentages
    avax_split = (avax_value / total_value * 100) if total_value > 0 else 0
    usdc_split = (usdc_value / total_value * 100) if total_value > 0 else 0

    # Compute shape skew (how far from balanced 50/50)
    skew = abs(avax_split - 50)

    # Determine shape description
    if skew < 5:
        shape_desc = "Balanced"
    elif avax_split > usdc_split:
        shape_desc = f"AVAX-heavy ({avax_split:.0f}/{usdc_split:.0f})"
    else:
        shape_desc = f"USDC-heavy ({usdc_split:.0f}/{avax_split:.0f})"

    # Fee efficiency (rough estimate based on position within range)
    # Max efficiency at center (50%), min at edges
    efficiency = (1 - abs(price_position - 50) / 50) * 100

    # Entry data for IL calculation
    entry_total = config["position"].get("total_usd", total_value)
    entry_avax = config["position"].get("token0_amount", token0_amount)

    return {
        "price": round(price, 4),
        "in_range": in_range,
        "range_low": range_low,
        "range_high": range_high,
        "price_position_pct": round(price_position, 1),
        "avax_amount": round(token0_amount, 4),
        "usdc_amount": round(token1_amount, 2),
        "avax_value": round(avax_value, 2),
        "usdc_value": round(usdc_value, 2),
        "total_value_usd": round(total_value, 2),
        "avax_split_pct": round(avax_split, 1),
        "usdc_split_pct": round(usdc_split, 1),
        "shape": shape,
        "shape_description": shape_desc,
        "skew_pct": round(skew, 1),
        "fee_efficiency_pct": round(efficiency, 1),
        "entry_total_usd": entry_total,
    }

# ─── State Tracking ──────────────────────────────────────────────────
def load_state() -> dict:
    try:
        with open(POSITION_STATE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_update": None, "price_history": []}

def save_state(state: dict):
    with open(POSITION_STATE, "w") as f:
        json.dump(state, f, indent=2)

def update_price_history(state: dict, price: float):
    """Keep last 24 hourly price snapshots."""
    now = time.time()
    history = state.get("price_history", [])
    # Add new entry
    history.append({"ts": now, "price": price})
    # Keep only last 24h
    cutoff = now - 86400
    history = [h for h in history if h["ts"] > cutoff]
    state["price_history"] = history

# ─── Main ─────────────────────────────────────────────────────────────
def main():
    # Load config
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Config load failed: {e}"}))
        sys.exit(1)

    # Get live price
    price_data = get_avax_price()
    if price_data["price"] <= 0:
        print(json.dumps({"error": "Failed to fetch AVAX price"}))
        sys.exit(1)

    price = price_data["price"]

    # Get pool state
    active_bin = get_active_bin()
    reserves = get_bin_reserves()

    # Compute position
    position = compute_position_value(config, price)

    # Update state
    state = load_state()
    update_price_history(state, price)
    state["last_update"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    state["last_price"] = price
    save_state(state)

    # Build output
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pool": {
            "address": POOL_ADDRESS,
            "chain": "avalanche",
            "active_bin": active_bin,
            "reserves_avax": round(reserves["avax"], 2) if reserves else None,
            "reserves_usdc": round(reserves["usdc"], 2) if reserves else None,
        },
        "price": {
            "avax_usd": price,
            "source": price_data["source"],
            "24h_avg": round(
                sum(h["price"] for h in state.get("price_history", [])) /
                max(len(state.get("price_history", [])), 1), 4
            ),
        },
        "position": position,
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
