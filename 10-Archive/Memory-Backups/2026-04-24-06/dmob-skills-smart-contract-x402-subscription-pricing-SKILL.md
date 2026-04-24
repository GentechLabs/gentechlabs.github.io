---
name: x402-subscription-pricing
description: Build profitable subscription tiers on top of x402 pay-per-request APIs using blended connector cost modeling
category: smart-contract
tags: [x402, pricing, subscription, aggregator, revenue]
---

# x402 Subscription Pricing — Aggregator Tier Model

Reusable approach for building subscription tiers on top of x402 pay-per-request APIs. Turns raw per-request costs into bundled, profitable tiers.

## When to Use
- Building a platform that aggregates multiple x402-gated APIs
- Designing subscription tiers where some connectors are cheap (internal infra) and others expensive (third-party like Birdeye)
- Modeling profit margins for agent-facing service marketplaces

## The Core Insight
**Don't pass through raw x402 costs.** If every request costs $0.003 (e.g., Birdeye), heavy tiers lose money. Instead, compute a **blended cost** across all connectors — most requests hit cheap/free internal infra, only a minority hit expensive external APIs.

## Steps

### 1. Map connector cost profile
List every data source and its per-request cost:

| Connector | Cost/Request | Expected Usage Share |
|---|---|---|
| Birdeye (external API) | $0.003 | 30% |
| LP Monitoring (own infra) | $0.0001 | 25% |
| Risk Scoring (own compute) | $0.0005 | 20% |
| Cached content | $0.0001 | 15% |
| Other external APIs | $0.002 | 10% |

**Blended cost** = Σ(cost × share) ≈ $0.0011

### 2. Design tiers around blended cost
Set price tiers so revenue per request > blended cost:

| Tier | Price/mo | Allowance | Avg Usage | Blended Cost | Margin |
|---|---|---|---|---|---|
| Basic | $15 | 5K | 3K | $3.30 | 78% |
| Pro | $50 | 25K | 15K | $16.50 | 67% |
| Power | $150 | 100K | 60K | $66.00 | 56% |

### 3. Model overages as profit maximizer
Overage rates (exceeding tier) should be higher than blended cost but lower than raw expensive API cost:

| Tier | Overage Rate | vs. Blended | Overage Margin |
|---|---|---|---|
| Basic | $0.005/call | $0.0011 | 78% |
| Pro | $0.003/call | $0.0011 | 63% |

Overages are the highest-margin revenue — power users who exceed limits are most profitable.

### 4. Account for token discounts
If platform has its own token (e.g., $TECH) with discount:
- Discount reduces per-transaction margin
- But creates token demand → treasury appreciates
- Net effect: lower per-txn margin, higher ecosystem value

### 5. Project revenue at user scale
```
Monthly Profit = (Users × Tier Price × Margin%) - Fixed Costs
```
Break-even point: typically 20-50 users depending on tier mix.

## Pitfalls
- **Don't assume all requests hit the expensive API.** Profile actual usage first.
- **Watch for cost creep.** If external API raises prices, blended cost rises. Mitigate with multiple providers per category.
- **Free tiers are traps** unless you control the cheap infra. A 500-request free tier costs ~$0.55 at blended rate — fine if conversions are high.
- **Connector diversity is the moat.** More cheap connectors = better blended cost = better margins.

## Tags
#x402 #pricing #subscription #aggregator #revenue #aee
