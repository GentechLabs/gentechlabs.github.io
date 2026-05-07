# Yield Gap Analysis — DeFi Milestone Tracking

Pattern for analyzing LP position yields, projecting capital requirements to hit daily fee targets, and calculating DCA timelines.

## Data Source Locations

Hermes Agent stores state across two locations:

| File | Path (DMOB profile) | Purpose |
|------|---------------------|---------|
| Vault Tracker | `/root/vaults/gentech/03-Strategies/scripts/.lfj-position-tracker.json` | Historical entry price, DCA injections, rebalance events |
| Runtime State | `/root/.hermes/profiles/dmob/home/.hermes/scripts/.lfj-aae-state.json` | Live position value, cumulative fees, days in range |
| Config JSON | `/root/.hermes/profiles/dmob/home/.hermes/scripts/.lfj-aae-config.json` | Pool parameters (fee tier, range, shape) |

**Merge strategy:** Vault provides *events* (entry, DCA, rebalance); runtime provides *current snapshot*. Cross-reference vault's latest `history[].value_usd` against runtime's `last_position_usd` to detect additions/withdrawals.

## Yield Calculation from DexScreener

When on-chain fee data is not directly available, infer daily fees from pool metrics:

```python
daily_fees = (volume_24h_usd × fee_tier_bps / 10000) × (position_usd / pool_tvl_usd)
```

- `fee_tier_bps`: Pool's fee rate in basis points (5, 10, 30, etc.)
- `position_usd`: Current USD value of LP position
- `pool_tvl_usd`: Total Value Locked in the pool
- `volume_24h_usd`: 24h trading volume

Derived APR:
```python
implied_apr = (daily_fees × 365 / position_usd) × 100
```

**Caveat:** This assumes uniform fee distribution across all LPs. Some protocols (Uniswap V3) concentrate fees to in-range positions only; adjust by fee efficiency percentage if calculating net earnings.

## Milestone Gap Analysis

```
shortfall_daily = target_daily_fees - current_daily_fees
required_principal_at_apr = shortfall_daily × 365 / (target_apr / 100)
```

Example targets:
| Tier | Daily Target |
|------|--------------|
| Scout | $5.00 |
| Raider | $20.00 |
| Warlord | $50.00 |
| Sovereign | $100.00 |
| Freedom | $200.00 |

Present gap at three APR scenarios:
- **Current APR** (from live pool data)
- **Historical APR** (best recent observed, e.g., 88.77% from Apr-24)
- **Target APR** (optimized operational goal, e.g., 50%)

## DCA Timeline Projection

```
weeks_needed = required_principal / weekly_dca_rate
```

Weekly DCA rate is user-configured split:
- Base: `$50` (Sun-Wed portion)
- Boost: `$50` (Thu-Sat portion) if efficiency ≥ threshold
- Total weekly: `$100` (steady) or `$150-$200` (with boosts active)

Convert to human-readable:
- `~173 weeks` → "~3.3 years"
- `~52 weeks` → "~1 year"
- `~12 weeks` → "~3 months"

## Capital Change Detection

Compare vault history vs runtime state:

```python
last_vault_value = vault_tracker['history'][-1]['value_usd']
current_runtime_value = aae_state['last_position_usd']
delta = current_runtime_value - last_vault_value

if delta > 0:
    print(f"DCA Boost detected: +${delta:.2f}")
elif delta < 0:
    print(f"Position decreased: -${abs(delta):.2f} (IL or fees claimed)")
else:
    print("Steady — no recent capital movement")
```

**Classification:**
- `+$45 to +$55` → Standard weekly DCA hit
- `+$10 to +$20` → Micro-DCA bonus triggered (low efficiency)
- `+$100+` → Multiple DCAs or large injection
- `-$$0.01 to -$2.00` → Normal fee harvesting/IL drift
- `-$5.00+` → Possible emergency withdrawal or large impermanent loss event

## Implementation Checklist

- [ ] Load vault tracker JSON → extract `history` array
- [ ] Load runtime AAE state JSON → read `last_position_usd`, `total_fees_earned_usd`
- [ ] Fetch DexScreener pool data → get `volume`, `liquidity`, `price`
- [ ] Load config → get `fee_tier_bps`, `range_low`, `range_high`, `shape`
- [ ] Calculate fee efficiency: `(price - low) / (high - low)` with shape adjustment
- [ ] Estimate daily fees via formula above
- [ ] Determine current milestone tier
- [ ] Compute gap at multiple APR assumptions
- [ ] Project DCA weeks at configured weekly rate(s)
- [ ] Flag capital change (DCA boost or decrease)
- [ ] Output structured JSON for frontend consumption

## Output Format (for AAE Frontend)

```json
{
  "timestamp": "2026-05-03T07:45:00-04:00",
  "position_usd": 134.94,
  "capital_change": {
    "detected": "steady",
    "delta_usd": -3.98,
    "last_event": "2026-04-27: Rebalance — Range updated 9.38–9.66"
  },
  "yield": {
    "daily_fees": 0.01,
    "implied_apr": 4.3,
    "fee_efficiency": 42.2,
    "pool_volume_24h": 1351652.92,
    "pool_tvl": 3839625.68
  },
  "milestone": {
    "current_tier": "Scout",
    "current_daily": 5.0,
    "target_tier": "Raider",
    "target_daily": 20.0,
    "progress_pct": 0.0
  },
  "gap_analysis": {
    "shortfall_daily": 19.99,
    "required_at_current_apr": 169700,
    "required_at_50pct_apr": 14600,
    "required_at_hist_apr": 8200
  },
  "dca_projection": {
    "weekly_rate_usd": 100,
    "weeks_to_close_current_apr": 1697,
    "weeks_to_close_target_apr": 146
  },
  "tips": [
    "Widen range to 9.00-9.45 to improve efficiency",
    "Consider secondary 15bps pool on Base for yield boost",
    "Rebalance immediately if efficiency drops below 30%"
  ]
}
```