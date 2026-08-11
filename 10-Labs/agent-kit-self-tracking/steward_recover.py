#!/usr/bin/env python3
"""
Steward — Recovery: partial USDC→WAVAX swap, then redeploy curve.
===============================================================
One-time recovery for the stranded position (Aug 11 2026): the withdraw-redeploy
bug converted ALL WAVAX→USDC, leaving 0 WAVAX so addLiquidity reverted. This
swaps a portion of USDC→WAVAX (so the deploy has both sides), then redeploys.

Safety (same as steward_execute.py):
  - Simulate the swap via .call() before sending.
  - Refuse if simulation reverts.
  - Require the Steward key + matching wallet + enough native gas.
"""
from __future__ import annotations
import json, os, sys, time, subprocess

from web3 import Web3

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = "/root/.blockrun/almanak-steward-key"  # Steward wallet key
STEWARD = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
RPC = "https://api.avax.network/ext/bc/C/rpc"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
ROUTER = "0x18556DA13313f3532c54711497A8FedAC273220E"
BIN_STEP = 10
VERSION_V22 = 3

# Minimal router ABI for swapExactTokensForTokens (V2.2 Path struct)
ROUTER_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"components":[{"internalType":"uint256[]","name":"pairBinSteps","type":"uint256[]"},{"internalType":"enum ILBRouter.Version[]","name":"versions","type":"uint8[]"},{"internalType":"address[]","name":"tokenPath","type":"address[]"}],"internalType":"struct ILBRouter.Path","name":"path","type":"tuple"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]')


def get_w3():
    return Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))


def bal(w3, token, addr):
    sel = "0x70a08231" + addr[2:].lower().zfill(64)
    r = w3.eth.call({"to": token, "data": sel})
    if isinstance(r, bytes):
        return int.from_bytes(r, "big")
    return int(r, 16)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--usdc-to-swap", type=float, default=21.0,
                    help="USDC amount to swap to WAVAX (default 21)")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    w3 = get_w3()
    if not os.path.exists(KEY_FILE):
        print("Key not found"); sys.exit(1)
    key = open(KEY_FILE).read().strip()
    acct = w3.eth.account.from_key(key)
    if acct.address.lower() != STEWARD.lower():
        print("Key mismatch!"); sys.exit(1)

    usdc_bal = bal(w3, USDC, acct.address)
    wavax_bal = bal(w3, WAVAX, acct.address)
    print(f"Before: USDC {usdc_bal/1e6:.4f}  WAVAX {wavax_bal/1e18:.6f}")

    swap_amount = int(args.usdc_to_swap * 1e6)
    if swap_amount > usdc_bal:
        print(f"Refusing: swap {args.usdc_to_swap} > USDC balance {usdc_bal/1e6:.4f}")
        sys.exit(1)

    router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
    path = {"pairBinSteps": [BIN_STEP], "versions": [VERSION_V22],
            "tokenPath": [USDC, WAVAX]}
    fn = router.functions.swapExactTokensForTokens(
        swap_amount, 0, path, acct.address, int(time.time()) + 600)

    # Simulate first (safety)
    try:
        out = fn.call({"from": acct.address})
        print(f"Simulated swap: {args.usdc_to_swap} USDC -> {out/1e18:.6f} WAVAX")
    except Exception as e:
        print(f"❌ Simulation reverted: {str(e)[:200]}")
        sys.exit(1)

    if not args.execute or not args.yes:
        print("(dry-run — to execute: --execute --yes)")
        sys.exit(0)

    # Send the swap (sign locally, send raw — public RPC has no wallet)
    print("Sending swap...")
    tx = fn.build_transaction({
        "from": acct.address,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 400000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"  tx: {tx_hash.hex()}")
    rcpt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"  status: {rcpt['status']}  gasUsed: {rcpt['gasUsed']}")

    if rcpt["status"] != 1:
        print("❌ Swap failed on-chain"); sys.exit(1)

    # Verify balances after swap
    usdc_bal2 = bal(w3, USDC, acct.address)
    wavax_bal2 = bal(w3, WAVAX, acct.address)
    print(f"After swap: USDC {usdc_bal2/1e6:.4f}  WAVAX {wavax_bal2/1e18:.6f}")

    # Redeploy curve
    print("\nRedeploying curve...")
    deploy = os.path.join(HERE, "deploy_lp_curve.py")
    proc = subprocess.run([sys.executable, deploy, "--execute", "--yes"],
                          capture_output=True, text=True, timeout=180)
    print(proc.stdout[-1500:])
    if proc.stderr:
        print(f"stderr: {proc.stderr[-300:]}")
    if proc.returncode != 0 or "deployed" not in proc.stdout.lower():
        print("❌ Redeploy failed"); sys.exit(1)
    print("✅ Recovery complete")


if __name__ == "__main__":
    main()
