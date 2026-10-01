#!/usr/bin/env python3
"""Decode the mystery swaps + find external deposits (the $28 question)."""
import json, urllib.request, time, collections
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
KNOWN = {'0x864d4e5ee7318e97483db7eb0912e09f161516ea': 'LFJ_LBPair',
         '0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7': 'BlackholePool',
         '0x18556da13313f3532c54711497a8fedac273220e': 'LFJ_Router',
         '0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146'.lower(): 'NFPM',
         '0x3ade52f9779c07471f4b6d5997444c3c2124c1c0': 'Gauge',
         '0xa47ad2c95fae476a73b85a355a5855adb4b3a449': 'FarmingCenter'}


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


def http(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=25))


# ── 1. decode selectors ──
print('=== SELECTOR DECODE ===')
for sel in ['0xc22159b6', '0xa3c7271a', '0x2a443fae']:
    try:
        d = http(f'https://www.4byte.directory/api/v1/signatures/?hex_signature={sel}')
        names = [r['text_signature'] for r in d.get('results', [])][:3]
        print(f'  {sel} -> {names if names else "(no match)"}')
    except Exception as e:
        print(f'  {sel} -> lookup err {str(e)[:50]}')

# ── 2. external deposits (30 days) ──
wp = '0x' + '0' * 24 + W[2:].lower()
head = int(rpc('eth_blockNumber', [])['result'], 16)
start = head - 30 * 43200
print(f'\n=== EXTERNAL INFLOWS, 30d (blocks {start}..{head}) ===')
ext = collections.defaultdict(float)
for addr, dec, sym in [(USDC, 6, 'USDC'), (WAVAX, 18, 'WAVAX')]:
    b = start
    while b <= head:
        e = min(b + 1999, head)
        r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e),
                                 'address': addr, 'topics': [T0, None, wp]}])
        for l in r.get('result', []):
            frm = ('0x' + l['topics'][1][-40:]).lower()
            amt = int(l['data'], 16) / 10**dec
            if frm not in KNOWN and frm != W.lower():
                ext[(sym, frm)] += amt
        b = e + 1
tot = 0.0
for (sym, frm), amt in sorted(ext.items(), key=lambda x: -x[1]):
    usd = amt * 7.72 if sym == 'WAVAX' else amt
    tot += usd
    print(f'  {sym:6s} {amt:>14,.6f} (${usd:8.2f})  from {frm}')
print(f'  --- external inflows (USD at current px): ${tot:.2f}')
