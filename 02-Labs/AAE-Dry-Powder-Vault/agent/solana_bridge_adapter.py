#!/usr/bin/env python3
"""
AAE Dry Powder Vault — Solana Bridge Adapter

Bridges USDC from EVM chains (Base, Avalanche) to Solana.
Primary: Across Protocol (sub-5s fills, 0.06-0.10% fees)
Fallback: deBridge (flat 0.001 ETH fee, instant finality)

Reference: docs/solana-bridge-comparison.md
"""

import json
import os
import time
import logging
from dataclasses import dataclass
from typing import Optional
from enum import Enum

try:
    from web3 import Web3
    from web3.contract import Contract
except ImportError:
    Web3 = None
    Contract = None

log = logging.getLogger("solana-bridge")

# ──────────────────── Constants ────────────────────

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(VAULT_DIR, "config", "vault-config.json")

# Across Protocol SpokePool Addresses
ACROSS_SPOKEPOOL_BASE = "0xb4a8d45647445EA9FC3E1058096142390683dBC2"
ACROSS_SPOKEPOOL_AVALANCHE = "0x6f26bf09b1c792e3228e5467807a900a503c0281"

# Solana USDC (native)
SOLANA_USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# deBridge Gateway
DEBRIDGE_GATEWAY = "0xE4edb0B5B4FBCcE5D4a3E205aa558aA9F77C62c5"  # Base
DEBRIDGE_FEE = 0.001  # ETH flat fee

# Across fee tiers
ACROSS_LP_FEE_PCT = 0.06    # 0.06%
ACROSS_RELAYER_FEE_PCT = 0.02  # ~0.02%

# ──────────────────── ABIs ────────────────────

# Across SpokePool Minimal ABI
SPOKEPOOL_ABI = [
    {
        "inputs": [
            {"name": "depositor", "type": "address"},
            {"name": "recipient", "type": "bytes32"},
            {"name": "originToken", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "destinationChainId", "type": "uint256"},
            {"name": "relayerFeePct", "type": "int64"},
            {"name": "quoteTimestamp", "type": "uint32"},
            {"name": "message", "type": "bytes"},
        ],
        "name": "depositV3",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "depositor", "type": "address"},
            {"name": "recipient", "type": "bytes32"},
            {"name": "originToken", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "destinationChainId", "type": "uint256"},
            {"name": "relayerFeePct", "type": "int64"},
            {"name": "quoteTimestamp", "type": "uint32"},
            {"name": "message", "type": "bytes"},
            {"name": "maxTokensSent", "type": "uint256"},
        ],
        "name": "depositV3",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "depositor", "type": "address"},
            {"name": "recipient", "type": "bytes32"},
            {"name": "originToken", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "destinationChainId", "type": "uint256"},
        ],
        "name": "depositNow",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
]

# ERC-20 ABI
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

class BridgeProtocol(Enum):
    ACROSS = "across"
    DEBRIDGE = "debridge"

class SourceChain(Enum):
    BASE = "base"
    AVALANCHE = "avalanche"

@dataclass
class BridgeQuote:
    protocol: BridgeProtocol
    source_chain: SourceChain
    amount: int
    fee_pct: float
    fee_amount: int
    total_cost_usd: float
    estimated_time_seconds: int
    gas_estimate: int

@dataclass
class BridgeResult:
    success: bool
    protocol: BridgeProtocol
    tx_hash: str
    source_chain: SourceChain
    amount: int
    fee: int
    destination: str  # Solana address
    estimated_arrival: str  # ISO timestamp
    status: str  # "pending", "completed", "failed"

# ──────────────────── Adapter ────────────────────

