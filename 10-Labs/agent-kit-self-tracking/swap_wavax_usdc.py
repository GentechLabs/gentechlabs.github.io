#!/usr/bin/env python3
"""Swap all WAVAX -> USDC on LFJ V2.2 (proven ABI pattern), keep native AVAX for gas."""
import json, sys, time, urllib.request
from eth_account import Account
from web3 import Web3

RPC = "https://api.avax.network/ext/bc/C/rpc"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
ROUTER = "0x18556DA13313f3532c54711497A8FedAC273220E"
BIN_STEP = 10
VERSION_V22 = 3
KEY_FILE = "/root/.blockrun/almanak-steward-key"

ROUTER_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"components":[{"internalType":"uint256[]","name":"pairBinSteps","type":"uint256[]"},{"internalType":"enum ILBRouter.Version[]","name":"versions","type":"uint8[]"},{"internalType":"address[]","name":"tokenPath","type":"address[]"}],"internalType":"struct ILBRouter.Path","name":"path","type":"tuple"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]')

w3 = Web3(Web3.HTTPProvider(RPC))
with open(KEY_FILE) as f:
    acct = Account.from_key(f.read().strip())
print("Sender:", acct.address)
if acct.address.lower() != "0x572abd6461bed2258615e6b99c585ab7c5d05037":
    print("Key mismatch!"); sys.exit(1)

def call(m, p):
    data = {"jsonrpc": "2.0", "method": m, "params": p, "id": 1}
    req = urllib.request.Request(RPC, json.dumps(data).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["result"]

def bal(tok):
    sel = "0x70a08231" + acct.address[2:].lower().zfill(64)
    r = call("eth_call", [{"to": tok, "data": sel}, "latest"])
    return int(r, 16)

wavax_bal = bal(WAVAX)
print(f"WAVAX to swap: {wavax_bal/1e18:.6f}")

# Approve router to spend WAVAX
approve_sel = "0x095ea7b3" + ROUTER[2:].lower().zfill(64) + hex(2**256 - 1)[2:].zfill(64)
nonce = w3.eth.get_transaction_count(acct.address)
approve_tx = {"to": WAVAX, "data": approve_sel, "nonce": nonce,
              "gas": 100000, "gasPrice": w3.eth.gas_price, "chainId": 43114}
signed = acct.sign_transaction(approve_tx)
h = w3.eth.send_raw_transaction(signed.raw_transaction)
w3.eth.wait_for_transaction_receipt(h, timeout=120)
print("Approved. tx:", h.hex())

# Swap WAVAX -> USDC via ABI
router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
path = {"pairBinSteps": [BIN_STEP], "versions": [VERSION_V22], "tokenPath": [WAVAX, USDC]}
fn = router.functions.swapExactTokensForTokens(wavax_bal, 0, path, acct.address, int(time.time()) + 600)

# Simulate first (safety)
try:
    out = fn.call({"from": acct.address})
    print(f"Simulated swap: {wavax_bal/1e18:.6f} WAVAX -> {out/1e6:.4f} USDC")
except Exception as e:
    print(f"❌ Simulation reverted: {str(e)[:200]}"); sys.exit(1)

tx = fn.build_transaction({"from": acct.address,
                           "nonce": w3.eth.get_transaction_count(acct.address),
                           "gas": 400000, "gasPrice": w3.eth.gas_price})
signed = acct.sign_transaction(tx)
h = w3.eth.send_raw_transaction(signed.raw_transaction)
print("Swap tx:", h.hex())
rcpt = w3.eth.wait_for_transaction_receipt(h, timeout=120)
print("Swap status:", rcpt["status"], "(1=success)")
print(f"USDC now: {bal(USDC)/1e6:.4f}")
