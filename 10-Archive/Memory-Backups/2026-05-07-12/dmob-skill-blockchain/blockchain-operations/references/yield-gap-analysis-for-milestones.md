# Yield Gap Analysis for DeFi Milestone Tracking

**Purpose:** Compute capital gap and DCA timeline when daily yield falls short of milestone targets.

## Scenario

Given:
- Current daily fees earned: `daily_fees`
- Target daily fees (next milestone): `target_daily`
- Position principal: `position_usd`
- Implied APR from pool metrics: `apr_pct`
- Weekly DCA rate (average): `weekly_dca`

## Gap Computation

If `apr_pct` > 0 and `target_daily` > `daily_fees`:

```
shortfall_per_day = target_daily - daily_fees
additional_principal_needed = shortfall_per_day * 365 / (apr_pct / 100)
```

**Interpretation:** The additional capital required to generate the shortfall at the current APR.

If position is out-of-range or volume collapsed such that `daily_fees` ≈ 0, the gap is effectively infinite unless a realistic post-rebalance APR can be estimated from historical averages.

## DCA Timeline

```
weeks_to_close = additional_principal_needed / weekly_dca
biweekly_cycles = weeks_to_close / 2  # given 2 injections per week schedule
```

Present both conservative and aggressive scenarios using the weekly DCA range (e.g., $50/wk vs $100/wk).

## Critical Caveats

1. **OOR blocker:** If `in_range = false`, estimated daily fees may be $0. Treat milestone progress as halted until rebalanced.
2. **APR volatility:** Volume-driven APR can swing dramatically; always attach disclaimer: "Projection assumes constant pool conditions."
3. **Compounding ignored:** The formula assumes new DCA capital also earns the same APR and does not compound. Real timeline is shorter if rewards are reinvested.
4. **State file cross-check:** Use `~/.hermes/scripts/.lfj-aae-state.json` for `total_fees_earned_usd` and `last_position_usd` to detect DCA injections vs yield growth.
5. **HTML tracker stale:** The `yield-farm-tracker-CURRENT.html` is a rendered view; never parse it for computations. Read `.lfj-aae-config.json` and live DexScreener data.

## Example (from May 4, 2026)

- `position_usd = $83.92`
- `daily_fees ≈ $0.07` (volume $6.69M, TVL $3.92M)
- `apr_pct ≈ 31%`
- Target: M2 = $20/day
- `shortfall = $19.93/day`
- `additional_principal_needed = 19.93 * 365 / 0.31 ≈ $23,500`
- With `$75/week` DCA → `~313 weeks (6 years)`

**Note:** Position was OOR → effective gap infinite until rebalancing.