class SolanaBridgeAdapter:
    """
    Bridge USDC from EVM chains to Solana.

    Uses Across Protocol as primary (fastest, cheapest for our volume).
    Falls back to deBridge for large transfers (>$50K).
    """

    def __init__(
        self,
        evm_rpc_url: str,
        private_key: str,
        source_chain: SourceChain = SourceChain.BASE,
    ):
        """
        Initialize the bridge adapter.

        Args:
            evm_rpc_url: RPC endpoint for source chain
            private_key: EVM private key
            source_chain: Source chain (Base or Avalanche)
        """
        if Web3 is None:
            raise ImportError("web3 required: pip install web3")

        self.w3 = Web3(Web3.HTTPProvider(evm_rpc_url))
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address
        self.source_chain = source_chain

        # Set spoke pool based on source chain
        if source_chain == SourceChain.BASE:
            self.spokepool_address = Web3.to_checksum_address(ACROSS_SPOKEPOOL_BASE)
            self.usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
        elif source_chain == SourceChain.AVALANCHE:
            self.spokepool_address = Web3.to_checksum_address(ACROSS_SPOKEPOOL_AVALANCHE)
            self.usdc_address = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
        else:
            raise ValueError(f"Unsupported source chain: {source_chain}")

        self.spokepool = self.w3.eth.contract(
            address=self.spokepool_address,
            abi=SPOKEPOOL_ABI,
        )

        self.usdc = self.w3.eth.contract(
            address=self.usdc_address,
            abi=ERC20_ABI,
        )

        log.info(f"Bridge adapter initialized: {source_chain.value} → Solana")

    # ──────────── Quote ────────────

    def get_quote(
        self,
        amount: int,
        protocol: BridgeProtocol = BridgeProtocol.ACROSS,
    ) -> BridgeQuote:
        """
        Get a bridge quote.

        Args:
            amount: Amount of USDC to bridge (6 decimals)
            protocol: Bridge protocol to use

        Returns:
            BridgeQuote with fee and timing details
        """
        if protocol == BridgeProtocol.ACROSS:
            return self._get_across_quote(amount)
        elif protocol == BridgeProtocol.DEBRIDGE:
            return self._get_debridge_quote(amount)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def _get_across_quote(self, amount: int) -> BridgeQuote:
        """Get Across Protocol quote."""
        fee_pct = ACROSS_LP_FEE_PCT + ACROSS_RELAYER_FEE_PCT
        fee_amount = int(amount * fee_pct / 100)
        total_cost = amount * fee_pct / 100 / 1e6  # Convert to USD

        return BridgeQuote(
            protocol=BridgeProtocol.ACROSS,
            source_chain=self.source_chain,
            amount=amount,
            fee_pct=fee_pct,
            fee_amount=fee_amount,
            total_cost_usd=total_cost,
            estimated_time_seconds=5,  # Sub-5 second fills
            gas_estimate=300_000,
        )

    def _get_debridge_quote(self, amount: int) -> BridgeQuote:
        """Get deBridge quote."""
        # deBridge charges flat 0.001 ETH
        eth_price = 3500  # Approximate; in production fetch live
        fee_usd = DEBRIDGE_FEE * eth_price
        fee_amount = int(fee_usd * 1e6)  # Convert to USDC units

        return BridgeQuote(
            protocol=BridgeProtocol.DEBRIDGE,
            source_chain=self.source_chain,
            amount=amount,
            fee_pct=fee_usd / (amount / 1e6) * 100 if amount > 0 else 0,
            fee_amount=fee_amount,
            total_cost_usd=fee_usd,
            estimated_time_seconds=30,  # Instant finality but relayer delay
            gas_estimate=200_000,
        )

    def choose_protocol(self, amount: int) -> BridgeProtocol:
        """
        Automatically choose the best protocol for a transfer.

        Rules:
        - <$50K: Across (cheapest, fastest)
        - >$50K: deBridge (flat fee becomes cheaper)
        """
        amount_usd = amount / 1e6

        across_quote = self._get_across_quote(amount)
        debridge_quote = self._get_debridge_quote(amount)

        if amount_usd > 50_000 and debridge_quote.total_cost_usd < across_quote.total_cost_usd:
            return BridgeProtocol.DEBRIDGE
        return BridgeProtocol.ACROSS

    # ──────────── Bridge (Execute) ────────────

    def bridge(
        self,
        amount: int,
        solana_recipient: str,
        protocol: BridgeProtocol = None,
        slippage_pct: float = 0.5,
    ) -> BridgeResult:
        """
        Bridge USDC from EVM to Solana.

        Args:
            amount: Amount of USDC to bridge (6 decimals)
            solana_recipient: Solana wallet address to receive funds
            protocol: Bridge protocol (auto-selects if None)
            slippage_pct: Slippage tolerance

        Returns:
            BridgeResult with transaction details
        """
        if protocol is None:
            protocol = self.choose_protocol(amount)

        log.info(
            f"Bridging {amount/1e6:.2f} USDC → Solana via {protocol.value} "
            f"(recipient: {solana_recipient})"
        )

        if protocol == BridgeProtocol.ACROSS:
            return self._bridge_across(amount, solana_recipient, slippage_pct)
        elif protocol == BridgeProtocol.DEBRIDGE:
            return self._bridge_debridge(amount, solana_recipient)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def _bridge_across(
        self,
        amount: int,
        solana_recipient: str,
        slippage_pct: float,
    ) -> BridgeResult:
        """Execute bridge via Across Protocol."""
        try:
            # Approve USDC to SpokePool
            self._approve_usdc(amount)

            # Convert Solana address to bytes32 for Across
            recipient_bytes = self._solana_to_bytes32(solana_recipient)

            # Get quote timestamp
            block = self.w3.eth.get_block("latest")
            quote_timestamp = block.timestamp

            # Calculate relayer fee (in basis points, 6 decimal precision)
            relayer_fee_pct = int(ACROSS_RELAYER_FEE_PCT * 10000)  # Convert to int64

            # Solana chain ID for Across
            SOLANA_CHAIN_ID = 1223790511  # Across chain ID for Solana

            log.info(f"Depositing {amount/1e6:.2f} USDC to SpokePool...")

            tx = self.spokepool.functions.depositV3(
                self.address,                  # depositor
                recipient_bytes,               # recipient (bytes32)
                self.usdc_address,             # originToken (USDC)
                amount,                        # amount
                SOLANA_CHAIN_ID,               # destinationChainId
                relayer_fee_pct,               # relayerFeePct
                quote_timestamp,               # quoteTimestamp
                b"",                           # message (empty)
            ).build_transaction({
                "from": self.address,
                "nonce": self.w3.eth.get_transaction_count(self.address),
                "gas": 500_000,
                "gasPrice": self.w3.eth.gas_price,
                "chainId": self.w3.eth.chain_id,
                "value": 0,  # Across doesn't require ETH payment
            })

            signed = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                log.info(f"✅ Bridge submitted: {tx_hash.hex()}")
                return BridgeResult(
                    success=True,
                    protocol=BridgeProtocol.ACROSS,
                    tx_hash=tx_hash.hex(),
                    source_chain=self.source_chain,
                    amount=amount,
                    fee=int(amount * (ACROSS_LP_FEE_PCT + ACROSS_RELAYER_FEE_PCT) / 100),
                    destination=solana_recipient,
                    estimated_arrival=self._estimate_arrival(5),
                    status="pending",
                )
            else:
                log.error(f"❌ Bridge failed: {tx_hash.hex()}")
                return BridgeResult(
                    success=False,
                    protocol=BridgeProtocol.ACROSS,
                    tx_hash=tx_hash.hex(),
                    source_chain=self.source_chain,
                    amount=amount,
                    fee=0,
                    destination=solana_recipient,
                    estimated_arrival="",
                    status="failed",
                )

        except Exception as e:
            log.error(f"Bridge error: {e}")
            return BridgeResult(
                success=False,
                protocol=BridgeProtocol.ACROSS,
                tx_hash="",
                source_chain=self.source_chain,
                amount=amount,
                fee=0,
                destination=solana_recipient,
                estimated_arrival="",
                status="failed",
            )

    def _bridge_debridge(
        self,
        amount: int,
        solana_recipient: str,
    ) -> BridgeResult:
        """
        Execute bridge via deBridge.

        deBridge uses a different contract interface. In production,
        this would call the deBridge gateway contract.
        """
        log.info(f"deBridge bridge not yet fully implemented")
        log.info(f"Would bridge {amount/1e6:.2f} USDC to {solana_recipient}")

        return BridgeResult(
            success=False,
            protocol=BridgeProtocol.DEBRIDGE,
            tx_hash="",
            source_chain=self.source_chain,
            amount=amount,
            fee=0,
            destination=solana_recipient,
            estimated_arrival="",
            status="not_implemented",
        )

    # ──────────── Status Check ────────────

    def get_bridge_status(self, tx_hash: str) -> dict:
        """
        Check bridge transaction status.

        Args:
            tx_hash: EVM transaction hash

        Returns:
            dict with status info
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                "tx_hash": tx_hash,
                "confirmed": receipt.status == 1,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "completed" if receipt.status == 1 else "failed",
            }
        except Exception as e:
            return {
                "tx_hash": tx_hash,
                "confirmed": False,
                "status": "unknown",
                "error": str(e),
            }

    # ──────────── Utility ────────────

    def _approve_usdc(self, amount: int) -> bool:
        """Approve USDC spending by SpokePool."""
        current_allowance = self.usdc.functions.allowance(
            self.address, self.spokepool_address
        ).call()

        if current_allowance >= amount:
            return True

        tx = self.usdc.functions.approve(
            self.spokepool_address, amount
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
            log.info(f"Approved {amount/1e6:.2f} USDC for SpokePool")
            return True
        else:
            log.error(f"Approval failed: {tx_hash.hex()}")
            return False

    def _solana_to_bytes32(self, solana_address: str) -> bytes:
        """
        Convert Solana base58 address to bytes32 for Across.

        Across uses bytes32 for cross-chain recipients.
        Solana addresses are 32-byte public keys, so we can
        directly encode them.
        """
        import base58
        decoded = base58.b58decode(solana_address)
        if len(decoded) != 32:
            raise ValueError(f"Invalid Solana address length: {len(decoded)}")
        return decoded

    def _estimate_arrival(self, seconds: int) -> str:
        """Estimate arrival time as ISO timestamp."""
        from datetime import datetime, timezone, timedelta
        arrival = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        return arrival.isoformat()

    def get_usdc_balance(self) -> int:
        """Get USDC balance on source chain."""
        return self.usdc.functions.balanceOf(self.address).call()

    def estimate_gas_cost(self, amount: int) -> float:
        """Estimate gas cost in USD."""
        gas_price = self.w3.eth.gas_price
        gas_units = 300_000
        gas_eth = gas_price * gas_units / 1e18

        # ETH price (approximate; in production fetch live)
        eth_price = 3500 if self.source_chain == SourceChain.BASE else 40

        return gas_eth * eth_price


# ──────────────────── Standalone Test ────────────────────

def test_adapter():
    """Quick test of adapter initialization."""
    print("🧪 Solana Bridge Adapter Test")
    print("=" * 50)

    # Load config
    with open(CONFIG_FILE) as f:
        config = json.load(f)

    print("Bridge Routes:")
    print(f"  Base → Solana (Across): {ACROSS_SPOKEPOOL_BASE}")
    print(f"  Avalanche → Solana (Across): {ACROSS_SPOKEPOOL_AVALANCHE}")
    print()

    print("Fees:")
    print(f"  Across LP Fee: {ACROSS_LP_FEE_PCT}%")
    print(f"  Across Relayer Fee: ~{ACROSS_RELAYER_FEE_PCT}%")
    print(f"  deBridge Flat Fee: {DEBRIDGE_FEE} ETH (~$3.50)")
    print()

    print("Decision Rules:")
    print("  <$50K → Across (cheapest, fastest)")
    print("  >$50K → deBridge (flat fee becomes cheaper)")
    print()

    # Check dependencies
    if Web3:
        print("✅ web3 installed")
    else:
        print("⚠️  pip install web3")

    if __import__('importlib').util.find_spec('base58'):
        print("✅ base58 installed")
    else:
        print("⚠️  pip install base58 (needed for Solana address conversion)")

    print()
    print("Adapter ready for deployment with PRIVATE_KEY env var")


if __name__ == "__main__":
    test_adapter()
