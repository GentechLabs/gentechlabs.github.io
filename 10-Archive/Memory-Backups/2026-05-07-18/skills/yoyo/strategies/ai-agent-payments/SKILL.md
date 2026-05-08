---
name: ai-agent-payments
title: AI Agent Payment Integration
description: Integrating payment rails (Pay.sh, x402, etc.) for autonomous AI agents, including escrow systems, fee management, and financial controllers.
version: 0.1.0
last_updated: 2026-05-06
---

## Trigger Conditions

Load this skill when working on any of the following:
- Integrating a new payment rail (Pay.sh, Stripe, etc.) for AI agents
- Designing escrow systems for agent services (AgentEscrow)
- Building financial controllers for autonomous agents (AAE)
- Evaluating payment protocols for agent economy
- Hackathon sidetrack submissions involving agent payments
- Troubleshooting payment integration issues

## Core Patterns

### 1. Pay.sh Integration Pattern

**Context**: Pay.sh is a Solana-based payment gateway for AI agents, backed by Solana Foundation and Google Cloud.

**Integration Points**:
- **AgentEscrow**: Add Pay.sh as a funding method for escrow contracts
- **AAE Financial Controller**: Use Pay.sh for automatic fee payments and API access
- **Agent-to-Agent Payments**: Enable service marketplace transactions

**Implementation Steps**:
```python
# Pay.sh client integration
class PayShClient:
    def __init__(self, api_key: str, network: str = "mainnet"):
        self.base_url = f"https://{network}.paysh.sh/api/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def create_payment(self, amount: float, recipient: str, memo: str = "") -> str:
        """Create a stablecoin payment via Pay.sh"""
        payload = {
            "amount": amount,
            "currency": "USDC",
            "recipient": recipient,
            "memo": memo
        }
        response = requests.post(
            f"{self.base_url}/payments",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["payment_id"]
    
    def get_balance(self) -> float:
        """Check Pay.sh wallet balance"""
        response = requests.get(
            f"{self.base_url}/wallet",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["balance"]
```

**Key Considerations**:
- Use testnet/sandbox first
- Implement webhook handlers for payment confirmations
- Add retry logic with exponential backoff
- Monitor rate limits

### 2. AgentEscrow Payment Architecture

**Context**: AgentEscrow is a trustless escrow system for AI agent services on Solana.

**Payment Flow**:
```
Buyer → Pay.sh → System Wallet → Escrow Contract → Agent (after verification)
```

**Smart Contract Integration**:
```solidity
// AgentEscrow.sol (modified)
interface PayShRouter {
    function pay(uint256 amount, bytes32 jobHash) external returns (bool);
}

function fundWithPaySh(bytes32 jobHash, uint256 amount) external {
    PayShRouter(paySh).pay(amount, jobHash);
    _fundEscrow(jobHash, amount, USDC_MINT);
}
```

**Security Patterns**:
- Multi-token support via Swig integration
- Soulbound reputation NFTs (Metaplex)
- World ID verification for Sybil resistance
- Decentralized dispute resolution

### 3. AAE Financial Controller Agent

**Context**: AAE (AI Agent Ecosystem) is a three-agent system for portfolio management.

**Agent Design**:
```python
class FinancialControllerAgent:
    def __init__(self, pay_sh_client: PayShClient, config: dict):
        self.pay_sh = pay_sh_client
        self.budgets = config["budgets"]
        self.metrics = {}
    
    def allocate_funds(self, strategy: str, amount: float):
        """Rotate capital between LP, staking, and farming"""
        # Payment logic integrated with Pay.sh
        if strategy == "data_feed":
            self.pay_sh.create_payment(
                amount=amount,
                recipient="birdeye_data",
                memo="AAE Analyst data subscription"
            )
        elif strategy == "transaction_fees":
            self.pay_sh.create_payment(
                amount=amount,
                recipient="solana_fee_payer",
                memo="Executor gas fees"
            )
    
    def optimize_portfolio(self, current_positions: dict):
        """Make allocation decisions based on market regime"""
        # Analyst signals → Strategy Brain → Validator → Executor
        # Financial Controller handles all monetary aspects
        pass
```

**Integration with AAE Stack**:
- Analyst agent requests data payments
- Executor agent requests gas fee payments
- Brain agent monitors budgets and approves

## Implementation Methodology

