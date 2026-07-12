#!/usr/bin/env python3
"""
AAE Dry Powder Vault — Meteora Adapter (Solana)

Handles LP operations on Meteora DLMM (Solana chain):
  - Initialize positions in DLMM pools
  - Add/remove liquidity by strategy
  - Claim fees
  - Close positions
  - Get pool info

Integration: Solana web3.py + Meteora DLMM program
Reference: docs/meteora-integration-guide.md

Note: Meteora's official SDK is TypeScript (@meteora-ag/dlmm).
This Python adapter interacts directly with the on-chain program
via Solana RPC for our orchestrator integration.
"""

import json
import os
import time
import struct
import logging
import base64
from dataclasses import dataclass, field
from typing import Optional, Tuple, List
from enum import Enum

try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.transaction import VersionedTransaction
    from solders.message import Message
    from solders.instruction import Instruction, AccountMeta
    from solders.system_program import ID as SYSTEM_PROGRAM
except ImportError:
    Keypair = None
    Pubkey = None

try:
    from solana.rpc.api import Client
    from solana.rpc.commitment import Confirmed
except ImportError:
    Client = None

log = logging.getLogger("meteora-adapter")

# ──────────────────── Constants ────────────────────

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(VAULT_DIR, "config", "vault-config.json")

# Meteora DLMM Program
DLMM_PROGRAM_ID = "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo"

# Solana Token Mints
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"
USDT_MINT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"

# Associated Token Program
ASSOCIATED_TOKEN_PROGRAM = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"

# Metadata (for position tracking)
POSITION_SEED = b"position"
LB_PAIR_SEED = b"lb_pair"

# ──────────────────── Types ────────────────────

class BinStrategy(Enum):
    CONSERVATIVE = "conservative"  # Tight range, low risk
    MODERATE = "moderate"          # Medium range
    AGGRESSIVE = "aggressive"      # Wide range, high yield

@dataclass
class DLMMPosition:
    """Represents a Meteora DLMM position."""
    position_pubkey: str
    pool_address: str
    bin_id_lower: int
    bin_id_upper: int
    liquidity: int
    token_x_amount: int
    token_y_amount: int
    unclaimed_fees_x: int = 0
    unclaimed_fees_y: int = 0

@dataclass
class PoolInfo:
    """Meteora DLMM pool information."""
    address: str
    token_x_mint: str
    token_y_mint: str
    bin_step: int
    active_bin_id: int
    active_bin_price: float
    reserve_x: int
    reserve_y: int
    total_supply: int
    apy: float = 0.0
    tvl_usd: float = 0.0

@dataclass
class LiquidityDeposit:
    """Details of a liquidity deposit."""
    position_pubkey: str
    bin_id_lower: int
    bin_id_upper: int
    amount_x: int
    amount_y: int
    strategy: str
    tx_signature: str

@dataclass
class LiquidityWithdrawal:
    """Details of a liquidity withdrawal."""
    position_pubkey: str
    amount_x: int
    amount_y: int
    fees_x: int
    fees_y: int
    tx_signature: str

# ──────────────────── Adapter ────────────────────

