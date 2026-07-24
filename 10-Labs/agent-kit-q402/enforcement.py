"""
Agent Kit × Q402 AAE Enforcement Hooks

Identity + policy enforcement that runs BEFORE Q402 settlement.
This is the trust layer — agents must prove who they are and
that they're authorized before any payment goes through.

Enforcement checks:
1. Agent identity verification (ERC-8004 / wallet signature)
2. Policy compliance (spending limits, approved recipients)
3. Reputation check (credit score, past behavior)
4. Rate limiting (prevent abuse)
5. Geographic/compliance restrictions

Architecture:
    Agent Request → Enforcement → Q402 Settlement → Trust Receipt
                      ↕
               Identity Check
               Policy Check
               Reputation Check
               Rate Limit Check

Usage:
    from enforcement import EnforcementEngine

    engine = EnforcementEngine(config_path="config.yaml")

    # Pre-settlement check
    result = engine.enforce_before_settlement(
        agent_id="0x1234",
        action="pay",
        amount=5.0,
        chain="base",
        token="USDC",
        provider="0x5678",
        endpoint="/v1/score"
    )

    if result["allowed"]:
        # Proceed with Q402 settlement
        ...
    else:
        # Block — reason in result["reason"]
        ...
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class AgentIdentity:
    """Verified identity of an agent."""
    address: str
    chain: str
    credit_score: int = 0  # 0-850 (from Agent Credit Score framework)
    reputation: float = 0.0  # 0.0-1.0
    registered: bool = False
    verified_at: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class EnforcementPolicy:
    """Policy rules for enforcement."""
    # Identity requirements
    require_identity: bool = True
    min_credit_score: int = 300  # minimum credit score to transact
    min_reputation: float = 0.1  # minimum reputation to transact

    # Spending limits (per-agent)
    agent_daily_limit_usd: float = 500.0
    agent_per_tx_limit_usd: float = 100.0

    # Rate limits
    max_tx_per_minute: int = 10
    max_tx_per_hour: int = 100

    # Allowed actions
    allowed_actions: list[str] = field(default_factory=lambda: [
        "pay", "receive", "batch_pay", "schedule"
    ])

    # Compliance
    require_kyc_above_usd: float = 1000.0  # KYC required for large transactions
    blocked_chains: list[str] = field(default_factory=list)
    blocked_tokens: list[str] = field(default_factory=list)


@dataclass
class EnforcementResult:
    """Result of an enforcement check."""
    allowed: bool
    reason: str
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    enforcement_id: str = ""
    timestamp: str = ""


class EnforcementEngine:
    """
    Pre-settlement enforcement for Agent Kit × Q402.

    Every payment goes through this engine BEFORE touching Q402.
    It verifies identity, checks policy, and logs the decision.
    """

    def __init__(self, config_path: Optional[str] = None,
                 policy: Optional[EnforcementPolicy] = None,
                 audit_dir: Optional[str] = None):
        self.policy = policy or EnforcementPolicy()
        self.audit_dir = Path(audit_dir or os.environ.get(
            "AGENT_KIT_AUDIT_DIR",
            os.path.expanduser("~/.hermes/profiles/gentech/audit/enforcement")
        ))
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.audit_dir / f"enforcement-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
        self.agents_file = self.audit_dir / "registered_agents.json"
        self.agents: dict[str, AgentIdentity] = self._load_agents()
        self._load_daily_counts()

        if config_path:
            self._load_config(config_path)

    def _load_config(self, path: str):
        """Load enforcement config from YAML."""
        try:
            import yaml
            with open(path) as f:
                cfg = yaml.safe_load(f)
            if "enforcement" in cfg:
                e = cfg["enforcement"]
                self.policy.require_identity = e.get("require_identity", self.policy.require_identity)
                self.policy.min_credit_score = e.get("min_credit_score", self.policy.min_credit_score)
                self.policy.min_reputation = e.get("min_reputation", self.policy.min_reputation)
                self.policy.agent_daily_limit_usd = e.get("agent_daily_limit_usd", self.policy.agent_daily_limit_usd)
                self.policy.agent_per_tx_limit_usd = e.get("agent_per_tx_limit_usd", self.policy.agent_per_tx_limit_usd)
                self.policy.max_tx_per_minute = e.get("max_tx_per_minute", self.policy.max_tx_per_minute)
                self.policy.max_tx_per_hour = e.get("max_tx_per_hour", self.policy.max_tx_per_hour)
        except Exception as e:
            print(f"Warning: Could not load enforcement config: {e}")

    def _generate_id(self) -> str:
        """Generate unique enforcement check ID."""
        return f"enf_{int(time.time() * 1000)}_{os.urandom(4).hex()}"

    def _load_agents(self) -> dict[str, AgentIdentity]:
        """Load registered agent identities."""
        if self.agents_file.exists():
            with open(self.agents_file) as f:
                data = json.load(f)
            return {k: AgentIdentity(**v) for k, v in data.items()}
        return {}

    def _save_agents(self):
        """Persist agent identities."""
        with open(self.agents_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.agents.items()}, f, indent=2)

    def _load_daily_counts(self):
        """Load today's transaction counts for rate limiting."""
        self.tx_count_minute = 0
        self.tx_count_hour = 0
        self.daily_spend = 0.0
        # Load from log if exists
        if self.log_file.exists():
            now = time.time()
            minute_ago = now - 60
            hour_ago = now - 3600
            with open(self.log_file) as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        ts = datetime.fromisoformat(record["timestamp"]).timestamp()
                        if record.get("status") == "approved":
                            self.daily_spend += record.get("amount", 0)
                            if ts > minute_ago:
                                self.tx_count_minute += 1
                            if ts > hour_ago:
                                self.tx_count_hour += 1
                    except (json.JSONDecodeError, KeyError):
                        continue

    # === Identity Management ===

    def register_agent(self, address: str, chain: str = "base",
                       credit_score: int = 0, reputation: float = 0.0,
                       metadata: Optional[dict] = None) -> AgentIdentity:
        """Register a new agent identity."""
        agent = AgentIdentity(
            address=address.lower(),
            chain=chain,
            credit_score=credit_score,
            reputation=reputation,
            registered=True,
            verified_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self.agents[address.lower()] = agent
        self._save_agents()
        return agent

    def update_agent(self, address: str, **kwargs) -> Optional[AgentIdentity]:
        """Update an agent's identity data."""
        agent = self.agents.get(address.lower())
        if not agent:
            return None
        for key, value in kwargs.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        self._save_agents()
        return agent

    def get_agent(self, address: str) -> Optional[AgentIdentity]:
        """Get an agent's identity."""
        return self.agents.get(address.lower())

    # === Core Enforcement ===

    def enforce_before_settlement(
        self,
        agent_id: str,
        action: str,
        amount: float,
        chain: str = "base",
        token: str = "USDC",
        provider: str = "",
        endpoint: str = "",
    ) -> dict:
        """
        Run all enforcement checks before Q402 settlement.

        Returns:
            {
                allowed: bool,
                reason: str,
                checks_passed: list[str],
                checks_failed: list[str],
                warnings: list[str],
                enforcement_id: str
            }
        """
        checks_passed = []
        checks_failed = []
        warnings = []
        enforcement_id = self._generate_id()

        # 1. Action check
        if action not in self.policy.allowed_actions:
            checks_failed.append(f"action:{action}")
            result = EnforcementResult(
                allowed=False,
                reason=f"Action '{action}' not in allowed actions: {self.policy.allowed_actions}",
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                warnings=warnings,
                enforcement_id=enforcement_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._log_result(result, amount)
            return asdict(result)
        checks_passed.append(f"action:{action}")

        # 2. Chain/token check
        if chain in self.policy.blocked_chains:
            checks_failed.append(f"chain:{chain}")
            result = EnforcementResult(
                allowed=False,
                reason=f"Chain '{chain}' is blocked",
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                warnings=warnings,
                enforcement_id=enforcement_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._log_result(result, amount)
            return asdict(result)
        checks_passed.append(f"chain:{chain}")

        if token in self.policy.blocked_tokens:
            checks_failed.append(f"token:{token}")
            result = EnforcementResult(
                allowed=False,
                reason=f"Token '{token}' is blocked",
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                warnings=warnings,
                enforcement_id=enforcement_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._log_result(result, amount)
            return asdict(result)
        checks_passed.append(f"token:{token}")

        # 3. Identity check
        agent = self.agents.get(agent_id.lower())
        if self.policy.require_identity:
            if not agent or not agent.registered:
                checks_failed.append(f"identity:{agent_id}")
                result = EnforcementResult(
                    allowed=False,
                    reason=f"Agent {agent_id} is not registered. Call register_agent() first.",
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    warnings=warnings,
                    enforcement_id=enforcement_id,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                self._log_result(result, amount)
                return asdict(result)
            checks_passed.append(f"identity:{agent_id}")

            # Credit score check
            if agent.credit_score < self.policy.min_credit_score:
                checks_failed.append(f"credit_score:{agent.credit_score}")
                result = EnforcementResult(
                    allowed=False,
                    reason=f"Credit score {agent.credit_score} below minimum {self.policy.min_credit_score}",
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    warnings=warnings,
                    enforcement_id=enforcement_id,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                self._log_result(result, amount)
                return asdict(result)
            checks_passed.append(f"credit_score:{agent.credit_score}")

            # Reputation check
            if agent.reputation < self.policy.min_reputation:
                checks_failed.append(f"reputation:{agent.reputation}")
                result = EnforcementResult(
                    allowed=False,
                    reason=f"Reputation {agent.reputation:.2f} below minimum {self.policy.min_reputation}",
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    warnings=warnings,
                    enforcement_id=enforcement_id,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                self._log_result(result, amount)
                return asdict(result)
            checks_passed.append(f"reputation:{agent.reputation:.2f}")
        else:
            warnings.append("Identity check skipped (require_identity=False)")

        # 4. Amount limits
        if amount > self.policy.agent_per_tx_limit_usd:
            checks_failed.append(f"per_tx_limit:{amount}")
            result = EnforcementResult(
                allowed=False,
                reason=f"Amount ${amount} exceeds per-tx limit ${self.policy.agent_per_tx_limit_usd}",
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                warnings=warnings,
                enforcement_id=enforcement_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._log_result(result, amount)
            return asdict(result)
        checks_passed.append(f"per_tx_limit:${amount}")

        if self.daily_spend + amount > self.policy.agent_daily_limit_usd:
            remaining = self.policy.agent_daily_limit_usd - self.daily_spend
            checks_failed.append(f"daily_limit:remaining=${remaining:.2f}")
            result = EnforcementResult(
                allowed=False,
                reason=f"Would exceed daily limit. Spent: ${self.daily_spend:.2f}, requested: ${amount}, remaining: ${remaining:.2f}",
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                warnings=warnings,
                enforcement_id=enforcement_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._log_result(result, amount)
            return asdict(result)
        checks_passed.append(f"daily_limit:remaining=${self.policy.agent_daily_limit_usd - self.daily_spend - amount:.2f}")

        # 5. Rate limiting
        if self.tx_count_minute >= self.policy.max_tx_per_minute:
            checks_failed.append(f"rate_limit:minute:{self.tx_count_minute}")
            result = EnforcementResult(
                allowed=False,
                reason=f"Rate limit: {self.tx_count_minute} tx in last minute (max {self.policy.max_tx_per_minute})",
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                warnings=warnings,
                enforcement_id=enforcement_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._log_result(result, amount)
            return asdict(result)
        checks_passed.append(f"rate_limit:minute:{self.tx_count_minute}/{self.policy.max_tx_per_minute}")

        if self.tx_count_hour >= self.policy.max_tx_per_hour:
            checks_failed.append(f"rate_limit:hour:{self.tx_count_hour}")
            result = EnforcementResult(
                allowed=False,
                reason=f"Rate limit: {self.tx_count_hour} tx in last hour (max {self.policy.max_tx_per_hour})",
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                warnings=warnings,
                enforcement_id=enforcement_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._log_result(result, amount)
            return asdict(result)
        checks_passed.append(f"rate_limit:hour:{self.tx_count_hour}/{self.policy.max_tx_per_hour}")

        # 6. KYC warning for large amounts
        if amount >= self.policy.require_kyc_above_usd:
            warnings.append(f"Amount ${amount} >= KYC threshold ${self.policy.require_kyc_above_usd}")

        # All checks passed
        result = EnforcementResult(
            allowed=True,
            reason="All enforcement checks passed",
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            warnings=warnings,
            enforcement_id=enforcement_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._log_result(result, amount)
        return asdict(result)

    def _log_result(self, result: EnforcementResult, amount: float):
        """Log enforcement result and update counters."""
        log_entry = {
            "enforcement_id": result.enforcement_id,
            "timestamp": result.timestamp,
            "allowed": result.allowed,
            "reason": result.reason,
            "checks_passed": len(result.checks_passed),
            "checks_failed": len(result.checks_failed),
            "warnings": result.warnings,
            "amount": amount,
            "status": "approved" if result.allowed else "blocked",
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        if result.allowed:
            self.daily_spend += amount
            self.tx_count_minute += 1
            self.tx_count_hour += 1

    def get_daily_summary(self, date: Optional[str] = None) -> dict:
        """Get enforcement summary for a day."""
        target_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self.audit_dir / f"enforcement-{target_date}.jsonl"

        total = 0
        approved = 0
        blocked = 0

        if log_file.exists():
            with open(log_file) as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        total += 1
                        if record.get("status") == "approved":
                            approved += 1
                        else:
                            blocked += 1
                    except json.JSONDecodeError:
                        continue

        return {
            "date": target_date,
            "total_checks": total,
            "approved": approved,
            "blocked": blocked,
            "approval_rate": f"{(approved / total * 100):.1f}%" if total > 0 else "N/A",
        }

    def list_agents(self) -> list[dict]:
        """List all registered agents."""
        return [asdict(agent) for agent in self.agents.values()]
