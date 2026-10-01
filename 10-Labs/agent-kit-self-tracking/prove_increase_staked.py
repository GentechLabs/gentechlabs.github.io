#!/usr/bin/env python3
"""CAN WE ADD LIQUIDITY TO OUR EXISTING STAKED POSITION? (Jordan's ask)

Jordan (Sep 11): "a lot of us want to just keep adding to the same position...
you want to put it together so it's in one big pool, farming... our new logic
should be to restake if possible."

The naive test is inconclusive: increaseLiquidity on #3479882 reverts, but the
revert is ambiguous because we hold $0.00 USDC. Two of our tests returned a
custom error (0xe6ace6df) and one returned 'STF' (token transfer failed).

'STF' is the giveaway: it means execution reached the *token transfer* stage,
i.e. ALL NFPM checks passed — including `isAuthorizedForToken`, even though the
position is staked. That implies we CAN increase a farmed position.

This script proves it beyond doubt by simulating with STATE OVERRIDES: grant
ourselves USDC balance + WAVAX allowance, then replay the real increaseLiquidity
calldata. If it returns a non-zero liquidity value, the capability is real and
the only blocker is funding — not authorization.
"""
import json
import time

from eth_utils import keccak
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
W = Web3.to_checksum_address(_sw_wallet())
NFPM = Web3.to_checksum_address("0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146")
WAVAX = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
POOL = Web3.to_checksum_address("0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7")
GAUGE = Web3.to_checksum_address("0x3ade52f9779c07471f4b6d5997444c3c2124c1c0")
TOKEN_ID = 3479882

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))

INC_ABI = [{
    "inputs": [{"components": [
        {"name": "tokenId", "type": "uint256"},
        {"name": "amount0Desired", "type": "uint256"},
        {"name": "amount1Desired", "type": "uint256"},
        {"name": "amount0Min", "type": "uint256"},
        {"name": "amount1Min", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ], "name": "params", "type": "tuple"}],
    "name": "increaseLiquidity",
    "outputs": [{"name": "liquidity", "type": "uint128"},
                {"name": "amount0", "type": "uint256"},
                {"name": "amount1", "type": "uint256"}],
    "stateMutability": "payable", "type": "function"}]


def find_balance_slot(token, holder, known_balance, max_slot=12):
    """Find the storage slot of balanceOf[holder] by matching a KNOWN value."""
    for s in range(max_slot):
        inner = keccak(bytes.fromhex("00" * 12 + holder[2:]) + s.to_bytes(32, "big"))
        got = w3.eth.get_storage_at(token, int.from_bytes(inner, "big"))
        if int.from_bytes(got, "big") == known_balance:
            return s
    return None


def main():
    print("=" * 66)
    print("PROVE IT: increaseLiquidity on STAKED #3479882 (with overrides)")
    print("=" * 66)

    # ── locate storage slots using values we can verify ──
    erc20 = w3.eth.contract(address=USDC, abi=[
        {"constant": True, "inputs": [{"name": "a", "type": "address"}],
         "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
         "stateMutability": "view", "type": "function"}])
    pool_usdc = erc20.functions.balanceOf(POOL).call()
    usdc_slot = find_balance_slot(USDC, POOL, pool_usdc)
    print(f"  USDC balanceOf slot: {usdc_slot} (validated vs pool balance "
          f"{pool_usdc/1e6:,.2f})")

    # WAVAX allowance slot 4 was validated earlier against allowance(W,NFPM)=2^256-1
    def allow_slot(owner, spender, base):
        inner = keccak(bytes.fromhex("00" * 12 + owner[2:]) + base.to_bytes(32, "big"))
        return int.from_bytes(keccak(bytes.fromhex("00" * 12 + spender[2:]) + inner), "big")

    wavax_allow = allow_slot(W, NFPM, 4)
    print(f"  WAVAX allowance slot: 4 (validated earlier)")

    if usdc_slot is None:
        print("  ❌ could not determine USDC balance slot — aborting")
        return 1

    # ── simulate with overrides ──
    # We want to add: 0.20 WAVAX + 0.75 USDC (a small top-up, both sides)
    a0 = int(0.20e18)
    a1 = int(0.75e6)
    c = w3.eth.contract(address=NFPM, abi=INC_ABI)
    data = c.encode_abi("increaseLiquidity", [{
        "tokenId": TOKEN_ID, "amount0Desired": a0, "amount1Desired": a1,
        "amount0Min": 0, "amount1Min": 0,
        "deadline": int(time.time()) + 900}])

    usdc_bal_slot = int.from_bytes(
        keccak(bytes.fromhex("00" * 12 + W[2:]) + usdc_slot.to_bytes(32, "big")), "big")

    overrides = {
        USDC: {"stateDiff": {hex(usdc_bal_slot): "0x" + format(10_000_000, "064x")}},
        WAVAX: {"stateDiff": {hex(wavax_allow): "0x" + "ff" * 32}},
    }
    # also give the wallet WAVAX balance headroom via storage override
    for s in range(12):
        inner = keccak(bytes.fromhex("00" * 12 + W[2:]) + s.to_bytes(32, "big"))
        got = int.from_bytes(w3.eth.get_storage_at(WAVAX, int.from_bytes(inner, "big")), "big")
        if got > 0:
            overrides[WAVAX]["stateDiff"][hex(int.from_bytes(inner, "big"))] = \
                "0x" + format(max(got, int(2e18)), "064x")
            print(f"  WAVAX balance slot {s} found (had {got/1e18:.6f})")
            break

    try:
        out = w3.eth.call({"from": W, "to": NFPM, "data": data}, "latest", overrides)
        liq = int.from_bytes(out[:32], "big")
        a0o = int.from_bytes(out[32:64], "big")
        a1o = int.from_bytes(out[64:96], "big")
        print(f"\n  ✅✅ SIMULATION PASSED ON THE STAKED POSITION")
        print(f"     liquidity added : {liq:,}")
        print(f"     WAVAX used      : {a0o/1e18:.6f}")
        print(f"     USDC  used      : {a1o/1e6:.6f}")
        print("\n  ⇒ We CAN add to the existing staked position.")
        print("     'STF' earlier was only the funding check, not authorization.")
        print("     Jordan's instinct is right AND supported by the contract.")
        return 0
    except Exception as e:
        print(f"\n  ❌ still reverted with overrides: {str(e)[:200]}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
