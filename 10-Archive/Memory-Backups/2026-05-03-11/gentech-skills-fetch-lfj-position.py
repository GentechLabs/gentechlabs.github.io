#!/usr/bin/env python3
"""
Standalone LFJ position fetcher — on-chain decode for AVAX/USDC pool.
Uses batch RPC calls; outputs JSON for cron consumption.
"""
import json
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

WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"

BALANCE_OF_SELECTOR = "0x00fdd58e"
TOTAL_SUPPLY_SELECTOR = "0xbd85b039"
ACTIVE_ID_SELECTOR_V2 = "0xdbe65edc"     # LFJ V2.2
ACTIVE_ID_SELECTOR_V1 = "0x05fc00e8"     # LFJ V2.1 fallback

# ─── Helpers ──────────────────────────────────────────────────────────
def rpc_call(to: str, data: str) -> Optional[str]:
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
        if start + batch_size < len(calls):
            time.sleep(0.2)
    return all_results

def fetch_price_dexscreener() -> Optional[float]:
    try:
        req = urllib.request.Request(DEXSCREENER_URL,
            headers={"User-Agent": "Gentech-YoYo/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        pair = data.get("pairs", [{}])[0] if data.get("pairs") else {}
        price = float(pair.get("priceNative", 0))
        return price if price > 0 else None
    except Exception:
        return None

def get_active_bin(w3_addr: str) -> Optional[int]:
    """Try V2.2 selector first, fall back to V2.1."""
    for selector in [ACTIVE_ID_SELECTOR_V2, ACTIVE_ID_SELECTOR_V1]:
        result = rpc_call(w3_addr, selector.hex())
        if result and result != "0x":
            return int(result, 16)
    return None

# ─── Main ─────────────────────────────────────────────────────────────
def main():
    # 1. Price
    avax_price = fetch_price_dexscreener() or 0.0

    # 2. Active bin
    active_bin = get_active_bin(POOL_ADDRESS)
    if active_bin is None:
        print(json.dumps({"error": "cannot fetch active bin"}))
        sys.exit(1)

    # 3. Scan ±50 bins
    scan_range = 50
    start_id = max(0, active_bin - scan_range)
    end_id = active_bin + scan_range + 1

    calls = []
    for bin_id in range(start_id, end_id):
        data_bal = BALANCE_OF_SELECTOR + \
                   WALLET[2:].rjust(64, '0') + \
                   bin_id.to_bytes(32, 'big').hex()
        calls.append({"to": POOL_ADDRESS, "data": "0x" + data_bal})
        data_sup = TOTAL_SUPPLY_SELECTOR + bin_id.to_bytes(32, 'big').hex()
        calls.append({"to": POOL_ADDRESS, "data": "0x" + data_sup})

    results = rpc_call_batch(calls)

    positions = []
    total_shares_by_bin = {}
    for i in range(0, len(results), 2):
        bin_id = start_id + i // 2
        bal_res = results[i]
        sup_res = results[i + 1] if i + 1 < len(results) else None

        if bal_res and bal_res != "0x":
            user_shares = int(bal_res, 16)
            if user_shares > 0:
                total_shares = int(sup_res, 16) if sup_res and sup_res != "0x" else 1
                positions.append({
                    "bin_id": bin_id,
                    "user_shares": str(user_shares),
                    "total_shares": str(total_shares),
                    "share_pct": round(user_shares / total_shares * 100, 4)
                })
                total_shares_by_bin[bin_id] = total_shares

    # 4. Range
    if positions:
        bins_with_pos = [p["bin_id"] for p in positions]
        range_start = min(bins_with_pos)
        range_end = max(bins_with_pos)
        avg_share_pct = round(sum(p["share_pct"] for p in positions) / len(positions), 1)
    else:
        range_start = range_end = active_bin
        avg_share_pct = 0.0

    # Output
    out = {
        "wallet": WALLET,
        "avax_price": avax_price,
        "active_bin": active_bin,
        "position_range": [range_start, range_end],
        "avg_share_pct": avg_share_pct,
        "positions": positions
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
