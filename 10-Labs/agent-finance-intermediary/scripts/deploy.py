#!/usr/bin/env python3
"""
BNPL Testnet Deploy Script
Deploys BNPLEscrow.sol to Base Sepolia testnet.
Requires: forge, a funded wallet, and RPC URL.
"""

import subprocess, json, os, sys

# ── Config ──
RPC_URL = os.environ.get("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
PRIVATE_KEY = os.environ.get("DEPLOYER_KEY", "")
VERIFIER_URL = "https://api-sepolia.etherscan.io"
CHAIN_ID = 84532  # Base Sepolia

PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..")
CONTRACT = "BNPLEscrow"

def check_deps():
    """Verify forge is available."""
    r = subprocess.run(["forge", "--version"], capture_output=True, text=True)
    if r.returncode != 0:
        print("❌ forge not found. Install: curl -L https://foundry.paradigm.xyz | bash")
        sys.exit(1)
    print(f"✅ forge: {r.stdout.strip()}")

def deploy():
    """Deploy the contract."""
    if not PRIVATE_KEY:
        print("⚠️  No DEPLOYER_KEY set. Dry-run only.")
        print(f"   Set: export DEPLOYER_KEY=your_private_key")
        print(f"   RPC: {RPC_URL}")
        print(f"   Chain: Base Sepolia ({CHAIN_ID})")
        return

    print(f"\n🚀 Deploying {CONTRACT} to Base Sepolia...")
    print(f"   RPC: {RPC_URL}")
    print(f"   Chain ID: {CHAIN_ID}")

    cmd = [
        "forge", "create",
        "--rpc-url", RPC_URL,
        "--private-key", PRIVATE_KEY,
        "--chain-id", str(CHAIN_ID),
        f"contracts/{CONTRACT}.sol:{CONTRACT}",
        "--broadcast",
    ]

    r = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ Deploy failed:\n{r.stderr}")
        sys.exit(1)

    print(f"✅ Deployed!")
    print(r.stdout)

def verify(address):
    """Verify contract on Base Sepolia explorer."""
    cmd = [
        "forge", "verify-contract",
        "--chain-id", str(CHAIN_ID),
        "--verifier-url", VERIFIER_URL,
        "--verifier", "etherscan",
        address,
        f"contracts/{CONTRACT}.sol:{CONTRACT}",
    ]
    r = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"⚠️  Verify failed (may already be verified):\n{r.stderr}")
    else:
        print(f"✅ Verified: {r.stdout}")

if __name__ == "__main__":
    check_deps()

    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        if len(sys.argv) < 3:
            print("Usage: deploy.py verify <contract_address>")
            sys.exit(1)
        verify(sys.argv[2])
    else:
        deploy()
