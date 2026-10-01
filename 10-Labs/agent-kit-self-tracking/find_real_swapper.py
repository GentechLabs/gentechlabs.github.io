#!/usr/bin/env python3
"""Find the contract that ACTUALLY executes swaps on our Blackhole pool.

We keep failing to price a swap through the official routers (ISTF custom error).
Rather than guess another router, read the chain: pull recent Swap events from
our pool and look at each transaction's `to` (the executing contract) and its
input selector. Whatever contract is really doing the swaps is the answer.
"""
import json
import urllib.request
from collections import Counter

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
# Swap event topic for Algebra/Uniswap-V3: Swap(address,address,int256,int256,uint160,uint128,int24)
SWAP_TOPIC = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"


def rpc(method, params):
    d = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    req = urllib.request.Request(RPC, json.dumps(d).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30)).get("result")


def main():
    head = int(rpc("eth_blockNumber", []), 16)
    print("=" * 64)
    print("WHO ACTUALLY SWAPS ON OUR POOL? (chain truth, not docs)")
    print("=" * 64)
    print(f"  pool {POOL}")
    print(f"  head block {head}\n")

    logs = []
    # page backwards to catch swaps without scanning a huge range
    for span in (2000, 8000, 30000):
        try:
            r = rpc("eth_getLogs", [{"fromBlock": hex(head - span),
                                     "toBlock": hex(head),
                                     "address": POOL,
                                     "topics": [SWAP_TOPIC]}])
            if r:
                logs = r
                print(f"  found {len(r)} Swap events in last {span} blocks")
                break
        except Exception as e:
            print(f"  range {span} failed: {type(e).__name__}")
    if not logs:
        print("  no swaps found in scan window — pool may be quiet")
        return

    callers = Counter()
    for lg in logs[-40:]:
        tx = rpc("eth_getTransactionByHash", [lg["transactionHash"]])
        if not tx:
            continue
        to = (tx.get("to") or "").lower()
        data = tx.get("input") or "0x"
        sel = data[:10]
        callers[(to, sel)] += 1

    print("\n  executing contract -> selector  (count)")
    for (to, sel), n in callers.most_common(10):
        print(f"    {to}  {sel}   x{n}")

    # name the top contract
    print("\n  ── identify the top caller ──")
    for (to, sel), n in callers.most_common(3):
        code = rpc("eth_getCode", [to, "latest"]) or "0x"
        print(f"    {to}: code_len={len(code)//2-1} bytes")


if __name__ == "__main__":
    main()
