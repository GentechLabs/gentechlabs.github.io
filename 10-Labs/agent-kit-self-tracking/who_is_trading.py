#!/usr/bin/env python3
"""Who is trading our wallet? + where did the capital go?

Collects every wallet-involving token transfer in the last 24h, resolves each
tx's SENDER, and groups. Decisive for: are our own crons still churning, or is
something else moving this wallet?
"""
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
head = int(rpc('eth_blockNumber', [])['result'], 16)
start = head - 43200  # ~24h

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

print(f'distinct wallet txs in last 24h: {len(hashes)}')
senders = collections.Counter()
rows = []
for h, blk in sorted(hashes.items(), key=lambda x: x[1]):
    t = rpc('eth_getTransactionByHash', [h]).get('result') or {}
    frm = (t.get('from') or '').lower()
    to = (t.get('to') or '').lower()
    sel = (t.get('input') or '0x')[:10]
    senders[frm] += 1
    rows.append((blk, frm, to, sel, h))

print('\n=== last 12 txs (sender / target / method) ===')
for blk, frm, to, sel, h in rows[-12:]:
    tag = ' <== OUR WALLET' if frm == W.lower() else ''
    print(f'  blk {blk}  from {frm}  to {to}  sel {sel}{tag}')

print('\n=== SENDERS (who is driving) ===')
for f, c in senders.most_common():
    tag = '  <== OUR WALLET' if f == W.lower() else ''
    print(f'  {f} : {c} txs{tag}')
print('\nour wallet:', W.lower())

# who are the non-wallet senders?
print('\n=== unknown senders (are they routers?) ===')
for f, c in senders.most_common():
    if f != W.lower():
        code = rpc('eth_getCode', [f, 'latest']).get('result') or '0x'
        print(f'  {f}  code_bytes={(len(code)-2)//2}  txs={c}')
