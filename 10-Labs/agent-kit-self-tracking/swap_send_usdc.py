#!/usr/bin/env python3
"""
Swap WAVAX → USDC on Avalanche (LFJ V2.2 router), then send ALL USDC to
Jordan's wallet. Farm wind-down (Aug 21 2026) — Jordan pulling capital.

Brain-confirmed: 0xeEe3fe6C5604C1069a50690043DE57848826e6C9 has received our
USDC before (Aug 11 sweep ~43.72 USDC). Destination is proven good.

Steps:
  1. Approve WAVAX to LFJ V2.2 router
  2. swapExactTokensForTokens: WAVAX → USDC (pair binStep 10, version 2)
  3. Read resulting USDC balance, send ALL (incl. existing 6.51) to dest
"""
import json, sys, time, urllib.request
from eth_account import Account
from web3 import Web3

RPC = "https://avalanche.drpc.org"  # api.avax.network rejects contract-calls with "invalid sender"; drpc works
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
LBROUTER = "0x18556DA13313f3532c54711497A8FedAC273220E"
LBPAIR = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
BIN_STEP = 10
DEST = Web3.to_checksum_address("0xeEe3fe6C5604C1069a50690043DE57848826e6C9")
KEY_FILE = "/root/.blockrun/almanak-steward-key"
# Public AVAX RPC node rejects txs below a gas-price floor; the node's
# eth_gasPrice (0.064 gwei) is below it and yields "invalid sender". Use a
# fixed, safe 25 gwei so the tx is accepted. (Verified: 0-value self-tx at
# 25 gwei succeeds.)
GAS_PRICE = 25_000_000_000  # 25 gwei

w3 = Web3(Web3.HTTPProvider(RPC))
with open(KEY_FILE) as f:
    acct = Account.from_key(f.read().strip())

ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "a", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "s", "type": "address"}, {"name": "v", "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [{"name": "o", "type": "address"}, {"name": "s", "type": "address"}],
     "name": "allowance", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
]

ROUTER_ABI = [{
    "inputs": [
        {"name": "amountIn", "type": "uint256"},
        {"name": "amountOutMin", "type": "uint256"},
        {"name": "swapParameters", "components": [
            {"name": "pairBinSteps", "type": "uint256[]"},
            {"name": "versions", "type": "uint8[]"},
            {"name": "tokenPath", "type": "address[]"},
        ], "type": "tuple"},
        {"name": "to", "type": "address"},
        {"name": "deadline", "type": "uint256"},
    ],
    "name": "swapExactTokensForTokens",
    "outputs": [{"name": "amounts", "type": "uint256[]"}],
    "stateMutability": "nonpayable", "type": "function",
}, {
    "inputs": [],
    "name": "getWavax", "outputs": [{"name": "", "type": "address"}],
    "stateMutability": "view", "type": "function",
}]

# Minimal transfer ABI
TRANSFER_ABI = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "v", "type": "uint256"}],
                 "name": "transfer", "outputs": [{"name": "", "type": "bool"}],
                 "stateMutability": "nonpayable", "type": "function"}]


def erc20_bal(token, addr):
    c = w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
    return c.functions.balanceOf(addr).call()


def main():
    print("Sender:", acct.address)
    print("Dest:", DEST)
    wavax_bal = erc20_bal(WAVAX, acct.address) / 1e18
    usdc_bal = erc20_bal(USDC, acct.address) / 1e6
    print(f"Before — WAVAX: {wavax_bal:.6f} | USDC: {usdc_bal:.6f}")
    if wavax_bal <= 0:
        print("No WAVAX to swap — skipping swap, only sending existing USDC.")
    else:
        # 1. Approve WAVAX to router
        router = w3.eth.contract(address=Web3.to_checksum_address(LBROUTER), abi=ROUTER_ABI)
        w = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20_ABI)
        allowance = w.functions.allowance(acct.address, Web3.to_checksum_address(LBROUTER)).call()
        amount_in = int(wavax_bal * 1e18)
        if allowance < amount_in:
            print(f"Approving WAVAX to router (allowance {allowance/1e18:.4f})...")
            approve_tx = w.functions.approve(Web3.to_checksum_address(LBROUTER), 2**256 - 1).build_transaction({
                "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
                "gas": 100000, "gasPrice": GAS_PRICE, "chainId": 43114})
            signed = acct.sign_transaction(approve_tx)
            txh = w3.eth.send_raw_transaction(signed.raw_transaction)
            rcpt = w3.eth.wait_for_transaction_receipt(txh, timeout=120)
            print(f"Approve tx {txh.hex()} status {rcpt['status']}")
        else:
            print("WAVAX already approved.")

        # 2. Swap WAVAX → USDC via LFJ V2.2 router (pair binStep 50, version 2)
        swap_params = {
            "pairBinSteps": [BIN_STEP],
            "versions": [2],
            "tokenPath": [Web3.to_checksum_address(WAVAX), Web3.to_checksum_address(USDC)],
        }
        swap_tx = router.functions.swapExactTokensForTokens(
            amount_in, 0, swap_params, acct.address, int(time.time()) + 300
        ).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 250000, "gasPrice": GAS_PRICE, "chainId": 43114})
        signed = acct.sign_transaction(swap_tx)
        txh = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"Swap tx: {txh.hex()}")
        rcpt = w3.eth.wait_for_transaction_receipt(txh, timeout=120)
        print(f"Swap status: {rcpt['status']} (1=success)")

    # 3. Send all USDC to dest
    final_usdc = erc20_bal(USDC, acct.address) / 1e6
    print(f"After swap — USDC: {final_usdc:.6f}")
    if final_usdc <= 0:
        print("No USDC to send — aborting.")
        return
    u = w3.eth.contract(address=Web3.to_checksum_address(USDC), abi=TRANSFER_ABI)
    amount = int(final_usdc * 1e6)
    send_tx = u.functions.transfer(DEST, amount).build_transaction({
        "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 100000, "gasPrice": GAS_PRICE, "chainId": 4314})
    signed = acct.sign_transaction(send_tx)
    txh = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Send USDC tx: {txh.hex()}")
    rcpt = w3.eth.wait_for_transaction_receipt(txh, timeout=120)
    print(f"Send status: {rcpt['status']} (1=success)  |  Sent {final_usdc:.6f} USDC to {DEST}")
    print("Remaining USDC:", erc20_bal(USDC, acct.address) / 1e6)


if __name__ == "__main__":
    main()
