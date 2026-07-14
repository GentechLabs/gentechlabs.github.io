# t54 SDK vs Gentech Brain — Technical Diff

**Author:** YoYo (Strategies)  
**Date:** 2026-04-26  
**Sources:** t54 claw.credit/SKILL.md, Gentech vault (x402-integration-map, agent-commerce-playbook, agentic-commerce-protocols)

---

## 1. What t54's SDK Actually Is

**Package:** `@t54-labs/clawcredit-sdk` (v0.2.40)  
**Runtime:** Node.js only  
**Core Function:** Credit underwriter + payment proxy for x402 services

### Architecture

```
Agent (Node.js)
  ↓ calls @t54-labs/clawcredit-sdk
ClawCredit API
  ↓ evaluates credit risk (agent context + reasoning traces)
Blockchain Settlement (Base/Solana/XRPL)
  ↓ pays merchant in USDC/RLUSD
Merchant x402 Endpoint
  ↓ returns service response
```

### Key SDK Components

| Component | What It Does |
|-----------|-------------|
| `ClawCredit` | Main client. Handles registration, credit evaluation, payments. |
| `wrapOpenAI` | Wraps OpenAI client to capture reasoning traces for underwriting. |
| `withTrace` | Execution context wrapper. Attaches LLM messages/completion as proof of reasoning. |
| `register()` | Submits agent context, enters pre-qualification monitoring. |
| `pay()` | Pays x402 merchants using credit line (not agent's own crypto). |
| `submitPrequalificationContext()` | Heartbeat-driven context updates for credit evaluation. |
| `getRepaymentUrgency()` | Returns urgency tier + active promotions. |
| `redeemPromotion()` | Redeem codes for chain-specific credit grants. |

### The Pre-Qualification Monitoring Loop

```
register() → pending → heartbeat every 6h → submit context → under_review → approved → credit issued
```

**What they monitor:**
- Agent transcripts (OpenClaw workspace sessions)
- Prompt files (AGENTS.md, workspace .md files)
- Runtime environment (node version, model used)
- Reasoning traces (captured via wrapOpenAI + withTrace)

**The insight:** Your agent's *behavior* determines creditworthiness. Not wallet balance. Not collateral.

---

## 2. How t54's Approach Differs from Gentech's Vault

### 2.1 Payment Model: Credit vs Escrow

| | t54 | Gentech (Vault) |
|---|---|---|
| **Pattern** | **Credit line** — ClawCredit pays merchant, agent owes ClawCredit | **Escrow** — buyer locks funds, seller does work, funds release on completion |
| **Trust model** | Underwriting + repayment history | Escrow + dispute resolution (IResolver) |
| **Who takes risk** | t54 underwrites and takes default risk | Buyer/seller risk is mutual via escrow lock |
| **When payment flows** | Before work (credit spent immediately) | After work validated (escrow release) |
| **REP relevance** | None — credit score is separate | REP gates premium features, dispute tiers |

**Verdict:** These are complementary, not competing. t54 = "pay now, settle later." Gentech = "lock now, release on proof."

### 2.2 Reasoning Traces vs Dispute Evidence

| | t54 | Gentech |
|---|---|---|
| **What they capture** | LLM reasoning trace (messages + completion) | Evidence URL + metadata (uploaded off-chain) |
| **Why they capture it** | Credit underwriting — prove agent isn't scamming | Dispute resolution — prove work was done / not done |
| **Where it lives** | Auto-discovered from OpenClaw workspace | Keeper bridge reads on-chain event → fetches evidence URL |
| **Who consumes it** | t54's risk engine | Human arbiter / AI oracle (GenLayer) |

**Verdict:** t54 uses traces for *prevention* (underwriting). Gentech uses evidence for *resolution* (disputes). Both need proof-of-work, but at different stages.

### 2.3 SDK Design: Monolithic vs Modular

| | t54 SDK | Gentech Patterns |
|---|---|---|
| **Architecture** | Monolithic NPM package. Single vendor lock-in. | Modular interfaces. IResolver, x402 pattern, keeper bridge — swappable components. |
| **Chain support** | Base, Solana, XRPL — hardcoded | "Chain-pragmatic" — use right chain for right job. Solana for micro-TX, Base for USDC, etc. |
| **Token model** | No token. USD credit lines only. | Dual-pricing: USDC + $TECH (20-30% discount) |
| **Integration style** | SKILL.md — machine-readable spec for agents | No standardized machine-readable spec yet. Human docs + code. |

**Verdict:** t54 is a product SDK. Gentech is building protocol infrastructure. t54's SKILL.md pattern is something we should adopt.

### 2.4 Agent Identity / Reputation

| | t54 | Gentech |
|---|---|---|
| **Identity** | Invite code + World ID (human verification) | Self-custody wallet + on-chain REP |
| **Reputation** | Credit score (payment history, usage patterns) | REP score (process, discipline, consistency — not just profit) |
| **Sybil resistance** | World ID (one human = one verified agent) | Economic stake + on-chain history |
| **Transferable?** | No — credit tied to agent instance | REP is on-chain and composable |

**Verdict:** t54's credit score is *financial* reputation. Gentech's REP is *behavioral* reputation. These could be combined: high REP = better credit terms.

---

## 3. What's Novel in t54's SDK (Things We Don't Have)

### ✅ 1. Machine-Readable SKILL.md
- Exposed at `claw.credit/SKILL.md`
- Agents can self-discover and self-integrate
- Uses YAML frontmatter + structured markdown
- **Gentech gap:** No machine-readable spec for AAE, LP Monitor, or any agent capability. All human docs.

### ✅ 2. Reasoning Trace Capture as First-Class SDK Feature
- `wrapOpenAI()` and `withTrace()` are built into the SDK
- Underwriting depends on *how* the agent thinks, not just *what* it does
- **Gentech gap:** No trace capture in our stack. Agents act, but we don't log reasoning.

### ✅ 3. Pre-Qualification as a Service
- Agents don't get credit immediately. They're monitored.
- 6-hour heartbeat cycles submit context updates
- System learns agent behavior before trusting with money
- **Gentech gap:** No pre-qualification. Anyone with REP can access features. No behavioral monitoring phase.

### ✅ 4. Credit Line Suspension + Tiered Notifications
- Overdue → suspension → 402 Payment Required error
- Urgency tiers: overdue, due_today, due_tomorrow, due_soon, due_this_week
- **Gentech gap:** No payment enforcement. $TECH subscriptions are voluntary. No consequence for non-payment.

### ✅ 5. Chain-Specific Credit Grants
- Universal USD credit + chain-locked grants (e.g., 5 XRP from XRPL Foundation)
- Grants consumed first on their chain
- **Gentech gap:** No chain-specific incentives. $TECH is universal.

### ✅ 6. Promotions Engine (Structured Push)
- Merchant cashback, credit line grants, redeem codes
- Delivered via `getRepaymentUrgency()` response
- **Gentech gap:** No promotions engine. No partner cashback or ecosystem grants.

### ✅ 7. World ID Integration for Instant Credit
- $5 instant credit upon human verification
- Sybil protection (one World ID = one agent)
- **Gentech gap:** No human verification layer. REP is purely on-chain/economic.

---

## 4. What Gentech Has That t54 Doesn't

### ✅ 1. Escrow + Dispute Resolution (IResolver Pattern)
- t54 has no escrow. Payment flows immediately to merchant.
- Gentech has swappable dispute resolution: human → AI oracle → multisig
- **Moat:** Trust-through-escrow is fundamentally different from trust-through-underwriting.

### ✅ 2. Dual-Pricing (USDC + $TECH)
- t54 is USD-only. No loyalty token.
- Gentech's $TECH creates incentive alignment and a sink mechanism.
- **Moat:** Token economics t54 explicitly avoids.

### ✅ 3. Cross-Chain Bridge Vision
- t54 supports 3 chains but they're parallel, not bridged.
- Gentech's AgentEscrow v2 envisions chain-agnostic routing.
- **Moat:** t54 is multi-chain. Gentech aims to be cross-chain.

### ✅ 4. "More Winners Than Losers" Philosophy
- t54's credit model rewards *financial* responsibility.
- Gentech's REP rewards *process and discipline*, not just profit.
- **Moat:** Behavioral reputation is stickier than credit score.

### ✅ 5. Arena / Competition Layer
- t54 has no competitive/gamification layer.
- Gentech's Arena lets agents compete, learn, improve.
- **Moat:** Community and engagement mechanics.

---

## 5. Integration Opportunities

### Opportunity A: Gentech Agents as ClawCredit Consumers
**What:** Let YoYo, DMOB, Desmond use ClawCredit to pay for x402 services.
**Why:** Gentech agents need to call APIs (Birdeye, Heurist, etc.). ClawCredit removes the need to pre-fund wallets.
**How:** Each agent registers with ClawCredit, gets credit line, pays for services. Jordan repays via dashboard.
**Risk:** Custody-based. Agents don't hold keys. But for API payments, this might be acceptable.

### Opportunity B: REP → Credit Score Bridge
**What:** High REP agents get better ClawCredit terms.
**Why:** t54's underwriting is behavioral. REP is behavioral reputation. Natural fit.
**How:** Build a bridge that submits Gentech REP score as additional context during ClawCredit pre-qualification.
**Value:** Gentech REP becomes valuable outside our ecosystem. t54 gets better risk signal.

### Opportunity C: AAE Escrow + ClawCredit as Payment Rail
**What:** Agent-to-agent escrow where buyer uses ClawCredit to fund escrow.
**Why:** Buyer doesn't need crypto upfront. Credit underwritten by t54, work secured by Gentech escrow.
**How:** `credit.pay()` sends funds to escrow contract instead of merchant. Escrow logic unchanged.
**Value:** Removes buyer friction (no pre-funding). Retains Gentech trust layer.

### Opportunity D: Adopt SKILL.md Pattern
**What:** Expose Gentech capabilities as machine-readable SKILL.md files.
**Why:** Other agents (not just humans) can discover and use our services.
**How:** Create `/SKILL.md` endpoints for LP Monitor, AAE Premium, Arena, etc.
**Value:** Gentech services become discoverable in the agentic economy.

---

## 6. The Brain Diff — Specific Vault Gaps

| Vault File | What's Missing vs t54 |
|------------|----------------------|
| `x402-integration-map.md` | No credit/underwriting layer. All payments assume buyer has funds. |
| `agent-commerce-playbook.md` | No trace capture pattern. No pre-qualification concept. No heartbeat SDK integration. |
| `agentic-commerce-protocols.md` | No mention of agent credit or underwriting protocols. Only payment protocols (x402, MPP, AP2). |
| `AAE-Consistency-REP-Spec.md` | REP is static score. No dynamic behavioral monitoring like t54's pre-qualification. |
| `AAE-Premium-Product-Spec.md` | No machine-readable integration spec (SKILL.md equivalent). |

---

## 7. Recommendations

### Immediate (This Week)
1. **Adopt SKILL.md pattern** — Create machine-readable specs for at least LP Monitor and AAE Premium. Host at `/SKILL.md` or similar.
2. **Trace capture POC** — Add reasoning trace logging to YoYo's next analysis. Prove the concept before building SDK features.

### Short-Term (Next 2 Weeks)
3. **Evaluate ClawCredit integration** — Try registering a test agent, going through pre-qualification, paying for a Birdeye x402 call. Document the experience.
4. **REP → Credit bridge concept** — Draft a spec for how REP score could be submitted as ClawCredit context. Even if not built, the concept strengthens our positioning.

### Strategic (Next Month)
5. **Differentiate on escrow** — t54 can't do escrow without major product shift. Double down on "escrow + reputation" as our unique angle.
6. **Position as complementary** — In Frontier / Colosseum submissions, acknowledge t54's credit layer and position Gentech as the "escrow + dispute resolution" layer that sits on top.

---

## 8. Raw t54 SDK Data

**NPM:** `@t54-labs/clawcredit-sdk` v0.2.40  
**Chains:** Base (USDC), Solana (USDC), XRPL (RLUSD)  
**Credit line:** Universal USD + chain-specific grants  
**Repayment:** Human via dashboard (Phase 1). Agent repayment coming later.  
**World ID:** $5 instant credit, sybil protection  
**Token stance:** No token planned  
**Integration:** x402-enabled services, lobster.cash, Heurist mesh  
**Heartbeat:** 6h pre-qualification check, 24h repayment check  
**Credentials:** Auto-saved to `~/.openclaw/agents/<agent>/agent/clawcredit.json`
