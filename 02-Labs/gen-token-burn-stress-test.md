# GEN Token — Black Hole Burn / Treasury Reserve Stress Test

**Date:** 2026-04-19
**Author:** Dmob

## Setup
- Initial Supply: 1B GEN
- Initial Treasury: $500K USDC
- Initial Price: $0.10/GEN
- Simulation: 365 days, daily timesteps

## Results Matrix

| Fee Scenario | Burn Rate | Final Supply | Treasury | Price | Burned% | Reserve Ratio | Status |
|---|---|---|---|---|---|---|---|
| Low ($1K/d) | Conservative (0.01%/d) | 964M | -$2.6M | $0.104 | 3.6% | -0.03x | 💀 Day 59 |
| Low ($1K/d) | Moderate (0.05%/d) | 833M | -$16.5M | $0.120 | 16.7% | -0.17x | 💀 Day 11 |
| Low ($1K/d) | Aggressive (0.10%/d) | 694M | -$33.9M | $0.145 | 30.6% | -0.36x | 💀 Day 6 |
| Mid ($10K/d) | Conservative (0.01%/d) | 964M | $619K | $0.107 | 3.6% | 0.01x | ⚠️ Underfunded |
| Mid ($10K/d) | Moderate (0.05%/d) | 833M | -$13.5M | $0.124 | 16.7% | -0.14x | 💀 Day 14 |
| Mid ($10K/d) | Aggressive (0.10%/d) | 694M | -$31.0M | $0.148 | 30.6% | -0.32x | 💀 Day 6 |
| High ($50K/d) | Conservative (0.01%/d) | 964M | $15.0M | $0.120 | 3.6% | 0.14x | ⚠️ Underfunded |
| High ($50K/d) | Moderate (0.05%/d) | 833M | $69K | $0.137 | 16.7% | 0.00x | ⚠️ Edge case |
| High ($50K/d) | Aggressive (0.10%/d) | 694M | -$18.3M | $0.161 | 30.6% | -0.17x | 💀 Day 11 |

## Critical Findings

### 1. Even "best case" is underfunded
High volume + conservative burn = 0.14x reserve ratio. Treasury covers only 14% of exit liability. **The $500K initial treasury is 10x too small even for the most conservative scenario.**

### 2. Break-even fee requirements
- Conservative burn: ≥ $10K/day fees minimum
- Moderate burn: ≥ $50K/day fees minimum
- Aggressive burn: ≥ $100K/day fees minimum

### 3. Required treasury sizing (30-day exit buffer)
- Conservative: ≥ $300K minimum
- Moderate: ≥ $1.5M minimum
- Aggressive: ≥ $3M minimum

### 4. Deflation impact is real but manageable
- Conservative: 96.4% supply remains after 1 year
- Moderate: 83.3% remains
- Aggressive: 69.4% remains

## Contract Design Requirements

1. **CIRCUIT BREAKER** — `require(treasury >= circulatingSupply * exitPrice)` or exits halt
2. **TWAP oracle** for exit price — never spot price
3. **Pull-over-push** — requestExit() → queue → claimExit() after cooldown
4. **Fee priority** — treasury reserve fills to 1.5x before any other distribution
5. **Graduated exit fees** — larger exits pay higher %, fee goes to treasury
6. **Initial treasury must be ≥ $300K** even for conservative burn rate
