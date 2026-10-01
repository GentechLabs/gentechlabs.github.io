#!/usr/bin/env python3
"""Forensics: what did the recent wallet txs cost, and which script drove them?

Checks every wallet tx in the last 24h: status, gas, method selector, and net
token delta. Also flags whether rebalance_swap.py copies diverged (the LFJ
router 0x18556... should NOT be used anymore).
"""
import json, urllib.request, time, collections, hashlib, os
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
W = _sw_wallet()
USDC = '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e'
WAVAX = '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7'
T0 = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
AVAX_USD = 7.80


def rpc(m, p, tries=3):
    for a in range(tries):
        try:
            d = {'jsonrpc': '2.0', 'method': m, 'params': p, 'id': 1}
            req = urllib.request.Request(RPC, json.dumps(d).encode(),
                                         {'Content-Type': 'application/json'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if a == tries - 1:
                raise
            time.sleep(1)


def sel4(sig):
    # keccak via web3 if available
    try:
        from web3 import Web3
        return '0x' + Web3.keccak(text=sig).hex()[:8]
    except Exception:
        return None


wp = '0x' + '0' * 24 + W[2:].lower()
head = int(rpc('eth_blockNumber', [])['result'], 16)
start = head - 43200

hashes = {}
for addr in (USDC, WAVAX):
    for topics in ([T0, wp], [T0, None, wp]):
        b = start
        while b <= head:
            e = min(b + 1999, head)
            r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e),
                                     'address': addr, 'topics': topics}])
            for l in r.get('result', []):
                hashes[l['transactionHash']] = int(l['blockNumber'], 16)
            b = e + 1

print(f'=== {len(hashes)} wallet txs in last 24h ===\n')
tot_gas = 0.0
sel_count = collections.Counter()
for h, blk in sorted(hashes.items(), key=lambda x: x[1]):
    t = rpc('eth_getTransactionByHash', [h]).get('result') or {}
    rc = rpc('eth_getTransactionReceipt', [h]).get('result') or {}
    status = int(rc.get('status', '0x0'), 16)
    gas = int(rc.get('gasUsed', '0x0'), 16)
    gp = int(rc.get('effectiveGasPrice', '0x0'), 16)
    cost = gas * gp / 1e18
    tot_gas += cost
    inp = t.get('input') or '0x'
    sel = inp[:10]
    sel_count[sel] += 1
    ts = int(rpc('eth_getBlockByNumber', [hex(blk), False])['result']['timestamp'], 16)
    print(f'{time.strftime("%H:%M:%S", time.gmtime(ts))} blk{blk} '
          f'{"OK " if status else "FAIL"} gas={gas:>7} cost={cost:.6f}AVAX '
          f'sel={sel} to={t.get("to","")[:12]}')

print(f'\ntotal gas spent (24h): {tot_gas:.6f} AVAX = ${tot_gas*AVAX_USD:.4f}')
print('\n=== selectors ===')
for s, c in sel_count.most_common():
    print(f'  {s} x{c}')

# Known LFJ / Blackhole selectors
print('\n=== known selectors ===')
known = {
    'swapExactTokensForTokens': '0x38ed1739',
    'swapExactAVAXForTokens': '0x7ff36ab5',
    'swapExactTokensForAVAX': '0x18cbafe5',
    'swapExactTokensForTokensSupportingFeeOnTransferTokens': '0x5c11d795',
    'multicall': '0xac9650d8',
    'exactInputSingle': '0x414bf389',
    'exactInput': '0xc04b8d59',
    'increaseLiquidity': '0x219f5d17',
    'decreaseLiquidity': '0x0c49ccbe',
    'collect': '0xfc6f7865',
    'mint': '0x88316456',
}
for name, s in known.items():
    if s in sel_count:
        print(f'  {s} = {name} x{sel_count[s]}')

# md5 of rebalance_swap.py across the 3 copies
print('\n=== rebalance_swap.py copies (divergence check) ===')
for p in ['/root/vaults/gentech/10-Labs/agent-kit-self-tracking/rebalance_swap.py',
          '/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/rebalance_swap.py',
          '/root/.hermes/profiles/gentech-treasury/scripts/rebalance_swap.py']:
    if os.path.exists(p):
        print(f'  {hashlib.md5(open(p,"rb").read()).hexdigest()[:8]}  {p}')
    else:
        print(f'  MISSING  {p}')
