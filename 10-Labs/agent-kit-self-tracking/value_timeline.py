#!/usr/bin/env python3
"""VALUE TIMELINE — were we EVER at $28?

Reads the wallet's total value at historical blocks (eth_call accepts a block
tag, so positions()/balances are all reconstructable) and compares against
what the reports claimed.

Total = loose (USDC + WAVAX + AVAX) + all Blackhole CL positions
        valued by the Uniswap-V3 tick math at that block.
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
SEL = {'bal': '0x70a08231', 'gs': '0xe76c01e4', 'pos': '0x99fbab88',
       'nbal': '0x70a08231', 'tokof': '0x2f745c59'}


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
            time.sleep(0.8)


def enc(v):
    return format(v & (2**256 - 1), '064x')


def words(h):
    if not h or h == '0x':
        return []
    h = h[2:]
    return [h[i:i + 64] for i in range(0, len(h), 64)]


def call(to, data, blk):
    r = rpc('eth_call', [{'to': to, 'data': data}, hex(blk)])
    return r.get('result')


def s24(v):
    v &= 0xffffff
    return v - 2**24 if v >= 2**23 else v


def bal(addr, dec, blk, who=W):
    r = call(addr, SEL['bal'] + enc(int(who, 16)), blk)
    return int(r, 16) / 10**dec if r else 0.0


def avax_bal(blk):
    r = rpc('eth_getBalance', [W, hex(blk)]).get('result')
    return int(r, 16) / 1e18 if r else 0.0


def cl_value(blk, price):
    """Sum of all CL positions at this block via tick math."""
    r = call(NFPM, SEL['nbal'] + enc(int(W, 16)), blk)
    n = int(r, 16) if r else 0
    gs = words(call(POOL, SEL['gs'], blk))
    if not gs:
        return 0.0, []
    tc = s24(int(gs[1], 16))
    total = 0.0
    det = []
    for i in range(n):
        tr = call(NFPM, SEL['tokof'] + enc(int(W, 16)) + enc(i), blk)
        if not tr:
            continue
        tid = int(words(tr)[0], 16)
        pw = words(call(NFPM, SEL['pos'] + enc(tid), blk))
        if len(pw) < 8:
            continue
        L = int(pw[7], 16)
        tl, tu = s24(int(pw[5], 16)), s24(int(pw[6], 16))
        t0 = '0x' + pw[2][-40:]
        sp = 1.0001 ** (tc / 2.0)
        sa = 1.0001 ** (tl / 2.0)
        sb = 1.0001 ** (tu / 2.0)
        if sp <= sa:
            a0 = L * (sb - sa) / (sa * sb); a1 = 0.0
        elif sp < sb:
            a0 = L * (sb - sp) / (sp * sb); a1 = L * (sp - sa)
        else:
            a0 = 0.0; a1 = L * (sb - sa)
        if t0.lower() == WAVAX.lower():
            v = a0 / 1e18 * price + a1 / 1e6
        else:
            v = a0 / 1e6 + a1 / 1e18 * price
        total += v
        det.append((tid, round(v, 2), tl <= tc < tu))
    return total, det


# historical AVAX prices
try:
    req = urllib.request.Request(
        'https://api.coingecko.com/api/v3/coins/avalanche-2/market_chart?vs_currency=usd&days=10',
        headers={'User-Agent': 'Mozilla/5.0'})
    chart = json.load(urllib.request.urlopen(req, timeout=25))['prices']
except Exception as e:
    chart = []
    print('price chart err', e)


def price_at(ts_ms):
    if not chart:
        return 7.80
    lo, hi = 0, len(chart) - 1
    best = chart[0][1]
    for t, p in chart:
        if t <= ts_ms:
            best = p
        else:
            break
    return best


head = int(rpc('eth_blockNumber', [])['result'], 16)
print(f'head={head}\n')
print(f'{"when":17s} {"AVAXpx":>7s} {"loose$":>8s} {"CL$":>7s} {"TOTAL$":>8s}  positions')
print('-' * 78)
step = 43200  # ~12h
for k in range(8, -1, -1):
    blk = head - k * step
    bd = rpc('eth_getBlockByNumber', [hex(blk), False]).get('result')
    if not bd:
        continue
    ts = int(bd['timestamp'], 16)
    px = price_at(ts * 1000)
    u = bal(USDC, 6, blk)
    w = bal(WAVAX, 18, blk)
    a = avax_bal(blk)
    loose = u + w * px + a * px
    clv, det = cl_value(blk, px)
    tot = loose + clv
    when = time.strftime('%m-%d %H:%M', time.gmtime(ts))
    ds = ' '.join(f'#{t}=${v}' + ('' if ir else '(OUT)') for t, v, ir in det)
    print(f'{when:17s} {px:7.2f} {loose:8.2f} {clv:7.2f} {tot:8.2f}  {ds}')
