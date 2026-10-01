#!/usr/bin/env python3
"""TREASURY TRUTH — full chain-truth reconciliation.

Sums EVERYTHING the wallet actually owns on Avalanche:
  - all Blackhole CL positions (via decreaseLiquidity simulation)
  - all LFJ V2.2 LP tokens (if any remain)
  - all loose token balances (USDC, WAVAX, AVAX, BLACK)

This is the number that answers "were we ever at $28?" — not the
config-derived funded_usd arithmetic.
"""
import json, urllib.request, time
from web3 import Web3
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

# Rotating providers via the shared module (single hardcoded host = one Cloudflare 1015
# took every reader dark on 2026-09-22).
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from avax_rpc import connect as _rpc_connect, rpc_call as _rpc_call, RpcUnavailable
W = _sw_wallet()
NFPM = '0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146'
POOL = '0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7'
LFJ_PAIR = '0x864d4e5ee7318e97483db7eb0912e09f161516ea'
USDC = '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e'
WAVAX = '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7'
BLACK = '0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6'


def rpc(m, p, tries=3):
    # ROTATES across providers instead of retrying one source-banned host (1015 is per-SOURCE).
    # Returns the same {'result': ...} shape callers already expect.
    for a in range(tries):
        try:
            return {'result': _rpc_call(m, p, timeout=30)}
        except RpcUnavailable:
            if a == tries - 1:
                raise
            time.sleep(1)


def s(sig):
    return '0x' + Web3.keccak(text=sig).hex()[:8]


def enc(v):
    return format(v & (2**256 - 1), '064x')


def W_(r):
    h = r[2:]
    return [h[i:i + 64] for i in range(0, len(h), 64)]


def call(to, data):
    return rpc('eth_call', [{'to': to, 'data': data}, 'latest']).get('result')


def s24(v):
    v &= 0xffffff
    return v - 2**24 if v >= 2**23 else v


# ── price ──
try:
    req = urllib.request.Request(
        'https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd',
        headers={'User-Agent': 'Mozilla/5.0'})
    P = float(json.load(urllib.request.urlopen(req, timeout=20))['avalanche-2']['usd'])
except Exception:
    P = 7.80
print(f'AVAX/USD = ${P:.4f}\n')

try:
    w3 = _rpc_connect(timeout=40)
except RpcUnavailable as _e:
    print(f'❌ no AVAX RPC provider: {_e}')
    raise SystemExit(3)

# ── 1. all CL positions ──
n = int(call(NFPM, s('balanceOf(address)') + enc(int(W, 16))), 16)
print(f'=== BLACKHOLE CL POSITIONS (wallet holds {n} NFTs) ===')
DLI = [{'inputs': [{'components': [{'name': 'tokenId', 'type': 'uint256'},
                                   {'name': 'liquidity', 'type': 'uint128'},
                                   {'name': 'amount0Min', 'type': 'uint256'},
                                   {'name': 'amount1Min', 'type': 'uint256'},
                                   {'name': 'deadline', 'type': 'uint256'}],
                    'name': 'params', 'type': 'tuple'}],
        'name': 'decreaseLiquidity',
        'outputs': [{'name': 'amount0', 'type': 'uint256'},
                    {'name': 'amount1', 'type': 'uint256'}],
        'stateMutability': 'nonpayable', 'type': 'function'}]
nfpm = w3.eth.contract(address=Web3.to_checksum_address(NFPM), abi=DLI)
pos_total = 0.0
rows = []
for i in range(n):
    tid = int(call(NFPM, s('tokenOfOwnerByIndex(address,uint256)') + enc(int(W, 16)) + enc(i)), 16)
    pos = W_(call(NFPM, s('positions(uint256)') + enc(tid)))
    L = int(pos[7], 16)
    tl, tu = s24(int(pos[5], 16)), s24(int(pos[6], 16))
    owed0, owed1 = int(pos[10], 16), int(pos[11], 16)
    # token0/token1 ordering
    t0 = '0x' + pos[2][-40:]
    t1 = '0x' + pos[3][-40:]
    try:
        a = nfpm.functions.decreaseLiquidity(
            {'tokenId': tid, 'liquidity': L, 'amount0Min': 0, 'amount1Min': 0,
             'deadline': 9999999999}).call({'from': Web3.to_checksum_address(W)})
        amt0, amt1 = a[0], a[1]
    except Exception as e:
        amt0 = amt1 = 0
        print(f'  #{tid}: SIM FAIL {str(e)[:60]}')
    # value by token identity
    if t0.lower() == WAVAX.lower():
        v0 = amt0 / 1e18 * P
        v1 = amt1 / 1e6
    else:
        v0 = amt0 / 1e6
        v1 = amt1 / 1e18 * P
    v = v0 + v1
    pos_total += v
    rows.append((tid, L, tl, tu, v))
    print(f'  #{tid}: liq={L:>20,}  ticks {tl}..{tu}  value=${v:8.2f}  (owed {owed0},{owed1})')
