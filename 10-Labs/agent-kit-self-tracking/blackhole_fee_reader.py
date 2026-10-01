#!/usr/bin/env python3
"""Algebra V3 / Blackhole fee-growth reader — compute REAL uncollected fees.

WHY: Blackhole (Algebra V3) does NOT store "fees earned" as a balance like LFJ
V2.2 bins do. Fees are computed from the fee-growth accumulator:

    fees0 = liquidity * (feeGrowthInside0_now - feeGrowthInside0_last) / 2^128
    fees1 = liquidity * (feeGrowthInside1_now - feeGrowthInside1_last) / 2^128

feeGrowthInside for [tickLower, tickUpper) is derived from the pool's global
accumulator + each boundary tick's OUTER fee growth:

    tickCurrent <  tickLower          -> inside = outer(lower) - outer(upper)
    tickLower <= tickCurrent < upper  -> inside = global - outer(lower) - outer(upper)
    tickCurrent >= tickUpper          -> inside = outer(upper) - outer(lower)

Struct layouts (verified against the Algebra Integral API reference docs):
  positions(uint256) -> word[5]=tickLower word[6]=tickUpper word[7]=liquidity
                        word[8]=feeGrowthInside0LastX128 word[9]=feeGrowthInside1LastX128
                        word[10]=tokensOwed0 word[11]=tokensOwed1
  ticks(int24)       -> word[0]=liquidityTotal word[1]=liquidityDelta
                        word[2]=prevTick word[3]=nextTick
                        word[4]=outerFeeGrowth0Token word[5]=outerFeeGrowth1Token
  globalState()      -> word[0]=price word[1]=tick

NOTE: this is the standard Uniswap-V3-family fee-growth math — it works on ANY
V3-style DEX (Uniswap V3, PancakeSwap V3, THENA, Ramesses, Algebra, Blackhole).
It is NOT Blackhole-exclusive.

Usage: python3 blackhole_fee_reader.py [--json]
"""
import json
import sys
import urllib.request
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
POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"
NFPM = "0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146"
WALLET = _sw_wallet()
WAVAX = "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7"
USDC = "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e"
Q128 = 2 ** 128
M = 2 ** 256


def select_position():
    """Pick OUR live position by HIGHEST LIQUIDITY.

    Sep 11 2026 (Jordan): a re-center withdraw->re-mint leaves a drained
    remnant NFT. This reader had the OLD tokenId hardcoded, so it measured an
    empty position and reported ~$0 fees. Always select the funded one.
    """
    n = int(_words(eth_call(NFPM, _keccak_selector("balanceOf(address)") +
                            _enc(int(WALLET, 16))))[0], 16)
    best_tid, best_liq = None, 0
    for i in range(n):
        tid = int(_words(eth_call(NFPM, _keccak_selector("tokenOfOwnerByIndex(address,uint256)") +
                                  _enc(int(WALLET, 16)) + _enc(i)))[0], 16)
        w = _words(eth_call(NFPM, _keccak_selector("positions(uint256)") + _enc(tid)))
        t0, t1 = "0x" + w[2][-40:], "0x" + w[3][-40:]
        pair_ok = ((t0.lower() == WAVAX.lower() and t1.lower() == USDC.lower()) or
                   (t0.lower() == USDC.lower() and t1.lower() == WAVAX.lower()))
        liq = int(w[7], 16)
        if pair_ok and liq > best_liq:
            best_liq, best_tid = liq, tid
    return best_tid, best_liq


def _keccak_selector(sig):
    from web3 import Web3
    return "0x" + Web3.keccak(text=sig).hex()[:8]


def _enc(v):
    return format(v & (M - 1), "064x")


def _words(hexstr):
    if not hexstr or hexstr == "0x":
        return []
    h = hexstr[2:]
    return [h[i:i + 64] for i in range(0, len(h), 64)]


def _s24(v):
    v &= 0xFFFFFF
    return v - 2 ** 24 if v >= 2 ** 23 else v


def eth_call(to, data):
    body = {"jsonrpc": "2.0", "method": "eth_call",
            "params": [{"to": to, "data": data}, "latest"], "id": 1}
    req = urllib.request.Request(RPC, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=25)).get("result")


def read_fees(token_id=None):
    if token_id is None:
        token_id, _sel_liq = select_position()
        if token_id is None:
            return {"error": "no WAVAX/USDC CL position found for wallet"}
    out = {"pool": POOL, "tokenId": token_id}
    # 1. Position checkpoint
    r = eth_call(NFPM, _keccak_selector("positions(uint256)") + _enc(token_id))
    w = _words(r)
    if len(w) < 12:
        return {"error": "positions() returned too few words"}
    liquidity = int(w[7], 16)
    fg_last0, fg_last1 = int(w[8], 16), int(w[9], 16)
    owed0, owed1 = int(w[10], 16), int(w[11], 16)
    tl, tu = _s24(int(w[5], 16)), _s24(int(w[6], 16))
    # 2. Pool current tick
    w = _words(eth_call(POOL, _keccak_selector("globalState()")))
    tc = _s24(int(w[1], 16))
    # 3. Global fee growth accumulators
    g0 = int(_words(eth_call(POOL, _keccak_selector("totalFeeGrowth0Token()")))[0], 16)
    g1 = int(_words(eth_call(POOL, _keccak_selector("totalFeeGrowth1Token()")))[0], 16)
    # 4. Boundary tick outer fee growth (docs layout: word[4], word[5])
    wl = _words(eth_call(POOL, _keccak_selector("ticks(int24)") + _enc(tl)))
    ol0, ol1 = int(wl[4], 16), int(wl[5], 16)
    wu = _words(eth_call(POOL, _keccak_selector("ticks(int24)") + _enc(tu)))
    ou0, ou1 = int(wu[4], 16), int(wu[5], 16)
    # 5. feeGrowthInside (uint256 wraparound arithmetic)
    if tc < tl:
        i0, i1 = (ol0 - ou0) % M, (ol1 - ou1) % M
    elif tc < tu:
        i0, i1 = (g0 - ol0 - ou0) % M, (g1 - ol1 - ou1) % M
    else:
        i0, i1 = (ou0 - ol0) % M, (ou1 - ol1) % M
    d0, d1 = (i0 - fg_last0) % M, (i1 - fg_last1) % M
    f0 = liquidity * d0 // Q128 + owed0   # token0 = WAVAX (18 dec)
    f1 = liquidity * d1 // Q128 + owed1   # token1 = USDC (6 dec)
    out.update({
        "liquidity": liquidity, "tickLower": tl, "tickUpper": tu, "tickCurrent": tc,
        "inRange": tl <= tc < tu,
        "feesWAVAX": f0 / 1e18, "feesUSDC": f1 / 1e6,
        "feesUSD": f0 / 1e18 * 7.36 + f1 / 1e6,
    })
    return out


if __name__ == "__main__":
    res = read_fees()
    if "--json" in sys.argv:
        print(json.dumps(res, indent=2))
    else:
        if "error" in res:
            print("❌", res["error"])
        else:
            print("🕳️  Blackhole (Algebra V3) fee-growth reader")
            print(f"  Position #{res['tokenId']} · liquidity {res['liquidity']}")
            print(f"  Ticks {res['tickLower']}..{res['tickUpper']} (current {res['tickCurrent']}) "
                  f"· {'IN range' if res['inRange'] else 'OUT of range'}")
            print(f"  ➜ UNCOLLECTED FEES: {res['feesWAVAX']:.8f} WAVAX + {res['feesUSDC']:.6f} USDC "
                  f"(~${res['feesUSD']:.6f})")
    sys.exit(0)
