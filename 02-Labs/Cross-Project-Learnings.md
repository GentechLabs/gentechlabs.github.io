# Cross-Project Learnings: Common Architecture Patterns

*Documented April 21, 2026 — from building across Arc, Colosseum, and LP Monitor submissions.*

---

## The Thesis

We're not building three separate hackathon projects. We're building **one modular architecture** that ships three demos. The patterns that repeat across projects are the ones worth defending.

---

## Pattern 1: Pluggable Oracle Adapters

**Discovered in:** Arc hackathon (DisputeResolver + GenLayerOracle)

The `IAdjudicationOracle` interface turned out to be chain-agnostic:
- GenLayer (AI adjudication on BNB Chain)
- Chainlink Functions (battle-tested oracle, any chain)
- Custom ZK proofs (future — provable SLA compliance)

**Lesson:** If your contract interfaces an external system, make it an interface, not an implementation. The moment you need to swap providers, you're already done.

**Reusable for:** Any project that needs offchain data or computation fed onchain.

---

## Pattern 2: Two-Tier Resolution (Human + AI Fallback)

**Discovered in:** Arc hackathon (DisputeResolver human arbiter + optional oracle opt-in)

- Tier 1: Human arbiter — works today, no external dependencies
- Tier 2: AI oracle — opt-in, speed + scale for high-volume disputes

**Lesson:** Don't make AI the only path. Judges and users trust systems that degrade gracefully. "Works out of the box, scales with AI" is a pitch, not just a feature.

**Reusable for:** Any system where AI augments human judgment (not replaces it).

---

## Pattern 3: x402 as Universal Payment Trigger

**Discovered in:** Arc (x402 → escrow), LP Monitor (x402 → Birdeye API calls), Colosseum (x402 → agent micro-transactions)

x402 (HTTP 402 "Payment Required") is the consistent entry point:
- Arc: `POST /api/task` → x402 payment → escrow lock → work → resolve
- LP Monitor: Agent hits Birdeye via x402 pay-per-call (50 calls min for hackathon)
- Colosseum: Solana's 400ms finality makes x402 micro-payments viable

**Lesson:** x402 is the "glue protocol" — it's the same trigger whether you're paying $0.01 for an API call or $1000 for an agent service. Build the payment handler once, plug in any backend.

**Reusable for:** Any agent-to-agent or agent-to-API payment flow.

---

## Pattern 4: Escrow as the Trust Layer

**Discovered in:** Arc (AgentEscrow), cross-project analysis of Agentic Market ($424K daily, zero dispute resolution)

Every x402 payment today is "pay and pray":
- Agentic Market: no escrow, no disputes, no recourse
- Apolo: escrow + GenLayer, but locked to BNB Chain
- Our approach: escrow + pluggable oracle + multi-chain

**Lesson:** Escrow isn't a feature — it's the missing infrastructure layer. The market is growing fast (Agentic Market volume) but nobody has solved trust yet.

**Reusable for:** Any service marketplace, agent commerce, or SLA-backed payment.

---

## Pattern 5: Interface-First Development

**Discovered in:** All projects — consistently the pattern that saves the most time.

Build the interface, test the interface, then build implementations:

| Interface | Implementations |
|-----------|----------------|
| `IAdjudicationOracle` | GenLayerOracle, ChainlinkOracle (pluggable) |
| `IERC20` | USDC, MockUSDC, any SPL/token wrapper |
| x402 protocol | Base (Coinbase CDP), Solana (PayAI), Arc (Circle) |

**Lesson:** Interfaces are the abstraction layer that lets you demo on any chain. Judges don't care about your implementation — they care that the architecture generalizes.

---

## Pattern 6: Security as a Feature, Not a Checklist

**Discovered in:** All projects — every contract review flagged the same patterns.

Non-negotiable patterns that keep showing up:
- `ReentrancyGuard` on every external call that moves funds
- `checks-effects-interactions` — no exceptions
- `OpenZeppelin` base contracts always
- Nonce-based replay protection (x402 payments)
- Access control on every admin function

**Lesson:** Security patterns compound. The same `ReentrancyGuard` pattern that protects escrow also protects oracle callbacks also protects LP withdrawals. Learn it once, apply everywhere.

---

## The Meta-Pattern: Modular Everything

```
┌─────────────────────────────────────────────────┐
│              Your Architecture                   │
├─────────────────────────────────────────────────┤
│  Payment Layer    │ x402 (Base, Solana, Arc)    │
│  Escrow Layer     │ AgentEscrow (any chain)      │
│  Oracle Layer     │ IAdjudicationOracle (swap)   │
│  Settlement Layer │ Chain-specific (swap)         │
└─────────────────────────────────────────────────┘
```

Every layer is swappable. Every layer has been tested on at least one chain. The pattern is the product.

---

## What to Tell Judges

> "We didn't build three projects. We built one modular system and proved it works on three chains with three different oracle providers. Swap the chain, keep the agent."

---

*Last updated: April 21, 2026*
*Projects: Arc Hackathon, Colosseum, LP Monitor*
