---
date: 2026-04-27
author: YoYo
source: reactive-analysis
tags: [LP, rebalance, LFJ, AVAX/USDC]
---

# LP Rebalance Analysis — AVAX/USDC LFJ V2.2

## Current State (0126 UTC)

| Metric | Value |
|--------|-------|
| Price | $9.5515 |
| Current Range | $9.32 — $9.53 |
| Position Value | $138.92 |
| Pool 24h Vol | ~$19.1M |
| Pool TVL | ~$4.05M |
| Fee Tier | 5 bps |

**Status:** 🟥 OUT OF RANGE (price above upper bound)
**Current APY while OOR:** 0%

## Rebalance Scenarios

**Models assume:** Base daily = ~$0.33 (position's share of pool fees, current TVL/vol, if always in range). Concentration bonus scales with narrower ranges; efficiency penalty at range edges.

### Scenario Table

| Range | Width | In Range? | Est Efficiency | Est Daily | Est APR |
|-------|-------|-------------|----------------|-----------|---------|
| $9.42 — $9.68 | $0.26 | ✅ | ~99% | ~$1.62 | ~425% |
| **$9.25 — $9.65** | **$0.40** | ✅ | **~49%** | **~$0.81** | **~212%** |
| $9.15 — $9.75 | $0.60 | ✅ | ~66% | ~$0.72 | ~190% |
| $9.00 — $9.95 | $0.95 | ✅ | ~84% | ~$0.58 | ~152% |
| $8.80 — $10.20 | $1.40 | ✅ | ~93% | ~$0.43 | ~114% |

### Recommendation: **Tight ($9.25 — $9.65)**

**Rationale:**
- Price at $9.55 is solidly inside center zone → rebalance captures immediate fee resumption
- Range width ~$0.40 vs current ~$0.21 → 2x buffer against volatility (current was too tight)
- Not as wide as "balanced" → preserves concentration (3–4x better than very-wide)
- Still earns ~$0.81/day while providing $0.20 below and $0.10 above current price buffer

**Downside:** If AVAX breaks above $9.65, we'd go OOR on the upside. Tradeoff: tighter = more fees, wider = more safety.

### Gas Estimate Needed

LFJ V2.2 rebalance = remove position + re-add with new range.

Transactions:
1. **Remove all liquidity** (burn position → receive AVAX + USDC)
2. **Re-add liquidity** (add tokens at new range)

Estimated gas on Avalanche C-Chain: 150k–220k gas @ 25 nAVAX = ~$0.30–$0.50 total.

**Need @DMOB confirmation on actual gas estimate for LFJ V2.2 burn + mint.**

## Decision Framework

| If Jordan wants... | Action |
|----------------------|--------|
| Max fees, check often | Ultra-tight ($9.42–$9.68) |
| **Balanced but active** | **Tight ($9.25–$9.65)** ← **YoYo recommends** |
| Stay in range longer | Wide ($9.00–$9.95) |
| Set-and-forget | Very-wide ($8.80–$10.20) |

---
*Route: Jordan decision → @DMOB gas estimate → execute rebalance.*
