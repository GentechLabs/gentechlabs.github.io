#!/usr/bin/env python3
"""
AAE Dry Powder Vault — Avalanche Bridge Adapter (Base → Avalanche USDC rail)

Fills the missing cross-chain rail for the Agentic Treasury (item #51).
The treasury can bridge Base→Solana (solana_bridge_adapter.py, Across) but NOT
Base→Avalanche. This adapter wires the Base→Avalanche USDC rail via Across
Protocol, with a live fee quote from the Across API and a per-bridge fee layer
for users (GenTech takes a spread on top of the underlying bridge cost).

Reference: Treasury/Agentic-Bridge-capability-and-spec-2026-08-06.md
"""

import json
import os
import time
import logging
import urllib.request
import urllib.parse
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum

try:
    from web3 import Web3
except ImportError:
    Web3 = None

log = logging.getLogger("avax-bridge")

# ──────────────────── Constants ────────────────────

VAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(VAULT_DIR, "config", "vault-config.json")

# Across Protocol SpokePool Addresses (mainnet)
ACROSS_SPOKEPOOL_BASE = "0xb4a8d45647445EA9FC3E1058096142390683dBC2"
ACROSS_SPOKEPOOL_AVALANCHE = "0x6f26bf09b1c792e3228e5467807a900a503c0281"

# USDC (native) addresses
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDC_AVALANCHE = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"

# Across API — live fee quotes
ACROSS_API = "https://app.across.to/api/suggested-fees"

# Chain IDs
CHAIN_BASE = 8453
CHAIN_AVALANCHE = 43114

# Across fee tiers (fallback if API unreachable)
ACROSS_LP_FEE_PCT = 0.06    # 0.06%
ACROSS_RELAYER_FEE_PCT = 0.02  # ~0.02%

# ──────────────────── ABIs ────────────────────

# Across SpokePool Minimal ABI (depositV3)
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
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# ──────────────────── Types ────────────────────


class BridgeProtocol(Enum):
    ACROSS = "across"
    CCTP = "cctp"


@dataclass
class BridgeQuote:
    protocol: str
    source_chain: str
    destination_chain: str
    amount: int
    fee_pct: float
    fee_amount: int
    total_cost_usd: float
    estimated_time_seconds: int
    output_amount: int
    gen_tech_fee: int
    source: str  # "live" or "estimate"


@dataclass
class BridgeResult:
    success: bool
    protocol: str
    tx_hash: str
    source_chain: str
    amount: int
    fee: int
    destination: str
    estimated_arrival: str
    status: str


# ──────────────────── Adapter ────────────────────


