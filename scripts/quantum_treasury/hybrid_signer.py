"""
Hybrid Signer — Dual ECDSA + SPHINCS+ Signatures

Every treasury transaction uses dual signatures:
- ECDSA (secp256k1) — current standard, available today
- SPHINCS+ (NIST standardized) — quantum-safe, stateless

A transaction is valid only if BOTH signatures verify.
When ECDSA becomes unsafe, drop ECDSA verification — PQC sigs are already there.

Uses `cryptography` for ECDSA and `oqs` (liboqs-python) for SPHINCS+.
Falls back to pure-Python hash-based signature (Winternitz OTS) when liboqs
is unavailable, so development and testing can proceed without C compilation.
"""

import hashlib
import json
import logging
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA,
    EllipticCurvePrivateKey,
    EllipticCurvePublicKey,
    SECP256K1,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HYBRID_ALGORITHM = "hybrid-ecdsa-sphincsplus-v1"
PQC_VARIANT_DEFAULT = "SLH_DSA_PURE_SHA2_128S"
ECDSA_CURVE = "secp256k1"

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


@dataclass
class HybridSignature:
    """A hybrid ECDSA + SPHINCS+ signature."""

    algorithm: str = HYBRID_ALGORITHM
    payload_hash: str = ""
    ecdsa_signature: str = ""
    ecdsa_public_key: str = ""
    sphincs_signature: str = ""
    sphincs_public_key: str = ""
    sphincs_variant: str = PQC_VARIANT_DEFAULT
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "payload_hash": self.payload_hash,
            "ecdsa_signature": self.ecdsa_signature,
            "ecdsa_public_key": self.ecdsa_public_key,
            "sphincs_signature": self.sphincs_signature,
            "sphincs_public_key": self.sphincs_public_key,
            "sphincs_variant": self.sphincs_variant,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HybridSignature":
        return cls(
            algorithm=data.get("algorithm", HYBRID_ALGORITHM),
            payload_hash=data.get("payload_hash", ""),
            ecdsa_signature=data.get("ecdsa_signature", ""),
            ecdsa_public_key=data.get("ecdsa_public_key", ""),
            sphincs_signature=data.get("sphincs_signature", ""),
            sphincs_public_key=data.get("sphincs_public_key", ""),
            sphincs_variant=data.get("sphincs_variant", PQC_VARIANT_DEFAULT),
            metadata=data.get("metadata", {}),
        )

    def serialize(self) -> str:
        """Serialize to JSON string for storage or transmission."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def deserialize(cls, data: str) -> "HybridSignature":
        """Load from JSON string."""
        return cls.from_dict(json.loads(data))


# ---------------------------------------------------------------------------
# Abstract Signer
# ---------------------------------------------------------------------------


class PqcSigner(ABC):
    """Abstract interface for post-quantum signature schemes."""

    @abstractmethod
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate (secret_key, public_key) pair."""

    @abstractmethod
    def sign(self, secret_key: bytes, message: bytes) -> bytes:
        """Sign a message, return signature bytes."""

    @abstractmethod
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify a signature. Return True if valid."""

    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the scheme."""


# ---------------------------------------------------------------------------
# SPHINCS+ via liboqs
# ---------------------------------------------------------------------------


class OqsSphincsPlusSigner(PqcSigner):
    """SPHINCS+ via liboqs-python (oqs module). Compiles C lib on first use."""

    def __init__(self, variant: str = PQC_VARIANT_DEFAULT):
        self._variant = variant
        self._available = self._check()
        self._signer_ref: Optional[Any] = None
        self._current_public_key: Optional[bytes] = None
        if not self._available:
            logger.warning(
                "liboqs not available, SPHINCS+ signing disabled. "
                "Install liboqs-python or use PurePythonSigner fallback."
            )

    def _check(self) -> bool:
        try:
            import oqs  # noqa: F401
            return True
        except ImportError:
            return False

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        if not self._available:
            raise RuntimeError("liboqs not available")
        import oqs
        self._signer_ref = oqs.Signature(self._variant)
        public_key = self._signer_ref.generate_keypair()
        self._current_public_key = public_key
        # oqs stores the secret key internally in the Signature object
        # We return an empty bytes as placeholder since the key is in the object
        return b"", public_key

    def sign(self, secret_key: bytes, message: bytes) -> bytes:
        if not self._available:
            raise RuntimeError("liboqs not available")
        if self._signer_ref is None:
            # No keypair generated yet — auto-generate
            self.generate_keypair()
        return self._signer_ref.sign(message)

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        if not self._available:
            raise RuntimeError("liboqs not available")
        import oqs
        try:
            verifier = oqs.Signature(self._variant)
            return verifier.verify(message, signature, public_key)
        except Exception:
            return False

    def name(self) -> str:
        return f"SPHINCS+ ({self._variant})"


