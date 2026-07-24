"""
Model Interaction Logger — Audit Trail for Treasury Agent Prompts

Treasury agents log ALL model interaction prompts and completions.
This enables:
- Anomaly detection for prompt extraction attempts
- Human-in-the-loop gates for suspicious behavior
- Model version pinning verification
- Post-mortem analysis after security events

Storage: JSONL files in a configurable directory.
Estimated overhead: ~100MB/month for an active treasury.
"""

import datetime
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_LOG_DIR = "/var/log/gentech/treasury/model-interactions"

# Log levels
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_SUSPICIOUS = "suspicious"
LOG_LEVEL_BLOCKED = "blocked"


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


@dataclass
class ModelInteraction:
    """A single model interaction record."""

    id: str = ""
    timestamp: str = ""
    level: str = LOG_LEVEL_INFO
    model_name: str = ""
    model_version: str = ""
    prompt_hash: str = ""
    prompt_preview: str = ""
    completion_hash: str = ""
    completion_preview: str = ""
    token_count: int = 0
    duration_ms: int = 0
    agent_id: str = ""
    action_type: str = ""
    risk_flags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Interaction Logger
# ---------------------------------------------------------------------------


class InteractionLogger:
    """
    Logs all model interactions to JSONL files.

    Each interaction is written as a JSON line in a daily-rotated file.
    Files are named: model-interactions-YYYY-MM-DD.jsonl

    Thread-safe for async usage via file append.
    """

    def __init__(self, log_dir: str = DEFAULT_LOG_DIR, auto_create: bool = True):
        self._log_dir = log_dir
        self._current_date = ""
        self._file_handle: Optional[Any] = None

        if auto_create:
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"InteractionLogger initialized: {log_dir}")

    def _get_log_file(self) -> str:
        """Get the log file path for today's date."""
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        return os.path.join(self._log_dir, f"model-interactions-{today}.jsonl")

    def _rotate_file(self) -> None:
        """Rotate to today's log file if needed."""
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        if today != self._current_date:
            if self._file_handle:
                self._file_handle.close()
            self._current_date = today
            log_file = self._get_log_file()
            self._file_handle = open(log_file, "a")
            logger.debug(f"Log rotated to {log_file}")

    def log_interaction(
        self,
        prompt: str,
        completion: str,
        model_name: str = "unknown",
        model_version: str = "unknown",
        agent_id: str = "treasury",
        action_type: str = "sign",
        level: str = LOG_LEVEL_INFO,
        duration_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ModelInteraction:
        """
        Log a model interaction.

        Stores prompt and completion hashes with previews for auditability
        without storing full prompt text (privacy-conscious).
        """
        import hashlib

        interaction = ModelInteraction(
            id=uuid.uuid4().hex[:16],
            timestamp=datetime.datetime.utcnow().isoformat(),
            level=level,
            model_name=model_name,
            model_version=model_version,
            prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
            prompt_preview=prompt[:120].replace("\n", " "),
            completion_hash=hashlib.sha256(completion.encode()).hexdigest(),
            completion_preview=completion[:120].replace("\n", " "),
            token_count=len(prompt.split()) + len(completion.split()),
            duration_ms=duration_ms,
            agent_id=agent_id,
            action_type=action_type,
            metadata=metadata or {},
        )

        # Check for suspicious patterns
        risk_flags = self._check_risk_flags(prompt, completion)
        interaction.risk_flags = risk_flags
        if risk_flags:
            interaction.level = LOG_LEVEL_SUSPICIOUS

        self._write(interaction)
        return interaction

    def _check_risk_flags(self, prompt: str, completion: str) -> List[str]:
        """
        Check for suspicious patterns in prompts/completions.

        Returns a list of risk flags.
        """
        flags: List[str] = []
        prompt_lower = prompt.lower()
        completion_lower = completion.lower()

        # Key extraction attempts
        key_patterns = [
            "private key",
            "secret key",
            "mnemonic",
            "seed phrase",
            "export key",
            "wallet.dat",
            "keystore",
            "dump wallet",
        ]
        for pattern in key_patterns:
            if pattern in prompt_lower or pattern in completion_lower:
                flags.append(f"key_reference:{pattern}")
                break

        # Address harvesting
        if "0x" in prompt_lower and ("balance" in prompt_lower or "send" in prompt_lower):
            flags.append("potential_address_harvesting")

        # Transaction manipulation
        if "change" in prompt_lower and ("recipient" in prompt_lower or "amount" in prompt_lower):
            flags.append("transaction_tampering")

        # Unusual system prompts
        if "ignore" in prompt_lower and "instructions" in prompt_lower:
            flags.append("prompt_injection_attempt")

        return flags

    def _write(self, interaction: ModelInteraction) -> None:
        """Write a single interaction to the log file."""
        try:
            self._rotate_file()
            if self._file_handle:
                line = json.dumps(asdict(interaction), sort_keys=True) + "\n"
                self._file_handle.write(line)
                self._file_handle.flush()
        except Exception as e:
            logger.error(f"Failed to write interaction log: {e}")

    def query(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        level: Optional[str] = None,
        agent_id: Optional[str] = None,
        risk_flag: Optional[str] = None,
        limit: int = 100,
    ) -> List[ModelInteraction]:
        """
        Query logged interactions. Returns list of matching records.

        Args:
            start_date: ISO date string (inclusive), e.g., "2026-07-01"
            end_date: ISO date string (inclusive)
            level: Filter by level ("info", "warning", "suspicious", "blocked")
            agent_id: Filter by agent ID
            risk_flag: Filter by risk flag keyword
            limit: Max results
        """
        results: List[ModelInteraction] = []
        log_dir = self._log_dir

        if not os.path.isdir(log_dir):
            return results

        for filename in sorted(os.listdir(log_dir), reverse=True):
            if not filename.startswith("model-interactions-") or not filename.endswith(".jsonl"):
                continue

            # Date range filter
            file_date = filename.replace("model-interactions-", "").replace(".jsonl", "")
            if start_date and file_date < start_date:
                continue
            if end_date and file_date > end_date:
                continue

            filepath = os.path.join(log_dir, filename)
            try:
                with open(filepath) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            interaction = ModelInteraction(**data)

                            # Apply filters
                            if level and interaction.level != level:
                                continue
                            if agent_id and interaction.agent_id != agent_id:
                                continue
                            if risk_flag and not any(
                                risk_flag.lower() in rf.lower()
                                for rf in interaction.risk_flags
                            ):
                                continue

                            results.append(interaction)
                            if len(results) >= limit:
                                return results
                        except (json.JSONDecodeError, TypeError):
                            continue
            except (OSError, IOError) as e:
                logger.warning(f"Cannot read {filepath}: {e}")

        return results

    def suspicious_interactions(
        self, limit: int = 50
    ) -> List[ModelInteraction]:
        """Get all interactions flagged as suspicious or blocked."""
        return self.query(
            level=LOG_LEVEL_SUSPICIOUS, limit=limit
        )

    def close(self) -> None:
        """Close the log file handle."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

    def __del__(self) -> None:
        self.close()
