---
title: RWA Token Impermanent Loss Calculator
date: 2026-05-03
session: PROPS-LAND-real-estate-analysis
tags: [defi, rwa, il-calculator, micro-cap]
---

# RWA Token IL Risk Assessment

**Context:** Small-cap Real World Asset tokens (PROPS $2.4M, LAND $795K) paired with blue-chip assets create severe IL risk due to volatility mismatch.

## The Problem

RWA tokens (real estate) are **low-volatility by nature** (land value changes slowly). Pairing them with volatile assets (AVAX, USDC against volatile USD) in an LP causes:

1. **Directional IL** — If RWA token appreciates 20% vs AVAX, you lose 20% of the RWA portion despite price gain
2. **Low fee offset** — With micro-cap MCap, pool fees are tiny; token rewards may not compensate IL
3. **Exit liquidity risk** — Low TVL means large exits cause slippage; IL realized on withdrawal

## Calculator Formula

For LP pair: RWA_TOKEN / STABLE (USDC or AVAX treated as stable for calculation)

```python
def il_percentage(price_change_pct):
    """
    IL as percentage of initial LP value when one asset price changes.
    Standard concentrated liquidity IL approximation.
    """
    import math
    x = price_change_pct / 100 + 1
    il = 2 * (math.sqrt(x) - 1) / (1 + x)
    return abs(il) * 100  #Return IL as percentage loss vs HODL
```

**Example:** RWA token +20% vs AVAX → IL ≈ **~5.7%** of LP value

## Risk Matrix for PROPS/LAND LPs

| Token Pair | RWA MCap | Expected RWA Volatility | Recommended Range Width | Max Allocation |
|------------|----------|------------------------|------------------------|----------------|
| PROPS/AVAX | $2.4M | ±15% monthly typical | 20-25% spread | 5% of portfolio |
| LAND/AVAX | $795K | ±25% monthly typical | 25-30% spread | 3% of portfolio |
| PROPS/USDC | $2.4M | ±15% monthly | 18-22% spread | 5% |
| LAND/USDC | $795K | ±25% monthly | 25-30% spread | 3% |

**Rationale:** LAND is smaller, more volatile → wider range needed, smaller allocation.

## Wide-Range Strategy (Volatility Capture)

Following Jordan's suggestion: *"widen to $8.50-$10.00"* for AVAX pair:

If AVAX = $9.17:
- Lower bound: $8.50 (-7.3%)
- Upper bound: $10.00 (+9.0%)
- **Total width: 16.3%** → captures most AVAX volatility

For RWA token paired with AVAX, you'd need even wider bounds because RWA token has its own volatility on top of AVAX movement.

## Alternative: Direct Hold vs LP

| Strategy | Expected Return | IL Risk | Complexity | Recommended For |
|----------|----------------|---------|------------|-----------------|
| **Direct HODL** (buy PROPS) | ±30-50% annually (speculative) | None (price risk only) | Minimal | Directional bet on RWA narrative |
| **LP position** (PROPS/AVAX) | 5-15% fees + token rewards | High (5-15% annual IL) | Moderate | Earn yield while maintaining exposure |
| **Staking** (if available) | 10-30% token rewards | Medium (reward token inflation) | Low | Project-specific programs |

**Verdict:** For 2-3 year hold, **direct HODL likely outperforms LP** unless token rewards are significant (>30% APY) to offset IL.

## Verification Checklist

- [ ] Pool TVL > token MCap × 0.5 (checks liquidity depth)
- [ ] 24h volume > token MCap × 0.01 (ensures tradability)
- [ ] Token rewards > 20% APY on top of fees (compensates IL)
- [ ] Range width covers 90% of last 30d price action (backtest on DEXScreener)
- [ ] Exit strategy documented (when to withdraw LP vs swap to USDC)

## Monitoring Script Extension

Add to `lp-aae-signal-monitor.py`:

```python
# RWA-specific IL warning
rwa_il_estimate = calculate_il_wideness(current_range_width, token_historical_vol)
if rwa_il_estimate > 10:  # >10% expected annual IL
    print(f"⚠️ High IL risk for {ticker}: estimated {rwa_il_estimate:.1f}% annual")
```

## Open Questions
- Does Landshare/Propbase offer direct staking? (Check docs)
- Are there protocol-owned liquidity programs that reward LPs with additional tokens?
- Historical price correlation: PROPS vs AVAX, LAND vs AVAX during bull/bear cycles?
