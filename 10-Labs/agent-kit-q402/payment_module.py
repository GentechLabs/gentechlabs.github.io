"""
Agent Kit × Q402 Payment Module

Wraps Q402's gasless payment infrastructure with Agent Kit policy enforcement
and audit trail. Agents can pay, get paid, and prove it — gaslessly.

Usage:
    from payment_module import AgentPayment

    payment = AgentPayment(config_path="config.yaml")
    
    # Single payment
    receipt = payment.pay(
        chain="base",
        token="USDC",
        to="0x...",
        amount=5.0,
        memo="API access fee"
    )
    
    # Batch payout
    receipts = payment.batch_pay(
        chain="base",
        token="USDC",
        recipients=[
            {"to": "0x...", "amount": 2.0, "memo": "Task 1"},
            {"to": "0x...", "amount": 3.0, "memo": "Task 2"},
        ]
    )
    
    # Check balance
    balance = payment.balance(chain="base", token="USDC")
    
    # Verify receipt
    verified = payment.verify_receipt(receipt_id="rct_...")
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class PaymentPolicy:
    """Spending limits and rules for agent payments."""
    daily_limit_usd: float = 100.0
    per_tx_limit_usd: float = 50.0
    approved_chains: list[str] = field(default_factory=lambda: [
        "base", "bnb", "ethereum", "arbitrum", "avalanche"
    ])
    approved_tokens: list[str] = field(default_factory=lambda: ["USDC", "USDT"])
    approved_recipients: list[str] = field(default_factory=list)  # empty = all allowed
    blocked_recipients: list[str] = field(default_factory=list)
    require_memo: bool = True
    auto_verify_receipts: bool = True


@dataclass
class PaymentRecord:
    """Record of a single payment transaction."""
    id: str
    timestamp: str
    chain: str
    token: str
    to: str
    amount: float
    memo: str
    receipt_id: Optional[str] = None
    receipt_verified: bool = False
    status: str = "pending"  # pending, settled, failed, blocked
    policy_check: dict = field(default_factory=dict)
    error: Optional[str] = None


class AgentPayment:
    """
    Agent Kit payment module backed by Q402.
    
    This module does NOT directly call Q402 APIs. Instead, it provides
    the policy enforcement and audit layer that wraps Q402 MCP tool calls.
    
    The actual Q402 calls are made by the Hermes agent via MCP tools:
    - q402_pay
    - q402_batch_pay
    - q402_balance
    - q402_verify_receipt
    - q402_aave_deposit
    - q402_ccip_bridge
    - q402_schedule
    
    This module:
    1. Validates payments against policy BEFORE the agent calls Q402
    2. Logs every payment attempt (approved or blocked)
    3. Records Trust Receipts after settlement
    4. Provides daily spending tracking
    5. Enforces limits without trusted intermediaries
    """
    
    def __init__(self, config_path: Optional[str] = None, policy: Optional[PaymentPolicy] = None):
        self.policy = policy or PaymentPolicy()
        self.audit_dir = Path(os.environ.get(
            "AGENT_KIT_AUDIT_DIR",
            os.path.expanduser("~/.hermes/profiles/gentech/audit/payments")
        ))
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.daily_log = self.audit_dir / f"payments-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
        self._load_daily_totals()
        
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, path: str):
        """Load payment policy from YAML config."""
        try:
            import yaml
            with open(path) as f:
                cfg = yaml.safe_load(f)
            if "policy" in cfg:
                p = cfg["policy"]
                self.policy.daily_limit_usd = p.get("daily_limit_usd", self.policy.daily_limit_usd)
                self.policy.per_tx_limit_usd = p.get("per_tx_limit_usd", self.policy.per_tx_limit_usd)
                self.policy.approved_chains = p.get("approved_chains", self.policy.approved_chains)
                self.policy.approved_tokens = p.get("approved_tokens", self.policy.approved_tokens)
                self.policy.approved_recipients = p.get("approved_recipients", self.policy.approved_recipients)
                self.policy.blocked_recipients = p.get("blocked_recipients", self.policy.blocked_recipients)
                self.policy.require_memo = p.get("require_memo", self.policy.require_memo)
                self.policy.auto_verify_receipts = p.get("auto_verify_receipts", self.policy.auto_verify_receipts)
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
    
    def _load_daily_totals(self):
        """Load today's spending totals from audit log."""
        self.daily_total = 0.0
        self.tx_count = 0
        if self.daily_log.exists():
            with open(self.daily_log) as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get("status") == "settled":
                            self.daily_total += record.get("amount", 0)
                            self.tx_count += 1
                    except json.JSONDecodeError:
                        continue
    
    def _check_policy(self, chain: str, token: str, to: str, amount: float, memo: str) -> dict:
        """Validate payment against policy. Returns {approved: bool, reason: str}."""
        checks = []
        
        # Chain check
        if chain not in self.policy.approved_chains:
            return {"approved": False, "reason": f"Chain '{chain}' not in approved list: {self.policy.approved_chains}"}
        
        # Token check
        if token not in self.policy.approved_tokens:
            return {"approved": False, "reason": f"Token '{token}' not in approved list: {self.policy.approved_tokens}"}
        
        # Per-tx limit
        if amount > self.policy.per_tx_limit_usd:
            return {"approved": False, "reason": f"Amount ${amount} exceeds per-tx limit ${self.policy.per_tx_limit_usd}"}
        
        # Daily limit
        if self.daily_total + amount > self.policy.daily_limit_usd:
            remaining = self.policy.daily_limit_usd - self.daily_total
            return {"approved": False, "reason": f"Would exceed daily limit. Spent: ${self.daily_total:.2f}, requested: ${amount}, remaining: ${remaining:.2f}"}
        
        # Memo check
        if self.policy.require_memo and not memo:
            return {"approved": False, "reason": "Memo required but not provided"}
        
        # Blocked recipients
        if to.lower() in [r.lower() for r in self.policy.blocked_recipients]:
            return {"approved": False, "reason": f"Recipient {to} is blocked"}
        
        # Approved recipients (if list is non-empty, only these are allowed)
        if self.policy.approved_recipients and to.lower() not in [r.lower() for r in self.policy.approved_recipients]:
            return {"approved": False, "reason": f"Recipient {to} not in approved list"}
        
        return {"approved": True, "reason": "All checks passed"}
    
    def _log_payment(self, record: PaymentRecord):
        """Append payment record to daily audit log."""
        with open(self.daily_log, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")
    
    def _generate_id(self) -> str:
        """Generate a unique payment ID."""
        return f"pay_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
    
    def validate(self, chain: str, token: str, to: str, amount: float, memo: str = "") -> dict:
        """
        Validate a payment against policy WITHOUT executing it.
        Returns the policy check result.
        
        Use this before calling q402_pay via MCP to ensure the payment will be approved.
        """
        return self._check_policy(chain, token, to, amount, memo)
    
    def record_attempt(self, chain: str, token: str, to: str, amount: float, 
                       memo: str = "", status: str = "pending", receipt_id: str = "",
                       error: str = "") -> PaymentRecord:
        """
        Record a payment attempt to the audit trail.
        
        Call this AFTER the agent attempts the Q402 MCP tool call.
        Status should be: "settled", "failed", or "blocked"
        """
        policy_check = self._check_policy(chain, token, to, amount, memo)
        
        record = PaymentRecord(
            id=self._generate_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            chain=chain,
            token=token,
            to=to,
            amount=amount,
            memo=memo,
            receipt_id=receipt_id,
            status=status,
            policy_check=policy_check,
            error=error,
        )
        
        self._log_payment(record)
        
        if status == "settled":
            self.daily_total += amount
            self.tx_count += 1
        
        return record
    
    def get_daily_summary(self) -> dict:
        """Get today's spending summary."""
        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "total_spent": self.daily_total,
            "daily_limit": self.policy.daily_limit_usd,
            "remaining": self.policy.daily_limit_usd - self.daily_total,
            "tx_count": self.tx_count,
            "limit Utilization": f"{(self.daily_total / self.policy.daily_limit_usd * 100):.1f}%"
        }
    
    def get_payment_history(self, limit: int = 20) -> list[dict]:
        """Get recent payment records."""
        records = []
        if self.daily_log.exists():
            with open(self.daily_log) as f:
                for line in f:
                    try:
                        records.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        return records[-limit:]
    
    def format_pay_command(self, chain: str, token: str, to: str, amount: float, memo: str = "") -> str:
        """
        Format a Q402 MCP tool call for the agent to execute.
        
        Returns a string the agent can use as a prompt:
        "Call q402_pay with chain=base, token=USDC, to=0x..., amount=5, memo=..."
        """
        return (
            f'q402_pay({{ chain:"{chain}", token:"{token}", '
            f'to:"{to}", amount:"{amount}", memo:"{memo}" }})'
        )
    
    def format_batch_command(self, chain: str, token: str, recipients: list[dict]) -> str:
        """Format a Q402 batch payment command."""
        rows = json.dumps(recipients)
        return f'q402_batch_pay({{ chain:"{chain}", token:"{token}", recipients:{rows} }})'


# === Convenience functions for direct use ===

def create_payment(config_path: str = None) -> AgentPayment:
    """Create an AgentPayment instance with default or custom config."""
    return AgentPayment(config_path=config_path)


def quick_pay(chain: str, token: str, to: str, amount: float, memo: str = "") -> dict:
    """
    Quick payment validation + command formatting.
    Returns {valid: bool, command: str, reason: str}
    """
    payment = AgentPayment()
    check = payment.validate(chain, token, to, amount, memo)
    
    if check["approved"]:
        cmd = payment.format_pay_command(chain, token, to, amount, memo)
        return {"valid": True, "command": cmd, "reason": check["reason"]}
    else:
        return {"valid": False, "command": None, "reason": check["reason"]}
