---
title: Cross-Chain Allocation Monitor Design
date: 2026-05-03
session: PROPS-LAND-real-estate-analysis
tags: [defi, allocation, monitoring, cross-chain]
---

# Cross-Chain Allocation Monitor Pattern

**Problem:** Track performance separately for yield generation layer (Solana) vs RWA hold layer (Avalanche) within a unified allocation strategy.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           Unified Allocation Dashboard                       │
├─────────────────────────────────────────────────────────────┤
│  Yield Layer (70%)          │  RWA Layer (10%)             │
│  ──────────────────────     │  ──────────────────────      │
│  Chain: Solana              │  Chain: Avalanche             │
│  Platform: Marinade/Raydium │  Tokens: PROPS, LAND         │
│  Asset: SOL, USDC           │  Strategy: Direct hold        │
│  Metric: Daily yield (USD)  │  Metric: Price change (USD)   │
│  Frequency: Hourly cron     │  Frequency: Daily cron        │
│  Alert: APR drop >20%       │  Alert: MCap swing >15%       │
└─────────────────────────────────────────────────────────────┘
```

## State Files

| File | Purpose | Chain Coverage |
|------|---------|----------------|
| `~/.hermes/scripts/.aae-allocation-state.json` | Total allocation breakdown | All chains |
| `~/.hermes/scripts/.solana-yield-state.json` | Daily yield, APR, fees earned | Solana only |
| `~/.hermes/scripts/.avalanche-rwa-state.json` | PROPS/LAND holdings, entry price, MCap | Avalanche only |
| `~/.hermes/scripts/.cross-chain-dca-schedule.json` | Weekly DCA splits across chains | Both |

## Monitoring Cadence

**Solana yield farms (hourly):**
- Fetch pool APR from Marinade/MarginFi/Raydium APIs
- Calculate projected daily/weekly yield from position size
- Alert if APR drops >20% in 24h (volume collapse or reward emission cut)

**Avalanche RWA holds (daily):**
- Fetch token prices from CoinGecko (no Binance support)
- Track MCap changes; flag if liquidity (volume) drops below $50K daily
- Weekly DCA trigger: buy from Amazon Flex income allocation

## Alert Logic

### Yield Layer Alerts
```python
if current_apr < historical_avg_apr * 0.8:
    alert = f"⚠️ SOL yield farm APR down {pct_drop:.1f}% — consider pool rotation"
if daily_yield_usd < 5 * (position_size / 1000):
    alert = f"📉 Yield efficiency low: ${daily_yield:.2f}/day (target: scale-based)"
```

### RWA Layer Alerts
```python
if token_mcap < 1000000:  # < $1M
    alert = f"🔴 Micro-cap warning: {ticker} MCap ${mcap/1e6:.2f}M — high IL risk"
if volume_24h < token_mcap * 0.01:  # < 1% of MCap daily
    alert = f"🟡 Low liquidity: {ticker} 24h volume ${volume/1e3:.0f}K — slippage risk"
```

## Integration with Existing Scripts

**Extension points:**
- `allocation_engine.py` — add RWA allocation class with regime-based weight
- `lp-aae-signal-monitor.py` — add cross-chain state aggregation
- D5 milestone tracker — add "RWA diversification" card alongside LP milestones

## Manual Verification Steps

1. Check Solana yield pools: `https://dexscreener.com/solana` + filter by Marinade/MarginFi
2. Check Avalanche RWA pools: Trader Joe pools for PROPS/AVAX, LAND/AVAX
3. Verify price feeds: CoinGecko API for `propbase`, `landshare` IDs
4. Audit DCA schedule: confirm weekly $50-100 split across chains as configured

## Open Questions
- Should RWA layer track portfolio diversification ratio (RWA % of total)?
- Bridge delay monitoring? (if moving capital Solana→Avalanche for RWA buys)
- Tax lot tracking for multi-chain holdings?
