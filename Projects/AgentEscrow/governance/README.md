# GenTech Governance — Hermes × AGT Integration

**Two-way consensus mechanism:**
- Hermes says "do this" (instruction)
- AGT checks "are you allowed to?" (verification)
- Agent executes or is denied (enforcement)
- Audit log records everything (accountability)

## Setup

```bash
pip install agent-governance-toolkit[full]
```

## Files

- `policies/defi-governance.yaml` — Our DeFi-specific policy (46 rules, OWASP ASI 10/10)
- `governance.py` — Integration wrapper for Hermes agents
- `audit.log` — Tamper-evident audit trail

## Quick Start

```python
from governance import GovernedAgent

# Create governed agent
agent = GovernedAgent(
    agent_id="escrow-agent-01",
    policy_path="policies/defi-governance.yaml"
)

# Check action (logged + enforced)
result = agent.execute("transfer", {"amount": 100, "to": "0x1234..."})
# → Requires human approval (policy rule: defi-block-unauthorized-transfer)

result = agent.execute("fetch_token_prices", {"tokens": "AVAX,USDC"})
# → Allowed (policy rule: defi-allow-read-operations)

# Emergency stop
agent.emergency_stop()
# → All operations halted, kill switch triggered
```

## Policy Rules (46 total)

| Category | Rules | Action |
|----------|-------|--------|
| Prompt injection (ASI-01) | 3 | deny |
| Tool misuse (ASI-02) | 3 | deny |
| Privilege escalation (ASI-03) | 2 | deny |
| Supply chain (ASI-04) | 2 | deny |
| Code execution (ASI-05) | 2 | deny |
| Memory poisoning (ASI-06) | 2 | deny |
| Hidden channels (ASI-07) | 1 | deny |
| Cascading failures (ASI-08) | 2 | deny/audit |
| Trust exploitation (ASI-09) | 2 | deny/audit |
| Rogue agents (ASI-10) | 2 | deny |
| DeFi domain | 10 | deny/audit/allow |
| Agent Arena | 2 | deny |

## Default Action: DENY

Every action is denied unless explicitly allowed. Read operations always pass.
Transfers require human approval. Trading is audited.

## Audit Trail

Every check is logged to `audit.log` with:
- Timestamp
- Agent ID
- Action attempted
- Decision (allowed/denied)
- Policy rule that matched
- Metadata

## Integration with Hermes

The `GovernedAgent` class wraps any Hermes tool call:
1. Agent receives instruction from Hermes
2. `agent.execute()` checks against policy
3. If allowed → tool runs, result returned
4. If denied → `GovernanceDenied` raised, logged
5. Emergency stop → kill switch triggers, all ops halt

## OWASP ASI 2026 Compliance

```
✅ ASI-01: Prompt Injection
✅ ASI-02: Insecure Tool Use
✅ ASI-03: Excessive Agency
✅ ASI-04: Unauthorized Escalation
✅ ASI-05: Trust Boundary Violation
✅ ASI-06: Insufficient Logging
✅ ASI-07: Insecure Identity
✅ ASI-08: Policy Bypass
✅ ASI-09: Supply Chain Integrity
✅ ASI-10: Behavioral Anomaly
```

---

*Built on Microsoft AGT (MIT) | Adapted for GenTech DeFi stack*
