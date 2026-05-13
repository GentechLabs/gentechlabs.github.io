# Modular Agent Architecture — Cross-Project Patterns
**Discovered:** 2026-04-21
**Status:** Living document — update as patterns emerge

---

## The Core Insight

Working across Arc, Birdeye BIP, and AgentEscrow, the same architectural pattern kept winning: **every component is a swappable module behind an interface.** This wasn't planned top-down — it emerged from building real things in parallel.

---

## Patterns That Recurred

### 1. Interface-First Design
Every time we defined the interface before the implementation, the project moved faster and shipped cleaner.

| Project | Interface | Implementations |
|---------|-----------|-----------------|
| AgentEscrow | `IResolver` | Custom DisputeResolver → GenLayer oracle |
| LP Monitor | Data fetcher layer | DexScreener → Birdeye x402 |
| Payment flow | x402 HTTP 402 | API key → USDC on Solana → USDC on Base |

**Rule:** If you can't swap it, you over-coupled it.

### 2. Graceful Degradation as Default
Every data source or service should have a fallback. The LP Monitor v2 proves this — Birdeye is the upgrade path, DexScreener is the safety net. No single point of failure.

**Pattern:** `try premium → fallback free → alert if both fail`

### 3. Payment Abstraction
The x402 protocol taught us this: the payment method should be invisible to the agent logic. Whether it's an API key, a USDC micropayment, or an escrow lock — the agent just calls `get_data()` and the payment layer handles the rest.

**Layer stack:**
```
Agent Logic
    ↓
[Payment Router] ← swap this
    ↓
[Data Provider]  ← swap this
    ↓
[Chain/Settlement] ← swap this
```

### 4. Resolver Pattern (Not Just Disputes)
The `IResolver` interface isn't just for escrow disputes. The same pattern works for:
- **Data verification** — "Is this token safe?" (GenLayer, custom rules, ML model)
- **SLA checking** — "Was the service delivered?" (Apolo pattern)
- **Price oracles** — "What's the real price?" (Chainlink → Birdeye → custom)

One interface. Multiple trust models. User picks.

### 5. "Works Now, Scales Later"
Every submission should ship as Tier 1 (battle-tested Solidity, no external deps) with a clear Tier 2 upgrade path (AI oracle, cross-chain, advanced features). Judges and users both respond to this — it's pragmatic, not vaporware.

---

## The Tagline Emerged From This

> **"Swap the chain, keep the agent."**

This works because it's literally true — the architecture proves it, not just marketing.

---

## Where This Applies

| Context | How modular architecture helps |
|---------|-------------------------------|
| Hackathon submissions | Same codebase, multiple submissions, different angles |
| Product positioning | "Your chain, your oracle, your rules" |
| Agent development | Hermes agents are already modular (skills, tools, channels) |
| Investor pitch | Infrastructure play, not single-chain bet |
| Open source | Community can add resolvers, data sources, chains |

---

## Lessons Learned

1. **Define interfaces before implementations** — saved us rework on both AgentEscrow and the LP Monitor
2. **Free tier first** — DexScreener as fallback meant we could build and test without API keys
3. **Config over code** — `birdeye-config.json` swap changes behavior, no redeploy needed
4. **Test with the fallback path** — if it works on free data, it works on paid data. Reverse isn't true.
5. **The module boundary IS the product** — each swappable piece is a potential partnership or integration point

---

*Documented by Hermes — emerged from parallel work on Arc, Birdeye BIP, and AgentEscrow (Apr 18-21, 2026)*
