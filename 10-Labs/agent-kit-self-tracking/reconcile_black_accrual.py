#!/usr/bin/env python3
"""Reconcile the BLACK accrual: when did #3478420 enter the farm, and what is
our share of FARMED liquidity?

At 100.7 BLACK/day, ~29h since mint implies ~121 BLACK accrued. We only see
~50 claimable. Either the farm entry was later, or the rate is not constant.
Find the enterFarming tx (ground truth for when accrual started).
"""
import json, urllib.request, time
from web3 import Web3
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
FC = '0xa47Ad2C95FaE476a73b85A355A5855aDb4b3A449'
EF = '0x01A8A00A6fC8106B94f84aAbAef689Fd0D77271A'
POOL = '0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7'
WALLET = _sw_wallet()
TID = 3478420

SIGS = {
    '0x' + Web3.keccak(text='FarmEntered(uint256,bytes32)').hex(): 'FarmEntered',
    '0x' + Web3.keccak(text='FarmEntered(uint256,bytes32,uint256)').hex(): 'FarmEntered3',
    '0x' + Web3.keccak(text='Deposit(address,uint256)').hex(): 'Deposit',
    '0x' + Web3.keccak(text='RewardClaimed(uint256,address,uint256)').hex(): 'RewardClaimed',
}


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
            time.sleep(0.6)


def enc(v):
    return format(v & (2**256 - 1), '064x')


def W_(r):
    if not r or r == '0x':
        return []
    h = r[2:]
    return [h[i:i + 64] for i in range(0, len(h), 64)]


def sel(s):
    return '0x' + Web3.keccak(text=s).hex()[:8]


def call(to, data, frm=None):
    o = {'to': to, 'data': data}
    if frm:
        o['from'] = frm
    r = rpc('eth_call', [o, 'latest'])
    return None if 'error' in r else r.get('result')


head = int(rpc('eth_blockNumber', [])['result'], 16)
print(f'head={head}')

# find the tx that entered our position into farming (any event from FC mentioning TID)
print('\n=== FarmingCenter events mentioning our tokenId (last 100k blocks) ===')
found = []
for topic, name in SIGS.items():
    b = head - 100000
    while b <= head:
        e = min(b + 1999, head)
        r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e),
                                 'address': FC, 'topics': [topic]}])
        for l in r.get('result', []):
            if str(TID) in str(int(l['topics'][1], 16) if len(l['topics']) > 1 else ''):
                found.append((int(l['blockNumber'], 16), name, l['transactionHash']))
        b = e + 1
for blk, name, h in sorted(found):
    ts = int(rpc('eth_getBlockByNumber', [hex(blk), False]).get('result', {}).get('timestamp', '0x0'), 16)
    print(f'  blk {blk} {time.strftime("%m-%d %H:%M UTC", time.gmtime(ts))} {name} tx={h[:18]}')
if not found:
    print('  (none found by topic match — checking any FC log for our tokenId)')

# Fallback: scan ALL FC logs for our tokenId in the data/topics
print('\n=== broad scan: FC logs containing tokenId 3478420 ===')
b = head - 100000
hits = []
while b <= head:
    e = min(b + 1999, head)
    r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e), 'address': FC}])
    for l in r.get('result', []):
        if hex(TID)[2:].zfill(64) in l['data'] or any(hex(TID)[2:] in t for t in l['topics']):
            hits.append((int(l['blockNumber'], 16), l['topics'][0][:10], l['transactionHash']))
    b = e + 1
for blk, t0, h in sorted(hits)[:12]:
    ts = int(rpc('eth_getBlockByNumber', [hex(blk), False]).get('result', {}).get('timestamp', '0x0'), 16)
    print(f'  blk {blk} {time.strftime("%m-%d %H:%M UTC", time.gmtime(ts))} topic={t0} tx={h[:18]}')
print(f'  total hits: {len(hits)}')

# current claimable for reference
r = call(EF, sel('incentiveKeys(address)') + enc(int(POOL, 16)))
w = W_(r)
kw = (enc(int('0x' + w[0][-40:], 16)) + enc(int('0x' + w[1][-40:], 16)) +
      enc(int('0x' + w[2][-40:], 16)) + enc(int(w[3], 16)))
cr = call(FC, sel('collectRewards((address,address,address,uint256),uint256)') + kw + enc(TID),
          frm=WALLET)
ww = W_(cr)
if len(ww) >= 2:
    print(f'\nclaimable now: {int(ww[0],16)/1e18:.6f} BLACK')
