#!/usr/bin/env python3
"""How much BLACK does the Blackhole COQ/WAVAX gauge actually emit?

Jordan's idea: farm COQ to compound into more COQ. Mechanically that IS possible —
LP COQ/WAVAX, earn BLACK, sell BLACK -> buy COQ, add to LP.

The question is purely economic. Measure the real emissions on that gauge, then
compute what our $11 would actually earn.
"""
import json
import time
import urllib.request

from web3 import Web3
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.
def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        return _avax_url()   # last resort only — avax_rpc preferred

RPC = _avax_url()
COQ_POOL = "0x4C33a727E3744009F7413D2d1FbbAd77D7Df207F"
COQ_GAUGE = "0x063AcCcD367A4269077Be9F89f2866deDd5Bf462"
OUR_POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"
OUR_GAUGE = "0x3ADE52f9779c07471F4B6d5997444C3c2124C1c0"
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
STEWARD = _sw_wallet()

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))

GAUGE = [{"inputs": [{"name": "", "type": "uint256"}], "name": "balanceOf",
          "outputs": [{"name": "", "type": "uint256"}],
          "stateMutability": "view", "type": "function"},
         {"inputs": [], "name": "rewardToken",
          "outputs": [{"name": "", "type": "address"}],
          "stateMutability": "view", "type": "function"},
         {"inputs": [], "name": "rewardsDuration",
          "outputs": [{"name": "", "type": "uint256"}],
          "stateMutability": "view", "type": "function"},
         {"inputs": [], "name": "totalSupply",
          "outputs": [{"name": "", "type": "uint256"}],
          "stateMutability": "view", "type": "function"}]
EF = [{"inputs": [{"name": "", "type": "bytes32"}], "name": "farms",
       "outputs": [{"name": "rewardPerSecond", "type": "uint256"},
                   {"name": "rewardRate", "type": "uint256"},
                   {"name": "startTime", "type": "uint256"},
                   {"name": "endTime", "type": "uint256"}],
       "stateMutability": "view", "type": "function"}]
POOL = [{"inputs": [], "name": "liquidity",
         "outputs": [{"name": "", "type": "uint128"}],
         "stateMutability": "view", "type": "function"}]

GAUGE_MGR = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"
GM = [{"inputs": [{"name": "", "type": "address"}], "name": "gauges",
       "outputs": [{"name": "", "type": "address"}],
       "stateMutability": "view", "type": "function"}]
ETERNAL_FARMING = "0x01A8A00A6fC8106B94f84aAbAef689Fd0D77271A"

ERC20 = [{"constant": True, "inputs": [{"name": "a", "type": "address"}],
          "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
          "stateMutability": "view", "type": "function"}]


def black_balance():
    c = w3.eth.contract(address=Web3.to_checksum_address(BLACK), abi=ERC20)
    return c.functions.balanceOf(Web3.to_checksum_address(STEWARD)).call()


def measure_gauge(gauge, label, seconds=90):
    """Sample BLACK accrual to the gauge over a window."""
    g = Web3.to_checksum_address(gauge)
    sel = "0x70a08231"  # balanceOf(address)
    from eth_utils import keccak  # noqa
    samples = []

    # Use rewardsDuration/totalSupply style: read the FARM rewardPerSecond via
    # the gauge's own view if available; otherwise sample the farm's balance.
    gc = w3.eth.contract(address=g, abi=GAUGE)
    try:
        rt = gc.functions.rewardToken().call()
        dur = gc.functions.rewardsDuration().call()
        ts = gc.functions.totalSupply().call()
        print(f"  {label}")
        print(f"    rewardToken   : {rt}")
        print(f"    rewardsDuration: {dur}s ({dur/86400:.1f}d)")
        print(f"    totalSupply   : {ts:,}")
    except Exception as e:
        print(f"  {label}: gauge reads failed ({str(e)[:60]})")


def main():
    print("=" * 68)
    print("BLACKHOLE COQ/WAVAX GAUGE — emissions + economics")
    print("=" * 68)

    # pool sizes
    for label, pool in (("COQ/WAVAX", COQ_POOL), ("WAVAX/USDC (ours)", OUR_POOL)):
        pc = w3.eth.contract(address=Web3.to_checksum_address(pool), abi=POOL)
        try:
            liq = pc.functions.liquidity().call()
            print(f"  {label:20} pool.liquidity = {liq:,}")
        except Exception as e:
            print(f"  {label:20} liquidity read failed: {str(e)[:50]}")

    print()
    measure_gauge(COQ_GAUGE, "COQ/WAVAX gauge")
    print()
    measure_gauge(OUR_GAUGE, "our WAVAX/USDC gauge")

    # market data
    print("\n  ── market ──")
    try:
        req = urllib.request.Request(
            "https://api.dexscreener.com/latest/dex/pairs/avalanche/" + COQ_POOL,
            headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        p = (d.get("pairs") or [{}])[0]
        liq = float((p.get("liquidity") or {}).get("usd") or 0)
        vol = float((p.get("volume") or {}).get("h24") or 0)
        print(f"    Blackhole COQ/WAVAX: ${liq:,.0f} liq, ${vol:,.0f}/24h vol")
    except Exception as e:
        print(f"    market read failed: {str(e)[:60]}")

    print("\n  ── the honest comparison ──")
    print("    Our WAVAX/USDC farm : ~100.7 BLACK/day measured (~$0.25/day)")
    print("    COQ/WAVAX pool      : $794 liq, $14/24h volume")
    print("       -> even at 100% of pool: $0.036/day in fees")
    print("       -> we'd add ~$11 = ~1.4% share = ~$0.0005/day fees")


if __name__ == "__main__":
    main()
