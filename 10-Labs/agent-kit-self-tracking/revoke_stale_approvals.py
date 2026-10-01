#!/usr/bin/env python3
"""Revoke the stale UNLIMITED approvals to the retired LFJ router.

Jordan authorized 2026-09-11: "go ahead and take care of whatever those LFJ
things are."

WHY: an approval is a standing grant. We migrated off LFJ, but USDC and WAVAX
still grant the LFJ router UNLIMITED allowance. That is precisely the class in
the ether.fi/Veda AtomicQueue exploit (ExVul, 2026-09-11): a contract you once
approved pulling real value. Cost to revoke: ~$0.0002.

SAFETY:
  1. verify the signing key matches our wallet
  2. confirm each allowance is currently non-zero
  3. SIMULATE approve(spender, 0) before sending
  4. send, wait, verify receipt status == 1
  5. RE-READ the allowance afterwards and assert it is 0

Usage:  python3 revoke_stale_approvals.py [--execute]
        (default is dry-run: plan + simulate, no tx sent)
"""
from __future__ import annotations

import json
import sys
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
CHAIN_ID = 43114
STEWARD_KEY_FILE = _sw_keypath()
STEWARD_WALLET = Web3.to_checksum_address(_sw_wallet())

# The retired rail — we no longer use this router at all.
LFJ_ROUTER = Web3.to_checksum_address("0x18556da13313f3532c54711497a8fedac273220e")

TOKENS = {
    "USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
    "WAVAX": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
}

ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"},
                                  {"name": "_spender", "type": "address"}],
     "name": "allowance", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"},
                                   {"name": "_value", "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol",
     "outputs": [{"name": "", "type": "string"}],
     "stateMutability": "view", "type": "function"},
]


def main():
    execute = "--execute" in sys.argv
    w3 = Web3(Web3.HTTPProvider(RPC))

    print("=" * 58)
    print("🔐 REVOKE STALE APPROVALS — retired LFJ router")
    print("=" * 58)
    print(f"  dry-run: {not execute}  (pass --execute to send)\n")

    acct = None
    if execute:
        try:
            key = open(STEWARD_KEY_FILE).read().strip()
            acct = w3.eth.account.from_key(key)
        except Exception as e:
            print(f"  ❌ cannot load steward key: {e}", file=sys.stderr)
            return 1
        if acct.address.lower() != STEWARD_WALLET.lower():
            print(f"  ❌ KEY MISMATCH: key={acct.address} expected={STEWARD_WALLET}",
                  file=sys.stderr)
            return 1
        print(f"  signer verified: {acct.address}")

    bal = w3.eth.get_balance(STEWARD_WALLET) / 1e18
    gp = w3.eth.gas_price
    print(f"  gas: {bal:.6f} AVAX available · gasPrice {gp/1e9:.3f} gwei")
    est = 2 * 46000 * gp / 1e18
    print(f"  estimated total cost: {est:.8f} AVAX (~${est*7.46:.5f})\n")

    pending = []
    for name, addr in TOKENS.items():
        c = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=ERC20_ABI)
        cur = c.functions.allowance(STEWARD_WALLET, LFJ_ROUTER).call()
        label = "UNLIMITED" if cur > 2 ** 200 else str(cur)
        print(f"  {name:6} current allowance -> LFJ: {label}")
        if cur == 0:
            print("         already revoked — skipping")
            continue
        pending.append((name, c))

        # SIMULATE before sending (never trust the plan; ask the chain)
        try:
            ok = c.functions.approve(LFJ_ROUTER, 0).call({"from": STEWARD_WALLET})
            print(f"         simulate approve(0): {'✅ ok' if ok else '❌ returned False'}")
        except Exception as e:
            print(f"         ❌ simulate FAILED: {str(e)[:90]}", file=sys.stderr)
            return 1

    if not pending:
        print("\n  ✅ nothing to revoke — all clean")
        return 0

    if not execute:
        print(f"\n  [dry-run] would send {len(pending)} revoke tx(s). "
              f"Re-run with --execute.")
        return 0

    print(f"\n  🚀 sending {len(pending)} revoke tx(s)...")
    sent = []
    for name, c in pending:
        tx = c.functions.approve(LFJ_ROUTER, 0).build_transaction({
            "from": STEWARD_WALLET,
            "nonce": w3.eth.get_transaction_count(STEWARD_WALLET),
            "gas": 60000,
            "gasPrice": int(gp * 1.3),
            "chainId": CHAIN_ID,
        })
        signed = acct.sign_transaction(tx)
        h = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"    {name}: sent {h.hex()}")
        rcpt = w3.eth.wait_for_transaction_receipt(h, timeout=180)
        ok = rcpt["status"] == 1
        print(f"    {name}: {'✅ confirmed' if ok else '❌ REVERTED'} "
              f"(block {rcpt['blockNumber']}, gas {rcpt['gasUsed']})")
        sent.append((name, h.hex(), ok))
        time.sleep(1)

    # VERIFY BY RE-READING — never claim success without reading it back
    print("\n  ── verification (re-read allowance) ──")
    allok = True
    for name, addr in TOKENS.items():
        c = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=ERC20_ABI)
        cur = c.functions.allowance(STEWARD_WALLET, LFJ_ROUTER).call()
        good = cur == 0
        allok &= good
        print(f"    {name:6} -> LFJ: {cur}  {'✅ REVOKED' if good else '❌ STILL LIVE'}")

    print()
    if allok:
        print("  ✅ ALL STALE APPROVALS REVOKED — the retired rail can no longer")
        print("     move our USDC or WAVAX.")
    else:
        print("  ❌ some approvals remain — investigate")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
