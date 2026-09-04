#!/usr/bin/env python3
"""Rebalance WAVAX -> USDC so USDC = target share of total working capital (default 60/40)."""
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
TARGET_USDC_SHARE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.60
SLIPPAGE = 0.03

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

usdc_bal = bal(USDC) / 1e6
wavax_bal = bal(WAVAX) / 1e18
router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
path = {"pairBinSteps": [BIN_STEP], "versions": [VERSION_V22], "tokenPath": [WAVAX, USDC]}

# Probe price: simulate tiny swap to get implied USDC per WAVAX
probe_fn = router.functions.swapExactTokensForTokens(int(0.01 * 1e18), 0, path, acct.address, int(time.time()) + 600)
probe_out = probe_fn.call({"from": acct.address})
price = (probe_out / 1e6) / 0.01
print(f"Implied price: ${price:.4f} USDC/WAVAX")

total = usdc_bal + wavax_bal * price
target_usdc = total * TARGET_USDC_SHARE
need_usdc = target_usdc - usdc_bal
print(f"Working capital: ${total:.2f} | USDC ${usdc_bal:.2f} ({usdc_bal/total*100:.0f}%) | target ${target_usdc:.2f} ({TARGET_USDC_SHARE*100:.0f}%)")
if need_usdc <= 0.05:
    print("Already balanced. No swap needed.")
    sys.exit(0)

wavax_to_swap = min(need_usdc / price, wavax_bal - 0.01)
print(f"Swapping {wavax_to_swap:.6f} WAVAX -> ~${wavax_to_swap*price:.2f} USDC")

# Approve router for WAVAX
approve_sel = "0x095ea7b3" + ROUTER[2:].lower().zfill(64) + hex(2**256 - 1)[2:].zfill(64)
nonce = w3.eth.get_transaction_count(acct.address)
approve_tx = {"to": WAVAX, "data": approve_sel, "nonce": nonce,
              "gas": 100000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": 43114}
signed = acct.sign_transaction(approve_tx)
h = w3.eth.send_raw_transaction(signed.raw_transaction)
w3.eth.wait_for_transaction_receipt(h, timeout=120)
print("Approved WAVAX to router.")

fn = router.functions.swapExactTokensForTokens(int(wavax_to_swap * 1e18), 0, path, acct.address, int(time.time()) + 600)
sim_out = fn.call({"from": acct.address})
print(f"Simulated: {wavax_to_swap:.6f} WAVAX -> {sim_out/1e6:.4f} USDC")
amount_out_min = int(sim_out * (1 - SLIPPAGE))

tx = fn.build_transaction({"from": acct.address,
                           "nonce": w3.eth.get_transaction_count(acct.address),
                           "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3)})
signed = acct.sign_transaction(tx)
h = w3.eth.send_raw_transaction(signed.raw_transaction)
rcpt = w3.eth.wait_for_transaction_receipt(h, timeout=120)
print("Swap tx:", h.hex(), "status:", rcpt["status"])

usdc_now = bal(USDC) / 1e6
wavax_now = bal(WAVAX) / 1e18
total_now = usdc_now + wavax_now * price
print(f"Now: USDC ${usdc_now:.2f} ({usdc_now/total_now*100:.0f}%) | WAVAX {wavax_now:.6f} (~${wavax_now*price:.2f}, {wavax_now*price/total_now*100:.0f}%)")