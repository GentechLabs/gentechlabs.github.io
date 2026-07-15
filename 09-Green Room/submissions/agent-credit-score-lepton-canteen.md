# Agent Credit Score — Lepton Canteen × Circle Submission

## Title: Building Agent Credit Score — On-Chain Reputation for the Autonomous Economy

AI agents now manage wallets, execute trades, and provide services. But there's no standardized way to assess their reliability. We built one.

### The Problem

AI agents are entering DeFi, but trust is the bottleneck. Every human asks: "How do I know you won't screw up?" Today the answer is "vibes" — check the GitHub, read the docs, hope for the best. That doesn't scale.

### The Solution: Agent Credit Score

A standardized, on-chain reputation system for AI agents, built on ERC-8004 identity standards.

**Architecture:**

- AgentIdentity (ERC-8004) — Agent UUID + wallet binding, verified identity
- AgentReputation — Task ledger, weighted completion rate, feedback aggregation
- CreditScore Oracle — Computes score from success rate, payment history, community feedback

**Scoring:**
- 0-1000 scale
- Weighted by: task completion rate (40%), payment history (30%), community feedback (20%), time since verified (10%)

**Integration Pattern:**

```javascript
// Gate payment by credit score
if (score.overall < 700) {
  require('x402 escrow');
} else {
  x402.instantPay();
}
```

### Why Circle + Canteen?

Circle's programmable payments and USDC infrastructure are natural complements. By integrating Agent Credit Score with Circle's developer tools, we enable:

1. **Trust-minimized agent payments** — Pay instantly when score > threshold
2. **Reduced fraud** — Low-score agents go through escrow
3. **Institutional readiness** — Standardized reputation unlocks treasury operations

### Status & Next Steps

- **Framework:** Defined, open sourcing July 2026
- **API:** Live at api.gentechlabs.net (x402 paid endpoint)
- **Smart contracts:** Interface finalized, deployment in progress on Base Sepolia
- **Partners:** Looking for integration partners — Circle builders welcome

Built by GenTech Labs. **Trust as Infrastructure.**
