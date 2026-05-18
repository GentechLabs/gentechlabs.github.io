# AAE Connector Economics — Revenue Model

**Created:** April 21, 2026
**Status:** Discussion / HQ Review
**Context:** Birdeye x402 integration sparked the connector-as-revenue-stream concept

---

## Core Concept

AAE acts as a **connector marketplace** — users subscribe to AAE tiers that include data credits for various providers (Birdeye, etc.). AAE pays providers via x402 on the backend, users never touch API keys.

```
User → AAE Tier (subscription) → Connector → x402 → Provider (Birdeye, etc.)
         ↑                           ↑
      Revenue                      Cost
```

---

## Provider Cost Basis

| Provider | x402 Cost/Request | Settlement | Notes |
|----------|------------------|------------|-------|
| **Birdeye** | $0.003 | Base + Solana, ~2s | Token data, trades, security, wallets |
| *Future providers* | TBD | TBD | Each x402-native provider = new connector |

---

## Tier Model

| Tier | Monthly | Data Credits | Connectors | Overage Rate |
|------|---------|-------------|------------|--------------|
| **Free** | $0 | 100 calls | Birdeye (basic endpoints only) | Blocked |
| **Pro** | $29 | 5,000 calls | Birdeye + 2 more | $0.004/call |
| **Agency** | $99 | 25,000 calls | All connectors | $0.003/call |
| **Enterprise** | Custom | Custom | All + custom integrations | Negotiated |

---

## Profit Modeling

### Worst-Case (All Credits Used)

| Tier | Revenue | Max Cost (Birdeye) | Gross Margin | Margin % |
|------|---------|-------------------|--------------|----------|
| Free | $0 | $0.30 | -$0.30 | Loss leader |
| Pro | $29 | $15.00 | $14.00 | 48% |
| Agency | $99 | $75.00 | $24.00 | 24% |

### Realistic (Avg 60% Credit Utilization)

Users don't max out every month. Average utilization ~60% is typical for bundled credits.

| Tier | Revenue | Avg Cost | Gross Margin | Margin % |
|------|---------|----------|--------------|----------|
| Free | $0 | $0.18 | -$0.18 | Loss leader |
| Pro | $29 | $9.00 | $20.00 | **69%** |
| Agency | $99 | $45.00 | $54.00 | **55%** |

### Overage Revenue (Pure Profit Boost)

| Overage Rate | Provider Cost | Margin/Call | Margin % |
|-------------|--------------|-------------|----------|
| $0.004 (Pro) | $0.003 | $0.001 | 33% |
| $0.003 (Agency) | $0.003 | $0.00 | Break-even (retention tool) |

### Revenue Projections (Birdeye Connector Only)

| Users | Pro (70%) | Agency (30%) | Monthly Revenue | Avg Cost | Gross Profit |
|-------|-----------|-------------|-----------------|----------|-------------|
| 100 | 70 | 30 | $4,980 | $2,220 | **$2,760** |
| 500 | 350 | 150 | $24,900 | $11,100 | **$13,800** |
| 1,000 | 700 | 300 | $49,800 | $22,200 | **$27,600** |
| 5,000 | 3,500 | 1,500 | $249,000 | $111,000 | **$138,000** |

*Assumes 60% avg utilization, Birdeye only, no overage revenue included.*

---

## Multi-Connector Flywheel

Each new x402 provider = new connector = more value per tier = higher conversion.

| Connectors | Value Prop | User Reach |
|-----------|-----------|------------|
| 1 (Birdeye) | Crypto token data | Solana/Base traders |
| 3 (+ DeFi + NFT) | Full market coverage | All crypto traders |
| 5 (+ Social + AI) | Cross-domain intelligence | Broader Web3 + AI |
| 10+ | "Stripe for AI agent data" | Enterprise + agents |

**The more connectors, the more users you accommodate** — each one expands the addressable market without increasing fixed costs.

---

## Why x402 Makes This Possible (Traditional vs x402)

| Factor | Traditional API | x402 Connector |
|--------|----------------|----------------|
| Upfront cost | Negotiate deals, prepay credits | $0 — pay per request |
| Onboarding | API keys, KYC, approval | Instant — just add endpoint |
| Scaling risk | Overpay for unused credits | Cost = exact usage |
| New provider | Weeks of integration | Hours (standard x402 flow) |
| Margin model | Fixed cost, hope users use it | Variable cost, margin guaranteed |

---

## Connector Plugin Spec (Draft)

```yaml
connector:
  name: birdeye
  version: "1.0"
  provider: Birdeye Data Services
  payment:
    method: x402
    currency: USDC
    networks: [base, solana]
    cost_per_request: 0.003
  endpoints:
    - id: token_price
      path: /defi/price
      cost_weight: 1
    - id: token_security
      path: /defi/token_security
      cost_weight: 1
    - id: wallet_portfolio
      path: /wallet/portfolio
      cost_weight: 2  # heavier endpoint
  limits:
    rate_limit: 100/min
    burst: 20
```

---

## Next Steps

- [ ] Validate Birdeye subscription tiers (for crossover analysis)
- [ ] Define connector plugin spec format (YAML vs JSON)
- [ ] Map which Birdeye endpoints AAE agents need most
- [ ] Identify next 2-3 x402 providers for connector expansion
- [ ] Design AAE dashboard for connector management
- [ ] Model Agency tier pricing with multiple connectors

---

## HQ Notes

This is a **platform play**, not just a tool. Every x402 provider that goes live is a potential connector. AAE becomes the middleware layer between AI agents and data providers — the "Stripe for agent commerce" positioning.

Key insight: x402 removes the biggest blocker to connector marketplaces (upfront API costs + key management). Traditional aggregator models require heavy partnerships. x402 makes it plug-and-play.
