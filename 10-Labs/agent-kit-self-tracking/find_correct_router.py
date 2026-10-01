#!/usr/bin/env python3
"""Find the CORRECT router for our pool by inspecting real successful swaps.

The router in the adapter (0xe946A9f3...) reverts ISTF() on every route —
even on our own liquid WAVAX/USDC pool. So it is the wrong router for this
factory. Ground truth: look at actual Swap events on our pool and read the
`to` address of the transactions that produced them (that's the router real
users call).
"""
import json, urllib.request, collections
from web3 import Web3

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
POOL = '0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7'
BLACK_POOL = '0x14e4A5beD2e5E688EE1A5Ca3a4914250D1aBD573'
SWAP = '0x' + Web3.keccak(
    text='Swap(address,address,int256,int256,uint160,uint128,int24)').hex()


def rpc(m, p, tries=3):
    for a in range(tries):
        try:
            d = {'jsonrpc': '2.0', 'method': m, 'params': p, 'id': 1}
            req = urllib.request.Request(RPC, json.dumps(d).encode(),
                                         {'Content-Type': 'application/json'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if a == tries - 1:
                return {}
            import time
            time.sleep(0.6)


head = int(rpc('eth_blockNumber', [])['result'], 16)


def callers(pool, label):
    logs = []
    b = head - 20000
    while b <= head:
        e = min(b + 1999, head)
        logs.extend(rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e),
                                         'address': pool, 'topics': [SWAP]}]).get('result', []))
        b = e + 1
    print(f'\n=== {label}: {len(logs)} Swap events in last 20k blocks ===')
    c = collections.Counter()
    for l in logs:
        t = rpc('eth_getTransactionByHash', [l['transactionHash']]).get('result') or {}
        to = (t.get('to') or '').lower()
        frm = (t.get('from') or '').lower()
        c[to] += 1
    for addr, n in c.most_common(6):
        code = rpc('eth_getCode', [addr, 'latest']).get('result') or '0x'
        print(f'  router/to={addr}  ({n} swaps, code={(len(code)-2)//2} bytes)')
    return c


callers(POOL, 'OUR WAVAX/USDC pool')
callers(BLACK_POOL, 'BLACK/WAVAX pool')
