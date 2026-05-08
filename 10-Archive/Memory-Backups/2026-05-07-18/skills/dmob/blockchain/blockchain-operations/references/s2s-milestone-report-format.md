# S2S Milestone Report Generation

**Required output format** (User-specified):

```
💰 Capital Update: [DCA Boost detected ($X injection on DATE) | Current: $Y vs Pre-Boost: $Z (net -$Δ)]  OR  [Steady]
🏁 Progress: $[current_daily_est] / $[target_daily] ([pct]% to [tier])
⏳ Gap: $[gap_amount] principal needed at current [apr]% APR
🛠️ DCA Path: [X] weeks ([Y] years) at current rate (Sun-Wed/Thu-Sat split)
💡 Pro Tips:
  [1. Tip title → Expected impact]
  [2. Tip title → Expected impact]
  [3. Tip title → Expected impact]
```

## Data Sources (priority order)

1. `s2s-milestone-report.json` (comprehensive prior analysis)
2. Vault log: `03-Projects/DeFi/LFJ-AVAX-USDC.md` (daily entries)
3. Runtime state: `~/.hermes/scripts/.lfj-aae-state.json`
4. Config: `03-Strategies/scripts/.lfj-aae-config.json`

## Capital Update Logic

- Compare current total position (`config.position.total_usd` or state `last_position_usd`) against last recorded value from the S2S report or vault log.
- If increase > $1: `DCA Boost detected ($X injection on DATE | Current: $Y vs Pre-Boost: $Z)`
- Else: `Steady`

## Progress Calculation

- `current_daily_est`: Use live DexScreener + config to compute fees, OR read from S2S report `apr_estimate_pct` to derive.
- `target_daily`: Next milestone threshold (M1: $5, M2: $20, M3: $50, etc.)
- `pct = (current_daily_est / target_daily) * 100`
- `tier`: Derived from current milestone index.

## Gap Field

- If `apr > 0` and position IN RANGE:
  `gap_amount = round((target_daily - current_daily_est) * 365 / (apr/100), 2)`
- Else: leave as `$[gap_amount]` with note that it's infinite while OOR.

## DCA Path

- Weekly average = `(50+100)/2 = $75`
- `weeks = gap_amount / weekly_average`
- `years = weeks / 52`
- Always mention split: `Sun-Wed/Thu-Sat`

## Pro Tips (priority)

1. Range efficiency: If `eff < 50%` → widen/tighten as appropriate, rebalance.
2. Config sync: If multiple config files have diverged values, consolidate.
3. Compounding: Claim and reinvest frequently if threshold met.
4. Volume monitoring: If pool TVL or volume trends down, consider moving capital.
5. OOR urgency: If out-of-range, prioritize rebalance over additional DCA.

## Example Output

```text
💰 Capital Update: 🚀 DCA BOOST DETECTED: +$55.26 injected on 2026-04-27 | Current: $83.92 vs Pre-Boost: $28.66
🏁 Progress: $0.00 / $20.00 (0%) — Position OUT OF RANGE, yield currently $0
⏳ Gap: Using estimated in-range APR ~21.6% (based on historical earnings), additional principal needed to hit M2 ≈ $33,661. At current $75/week DCA, timeline ≈ 449 weeks (~8.6 years). *Note: Gap is effectively infinite while out of range.*
🛠️ DCA Path: N/A until position rebalanced back in range and generating positive yield. Once earning, at $50–100/week average, projected closure would still be ~8+ years — urgent optimization required.
💡 Pro Tips:
  1. Rebalance range IMMEDIATELY — current price ~$9.20 is below your range ($9.33–$9.52), efficiency 0%, earning nothing. Shift range to ~$9.10–$9.30 to include current ~$9.20; being OOR is the primary yield killer.
  2. Tighten range after rebalancing — once price stabilizes, reduce width to ~5–6% to increase fee capture and APR; monitor binStep for optimal liquidity concentration.
  3. Compound any claimable rewards daily — even small amounts benefit from exponential growth; set up automated claiming during active earning periods.
```