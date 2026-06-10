---
date: 2026-04-29
author: Desmond
status: draft
tags: [strategy, LP, hybrid, DeFi, market-making]
---

# Hybrid LP-Core + Tactical Spot Strategy

## Overview
Core philosophy: **Be a market maker in chop, be a spot holder in trend.**

This strategy defines when to LP (earn fees) vs when to ride spot (capture upside), based on market regime signals.

---

## Regime Detection

### Current State: Correction/Range-Bound
- BTC above $60K (not capitulation) but below recent highs
- AVAX range: $9.00–$9.45 (LP earns fees during chop)
- LP composition: ~58% USDC / ~42% AVAX (dry powder positioned)

### Target: Bull Confirmed
Exit LP, go spot, ride to resistance.

---

## "Go Spot" Signal — Exit LP Criteria

**Trigger when 3+ of these fire simultaneously:**

| # | Signal | Threshold | Source |
|---|--------|-----------|--------|
| 1 | AVAX price hold | Above key level (e.g. $10) for 48+ hours | On-chain / price feed |
| 2 | BTC trend | Breaks above $130K and holds | CoinGecko / CMC |
| 3 | Macro pivot | FOMC confirms dovish shift OR peace deal signed | News / Fed calendar |
| 4 | Volume confirmation | 24h volume > 2x 7-day average | CoinGecko |
| 5 | Higher lows pattern | 3+ consecutive higher lows on 4H chart | Chart analysis |

**When 3+ fire → Recommendation: Exit 75% LP, convert to spot AVAX**

---

## LP Re-Entry at Resistance

Once in spot, watch for consolidation at key resistance levels:

| Level | Historical significance | LP re-entry zone |
|-------|------------------------|------------------|
| $15 | Previous support/resistance | LP if price chops here 12-24h |
| $20 | Psychological + technical | Same pattern |
| $30 | Major historical level | Same pattern |
| $40 | Mid-range of previous cycle | Same pattern |
| $60 | Upper range | Same pattern |

**Rule: Only re-LP if price consolidates at level for 12-24h. If it blasts through, stay spot.**

---

## Exit LP → Go Cash Signal

**When to exit EVERYTHING (LP + spot) and go USDC:**

- AVAX hits euphoric extension (RSI > 85 on daily)
- BTC shows distribution pattern (lower highs at ATH)
- Macro shock (war escalation, black swan)
- AVAX 3x from current levels without consolidation

---

## Current Position (Baseline)

- **Pool:** LFJ AVAX/USDC (5bps)
- **Range:** $9.00–$9.45 (curve shape)
- **Balance:** $135.21 (6.169 AVAX + 78.22 USDC)
- **Date:** 2026-04-29
- **Status:** Earning fees during correction

---

## TODO

- [ ] Build automated indicator script (DMOB)
- [ ] Backtest signals on historical AVAX price data
- [ ] Define exact thresholds for each signal
- [ ] Integrate with LP monitoring cron (YoYo)
- [ ] Test with paper trading before live execution

---

*This strategy is part of the DeFi milestone — professional market making with regime-based position management.*
