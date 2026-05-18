# $GENTECH — Black Hole Burn Stress Test

**Date:** 2026-04-19
**Status:** Model v1
**Assumptions:** Daily fee volume, burn %, exit demand, $1M initial treasury

---

## Mechanic

Fees collected → % burned (black hole) → remaining exits paid from treasury reserve.
**Core question:** Can the treasury always honor exit demands?

---

## Results — Days Until Treasury Depletion

| Scenario | Burn Rate | $100K | $500K | $1M | $5M |
|---|---|---|---|---|---|
| Bear Market | 50% | 8d | 40d | 80d | 400d |
| **Steady State** | **50%** | **∞ ✅** | **∞** | **∞** | **∞** |
| **Bull Run** | **50%** | **∞ ✅** | **∞** | **∞** | **∞** |
| Black Swan | 50% | 0d | 3d | 6d | 31d |
| Death Spiral | 50% | 1d | 5d | 10d | 50d |

**Key insight:** At ≥50% burn, Steady State and Bull Run are *self-funding* — the treasury grows because fee revenue exceeds exit demand.

---

## Deep Dive — 365 Day Projection ($1M start, 50% burn)

| Day | Bear Mkt | Steady State | Bull Run | Black Swan | Death Spiral |
|---|---|---|---|---|---|
| 1 | $988K | $1,005K | $1,085K | $840K | $901K |
| 7 | $912K | $1,035K | $1,595K | BUST | $307K |
| 30 | $625K | $1,150K | $3,550K | BUST | BUST |
| 90 | BUST | $1,450K | $8,650K | BUST | BUST |
| 365 | BUST | $2,825K | $32,025K | BUST | BUST |

---

## Scenario Definitions

| Scenario | Daily Fees | Daily Exit Demand | Description |
|---|---|---|---|
| Bear Market | $5,000 | $15,000 | Low activity, moderate panic exits |
| Steady State | $50,000 | $20,000 | Normal operations, healthy churn |
| Bull Run | $250,000 | $40,000 | High volume, profit-taking exits |
| Black Swan | $80,000 | $200,000 | Fees spike but mass exit event |
| Death Spiral | $2,000 | $100,000 | Fees collapse, panic accelerates |

---

## Critical Findings

### 1. Death Spiral is the existential threat
- Fees collapse to $2K/day, exits hit $100K/day
- **No burn rate saves this** — burning 100% of $2K still leaves $98K daily hole
- Requires emergency brake (circuit breaker)

### 2. Black Swan destroys $1M treasury in 6 days
- Net daily drain: $160K
- **30-day survival requires $4.8M reserve**

### 3. Steady State is self-funding at ≥50% burn
- Net daily: +$5K (treasury grows $1.8M/year)
- Bull run: +$170K/day (treasury grows $62M/year)

### 4. Bear Market at $1M = 80 days runway
- Enough time to react, not enough to be comfortable

---

## Safeguard Recommendations

| Parameter | Value | Rationale |
|---|---|---|
| **Treasury floor** | $4.8M | Covers 30-day Black Swan event |
| **Emergency brake** | Triggered at $100K | Pause exits, activate mint circuit breaker |
| **Minimum burn rate** | 50% | Flips Steady State from draining to accumulating |
| **Surplus allocation** | Above $2M | Excess flows to buybacks or ecosystem grants |
| **Burn rate adjustment** | Governance-controlled | Can increase during stress events |

---

## Open Questions for Dmob (Solidity)

- [ ] How to implement emergency brake in contract?
- [ ] Can treasury be partially backed by non-$GENTECH assets (stablecoins)?
- [ ] Circuit breaker: pause exits vs. rate-limit exits vs. dynamic fees?
- [ ] How to handle oracle price feeds during Black Swan events?

---

*Next: Validate assumptions with Dmob, integrate into contract design.*
