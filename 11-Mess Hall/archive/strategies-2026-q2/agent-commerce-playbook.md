# Agent Commerce Playbook — Cross-Project Patterns

**Author:** YoYo (Strategies)
**Date:** Apr 21, 2026
**Status:** 🟢 LIVING DOCUMENT — Update as we ship
**Source projects:** arc-hackathon, agent-escrow-solana, kite-agent-commerce, agent-economy-solana

---

## The Thesis

We're not building escrow contracts. We're building **modular infrastructure for the agent economy.** Every project we ship proves the same core insight: agents need payments, trust, and dispute resolution — and those systems should be chain-agnostic, swappable, and composable.

---

## Patterns That Hold Across All Projects

### 1. The IResolver Pattern — Swappable Dispute Resolution

**Discovered in:** arc-hackathon → abstracted for all chains

The escrow doesn't care *who* adjudicates. It calls an interface. The resolver does the thinking.

```
Escrow → IResolver.fileDispute(ctx) → resolver handles everything → escrow.executeVerdict()
```

**Why it works:**
- Human arbiter (Tier 1): cheap, fast, deterministic — good enough for 90% of cases
- AI oracle (Tier 2): GenLayer LLM reads evidence URL → consensus verdict — for complex SLA disputes
- Multisig / custom (Tier 3): DAO governance, insurance pools, whatever comes next

**Cross-chain portability:**
- EVM: Solidity interface, standard pattern
- Solana: Anchor trait + PDA-based resolver accounts
- Same mental model, different implementation

**Lesson:** Every time we hardcode a decision, we lose optionality. Interfaces are free. Use them.

---

### 2. The x402 Payment Trigger — HTTP 402 as Universal Payment Layer

**Discovered in:** kite-agent-commerce → validated across arc-hackathon, agent-economy-solana

x402 isn't a protocol — it's a **pattern**. Server returns 402, client pays, server responds. Works on any chain.

```
Agent A → POST /api/service → 402 {price, payment_instructions}
Agent A → signs tx / X-PAYMENT header → 200 OK + data
```

**What we learned:**
- Coinbase's Agentic Market ($424K daily volume) proves the demand on Base
- PayAI facilitator does the same on Solana
- Birdeye x402 API ($0.003/request) proves it works for data services
- **The payment rail doesn't matter** — the 402 pattern is chain-agnostic

**Cross-project application:**
- LP Monitor: Birdeye x402 as data source → our API as x402-gated service
- Escrow: x402 triggers escrow creation → funds lock → work completes → settle
- Agent-to-agent: any agent can be both buyer and seller in the same workflow

**Lesson:** x402 is the "TCP/IP of agent payments." Build on the pattern, not the implementation.

---

### 3. The Keeper/Oracle Bridge — Connecting On-Chain to Off-Chain Intelligence

**Discovered in:** arc-hackathon GenLayer integration → applies to any AI oracle

Solidity can't call an LLM. Python can't settle on-chain. The bridge is a keeper.

```
On-chain event → Keeper picks up → Off-chain processing → Callback with result
```

**Pattern variants:**
- **GenLayer:** Keeper calls Intelligent Contract (Python) → LLM reads evidence → consensus → relay verdict
- **Chainlink-style:** Oracle node observes off-chain → reports on-chain
- **Optimistic:** Anyone can submit result → challenge period → finality

**What we learned:**
- Challenge period is non-negotiable — optimistic systems need appeal windows
- Keeper trust model: start trusted (hackathon), migrate to trustless (production via LayerZero / native bridge)
- The metadata/URL pattern (evidence stored off-chain, reference on-chain) is universal

**Lesson:** Every "AI on-chain" project is actually "AI off-chain + bridge." Design the bridge first.

---

### 4. The Dual-Pricing Model — USDC Base, $TECH Premium

**Discovered in:** agent-economy-solana, AAE tokenomics → validated in escrow pricing

Two price points, one system:
- **USDC:** Standard price, no friction, universal access
- **$TECH:** 20-30% discount, REP-gated tiers, loyalty play

**Applied to escrow:**
- Basic dispute resolution (human arbiter): USDC flat fee ($5-20)
- AI oracle adjudication: $TECH only (premium service, REP discount)
- Escalation from Tier 1 → Tier 2: $TECH staking required

**Why it works:**
- USDC brings in anyone — no token acquisition friction
- $TECH discount creates demand for the token without forcing it
- REP levels gate premium features — "more winners than losers" brand

**Lesson:** Never force token usage. Make it a better deal, not a requirement.

---

### 5. The Demo Pattern — Three Payments, One Workflow

**Discovered in:** arc-hackathon pitch → standardized for all demos

Every demo should show **three payments in one workflow**. This proves the full stack:

