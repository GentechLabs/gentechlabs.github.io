---
name: connector-model-pricing
description: Evaluate x402/pay-per-use APIs and model them into subscription tiers with bundled data pools. Framework for connector-layer monetization.
category: strategies
tags: [x402, monetization, subscription, pricing, strategy]
---

# Connector Model — x402 API to Subscription Tier Analysis

## When to Use
When a new x402-native or pay-per-use API provider enters the ecosystem and you need to evaluate how to integrate it into Gentech's subscription model as a **connector layer** (not the data provider).

## The Framework

### Step 1: Map the API's Economics
- Cost per request (x402 price in USDC)
- Settlement chain (Base, Solana, etc.)
- Rate limits or free tiers
- Available endpoints and data quality
- WebSocket vs REST (streaming vs polling)

### Step 2: Calculate Usage Scenarios
```
Budget     → Requests     → Use Case
$3/mo      → ~1,000       → Casual / spot checks
$15/mo     → ~5,000       → Active monitoring
$45/mo     → ~15,000      → Heavy / 500 queries/day
$150/mo    → ~50,000      → Institutional / multi-agent
```
Adjust the cost per request to get real numbers.

### Step 3: Model Subscription Tiers with Data Pools
Key insight: **Bundle data credits into tiers, don't gate data access.**

| Tier | Price | Data Pool | Calls | Value Proposition |
|---|---|---|---|---|
| Free | $0 | ~$0.50 | ~150 | Loss leader, hook users |
| Entry | $10 | $3 | ~1,000 | Dedicated agent + execution |
| Pro | $30 | $10 | ~3,333 | Full suite + multi-source |
| Power | $50 | $20 | ~6,666 | Multi-agent + API + BYOK |
| PAYG | $0.005/call | — | — | Funnel to subscriptions |

**Critical assumptions to model:**
- Avg data pool utilization (use 45% as baseline)
- Free tier absorption cost
- PAYG markup (typically 40-66% over provider cost)

### Step 4: Calculate Profit Margins
```python
# Per tier
revenue = users * price
used_calls = pool * utilization_rate
data_cost = users * used_calls * provider_cost_per_call
profit = revenue - data_cost
margin = profit / revenue * 100

# Free tier is a loss leader
if price == 0:
    data_cost = users * pool * provider_cost_per_call
```

### Step 5: Identify the Margin Levers
1. **Unused data pool** = 100% margin (users don't use full allocation)
2. **Multi-provider routing** = drops blended cost (route to cheapest source)
3. **Free endpoint fallback** = some queries cost $0 (basic data, RPC calls)
4. **Conversion rate** = free→paid is the biggest revenue driver

### Step 6: Multi-Provider Routing
Don't depend on one provider. Build a router that picks the cheapest/best source:
- Birdeye → Solana token data, trending, new listings
- CoinGecko → Global prices, market data
- Free RPCs → Basic on-chain data
- Custom endpoints → LP positions, protocol-specific

Blended cost drops from $0.003 to ~$0.001 when routing intelligently.

## Project Impact Checklist
When a new x402 provider lands, check:
- [ ] Does it improve YoYo's data pipeline? (cheaper, better data)
- [ ] Does it strengthen the hackathon pitch? (reference implementation)
- [ ] Does it enable a new integration point? (see x402-integration-map.md)
- [ ] Does it change subscription tier economics? (run the numbers)
- [ ] Should we prototype an integration? (agent script to test)

## Discussion Template (for HQ/Mess Hall)
Save to `11-Mess Hall/` with:
1. Provider name + economics
2. Profit projections (Y1 conservative, Y2 growth)
3. 3-5 discussion points (routing, free tier, BYOK, timing)
4. Reference files in vault

## Pitfalls
- Don't overestimate utilization — 45% is realistic, 80%+ is fantasy
- Free tier costs add up at scale — cap queries, not just budget
- WebSocket limitations mean polling costs can spike for real-time use cases
- BYOK increases retention but kills data markup margin — offer it only on top tier
- Marketplace/escrow revenue is speculative until you have users — don't count it in Y1

## Files to Update
- `03-Strategies/connector-model-profit-projections.md` — profit analysis
- `11-Mess Hall/` — HQ discussion thread
- `06-Content/research/x402-ecosystem.md` — ecosystem tracker
- `03-Strategies/x402-integration-map.md` — integration points

## Tags
#x402 #monetization #subscription #connector-model #strategy #pricing
