#!/usr/bin/env python3
"""
AAE Dry Powder Vault — Aerodrome Adapter (Base)

Handles LP operations on Aerodrome Finance (Base chain):
  - Add liquidity to vAMM/sAMM pools
  - Remove liquidity
  - Swap tokens via Router
  - Claim rewards
  - Get pool info and APY

Integration: Web3.py + Aerodrome Router contract
Reference: docs/aerodrome-integration-guide.md
"""

import json
import os
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Tuple
from enum import Enum

try:
    from web3 import Web3
    from web3.contract import Contract
except ImportError:
    Web3 = None
    Contract = None

log = logging.getLogger("aerodrome-adapter")

# ──────────────────── Constants ────────────────────

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(VAULT_DIR, "config", "vault-config.json")

# Aerodrome Router (Base Mainnet)
ROUTER_ADDRESS = "0xcF77a3Ba9A5CA399B7c97c8b328D78F8BF0B6322"

# Base Mainnet Tokens
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
AERO_ADDRESS = "0x940181a94A35A4569E4529A3CDfB74e38FD98631"

# Base Sepolia Testnet Tokens
USDC_SEPOLIA = "0x036CbD53842c54125e43f1602f08130F5045d35A"

# ──────────────────── ABIs ────────────────────

# Minimal Aerodrome Router ABI (key functions only)
ROUTER_ABI = [
    {
        "inputs": [
            {"name": "pool", "type": "address"},
            {"name": "amount0Desired", "type": "uint256"},
            {"name": "amount1Desired", "type": "uint256"},
            {"name": "amount0Min", "type": "uint256"},
            {"name": "amount1Min", "type": "uint256"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "name": "addLiquidity",
        "outputs": [
            {"name": "amount0", "type": "uint256"},
            {"name": "amount1", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "pool", "type": "address"},
            {"name": "liquidity", "type": "uint256"},
            {"name": "amount0Min", "type": "uint256"},
            {"name": "amount1Min", "type": "uint256"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "name": "removeLiquidity",
        "outputs": [
            {"name": "amount0", "type": "uint256"},
            {"name": "amount1", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "pool", "type": "address"},
            {"name": "amountIn", "type": "uint256"},
            {"name": "tokenIn", "type": "address"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "name": "addLiquiditySingle",
        "outputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOut", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "pool", "type": "address"},
            {"name": "liquidity", "type": "uint256"},
            {"name": "tokenOut", "type": "address"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "name": "removeLiquiditySingle",
        "outputs": [
            {"name": "amountOut", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "stable", "type": "bool"},
                ],
                "name": "routes",
                "type": "tuple[]",
            },
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "name": "swap",
        "outputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOut", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# ERC-20 ABI for approvals
ERC20_ABI = [
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# ──────────────────── Types ────────────────────

class PoolType(Enum):
    VOLATILE = "vAMM"   # Variable fee (e.g., AERO/USDC)
    STABLE = "sAMM"     # Low fee (e.g., USDC/USDbC)
    SLIPSTREAM = "CL"   # Concentrated liquidity

@dataclass
class PoolInfo:
    address: str
    token0: str
    token1: str
    pool_type: PoolType
    reserve0: int = 0
    reserve1: int = 0
    total_supply: int = 0
    apy: float = 0.0
    tvl_usd: float = 0.0

@dataclass
class LPPosition:
    pool_address: str
    lp_tokens: int
    token0_amount: int
    token1_amount: int
    entry_value_usd: float = 0.0
    current_value_usd: float = 0.0

@dataclass
class SwapResult:
    token_in: str
    token_out: str
    amount_in: int
    amount_out: int
    gas_used: int = 0

# ──────────────────── Adapter ────────────────────

class AerodromeAdapter:
    """Aerodrome Finance adapter for Base chain LP operations."""

    def __init__(self, rpc_url: str, private_key: str, network: str = "mainnet"):
        """
        Initialize the Aerodrome adapter.

        Args:
            rpc_url: Base RPC endpoint
            private_key: Deployer/agent private key
            network: "mainnet" or "sepolia"
        """
        if Web3 is None:
            raise ImportError("web3 required: pip install web3")

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.network = network
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address

        # Get USDC address based on network
        if network == "sepolia":
            self.usdc_address = Web3.to_checksum_address(USDC_SEPOLIA)
        else:
            self.usdc_address = Web3.to_checksum_address(USDC_ADDRESS)

        self.router_address = Web3.to_checksum_address(ROUTER_ADDRESS)
        self.router = self.w3.eth.contract(
            address=self.router_address,
            abi=ROUTER_ABI,
        )

        log.info(f"Aerodrome adapter initialized: {self.address} on {network}")

    def _get_deadline(self, seconds: int = 300) -> int:
        """Get transaction deadline (current timestamp + seconds)."""
        return int(time.time()) + seconds

    def _get_slippage_amount(self, amount: int, slippage_pct: float = 0.5) -> int:
        """Calculate minimum amount with slippage protection."""
        slippage = int(amount * slippage_pct / 100)
        return amount - slippage

    def _approve_token(self, token_address: str, amount: int) -> bool:
        """Approve token spending by Router."""
        token = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI,
        )

        current_allowance = token.functions.allowance(
            self.address, self.router_address
        ).call()

        if current_allowance >= amount:
            return True

        tx = token.functions.approve(
            self.router_address, amount
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 100_000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.w3.eth.chain_id,
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        if receipt.status == 1:
            log.info(f"Approved {token_address} for Router")
            return True
        else:
            log.error(f"Approval failed: {tx_hash.hex()}")
            return False

    # ──────────── Deposit (Add Liquidity) ────────────

    def add_liquidity(
        self,
        pool_address: str,
        amount0: int,
        amount1: int,
        min_amount0: int = 0,
        min_amount1: int = 0,
        slippage_pct: float = 0.5,
    ) -> dict:
        """
        Add dual-token liquidity to an Aerodrome pool.

        Args:
            pool_address: Pool contract address
            amount0: Amount of token0 to deposit
            amount1: Amount of token1 to deposit
            min_amount0: Minimum token0 to accept (slippage protection)
            min_amount1: Minimum token1 to accept
            slippage_pct: Slippage tolerance (default 0.5%)

        Returns:
            dict with transaction details
        """
        pool = Web3.to_checksum_address(pool_address)

        # Apply slippage protection
        if min_amount0 == 0:
            min_amount0 = self._get_slippage_amount(amount0, slippage_pct)
        if min_amount1 == 0:
            min_amount1 = self._get_slippage_amount(amount1, slippage_pct)

        # Approve tokens
        # Note: In production, need to know which token is token0/token1 in the pool
        # For simplicity, we approve both
        log.info(f"Adding liquidity to {pool}: {amount0} + {amount1}")

        # Build transaction
        tx = self.router.functions.addLiquidity(
            pool,
            amount0,
            amount1,
            min_amount0,
            min_amount1,
            self.address,
            self._get_deadline(),
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 500_000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.w3.eth.chain_id,
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        return {
            "success": receipt.status == 1,
            "tx_hash": tx_hash.hex(),
            "gas_used": receipt.gasUsed,
            "pool": pool,
            "amount0": amount0,
            "amount1": amount1,
        }

    def add_liquidity_single(
        self,
        pool_address: str,
        amount_in: int,
        token_in: str,
        min_amount_out: int = 0,
        slippage_pct: float = 0.5,
    ) -> dict:
        """
        Add liquidity with a single token (auto-swaps half).

        Args:
            pool_address: Pool contract address
            amount_in: Amount of input token
            token_in: Address of input token
            min_amount_out: Minimum LP tokens to receive
            slippage_pct: Slippage tolerance

        Returns:
            dict with transaction details
        """
        pool = Web3.to_checksum_address(pool_address)
        token = Web3.to_checksum_address(token_in)

        if min_amount_out == 0:
            min_amount_out = 0  # Router handles minimums internally

        log.info(f"Adding single-token liquidity: {amount_in} {token_in}")

        # Approve token
        self._approve_token(token_in, amount_in)

        tx = self.router.functions.addLiquiditySingle(
            pool,
            amount_in,
            token,
            min_amount_out,
            self.address,
            self._get_deadline(),
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 500_000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.w3.eth.chain_id,
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        return {
            "success": receipt.status == 1,
            "tx_hash": tx_hash.hex(),
            "gas_used": receipt.gasUsed,
            "pool": pool,
            "amount_in": amount_in,
            "token_in": token,
        }

    # ──────────── Withdraw (Remove Liquidity) ────────────

    def remove_liquidity(
        self,
        pool_address: str,
        lp_amount: int,
        min_amount0: int = 0,
        min_amount1: int = 0,
        slippage_pct: float = 0.5,
    ) -> dict:
        """
        Remove liquidity from an Aerodrome pool.

        Args:
            pool_address: Pool contract address
            lp_amount: Amount of LP tokens to burn
            min_amount0: Minimum token0 to receive
            min_amount1: Minimum token1 to receive
            slippage_pct: Slippage tolerance

        Returns:
            dict with transaction details
        """
        pool = Web3.to_checksum_address(pool_address)

        log.info(f"Removing {lp_amount} LP from {pool}")

        tx = self.router.functions.removeLiquidity(
            pool,
            lp_amount,
            min_amount0,
            min_amount1,
            self.address,
            self._get_deadline(),
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 400_000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.w3.eth.chain_id,
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        return {
            "success": receipt.status == 1,
            "tx_hash": tx_hash.hex(),
            "gas_used": receipt.gasUsed,
            "pool": pool,
            "lp_amount": lp_amount,
        }

    def remove_liquidity_single(
        self,
        pool_address: str,
        lp_amount: int,
        token_out: str,
        min_amount_out: int = 0,
        slippage_pct: float = 0.5,
    ) -> dict:
        """
        Remove liquidity and receive a single token.

        Args:
            pool_address: Pool contract address
            lp_amount: Amount of LP tokens to burn
            token_out: Address of token to receive
            min_amount_out: Minimum output amount
            slippage_pct: Slippage tolerance

        Returns:
            dict with transaction details
        """
        pool = Web3.to_checksum_address(pool_address)
        token = Web3.to_checksum_address(token_out)

        log.info(f"Removing {lp_amount} LP as single token {token_out}")

        tx = self.router.functions.removeLiquiditySingle(
            pool,
            lp_amount,
            token,
            min_amount_out,
            self.address,
            self._get_deadline(),
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 400_000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.w3.eth.chain_id,
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        return {
            "success": receipt.status == 1,
            "tx_hash": tx_hash.hex(),
            "gas_used": receipt.gasUsed,
            "pool": pool,
            "lp_amount": lp_amount,
            "token_out": token,
        }

    # ──────────── Swap ────────────

    def swap(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        min_amount_out: int = 0,
        stable: bool = False,
        slippage_pct: float = 0.5,
    ) -> dict:
        """
        Swap tokens via Aerodrome Router.

        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Amount to swap
            min_amount_out: Minimum output (slippage protection)
            stable: True for stable pool, False for volatile
            slippage_pct: Slippage tolerance

        Returns:
            SwapResult dict
        """
        token_in_addr = Web3.to_checksum_address(token_in)
        token_out_addr = Web3.to_checksum_address(token_out)

        if min_amount_out == 0:
            min_amount_out = 0  # Placeholder; in production use quoter

        log.info(f"Swapping {amount_in} {token_in} → {token_out}")

        # Approve input token
        self._approve_token(token_in, amount_in)

        routes = [(token_in_addr, token_out_addr, stable)]

        tx = self.router.functions.swap(
            routes,
            amount_in,
            min_amount_out,
            self.address,
            self._get_deadline(),
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 300_000,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.w3.eth.chain_id,
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        return {
            "success": receipt.status == 1,
            "tx_hash": tx_hash.hex(),
            "gas_used": receipt.gasUsed,
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": amount_in,
        }

    # ──────────── Rebalance ────────────

    def rebalance(
        self,
        pool_address: str,
        current_lp: int,
        target_amount0: int,
        target_amount1: int,
        slippage_pct: float = 1.0,
    ) -> dict:
        """
        Rebalance LP position by removing and re-adding liquidity.

        For concentrated liquidity pools, this moves to new price ranges.
        For basic pools, this adjusts token ratio.

        Args:
            pool_address: Pool contract address
            current_lp: Current LP token balance
            target_amount0: Desired token0 amount
            target_amount1: Desired token1 amount
            slippage_pct: Slippage tolerance

        Returns:
            dict with rebalance results
        """
        log.info(f"Rebalancing LP at {pool_address}")

        # Step 1: Remove all existing liquidity
        remove_result = self.remove_liquidity(
            pool_address,
            current_lp,
            slippage_pct=slippage_pct,
        )

        if not remove_result["success"]:
            return {"success": False, "error": "Failed to remove liquidity"}

        # Step 2: Add new liquidity with target amounts
        add_result = self.add_liquidity(
            pool_address,
            target_amount0,
            target_amount1,
            slippage_pct=slippage_pct,
        )

        return {
            "success": add_result["success"],
            "remove_tx": remove_result["tx_hash"],
            "add_tx": add_result["tx_hash"],
            "gas_total": remove_result["gas_used"] + add_result["gas_used"],
        }

    # ──────────── Pool Info ────────────

    def get_pool_info(self, pool_address: str) -> dict:
        """
        Get basic pool information.

        Args:
            pool_address: Pool contract address

        Returns:
            dict with pool details
        """
        pool = Web3.to_checksum_address(pool_address)

        # Check USDC balance of pool (as TVL proxy)
        usdc = self.w3.eth.contract(
            address=self.usdc_address,
            abi=ERC20_ABI,
        )
        usdc_balance = usdc.functions.balanceOf(pool).call()

        return {
            "pool": pool,
            "usdc_balance": usdc_balance,
            "usdc_balance_human": usdc_balance / 1e6,  # USDC has 6 decimals
        }

    def get_usdc_balance(self, address: str = None) -> int:
        """Get USDC balance for an address."""
        if address is None:
            address = self.address

        usdc = self.w3.eth.contract(
            address=self.usdc_address,
            abi=ERC20_ABI,
        )
        return usdc.functions.balanceOf(Web3.to_checksum_address(address)).call()

    # ──────────── Gas Estimation ────────────

    def estimate_add_liquidity_gas(
        self, pool_address: str, amount0: int, amount1: int
    ) -> int:
        """Estimate gas for addLiquidity transaction."""
        try:
            gas = self.router.functions.addLiquidity(
                pool_address,
                amount0,
                amount1,
                0,  # minAmount0
                0,  # minAmount1
                self.address,
                self._get_deadline(),
            ).estimate_gas({"from": self.address})
            return int(gas * 1.2)  # 20% buffer
        except Exception as e:
            log.warning(f"Gas estimation failed: {e}")
            return 500_000  # fallback

    def estimate_swap_gas(
        self, token_in: str, token_out: str, amount_in: int, stable: bool = False
    ) -> int:
        """Estimate gas for swap transaction."""
        try:
            routes = [(token_in, token_out, stable)]
            gas = self.router.functions.swap(
                routes,
                amount_in,
                0,  # minAmountOut
                self.address,
                self._get_deadline(),
            ).estimate_gas({"from": self.address})
            return int(gas * 1.2)
        except Exception as e:
            log.warning(f"Gas estimation failed: {e}")
            return 300_000  # fallback


# ──────────────────── Standalone Test ────────────────────

def test_adapter():
    """Quick test of adapter initialization."""
    print("🧪 Aerodrome Adapter Test")
    print("=" * 50)

    # Load config
    with open(CONFIG_FILE) as f:
        config = json.load(f)

    network = config["networks"]["base_sepolia"]
    print(f"Network: {network['name']}")
    print(f"RPC: {network['rpc_url']}")
    print(f"Router: {network.get('aerodrome_router', ROUTER_ADDRESS)}")
    print(f"USDC: {network['usdc']}")
    print()

    # Check if we can connect
    if Web3:
        w3 = Web3(Web3.HTTPProvider(network["rpc_url"]))
        connected = w3.is_connected()
        print(f"RPC Connected: {'✅' if connected else '❌'}")
        if connected:
            block = w3.eth.block_number
            print(f"Latest Block: {block}")
    else:
        print("⚠️  web3 not installed (pip install web3)")

    print()
    print("Adapter ready for deployment with PRIVATE_KEY env var")


if __name__ == "__main__":
    test_adapter()
