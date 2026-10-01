#!/usr/bin/env python3
"""Wallet value timeline — chain-truth balances at key blocks + recent activity."""
import json, urllib.request, time
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

wp = '0x' + '0' * 24 + W[2:].lower()

def bal(addr, dec, blk='latest'):
    r = rpc('eth_call', [{'to': addr, 'data': '0x70a08231' + wp[2:]}, blk]).get('result')
    return int(r, 16) / 10**dec if r else None

def avax(blk='latest'):
    r = rpc('eth_getBalance', [W, blk]).get('result')
    return int(r, 16) / 1e18 if r else None

head = int(rpc('eth_blockNumber', [])['result'], 16)
print('head block', head)

# Key blocks from forensics
SNAP = [
    ('Sep8 23:47 first mint #3476545', 94810980),
    ('Sep10 11:55 re-mint #3478420',   94935145),
    ('NOW', 'latest'),
]
print('\n=== WALLET BALANCES (chain truth) ===')
for label, blk in SNAP:
    try:
        u, w, a = bal(USDC, 6, blk), bal(WAVAX, 18, blk), avax(blk)
        print(f'{label:34s} USDC={u:10.4f}  WAVAX={w:10.6f}  AVAX={a:.6f}')
    except Exception as e:
        print(f'{label:34s} ERR {str(e)[:70]}')

# Recent activity: last ~3h
start = head - 5400
print('\n=== LAST ~3h WALLET ACTIVITY (grouped by tx) ===')
txs = {}
for addr, dec, sym in [(USDC, 6, 'USDC'), (WAVAX, 18, 'WAVAX')]:
    for topics, direction in [([T0, wp], 'out'), ([T0, None, wp], 'in')]:
        b = start
        while b <= head:
            e = min(b + 1999, head)
            r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e),
                                     'address': addr, 'topics': topics}])
            for l in r.get('result', []):
                h = l['transactionHash']
                amt = int(l['data'], 16) / 10**dec
                cp = ('0x' + l['topics'][2][-40:]) if direction == 'out' else ('0x' + l['topics'][1][-40:])
                txs.setdefault(h, {'blk': int(l['blockNumber'], 16), 'f': []})
                txs[h]['f'].append(f'{"-" if direction=="out" else "+"}{amt:.6f} {sym} ({cp[:10]})')
            b = e + 1
for h, v in sorted(txs.items(), key=lambda x: x[1]['blk'])[-12:]:
    print(f'  blk {v["blk"]}: ' + ' | '.join(v['f']) + f'  tx={h[:18]}')
print(f'\ntotal distinct txs in last 3h: {len(txs)}')
