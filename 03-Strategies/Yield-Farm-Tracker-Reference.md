# Yield Farm Tracker — Reference Design
**Date:** 2026-04-25
**Source:** Jordan shared screenshot from YoYo's LP tracking system
**Pool:** AVAX / USDC — LFJ (Trader Joe) — Avalanche C-Chain

## What It Is
Real-time LP position dashboard tracking an AVAX/USDC concentrated liquidity position on Trader Joe (LFJ). Shows position health, fee earnings, rewards, DCA schedule, and range configuration.

## Key Data (Snapshot: Mar 31, 2026)
| Metric | Value |
|--------|-------|
| Total Position | $31.16 |
| AVAX Price | $8.853 |
| Rewards APR | 5,138% |
| Claimable | $1.13 (0.12782 AVAX) |
| 24H Fees | $0.333 |
| Range TVL | $629.18 |
| Position Split | 39.5% AVAX / 60.5% USDC |
| Strategy | CURVE — 149 Bins |
| Fee Tier | 5 bps |

## Range Configuration
| Parameter | Value |
|-----------|-------|
| Min Price | 8.2217 USDC/AVAX |
| Max Price | 9.5325 USDC/AVAX |
| Active Bin | 8.85289 USDC/AVAX |
| Range Width | ~16% spread |

## DCA Schedule
- Weekly: $50-100
- Monthly: $200-400
- Funded by Amazon Flex income
- Conviction: HIGH

## Strategy Notes
- Fees back online — position is IN RANGE
- Both rewards + fee income running simultaneously
- Compound immediately: 0.12782 AVAX claimable
- Wallet ready: 0.11031 AVAX + 0.05 USDC for next deposit

## Relevance to AAE
This dashboard format could be adapted for the GenTech platform:
- LP position tracking with real-time fee monitoring
- Rewards APR display with claim/compound actions
- DCA schedule integration
- Range health visualization
- Milestone-based wealth building UI

**Source files:**
- HTML template: `03-Strategies/Yield-Farm-Tracker.html`
- Markdown notes: `03-Strategies/Yield-Farm-Tracker-Reference.md`

## Tags
#lp-tracking #yield-farming #avax #usdc #trader-joe #lfj #dashboard #aee-reference