### Hackathon Sidetrack Adapter Workflow

**When to use**: For hackathon submissions involving new payment integrations.

**5-Step Process**:
1. **API Surface Research** — Map auth, endpoints, SDKs, rate limits
2. **Fit Assessment** — Determine if adapter is "thin" (wraps existing code) or "new program" (requires fresh build)
3. **Decision Framework** — Present options: main focus, low-effort adapters, or full blitz
4. **Adapter Spec Creation** — Write spec with API details, architecture, CLI commands
5. **Sprint Plan Update** — Add adapter tasks to milestones (Days 5-6 after main submission)

**Reference**: `references/sidetrack-adapter-workflow.md`

### Provider Auth Resilience

**Problem**: Recurring authentication errors (API keys, OAuth tokens).

**Mitigation Stack**:
1. **Retry logic** — Exponential backoff with jitter
2. **Dead-letter queue** — Log failures to `11-Mess Hall/provider-errors/`
3. **Credential pre-rotation** — Validate before critical jobs
4. **Fallback provider pool** — Secondary API keys
5. **Centralized credential store** — HashiCorp Vault or similar

**Monitoring**: Scan logs for `AuthError|401|403|revoked` and alert if threshold crossed.

### Ground Truth Protocol

**Hierarchy**:
1. On-chain decoded balances (authoritative)
2. Watchlist/price aggregators (secondary)
3. Narrative/summary scripts (tertiary)

**Operational Protocol**:
- Daily vault entries must match ground truth exactly
- If divergence >$0.50 or efficiency differs >5%, document and investigate
- Use symlinks for state files across profiles

**Reference**: `references/ground-truth-protocol.md`

## Pitfalls

### P1: Payment Rail Not Ready
- **Symptom**: API returns 500 or rate limited during integration
- **Cause**: Sandbox not fully implemented or test keys invalid
- **Fix**: Start with testnet, have backup provider, implement graceful degradation

### P2: Over-Engineering
- **Symptom**: Building complex adapter when simple webhook would suffice
- **Cause**: Trying to cover all edge cases upfront
- **Fix**: Start minimal, iterate based on actual usage

### P3: Security Misconfiguration
- **Symptom**: API keys exposed in logs or client-side code
- **Cause**: Improper secret management
- **Fix**: Use environment variables, never commit keys, implement key rotation

### P4: Ignoring Quiet Hours
- **Symptom**: Alerts sent during user's quiet hours
- **Cause**: `is_quiet_hours()` not checked before sending
- **Fix**: Implement two-mode notification throttling (see `strategies` skill)

### P5: State File Divergence
- **Symptom**: Different scripts report different balances/efficiency
- **Cause**: State files not synchronized across profiles
- **Fix**: Use symlinks and ground truth protocol

### P6: Parameter Name Mismatches
- **Symptom**: `NameError: name 'X' is not defined` despite parameter existing
- **Cause**: Call site uses wrong keyword argument name
- **Fix**: Verify function signatures with `grep -n "^def"`; ensure call sites match exactly

## References

- `references/sidetrack-adapter-workflow.md` — API research template, adapter spec format
- `references/ground-truth-protocol.md` — Script discrepancy resolution, state file layout
- `references/provider-strategy.md` — Provider auth resilience, credential management
- `references/d5-milestone-enhancements-2026-05.md` — Implementation details for payment-related alerts
- `references/portfolio-positioning.md` — Messaging and positioning for AI agent projects
- `references/solana-frontier-hackathon.md` — Solana Frontier tracks, AgentEscrow architecture
- `templates/protocol-evaluation-template.md` — Vault file template for new protocol reviews
- `templates/il-spike-vault-entry.md` — Vault entry format for IL review flags

## Related Skills

- `strategies` — Core DeFi and portfolio strategy patterns
- `defi-lp-monitor` — LP position monitoring and milestone tracking
- `hermes-agent` — Hermes agent configuration and environment debugging
- `gentech` — Gentech-specific workflows and coordination
- `handoff-reporting` — End-of-shift handoff reports

## Verification

**Before considering integration complete**:
- [ ] Pay.sh testnet integration working
- [ ] End-to-end payment flow tested (create → confirm → settle)
- [ ] Error handling and retry logic implemented
- [ ] Security audit passed (no keys exposed)
- [ ] Documentation updated in vault
- [ ] Demo video recorded (if for hackathon)