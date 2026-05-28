# Microsoft Agent Governance Toolkit — Technical Assessment

**Date:** May 26, 2026
**Repo:** https://github.com/microsoft/agent-governance-toolkit
**Status:** Cloned to `/root/agent-governance-toolkit/`
**License:** MIT | **Stars:** 2,344 | **Language:** Python (also TS/.NET/Rust/Go)

---

## TL;DR

AGT is a comprehensive runtime governance framework for AI agents. It covers policy enforcement, identity, sandboxing, SRE, compliance, and marketplace trust. **We need ~40% of it.** The rest is overkill for our stage.

---

## What We Need (High Value)

### 1. Agent OS — Policy Engine ✅ IMMEDIATE
**Use for:** AgentEscrow vault operations, Agent Arena rule enforcement

- `govern(tool, policy="policy.yaml")` — wraps any tool function, enforces policy on every call
- YAML-based policies with deny-by-default, priority ordering
- Operators: eq, ne, gt, lt, in, matches, contains
- Financial services policy template included (SOX/PCI DSS/AML aligned)

**Integration point:** Wrap AgentEscrow's payment/release functions with governance policies. Define what agents can and cannot do with funds.

### 2. Agent SRE — Kill Switch + SLO ✅ IMMEDIATE
**Use for:** Agent fleet reliability, emergency stops

- `KillSwitch` — emergency agent termination
- SLO engine with error budgets and burn rate alerting
- `CostGuard` — LLM token/API cost tracking
- Circuit breakers for cascade failure prevention

**Integration point:** Kill switch for rogue trading agents. SLO tracking for agent performance in Agent Arena.

### 3. Agent Compliance — OWASP Verification ✅ IMMEDIATE
**Use for:** Security posture, audit readiness

- `agt verify` — checks all 10 OWASP Agentic Top 10 controls
- Compliance grade (A-F) with badge URL for README
- `agt red-team scan` — prompt injection auditing
- `agt lint-policy` — policy file validation

**Integration point:** Run `agt verify` on our agent fleet to prove security posture. Badge on portfolio for credibility.

### 4. Financial Services Policy Template ✅ IMMEDIATE
**Use for:** Starting point for Agent Arena/AgentEscrow governance

- Already includes: credit card detection, IBAN blocking, SWIFT auditing, payment redirection prevention
- Token budget limits, tool call circuit breakers
- Segregation of duties controls

**Integration point:** Adapt template for DeFi-specific policies (max transfer amounts, allowed DEXes, slippage limits).

---

## What We Might Need (Medium Value, Later)

### 5. Agent Mesh — Identity + Trust Scoring 🔶 PHASE 2
**Use for:** Agent Arena reputation system, cross-chain agent identity

- Ed25519 keypair identity per agent
- DID format: `did:mesh:<hex>`
- 5-dimension trust scoring: competence, integrity, availability, predictability, transparency
- Delegation chains (max depth 10) with capability narrowing

**Why later:** We're building our own reputation system ("rep-as-currency"). AGT's trust model could inform it, but we don't need the full mesh deployment yet.

### 6. Agent Runtime — Saga Orchestration 🔶 PHASE 2
**Use for:** Multi-step DeFi transaction workflows

- Saga DSL for multi-step operations with compensation
- Fan-out orchestration for parallel execution
- Checkpoint management for recovery

**Why later:** Our multi-agent handoff chains are simpler right now. Saga orchestration becomes valuable when we have complex multi-step vault operations.

---

## What We Don't Need (Overkill for Now)

### ❌ Full Agent Mesh Deployment
- Sidecar proxy, K8s operator, Redis backend
- Federation, cross-org trust
- **Why:** We're single-tenant, not building a multi-organization mesh

### ❌ Agent Marketplace Plugin Governance
- Plugin manifest schema, installer security, AST scanning
- **Why:** We're building our own marketplace for AAE. AGT's plugin model is enterprise-oriented.

### ❌ Chaos Engineering
- Fault injection, adversarial testing scheduler
- **Why:** Relevant later for production hardening, not now

### ❌ Agent Hypervisor (Full Stack)
- 4-ring privilege system, vector clocks, liability matrix
- **Why:** The ring system is interesting conceptually but too heavy for our current agent fleet

### ❌ Docker/K8s Deployment Hardening
- `--cap-drop ALL`, `--read-only`, seccomp profiles
- **Why:** We're not deploying to K8s yet. Our agents run on a single VPS.

---

## GenLayer vs AGT — Complementary, Not Competing

| Dimension | GenLayer | AGT |
|-----------|----------|-----|
| **Purpose** | Intelligent contracts (AI-powered on-chain logic) | Runtime governance (policy, identity, sandboxing) |
| **Layer** | On-chain execution | Off-chain policy enforcement |
| **When it runs** | Smart contract execution time | Before/after every agent action |
| **Focus** | "What should the agent decide?" | "Is this action allowed?" |
| **Integration** | We build governance intelligence (yield scoring, risk detection) | We enforce policies on those decisions |

**They work together:** GenLayer contract makes a yield recommendation → AGT policy engine checks if the action is within bounds → Agent executes or is denied.

---

## Recommended Integration Path

### Phase 1 (This Week)
1. `pip install agent-governance-toolkit[full]`
2. Run `agt verify` on our existing agent fleet
3. Adapt financial services policy template for AgentEscrow
4. Wrap key AgentEscrow functions with `govern()`

### Phase 2 (June)
1. Integrate kill switch into agent monitoring cron
2. Add SLO tracking for Agent Arena agent performance
3. Run `agt red-team scan` on our prompt templates

### Phase 3 (Post-MVP)
1. Evaluate Agent Mesh identity for cross-chain agent auth
2. Study trust scoring model for Agent Arena reputation
3. Consider saga orchestration for complex vault operations

---

## Key Files to Read
- `examples/policy-templates/financial-services.yaml` — starting point for our policies
- `agent-governance-python/agent-os/` — core policy engine
- `agent-governance-python/agent-sre/src/agent_sre/kill_switch.py` — emergency stops
- `agent-governance-python/agent-compliance/` — OWASP verification

---

*Assessment by Gentech | May 26, 2026*
