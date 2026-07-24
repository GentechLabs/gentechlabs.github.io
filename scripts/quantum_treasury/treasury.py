"""
Quantum-Safe Agentic Treasury — Main Orchestrator

Ties together:
- Hybrid signing (ECDSA + SPHINCS+)
- Fresh address generation
- Model interaction logging
- Quantum emergency circuit

Usage:
    from agentic_treasury import Treasury

    treasury = Treasury(master_seed=b"...")
    sig = treasury.sign(b"transaction data")
    result = treasury.verify(sig, b"transaction data")
"""

import datetime
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .hybrid_signer import (
    HYBRID_ALGORITHM,
    HybridSigner,
    HybridSignature,
)
from .address_generator import AddressGenerator, FreshAddress
from .export_logger import InteractionLogger, ModelInteraction

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_DIR = "/etc/gentech/treasury"
DEFAULT_LOG_DIR = "/var/log/gentech/treasury"

# Circuit breaker states
CIRCUIT_CLOSED = "closed"  # Normal operation
CIRCUIT_OPEN = "open"  # All outbound paused
CIRCUIT_HALTED = "halted"  # Emergency — all operations paused


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


@dataclass
class SignedTransaction:
    """A transaction with its hybrid signature."""

    transaction_data: bytes
    hybrid_signature: HybridSignature
    source_address: Optional[str] = None
    destination_address: Optional[str] = None
    amount_usd: float = 0.0
    chain: str = "base"
    created_at: str = ""
    id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "transaction_data": self.transaction_data.hex(),
            "hybrid_signature": self.hybrid_signature.to_dict(),
            "source_address": self.source_address,
            "destination_address": self.destination_address,
            "amount_usd": self.amount_usd,
            "chain": self.chain,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Treasury
# ---------------------------------------------------------------------------


