#!/usr/bin/env python3
"""
Mastercard Innovation Challenge 2026 — BLUE TEAM
Pre-execution governance guard.

The GenTech thesis: don't just DETECT fraud after it happens — STOP it at the
boundary BEFORE the agent can act. This is deterministic pre-execution
governance, the counter-position to stochastic post-hoc fraud detection.

For every incoming PaymentIntent, the guard evaluates policy checks and
returns a verdict:
  - BLOCK    — a hard policy violation (identity mismatch, unlisted beneficiary,
               prompt-injection marker). Refused before execution.
  - FLAG     — an anomaly (velocity, amount, chain) that fails a soft check;
               requires human/principal confirmation before release.
  - ALLOW    — all checks pass; the payment may execute.

Output is a structured Verdict. Deterministic and auditable (every block
carries the exact rule that fired) — this is the ERC-8004 / x402 "audit trail"
story made concrete.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional

from red_team import (
    ALLOWED_BENEFICIARIES,
    APPROVED_RAILS,
    ATTACK_TYPES,
    PaymentIntent,
)

# Policy knobs (the "governance rules" — the configurable trust boundary)
POLICY = {
    "max_velocity_multiplier": 1,  # velocity_ok is already a boolean signal
    "require_identity_match": True,
    "require_beneficiary_listed": True,
    "require_approved_chain": True,
    "require_amount_within_ticket": True,
    "block_on_injection": True,  # detect the [IGNORE PREVIOUS] marker
}

# Hard rules -> BLOCK
HARD_RULES = {
    "identity_spoof": lambda p: not p.payer_identity_match,
    "out_of_policy": lambda p: not p.beneficiary_listed,
    "chain_shift": lambda p: p.chain not in APPROVED_RAILS,
    "injection": lambda p: _injection_marker(p.request_text),
}

# Soft rules -> FLAG (anomaly, needs confirmation)
SOFT_RULES = {
    "velocity_spike": lambda p: not p.velocity_ok,
    "amount_anomaly": lambda p: not p.amount_within_ticket,
}


def _injection_marker(text: str) -> bool:
    """Detect common prompt-injection / instruction-override markers."""
    t = (text or "").lower()
    markers = [
        "[ignore previous",
        "ignore previous instructions",
        "ignore all previous",
        "release the full balance",
        "pay the above address the full",
        "do not let the agent refuse",
    ]
    return any(m in t for m in markers)


@dataclass
class Verdict:
    intent_id: str
    decision: str  # BLOCK | FLAG | ALLOW
    rules: list[str]
    reason: str
    attack_type: Optional[str]
    decided_at_utc: str = ""

    def __post_init__(self):
        if not self.decided_at_utc:
            self.decided_at_utc = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate(intent: PaymentIntent) -> Verdict:
    """Pre-execution governance evaluation of a PaymentIntent."""
    rules = []

    # Hard checks first — any violation is an immediate BLOCK.
    for name, check in HARD_RULES.items():
        if check(intent):
            rules.append(name)

    # Injection always blocks regardless of other signals.
    if _injection_marker(intent.request_text) and "injection" not in rules:
        rules.append("injection")

    if rules:
        atk = intent.attack_type or "out_of_policy"
        label = ATTACK_TYPES.get(atk, {}).get("label", atk)
        return Verdict(
            intent_id=intent.intent_id,
            decision="BLOCK",
            rules=rules,
            reason=f"Hard policy violation — blocked at the boundary before execution "
                   f"(attack: {label}). Audit: {', '.join(rules)}.",
            attack_type=intent.attack_type,
        )

    # Soft checks — anomalies FLAG for principal/human confirmation.
    for name, check in SOFT_RULES.items():
        if check(intent):
            rules.append(name)

    if rules:
        atk = intent.attack_type or "out_of_policy"
        label = ATTACK_TYPES.get(atk, {}).get("label", atk)
        return Verdict(
            intent_id=intent.intent_id,
            decision="FLAG",
            rules=rules,
            reason=f"Anomaly detected — requires principal confirmation before release "
                   f"(attack: {label}). Flags: {', '.join(rules)}.",
            attack_type=intent.attack_type,
        )

    # All clear
    return Verdict(
        intent_id=intent.intent_id,
        decision="ALLOW",
        rules=[],
        reason="All governance checks passed — payment eligible for execution.",
        attack_type=intent.attack_type,
    )


def evaluate_batch(intents: list[PaymentIntent]) -> list[Verdict]:
    return [evaluate(i) for i in intents]


def main() -> int:
    import argparse

    from red_team import generate_batch

    ap = argparse.ArgumentParser(description="Mastercard blue team — governance guard")
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    intents = generate_batch(args.count, seed=args.seed)
    verdicts = evaluate_batch(intents)

    if args.json:
        print(json.dumps([v.to_dict() for v in verdicts], indent=2))
        return 0

    print(f"🔵 BLUE TEAM — pre-execution governance on {args.count} intents (seed={args.seed})\n")
    for v in verdicts:
        icon = {"BLOCK": "⛔", "FLAG": "🚩", "ALLOW": "✅"}[v.decision]
        print(f"{icon} {v.intent_id} → {v.decision}")
        print(f"    {v.reason}")
        print()
    return 0


if __name__ == "__main__":
    main()
