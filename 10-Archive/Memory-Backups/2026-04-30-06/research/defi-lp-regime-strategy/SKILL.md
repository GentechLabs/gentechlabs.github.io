---
name: defi-lp-regime-strategy
description: "DeFi LP regime-based strategy: decide when to LP (earn fees in chop) vs spot (capture trend upside). Covers regime detection signals, hybrid LP-core + tactical spot frameworks, and resistance-level re-entry rules."
tags: [defi, lp, strategy, regime, spot, concentrated-liquidity, avalanche]
triggers:
  - Designing LP strategy for range-bound vs trending markets
  - Deciding when to exit LP and go spot
  - Building regime detection signals for LP position management
  - Hybrid LP-core + tactical spot strategy discussions
  - Re-entering LP at resistance levels after a trend move
  - Explaining LP vs spot tradeoffs to users
  - Updating LP strategy docs after market regime change
---

# DeFi LP Regime-Based Strategy

Framework for deciding when to LP (provide liquidity, earn fees) vs hold spot (capture full price movement) based on market regime.

## Core Concept: LP = Market Maker, Spot = Trend Rider

**LP mechanics (concentrated liquidity):**
- As price rises → your volatile asset (AVAX) gets auto-sold into stablecoin (USDC)
- As price drops → your stablecoin gets auto-bought into volatile asset
- You earn fees but cap your upside in a bull market
- You outperform in sideways/choppy markets (fees accumulate)

**Spot mechanics:**
- You hold the volatile asset and capture full price movement
- No fee earnings, no auto-rebalancing
- Best during confirmed uptrends (bull markets)

## Regime Classification

| Regime | Signal | Best Position |
|--------|--------|---------------|
| **Range-bound / Choppy** | Price oscillates within a defined range, no clear trend | 100% LP — earn fees on volatility |
| **Bull confirmed** | Price breaks above key level and holds 2-3 days | 25% LP (base) + 75% SPOT (ride trend) |
| **Bear confirmed** | Price breaks below key level with volume | 100% LP (accumulate at lower prices) or 100% stablecoin |
| **Uncertain / Pre-catalyst** | Major event pending (FOMC, merger, etc.) | LP with wider range — wait for confirmation |

## "Go Spot" Signal Framework

Exit LP and convert to spot when 3+ of these fire simultaneously:

| # | Signal | Threshold | Notes |
|---|--------|-----------|-------|
| 1 | **Price hold** | Above key level for 48+ hours | Not a wick — a sustained hold |
| 2 | **BTC trend** | BTC breaks above major resistance and holds | Broader market risk-on |
| 3 | **Macro pivot** | FOMC dovish shift, peace deal signed, etc. | External catalyst confirmation |
| 4 | **Volume confirmation** | 24h volume > 2x 7-day average | Conviction behind the move |
| 5 | **Higher lows** | 3+ consecutive higher lows on 4H chart | Trend structure confirmed |

**When 3+ fire → Exit 75% LP, convert to spot AVAX**

## LP Re-Entry at Resistance

Once in spot, watch for consolidation at key resistance levels:

| Action | Condition | Duration |
|--------|-----------|----------|
| Re-enter LP | Price consolidates at resistance level | 12-24 hours of ranging |
| Stay spot | Price blasts through resistance | No consolidation |
| Exit LP → spot | Price breaks above LP range with volume | Immediate |

**Rule: Only re-LP if price consolidates. If it blasts through, stay spot and wait for next level.**

## Exit Everything Signal

When to exit ALL positions (LP + spot) and go stablecoin:

- RSI > 85 on daily (euphoric extension)
- BTC shows distribution pattern (lower highs at ATH)
- Macro shock (war escalation, black swan)
- Asset 3x from recent levels without consolidation

## Hybrid Position Architecture

```
BULL CONFIRMED? (3+ Go Spot signals)
│
├── NO → 100% LP (earn fees in range)
│
└── YES → Split:
    ├── 25% LP (always on — "market maker" base)
    └── 75% SPOT (ride the trend)
```

**As price climbs through resistance:**

1. Price hits resistance → consolidates → LP that level (earn fees during chop)
2. Price breaks above resistance → back to spot (ride to next level)
3. Repeat at each resistance zone

## LP vs Spot Decision Matrix

| Market Condition | LP (bid-ask) | Spot | Winner |
|-----------------|-------------|------|--------|
| Sideways/range-bound | Fees accumulate while price chops | Dead money | **LP** |
| Bull pump (confirmed trend) | Auto-sells into rally — capped upside | Full upside capture | **Spot** |
| Bear dump | Softens blow — accumulates cheaper bags | Full pain | **LP** (or stablecoin) |
| Pre-catalyst uncertainty | Fees while waiting, wider range | Full exposure to either direction | **LP** (wider range) |

## Implementation Checklist

When building this strategy for a user:

1. **Identify current regime** — where are we in the cycle?
2. **Set up LP range** — wider for uncertainty, tighter for confirmed range
3. **Define exit signals** — what fires trigger the LP→spot switch?
4. **Map resistance levels** — where will you re-enter LP on the way up?
5. **Document everything** — strategy doc in vault, config in env file
6. **Set up monitoring** — cron job to track regime signals and alert on changes

## Related

- `defi-lp-monitoring` — real-time LP alerts and cron jobs (complements this strategy skill)
- `defi-dashboard-digest` — daily market overview for regime context
- Vault: `03-Strategies/hybrid-lp-spot-strategy.md` — full strategy doc with signals and thresholds
