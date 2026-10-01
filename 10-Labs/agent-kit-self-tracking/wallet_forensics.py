#!/usr/bin/env python3
"""Wallet forensics — page getLogs to reconstruct what actually happened.

Answers: were we EVER at $28? When was each CL NFT minted? Where did the
capital go? Public Avalanche RPC caps getLogs at 2048 blocks, so we page.
"""
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
WALLET = _sw_wallet()
NFPM = '0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146'
USDC = '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e'
WAVAX = '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7'
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
CHUNK = 2000

def rpc(m, p, retries=3):
    for a in range(retries):
        try:
            d = {'jsonrpc': '2.0', 'method': m, 'params': p, 'id': 1}
            req = urllib.request.Request(RPC, json.dumps(d).encode(),
                                         {'Content-Type': 'application/json'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            if a == retries - 1:
                raise
            time.sleep(1.5)

def page_logs(address, topics, from_block, to_block):
    """Page getLogs in CHUNK-sized windows (public RPC limit)."""
    out = []
    b = from_block
    while b <= to_block:
        e = min(b + CHUNK - 1, to_block)
        r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e),
                                 'address': address, 'topics': topics}])
        out.extend(r.get('result', []))
        b = e + 1
    return out

def main():
    head = int(rpc('eth_blockNumber', [])['result'], 16)
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    span = days * 43200  # ~2s blocks
    start = max(0, head - span)
    print(f'head={head} scanning {days}d -> blocks {start}..{head} '
          f'({(head-start)//CHUNK} chunks per query type)')
    w_pad = '0x' + '0' * 24 + WALLET[2:].lower()

    # 1. NFT mints to our wallet (NFPM Transfer, to=wallet)
    mints = page_logs(NFPM, [TRANSFER, None, w_pad], start, head)
    print(f'\n=== NFPM mints TO wallet: {len(mints)} ===')
    nft_events = []
    for l in mints:
        tid = int(l['topics'][3], 16)
        blk = int(l['blockNumber'], 16)
        ts = int(rpc('eth_getBlockByNumber', [hex(blk), False])['result']['timestamp'], 16)
        frm = '0x' + l['topics'][1][-40:]
        nft_events.append((ts, blk, tid, frm))
    for ts, blk, tid, frm in sorted(nft_events):
        print(f'  {time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(ts))} blk {blk} '
              f'tokenId #{tid} from {frm}')

    # 2. USDC + WAVAX flows involving the wallet
    for sym, addr, dec in [('USDC', USDC, 6), ('WAVAX', WAVAX, 18)]:
        outs = page_logs(addr, [TRANSFER, w_pad], start, head)
        ins = page_logs(addr, [TRANSFER, None, w_pad], start, head)
        print(f'\n=== {sym}: {len(outs)} out, {len(ins)} in ===')
        evs = []
        for l in outs:
            evs.append((int(l['blockNumber'], 16), -int(l['data'], 16) / 10**dec,
                        'OUT', '0x' + l['topics'][2][-40:]))
        for l in ins:
            evs.append((int(l['blockNumber'], 16), int(l['data'], 16) / 10**dec,
                        'IN', '0x' + l['topics'][1][-40:]))
        for blk, amt, d, cp in sorted(evs)[-25:]:
            print(f'  blk {blk} {d:3s} {amt:>16,.6f} {sym}  cp={cp}')

if __name__ == '__main__':
    main()
