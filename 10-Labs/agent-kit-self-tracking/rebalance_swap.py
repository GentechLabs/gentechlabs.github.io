#!/usr/bin/env python3
"""Rebalance idle WAVAX/USDC so both sides are present for compounding.

Blackhole-aware (Jordan Sep 10 2026): the old version used the LFJ bin router
(0x18556...) which is FLAT since we moved to Blackhole — every probe swap
reverted with 0x32e2717a, and it only swapped WAVAX->USDC (wrong direction for
our excess-USDC case). This version uses the Blackhole router (LEGACY_ROUTER,
Trader Joe-style route struct) and swaps whichever side is in excess so the
idle becomes a balanced WAVAX+USDC pot that increaseLiquidity can accept.

Usage: python3 rebalance_swap.py [target_usdc_share]   (default 0.50)
"""
import json, sys, time, urllib.request
from eth_account import Account
from web3 import Web3

RPC = "https://api.avax.network/ext/bc/C/rpc"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
# Blackhole router (Trader Joe-style route struct) — NOT the flat LFJ bin router.
ROUTER = "0xe946A9f39312E2346BA79DAb865B0e9A74f2F981"
POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"
KEY_FILE = "/root/.blockrun/almanak-steward-key"
TARGET_USDC_SHARE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.50
SLIPPAGE = 0.03

# Blackhole router swapExactTokensForTokens(amountIn, amountOutMin, routes[], to, deadline)
ROUTER_ABI = json.loads('[{"inputs":[{"name":"amountIn","type":"uint256"},{"name":"amountOutMin","type":"uint256"},{"components":[{"name":"pair","type":"address"},{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"stable","type":"bool"},{"name":"concentrated","type":"bool"},{"name":"receiver","type":"address"}],"name":"routes","type":"tuple[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}]')

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
router = w3.eth.contract(address=Web3.to_checksum_address(ROUTER), abi=ROUTER_ABI)

# Probe price: simulate a tiny swap to get implied USDC per WAVAX (or WAVAX per USDC)
# Use the Blackhole pool route (concentrated=True).
def route_for(frm, to):
    return [{"pair": Web3.to_checksum_address(POOL), "from": Web3.to_checksum_address(frm),
             "to": Web3.to_checksum_address(to), "stable": False, "concentrated": True,
             "receiver": acct.address}]

# Probe WAVAX->USDC price
probe_fn = router.functions.swapExactTokensForTokens(
    int(0.01 * 1e18), 0, route_for(WAVAX, USDC), acct.address, int(time.time()) + 600)
probe_out = probe_fn.call({"from": acct.address})
price = (probe_out / 1e6) / 0.01  # USDC per WAVAX
print(f"Implied price: ${price:.4f} USDC/WAVAX")

total = usdc_bal + wavax_bal * price
target_usdc = total * TARGET_USDC_SHARE
need_usdc = target_usdc - usdc_bal
print(f"Working capital: ${total:.2f} | USDC ${usdc_bal:.2f} ({usdc_bal/total*100:.0f}%) | "
      f"WAVAX {wavax_bal:.6f} (~${wavax_bal*price:.2f}) | target USDC {TARGET_USDC_SHARE*100:.0f}%")

if abs(need_usdc) <= 0.05:
    print("Already balanced. No swap needed.")
    sys.exit(0)

if need_usdc > 0:
    # Need more USDC -> swap WAVAX -> USDC
    wavax_to_swap = min(need_usdc / price, wavax_bal - 0.01)
    if wavax_to_swap <= 0:
        print("Not enough WAVAX to swap for USDC. Skipping.")
        sys.exit(0)
    frm, to = WAVAX, USDC
    amount_in = int(wavax_to_swap * 1e18)
    print(f"Swapping {wavax_to_swap:.6f} WAVAX -> ~${wavax_to_swap*price:.2f} USDC")
else:
    # Need more WAVAX -> swap USDC -> WAVAX (our current case: excess USDC)
    usdc_to_swap = min(-need_usdc, usdc_bal - 0.10)
    if usdc_to_swap <= 0:
        print("Not enough USDC to swap for WAVAX. Skipping.")
        sys.exit(0)
    frm, to = USDC, WAVAX
    amount_in = int(usdc_to_swap * 1e6)
    print(f"Swapping ${usdc_to_swap:.2f} USDC -> ~{usdc_to_swap/price:.6f} WAVAX")

# Approve router for the source token
approve_sel = "0x095ea7b3" + ROUTER[2:].lower().zfill(64) + hex(2**256 - 1)[2:].zfill(64)
nonce = w3.eth.get_transaction_count(acct.address)
approve_tx = {"to": frm, "data": approve_sel, "nonce": nonce,
              "gas": 100000, "gasPrice": int(w3.eth.gas_price * 1.3), "chainId": 43114}
signed = acct.sign_transaction(approve_tx)
h = w3.eth.send_raw_transaction(signed.raw_transaction)
w3.eth.wait_for_transaction_receipt(h, timeout=120)
print("Approved router for source token.")

fn = router.functions.swapExactTokensForTokens(
    amount_in, 0, route_for(frm, to), acct.address, int(time.time()) + 600)
sim_out = fn.call({"from": acct.address})
print(f"Simulated: {amount_in/1e18 if frm==WAVAX else amount_in/1e6:.6f} -> "
      f"{sim_out/1e6 if to==USDC else sim_out/1e18:.6f}")
amount_out_min = int(sim_out * (1 - SLIPPAGE))

tx = fn.build_transaction({"from": acct.address,
                           "nonce": w3.eth.get_transaction_count(acct.address),
                           "gas": 500000, "gasPrice": int(w3.eth.gas_price * 1.3)})
signed = acct.sign_transaction(tx)
h = w3.eth.send_raw_transaction(signed.raw_transaction)
rcpt = w3.eth.wait_for_transaction_receipt(h, timeout=120)
print("Swap tx:", h.hex(), "status:", rcpt["status"])
if rcpt["status"] != 1:
    print("❌ Swap REVERTED", file=sys.stderr)
    sys.exit(1)

usdc_now = bal(USDC) / 1e6
wavax_now = bal(WAVAX) / 1e18
total_now = usdc_now + wavax_now * price
print(f"Now: USDC ${usdc_now:.2f} ({usdc_now/total_now*100:.0f}%) | "
      f"WAVAX {wavax_now:.6f} (~${wavax_now*price:.2f}, {wavax_now*price/total_now*100:.0f}%)")
print("✅ Rebalanced — both sides present for compounding.")
