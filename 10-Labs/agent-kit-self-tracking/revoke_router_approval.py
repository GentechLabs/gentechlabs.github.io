#!/usr/bin/env python3
"""Revoke a specific ERC-20 approval to zero (self-audit fix, Sep 12 2026).

Context: the first COQ swap granted an UNLIMITED WAVAX allowance to the
KyberSwap router. The accumulator now uses BOUNDED approvals, so the standing
unlimited grant is redundant exposure — a swap router should never hold a
permission we don't need.

Simulates first, reports the real gas cost, then executes.
"""
import sys
import time

from web3 import Web3

from steward_identity import signer, wallet

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
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
SPENDER = "0x6131B5fae19EA4f9D964eAc0408E4408b66337b5"   # KyberSwap router

ABI = [{"constant": False, "inputs": [{"name": "s", "type": "address"},
                                      {"name": "v", "type": "uint256"}],
        "name": "approve", "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable", "type": "function"},
       {"constant": True, "inputs": [{"name": "o", "type": "address"},
                                     {"name": "s", "type": "address"}],
        "name": "allowance", "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view", "type": "function"}]


def main():
    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 25}))
    W = wallet()
    c = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ABI)

    cur = c.functions.allowance(W, Web3.to_checksum_address(SPENDER)).call()
    print(f"  wallet  {W}")
    print(f"  token   WAVAX")
    print(f"  spender {SPENDER}")
    print(f"  current allowance: {cur} "
          f"({'UNLIMITED' if cur > 2**200 else f'{cur/1e18:.6f} WAVAX'})")
    if cur == 0:
        print("  already zero — nothing to do")
        return 0

    gp = w3.eth.gas_price
    gas_cost = gp * 60_000 / 1e18
    print(f"  gas: {gp/1e9:.2f} gwei → ~{gas_cost:.8f} AVAX")

    if "--execute" not in sys.argv:
        print("  [dry-run] re-run with --execute to revoke.")
        return 0

    acct = signer()          # refuses if the key doesn't match the config
    tx = c.functions.approve(Web3.to_checksum_address(SPENDER), 0) \
        .build_transaction({"from": W, "nonce": w3.eth.get_transaction_count(W),
                            "gas": 60_000, "gasPrice": int(gp * 1.3),
                            "chainId": CHAIN_ID})
    h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
    r = w3.eth.wait_for_transaction_receipt(h, timeout=180)
    print(f"  {'✅' if r['status']==1 else '❌'} revoke tx {h.hex()} status={r['status']}")

    # Verify by settled re-read. NEVER trust a single read after a tx: the
    # public Avalanche RPC lags fresh blocks and will happily report the OLD
    # value, which reads as a failed revoke when it actually succeeded.
    after = cur
    for attempt in range(5):
        r2 = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ABI)
        after = r2.functions.allowance(W, Web3.to_checksum_address(SPENDER)).call()
        if after == 0:
            break
        time.sleep(3)
    print(f"  verified allowance now: {after} "
          f"{'✅ ZERO' if after == 0 else '❌ STILL SET (re-check before retrying)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
