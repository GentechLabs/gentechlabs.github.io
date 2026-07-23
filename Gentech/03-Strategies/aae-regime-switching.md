# AAE Regime-Switching Strategy — CURVE / Bid-Ask

> Established: 2026-07-19
> Author: Jordan + Gentech

## Core Thesis

The market has two distinct regimes. Each demands a different liquidity shape. The Agentic Treasury should detect which regime we're in and switch automatically.

## Regimes

### Regime 1: Chop / No Direction (Default → CURVE)

- **When**: Between macro events, consolidation, priced-in anxiety, low volatility
- **Shape**: CURVE (wide distribution across range)
- **Behavior**: Set and forget. All bins earn as price oscillates within range.
- **Why**: No clear directional bias. Bid-ask would sit in the dead zone between edges and earn 0%.
- **Current status (Jul 19)**: ✅ ACTIVE — market chopping after inflation pump, Iran headline priced in

### Regime 2: Macro Event (Fed / CPI / NFP → Bid-Ask)

- **When**: 24h before Fed meetings, CPI/NFP releases, earnings, geopolitics
- **Shape**: Bid-Ask (concentrated at two edges)
- **Behavior**: Price moves hard one direction → one edge catches it → peak efficiency
- **Why**: You know the direction of risk (usually risk-off for macro surprises). No point spreading liquidity across a range when 90% of the action is at one edge.
- **Next event**: **FOMC Jul 29-30** — switch to bid-ask by Jul 28 EOD

### Regime 3:? Trending Market (Future Enhancement)

- Directional trend with momentum
- Could use a skewed CURVE or 100% spot position
- Not yet implemented — waiting for a clear trend to form

## Automation Plan

1. Cron job checks macro calendar daily (fed-event-tracker.py already exists)
2. 24h before FOMC/CPI/NFP → auto-switch config to bid-ask at current macro-relevant range
3. 24h after event settles → auto-switch back to CURVE
4. Manual override always available (Jordan sets shape directly on LFJ)

## Current Position

- **Shape**: Bid-Ask (awaiting Jordan's rebalance to CURVE for chop)
- **Range**: $6.3656 – $6.5856
- **Entry**: $6.48
- **Next Fed**: Jul 29-30 → switch back to bid-ask Jul 28
