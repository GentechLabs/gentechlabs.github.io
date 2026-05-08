---
name: multi-chain-portfolio
description: "Construct and manage multi-year, multi-chain cryptocurrency portfolios balancing Core DeFi LP positions, RWA/thesis holds, and cycle-aligned yield farming with DCA optimization."
tags: [portfolio, multi-chain, investment, dca, yield-farming, rwa]
trigger: "When building long-term crypto portfolios across multiple chains, allocating capital between spot holds/LP positions/yield farms, classifying assets by strategy intent, or designing DCA schedules for 2+ year horizons."
related_skills:
  - defi  # LP position fundamentals
  - defi-lp-monitor  # Position tracking
  - defi-lp-strategy-designer  # Exit/entry rules
  - investment-strategy-dca  # Dollar-cost averaging mechanics
version: 1.0.0
author: Gentech
last_updated: 2026-05-03
---
# Multi-Chain Portfolio Construction

**Class:** Investment Strategy & Portfolio Management  
**Scope:** 2–3 year horizons where compounding through cycles beats short-term yield chasing  
**Primary Agent:** gentech (strategic vision), yoyo (DeFi execution), dmob (monitoring)

---

## Purpose

Systematically construct diversified crypto portfolios across multiple chains with clear capital allocation between:

| Bucket | Purpose | Examples |
|--------|---------|----------|
| **Core DeFi** | Stable compounding, proven protocols | AVAX/USDC LP, ETH/DAI pool |
| **RWA / Thesis** | Long-term narrative holds | PROPS (real estate), LAND (virtual real estate), TAO (AI) |
| **Cycle Plays** | Asymmetric upside on ecosystem waves | SOL/BONK/JUP yield, new L1 rotations |

Each bucket has distinct: position sizing rules, range widths, rebalance frequency, and monitoring cadence.

---

## When to Use

- Building a multi-year crypto portfolio from scratch
- Adding a new asset class (RWA, metaverse) to existing DeFi base
- Deciding whether to hold spot vs. provide liquidity for a token
- Allocating new capital across chains (Solana vs Avalanche vs Ethereum)
- Designing DCA schedules that align with market cycles
- Evaluating if a thin-liquidity token belongs in yourportfolio

---

## Quick Decision Table

