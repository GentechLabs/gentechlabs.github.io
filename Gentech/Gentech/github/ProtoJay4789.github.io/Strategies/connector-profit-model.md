# AAE Connector Profit Model — Birdeye x402

**Date:** April 21, 2026
**Author:** YoYo (Strategies)
**Status:** DRAFT — open for team input

---

## Core Thesis

AAE sits between users and x402 data providers (Birdeye today, more tomorrow). We bundle data into tiers, add agent analysis, and capture value through:
1. Tier subscriptions (covers cost + small margin)
2. Agent services (pure margin)
3. $TECH burn mechanism (token value capture)
4. Overage pricing (margin on excess usage)

---

## Cost Floor (What We Pay)

**Birdeye x402:** $0.003/request, USDC, Base or Solana settlement

### Current YoYo Data Spend (CMC Crons)
- 13 cron jobs running CoinMarketCap API
- Free tier (limited)
- Running every 2h = ~156 calls/day = ~4,680/month
- **Cost: $0** (free tier) but unreliable, rate-limited

### Birdeye Equivalent
- 4,680 requests/month × $0.003 = **$14.04/month**
- But: full API access, reliable, real-time, no rate limits
- **Net upgrade:** More data, more reliable, ~$14/month

---

## Revenue Model — Three Scenarios

### Scenario A: Conservative (Pass-Through + Small Markup)

| Tier | Price | Quota | Our Cost | Gross Profit | Margin |
|------|-------|-------|----------|-------------|--------|
| 🌱 Free | $0 | 50/mo | $0.15 | -$0.15 | Loss leader |
| ⚔️ Proven | $5 | 1,000/mo | $3.00 | $2.00 | 40% |
| 🏆 Graduate | $15 | 5,000/mo | $15.00 | $0.00 | 0% |
| 🔥 Elite | $40 | 15,000/mo | $45.00 | -$5.00 | -12% |

**Break-even per user:** 1,667 requests/month ($5 tier)
**Assumption:** Average user uses 60% of quota

Adjusted with 60% avg usage:
| Tier | Our Actual Cost | Gross Profit | Margin |
|------|----------------|-------------|--------|
| ⚔️ Proven | $1.80 | $3.20 | **64%** |
| 🏆 Graduate | $9.00 | $6.00 | **40%** |
| 🔥 Elite | $27.00 | $13.00 | **33%** |

**Much healthier with realistic usage.**

---

### Scenario B: Growth (Undercut to Acquire)

Charge below cost on top tiers, make it up on volume + $TECH:

| Tier | Price | Quota | Our Cost | Gross Profit |
|------|-------|-------|----------|-------------|
| 🌱 Free | $0 | 100/mo | $0.30 | -$0.30 |
| ⚔️ Proven | $3 | 1,000/mo | $3.00 | $0.00 |
| 🏆 Graduate | $10 | 5,000/mo | $15.00 | -$5.00 |
| 🔥 Elite | $25 | 15,000/mo | $45.00 | -$20.00 |

**Revenue captured elsewhere:**
- $TECH 20-30% discount → drives token demand → burn → value
- Agent marketplace fees (5-10% on signal trades)
- Strategy marketplace (GEPA-evolved strategies, 10% platform fee)
- Overages at $0.008/request (167% markup)

**This is the "more winners" play — users feel they're getting a deal.**

---

### Scenario C: Hybrid (Recommended)

Data at cost. Intelligence at premium.

| Tier | Data Quota | Data Cost to Us | Price | What We Actually Sell |
|------|-----------|----------------|-------|----------------------|
| 🌱 Free | 100/mo | $0.30 | $0 | Raw data only, no agent analysis |
| ⚔️ Proven | 1,000/mo | $3.00 | $5 | Data + basic agent summaries |
| 🏆 Graduate | 5,000/mo | $15.00 | $15 | Data + full agent analysis + signals |
| 🔥 Elite | 15,000/mo | $45.00 | $40 | Data + autonomous agent + priority |

**Margin source: Agent services, not data pass-through.**
- Proven: Pay $2 for agent summaries (cost: ~$0.50 inference)
- Graduate: Pay for signal generation (cost: ~$2 inference)
- Elite: Pay for autonomous execution (cost: ~$5 inference + gas)

