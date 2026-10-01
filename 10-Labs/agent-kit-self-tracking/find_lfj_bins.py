#!/usr/bin/env python3
"""Locate the wallet's LFJ V2.2 bin liquidity via ERC1155 TransferSingle logs.

LFJ V2.2 positions are per-bin ERC1155 balances, NOT an ERC20 LP token. A
narrow bin scan misses out-of-range liquidity, so we find the bin ids from the
wallet's own transfer history and value exactly those.
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
W = _sw_wallet()
PAIR = '0x864d4e5ee7318e97483db7eb0912e09f161516ea'
PX = 7.72
TS_SINGLE = '0x' + Web3.keccak(
    text='TransferSingle(address,address,address,uint256,uint256)').hex()
TS_BATCH = '0x' + Web3.keccak(
    text='TransferBatch(address,address,address,uint256[],uint256[])').hex()


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


head = int(rpc('eth_blockNumber', [])['result'], 16)
start = head - 12 * 43200
wpad = '0x' + '0' * 24 + W[2:].lower()

bin_ids = set()
# to = wallet
b = start
while b <= head:
    e = min(b + 1999, head)
    r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e), 'address': PAIR,
                             'topics': [TS_SINGLE, None, None, wpad]}])
    for l in r.get('result', []):
        d = l['data'][2:]
        bin_ids.add(int(d[0:64], 16))
    b = e + 1
# from = wallet
b = start
while b <= head:
    e = min(b + 1999, head)
    r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e), 'address': PAIR,
                             'topics': [TS_SINGLE, None, wpad]}])
    for l in r.get('result', []):
        d = l['data'][2:]
        bin_ids.add(int(d[0:64], 16))
    b = e + 1

print(f'bins touched by wallet in 12d: {len(bin_ids)}')
if bin_ids:
    print('  ids:', sorted(bin_ids)[:40])

w3 = Web3(Web3.HTTPProvider(RPC))
ABI = [{'inputs': [{'name': 'account', 'type': 'address'}, {'name': 'id', 'type': 'uint256'}],
        'name': 'balanceOf', 'outputs': [{'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function'},
       {'inputs': [{'name': 'id', 'type': 'uint256'}], 'name': 'totalSupply',
        'outputs': [{'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'},
       {'inputs': [{'name': 'id', 'type': 'uint256'}], 'name': 'getBin',
        'outputs': [{'name': 'binReserveX', 'type': 'uint128'},
                    {'name': 'binReserveY', 'type': 'uint128'}],
        'stateMutability': 'view', 'type': 'function'},
       {'inputs': [], 'name': 'getActiveId', 'outputs': [{'name': '', 'type': 'uint24'}],
        'stateMutability': 'view', 'type': 'function'}]
c = w3.eth.contract(address=Web3.to_checksum_address(PAIR), abi=ABI)
aid = c.functions.getActiveId().call()
print(f'\nactive bin id: {aid}\n')

total = 0.0
held = []
for bid in sorted(bin_ids):
    try:
        bal = c.functions.balanceOf(Web3.to_checksum_address(W), bid).call()
        if bal == 0:
            continue
        ts = c.functions.totalSupply(bid).call()
        rx, ry = c.functions.getBin(bid).call()
        share = bal / ts if ts else 0
        vx, vy = rx / 1e18 * share, ry / 1e6 * share
        v = vx * PX + vy
        total += v
        held.append((bid, share, vx, vy, v, bid == aid))
    except Exception:
        pass

for bid, share, vx, vy, v, is_act in held:
    print(f'  bin {bid}{"  <-- ACTIVE" if is_act else "  (out of range)"}: '
          f'{share*100:.4f}% -> {vx:.6f} WAVAX + {vy:.4f} USDC = ${v:.2f}')
print(f'\n=== WALLET LFJ V2.2 BIN VALUE: ${total:.2f} ===')
