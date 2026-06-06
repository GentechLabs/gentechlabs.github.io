#!/usr/bin/env python3
"""
Deploy DryPowderVault to Base Sepolia testnet.

Prerequisites:
  pip install web3 py-solc-x
  Set PRIVATE_KEY env var with deployer wallet key

Usage:
  python3 deploy_vault.py
"""

import json
import os
import sys

try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
except ImportError:
    print("ERROR: pip install web3 py-solc-x")
    sys.exit(1)

# ──────────────────── Config ────────────────────

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(VAULT_DIR, "config", "vault-config.json")

with open(CONFIG_FILE) as f:
    CONFIG = json.load(f)

NETWORK = CONFIG["networks"]["base_sepolia"]
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")

if not PRIVATE_KEY:
    print("ERROR: Set PRIVATE_KEY environment variable")
    sys.exit(1)

# ──────────────────── Compile ────────────────────

def compile_contracts():
    """Compile Solidity contracts using solcx."""
    try:
        import solcx
        solcx.install_solc("0.8.20")
    except Exception as e:
        print(f"WARNING: solcx not available ({e}), using pre-compiled ABIs")
        return load_precompiled()

    contract_files = {
        "DryPowderVault": os.path.join(VAULT_DIR, "contracts", "DryPowderVault.sol"),
        "CCTPBridgeAdapter": os.path.join(VAULT_DIR, "contracts", "CCTPBridgeAdapter.sol"),
    }

    compiled = {}
    for name, path in contract_files.items():
        with open(path) as f:
            source = f.read()

        compiled[name] = solcx.compile_standard(
            {
                "language": "Solidity",
                "sources": {f"{name}.sol": {"content": source}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "bin"]}
                    }
                },
            },
            solc_version="0.8.20",
        )

    return compiled

def load_precompiled():
    """Load pre-compiled ABIs if available."""
    abis_dir = os.path.join(VAULT_DIR, "abis")
    if os.path.exists(abis_dir):
        compiled = {}
        for f in os.listdir(abis_dir):
            if f.endswith(".json"):
                name = f.replace(".json", "")
                with open(os.path.join(abis_dir, f)) as fh:
                    compiled[name] = json.load(fh)
        return compiled
    return {}

# ──────────────────── Deploy ────────────────────

def deploy():
    w3 = Web3(Web3.HTTPProvider(NETWORK["rpc_url"]))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Deployer: {account.address}")
    print(f"Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} ETH")
    print(f"Network: {NETWORK['name']} (chain {NETWORK['chain_id']})")
    print()

    usdc_address = w3.to_checksum_address(NETWORK["usdc"])

    # Compile or load ABIs
    compiled = compile_contracts()

    # Deploy DryPowderVault
    print("📦 Deploying DryPowderVault...")
    vault_abi = compiled.get("DryPowderVault", {}).get("contracts", {}).get("DryPowderVault.sol", {}).get("DryPowderVault", {}).get("abi")
    vault_bin = compiled.get("DryPowderVault", {}).get("contracts", {}).get("DryPowderVault.sol", {}).get("DryPowderVault", {}).get("bin")

    if not vault_abi or not vault_bin:
        print("ERROR: Could not compile DryPowderVault. Check Solidity compiler.")
        sys.exit(1)

    VaultContract = w3.eth.contract(abi=vault_abi, bytecode=f"0x{vault_bin}")

    tx = VaultContract.constructor(usdc_address).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 3_000_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": NETWORK["chain_id"],
    })

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"  TX: {NETWORK['explorer']}/tx/{tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    vault_address = receipt.contractAddress
    print(f"  ✅ Deployed: {vault_address}")
    print(f"  Gas used: {receipt.gasUsed}")

    # Deploy CCTPBridgeAdapter
    print("\n📦 Deploying CCTPBridgeAdapter...")
    cctp_abi = compiled.get("CCTPBridgeAdapter", {}).get("contracts", {}).get("CCTPBridgeAdapter.sol", {}).get("CCTPBridgeAdapter", {}).get("abi")
    cctp_bin = compiled.get("CCTPBridgeAdapter", {}).get("contracts", {}).get("CCTPBridgeAdapter.sol", {}).get("CCTPBridgeAdapter", {}).get("bin")

    if not cctp_abi or not cctp_bin:
        print("WARNING: Could not compile CCTPBridgeAdapter, skipping")
    else:
        CctpContract = w3.eth.contract(abi=cctp_abi, bytecode=f"0x{cctp_bin}")

        tx = CctpContract.constructor(usdc_address).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 2_000_000,
            "gasPrice": w3.eth.gas_price,
            "chainId": NETWORK["chain_id"],
        })

        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"  TX: {NETWORK['explorer']}/tx/{tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        cctp_address = receipt.contractAddress
        print(f"  ✅ Deployed: {cctp_address}")

        # Configure CCTP domains
        print("\n🔧 Configuring CCTP domains...")
        cctp_contract = w3.eth.contract(address=cctp_address, abi=cctp_abi)

        # Base (self)
        base_domain = w3.to_checksum_address(NETWORK["cctp_token_messenger"])
        base_transmitter = w3.to_checksum_address(NETWORK["cctp_message_transmitter"])
        tx = cctp_contract.functions.configureDomain(
            NETWORK["chain_id"], 6, base_domain, base_transmitter
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 100_000,
            "gasPrice": w3.eth.gas_price,
            "chainId": NETWORK["chain_id"],
        })
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print("  ✅ Base domain configured")

        # Save deployment info
        deployment = {
            "network": "base_sepolia",
            "vault_address": vault_address,
            "cctp_adapter_address": cctp_address,
            "usdc": usdc_address,
            "deployer": account.address,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }

        deploy_file = os.path.join(VAULT_DIR, "deployments", "base-sepolia.json")
        os.makedirs(os.path.dirname(deploy_file), exist_ok=True)
        with open(deploy_file, "w") as f:
            json.dump(deployment, f, indent=2)

        print(f"\n📋 Deployment saved to: {deploy_file}")
        print(f"\n🎉 Deployment complete!")
        print(f"  Vault: {vault_address}")
        print(f"  CCTP Adapter: {cctp_address}")

if __name__ == "__main__":
    deploy()
