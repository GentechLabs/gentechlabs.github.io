---
name: lp-compound-tracker
description: Unified LP position monitor with compound milestone tracking. AAE "body" layer pattern for yield-bearing DeFi positions.
category: finance
---

# LP Compound Tracker

Unified LP position monitor with compound milestone tracking. Designed as the AAE "body" layer pattern — generalizable to any yield-bearing DeFi position.

## What It Does

1. **Range Monitoring** — Price vs LP range, fee efficiency, out-of-range alerts
2. **Yield Tracking** — Daily fee estimation from pool volume × position share
3. **Milestone Progression** — Tracks progress through earning tiers ($3 → $5 → $10 → $20/day)
4. **Compound Readiness** — Alerts when accumulated fees hit compound threshold ($50)
5. **DCA Reminders** — Weekly DCA day prompts
6. **Smart Silence** — No alerts when in range + high efficiency

## Data Sources

- **Primary:** Birdeye x402 (token security, holder distribution, buy/sell pressure)
- **Fallback:** DexScreener (free, no key needed)

## Configuration

Edit these in the script:
- `POSITION_SIZE_USD` — Current LP position value
- `RANGE_LOW` / `RANGE_HIGH` — LP range bounds
- `DCA_AMOUNT` — Weekly DCA amount
- `COMPOUND_THRESHOLD` — Fee accumulation before compound alert ($50)

## State Persistence

State saved to `~/.hermes/scripts/.lfj-range-state.json`:
- Cumulative fees across runs
- Out-of-range tracking
- Last alert timestamp
- Milestone progression

## AAE Generalization

This pattern extends to any yield-bearing position:
- LP positions (any DEX, any chain)
- Staking rewards
- Lending protocol interest
- Auto-compound vaults

Each user gets personalized milestones and alert preferences.

## Files

- Script: `scripts/lp-unified-monitor.py`
- Rules: `03-Strategies/LP-Monitor-Rules.md`
- AAE Pattern: `03-Strategies/AAE-Body-Layer-Pattern.md`
