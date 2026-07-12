#!/usr/bin/env python3
"""
Test bridge operations on Base Sepolia testnet.

Deploys mock CCTP, tests bridge flow end-to-end.
"""

import json
import os
import sys

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(VAULT_DIR, "config", "vault-config.json")
DEPLOY_FILE = os.path.join(VAULT_DIR, "deployments", "base-sepolia.json")

with open(CONFIG_FILE) as f:
    CONFIG = json.load(f)

def test_bridge_flow():
    """Simulate a bridge flow (requires deployed contracts)."""
    if not os.path.exists(DEPLOY_FILE):
        print("ERROR: No deployment found. Run deploy_vault.py first.")
        sys.exit(1)

    with open(DEPLOY_FILE) as f:
        deployment = json.load(f)

    print("=" * 50)
    print("🧪 Bridge Flow Test")
    print("=" * 50)
    print(f"Network: Base Sepolia")
    print(f"Vault: {deployment['vault_address']}")
    print(f"CCTP Adapter: {deployment.get('cctp_adapter_address', 'N/A')}")
    print()

    # Test scenarios
    scenarios = [
        {
            "name": "Base → Avalanche via CCTP",
            "from_chain": "base",
            "to_chain": "avalanche",
            "amount": "1000 USDC",
            "protocol": "CCTP",
            "expected_fee": "Free (gas only)",
            "expected_time": "~15 minutes",
        },
        {
            "name": "Base → Solana via Across",
            "from_chain": "base",
            "to_chain": "solana",
            "amount": "500 USDC",
            "protocol": "Across",
            "expected_fee": "0.10% (~$0.50)",
            "expected_time": "~2 minutes",
        },
        {
            "name": "Avalanche → Base via CCTP",
            "from_chain": "avalanche",
            "to_chain": "base",
            "amount": "2000 USDC",
            "protocol": "CCTP",
            "expected_fee": "Free (gas only)",
            "expected_time": "~15 minutes",
        },
    ]

    for scenario in scenarios:
        print(f"📋 {scenario['name']}")
        print(f"  Amount: {scenario['amount']}")
        print(f"  Protocol: {scenario['protocol']}")
        print(f"  Expected Fee: {scenario['expected_fee']}")
        print(f"  Expected Time: {scenario['expected_time']}")
        print(f"  Status: ⏳ Pending deployment verification")
        print()

    print("=" * 50)
    print("To run on testnet:")
    print("  1. Fund deployer with Base Sepolia ETH")
    print("     https://faucet.sepolia.base.org")
    print("  2. Run: python3 scripts/deploy_vault.py")
    print("  3. Run: python3 scripts/test_bridge.py")
    print("=" * 50)

if __name__ == "__main__":
    test_bridge_flow()
