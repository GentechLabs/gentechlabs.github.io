#!/usr/bin/env python3
"""Fine-grained value scan around Sep 10 11:50-13:10 — pin the loss."""
import json, urllib.request, time, sys
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
LFJ = '0x864d4e5ee7318e97483db7eb0912e09f161516ea'
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
            time.sleep(0.6)


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


PX = 7.94


def snap(blk):
    u = int(call(USDC, '0x70a08231' + enc(int(W, 16)), blk) or '0x0', 16) / 1e6
    w = int(call(WAVAX, '0x70a08231' + enc(int(W, 16)), blk) or '0x0', 16) / 1e18
    a = int(rpc('eth_getBalance', [W, hex(blk)]).get('result', '0x0'), 16) / 1e18
    lbt = int(call(LFJ, '0x70a08231' + enc(int(W, 16)), blk) or '0x0', 16) / 1e18
    gs = words(call(POOL, '0xe76c01e4', blk))
    tc = s24(int(gs[1], 16)) if gs else 0
    n = int(call(NFPM, '0x70a08231' + enc(int(W, 16)), blk) or '0x0', 16)
    pv, det = 0.0, []
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
        v = (a0 / 1e18 * PX + a1 / 1e6) if t0.lower() == WAVAX.lower() else (a0 / 1e6 + a1 / 1e18 * PX)
        pv += v
        det.append(f'#{tid}=${v:.2f}')
    loose = u + w * PX + a * PX
    return u, w, a, lbt, loose, pv, loose + pv, det, tc


head = int(rpc('eth_blockNumber', [])['result'], 16)
print(f'{"block":>10s} {"time UTC":9s} {"USDC":>8s} {"WAVAX":>9s} {"LBT":>10s} {"loose$":>7s} {"CL$":>7s} {"TOTAL$":>7s}')
print('-' * 82)
for blk in [94935130, 94935145, 94935260, 94935270, 94935835, 94935845, 94935900, 94935910,
            94936000, 94937000, 94937920, 94938000]:
    ts = int(rpc('eth_getBlockByNumber', [hex(blk), False]).get('result', {}).get('timestamp', '0x0'), 16)
    u, w, a, lbt, loose, pv, tot, det, tc = snap(blk)
    print(f'{blk:>10d} {time.strftime("%H:%M:%S", time.gmtime(ts))} {u:8.4f} {w:9.6f} {lbt:10.6f} '
          f'{loose:7.2f} {pv:7.2f} {tot:7.2f}')

print('\n=== transfers involving wallet, blocks 94935130..94935920 ===')
wp = '0x' + '0' * 24 + W[2:].lower()
rows = []
for addr, dec, sym in [(USDC, 6, 'USDC'), (WAVAX, 18, 'WAVAX')]:
    for topics, d in [([T0, wp], 'OUT'), ([T0, None, wp], 'IN ')]:
        r = rpc('eth_getLogs', [{'fromBlock': hex(94935130), 'toBlock': hex(94935920),
                                 'address': addr, 'topics': topics}])
        for l in r.get('result', []):
            cp = ('0x' + l['topics'][2][-40:]) if d == 'OUT' else ('0x' + l['topics'][1][-40:])
            rows.append((int(l['blockNumber'], 16), d, int(l['data'], 16) / 10**dec, sym, cp,
                         l['transactionHash'][:12]))
for r_ in sorted(rows):
    print(f'  blk {r_[0]} {r_[1]} {r_[2]:14.6f} {r_[3]:5s} cp={r_[4][:12]} tx={r_[5]}')
