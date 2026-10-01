#!/usr/bin/env python3
"""CORRECTED BLACK-emissions verification.

Previous attempt encoded collectRewards(IncentiveKey,uint256) with an offset —
but IncentiveKey is a STATIC struct (4 value types), so it must be encoded
INLINE (5 words total). The bad encoding made the contract read a garbage
tokenId, hence "ERC721: invalid token ID".

Ground truth = simulate collectRewards (what can we actually claim).
"""
import json, urllib.request
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
BLACK = '0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6'
WALLET = _sw_wallet()
TIDS = [3476545, 3478420]

w3 = Web3(Web3.HTTPProvider(RPC))


def call(to, data, frm=None):
    o = {'to': to, 'data': data}
    if frm:
        o['from'] = frm
    d = {'jsonrpc': '2.0', 'method': 'eth_call', 'params': [o, 'latest'], 'id': 1}
    req = urllib.request.Request(RPC, json.dumps(d).encode(),
                                 {'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=25))
    if 'error' in r:
        return 'ERR:' + str(r['error'].get('message', r['error']))[:140]
    return r.get('result')


def enc(v):
    return format(v & (2**256 - 1), '064x')


def W_(r):
    if not r or r == '0x' or str(r).startswith('ERR'):
        return []
    h = r[2:]
    return [h[i:i + 64] for i in range(0, len(h), 64)]


def sel(sig):
    return '0x' + Web3.keccak(text=sig).hex()[:8]


# incentive key
r = call(EF, sel('incentiveKeys(address)') + enc(int(POOL, 16)))
w = W_(r)
reward, bonus, pool, nonce = ('0x' + w[0][-40:], '0x' + w[1][-40:], '0x' + w[2][-40:], int(w[3], 16))
key_words = enc(int(reward, 16)) + enc(int(bonus, 16)) + enc(int(pool, 16)) + enc(nonce)
expected_id = Web3.keccak(hexstr='0x' + key_words).hex()
print('=== INCENTIVE KEY ===')
print(f'  reward={reward}  bonus={bonus}')
print(f'  pool  ={pool}  nonce={nonce}')
print(f'  incentiveId={expected_id}')

print('\n=== FARMING REGISTRATION ===')
for tid in TIDS:
    d = (call(FC, sel('deposits(uint256)') + enc(tid)) or '').replace('0x', '')
    is_zero = set(d) == {'0'}
    print(f'  #{tid}: {"NOT farmed" if is_zero else "FARMED (id " + d[:16] + "...)"}'
          f'  match={d == expected_id}')

print('\n=== CLAIMABLE REWARDS (ground truth: simulate collectRewards) ===')
# static struct -> INLINE encoding: 4 key words + tokenId
for tid in TIDS:
    args = key_words + enc(tid)
    res = call(FC, sel('collectRewards((address,address,address,uint256),uint256)') + args, frm=WALLET)
    w2 = W_(res)
    if len(w2) >= 2:
        print(f'  #{tid}: claimable = {int(w2[0],16)/1e18:.12f} BLACK '
              f'+ bonus {int(w2[1],16)/1e18:.12f}')
    else:
        print(f'  #{tid}: {res}')

print('\n=== ENTER-FARMING re-sim (already entered?) ===')
for tid in TIDS:
    args = key_words + enc(tid)
    res = call(FC, sel('enterFarming((address,address,address,uint256),uint256)') + args, frm=WALLET)
    print(f'  #{tid}: {res if str(res).startswith("ERR") else "would SUCCEED (not currently entered)"}')

print('\n=== ETERNAL FARMING farm state ===')
for sig in ['getRewardRates(bytes32)']:
    pass
res = call(EF, sel('farms(bytes32)') + expected_id.replace('0x', ''))
w3_ = W_(res)
print(f'  EF.farms(incentiveId) -> {len(w3_)} words')
for i, x in enumerate(w3_[:8]):
    print(f'      [{i}] {int(x,16)}')