**Blended margins:**
- Proven: 60% ($2 profit on $5, agent cost ~$0.50)
- Graduate: 47% ($7 profit on $15, agent cost ~$3)
- Elite: 28% ($11 profit on $40, agent cost ~$9)

---

## Scale Projections

### Conservative (Scenario A, 60% usage)
| Users | MRR | Monthly Data Cost | Gross Profit |
|-------|-----|------------------|-------------|
| 100 | $1,500 | $540 | $960 |
| 500 | $7,500 | $2,700 | $4,800 |
| 1,000 | $15,000 | $5,400 | $9,600 |
| 5,000 | $75,000 | $27,000 | $48,000 |
| 10,000 | $150,000 | $54,000 | $96,000 |

*Assumes 40% Free, 35% Proven, 20% Graduate, 5% Elite distribution*

### Hybrid (Scenario C — Recommended)
| Users | MRR | Data Cost | Agent Cost | Gross Profit | Margin |
|-------|-----|-----------|-----------|-------------|--------|
| 100 | $1,200 | $400 | $200 | $600 | 50% |
| 500 | $6,000 | $2,000 | $1,000 | $3,000 | 50% |
| 1,000 | $12,000 | $4,000 | $2,000 | $6,000 | 50% |
| 5,000 | $60,000 | $20,000 | $10,000 | $30,000 | 50% |
| 10,000 | $120,000 | $40,000 | $20,000 | $60,000 | 50% |

*Distribution: 30% Free, 40% Proven, 25% Graduate, 5% Elite*

---

## $TECH Flywheel Impact

When users pay with $TECH (20-30% discount):
- Platform receives $TECH
- 70% burned (per TechPaymentRouter design)
- 30% to treasury

At 50% $TECH adoption:
- Revenue drops ~12.5% (avg 25% discount on half of payments)
- But: $TECH burn creates scarcity → token price appreciation
- Users holding $TECH for discounts = sticky retention

**Net effect:** Short-term margin compression, long-term token value + retention

---

## Multi-Provider Expansion

Birdeye is provider #1. The model scales by adding x402 providers:

| Provider | Cost/Request | Data Type | Status |
|----------|-------------|-----------|--------|
| Birdeye | $0.003 | Token market data | ✅ Live |
| Corbits | Varies | API marketplace | Research |
| PayAI | Varies | Solana data + compute | Research |
| Dexter | Varies | Cross-chain discovery | SDK available |
| Custom | $0 | Proprietary analysis | Our agents |

**As we add providers, our bundles get more valuable at similar cost.**
- Birdeye alone: $0.003/request for market data
- Birdeye + Corbits + PayAI: $0.005/request for multi-source intel
- **Same tier price, more value = better margins over time**

---

## Key Risks

1. **Birdeye raises prices** — Mitigation: multi-provider strategy, don't depend on single source
2. **Low usage = margin trap** — Mitigation: soft caps, overage pricing, usage-based tiers
3. **$TECH discount eats margin** — Mitigation: dynamic discount tied to market price, floor at 15%
4. **Free tier abuse** — Mitigation: wallet-based quotas, REP gates, one free tier per address

---

## Recommendation

**Go Scenario C (Hybrid).** Here's why:
1. Data at cost = trust play, aligns with "more winners"
2. Agent services = real margin, defensible moat
3. $TECH flywheel captures long-term value
4. Scales to 10K+ users at 50% margin
5. Multi-provider expansion increases bundle value without increasing price

**First milestone:** 100 paying users × $12 ARPU = $1,200 MRR
**Target:** 1,000 users × $12 ARPU = $12,000 MRR at 50% margin

---

## Next Steps
- [ ] Get Birdeye subscription pricing for crossover analysis
- [ ] Model $TECH burn rate under Scenario C
- [ ] DMOB: TechPaymentRouter integration with x402 flow
- [ ] Design tier UI/UX — what does each tier actually see?
- [ ] Prototype: YoYo querying Birdeye via x402 (cost validation)

---

#AAE #strategy #pricing #x402 #economics
