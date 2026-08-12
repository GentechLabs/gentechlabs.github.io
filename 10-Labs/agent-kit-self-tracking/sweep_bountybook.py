#!/usr/bin/env python3
"""Sweep BountyBook agent-wallet USDC on Base → GenTech treasury wallet.

BountyBook pays USDC on Base (chain 8453) to the agent wallet that claimed the job.
This script sweeps those earnings to the Agentic Treasury wallet, so the Steward's
deposit-detection counts them as income (milestone progress on the D5 ladder).

Same EOA works on both Avalanche and Base; we're sending Base-native USDC.

Safety:
  - Dry-run by default (reads balance, builds tx, NO funds move)
  - --execute --yes for real transfer (guarded)
  - Skips if balance below a minimum (don't burn gas on dust)
  - Logs a receipt with tx hash + amount swept
"""
import json, os, sys, time, urllib.request
from eth_account import Account
from web3 import Web3

# ── Config ──────────────────────────────────────────────────────────────
BASE_RPC = "https://base.drpc.org"                      # most reliable free Base RPC
BASE_CHAIN_ID = 8453
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" # USDC on Base (native)
AGENT_KEY_FILE = "/root/.blockrun/bountybook-agent"      # BountyBook throwaway wallet
TREASURY_WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"  # Steward/treasury (Base)
MIN_SWEEP_USD = 5.0                                     # don't sweep dust < $5
GAS_LIMIT = 100_000
DEST_TAG = "gentech-treasury"


def _usdc_balance(w3, acct_addr: str) -> int:
    # balanceOf(address) = 0x70a08231
    data = "0x70a08231" + acct_addr[2:].lower().zfill(64)
    return int.from_bytes(w3.eth.call({"to": USDC_BASE, "data": data}), "big")


def _base_eth_for_gas(w3, acct_addr: str) -> float:
    return w3.eth.get_balance(acct_addr) / 1e18


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Sweep BountyBook USDC (Base) → treasury")
    ap.add_argument("--execute", action="store_true", help="actually send (guarded)")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()
    execute = args.execute and args.yes

    w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    if not w3.is_connected():
        print("ERROR: cannot connect to Base RPC")
        return 1

    with open(AGENT_KEY_FILE) as f:
        acct = Account.from_key(f.read().strip())
    print("Agent wallet (Base):", acct.address)

    bal = _usdc_balance(w3, acct.address)
    usdc = bal / 1e6
    gas_eth = _base_eth_for_gas(w3, acct.address)
    print(f"USDC balance: {usdc:.4f} USDC | gas: {gas_eth:.6f} ETH")

    if usdc < MIN_SWEEP_USD:
        print(f"Below min sweep (${MIN_SWEEP_USD}); skipping (dust stays in agent wallet).")
        return 0

    if gas_eth < 0.0005:
        print("ERROR: insufficient Base ETH for gas on agent wallet. Refuel ~$0.01 ETH.")
        return 1

    amount = bal  # sweep full balance
    data = "0xa9059cbb" + TREASURY_WALLET[2:].lower().zfill(64) + hex(amount)[2:].zfill(64)

    if not execute:
        print(f"[DRY-RUN] would send {usdc:.4f} USDC (Base) → {TREASURY_WALLET} ({DEST_TAG})")
        print("Run with --execute --yes to actually sweep.")
        return 0

    nonce = w3.eth.get_transaction_count(acct.address)
    tx = {
        "to": USDC_BASE, "data": data, "nonce": nonce,
        "gas": GAS_LIMIT, "gasPrice": w3.eth.gas_price, "chainId": BASE_CHAIN_ID,
    }
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Sweeping {usdc:.4f} USDC → treasury... TX: {tx_hash.hex()}")
    rcpt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"Status: {rcpt['status']} (1=success)")
    return 0 if rcpt["status"] == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