```
Agent A (buyer)              Middleware               Agent B (seller)         Data API
    |                            |                          |                     |
    |--- request --------------->|                          |                     |
    |<-- 402 {price} -----------|                          |                     |
    |--- X-PAYMENT ------------>|                          |                     |
    |                           |-- create_escrow() -------|                     |
    |                           |                          |-- GET /data -------->|
    |                           |                          |<-- 402 {$0.01} -----|
    |                           |                          |-- X-PAYMENT -------->|
    |                           |                          |<-- 200 + data -------|
    |                           |                          |                     |
    |                           |          [work completes]                      |
    |                           |-- validate_work() ------|                     |
    |                           |-- release_funds() ----->|                     |
    |<-- 200 OK + result -------|                          |                     |
```

**Three payments. One workflow. Zero billing infrastructure.**

1. Agent A → Agent B (escrow + x402) = main transaction
2. Agent B → Data API (x402) = sub-payment for data
3. Escrow settles = on-chain finality

**Why this works for judges:**
- Shows agent-to-agent commerce (not just human-to-contract)
- Proves x402 works as payment trigger
- Demonstrates full lifecycle: request → pay → escrow → work → dispute → settle
- Each payment is real, tiny, and instant — exactly what agents need

**Lesson:** One payment is a demo. Three payments in one workflow is a product.

---

### 6. The Chain Selection Matrix — Right Chain for Right Job

**Discovered across:** Arc, Solana, Base, BNB comparisons

| Chain | Best For | Weakness | Our Play |
|-------|----------|----------|----------|
| **Solana** | Micro-transactions, speed (400ms), low gas | No Solidity, different dev model | Colosseum — "where agent micro-TXs make economic sense" |
| **Base** | EVM compat, Coinbase ecosystem, x402 market | Higher gas than Solana | x402 settlement, Coinbase integration |
| **Arc (Circle)** | USDC native, x402 batching SDK | New (unproven), settle broken until Apr 22 | USDC settlement layer |
| **BNB Chain** | GenLayer lives here, Apolo proven | Not our ecosystem | Reference architecture, not primary |
| **Avalanche** | Subnets, custom VMs | Lower mindshare | Future: dedicated agent subnet? |

**Decision framework:**
- Micro-transactions (< $0.10): Solana (gas economics)
- USDC settlement: Base or Arc (native USDC)
- AI adjudication: BNB (GenLayer) or cross-chain via bridge
- Demo/judges: whatever chain the hackathon is for

**Lesson:** Don't be chain-maxi. Be chain-pragmatic. Use the right tool for the right job. That's what "modular" means.

---

## The Unifying Pitch

> **"Modular AI agents. Your chain, your oracle, your rules."**

Every project we ship reinforces this:
- **Escrow:** Swappable resolvers (human ↔ AI ↔ multisig)
- **Payments:** x402 pattern works on any chain
- **Data:** Birdeye / custom APIs, pay-per-call
- **Adjudication:** GenLayer / human / custom — plug in what you need
- **Tokenomics:** USDC for access, $TECH for premium, REP for trust

We're not building one product. We're building the **protocol layer for agent commerce.** Each hackathon submission is a proof point.

---

## What to Reuse Across Projects

| Component | arc-hackathon | agent-escrow-solana | kite-agent-commerce | Future |
|-----------|:---:|:---:|:---:|:---:|
| IResolver interface | ✅ built | port to Anchor | N/A | standard everywhere |
| x402 payment flow | ✅ built | port to PayAI | ✅ built | universal pattern |
| Keeper bridge pattern | ✅ designed | same pattern | N/A | any AI oracle integration |
| Dual pricing model | apply | apply | apply | $TECH + USDC everywhere |
| Three-payment demo | ✅ scripted | adapt for Solana | ✅ built | standard demo format |

---

## Revenue Model (Consistent Across Projects)

| Revenue Stream | USDC | $TECH | REP Gate |
|---------------|------|-------|----------|
| API calls (x402) | Full price | 20-30% off | None |
| Escrow creation | Flat fee | Discounted | None |
| Human dispute resolution | $5-20 | Discounted | None |
| AI oracle adjudication | N/A | Required | Level 2+ |
| Escalation (Tier 1→2) | N/A | Required | Level 3+ |
| Custom resolver deployment | N/A | Premium | Level 4+ |

---

## Next Actions

1. **DMOB:** Refactor DisputeResolver to IResolver — this pattern must be proven before Colosseum
2. **YoYo:** Revenue projections using this model — due May 1
3. **Desmond:** Pitch script should lead with "modular infrastructure" — not "we built an escrow"
4. **All:** Every new project asks: "Does this follow the IResolver pattern? Does it use x402? Is it chain-agnostic?"

---

*This is our playbook. Update it every time we learn something new. The patterns are more valuable than any single project.*
