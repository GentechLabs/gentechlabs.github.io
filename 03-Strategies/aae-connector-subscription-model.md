# AAE Connector Subscription — Profit Model

**Author:** DMOB (Labs)
**Date:** April 21, 2026
**Status:** Draft — pending YoYo financial review

---

## The Model

AAE = aggregator platform. Users pay AAE (subscription), AAE pays connectors (x402 per-request). Profit = spread + bundling margin.

---

## Tier Structure + Unit Economics

| Tier | REP | Price/mo | Request Allowance | Est. Avg Usage | Connector Cost | Gross Margin | Margin % |
|---|---|---|---|---|---|---|---|
| 🌱 Explorer | 0-50 | $15 | 5,000 | 3,000 | $9.00 | **$6.00** | 40% |
| ⚔️ Trader | 50-200 | $50 | 25,000 | 15,000 | $45.00 | **$5.00** | 10% |
| 🏆 Pro | 200-500 | $150 | 100,000 | 60,000 | $180.00 | **-$30.00** | -20% |
| 🔥 Fleet | 500+ | $300 | Unlimited | 150,000 | $450.00 | **-$150.00** | -50% |

### ⚠️ Problem: Pure Birdeye pass-through loses money at scale

If every request hits Birdeye at $0.003, heavy tiers are unprofitable. This is the classic aggregator trap.

---

## The Fix: Connector Mix Blended Cost

Not all connectors cost $0.003. Here's the real cost profile:

| Connector | Cost/Request | Usage Share |
|---|---|---|
| **Birdeye** (market data) | $0.003 | 30% |
| **LP Monitoring** (our infra) | $0.0001 | 25% |
| **Risk Scoring** (our compute) | $0.0005 | 20% |
| **Contract Auditor** (automated) | $0.001 | 10% |
| **Content/Research** (cached) | $0.0001 | 10% |
| **Custom/3rd-party** (varies) | $0.002 | 5% |

**Blended cost per request:** ~$0.0011 (not $0.003)

### Revised Unit Economics (Blended)

| Tier | Price/mo | Avg Requests | Blended Cost | Gross Margin | Margin % |
|---|---|---|---|---|---|
| 🌱 Explorer | $15 | 3,000 | $3.30 | **$11.70** | 78% |
| ⚔️ Trader | $50 | 15,000 | $16.50 | **$33.50** | 67% |
| 🏆 Pro | $150 | 60,000 | $66.00 | **$84.00** | 56% |
| 🔥 Fleet | $300 | 150,000 | $165.00 | **$135.00** | 45% |

**Much better.** The key insight: Birdeye is the expensive connector, but most agent requests are for LP monitoring, risk scoring, and cached data — which cost almost nothing on our infra.

---

## Revenue Projections by User Count

### Conservative (6-month ramp)

| Month | Users | Explorer | Trader | Pro | Fleet | Monthly Revenue | Monthly Cost | Monthly Profit |
|---|---|---|---|---|---|---|---|---|
| 1 | 50 | 35 | 12 | 3 | 0 | $1,125 | $313 | **$812** |
| 3 | 200 | 140 | 48 | 12 | 0 | $4,500 | $1,253 | **$3,247** |
| 6 | 500 | 350 | 120 | 28 | 2 | $11,100 | $3,420 | **$7,680** |
| 12 | 2,000 | 1,400 | 480 | 110 | 10 | $43,800 | $14,070 | **$29,730** |

### Aggressive (viral agent adoption)

| Month | Users | Monthly Revenue | Monthly Profit |
|---|---|---|---|
| 1 | 100 | $2,250 | $1,625 |
| 3 | 500 | $11,250 | $8,100 |
| 6 | 2,000 | $45,000 | $32,400 |
| 12 | 10,000 | $225,000 | $162,000 |

---

## $TECH Discount Impact

Users paying with $TECH get 20-30% discount. AAE buys $TECH at market rate.

**Scenario:** ⚔️ Trader pays $37.50 in $TECH (25% off $50)
- AAE receives $37.50 in $TECH
- AAE's cost: $16.50 (blended)
- AAE's margin: $21.00 (42% instead of 67%)
- **BUT:** $TECH demand increases → token price rises → AAE's treasury appreciates

**Net effect:** Lower per-transaction margin, but token ecosystem growth compensates long-term.

---

## Overages (Profit Maximizer)

Users exceeding tier allowance pay per-request at premium:

| Tier | Included | Overage Rate | vs. Blended Cost | Overage Margin |
|---|---|---|---|---|
| 🌱 Explorer | 5,000 | $0.005/call | $0.0011 | **78%** |
| ⚔️ Trader | 25,000 | $0.004/call | $0.0011 | **73%** |
| 🏆 Pro | 100,000 | $0.003/call | $0.0011 | **63%** |

Overages are the highest-margin revenue stream. Power users who exceed limits are the most profitable customers.

---

## Connector Registration Revenue

Third-party providers pay to list on AAE:

| Fee Type | Amount | Notes |
|---|---|---|
| Listing fee | $500 one-time | Per connector |
| Revenue share | 10-15% of connector usage | AAE takes cut |
| Featured placement | $100/mo | Premium visibility |

**If 20 connectors list by end of year:** $10,000 in listing fees + ongoing rev share.

---

## Key Risks

1. **Birdeye pricing changes** — if they raise $0.003, our blended cost goes up
2. **Low connector diversity** — if users only use Birdeye, margins compress
3. **Competitor aggregator** — another platform could offer same model cheaper
4. **Free tier pressure** — users expect some free access before paying

## Mitigations

1. **Multi-provider per category** — don't depend on Birdeye alone. Add GeckoCoin, CoinHall, etc.
2. **Build more internal connectors** — LP monitoring, risk scoring = near-zero cost
3. **First-mover on agent-native** — we're building for AI agents, not humans
4. **Freemium tier** — 500 free requests/month, then convert to paid

---

## Bottom Line

| Metric | Value |
|---|---|
| **Blended cost per request** | ~$0.0011 |
| **Average revenue per request** | ~$0.003-0.005 |
| **Average gross margin** | 55-70% |
| **Year 1 projected profit (conservative)** | ~$120K |
| **Year 1 projected profit (aggressive)** | ~$600K |
| **Break-even users** | ~25 (month 1) |

The connector model works because:
1. Most data is cheap/free (our infra, cached content)
2. Only 30% of requests hit expensive APIs (Birdeye)
3. Bundling hides complexity — users pay for convenience
4. $TECH discount creates token demand flywheel
5. Overages are pure profit

---

## Next Steps

- [ ] YoYo: Validate cost assumptions, refine tier pricing
- [ ] DMOB: Build connector interface spec (IConnector)
- [ ] Jordan: Decide on freemium vs. paid-only launch
- [ ] Desmond: Position for pitch — "Shopify for agent services"

---

#x402 #pricing #revenue #aee #connectors #strategy
