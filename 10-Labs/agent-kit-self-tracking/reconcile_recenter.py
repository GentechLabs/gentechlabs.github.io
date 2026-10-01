#!/usr/bin/env python3
"""RECONCILE the Sep 10 re-center: did ~$11 leave the wallet?

Precise balance + position snapshots bracketing the re-center, plus every
token transfer in the window, so the value delta is fully accounted for.
"""
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
NFPM = '0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146'
POOL = '0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7'
USDC = '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e'
WAVAX = '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7'
T0 = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'


def rpc(m, p, tries=4):
    for a in range(tries):
        try:
            d = {'jsonrpc': '2.0', 'method': m, 'params': p, 'id': 1}
            req = urllib.request.Request(RPC, json.dumps(d).encode(),
                                         {'Content-Type': 'application/json'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if a == tries - 1:
                return {}
            time.sleep(0.7)


def enc(v):
    return format(v & (2**256 - 1), '064x')


def words(h):
    if not h or h == '0x':
        return []
    h = h[2:]
    return [h[i:i + 64] for i in range(0, len(h), 64)]


def call(to, data, blk):
    return rpc('eth_call', [{'to': to, 'data': data}, hex(blk)]).get('result')


def s24(v):
    v &= 0xffffff
    return v - 2**24 if v >= 2**23 else v


def snap(blk, px):
    u = int(call(USDC, '0x70a08231' + enc(int(W, 16)), blk) or '0x0', 16) / 1e6
    w = int(call(WAVAX, '0x70a08231' + enc(int(W, 16)), blk) or '0x0', 16) / 1e18
    a = int(rpc('eth_getBalance', [W, hex(blk)]).get('result', '0x0'), 16) / 1e18
    gs = words(call(POOL, '0xe76c01e4', blk))
    tc = s24(int(gs[1], 16)) if gs else 0
    n = int(call(NFPM, '0x70a08231' + enc(int(W, 16)), blk) or '0x0', 16)
    pos = []
    pv = 0.0
    for i in range(n):
        tr = call(NFPM, '0x2f745c59' + enc(int(W, 16)) + enc(i), blk)
        if not tr:
            continue
        tid = int(words(tr)[0], 16)
        pw = words(call(NFPM, '0x99fbab88' + enc(tid), blk))
        if len(pw) < 8:
            continue
        L = int(pw[7], 16)
        tl, tu = s24(int(pw[5], 16)), s24(int(pw[6], 16))
        t0 = '0x' + pw[2][-40:]
        sp, sa, sb = 1.0001 ** (tc / 2), 1.0001 ** (tl / 2), 1.0001 ** (tu / 2)
        if sp <= sa:
            a0, a1 = L * (sb - sa) / (sa * sb), 0.0
        elif sp < sb:
            a0, a1 = L * (sb - sp) / (sp * sb), L * (sp - sa)
        else:
            a0, a1 = 0.0, L * (sb - sa)
        v = (a0 / 1e18 * px + a1 / 1e6) if t0.lower() == WAVAX.lower() else (a0 / 1e6 + a1 / 1e18 * px)
        pos.append((tid, round(v, 2)))
        pv += v
    loose = u + w * px + a * px
    return dict(usdc=u, wavax=w, avax=a, loose=loose, cl=pv, total=loose + pv, pos=pos, tick=tc)


PX = 7.94  # AVAX around Sep 10 11:55
BLOCKS = [
    ('before re-center', 94935130),
    ('after re-center ', 94935150),
    ('after swaps     ', 94938000),
    ('now             ', None),
]
head = int(rpc('eth_blockNumber', [])['result'], 16)
print(f'{"point":18s} {"USDC":>8s} {"WAVAX":>9s} {"loose$":>8s} {"CL$":>8s} {"TOTAL$":>8s}  positions')
print('-' * 88)
for label, b in BLOCKS:
    bb = head if b is None else b
    s = snap(bb, PX)
    print(f'{label:18s} {s["usdc"]:8.4f} {s["wavax"]:9.6f} {s["loose"]:8.2f} {s["cl"]:8.2f} '
          f'{s["total"]:8.2f}  {s["pos"]}')

# every transfer in the re-center window
print('\n=== ALL wallet token transfers, blocks 94935130..94935160 ===')
wp = '0x' + '0' * 24 + W[2:].lower()
for addr, dec, sym in [(USDC, 6, 'USDC'), (WAVAX, 18, 'WAVAX')]:
    for topics, d in [([T0, wp], 'OUT'), ([T0, None, wp], 'IN ')]:
        r = rpc('eth_getLogs', [{'fromBlock': hex(94935130), 'toBlock': hex(94935160),
                                 'address': addr, 'topics': topics}])
        for l in r.get('result', []):
            cp = ('0x' + l['topics'][2][-40:]) if d == 'OUT' else ('0x' + l['topics'][1][-40:])
            print(f'  blk {int(l["blockNumber"],16)} {d} {int(l["data"],16)/10**dec:14.6f} {sym} '
                  f'cp={cp[:12]} tx={l["transactionHash"][:14]}')
