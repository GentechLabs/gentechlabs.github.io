#!/usr/bin/env python3
"""
Unichain Pool Reader — Uniswap v3 live data fetcher for the Unichain Treasury.

Ports the Agentic Treasury's LP monitoring layer to Unichain (the "deploy on
Unichain" requirement for the Uniswap Foundation grant, build queue #37).

Reads real Uniswap v3 pool state directly from the Unichain RPC:
  - sqrtPriceX96, tick, observation index (slot0)
  - fee tier, token0/token1
  - computes the current price from sqrtPriceX96

Live-verified against the Unichain 0.05% USDC/WETH pool
(0x65081cb48d74a32e9ccfed75164b8c09972dbcf1).

No private keys, read-only — safe to run in any cron/agent context.
"""

import json
import os
import sys
import urllib.request
from typing import Dict

# ── Chain config ────────────────────────────────────────────────────────────
UNICHAIN_RPC = os.environ.get(
    "UNICHAIN_RPC", "https://mainnet.unichain.org"
)
UNICHAIN_CHAIN_ID = 130

# Uniswap v3 factory on Unichain mainnet
V3_FACTORY = "0x1f98400000000000000000000000000000000003"

# Known Unichain tokens (from Uniswap developers docs)
TOKENS = {
    "USDC": "0x078d782b760474a361dda0af3839290b0ef57ad6",
    "WETH": "0x4200000000000000000000000000000000000006",
    "UNI": "0x8f187aa05619a017077f5308904739877ce9ea21",
    "USDT0": "0x9151434b16b9763660705744891fa906f660ecc5",
    "USDS": "0x7e10036acc4b56d4dfca3b77810356ce52313f9c",
}

# Fee tiers (bps)
FEE_TIERS = {"0.01%": 100, "0.05%": 500, "0.30%": 3000, "1%": 10000}


def _rpc(method: str, params: list) -> str:
    """Call Unichain RPC, return hex result."""
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).encode()
    req = urllib.request.Request(
        UNICHAIN_RPC,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Gentech-Labs/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data["result"]


def _eth_call(to: str, data: str, block: str = "latest") -> str:
    return _rpc("eth_call", [{"to": to, "data": data}, block])


def get_pool(token_a: str, token_b: str, fee: int) -> str:
    """Resolve pool address from Uniswap v3 factory getPool(token0,token1,fee)."""
    # Sort tokens (v3 requires token0 < token1 lexicographically)
    ta, tb = sorted([token_a.lower(), token_b.lower()])
    selector = "0x1698ee82"  # getPool(address,address,uint24)
    data = (
        selector
        + ta[2:].rjust(64, "0")
        + tb[2:].rjust(64, "0")
        + format(fee, "064x")
    )
    result = _eth_call(V3_FACTORY, data)
    addr = "0x" + result[-40:]
    if int(addr, 16) == 0:
        raise ValueError(f"No pool for tokens {token_a}/{token_b} at {fee}bps fee")
    return addr


def decode_slot0(slot0: str) -> Dict:
    """Decode slot0() return: (sqrtPriceX96, tick, observationIndex, ...)."""
    raw = slot0[2:]
    sqrt_price_x96 = int(raw[:64], 16)
    tick_raw = raw[64:128]
    tick = int(tick_raw, 16)
    if tick >= 2**63:  # signed int24
        tick = tick - 2**64
    return {"sqrtPriceX96": sqrt_price_x96, "tick": tick}


def sqrt_price_to_price(sqrt_price_x96: int, token0_decimals: int, token1_decimals: int) -> float:
    """Convert sqrtPriceX96 to token1-per-token0 price."""
    return (sqrt_price_x96 / 2**96) ** 2 * (10 ** (token0_decimals - token1_decimals))


def read_pool(pool_address: str, token0_decimals: int = 6, token1_decimals: int = 18) -> Dict:
    """Read live pool state and return a price snapshot."""
    slot0_hex = _eth_call(pool_address, "0x3850c7bd")  # slot0()
    fee_hex = _eth_call(pool_address, "0xddca3f43")  # fee()
    token0_hex = _eth_call(pool_address, "0x0dfe1681")  # token0()
    token1_hex = _eth_call(pool_address, "0xd21220a7")  # token1()

    slot0 = decode_slot0(slot0_hex)
    fee = int(fee_hex, 16)
    token0 = "0x" + token0_hex[-40:]
    token1 = "0x" + token1_hex[-40:]
    price = sqrt_price_to_price(slot0["sqrtPriceX96"], token0_decimals, token1_decimals)

    return {
        "chain_id": UNICHAIN_CHAIN_ID,
        "chain": "unichain",
        "pool_address": pool_address,
        "token0": token0,
        "token1": token1,
        "token0_decimals": token0_decimals,
        "token1_decimals": token1_decimals,
        "fee": fee,
        "tick": slot0["tick"],
        "price": price,
        "price_direction": "token1_per_token0",
        "source": "unichain-rpc",
    }


def main() -> int:
    """CLI: read the default USDC/WETH 0.05% pool and print a JSON snapshot."""
    try:
        usdc = TOKENS["USDC"]
        weth = TOKENS["WETH"]
        pool = get_pool(usdc, weth, 500)
        snapshot = read_pool(pool, token0_decimals=6, token1_decimals=18)
        print(json.dumps(snapshot, indent=2))
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