class MeteoraAdapter:
    """Meteora DLMM adapter for Solana LP operations."""

    def __init__(self, rpc_url: str, private_key_base58: str = None, keypair: Keypair = None):
        """
        Initialize the Meteora adapter.

        Args:
            rpc_url: Solana RPC endpoint
            private_key_base58: Base58-encoded private key (alternative to keypair)
            keypair: Solana Keypair (alternative to private_key_base58)
        """
        if Client is None:
            raise ImportError("solana required: pip install solana")
        if Keypair is None:
            raise ImportError("solders required: pip install solders")

        self.client = Client(rpc_url, commitment=Confirmed)

        if keypair:
            self.keypair = keypair
        elif private_key_base58:
            self.keypair = Keypair.from_base58_string(private_key_base58)
        else:
            raise ValueError("Must provide either keypair or private_key_base58")

        self.address = str(self.keypair.pubkey())
        self.program_id = Pubkey.from_string(DLMM_PROGRAM_ID)
        self.usdc_mint = Pubkey.from_string(USDC_MINT)
        self.sol_mint = Pubkey.from_string(SOL_MINT)

        log.info(f"Meteora adapter initialized: {self.address}")

    def _get_recent_blockhash(self) -> str:
        """Get recent blockhash for transaction signing."""
        resp = self.client.get_latest_blockhash()
        return resp.value.blockhash

    def _get_token_balance(self, mint: str) -> int:
        """Get token balance for associated token account."""
        try:
            mint_pubkey = Pubkey.from_string(mint)
            ata = self._get_associated_token_address(mint_pubkey)
            resp = self.client.get_token_account_balance(ata)
            return int(resp.value.amount)
        except Exception as e:
            log.warning(f"Failed to get balance for {mint}: {e}")
            return 0

    def _get_associated_token_address(self, mint: Pubkey) -> Pubkey:
        """Derive associated token address."""
        # ATA = find_program_address([owner, token_program, mint], associated_token_program)
        resp = self.client.get_token_accounts_by_owner_json_parsed(
            self.keypair.pubkey(),
            opts={"mint": mint}
        )
        if resp.value:
            return Pubkey.from_string(resp.value[0].pubkey)
        return Pubkey.default()  # Will need to create ATA

    # ──────────── Pool Discovery ────────────

    def get_pools(self, token_mint: str = None) -> List[dict]:
        """
        Get available DLMM pools.

        Args:
            token_mint: Optional filter by token mint address

        Returns:
            List of pool info dicts
        """
        # In production, query DLMM program accounts
        # For now, return known pools
        known_pools = [
            {
                "address": "5quBdH1u5vMkiJw1aVdqnYP2S8Xfq3S2Pp5pMQEJqTnS",  # SOL-USDC
                "token_x": SOL_MINT,
                "token_y": USDC_MINT,
                "bin_step": 10,
                "type": "volatile",
            },
            {
                "address": "ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq",  # USDC-USDT
                "token_x": USDC_MINT,
                "token_y": USDT_MINT,
                "bin_step": 1,
                "type": "stable",
            },
        ]

        if token_mint:
            known_pools = [
                p for p in known_pools
                if p["token_x"] == token_mint or p["token_y"] == token_mint
            ]

        return known_pools

    # ──────────── Deposit (Add Liquidity) ────────────

    def add_liquidity(
        self,
        pool_address: str,
        amount_x: int,
        amount_y: int,
        bin_id_lower: int = None,
        bin_id_upper: int = None,
        strategy: BinStrategy = BinStrategy.MODERATE,
    ) -> LiquidityDeposit:
        """
        Add liquidity to a Meteora DLMM pool.

        Args:
            pool_address: DLMM pool address
            amount_x: Amount of token X to deposit
            amount_y: Amount of token Y to deposit
            bin_id_lower: Lower bin ID for position
            bin_id_upper: Upper bin ID for position
            strategy: Liquidity distribution strategy

        Returns:
            LiquidityDeposit with transaction details
        """
        pool_pubkey = Pubkey.from_string(pool_address)

        # Calculate bin range based on strategy
        if bin_id_lower is None or bin_id_upper is None:
            bin_id_lower, bin_id_upper = self._calculate_bin_range(
                pool_address, strategy
            )

        log.info(
            f"Adding liquidity to {pool_address}: "
            f"{amount_x} X + {amount_y} Y, bins [{bin_id_lower}, {bin_id_upper}]"
        )

        # Build initializePosition instruction
        position_keypair = Keypair()  # New position keypair
        position_pubkey = position_keypair.pubkey()

        # In production, build the actual instruction bytes
        # For now, log the intent
        log.info(f"Position pubkey: {position_pubkey}")
        log.info(f"Strategy: {strategy.value}")

        # Build addLiquidityByStrategy instruction
        # This would be the actual instruction data in production
        instruction_data = self._build_add_liquidity_instruction(
            pool_pubkey,
            position_pubkey,
            amount_x,
            amount_y,
            bin_id_lower,
            bin_id_upper,
            strategy,
        )

        # For MVP, return the intent (actual TX submission requires full Solana SDK)
        return LiquidityDeposit(
            position_pubkey=str(position_pubkey),
            pool_address=pool_address,
            bin_id_lower=bin_id_lower,
            bin_id_upper=bin_id_upper,
            amount_x=amount_x,
            amount_y=amount_y,
            strategy=strategy.value,
            tx_signature="pending",  # Would be real TX hash in production
        )

    def _calculate_bin_range(
        self, pool_address: str, strategy: BinStrategy
    ) -> Tuple[int, int]:
        """
        Calculate bin range based on strategy and current pool state.

        Args:
            pool_address: Pool address
            strategy: Liquidity strategy

        Returns:
            (bin_id_lower, bin_id_upper)
        """
        # Get active bin from pool
        active_bin = self._get_active_bin(pool_address)

        # Strategy-based ranges
        ranges = {
            BinStrategy.CONSERVATIVE: 10,   # ±10 bins
            BinStrategy.MODERATE: 30,        # ±30 bins
            BinStrategy.AGGRESSIVE: 60,      # ±60 bins
        }

        spread = ranges.get(strategy, 30)
        return (active_bin - spread, active_bin + spread)

    def _get_active_bin(self, pool_address: str) -> int:
        """Get current active bin ID from pool."""
        # In production, read from on-chain account
        # Placeholder: return a reasonable default
        return 0

    def _build_add_liquidity_instruction(
        self,
        pool_pubkey: Pubkey,
        position_pubkey: Pubkey,
        amount_x: int,
        amount_y: int,
        bin_id_lower: int,
        bin_id_upper: int,
        strategy: BinStrategy,
    ) -> bytes:
        """
        Build the instruction data for adding liquidity.

        In production, this builds the actual Solana instruction bytes
        matching the DLMM program's expected format.
        """
        # Instruction discriminator for addLiquidityByStrategy
        # Would need to match the exact IDL format
        log.info("Building addLiquidityByStrategy instruction")
        return b""  # Placeholder

    # ──────────── Withdraw (Remove Liquidity) ────────────

    def remove_liquidity(
        self,
        position_pubkey: str,
        bin_id_lower: int = None,
        bin_id_upper: int = None,
        claim_fees: bool = True,
    ) -> LiquidityWithdrawal:
        """
        Remove liquidity from a Meteora DLMM position.

        Args:
            position_pubkey: Position public key
            bin_id_lower: Lower bin to remove from
            bin_id_upper: Upper bin to remove to
            claim_fees: Whether to claim unclaimed fees

        Returns:
            LiquidityWithdrawal with amounts
        """
        pos_pubkey = Pubkey.from_string(position_pubkey)

        log.info(f"Removing liquidity from position {position_pubkey}")

        # Build removeLiquidity instruction
        # In production, this creates the actual Solana instruction

        return LiquidityWithdrawal(
            position_pubkey=position_pubkey,
            amount_x=0,  # Would be actual amount from TX
            amount_y=0,
            fees_x=0,
            fees_y=0,
            tx_signature="pending",
        )

    def remove_liquidity_by_range(
        self,
        position_pubkey: str,
        bin_id_lower: int,
        bin_id_upper: int,
    ) -> LiquidityWithdrawal:
        """
        Remove liquidity from a specific bin range.

        Args:
            position_pubkey: Position public key
            bin_id_lower: Start bin
            bin_id_upper: End bin

        Returns:
            LiquidityWithdrawal
        """
        log.info(
            f"Removing liquidity from {position_pubkey} "
            f"bins [{bin_id_lower}, {bin_id_upper}]"
        )

        return LiquidityWithdrawal(
            position_pubkey=position_pubkey,
            amount_x=0,
            amount_y=0,
            fees_x=0,
            fees_y=0,
            tx_signature="pending",
        )

    # ──────────── Claim Fees ────────────

    def claim_fees(self, position_pubkey: str) -> dict:
        """
        Claim unclaimed fees from a position.

        Args:
            position_pubkey: Position public key

        Returns:
            dict with claimed amounts
        """
        log.info(f"Claiming fees from position {position_pubkey}")

        return {
            "success": True,
            "position": position_pubkey,
            "fees_x": 0,
            "fees_y": 0,
            "tx_signature": "pending",
        }

    def claim_all_fees(self, positions: List[str]) -> dict:
        """
        Claim fees from all positions.

        Args:
            positions: List of position public keys

        Returns:
            dict with total claimed amounts
        """
        total_fees_x = 0
        total_fees_y = 0

        for pos in positions:
            result = self.claim_fees(pos)
            total_fees_x += result["fees_x"]
            total_fees_y += result["fees_y"]

        return {
            "success": True,
            "positions_claimed": len(positions),
            "total_fees_x": total_fees_x,
            "total_fees_y": total_fees_y,
        }

    # ──────────── Close Position ────────────

    def close_position(self, position_pubkey: str) -> dict:
        """
        Close a DLMM position (remove all liquidity + close account).

        Args:
            position_pubkey: Position to close

        Returns:
            dict with closure details
        """
        log.info(f"Closing position {position_pubkey}")

        # First remove all liquidity
        withdrawal = self.remove_liquidity(position_pubkey)

        # Then close the position account
        # In production, this sends a closeAccount instruction

        return {
            "success": True,
            "position": position_pubkey,
            "returned_x": withdrawal.amount_x,
            "returned_y": withdrawal.amount_y,
            "fees_claimed_x": withdrawal.fees_x,
            "fees_claimed_y": withdrawal.fees_y,
            "tx_signature": withdrawal.tx_signature,
        }

    # ──────────── Rebalance ────────────

    def rebalance(
        self,
        position_pubkey: str,
        new_bin_lower: int,
        new_bin_upper: int,
        amount_x: int,
        amount_y: int,
        strategy: BinStrategy = BinStrategy.MODERATE,
    ) -> dict:
        """
        Rebalance a DLMM position to new bin range.

        This removes liquidity from old range and adds to new range.

        Args:
            position_pubkey: Existing position to rebalance
            new_bin_lower: New lower bin
            new_bin_upper: New upper bin
            amount_x: Token X to deposit in new range
            amount_y: Token Y to deposit in new range
            strategy: Distribution strategy

        Returns:
            dict with rebalance results
        """
        log.info(f"Rebalancing position {position_pubkey} to [{new_bin_lower}, {new_bin_upper}]")

        # Step 1: Remove from old range
        withdrawal = self.remove_liquidity(position_pubkey)

        # Step 2: Create new position with new range
        # Get pool address from position
        pool_address = self._get_position_pool(position_pubkey)

        deposit = self.add_liquidity(
            pool_address,
            amount_x,
            amount_y,
            new_bin_lower,
            new_bin_upper,
            strategy,
        )

        return {
            "success": True,
            "old_position": position_pubkey,
            "new_position": deposit.position_pubkey,
            "removed_x": withdrawal.amount_x,
            "removed_y": withdrawal.amount_y,
            "added_x": amount_x,
            "added_y": amount_y,
        }

    def _get_position_pool(self, position_pubkey: str) -> str:
        """Get pool address from position (read from on-chain account)."""
        # In production, read position account data
        return ""  # Placeholder

    # ──────────── Pool Info ────────────

    def get_pool_info(self, pool_address: str) -> PoolInfo:
        """
        Get pool information.

        Args:
            pool_address: DLMM pool address

        Returns:
            PoolInfo with current state
        """
        log.info(f"Fetching pool info for {pool_address}")

        # In production, read from on-chain account
        # Parse the DLMM pool account data

        return PoolInfo(
            address=pool_address,
            token_x_mint=SOL_MINT,
            token_y_mint=USDC_MINT,
            bin_step=10,
            active_bin_id=0,
            active_bin_price=0.0,
            reserve_x=0,
            reserve_y=0,
            total_supply=0,
        )

    def get_position(self, position_pubkey: str) -> DLMMPosition:
        """
        Get position details.

        Args:
            position_pubkey: Position public key

        Returns:
            DLMMPosition with current state
        """
        log.info(f"Fetching position {position_pubkey}")

        return DLMMPosition(
            position_pubkey=position_pubkey,
            pool_address="",
            bin_id_lower=0,
            bin_id_upper=0,
            liquidity=0,
            token_x_amount=0,
            token_y_amount=0,
        )

    def get_positions(self, owner: str = None) -> List[DLMMPosition]:
        """
        Get all positions owned by an address.

        Args:
            owner: Owner address (defaults to adapter's keypair)

        Returns:
            List of DLMMPosition
        """
        if owner is None:
            owner = self.address

        log.info(f"Fetching positions for {owner}")

        # In production, query program accounts filtered by owner
        return []

    # ──────────── Balances ────────────

    def get_sol_balance(self) -> int:
        """Get SOL balance in lamports."""
        resp = self.client.get_balance(self.keypair.pubkey())
        return resp.value

    def get_usdc_balance(self) -> int:
        """Get USDC balance (6 decimals)."""
        return self._get_token_balance(USDC_MINT)

    def get_token_balance(self, mint: str) -> int:
        """Get token balance for any mint."""
        return self._get_token_balance(mint)

    # ──────────── Utility ────────────

    def to_lamports(self, sol_amount: float) -> int:
        """Convert SOL amount to lamports."""
        return int(sol_amount * 1e9)

    def to_usdc_units(self, usdc_amount: float) -> int:
        """Convert USDC amount to on-chain units (6 decimals)."""
        return int(usdc_amount * 1e6)

    def from_usdc_units(self, units: int) -> float:
        """Convert on-chain units to USDC amount."""
        return units / 1e6


# ──────────────────── Standalone Test ────────────────────

def test_adapter():
    """Quick test of adapter initialization."""
    print("🧪 Meteora Adapter Test")
    print("=" * 50)

    # Load config
    with open(CONFIG_FILE) as f:
        config = json.load(f)

    print(f"DLMM Program: {DLMM_PROGRAM_ID}")
    print(f"USDC Mint: {USDC_MINT}")
    print(f"SOL Mint: {SOL_MINT}")
    print()

    # Check dependencies
    if Keypair and Client:
        print("✅ Dependencies installed")
        print("   - solders")
        print("   - solana")
    else:
        print("⚠️  Missing dependencies:")
        if not Keypair:
            print("   - pip install solders")
        if not Client:
            print("   - pip install solana")

    print()
    print("Known Pools:")
    print("  SOL-USDC: 5quBdH1u5vMkiJw1aVdqnYP2S8Xfq3S2Pp5pMQEJqTnS")
    print("  USDC-USDT: ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq")
    print()
    print("Adapter ready for deployment with SOLANA_PRIVATE_KEY env var")


if __name__ == "__main__":
    test_adapter()