class AvalancheBridgeAdapter:
    """
    Bridge USDC from Base to Avalanche via Across Protocol.

    Fills the Base→Avalanche gap in the Agentic Treasury. Uses the Across
    API for live fee quotes, and applies a per-bridge GenTech fee layer
    (bridge_fee_bps from vault-config.json) on top of the underlying cost.
    """

    def __init__(
        self,
        evm_rpc_url: str = "https://mainnet.base.org",
        private_key: Optional[str] = None,
        bridge_fee_bps: Optional[int] = None,
    ):
        self.rpc_url = evm_rpc_url
        self.private_key = private_key
        self.address = None

        # Load bridge fee from config if not provided
        if bridge_fee_bps is None:
            bridge_fee_bps = self._load_bridge_fee_bps()
        self.bridge_fee_bps = bridge_fee_bps

        if Web3 is not None:
            self.w3 = Web3(Web3.HTTPProvider(evm_rpc_url))
            self.spokepool_address = Web3.to_checksum_address(ACROSS_SPOKEPOOL_BASE)
            self.usdc_address = Web3.to_checksum_address(USDC_BASE)
            self.spokepool = self.w3.eth.contract(
                address=self.spokepool_address, abi=SPOKEPOOL_ABI
            )
            self.usdc = self.w3.eth.contract(
                address=self.usdc_address, abi=ERC20_ABI
            )
            if private_key:
                self.account = self.w3.eth.account.from_key(private_key)
                self.address = self.account.address
        else:
            self.w3 = None

    def _load_bridge_fee_bps(self) -> int:
        """Load bridge_fee_bps from vault config (default 20 = 0.20%)."""
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            return int(cfg.get("vault", {}).get("bridge_fee_bps", 20))
        except Exception:
            return 20

    # ──────────── Live Quote (Across API) ────────────

    def get_quote(self, amount: int) -> BridgeQuote:
        """
        Get a live Base→Avalanche USDC bridge quote from the Across API.

        Args:
            amount: Amount of USDC to bridge (6 decimals, e.g. 1_000_000 = $1.00)

        Returns:
            BridgeQuote with live fee + timing + GenTech fee layer.
        """
        params = {
            "originChainId": CHAIN_BASE,
            "destinationChainId": CHAIN_AVALANCHE,
            "token": USDC_BASE,
            "amount": str(amount),
        }
        url = f"{ACROSS_API}?{urllib.parse.urlencode(params)}"

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0 (GenTech Agentic Treasury; +https://gentechlabs.net)",
                },
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())

            # Across returns fees in raw units (6 decimals for USDC)
            relay_fee_total = int(data.get("relayFeeTotal", 0))
            lp_fee_total = int(data.get("lpFee", {}).get("total", 0))
            total_fee = relay_fee_total + lp_fee_total
            output_amount = int(data.get("outputAmount", amount - total_fee))
            fill_time = int(data.get("estimatedFillTimeSec", 5))

            fee_pct = (total_fee / amount * 100) if amount > 0 else 0.0
            gen_tech_fee = int(amount * self.bridge_fee_bps / 10000)

            return BridgeQuote(
                protocol="across",
                source_chain="base",
                destination_chain="avalanche",
                amount=amount,
                fee_pct=fee_pct,
                fee_amount=total_fee,
                total_cost_usd=total_fee / 1e6,
                estimated_time_seconds=fill_time,
                output_amount=output_amount,
                gen_tech_fee=gen_tech_fee,
                source="live",
            )
        except Exception as e:
            log.warning(f"Across API quote failed ({e}); using estimate")
            return self._estimate_quote(amount)

    def _estimate_quote(self, amount: int) -> BridgeQuote:
        """Fallback estimate if the Across API is unreachable."""
        fee_pct = ACROSS_LP_FEE_PCT + ACROSS_RELAYER_FEE_PCT
        fee_amount = int(amount * fee_pct / 100) if amount > 0 else 0
        gen_tech_fee = int(amount * self.bridge_fee_bps / 10000) if amount > 0 else 0
        return BridgeQuote(
            protocol="across",
            source_chain="base",
            destination_chain="avalanche",
            amount=amount,
            fee_pct=fee_pct if amount > 0 else 0.0,
            fee_amount=fee_amount,
            total_cost_usd=fee_amount / 1e6,
            estimated_time_seconds=5,
            output_amount=amount - fee_amount,
            gen_tech_fee=gen_tech_fee,
            source="estimate",
        )

    # ──────────── Execute ────────────

    def bridge(
        self,
        amount: int,
        recipient: str,
        slippage_pct: float = 0.5,
    ) -> BridgeResult:
        """
        Bridge USDC from Base to Avalanche via Across Protocol.

        Args:
            amount: Amount of USDC to bridge (6 decimals)
            recipient: Avalanche address to receive funds
            slippage_pct: Slippage tolerance (unused for USDC→USDC, kept for API compat)

        Returns:
            BridgeResult with transaction details.
        """
        if self.w3 is None:
            raise ImportError("web3 required: pip install web3")
        if not self.private_key or not self.address:
            raise RuntimeError("private_key required to execute bridge")

        try:
            # Approve USDC to SpokePool
            self._approve_usdc(amount)

            # Get live quote for relayer fee
            quote = self.get_quote(amount)
            relayer_fee_pct = int(quote.fee_pct * 10000)  # to int64 basis points

            block = self.w3.eth.get_block("latest")
            quote_timestamp = block.timestamp

            # Convert Avalanche address to bytes32 for Across
            recipient_bytes = self._evm_to_bytes32(recipient)

            log.info(
                f"Depositing {amount/1e6:.2f} USDC Base→Avalanche "
                f"(relayerFeePct={relayer_fee_pct})..."
            )

            tx = self.spokepool.functions.depositV3(
                self.address,          # depositor
                recipient_bytes,       # recipient (bytes32)
                self.usdc_address,     # originToken (USDC Base)
                amount,                # amount
                CHAIN_AVALANCHE,       # destinationChainId
                relayer_fee_pct,       # relayerFeePct
                quote_timestamp,       # quoteTimestamp
                b"",                   # message (empty)
            ).build_transaction({
                "from": self.address,
                "nonce": self.w3.eth.get_transaction_count(self.address),
                "gas": 500_000,
                "gasPrice": self.w3.eth.gas_price,
                "chainId": self.w3.eth.chain_id,
                "value": 0,
            })

            signed = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                log.info(f"✅ Bridge submitted: {tx_hash.hex()}")
                return BridgeResult(
                    success=True,
                    protocol="across",
                    tx_hash=tx_hash.hex(),
                    source_chain="base",
                    amount=amount,
                    fee=quote.fee_amount,
                    destination=recipient,
                    estimated_arrival=self._estimate_arrival(quote.estimated_time_seconds),
                    status="pending",
                )
            else:
                log.error(f"❌ Bridge failed: {tx_hash.hex()}")
                return BridgeResult(
                    success=False, protocol="across", tx_hash=tx_hash.hex(),
                    source_chain="base", amount=amount, fee=0,
                    destination=recipient, estimated_arrival="", status="failed",
                )
        except Exception as e:
            log.error(f"Bridge error: {e}")
            return BridgeResult(
                success=False, protocol="across", tx_hash="",
                source_chain="base", amount=amount, fee=0,
                destination=recipient, estimated_arrival="", status="failed",
            )

    # ──────────── Status Check ────────────

    def get_bridge_status(self, tx_hash: str) -> dict:
        """Check bridge transaction status on Base."""
        if self.w3 is None:
            return {"tx_hash": tx_hash, "confirmed": False, "status": "unknown"}
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
            return {"tx_hash": tx_hash, "confirmed": False, "status": "unknown", "error": str(e)}

    # ──────────── Utility ────────────

    def _approve_usdc(self, amount: int) -> bool:
        """Approve USDC spending by SpokePool."""
        current = self.usdc.functions.allowance(
            self.address, self.spokepool_address
        ).call()
        if current >= amount:
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
        log.error(f"Approval failed: {tx_hash.hex()}")
        return False

    @staticmethod
    def _evm_to_bytes32(address: str) -> bytes:
        """Convert an EVM address to bytes32 (left-padded) for Across."""
        addr = address.lower().replace("0x", "")
        return bytes.fromhex(addr.rjust(64, "0"))

    @staticmethod
    def _estimate_arrival(seconds: int) -> str:
        """Return ISO timestamp for estimated arrival."""
        import datetime
        return (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)).isoformat() + "Z"

    def to_dict(self, quote: BridgeQuote) -> dict:
        """Serialize a quote for logging/reporting."""
        return asdict(quote)


