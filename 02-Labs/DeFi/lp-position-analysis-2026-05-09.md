# AVAX/USDC LFJ Position Analysis — 2026-05-09

**Analyst**: DMOB (Labs)
**Timestamp**: 2026-05-09 ~21:00 UTC
**Data Sources**: DexScreener API, CoinGecko, `.lfj-aae-config.json`, `.lfj-aae-state.json`

---

## Position Status: ✅ IN RANGE

| Metric | Value |
|--------|-------|
| AVAX Price | $9.96 |
| Range | $9.78 – $10.02 |
| Position in Range | 75.0% (well-centered) |
| Buffer to Low Edge | 1.81% |
| Buffer to High Edge | 0.60% |
| Range Width | 2.41% |
| Shape | CURVE |
| Fee Tier | 5 bps |
| Bin Step | 10 bps (24 bins) |

## Position Value & Fees

| Metric | Value |
|--------|-------|
| Position Value | $125.38 (6.758 AVAX + 58.5 USDC) |
| Pool TVL | $4,040,720 |
| Position/Pool Ratio | 0.0031% |
| Pool 24h Volume | $4,459,104 |
| Pool Daily Fees | $2,229.55 |
| Position Est. Daily Fees | $0.0519 |
| Position Est. Annual Fees | $18.94 |
| **Position APR** | **15.1%** |
| vs Staking APY (6.5%) | 2.3x advantage |

## Pool Health

| Metric | Value |
|--------|-------|
| Volume/TVL Ratio | 1.1x |
| 24h Transactions | 3,083 (1,495 buys / 1,588 sells) |
| Buy/Sell Ratio | 0.94 (slight sell pressure) |
| 24h Price Change | +0.8% |
| 6h Price Change | +1.21% |
| 1h Price Change | -0.30% |

## Risk Assessment: LOW

- **IL Amplification**: ~41x vs passive LP (tight 2.41% range)
- **Current IL**: Moderate — price well within range
- **Toxic Flow**: Low — position size negligible vs pool
- **Slippage**: <0.01% for full exit
- **Volatility Accumulator**: Active — tight range benefits from surge pricing
- **Bin Efficiency**: 24 bins — sufficient granularity

## Milestone Gap

| Tier | Daily Target | Current | Gap | Required Principal |
|------|-------------|---------|-----|-------------------|
| Scout | $5.00/day | $0.052/day | $4.948/day | $11,957 |
| Raider | $20.00/day | $0.052/day | $19.948/day | $48,165 |

**DCA Path to Scout**: ~159 weeks (3.1 years) at $75/week

## Key Discrepancy: Task Parameters vs Live Config

The cron task provided parameters from a May 6 snapshot:
- Range: 9.44–9.74 (Bid-Ask shape)
- Current Price: ~$9.60
- Reserves: 170,549 AVAX / 2,372,096 USDC

**Actual current config** (updated May 9):
- Range: 9.78–10.02 (CURVE shape)
- Live Price: $9.96
- Position: $125.38

The range was widened and shifted up between May 6 and May 9, and the shape changed from Bid-Ask to CURVE. Config is now better aligned with current price action.

## Recommendations

1. **No rebalance needed** — price well-centered in range
2. **DCA is critical** — position is capital-constrained (0.0031% of pool)
3. **Monitor price drift** — RED ALERT if AVAX < $9.78, WARNING if AVAX > $10.01
4. **Gas optimization** — wait for $50 compound threshold before harvesting
5. **Security** — review wallet approvals for LFJ router, revoke unused quarterly
6. **Config sync** — ensure all monitoring scripts use latest 9.78–10.02 range
