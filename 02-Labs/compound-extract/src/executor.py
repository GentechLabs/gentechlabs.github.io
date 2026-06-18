"""
Compound vs. Extract Protocol — Executor Module

Executes compound or extract operations on LP positions.
Supports pluggable swap adapters for cross-chain compatibility.

Adapters:
  - LFJAdapter: Trader Joe on Avalanche (concentrated liquidity)
  - ZeroXSwapRouter: 0x API for EVM chains
  - JupiterSwapRouter: Jupiter aggregator on Solana
"""

import json
import time
import logging
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OperationResult(Enum):
    """Outcome of an executor operation"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SIMULATED = "simulated"


@dataclass
class TransactionReceipt:
    """Receipt for a single on-chain transaction"""
    tx_hash: str
    status: OperationResult
    gas_used: int
    block_number: int
    timestamp: str
    method: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractResult:
    """Full result of an extract operation"""
    status: OperationResult
    position_id: str
    amount_claimed: Dict[str, float]
    amount_received: Dict[str, float]
    swap_rate: float
    gas_fees: float
    transactions: List[TransactionReceipt]
    timestamp: str
    error: Optional[str] = None


@dataclass
class CompoundResult:
    """Full result of a compound operation"""
    status: OperationResult
    position_id: str
    amount_compounded: Dict[str, float]
    new_position_value: Dict[str, float]
    gas_fees: float
    transactions: List[TransactionReceipt]
    timestamp: str
    error: Optional[str] = None


# ─── Adapter Interfaces ───────────────────────────────────────────────────────

class SwapAdapter(ABC):
    """Abstract base for DEX swap adapters"""

    @abstractmethod
    def get_quote(self, token_in: str, token_out: str, amount_in: float) -> Dict:
        """Get a swap quote without executing"""
        ...

    @abstractmethod
    def swap(self, token_in: str, token_out: str, amount_in: float,
             slippage: float = 0.005) -> TransactionReceipt:
        """Execute a swap"""
        ...

    @abstractmethod
    def approve(self, token: str, amount: float) -> TransactionReceipt:
        """Approve token spend"""
        ...


class LFJAdapter(SwapAdapter):
    """
    Trader Joe (LFJ) adapter for Avalanche.

    Supports both concentrated liquidity (V2.1) and standard pools.
    Uses on-chain Router and Position Manager contracts.
    """

    def __init__(self, rpc_url: str, chain_id: int, wallet_address: str = "",
                 private_key: str = ""):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.wallet_address = wallet_address
        self.private_key = private_key

        # LFJ V2.1 contract addresses (Avalanche)
        self.contracts = {
            "router": "0x530d3DE1b623d044682C9f13a816F13648174c48",
            "position_manager": "0x6423144E432B44e70162476cDc4A99510b4B41e4",
            "factory": "0x86dAD609A08c0A780ad798Ff0694f0f10f04b510",
            "weth": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
            "usdc": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        }

        # Swap route cache
        self._route_cache: Dict[str, Dict] = {}

        logger.info(f"LFJAdapter initialized — chain {self.chain_id}, RPC {self.rpc_url}")

    def get_quote(self, token_in: str, token_out: str, amount_in: float) -> Dict:
        """Get LFJ swap quote (simulated on testnet)"""
        cache_key = f"{token_in}:{token_out}:{amount_in}"

        # Simulate a realistic quote
        simulated_rate = self._get_simulated_rate(token_in, token_out)
        amount_out = amount_in * simulated_rate

        quote = {
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": amount_in,
            "amount_out": amount_out,
            "rate": simulated_rate,
            "price_impact": 0.001,  # 0.1%
            "pool_fee": 0.003,       # 0.3%
            "estimated_gas": 250000,
            "router": self.contracts["router"],
        }

        self._route_cache[cache_key] = quote
        logger.info(f"LFJ quote: {amount_in} {token_in} → {amount_out:.4f} {token_out}")
        return quote

    def swap(self, token_in: str, token_out: str, amount_in: float,
             slippage: float = 0.005) -> TransactionReceipt:
        """Execute LFJ swap (simulated on testnet)"""
        quote = self.get_quote(token_in, token_out, amount_in)

        # Simulate tx hash
        tx_data = f"lfj:{token_in}:{token_out}:{amount_in}:{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        receipt = TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=250000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="swap",
            details={
                "token_in": token_in,
                "token_out": token_out,
                "amount_in": amount_in,
                "amount_out": quote["amount_out"],
                "slippage": slippage,
                "pool_fee": quote["pool_fee"],
            },
        )

        logger.info(f"LFJ swap simulated: {tx_hash[:16]}...")
        return receipt

    def approve(self, token: str, amount: float) -> TransactionReceipt:
        """Approve LFJ router to spend tokens (simulated)"""
        tx_data = f"approve:{token}:{amount}:{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=50000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="approve",
            details={"token": token, "amount": amount, "spender": self.contracts["router"]},
        )

    def add_liquidity(self, position_id: str, amount0: float, amount1: float) -> TransactionReceipt:
        """Add liquidity to existing LFJ position (simulated)"""
        tx_data = f"add_liq:{position_id}:{amount0}:{amount1}:{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=400000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="increaseLiquidity",
            details={
                "position_id": position_id,
                "amount0": amount0,
                "amount1": amount1,
            },
        )

    def claim_fees(self, nft_id: str) -> TransactionReceipt:
        """Claim accumulated fees from LFJ position (simulated)"""
        tx_data = f"claim:{nft_id}:{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=180000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="collect",
            details={"nft_id": nft_id, "fees_claimed": True},
        )

    def _get_simulated_rate(self, token_in: str, token_out: str) -> float:
        """Get simulated exchange rate for testnet"""
        rates = {
            ("AVAX", "USDC"): 35.0,
            ("USDC", "AVAX"): 1.0 / 35.0,
            ("AVAX", "USDC.e"): 35.0,
            ("USDC.e", "AVAX"): 1.0 / 35.0,
            ("USDC", "USDC.e"): 1.0,
            ("USDC.e", "USDC"): 1.0,
        }
        return rates.get((token_in, token_out), 1.0)


class ZeroXSwapRouter(SwapAdapter):
    """
    0x API swap adapter for EVM chains.

    Uses 0x Swap API for best-rate routing across DEXs.
    Supports: Ethereum, Polygon, Avalanche, Base, Arbitrum, Optimism.
    """

    BASE_URLS = {
        1: "https://api.0x.org/swap/v1",
        43114: "https://avalanche.api.0x.org/swap/v1",
        43113: "https://avalanche.api.0x.org/swap/v1",  # testnet uses same
        8453: "https://base.api.0x.org/swap/v1",
    }

    def __init__(self, rpc_url: str, chain_id: int, wallet_address: str = "",
                 api_key: str = ""):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.wallet_address = wallet_address
        self.api_key = api_key
        self.base_url = self.BASE_URLS.get(chain_id, "https://api.0x.org/swap/v1")

        logger.info(f"ZeroXSwapRouter initialized — chain {self.chain_id}")

    def get_quote(self, token_in: str, token_out: str, amount_in: float) -> Dict:
        """Get 0x quote (simulated on testnet)"""
        simulated_rate = self._get_simulated_rate(token_in, token_out)
        amount_out = amount_in * simulated_rate * 0.999  # 0.1% spread

        return {
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": amount_in,
            "amount_out": amount_out,
            "rate": simulated_rate,
            "price_impact": 0.001,
            "source": "0x",
            "estimated_gas": 150000,
        }

    def swap(self, token_in: str, token_out: str, amount_in: float,
             slippage: float = 0.005) -> TransactionReceipt:
        """Execute 0x swap (simulated)"""
        quote = self.get_quote(token_in, token_out, amount_in)

        tx_data = f"0x:{token_in}:{token_out}:{amount_in}:{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=150000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="swap",
            details={
                "token_in": token_in,
                "token_out": token_out,
                "amount_in": amount_in,
                "amount_out": quote["amount_out"],
                "source": "0x",
            },
        )

    def approve(self, token: str, amount: float) -> TransactionReceipt:
        """Approve 0x proxy (simulated)"""
        tx_data = f"0x_approve:{token}:{amount}:{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=45000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="approve",
            details={"token": token, "amount": amount},
        )

    def _get_simulated_rate(self, token_in: str, token_out: str) -> float:
        rates = {
            ("AVAX", "USDC"): 35.0,
            ("USDC", "AVAX"): 1.0 / 35.0,
            ("WETH", "USDC"): 3500.0,
            ("USDC", "WETH"): 1.0 / 3500.0,
        }
        return rates.get((token_in, token_out), 1.0)


class JupiterSwapRouter(SwapAdapter):
    """
    Jupiter aggregator adapter for Solana.

    Uses Jupiter API for best-rate routing across Solana DEXs.
    """

    def __init__(self, rpc_url: str, wallet_address: str = ""):
        self.rpc_url = rpc_url
        self.wallet_address = wallet_address
        logger.info(f"JupiterSwapRouter initialized — Solana")

    def get_quote(self, token_in: str, token_out: str, amount_in: float) -> Dict:
        return {
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": amount_in,
            "amount_out": amount_in,  # placeholder
            "source": "jupiter",
        }

    def swap(self, token_in: str, token_out: str, amount_in: float,
             slippage: float = 0.005) -> TransactionReceipt:
        tx_data = f"jup:{token_in}:{token_out}:{amount_in}:{time.time()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=5000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="swap",
            details={"token_in": token_in, "token_out": token_out},
        )

    def approve(self, token: str, amount: float) -> TransactionReceipt:
        tx_data = f"jup_approve:{token}:{amount}:{time.time()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()[:64]
        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=5000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="approve",
            details={"token": token, "amount": amount},
        )


# ─── Executor ─────────────────────────────────────────────────────────────────

class Executor:
    """
    Executes compound and extract operations for LP positions.

    Usage:
        lfj = LFJAdapter(rpc_url="...", chain_id=43113)
        executor = Executor(adapter=lfj, wallet_address="0x...")
        result = executor.extract(position, fees, target_token="USDC")
    """

    def __init__(self, adapter: SwapAdapter, wallet_address: str,
                 max_slippage: float = 0.005):
        self.adapter = adapter
        self.wallet_address = wallet_address
        self.max_slippage = max_slippage
        self.operation_log: List[Dict] = []

        logger.info(f"Executor initialized with {adapter.__class__.__name__}")

    def extract(self,
                position_id: str,
                fees: Dict[str, float],
                target_token: str = "USDC",
                amount_usd: Optional[float] = None) -> ExtractResult:
        """
        Extract fees from a position.

        Flow:
          1. Claim fees from DEX (on-chain)
          2. Swap claimed tokens to target stablecoin
          3. Transfer to user wallet (simulated — already in wallet after swap)

        Args:
            position_id: Position to extract from
            fees: Dict of token -> amount (e.g. {"AVAX": 0.5, "USDC": 10.0})
            target_token: Token to convert fees into
            amount_usd: Optional USD cap on extraction amount
        """
        logger.info(f"=== EXTRACT: position={position_id}, target={target_token} ===")
        transactions = []
        amount_claimed = dict(fees)
        amount_received = {}

        try:
            # Step 1: Claim fees from DEX
            # In production, this calls the LFJ Position Manager
            # For testnet scaffold, simulate it
            nft_id = position_id.split("_")[-1] if "_" in position_id else "001"
            claim_tx = self._simulate_claim_fees(nft_id)
            transactions.append(claim_tx)
            logger.info(f"  ✅ Claimed fees: {amount_claimed}")

            # Step 2: Swap each non-target token to target
            total_target = amount_claimed.get(target_token, 0.0)

            for token, amount in amount_claimed.items():
                if token == target_token or amount <= 0:
                    continue

                logger.info(f"  Swapping {amount} {token} → {target_token}")
                swap_tx = self.adapter.swap(
                    token_in=token,
                    token_out=target_token,
                    amount_in=amount,
                    slippage=self.max_slippage,
                )
                transactions.append(swap_tx)

                # Extract received amount from details
                received = swap_tx.details.get("amount_out", 0.0)
                total_target += received
                amount_received[target_token] = total_target
                logger.info(f"  ✅ Received {received:.4f} {target_token}")

            if target_token not in amount_received:
                amount_received[target_token] = total_target

            # Step 3: Transfer to wallet (simulated — balance updates)
            logger.info(f"  Total {target_token} in wallet: {total_target:.4f}")

            result = ExtractResult(
                status=OperationResult.SIMULATED,
                position_id=position_id,
                amount_claimed=amount_claimed,
                amount_received=amount_received,
                swap_rate=amount_received.get(target_token, 0) / max(sum(fees.values()), 0.001),
                gas_fees=sum(tx.gas_used * 25e-9 for tx in transactions),  # rough AVAX estimate
                transactions=transactions,
                timestamp=datetime.utcnow().isoformat(),
            )

            self._log_operation("extract", result)
            return result

        except Exception as e:
            logger.error(f"Extract failed: {e}")
            return ExtractResult(
                status=OperationResult.FAILED,
                position_id=position_id,
                amount_claimed=amount_claimed,
                amount_received={},
                swap_rate=0,
                gas_fees=0,
                transactions=transactions,
                timestamp=datetime.utcnow().isoformat(),
                error=str(e),
            )

    def compound(self,
                 position_id: str,
                 fees: Dict[str, float],
                 pair_tokens: tuple = ("AVAX", "USDC"),
                 compound_ratio: float = 1.0) -> CompoundResult:
        """
        Compound fees back into the LP position.

        Flow:
          1. Claim fees from DEX
          2. Swap half to the other token in the pair
          3. Add liquidity back into the position

        Args:
            position_id: Position to compound into
            fees: Dict of token -> amount
            pair_tokens: Tuple of (token0, token1) in the pair
            compound_ratio: Fraction of fees to compound (0-1)
        """
        logger.info(f"=== COMPOUND: position={position_id}, ratio={compound_ratio} ===")
        transactions = []
        compounded = {}

        try:
            # Step 1: Claim fees
            nft_id = position_id.split("_")[-1] if "_" in position_id else "001"
            claim_tx = self._simulate_claim_fees(nft_id)
            transactions.append(claim_tx)
            logger.info(f"  ✅ Claimed fees: {fees}")

            # Step 2: Swap to balance the pair
            token0, token1 = pair_tokens
            fees_to_compound = {t: a * compound_ratio for t, a in fees.items()}

            # Calculate how much of each token we need
            total_value = sum(fees_to_compound.values())
            if total_value <= 0:
                raise ValueError("No fees to compound")

            # Swap excess of one token to the other
            for token, amount in fees_to_compound.items():
                if amount <= 0:
                    continue

                other_token = token1 if token == token0 else token0
                swap_amount = amount / 2  # Swap half

                if swap_amount > 0:
                    logger.info(f"  Swapping {swap_amount:.4f} {token} → {other_token}")
                    swap_tx = self.adapter.swap(
                        token_in=token,
                        token_out=other_token,
                        amount_in=swap_amount,
                        slippage=self.max_slippage,
                    )
                    transactions.append(swap_tx)
                    logger.info(f"  ✅ Swap complete: {swap_tx.tx_hash[:16]}...")

            # Step 3: Add liquidity
            liq_amount0 = fees_to_compound.get(token0, 0) / 2
            liq_amount1 = fees_to_compound.get(token1, 0) / 2

            if hasattr(self.adapter, 'add_liquidity'):
                liq_tx = self.adapter.add_liquidity(position_id, liq_amount0, liq_amount1)
            else:
                # Generic — simulate add liquidity
                liq_tx = self._simulate_add_liquidity(position_id, liq_amount0, liq_amount1)

            transactions.append(liq_tx)
            logger.info(f"  ✅ Liquidity added: {liq_amount0:.4f} {token0} + {liq_amount1:.4f} {token1}")

            # Record compounded amounts
            compounded = {t: a for t, a in fees_to_compound.items() if a > 0}

            result = CompoundResult(
                status=OperationResult.SIMULATED,
                position_id=position_id,
                amount_compounded=compounded,
                new_position_value={t: a * 1.1 for t, a in compounded.items()},  # simulated growth
                gas_fees=sum(tx.gas_used * 25e-9 for tx in transactions),
                transactions=transactions,
                timestamp=datetime.utcnow().isoformat(),
            )

            self._log_operation("compound", result)
            return result

        except Exception as e:
            logger.error(f"Compound failed: {e}")
            return CompoundResult(
                status=OperationResult.FAILED,
                position_id=position_id,
                amount_compounded={},
                new_position_value={},
                gas_fees=0,
                transactions=transactions,
                timestamp=datetime.utcnow().isoformat(),
                error=str(e),
            )

    def _simulate_claim_fees(self, nft_id: str) -> TransactionReceipt:
        """Simulate claiming fees from a position"""
        tx_data = f"claim:{nft_id}:{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=180000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="collect",
            details={"nft_id": nft_id},
        )

    def _simulate_add_liquidity(self, position_id: str, amount0: float,
                                 amount1: float) -> TransactionReceipt:
        """Simulate adding liquidity"""
        tx_data = f"add_liq:{position_id}:{amount0}:{amount1}:{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        return TransactionReceipt(
            tx_hash=tx_hash,
            status=OperationResult.SIMULATED,
            gas_used=400000,
            block_number=99999999,
            timestamp=datetime.utcnow().isoformat(),
            method="increaseLiquidity",
            details={"position_id": position_id, "amount0": amount0, "amount1": amount1},
        )

    def _log_operation(self, op_type: str, result):
        """Log operation to internal history"""
        entry = {
            "type": op_type,
            "timestamp": datetime.utcnow().isoformat(),
            "status": result.status.value,
            "position_id": result.position_id,
            "tx_count": len(result.transactions),
            "gas_fees": result.gas_fees,
        }
        self.operation_log.append(entry)
        logger.info(f"  📝 Logged {op_type} operation: {entry}")


# ─── Convenience factory ──────────────────────────────────────────────────────

def create_executor(chain: str = "avalanche", **kwargs) -> Executor:
    """
    Factory to create an Executor with the right adapter.

    Usage:
        executor = create_executor(chain="avalanche", rpc_url="...", wallet="0x...")
        executor = create_executor(chain="evm", rpc_url="...", wallet="0x...", chain_id=137)
    """
    chain = chain.lower()

    if chain in ("avalanche", "avax", "fuji"):
        adapter = LFJAdapter(
            rpc_url=kwargs.get("rpc_url", "https://api.avax-test.network/ext/bc/C/rpc"),
            chain_id=kwargs.get("chain_id", 43113),
            wallet_address=kwargs.get("wallet", ""),
        )
    elif chain in ("solana", "sol"):
        adapter = JupiterSwapRouter(
            rpc_url=kwargs.get("rpc_url", "https://api.mainnet-beta.solana.com"),
            wallet_address=kwargs.get("wallet", ""),
        )
    else:
        adapter = ZeroXSwapRouter(
            rpc_url=kwargs.get("rpc_url", ""),
            chain_id=kwargs.get("chain_id", 1),
            wallet_address=kwargs.get("wallet", ""),
        )

    return Executor(
        adapter=adapter,
        wallet_address=kwargs.get("wallet", ""),
        max_slippage=kwargs.get("max_slippage", 0.005),
    )


# ─── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🧪 Compound vs. Extract — Executor Module\n")

    # Create testnet executor
    executor = create_executor(
        chain="avalanche",
        rpc_url="https://api.avax-test.network/ext/bc/C/rpc",
        wallet="0xTestWallet1234567890abcdef1234567890abcdef",
    )

    # Simulate extract
    print("--- Extract Test ---")
    extract_result = executor.extract(
        position_id="lfj_avax_usdc_001",
        fees={"AVAX": 0.5, "USDC": 10.0},
        target_token="USDC",
    )
    print(f"  Status: {extract_result.status.value}")
    print(f"  Claimed: {extract_result.amount_claimed}")
    print(f"  Received: {extract_result.amount_received}")
    print(f"  Gas: {extract_result.gas_fees:.6f} AVAX")

    # Simulate compound
    print("\n--- Compound Test ---")
    compound_result = executor.compound(
        position_id="lfj_avax_usdc_001",
        fees={"AVAX": 0.3, "USDC": 8.0},
        pair_tokens=("AVAX", "USDC"),
    )
    print(f"  Status: {compound_result.status.value}")
    print(f"  Compounded: {compound_result.amount_compounded}")
    print(f"  Gas: {compound_result.gas_fees:.6f} AVAX")

    print("\n✅ Executor module working (testnet simulated)")