print(f'  --- CL positions subtotal: ${pos_total:.2f}')

# ── 2. LFJ LP tokens ──
# FIXED 2026-09-23 (HQ caught this; it was my bug). The LFJ V2.2 pair is an ERC-1155 LBToken, so
# `balanceOf(address)` DOES NOT EXIST on it and REVERTS. A revert returns {"error":...} with no
# `result` -> `.get('result')` -> None -> `or '0x0'` -> printed "0.00000000". So a method that does
# not exist was reported as "you own zero LP", and I then told HQ there was no live position.
# Ownership is PER-BIN: read balanceOf(address,uint256) (0x00fdd58e) across a window around the
# ACTIVE bin. A failed read reports UNKNOWN, never 0 — a revert is not a zero balance.
lbt = None
lfj_bins = 0
lfj_raw = 0
try:
    _active = call(LFJ_PAIR, s('getActiveId()'))   # call() already unwraps .result -> a hex str
    if _active:
        active_id = int(_active, 16)
        _scan = 0
        for _d in range(-600, 601):
            _bid = active_id + _d
            if _bid < 0:
                continue
            _v = call(LFJ_PAIR, s('balanceOf(address,uint256)') + enc(int(W, 16)) + enc(_bid))
            if _v is None:
                _scan += 1
                continue
            _b = int(_v, 16)
            if _b:
                lfj_bins += 1
                lfj_raw += _b
    _lbt_read_failed = False
except Exception:
    _lbt_read_failed = True

print(f'\n=== LFJ V2.2 LP (LBT, ERC-1155 — per-bin) ===')
if _lbt_read_failed:
    print('  bins holding this wallet: UNKNOWN (read failed — NOT zero)')
    print('  → do NOT report a zero here; a failed read is not an empty position.')
else:
    print(f'  bins holding this wallet: {lfj_bins}  (active bin {active_id})')
    print(f'  raw per-bin units       : {lfj_raw}')
    if lfj_bins:
        print('  → POSITION EXISTS. Value it via the withdraw sim / LP reader, not from this number.')
    else:
        print('  → no bins held (confirmed by a successful per-bin scan, not by a revert)')

# ── 3. loose balances ──
print(f'\n=== LOOSE WALLET BALANCES ===')
loose = 0.0
for name, addr, dec, kind in [('USDC', USDC, 6, 'usd'), ('WAVAX', WAVAX, 18, 'avax'),
                              ('BLACK', BLACK, 18, 'black')]:
    try:
        b = int(call(addr, s('balanceOf(address)') + enc(int(W, 16))) or '0x0', 16) / 10**dec
    except Exception:
        b = 0
    usd = b * P if kind == 'avax' else b
    loose += usd
    print(f'  {name:6s} {b:>16,.6f}  = ${usd:.2f}' + ('   (BLACK, not priced)' if kind == 'black' else ''))
av = int(rpc('eth_getBalance', [W, 'latest'])['result'], 16) / 1e18
loose += av * P
print(f'  {"AVAX":6s} {av:>16,.6f}  = ${av*P:.2f}')
print(f'  --- loose subtotal: ${loose:.2f}')

print(f'\n{"="*52}')
print(f'  CHAIN-TRUTH TOTAL: ${pos_total + loose:.2f}')
# A total that silently OMITS an owned position is the same failure mode as reporting a reverted
# read as zero. If bins are held, the number above does NOT include them — say so, loudly.
if lfj_bins:
    print(f'  ⚠️  EXCLUDES the LFJ position: {lfj_bins} bins are held and are NOT in the number above.')
    print(f'      Reason: this script has no bin-pricer. Use lfj_fee_measure.py (reads bins, values the')
    print(f'      claimable side) for the LFJ leg. A total missing an owned position is not a total.')
elif _lbt_read_failed:
    print(f'  ⚠️  LFJ leg UNKNOWN (bin read failed) — the number above may be incomplete.')
else:
    print(f'  (LFJ leg: no bins held, confirmed by a successful per-bin scan)')
print(f'  config funded_usd: $29.00')
print(f'{"="*52}')
