"""
Agent Kit × Q402 Audit Trail

Connects Trust Receipts to the audit log. After Q402 settles a payment,
this module:
1. Verifies the receipt format and structure
2. Links it to the original payment record
3. Creates an immutable audit entry (append-only JSONL)
4. Provides query API for compliance and reporting

Architecture:
    Q402 Settlement → Trust Receipt → Audit Trail → Compliance Query
                              ↕
                     Receipt Verification
                     Payment Linking
                     Immutable Log

Usage:
    from audit_trail import AuditTrail

    trail = AuditTrail()

    # Record a settlement with receipt
    entry = trail.record_settlement(
        payment_id="pay_...",
        receipt_id="rct_...",
        receipt_data={"chain": "base", "amount": 5.0, "tx_hash": "0x..."},
        chain="base",
        amount=5.0,
        payer="0x1234",
        provider="0x5678",
        endpoint="/v1/score"
    )

    # Query audit entries
    entries = trail.query(payer="0x1234")
    entries = trail.query(date="2026-06-21")
    entries = trail.query(endpoint="/v1/score")
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class AuditEntry:
    """Immutable audit record for a settled payment."""
    id: str
    timestamp: str
    payment_id: str
    receipt_id: str
    receipt_data: dict
    chain: str
    amount: float
    token: str
    payer: str
    provider: str
    endpoint: str
    memo: str = ""
    receipt_verified: bool = False
    receipt_format_valid: bool = False
    receipt_warnings: list[str] = field(default_factory=list)
    status: str = "recorded"  # recorded, verified, flagged, disputed


class AuditTrail:
    """
    Append-only audit trail for Q402 payment settlements.

    Every settled payment gets an immutable entry that links:
    - Original payment attempt (payment_id)
    - Q402 Trust Receipt (receipt_id + receipt_data)
    - Settlement details (chain, amount, addresses)
    - Verification status

    The trail is append-only — entries are never modified after creation.
    Disputes and flags are added as new entries that reference the original.
    """

    def __init__(self, audit_dir: Optional[str] = None):
        self.audit_dir = Path(audit_dir or os.environ.get(
            "AGENT_KIT_AUDIT_DIR",
            os.path.expanduser("~/.hermes/profiles/gentech/audit/trail")
        ))
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.trail_file = self.audit_dir / "settlements.jsonl"
        self._stats_file = self.audit_dir / "trail_stats.json"

    def _generate_id(self) -> str:
        """Generate unique audit entry ID."""
        return f"aud_{int(time.time() * 1000)}_{os.urandom(4).hex()}"

    def _validate_receipt(self, receipt_data: dict) -> tuple[bool, list[str]]:
        """
        Validate receipt structure and data.
        Returns (is_valid, warnings).
        """
        warnings = []
        valid = True

        # Required fields
        required_fields = ["chain", "amount"]
        for field_name in required_fields:
            if field_name not in receipt_data:
                warnings.append(f"Missing required field: {field_name}")
                valid = False

        # Amount validation
        amount = receipt_data.get("amount")
        if amount is not None:
            if not isinstance(amount, (int, float)):
                warnings.append(f"Amount is not numeric: {amount}")
                valid = False
            elif amount <= 0:
                warnings.append(f"Amount is non-positive: {amount}")
                valid = False

        # Chain validation
        valid_chains = {"base", "bnb", "ethereum", "arbitrum", "avalanche",
                        "optimism", "polygon", "solana"}
        chain = receipt_data.get("chain")
        if chain and chain.lower() not in valid_chains:
            warnings.append(f"Unknown chain: {chain}")

        # Address validation (if present)
        for addr_field in ["payer", "provider", "to"]:
            addr = receipt_data.get(addr_field)
            if addr:
                if not addr.startswith("0x") or len(addr) != 42:
                    warnings.append(f"Invalid address format for {addr_field}: {addr}")
                    valid = False

        # Tx hash validation (if present)
        tx_hash = receipt_data.get("tx_hash")
        if tx_hash:
            if not tx_hash.startswith("0x") or len(tx_hash) < 66:
                warnings.append(f"Invalid tx_hash format: {tx_hash[:20]}...")
                valid = False

        return valid, warnings

    def record_settlement(
        self,
        payment_id: str,
        receipt_id: str,
        receipt_data: dict,
        chain: str,
        amount: float,
        payer: str,
        provider: str,
        endpoint: str,
        token: str = "USDC",
        memo: str = "",
    ) -> AuditEntry:
        """
        Record a settled payment to the audit trail.

        This is called after Q402 confirms settlement. The receipt is
        validated, linked to the payment, and logged immutably.
        """
        # Validate receipt
        receipt_valid, warnings = self._validate_receipt(receipt_data)

        # Create audit entry
        entry = AuditEntry(
            id=self._generate_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            payment_id=payment_id,
            receipt_id=receipt_id,
            receipt_data=receipt_data,
            chain=chain,
            amount=amount,
            token=token,
            payer=payer,
            provider=provider,
            endpoint=endpoint,
            memo=memo,
            receipt_verified=receipt_valid,
            receipt_format_valid=receipt_valid,
            receipt_warnings=warnings,
            status="verified" if receipt_valid else "flagged",
        )

        # Append to trail (immutable — append only)
        with open(self.trail_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

        # Update stats
        self._update_stats(entry)

        return entry

    def record_flag(
        self,
        original_entry_id: str,
        flag_reason: str,
        flagged_by: str = "system",
    ) -> AuditEntry:
        """
        Flag an existing audit entry for review.
        Creates a new entry that references the original.
        """
        entry = AuditEntry(
            id=self._generate_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            payment_id=f"ref:{original_entry_id}",
            receipt_id="",
            receipt_data={"flag": flag_reason, "flagged_by": flagged_by},
            chain="",
            amount=0.0,
            token="",
            payer="",
            provider="",
            endpoint="",
            memo=f"FLAG for {original_entry_id}: {flag_reason}",
            status="flagged",
        )

        with open(self.trail_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

        return entry

    def query(
        self,
        payer: Optional[str] = None,
        provider: Optional[str] = None,
        endpoint: Optional[str] = None,
        date: Optional[str] = None,
        status: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        Query audit entries with filters.
        Returns most recent entries first.
        """
        if not self.trail_file.exists():
            return []

        results = []
        with open(self.trail_file) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                # Apply filters
                if payer and entry.get("payer", "").lower() != payer.lower():
                    continue
                if provider and entry.get("provider", "").lower() != provider.lower():
                    continue
                if endpoint and entry.get("endpoint") != endpoint:
                    continue
                if date and entry.get("timestamp", "")[:10] != date:
                    continue
                if status and entry.get("status") != status:
                    continue
                if min_amount is not None and entry.get("amount", 0) < min_amount:
                    continue
                if max_amount is not None and entry.get("amount", 0) > max_amount:
                    continue

                results.append(entry)

        # Most recent first
        results.reverse()
        return results[:limit]

    def get_receipt_status(self, receipt_id: str) -> Optional[dict]:
        """
        Check if a receipt has been recorded in the audit trail.
        Returns the entry if found, None otherwise.
        """
        if not self.trail_file.exists():
            return None

        with open(self.trail_file) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("receipt_id") == receipt_id:
                        return entry
                except json.JSONDecodeError:
                    continue
        return None

    def get_daily_summary(self, date: Optional[str] = None) -> dict:
        """
        Get summary stats for a given day (defaults to today).
        """
        target_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entries = self.query(date=target_date, limit=10000)

        total_amount = sum(e.get("amount", 0) for e in entries)
        verified = sum(1 for e in entries if e.get("status") == "verified")
        flagged = sum(1 for e in entries if e.get("status") == "flagged")
        unique_payers = len(set(e.get("payer") for e in entries if e.get("payer")))
        unique_providers = len(set(e.get("provider") for e in entries if e.get("provider")))

        return {
            "date": target_date,
            "total_settlements": len(entries),
            "total_amount_usd": total_amount,
            "verified": verified,
            "flagged": flagged,
            "unique_payers": unique_payers,
            "unique_providers": unique_providers,
        }

    def _update_stats(self, entry: AuditEntry):
        """Update cumulative stats."""
        stats = self._load_stats()
        stats["total_entries"] = stats.get("total_entries", 0) + 1
        stats["total_amount_usd"] = stats.get("total_amount_usd", 0) + entry.amount
        stats["last_entry_timestamp"] = entry.timestamp
        stats["last_receipt_id"] = entry.receipt_id
        self._save_stats(stats)

    def _load_stats(self) -> dict:
        if self._stats_file.exists():
            with open(self._stats_file) as f:
                return json.load(f)
        return {
            "total_entries": 0,
            "total_amount_usd": 0.0,
            "created": datetime.now(timezone.utc).isoformat(),
        }

    def _save_stats(self, stats: dict):
        with open(self._stats_file, "w") as f:
            json.dump(stats, f, indent=2)