# ---------------------------------------------------------------------------
# Pure-Python Winternitz OTS (for dev/testing without liboqs)
# ---------------------------------------------------------------------------


class PurePythonWinternitzSigner(PqcSigner):
    """
    Pure-Python Winternitz One-Time Signature (WOTS).

    This is a SIMPLIFIED implementation for development and testing.
    NOT production-ready — use SPHINCS+ via liboqs for real signing.

    Security level: ~128 bits (SHA-256 based)
    Signature size: ~2KB (chain of hashes)
    """

    WINTERS = 16
    CHAINS = 36  # 32 message chains + 4 checksum chains

    def __init__(self):
        self._name = "Winternitz-OTS (SHA-256, w=16)"

    def _checksum(self, msg_hash: bytes) -> int:
        """Compute checksum over the message hash blocks."""
        total = 0
        for b in msg_hash:
            total += (self.WINTERS - 1) - (b % self.WINTERS)
        return total

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate a WOTS keypair. Secret key = 36 random 32-byte chains."""
        secret_key = secrets.token_bytes(self.CHAINS * 32)
        # Public key = hash each chain end
        public_key = b""
        for i in range(self.CHAINS):
            chain_start = secret_key[i * 32 : (i + 1) * 32]
            # Apply full chain (WINTERS-1 hashes)
            current = chain_start
            for _ in range(self.WINTERS - 1):
                current = hashlib.sha256(current).digest()
            public_key += current
        return secret_key, public_key

    def sign(self, secret_key: bytes, message: bytes) -> bytes:
        """Sign a message using Winternitz OTS."""
        msg_hash = hashlib.sha256(message).digest()
        checksum_val = self._checksum(msg_hash)
        signature = b""

        for i in range(32):
            chain_start = secret_key[i * 32 : (i + 1) * 32]
            value = msg_hash[i] % self.WINTERS
            current = chain_start
            for _ in range(value):
                current = hashlib.sha256(current).digest()
            signature += current

        # Append checksum chain
        checksum_bytes = checksum_val.to_bytes(4, "big")
        for i in range(4):
            chain_start = secret_key[(32 + i) * 32 : (33 + i) * 32]
            value = checksum_bytes[i] % self.WINTERS
            current = chain_start
            for _ in range(value):
                current = hashlib.sha256(current).digest()
            signature += current

        return signature

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify a WOTS signature."""
        if len(signature) != self.CHAINS * 32:
            return False
        msg_hash = hashlib.sha256(message).digest()
        checksum_val = self._checksum(msg_hash)

        # Re-derive public key from signature
        derived_pk = b""
        for i in range(32):
            value = msg_hash[i] % self.WINTERS
            steps = (self.WINTERS - 1) - value
            current = signature[i * 32 : (i + 1) * 32]
            for _ in range(steps):
                current = hashlib.sha256(current).digest()
            derived_pk += current

        checksum_bytes = checksum_val.to_bytes(4, "big")
        for i in range(4):
            value = checksum_bytes[i] % self.WINTERS
            steps = (self.WINTERS - 1) - value
            current = signature[(32 + i) * 32 : (33 + i) * 32]
            for _ in range(steps):
                current = hashlib.sha256(current).digest()
            derived_pk += current

        return derived_pk == public_key

    def name(self) -> str:
        return self._name


# ---------------------------------------------------------------------------
# Hybrid Signer — Orchestrator
# ---------------------------------------------------------------------------