| User Question | Go To Section |
|----------------|---------------|
| "Should I add PROPS/LAND to my portfolio?" | [Asset Classification](#step-1--asset-classification--chain-mapping) |
| "How much SOL vs AVAX should I allocate?" | [Capital Allocation Templates](#step-3--capital-allocation-per-dca-cycle) |
| "What range width for a 2-year hold?" | [Range Width Matrix](#step-2--strategy-assignment-by-class) |
| "Yield farming or spot holding?" | [Strategy Assignment](#step-2--strategy-assignment-by-class) |

---

## Process

### Step 1 — Asset Classification & Chain Mapping

For each candidate token:

**1a. Identify chain(s) and contracts**
- Primary source: CMC API `/v1/cryptocurrency/info?symbol=XXX`
- Fallback: CoinGecko `/coins/{id}` → `platforms` field
- Record all chain addresses (tokens can live on multiple chains)

**1b. Evaluate liquidity depth**
| Metric | Threshold | Classification |
|--------|-----------|----------------|
| TVL | > $5M | Core DeFi candidate |
| TVL | $1–5M | RWA / Thesis candidate |
| TVL | < $1M | Spot-hold only (avoid LP) |
| 24h volume | > $500K | Healthy |
| 24h volume | $100–500K | Moderate |
| 24h volume | < $100K | Thin — use limit orders, wide spreads |

**1c. Classify intent**
- **Core DeFi** — High TVL, high volume, established platform, yield-bearing
- **RWA / Thesis** — RWA narrative, moderate TVL, long-term hold thesis, often staking rewards
- **Cycle Play** — Ecosystem token, volatile, cyclical upside, often farming incentives

---

### Step 2 — Strategy Assignment by Class

| Asset Class | Recommended Strategy | Range Width | Rebalance Frequency | DCA Method |
|-------------|---------------------|-------------|---------------------|------------|
| **Core DeFi** (AVAX/USDC) | Concentrated LP (bid-ask or tight curve) | 5–15% | Weekly (volatility-based triggers) | Weekly $50–100 + opportunistic dips |
| **RWA / Thesis** (PROPS/LAND) | Spot hold + occasional wide-range LP | 30–50% | Monthly (or after +10% price move) | Monthly $100–200 systematic |
| **Cycle Play** (SOL/BONK) | Concentrated LP on high-volume pairs | 10–20% | Weekly + event-driven (upgrades, catalysts) | Weekly $50–100 |

**Rationale:**
- **Core:** Tight ranges capture fees efficiently when price stable; rebalance often to stay centered
- **RWA:** Wide ranges avoid frequent rebalancing cost; hold spot for thesis, add LP only when naturally in-range
- **Cycle:** Tighter ranges during high volatility capture fee spikes; exit to spot on breakout signals

---

### Step 3 — Capital Allocation (per DCA cycle)

**Default template:**
```
- 50% Core DeFi (rebalance existing positions, profit-taking into new entries)
- 30% RWA / Thesis (new spot buys, selective LP additions)
- 20% Cycle Plays (new yield positions, ecosystem rotation)
```

**Adjust by market regime:**
| Regime | Core | RWA | Cycle |
|--------|------|-----|-------|
| Bull breakout | 40% | 30% | 30% (take profit into cycle) |
| Bear / crash | 60% | 30% | 10% (defensive) |
| Choppy consolidation | 50% | 30% | 20% |

---

### Step 4 — DCA Schedule Design

**Tiered approach:**

| Frequency | Amount per bucket | Purpose |
|-----------|-------------------|---------|
| **Weekly micro** | $50–100 | Core + Cycle (automated where possible) |
| **Monthly macro** | $200–400 | RWA thesis (discretionary based on news) |
| **Opportunistic** | Variable | Buy the dip (>5% drop), consolidation phases |

**Rule of thumb:** Total monthly DCA ≤ 5% of portfolio value (if building from zero, scale up to this level over 6 months).

---

### Step 5 — Monitor & Triage

Set up separate monitoring cadences:

| Bucket | Price Check | Volume Review | Position Health | Tool |
|--------|-------------|---------------|-----------------|------|
| **Core DeFi** | 4× daily | Daily | 10-min LP monitor (in-range, fees) | `defi-lp-monitor` cron |
| **RWA / Thesis** | Hourly | Daily | Weekly health review (IL, TVL) | `cron-watchlist` + manual review |
| **Cycle Plays** | Real-time alerts | Real-time | Daily farming reward claims | Custom script + Telegram |

---

## Pitfalls

### Pitfall 1 — Thin Liquidity Trap
**Symptoms:** TVL < $2M, 24h volume < $100K, wide spreads (>2%)  
**Wrong:** Providing LP to "earn yield"  
**Right:** Spot buy only, use limit orders, wide DCA bands  
**Why:** Impermanent loss risk + exit liquidity problems dwarf fee income

### Pitfall 2 — Multi-Chain Accounting Confusion
**Symptoms:** Holding same token on 2+ chains, aggregating TVL in one view  
**Wrong:** "My PROPS position is worth $X total" (summing Ethereum + Aptos)  
**Right:** Track per-chain positions separately; choose one chain for liquidity provision  
**Why:** Different liquidity depths, fee structures, bridge costs

### Pitfall 3 — Range Anchoring Bias
**Symptoms:** Initial range 10% width, never changed despite 50% price move  
**Wrong:** "The range is fine" when position out-of-range 90% of time  
**Right:** Re-evaluate range width monthly; widen or recenter based on volatility  
**Why:** Concentrated liquidity only earns fees when price in range

### Pitfall 4 — Cycle Mistiming
**Symptoms:** Cycle plays > 50% of portfolio, chasing highest APR pools  
**Wrong:** "BONK farm at 800% APR" becomes 40% of capital  
**Right:** Cap cycle allocation at 20%; rotate profits into Core and RWA  
**Why:** Ecosystem tokens can drop 80% in bear markets; Core/RWA provide stability

### Pitfall 5 — Yield Chasing Without Fee Quality Check
**Symptoms:** High APR headline, low actual fee accrual  
**Wrong:** Entering pool based on APR display alone  
**Right:** Check 24h volume × fee tier = actual fees; divide by TVL = real yield  
**Why:** APR often inflated by token emissions; real yield = fees / liquidity

---

## Verification Checklist

Before finalizing a portfolio decision:
- [ ] Asset classified (Core / RWA / Cycle) and chain(s) mapped
- [ ] Liquidity metrics checked (TVL, volume, spread)
- [ ] Strategy assigned with range width and rebalance triggers documented
- [ ] Capital allocation % aligns with portfolio template (adjust if regime ≠ neutral)
- [ ] DCA schedule entered into calendar or automation (weeklymicro + monthlymacro)
- [ ] Monitoring setup:
  - [ ] Core: 10-min LP monitor cron active
  - [ ] RWA: Hourly price alert active (1.5% threshold)
  - [ ] Cycle: Real-time Telegram alerts configured
- [ ] Exit criteria defined (time-based: 2–3 years; price-based: 2x or -50% stop-loss)
- [ ] Vault entry created: `03-Projects/Portfolios/Active/{Year}-{Strategy}.md`

---

## Related Sessions (References)

See `references/` directory for session-specific research and templates:

- **2026-05-03** — PROPS/LAND real estate tokens added to RWA bucket; Solana yield farming mapped as parallel cycle track; portfolio allocation template finalized
- **Vault paths:** `03-Strategies/Investment_Strategy_Agent_Economy.md`, `03-Strategies/Yield-Farm-Tracker-Reference.md`

---

## References (Supporting Files)

**Session-specific detail:**
- `references/2026-05-03-real-estate-rwa-analysis.md` — PROPS/LAND token data, chain mapping, liquidity assessment
- `references/2026-05-03-solana-yield-landscape.md` — Solana DEX pool API patterns, Raydium/Orca pool structures, yield composition breakdown
- `references/token-classification-cheatsheet.md` — Quick-lookup TVL/volume thresholds and strategy mapping

**Templates:**
- `templates/portfolio-allocation-template.md` — Markdown template for new portfolio entries
- `templates/dca-schedule-template.md` — Calendar-blocking template + automation hooks

**Scripts:**
- `scripts/classify-token.py` — Given token symbol, fetches CMC/CoinGecko data, outputs classification + chain + liquidity metrics
- `scripts/portfolio-summary.py` — Aggregates all active positions by bucket, computes allocation %, generates report
