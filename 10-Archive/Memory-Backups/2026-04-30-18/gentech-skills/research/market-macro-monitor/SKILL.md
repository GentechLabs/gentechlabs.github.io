---
name: market-macro-monitor
description: "Real-time market data lookup + personal finance impact analysis: crypto prices, forex rates, equity indices via free APIs. Translate macro moves into actionable insights for DeFi positions, travel currency, and portfolio decisions."
version: 1.0.0
author: Gentech
tags: [research, market-data, defi, forex, macro, coinbase, dexscreener]
trigger: "When the user asks about market conditions, price movements, macro events, currency conversion, or how news affects their positions/travel plans."
---

# Market Macro Monitor

Pull live market data and translate it into personal finance insights.

## Data Sources

### CoinMarketCap (preferred — richer data, needs API key)
```bash
# API key stored in /root/.hermes/scripts/cmc_config.json
# Read with: python3 -c "import json; print(json.load(open('/root/.hermes/scripts/cmc_config.json'))['coinmarketcap_api_key'])"

# Batch quote (symbol-based)
curl -s "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC,SOL,LINK,AVAX,TAO&convert=USD" \
  -H "X-CMC_PRO_API_KEY: $CMC_API_KEY"
```

**Why CMC?** More reliable for batch fetches, has 1h change data, doesn't rate-limit as aggressively.

**Key loading:** Read from `/root/.hermes/scripts/cmc_config.json` (primary) or `CMC_API_KEY` env var (fallback). All scripts across profiles use this pattern.

### CoinGecko (free, no key — fallback)
```bash
# Crypto prices + 24h change
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,avalanche-2&vs_currencies=usd&include_24hr_change=true"

# Forex via stablecoins (use USDT as USD proxy)
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=php,eur,gbp,jpy,krw,thb"
```

**Rate limits:** ~10-30 calls/min on free tier. Cache results, batch IDs in single calls.

### DexScreener (DEX pairs, LP pools)
```bash
# By pair address (e.g., LFJ AVAX/USDC on Avalanche)
curl -s "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea"

# By token symbol (less reliable for native assets)
curl -s "https://api.dexscreener.com/latest/dex/tokens/TOKEN_ADDRESS"
```

**Response structure:** `pairs[0].priceUsd`, `pairs[0].priceChange.24h`, `pairs[0].volume.24h`, `pairs[0].liquidity.usd`

### CoinGecko Market Overview
```bash
# Global market cap + BTC dominance
curl -s "https://api.coingecko.com/api/v3/global"
```

## Reading X Posts (Browser Fallback)

When xurl isn't authenticated, use browser_navigate to read X posts:
```
browser_navigate → https://x.com/i/status/POST_ID
```
Extract key data from the page snapshot (headline, numbers, sentiment).

## Analysis Framework

### For DeFi Positions
1. Check current price vs position range
2. Calculate fee efficiency: `(1 - abs(position - 0.5) * 2) * 100`
3. Assess if rebalance needed
4. Factor in macro context (risk-on vs risk-off)

### For Travel Currency
1. Look up USD → target currency rate (use USDT as proxy)
2. Compare to historical average (general knowledge)
3. Assess direction: weakening local currency = good for USD travelers
4. Give timing advice: lock in now vs wait

### For LP Pool Analysis (APR Estimation)
When evaluating a new LP pool (e.g., gold on LFJ), estimate APR from available data:

```python
# From DexScreener data
volume_24h = pair["volume"]["h24"]
liquidity = pair["liquidity"]["usd"]
fee_rate = 0.003  # Assume 0.3% swap fee (check pool's actual fee tier)

daily_fees = volume_24h * fee_rate
annual_fees = daily_fees * 365
apr = (annual_fees / liquidity) * 100
vol_liq_ratio = volume_24h / liquidity
```

**Interpretation:**
- APR > 100% = high but verify with multi-day volume (24h can be spiky)
- Vol/Liq ratio > 1.0 = heavily traded relative to depth (good for fees, risky for IL)
- TVL < $100K = thin pool, expect slippage on large trades
- Always check buy/sell ratio for directional pressure

### For Gold/Commodity Exposure
- **XAUt** (Tether Gold) = 1 token = 1 oz gold, available on multiple chains
- **PAXG** (Paxos Gold) = same concept, more liquid on Ethereum
- Gold price via CoinGecko: `ids=tether-gold` or `pax-gold`
- Gold LPs are rare on Avalanche — check LFJ for XAUt0/USDt pairs
- Gold is a macro hedge: up in risk-off, inflation, USD weakness; down in risk-on, rising real yields

### For Portfolio Decisions
1. Check BTC/ETH/majors for broad market direction
2. Look for correlation breaks (e.g., gold not rallying = liquidity crisis)
3. Assess oil/commodities impact on inflation narrative
4. Translate to: hold, accumulate, or de-risk

## Known Rate Limits & Pitfalls

- **CoinGecko free tier:** ~10-30 calls/min. Batch IDs. If 429, wait 60s.
- **CoinGecko on Cloudflare:** Website scraping blocked. Use API only.
- **CoinGecko IDs ≠ ticker symbols:** Always verify the CoinGecko ID via `/search` endpoint before adding tokens. Examples: LAND (not LSRWA), PROPS (not PROP). Wrong IDs silently return empty results.
- **DexScreener:** Native assets (AVAX, BTC) don't work by symbol — use pair address or contract address.
- **Forex via stablecoins:** USDT/PHP ≈ USD/PHP. Small spread (~0.1%) but acceptable for analysis.
- **X posts:** Browser may hit login walls. Snapshot usually still contains the post text.

## Example: Full Market Check

```bash
# 1. Crypto prices
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,avalanche-2&vs_currencies=usd&include_24hr_change=true"

# 2. Forex for travel
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=php,eur,thb"

# 3. Your LP pool
curl -s "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea"
```