class HybridSigner:
    """
    Orchestrates hybrid ECDSA + PQC signing.

    Uses ECDSA (secp256k1 via cryptography) as the current standard.
    Uses SPHINCS+ (via liboqs if available, pure Python fallback) as the
    quantum-safe layer.

    A transaction is valid only if BOTH signatures verify.
    """

    def __init__(
        self,
        pqc_signer: Optional[PqcSigner] = None,
        ecdsa_private_key: Optional[EllipticCurvePrivateKey] = None,
    ):
        self._pqc_signer = pqc_signer or self._default_pqc_signer()
        self._ecdsa_private_key = ecdsa_private_key or ec.generate_private_key(SECP256K1())
        self._ecdsa_public_key = self._ecdsa_private_key.public_key()

    @staticmethod
    def _default_pqc_signer() -> PqcSigner:
        """Select best available PQC signer."""
        try:
            import oqs
            # Check if SPHINCS+/SLH-DSA is actually available (liboqs may be
            # installed but the C library not yet compiled)
            enabled = oqs.get_enabled_sig_mechanisms()
            sphincs_available = any(
                "SPHINCS" in m.upper() or "SLH_DSA" in m.upper()
                for m in enabled
            )
            if sphincs_available:
                return OqsSphincsPlusSigner()
            logger.info(
                "liboqs installed but SPHINCS+ not yet compiled, "
                "using pure Python WOTS fallback"
            )
        except ImportError:
            logger.info("liboqs not available, using pure Python WOTS fallback")
        return PurePythonWinternitzSigner()

    def generate_ecdsa_keypair(self) -> Tuple[EllipticCurvePrivateKey, EllipticCurvePublicKey]:
        """Generate a fresh ECDSA keypair for one-time use."""
        private_key = ec.generate_private_key(SECP256K1())
        return private_key, private_key.public_key()

    def _hash_payload(self, payload: bytes) -> bytes:
        """Hash the payload with SHA-256."""
        return hashlib.sha256(payload).digest()

    def sign(self, payload: bytes, **metadata) -> HybridSignature:
        """
        Sign a payload with both ECDSA and PQC.

        Returns a HybridSignature containing both signatures and public keys.
        """
        payload_hash = self._hash_payload(payload)
        payload_hash_hex = payload_hash.hex()

        # ECDSA signature
        ecdsa_sig = self._ecdsa_private_key.sign(payload_hash, ECDSA(hashes.SHA256()))
        ecdsa_pub_bytes = self._ecdsa_public_key.public_bytes(
            Encoding.X962, PublicFormat.UncompressedPoint
        )
        ecdsa_sig_bytes = ecdsa_sig

        # PQC signature
        pqc_secret, pqc_public = self._pqc_signer.generate_keypair()
        pqc_sig = self._pqc_signer.sign(pqc_secret, payload_hash)

        return HybridSignature(
            payload_hash=payload_hash_hex,
            ecdsa_signature=ecdsa_sig_bytes.hex(),
            ecdsa_public_key=ecdsa_pub_bytes.hex(),
            sphincs_signature=pqc_sig.hex(),
            sphincs_public_key=pqc_public.hex(),
            sphincs_variant=self._pqc_signer.name(),
            metadata=metadata,
        )

    def verify(self, hybrid_sig: HybridSignature, original_payload: bytes) -> Dict[str, Any]:
        """
        Verify a hybrid signature against the original payload.

        Returns a dict: {
            "valid": bool,
            "ecdsa_valid": bool,
            "pqc_valid": bool,
            "errors": [str, ...]
        }
        """
        result = {
            "valid": False,
            "ecdsa_valid": False,
            "pqc_valid": False,
            "errors": [],
        }

        # Hash the original payload
        payload_hash = self._hash_payload(original_payload)
        expected_hash_hex = payload_hash.hex()

        # Verify payload hash match
        if hybrid_sig.payload_hash != expected_hash_hex:
            result["errors"].append(
                f"Payload hash mismatch: expected {expected_hash_hex}, "
                f"got {hybrid_sig.payload_hash}"
            )
            return result

        # Verify ECDSA signature
        try:
            ecdsa_pub_bytes = bytes.fromhex(hybrid_sig.ecdsa_public_key)
            ecdsa_pub = ec.EllipticCurvePublicKey.from_encoded_point(SECP256K1(), ecdsa_pub_bytes)
            ecdsa_sig_der = bytes.fromhex(hybrid_sig.ecdsa_signature)
            ecdsa_pub.verify(ecdsa_sig_der, payload_hash, ECDSA(hashes.SHA256()))
            result["ecdsa_valid"] = True
        except Exception as e:
            result["errors"].append(f"ECDSA verification failed: {e}")

        # Verify PQC signature
        try:
            pqc_pub = bytes.fromhex(hybrid_sig.sphincs_public_key)
            pqc_sig = bytes.fromhex(hybrid_sig.sphincs_signature)
            pqc_valid = self._pqc_signer.verify(pqc_pub, payload_hash, pqc_sig)
            result["pqc_valid"] = pqc_valid
            if not pqc_valid:
                result["errors"].append("PQC verification returned False")
        except Exception as e:
            result["errors"].append(f"PQC verification exception: {e}")

        # Both must be valid
        result["valid"] = result["ecdsa_valid"] and result["pqc_valid"]
        return result

    def rotate_ecdsa_key(self) -> Tuple[EllipticCurvePrivateKey, EllipticCurvePublicKey]:
        """Rotate to a fresh ECDSA keypair. Returns (new_private, new_public)."""
        self._ecdsa_private_key = ec.generate_private_key(SECP256K1())
        self._ecdsa_public_key = self._ecdsa_private_key.public_key()
        return self._ecdsa_private_key, self._ecdsa_public_key

    @property
    def pqc_scheme(self) -> str:
        return self._pqc_signer.name()
