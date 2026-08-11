#!/usr/bin/env python3
"""Send USDC on Avalanche to a destination address."""
import json, os, sys, time, urllib.request
from eth_account import Account
from web3 import Web3

RPC = "https://api.avax.network/ext/bc/C/rpc"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
KEY_FILE = "/root/.blockrun/almanak-steward-key"
DEST = "0xeEe3fe6C5604C1069a50690043DE57848826e6C9"

w3 = Web3(Web3.HTTPProvider(RPC))
with open(KEY_FILE) as f:
    acct = Account.from_key(f.read().strip())
print("Sender:", acct.address)

# USDC transfer selector: transfer(address,uint256)
amount = int(21.33 * 1e6)  # 21.33 USDC
data = "0xa9059cbb" + DEST[2:].lower().zfill(64) + hex(amount)[2:].zfill(64)

# Build + sign + send raw
nonce = w3.eth.get_transaction_count(acct.address)
tx = {
    "to": USDC,
    "data": data,
    "nonce": nonce,
    "gas": 100000,
    "gasPrice": w3.eth.gas_price,
    "chainId": 43114,
}
signed = acct.sign_transaction(tx)
raw = signed.raw_transaction
print("Sending", amount / 1e6, "USDC to", DEST)
tx_hash = w3.eth.send_raw_transaction(raw)
print("TX:", tx_hash.hex())
rcpt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
print("Status:", rcpt["status"], "(1=success)")
