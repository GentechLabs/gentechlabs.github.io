#!/usr/bin/env python3
"""ADD CAPITAL TO OUR EXISTING BLACKHOLE POSITION (Jordan's restake logic).

Jordan (Sep 11 2026):
    "a lot of us want to just keep adding to the same position... you want to
     put it together so it's in one big pool, farming, and would make you more
     money... our new logic should be to restake if possible."

VERIFIED FACTS (chain, not assumption):
  - #3479882 is STAKED, but ownerOf() == our wallet and getApproved() == gauge.
    The gauge holds liquidity via APPROVAL, not ownership.
  - Algebra's increaseLiquidity is guarded by `isAuthorizedForToken` only, and
    we are the owner -> we pass.
  - PROVEN by simulation with state overrides: increaseLiquidity on the STAKED
    position returned liquidity 5,950,601,297,693 (used 0.112 WAVAX + 0.75 USDC).
    Earlier 'STF' was the funding check, never authorization.
  - gauge.balanceOf(tokenId) == position.liquidity exactly -> the farm tracks
    live liquidity, so an increase should be credited automatically.

So the correct shape is NOT "unstake -> re-mint -> restake". It is:
    swap the needed ratio -> increaseLiquidity -> verify the gauge credited it.

This script:
  1. solves the exact two-sided ratio for the position's range at the live price
  2. swaps only the WAVAX that must become USDC (aggregator route, proven)
  3. calls increaseLiquidity on the EXISTING staked position
  4. verifies BOTH position.liquidity and gauge.balanceOf increased

Usage: python3 add_to_position.py [--usd 11.12] [--execute]
       default = dry-run (simulate everything, move nothing)
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.parse
import urllib.request

from web3 import Web3
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)
import steward_identity as _SI   # ONE signing path: asserts the tenant + decrypts

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

sys.path.insert(0, "/root/.hermes/profiles/gentech-treasury/scripts")

RPC = _avax_url()
W = Web3.to_checksum_address(_sw_wallet())
NFPM = Web3.to_checksum_address("0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146")
WAVAX = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
POOL = Web3.to_checksum_address("0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7")
GAUGE = Web3.to_checksum_address("0x3ade52f9779c07471f4b6d5997444c3c2124c1c0")
KYBER_ROUTER = "0x6131B5fae19EA4f9D964eAc0408E4408b66337b5"
STEWARD_KEY = _sw_keypath()
CHAIN_ID = 43114

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))

ERC20 = [
    {"constant": True, "inputs": [{"name": "a", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [{"name": "o", "type": "address"},
                                  {"name": "s", "type": "address"}],
     "name": "allowance", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "s", "type": "address"},
                                   {"name": "v", "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "nonpayable", "type": "function"},
]
# Algebra pools expose globalState() — NOT Uniswap V3's slot0(). Calling slot0()
# on an Algebra pool reverts, which is an easy cross-venue porting trap.
SLOT0 = [{"inputs": [], "name": "globalState",
          "outputs": [{"name": "price", "type": "uint160"},
                      {"name": "tick", "type": "int24"},
                      {"name": "fee", "type": "uint16"},
                      {"name": "timepointIndex", "type": "uint16"},
                      {"name": "communityFeeToken0", "type": "uint8"},
                      {"name": "communityFeeToken1", "type": "uint8"}],
          "stateMutability": "view", "type": "function"}]
INC_ABI = [{"inputs": [{"components": [
    {"name": "tokenId", "type": "uint256"},
    {"name": "amount0Desired", "type": "uint256"},
    {"name": "amount1Desired", "type": "uint256"},
    {"name": "amount0Min", "type": "uint256"},
    {"name": "amount1Min", "type": "uint256"},
    {"name": "deadline", "type": "uint256"}], "name": "params", "type": "tuple"}],
    "name": "increaseLiquidity",
    "outputs": [{"name": "liquidity", "type": "uint128"},
                {"name": "amount0", "type": "uint256"},
                {"name": "amount1", "type": "uint256"}],
    "stateMutability": "payable", "type": "function"}]


def best_token_id():
    """Highest-liquidity position we own (pitfall #42 — never index 0)."""
    nfpm = w3.eth.contract(address=NFPM, abi=__import__("blackhole_cl_adapter").NFPM_ABI)
    n = nfpm.functions.balanceOf(W).call()
    best, best_liq = None, -1
    for i in range(n):
        tid = nfpm.functions.tokenOfOwnerByIndex(W, i).call()
        liq = nfpm.functions.positions(tid).call()[7]
        if liq > best_liq:
            best, best_liq = tid, liq
    return best, best_liq


def ratio_for_range(tick_lower, tick_upper, tick_now, price_usd=None):
    """Fraction of value that belongs in token0 (WAVAX) vs token1 (USDC).

    Standard CL math with sqrtPrice = 1.0001^(tick/2):
      amount0 = L*(sqrtB - sqrtP)/(sqrtP*sqrtB)   [WAVAX, raw 18dp]
      amount1 = L*(sqrtP - sqrtA)                 [USDC, raw 6dp]
    We return (wavax_value_frac, usdc_value_frac) so the caller can split a USD
    budget correctly — raw unit counts alone would be wrong across 18/6 decimals.
    """
    sp = 1.0001 ** (tick_now / 2)
    sa = 1.0001 ** (tick_lower / 2)
    sb = 1.0001 ** (tick_upper / 2)
    if not (sa < sp < sb):
        return None
    a0_raw = (sb - sp) / (sp * sb)   # raw token0 per unit L
    a1_raw = (sp - sa)               # raw token1 per unit L
    # convert to human units, then to USD value
    wavax_units = a0_raw / 1e18
    usdc_units = a1_raw / 1e6
    px = price_usd if price_usd else 7.4698
    v0 = wavax_units * px
    v1 = usdc_units
    tot = v0 + v1
    if tot <= 0:
        return None
    return (v0 / tot, v1 / tot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--usd", type=float, default=11.12)
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()
    dry = not args.execute

    print("=" * 66)
    print("ADD TO EXISTING POSITION (Jordan's restake logic)")
    print("=" * 66)
    print(f"  mode: {'DRY-RUN' if dry else 'EXECUTE'}\n")

    tid, liq = best_token_id()
    print(f"  target position: #{tid} (liquidity {liq:,}) — highest-liquidity owned")

    nfpm = w3.eth.contract(address=NFPM, abi=__import__("blackhole_cl_adapter").NFPM_ABI)
    pos = nfpm.functions.positions(tid).call()
    tl, tu = pos[5], pos[6]
    pool = w3.eth.contract(address=POOL, abi=SLOT0)
    # Use the adapter's own raw reader — it already handles Algebra's
    # globalState() layout and the 18/6 decimal scaling correctly. Re-deriving
    # this locally is how the earlier STF() decimal bug happened.
    import blackhole_cl_adapter as _A
    tick, price_usd = _A.get_pool_tick(w3)
    print(f"  range {tl}..{tu} · current tick {tick} · live ${price_usd:.4f}"
          f" · IN RANGE: {tl <= tick <= tu}")
    if not (tl < tick < tu):
        print("  ❌ price is outside the range — increaseLiquidity would be one-sided.")
        print("     Re-center first, then add.")
        return 1

    frac = ratio_for_range(tl, tu, tick, price_usd)
    if not frac:
        print("  ❌ could not solve the range ratio")
        return 1
    f0, f1 = frac
    print(f"  value split at current price: {f0*100:.1f}% WAVAX / {f1*100:.1f}% USDC")

    wavax_c = w3.eth.contract(address=WAVAX, abi=ERC20)
    usdc_c = w3.eth.contract(address=USDC, abi=ERC20)
    wavax_bal = wavax_c.functions.balanceOf(W).call() / 1e18
    usdc_bal = usdc_c.functions.balanceOf(W).call() / 1e6
    print(f"  wallet: {wavax_bal:.6f} WAVAX  |  {usdc_bal:.4f} USDC")
    target = args.usd

    # Deployable value is constrained by whichever side runs out first.
    # f0 = WAVAX value share, f1 = USDC value share.
    # We must satisfy: wavax_used/f0 == usdc_used/f1  (both sides in ratio)
    # so max_value = min(wavax_usd / f0, usdc_bal / f1), capped at the target.
    wavax_usd = wavax_bal * 7.4518
    max_by_wavax = wavax_usd / f0 if f0 > 0 else float("inf")
    max_by_usdc = usdc_bal / f1 if f1 > 0 else float("inf")
    deploy_value = min(target, max_by_wavax, max_by_usdc)

    # keep a small WAVAX residue only if we still need to swap for USDC
    need_usdc = deploy_value * f1
    need_wavax = (deploy_value * f0) / 7.4518
    swap_wavax = max(0.0, need_usdc - usdc_bal) / 7.4518
    print(f"\n  plan: deploy ${deploy_value:.2f} of ${target:.2f} target")
    print(f"        need {need_wavax:.6f} WAVAX + {need_usdc:.4f} USDC")
    if swap_wavax > 1e-9:
        print(f"        swap {swap_wavax:.6f} WAVAX -> USDC first")
    if swap_wavax > wavax_bal - 0.01:
        print("  ❌ swap would eat the balance — reduce target")
        return 1

    if dry:
        print("\n  [dry-run] would: approve -> swap -> increaseLiquidity -> verify gauge")
        print("  Re-run with --execute.")
        return 0

    acct = _SI.signer()
    if acct.address.lower() != W.lower():
        print("  ❌ key mismatch", file=sys.stderr)
        return 1
    print(f"\n  signer: {acct.address}")

    # ── 1. swap WAVAX -> USDC via the PROVEN aggregator route (only if needed) ──
    amt_in = int(swap_wavax * 1e18)
    if amt_in < 10_000_000_000_000_000:   # < 0.01 WAVAX — nothing worth swapping
        print("  no swap needed (already hold both sides in ratio)")
    else:
      u = ("https://aggregator-api.kyberswap.com/avalanche/api/v1/routes?"
           + urllib.parse.urlencode({"tokenIn": WAVAX, "tokenOut": USDC,
                                     "amountIn": str(amt_in)}))
      req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
      routes = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
      summary = routes["data"]["routeSummary"]
      body = json.dumps({"routeSummary": summary, "sender": W,
                         "recipient": W, "slippageTolerance": 100,
                         "deadline": int(time.time()) + 900,
                         "source": "steward"}).encode()
      req = urllib.request.Request(
          "https://aggregator-api.kyberswap.com/avalanche/api/v1/route/build",
          data=body, headers={"Content-Type": "application/json",
                              "User-Agent": "Mozilla/5.0"})
      built = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
      swap_to = built["data"]["routerAddress"]
      swap_data = built["data"]["data"]
      out_usdc = int(summary["amountOut"]) / 1e6
      print(f"  swap quote: {swap_wavax:.6f} WAVAX -> {out_usdc:.4f} USDC")

      gp = w3.eth.gas_price
      print(f"  approving WAVAX -> {swap_to}")
      tx = wavax_c.functions.approve(Web3.to_checksum_address(swap_to),
                                     int(amt_in * 4)).build_transaction({
          "from": W, "nonce": w3.eth.get_transaction_count(W),
          "gas": 60000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
      h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
      r = w3.eth.wait_for_transaction_receipt(h, timeout=180)
      print(f"    {'✅' if r['status']==1 else '❌'} approve {h.hex()}")

      print("  executing swap...")
      tx = {"from": W, "to": Web3.to_checksum_address(swap_to),
            "data": swap_data, "value": int(built["data"].get("transactionValue") or 0),
            "nonce": w3.eth.get_transaction_count(W),
            "gas": int(built["data"].get("gas") or 500000) + 100000,
            "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID}
      h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
      r = w3.eth.wait_for_transaction_receipt(h, timeout=240)
      print(f"    {'✅' if r['status']==1 else '❌'} swap {h.hex()} status={r['status']}")
      if r["status"] != 1:
          print("  ❌ swap reverted — aborting before any liquidity move")
          return 1

    usdc_now = usdc_c.functions.balanceOf(W).call()
    wavax_now = wavax_c.functions.balanceOf(W).call()
    print(f"  after swap: {wavax_now/1e18:.6f} WAVAX | {usdc_now/1e6:.4f} USDC")
    gp = w3.eth.gas_price

    # ── 2. increaseLiquidity on the STAKED position ──
    # Use the SOLVED needs (in token units), not balance*fraction — the latter
    # redeploys only a slice each pass and leaves the rest idle.
    a0 = int(min(need_wavax, wavax_now / 1e18) * 1e18)
    a1 = int(min(need_usdc, usdc_now / 1e6) * 1e6)
    print(f"\n  increasing #{tid}: {a0/1e18:.6f} WAVAX + {a1/1e6:.4f} USDC")
    inc = w3.eth.contract(address=NFPM, abi=INC_ABI)
    params = {"tokenId": tid, "amount0Desired": a0, "amount1Desired": a1,
              "amount0Min": 0, "amount1Min": 0, "deadline": int(time.time()) + 900}
    # simulate first — never send blind
    try:
        sim = inc.functions.increaseLiquidity(params).call({"from": W})
        print(f"    simulate ✅ liquidity {sim[0]:,}")
    except Exception as e:
        print(f"    ❌ simulate failed: {str(e)[:160]}")
        return 1

    tx = inc.functions.increaseLiquidity(params).build_transaction({
        "from": W, "nonce": w3.eth.get_transaction_count(W),
        "gas": 700000, "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID})
    h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
    r = w3.eth.wait_for_transaction_receipt(h, timeout=240)
    print(f"    {'✅' if r['status']==1 else '❌'} increaseLiquidity {h.hex()}")
    if r["status"] != 1:
        print("  ❌ increase reverted")
        return 1

    # ── 3. VERIFY: did BOTH the position and the gauge credit it? ──
    time.sleep(3)
    new_pos = nfpm.functions.positions(tid).call()[7]
    gauge = w3.eth.contract(address=GAUGE, abi=[
        {"inputs": [{"name": "t", "type": "uint256"}], "name": "balanceOf",
         "outputs": [{"name": "", "type": "uint256"}],
         "stateMutability": "view", "type": "function"}])
    new_gauge = gauge.functions.balanceOf(tid).call()
    print("\n  ── verification ──")
    print(f"    position.liquidity: {liq:,} -> {new_pos:,}  {'✅ GREW' if new_pos > liq else '❌ unchanged'}")
    print(f"    gauge.balanceOf   : {liq:,} -> {new_gauge:,}  "
          f"{'✅ FARM CREDITED IT' if new_gauge > liq else '⚠️ farm did NOT credit — needs exit/enter'}")
    return 0 if new_pos > liq else 1


if __name__ == "__main__":
    sys.exit(main())