# ──────────────────── CLI ────────────────────


def main():
    import sys

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(sys.argv) < 2:
        print("Usage: python3 avax_bridge_adapter.py <amount_usdc> [--json]")
        print("  amount_usdc: amount in whole USDC (e.g. 100 = $100)")
        sys.exit(1)

    amount_usd = float(sys.argv[1])
    amount = int(amount_usd * 1e6)
    as_json = "--json" in sys.argv

    adapter = AvalancheBridgeAdapter()
    quote = adapter.get_quote(amount)

    if as_json:
        print(json.dumps(adapter.to_dict(quote), indent=2))
    else:
        print("=" * 56)
        print("🧭 Base → Avalanche USDC Bridge Quote (Across)")
        print("=" * 56)
        print(f"  Amount:            ${amount/1e6:,.2f} USDC")
        print(f"  Output:            ${quote.output_amount/1e6:,.2f} USDC")
        print(f"  Bridge fee:        ${quote.fee_amount/1e6:,.4f} ({quote.fee_pct:.4f}%)")
        print(f"  GenTech fee:       ${quote.gen_tech_fee/1e6:,.4f} ({self_bps(adapter)} bps)")
        print(f"  Est. fill time:    {quote.estimated_time_seconds}s")
        print(f"  Quote source:      {quote.source}")
        print("=" * 56)


def self_bps(adapter):
    return adapter.bridge_fee_bps


if __name__ == "__main__":
    main()
