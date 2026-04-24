---
title: Trade Off Platform Architecture
date: 2026-04-21
tags: [trade-off, architecture, platform]
---

# The Trade Off — Canonical Architecture Stack

*(Dropped by Jordan Apr 21, 2026)*

## The Stack (top to bottom)

1. 🎮 **"The Trade Off"** — the product people see (ghost trading, skill-based DeFi competition)
2. 💰 **Revenue model** — launch fees (hook) + swap fees (river) + extensions (recurring) + marketplace (cut)
3. 🧠 **Rep system** — engagement tracking, non-transferable reputation scores
4. 💎 **Dual-payment** — USDC full price / $TECH discount (token sink mechanism)
5. 🔗 **Multi-chain adapter** — AVAX first, expand outward
6. 🏗️ **AgentPaymentFlow** — core contract, chain-agnostic foundation

## Revenue Streams Breakdown

| Stream | Type | Description |
|--------|------|-------------|
| Launch Fees | Hook | One-time onboarding revenue |
| Swap Fees | River | Continuous flow from trading activity |
| Extensions | Recurring | Premium features, subscriptions |
| Marketplace | Cut | Percentage of marketplace transactions |

## Key Design Decisions

- **Non-transferable rep** — prevents gaming, ties reputation to engagement
- **$TECH as token sink** — dual-payment creates real demand, not speculation
- **Chain-agnostic core** — AgentPaymentFlow abstracts away chain specifics
- **AVAX first** — strategic entry point, lower fees, established DeFi ecosystem

## Related Projects

- `02-Labs/tech-payment-router/` — Foundry project with DiscountCalculator, BurnSplitter, TechPaymentRouter
- `09-Green Room/trade-off-concept-brainstorm.md` — Original brainstorm with dynamic discount resolution
- `09-Green Room/AgentFi-Layer7-DeepDive.md` — Layer 7 economics architecture

## Security Considerations

- Flash loan manipulation on pricing
- Copy-trade routing exploits (malicious lead traders)
- Gas griefing on multi-hop operations
- Reputation sybil attacks (mitigated by non-transferability + engagement weighting)
