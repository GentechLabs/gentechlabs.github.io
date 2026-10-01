#!/usr/bin/env python3
"""Decisive LFJ investigation: where did the ~$11 go on Sep 10?

Examines the exact txs that moved USDC/WAVAX to the LFJ pair, decodes their
receipt logs, and checks whether ANY LB-token (ERC1155) was minted to the
wallet or to anyone else. Answers: recoverable, or gone?
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
USDC = '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e'
WAVAX = '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7'

SIG = {
    '0x' + Web3.keccak(text='TransferSingle(address,address,address,uint256,uint256)').hex():
        'TransferSingle',
    '0x' + Web3.keccak(text='TransferBatch(address,address,address,uint256[],uint256[])').hex():
        'TransferBatch',
    '0x' + Web3.keccak(text='Swap(address,address,uint256,uint256,uint256,uint256,uint256,uint256)').hex():
        'Swap',
    '0x' + Web3.keccak(text='DepositedToBins(address,address,uint256[],uint256[],uint256[])').hex():
        'DepositedToBins',
    '0x' + Web3.keccak(text='WithdrawnFromBins(address,address,uint256[],uint256[],uint256[])').hex():
        'WithdrawnFromBins',
    '0x' + Web3.keccak(text='Transfer(address,address,uint256)').hex(): 'Transfer(ERC20)',
}


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


def addr_of(topic):
    return '0x' + topic[-40:]


TXS = [
    ('0xd915141e58', None),   # add? at 11:57
    ('0x098b2836d9', None),   # remove at 11:57
    ('0xc7b917c39b', None),   # IN 8.02 USDC at 12:08
    ('0xdc71a26d57', None),   # OUT 5.5 USDC at 12:09
]

print('=== scanning wallet<->LFJ pair txs, Sep 10 11:50-13:00 ===')
# find full hashes by block range + pair logs
logs = []
b = 94935250
while b <= 94936000:
    e = min(b + 1999, 94936000)
    r = rpc('eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(e), 'address': PAIR}])
    logs.extend(r.get('result', []))
    b = e + 1
print(f'pair logs in window: {len(logs)}')

by_tx = {}
for l in logs:
    by_tx.setdefault(l['transactionHash'], []).append(l)
print(f'distinct txs touching the pair: {len(by_tx)}\n')

wlow = W.lower()
for h, ls in sorted(by_tx.items(), key=lambda x: int(x[1][0]['blockNumber'], 16)):
    blk = int(ls[0]['blockNumber'], 16)
    t = rpc('eth_getTransactionByHash', [h]).get('result') or {}
    rc = rpc('eth_getTransactionReceipt', [h]).get('result') or {}
    frm = (t.get('from') or '').lower()
    to = (t.get('to') or '').lower()
    st = int(rc.get('status', '0x0'), 16)
    if frm != wlow and to != PAIR:
        continue
    print(f'--- blk {blk} tx {h[:14]} status={st} from={frm[:12]} to={to[:12]} '
          f'sel={(t.get("input") or "0x")[:10]}')
    for l in ls:
        name = SIG.get(l['topics'][0], l['topics'][0][:10])
        if name in ('TransferSingle', 'TransferBatch'):
            d = l['data'][2:]
            if name == 'TransferSingle':
                tid = int(d[0:64], 16); val = int(d[64:128], 16)
                print(f'      {name}: from={addr_of(l["topics"][2])[:12]} '
                      f'to={addr_of(l["topics"][3])[:12]} bin={tid} value={val}')
            else:
                ids = [int(d[i:i+64], 16) for i in range(0, 128, 64)]
                print(f'      {name}: from={addr_of(l["topics"][2])[:12]} '
                      f'to={addr_of(l["topics"][3])[:12]}')
        else:
            print(f'      {name}')
    print()

# FINAL: any LB token anywhere for the wallet, right now?
print('=== does the wallet hold ANY LB token right now? ===')
ABI = [{'inputs': [{'name': 'account', 'type': 'address'}, {'name': 'id', 'type': 'uint256'}],
        'name': 'balanceOf', 'outputs': [{'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function'},
       {'inputs': [], 'name': 'getActiveId', 'outputs': [{'name': '', 'type': 'uint24'}],
        'stateMutability': 'view', 'type': 'function'}]
w3 = Web3(Web3.HTTPProvider(RPC))
c = w3.eth.contract(address=Web3.to_checksum_address(PAIR), abi=ABI)
aid = c.functions.getActiveId().call()
hits = 0
for bid in range(aid - 200, aid + 201):
    try:
        if c.functions.balanceOf(Web3.to_checksum_address(W), bid).call() > 0:
            print(f'  bin {bid}: HAS BALANCE')
            hits += 1
    except Exception:
        pass
print(f'  bins with balance (active±200): {hits}')
