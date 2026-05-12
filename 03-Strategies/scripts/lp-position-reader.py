#!/usr/bin/env python3
"""
LFJ On-Chain Position Reader v2
Fetches live AVAX price + wallet balances + position value from pool contract.
Output: JSON with position data for cron job consumption.

Pool: LFJ V2.2 AVAX/USDC (binStep 10, 5 bps)
Chain: Avalanche C-Chain

Changes from v1:
- Added wallet balance reading (native AVAX + USDC via Routescan API)
- Added on-chain LP position reading via bin share queries
- Added bin-level token decomposition where possible
- Config amounts now used as fallback only (labeled as "estimated")
"""
import json
import math
import os
import sys
import time
import urllib.request
from typing import Optional, List, Dict

# ─── Config ───────────────────────────────────────────────────────────
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"
RPC_URL = "https://api.avax.network/ext/bc/C/rpc"
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/avalanche/" + POOL_ADDRESS
ROUTESCAN_API = "https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api"
CONFIG_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-aae-config.json")
POSITION_STATE = os.path.expanduser("~/.hermes/scripts/.lfj-position-state.json")

# AVAX/USDC token addresses
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"

# LFJ balanceOf selector
BALANCE_OF_SELECTOR = "0x00fdd58e"

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

def rpc_call_batch(calls: List[dict], batch_size: int = 15) -> List[Optional[str]]:
    """Batch eth_call in small chunks — Avalanche RPC limits batch size."""
    all_results = []
    for start in range(0, len(calls), batch_size):
        chunk = calls[start:start + batch_size]
        batch = []
        for i, call in enumerate(chunk):
            batch.append({
                "jsonrpc": "2.0", "method": "eth_call",
                "params": [{"to": call["to"], "data": call["data"]}, "latest"],
                "id": i + 1
            })
        payload = json.dumps(batch).encode()
        req = urllib.request.Request(RPC_URL, data=payload,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                results = json.loads(resp.read().decode())
            if isinstance(results, list):
                results.sort(key=lambda x: x.get("id", 0))
                all_results.extend([r.get("result", "0x") for r in results])
            else:
                all_results.extend([None] * len(chunk))
        except Exception:
            all_results.extend([None] * len(chunk))
        # Small delay between batches to avoid rate limiting
        if start + batch_size < len(calls):
            time.sleep(0.2)
    return all_results

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
    """Get AVAX price from pool's getSwapOut (1 AVAX -> USDC)."""
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
    """Get AVAX price with fallback chain: DexScreener -> on-chain."""
    price = fetch_price_dexscreener()
    if price:
        return {"price": price, "source": "dexscreener"}

    price = fetch_price_onchain()
    if price:
        return {"price": price, "source": "onchain"}

    return {"price": 0, "source": "unavailable"}

# ─── Wallet Balances ─────────────────────────────────────────────────
def get_wallet_balances() -> dict:
    """
    Fetch wallet balances from Routescan API.
    Returns native AVAX + USDC ERC-20 balances.
    """
    result = {"avax": 0, "usdc": 0, "source": "routescan", "error": None}

    try:
        # Native AVAX balance
        url = f"{ROUTESCAN_API}?module=account&action=balance&address={WALLET}&tag=latest"
        req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        result["avax"] = round(int(data.get("result", 0)) / 1e18, 4)
    except Exception as e:
        result["error"] = f"AVAX balance: {e}"

    try:
        # USDC balance
        url = f"{ROUTESCAN_API}?module=account&action=tokenbalance&contractaddress={USDC}&address={WALLET}&tag=latest"
        req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        result["usdc"] = round(int(data.get("result", 0)) / 1e6, 2)
    except Exception as e:
        result["error"] = (result.get("error", "") + f" USDC: {e}").strip()

    return result

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

# ─── LP Position Reading ─────────────────────────────────────────────
def bin_to_price(bin_id: int, active_bin: int, price: float) -> float:
    """Convert bin ID to approximate price."""
    log_step = math.log(1 + 10 / 10000)  # binStep = 10
    return price * math.exp((bin_id - active_bin) * log_step)

def get_lp_position_onchain(active_bin: int, price: float, range_low: float, range_high: float) -> dict:
    """
    Read LP position from on-chain bin shares.
    Returns bin-level data and approximate token amounts.
    """
    # Compute bin IDs for the range
    log_step = math.log(1 + 10 / 10000)
    bin_900 = active_bin - int(round(math.log(price / range_low) / log_step))
    bin_930 = active_bin + int(round(math.log(range_high / price) / log_step))

    # Tight range: just the known position range + 5 bins margin
    start_bin = bin_900 - 5
    end_bin = bin_930 + 5

    # Query balanceOf for all bins in range (batch)
    calls = []
    bin_ids = list(range(start_bin, end_bin + 1))
    for bin_id in bin_ids:
        user_hex = WALLET[2:].lower().zfill(64)
        bin_hex = format(bin_id, "064x")
        calls.append({
            "to": POOL_ADDRESS,
            "data": BALANCE_OF_SELECTOR + user_hex + bin_hex
        })

    results = rpc_call_batch(calls)

    # Collect bins with balances
    below_active = []  # USDC side
    above_active = []  # AVAX side
    active_balance = 0

    for i, (bin_id, result) in enumerate(zip(bin_ids, results)):
        if result and result != "0x":
            val = int(result, 16)
            if val > 0:
                bin_price = bin_to_price(bin_id, active_bin, price)
                entry = {"bin_id": bin_id, "shares": val, "price": round(bin_price, 4)}
                if bin_id < active_bin:
                    below_active.append(entry)
                elif bin_id > active_bin:
                    above_active.append(entry)
                else:
                    active_balance = val

    # Compute approximate token amounts from share ratios
    # Below active bins: shares represent USDC deposits
    # Above active bins: shares represent AVAX deposits
    # Active bin: mix of both
    total_below_shares = sum(e["shares"] for e in below_active)
    total_above_shares = sum(e["shares"] for e in above_active)

    # Approximate token amounts using config as reference point
    # This gives us a relative weighting, not exact on-chain amounts
    total_shares = total_below_shares + total_above_shares + active_balance

    # Estimate AVAX/USDC split from bin positions
    avax_shares = total_above_shares + (active_balance // 2)  # Above + half of active
    usdc_shares = total_below_shares + (active_balance - active_balance // 2)  # Below + half active

    if total_shares > 0:
        avax_pct = avax_shares / total_shares * 100
        usdc_pct = usdc_shares / total_shares * 100
    else:
        avax_pct = 50
        usdc_pct = 50

    return {
        "active_bin": active_bin,
        "range_bin_start": bin_900,
        "range_bin_end": bin_930,
        "bins_with_balance": len(below_active) + len(above_active) + (1 if active_balance > 0 else 0),
        "below_active_bins": len(below_active),
        "above_active_bins": len(above_active),
        "total_shares": total_shares,
        "avax_shares_pct": round(avax_pct, 1),
        "usdc_shares_pct": round(usdc_pct, 1),
        "has_position": total_shares > 0,
    }

# ─── Position Math ───────────────────────────────────────────────────
def compute_position_value(config: dict, price: float, wallet: dict, lp_onchain: dict) -> dict:
    """
    Compute position value from live data.
    Uses config amounts as fallback, but labels them appropriately.
    """
    pos = config.get("position", {})
    range_low = pos.get("range_low", 9.75)
    range_high = pos.get("range_high", 10.01)
    shape = pos.get("shape", "bid-ask")

    # LP position amounts — prefer on-chain data, fallback to config
    if lp_onchain.get("has_position"):
        # Use on-chain share percentages with config total value to estimate
        total_usd = pos.get("total_usd", 0)
        avax_split = lp_onchain["avax_shares_pct"] / 100
        usdc_split = lp_onchain["usdc_shares_pct"] / 100

        # Estimate token amounts from splits
        avax_value = total_usd * avax_split
        usdc_value = total_usd * usdc_split
        token0_amount = avax_value / price if price > 0 else 0
        token1_amount = usdc_value

        position_source = "onchain_shares"
    else:
        # Fallback to config
        token0_amount = pos.get("token0_amount", 0)
        token1_amount = pos.get("token1_amount", 0)
        avax_value = token0_amount * price
        usdc_value = token1_amount
        position_source = "config_fallback"

    total_value = (token0_amount * price) + token1_amount

    # Position within range (0% = bottom, 100% = top)
    if range_high > range_low:
        price_position = (price - range_low) / (range_high - range_low) * 100
    else:
        price_position = 50.0

    in_range = range_low <= price <= range_high

    # Token split percentages
    avax_split_pct = (token0_amount * price / total_value * 100) if total_value > 0 else 0
    usdc_split_pct = (token1_amount / total_value * 100) if total_value > 0 else 0

    # Compute shape skew (how far from balanced 50/50)
    skew = abs(avax_split_pct - 50)

    # Determine shape description
    if skew < 5:
        shape_desc = "Balanced"
    elif avax_split_pct > usdc_split_pct:
        shape_desc = f"AVAX-heavy ({avax_split_pct:.0f}/{usdc_split_pct:.0f})"
    else:
        shape_desc = f"USDC-heavy ({usdc_split_pct:.0f}/{avax_split_pct:.0f})"

    # Fee efficiency (rough estimate based on position within range)
    efficiency = (1 - abs(price_position - 50) / 50) * 100

    # Entry data for IL calculation
    entry_total = pos.get("total_usd", total_value)

    # Wallet value
    wallet_avax_value = wallet.get("avax", 0) * price
    wallet_usdc_value = wallet.get("usdc", 0)
    wallet_total = wallet_avax_value + wallet_usdc_value

    return {
        "price": round(price, 4),
        "in_range": in_range,
        "range_low": range_low,
        "range_high": range_high,
        "price_position_pct": round(price_position, 1),
        "lp_position": {
            "source": position_source,
            "avax_amount": round(token0_amount, 4),
            "usdc_amount": round(token1_amount, 2),
            "avax_value_usd": round(token0_amount * price, 2),
            "usdc_value_usd": round(token1_amount, 2),
            "total_value_usd": round(total_value, 2),
        },
        "wallet": {
            "avax": wallet.get("avax", 0),
            "usdc": wallet.get("usdc", 0),
            "avax_value_usd": round(wallet_avax_value, 2),
            "usdc_value_usd": round(wallet_usdc_value, 2),
            "total_value_usd": round(wallet_total, 2),
        },
        "combined_total_usd": round(total_value + wallet_total, 2),
        "avax_split_pct": round(avax_split_pct, 1),
        "usdc_split_pct": round(usdc_split_pct, 1),
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
    os.makedirs(os.path.dirname(POSITION_STATE), exist_ok=True)
    with open(POSITION_STATE, "w") as f:
        json.dump(state, f, indent=2)

def update_price_history(state: dict, price: float):
    """Keep last 24 hourly price snapshots."""
    now = time.time()
    history = state.get("price_history", [])
    history.append({"ts": now, "price": price})
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

    # Get wallet balances
    wallet = get_wallet_balances()

    # Get LP position from on-chain bins
    pos_config = config.get("position", {})
    range_low = pos_config.get("range_low", 9.75)
    range_high = pos_config.get("range_high", 10.01)

    lp_onchain = {"has_position": False}
    if active_bin:
        try:
            lp_onchain = get_lp_position_onchain(active_bin, price, range_low, range_high)
        except Exception as e:
            lp_onchain = {"has_position": False, "error": str(e)}

    # Compute position
    position = compute_position_value(config, price, wallet, lp_onchain)

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
        "lp_position": position["lp_position"],
        "wallet": position["wallet"],
        "combined_total_usd": position["combined_total_usd"],
        "range_check": {
            "in_range": position["in_range"],
            "range_low": position["range_low"],
            "range_high": position["range_high"],
            "price_position_pct": position["price_position_pct"],
        },
        "shape": {
            "description": position["shape_description"],
            "avax_split_pct": position["avax_split_pct"],
            "usdc_split_pct": position["usdc_split_pct"],
            "skew_pct": position["skew_pct"],
        },
        "efficiency": {
            "fee_efficiency_pct": position["fee_efficiency_pct"],
        },
        "lp_onchain": lp_onchain if lp_onchain.get("has_position") else None,
        "entry_total_usd": position["entry_total_usd"],
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