class Treasury:
    """
    Quantum-Safe Agentic Treasury.

    Manages hybrid signing, fresh addresses, model logging,
    and the quantum emergency circuit.

    Usage:
        treasury = Treasury()
        tx = treasury.create_transaction(
            data=b"transfer 100 USDC to 0x...",
            destination="0x...",
            amount_usd=100.0,
        )
        # tx contains the signed transaction with hybrid signature
    """

    def __init__(
        self,
        master_seed: Optional[bytes] = None,
        config_dir: str = DEFAULT_CONFIG_DIR,
        log_dir: str = DEFAULT_LOG_DIR,
        auto_setup: bool = True,
    ):
        self._master_seed = master_seed
        self._config_dir = config_dir
        self._log_dir = log_dir

        # State
        self._circuit_state = CIRCUIT_CLOSED
        self._circuit_triggered_at: Optional[str] = None
        self._transaction_count = 0
        self._tx_log: List[SignedTransaction] = []

        # Sub-modules
        self._signer = HybridSigner()
        self._address_gen = AddressGenerator(master_seed=master_seed)
        self._logger = InteractionLogger(log_dir=os.path.join(log_dir, "model-interactions"))

        if auto_setup:
            os.makedirs(config_dir, exist_ok=True)
            os.makedirs(os.path.join(log_dir, "transactions"), exist_ok=True)

        logger.info(
            f"Treasury initialized. PQC scheme: {self._signer.pqc_scheme}. "
            f"Circuit: {self._circuit_state}"
        )

    # -----------------------------------------------------------------------
    # Core Operations
    # -----------------------------------------------------------------------

    def sign_transaction_data(self, data: bytes, **metadata) -> HybridSignature:
        """
        Sign arbitrary transaction data with hybrid ECDSA + PQC.

        This is the core signing operation. All outbound transactions
        go through this method.
        """
        if self._circuit_state != CIRCUIT_CLOSED:
            raise RuntimeError(
                f"Circuit is {self._circuit_state}. "
                "Cannot sign transactions while circuit is open."
            )

        hybrid_sig = self._signer.sign(data, **metadata)
        self._transaction_count += 1

        logger.info(
            f"Signed transaction #{self._transaction_count}. "
            f"Payload hash: {hybrid_sig.payload_hash[:16]}..."
        )

        return hybrid_sig

    def create_transaction(
        self,
        data: bytes,
        destination: Optional[str] = None,
        amount_usd: float = 0.0,
        chain: str = "base",
        source_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SignedTransaction:
        """
        Create a fully signed transaction with fresh address.

        High-level API:
        1. Generate a fresh source address
        2. Sign the transaction data with hybrid signing
        3. Log the interaction
        4. Return the signed transaction
        """
        import uuid

        # Generate fresh source address if not provided
        if source_address is None:
            fresh = self._address_gen.generate_fresh_address()
            source_address = fresh.address

        # Sign
        sig = self.sign_transaction_data(
            data,
            source_address=source_address,
            destination=destination or "",
            chain=chain,
        )

        tx = SignedTransaction(
            transaction_data=data,
            hybrid_signature=sig,
            source_address=source_address,
            destination_address=destination,
            amount_usd=amount_usd,
            chain=chain,
            created_at=datetime.datetime.utcnow().isoformat(),
            id=uuid.uuid4().hex[:16],
        )

        self._tx_log.append(tx)
        self._log_transaction(tx)

        return tx

    def verify_transaction(
        self, tx: SignedTransaction
    ) -> Dict[str, Any]:
        """Verify a signed transaction's hybrid signature."""
        return self._signer.verify(tx.hybrid_signature, tx.transaction_data)

    def _log_transaction(self, tx: SignedTransaction) -> None:
        """Persist a signed transaction to disk."""
        try:
            tx_log_dir = os.path.join(self._log_dir, "transactions")
            os.makedirs(tx_log_dir, exist_ok=True)

            log_file = os.path.join(
                tx_log_dir,
                f"tx-{datetime.datetime.utcnow().strftime('%Y%m%d')}.jsonl",
            )
            with open(log_file, "a") as f:
                f.write(json.dumps(tx.to_dict(), sort_keys=True) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist transaction log: {e}")

    # -----------------------------------------------------------------------
    # Model Interaction Logging
    # -----------------------------------------------------------------------

    def log_model_interaction(
        self,
        prompt: str,
        completion: str,
        model_name: str = "unknown",
        model_version: str = "unknown",
        action_type: str = "sign",
        duration_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ModelInteraction:
        """Log a model interaction for audit trail."""
        return self._logger.log_interaction(
            prompt=prompt,
            completion=completion,
            model_name=model_name,
            model_version=model_version,
            agent_id="treasury",
            action_type=action_type,
            duration_ms=duration_ms,
            metadata=metadata,
        )

    def get_suspicious_interactions(
        self, limit: int = 50
    ) -> List[ModelInteraction]:
        """Get all suspicious model interactions."""
        return self._logger.suspicious_interactions(limit=limit)

    # -----------------------------------------------------------------------
    # Address Management
    # -----------------------------------------------------------------------

    def generate_address(self) -> FreshAddress:
        """Generate a fresh address for the next transaction."""
        return self._address_gen.generate_fresh_address()

    def peek_next_address(self) -> FreshAddress:
        """Preview the next address without consuming it."""
        return self._address_gen.peek_next()

    @property
    def addresses_used(self) -> int:
        return self._address_gen.used_count()

    # -----------------------------------------------------------------------
    # Key Management
    # -----------------------------------------------------------------------

    def rotate_ecdsa_key(self) -> None:
        """Rotate the ECDSA signing key."""
        self._signer.rotate_ecdsa_key()
        logger.info("ECDSA signing key rotated")

    # -----------------------------------------------------------------------
    # Quantum Emergency Circuit
    # -----------------------------------------------------------------------

    @property
    def circuit_state(self) -> str:
        """Current circuit breaker state."""
        return self._circuit_state

    def trigger_emergency(
        self, reason: str
    ) -> Dict[str, Any]:
        """
        Trigger the quantum emergency circuit.

        Returns an action plan for the emergency.
        """
        self._circuit_state = CIRCUIT_OPEN
        self._circuit_triggered_at = datetime.datetime.utcnow().isoformat()

        plan = {
            "state": self._circuit_state,
            "triggered_at": self._circuit_triggered_at,
            "reason": reason,
            "actions": [
                "Pause all outbound transactions",
                "Sweep funds to quantum-safe cold storage",
                "Rotate all signing keys",
                "Notify wallet owner",
                "Generate post-mortem report",
            ],
        }

        logger.warning(f"Emergency circuit triggered: {reason}")
        return plan

    def reset_circuit(self) -> None:
        """Reset the circuit breaker after emergency is resolved."""
        self._circuit_state = CIRCUIT_CLOSED
        self._circuit_triggered_at = None
        logger.info("Emergency circuit reset to normal operation")

    # -----------------------------------------------------------------------
    # Status
    # -----------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Get treasury status report."""
        return {
            "circuit_state": self._circuit_state,
            "transaction_count": self._transaction_count,
            "addresses_used": self._address_gen.used_count(),
            "pqc_scheme": self._signer.pqc_scheme,
            "hybrid_algorithm": HYBRID_ALGORITHM,
            "circuit_triggered_at": self._circuit_triggered_at,
            "config_dir": self._config_dir,
            "log_dir": self._log_dir,
        }
