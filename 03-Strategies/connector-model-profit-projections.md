# Connector Model — Profit Projections & Discussion

**Date:** 2026-04-21
**Status:** DRAFT — pending HQ discussion
**Origin:** Birdeye x402 analysis → subscription model evolution

---

## The Insight

We don't need to be the data provider. We're the **connector layer** — users subscribe to our agent, agent handles x402 micropayments to Birdeye, CoinGecko, and other providers behind the scenes.

**User pays us → Agent pays data providers → User gets value-add (strategy, execution, LP mgmt)**

---

## Tier Model

| Tier | Price/mo | Data Pool | Calls | Value Proposition |
|---|---|---|---|---|
| Explorer | Free | $0.50 | ~150 | Hook — community, read-only, 5 queries/day |
| Agent | $10 | $3 | ~1,000 | Dedicated agent, execution, auto-routing |
| Pro | $30 | $10 | ~3,333 | Full suite, LP mgmt, multi-source routing |
| Studio | $50 | $20 | ~6,666 | Multi-agent, API access, BYOK option |
| PAYG | $0.005/call | — | — | No commitment, funnel to subscriptions |

---

## Profit Projections

### Year 1 (Conservative)
- 640 total users
- $2,592/mo revenue, $583/mo data cost
- **$2,009/mo profit (77% margin)**
- **$24,102/yr**

### Year 2 (Growth)
- 2,700 total users
- $12,810/mo revenue, $2,655/mo data cost
- **$10,155/mo profit (79% margin)**
- **$121,861/yr** (+ marketplace & escrow)

### Assumptions
- 45% avg data pool utilization
- 30% of users also buy PAYG
- Free tier = loss leader ($188-750/mo cost)
- Blended data cost: $0.0025/call (multi-provider routing)

---

## Why Margins Are 77-79%

1. Data is the cheapest input ($0.003/call)
2. Subscription prices are 10-50x data cost
3. Users don't use full data pool (unused = 100% margin)
4. Multi-provider routing drops blended cost below $0.001
5. Value-add (agent execution, strategies) has near-zero marginal cost

---

## Additional Revenue Streams (Y2)

- **Agent Marketplace:** ~$15/mo (50 sales × $50 avg × 30% cut)
- **Escrow Platform Fees:** ~$75/mo (200 jobs × $5 × 7.5%)
- **Combined Y2 total: ~$123K/yr**

---

## Key Levers

1. Free → Agent conversion rate (each = $8.88 profit/mo)
2. Data pool utilization < 50% (wider margin)
3. Multi-provider routing (lower blended cost)
4. Marketplace volume growth
5. Enterprise/white-label deals ($500-2000/mo)

---

## Open Questions for HQ

1. Should we build multi-provider routing now or after hackathon?
2. Free tier data limit — 150 calls enough or too generous?
3. BYOK (bring your own keys) for Studio tier — does it cannibalize our margin or increase retention?
4. Marketplace timing — ship with MVP or Phase 2?

---

#strategy #monetization #x402 #connector-model
