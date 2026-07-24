"""
Fresh Address Generator — One-Shot Address Per Transaction

Inspired by Taproot's key-spend path mitigation:
- No address is used more than once
- Each outbound transaction uses a fresh address
- Change addresses are swept to cold storage

Uses BIP32 hierarchical derivation from a master seed to generate
deterministic but unique addresses. Compatible with Ethereum-style
addresses (0x...) and can be extended for other chains.

Each address is derived from:
    derivation_path = "m/44'/60'/0'/0/{account_index}"
    where account_index increments for each transaction.

The master seed is stored securely in the treasury config (not in code).
"""

import hashlib
import hmac
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

from cryptography.hazmat.primitives import hashes as crypto_hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import (
    EllipticCurvePrivateKey,
    EllipticCurvePublicKey,
    SECP256K1,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# BIP32 secp256k1 curve order
CURVE_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Ethereum address prefix
ETH_ADDRESS_PREFIX = "0x"


# ---------------------------------------------------------------------------
# BIP32-like Key Derivation
# ---------------------------------------------------------------------------


def _derive_child_key(
    parent_key: bytes, parent_chain: bytes, index: int
) -> Tuple[bytes, bytes]:
    """
    Derive a child key using CKD (Child Key Derivation) similar to BIP32.
    Uses HMAC-SHA512 for the derivation.

    Returns (child_private_key_bytes, child_chain_code_bytes).
    """
    # Hardened derivation (index >= 0x80000000)
    # Data = 0x00 || parent_key || index (4 bytes big-endian)
    data = b"\x00" + parent_key + index.to_bytes(4, "big")
    hmac_result = hmac.digest(parent_chain, data, "sha512")
    child_key_bytes = hmac_result[:32]
    child_chain = hmac_result[32:]

    # Add parent key to derived key (mod curve order)
    parent_int = int.from_bytes(parent_key, "big")
    child_int = int.from_bytes(child_key_bytes, "big")
    full_int = (parent_int + child_int) % CURVE_ORDER
    full_key = full_int.to_bytes(32, "big")

    # Derive new chain code
    return full_key, child_chain


# ---------------------------------------------------------------------------
# Address Generator
# ---------------------------------------------------------------------------


@dataclass
class FreshAddress:
    """A freshly generated address and its associated data."""

    address: str
    public_key_hex: str
    account_index: int
    derivation_path: str


class AddressGenerator:
    """
    Generates fresh Ethereum-style addresses for each outbound transaction.

    Uses BIP32-like hierarchical derivation from a master seed.
    Each address is used at most once.

    If no master_seed is provided, generates a random one.
    """

    def __init__(self, master_seed: Optional[bytes] = None, start_index: int = 0):
        self._master_seed = master_seed or self._generate_seed()
        self._account_index = start_index

        # Derive the master key and chain code
        # First, create the master node from seed using HMAC-SHA512
        # BIP32: master_key = HMAC-SHA512("Bitcoin seed", seed)
        hmac_result = hmac.digest(b"Bitcoin seed", self._master_seed, "sha512")
        self._master_key = hmac_result[:32]
        self._master_chain = hmac_result[32:]

        logger.info(
            f"AddressGenerator initialized with master seed "
            f"(first 4 bytes: {self._master_seed[:4].hex()}...) "
            f"starting at index {start_index}"
        )

    @staticmethod
    def _generate_seed() -> bytes:
        """Generate a random 32-byte master seed."""
        import secrets
        return secrets.token_bytes(32)

    def _derive_ethereum_address(self, private_key_bytes: bytes) -> str:
        """
        Derive an Ethereum-style address from a private key.
        Ethereum address = last 20 bytes of keccak256(public_key).

        Using SHA-256 as a stand-in where keccak256 is not available.
        For production, use eth-keys or web3.py.
        """
        # Create EC private key from bytes
        private_key = ec.derive_private_key(
            int.from_bytes(private_key_bytes, "big"), SECP256K1()
        )
        public_key = private_key.public_key()
        pub_bytes = public_key.public_bytes(
            Encoding.X962, PublicFormat.UncompressedPoint
        )

        # Strip the 0x04 prefix (uncompressed point indicator)
        pub_key_raw = pub_bytes[1:]

        # Hash to get address (SHA-256 as stand-in for keccak256)
        # For production, replace with keccak256 from eth_hash or web3
        address_hash = hashlib.sha256(pub_key_raw).digest()
        address = ETH_ADDRESS_PREFIX + address_hash[-20:].hex()

        return address

    def generate_fresh_address(self) -> FreshAddress:
        """
        Generate the next fresh address, incrementing the internal counter.
        """
        index = self._account_index
        self._account_index += 1

        # Derive the key for this index
        # BIP44 path: m/44'/60'/0'/0/{index}
        # We simplify to a single hardened derivation step
        key, _ = _derive_child_key(self._master_key, self._master_chain, index)

        address = self._derive_ethereum_address(key)
        public_key_hex = key.hex()[:64]  # first 32 bytes as pub key identifier

        derivation_path = f"m/44'/60'/0'/0/{index}"

        return FreshAddress(
            address=address,
            public_key_hex=public_key_hex,
            account_index=index,
            derivation_path=derivation_path,
        )

    @property
    def current_index(self) -> int:
        return self._account_index

    def peek_next(self) -> FreshAddress:
        """
        Preview the next address without consuming it.
        Useful for pre-announcing an address before use.
        """
        # Temporarily save state
        saved_index = self._account_index
        address = self.generate_fresh_address()
        # Restore state
        self._account_index = saved_index
        return address

    def set_index(self, index: int) -> None:
        """Set the account index (e.g., after recovering from backup)."""
        if index < 0:
            raise ValueError("Index must be non-negative")
        self._account_index = index
        logger.info(f"AddressGenerator index set to {index}")

    def used_count(self) -> int:
        """Number of addresses that have been generated (consumed)."""
        return self._account_index
