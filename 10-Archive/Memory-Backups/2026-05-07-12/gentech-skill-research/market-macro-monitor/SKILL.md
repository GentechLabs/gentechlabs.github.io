---
name: market-macro-monitor
description: "Real-time market data lookup + personal finance impact analysis: crypto prices, forex rates, equity indices, DeFi protocol research (TVL, categories, chain analysis), and token watchlist management via free APIs. Translate macro moves into actionable insights for DeFi positions, travel currency, and portfolio decisions."
version: 1.1.0
author: Gentech
tags: [research, market-data, defi, forex, macro, coinbase, dexscreener, defillama, rwa, watchlist]
trigger: "When the user asks about market conditions, price movements, macro events, currency conversion, protocol research (TVL, categories, chain analysis), token watchlist management, or how news affects their positions/travel plans."
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

### DeFiLlama (protocols, TVL, categories — most reliable)
```bash
# All protocols (large response ~5MB, cache it)
curl -s "https://api.llama.fi/protocols" > /tmp/llama_protocols.json

# Filter in Python for specific chains/categories
python3 -c "
import json
data = json.load(open('/tmp/llama_protocols.json'))
avax_rwa = [p for p in data if 'Avalanche' in p.get('chains',[]) and 'rwa' in p.get('category','').lower()]
for p in sorted(avax_rwa, key=lambda x: x.get('tvl',0) or 0, reverse=True):
    print(f\"{p['name']} | TVL: \${(p.get('tvl',0) or 0)/1e6:.2f}M | Category: {p.get('category','N/A')}\")
"

# Single protocol historical TVL
curl -s "https://api.llama.fi/protocol/landshare" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"Name: {d['name']}, Chains: {d.get('chains',[])}\")
for tvl in d.get('currentChainTvls',{}).items():
    print(f\"  {tvl[0]}: \${tvl[1]/1e6:.2f}M\")
"
```

**Why DeFiLlama?** No API key needed, no rate limits, no bot detection. Covers TVL, protocol categories, chain breakdowns, and historical data. Best source for RWA/DeFi protocol research. Response is large (~5MB for all protocols) — cache locally and filter in Python.

**Key fields per protocol:** `name`, `tvl`, `mcap`, `category`, `chains[]`, `slug`, `description`

**Pitfall:** The `/protocols` endpoint returns ALL protocols across all chains. Filter by chain and category in Python — don't try to paginate.

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

## Token Watchlist Management

When adding/removing tokens from Jordan's watchlist, coordinate across multiple files:

### Files to update (in order):
1. **`03-Strategies/cron-watchlist-config.md`** — Primary config the cron job reads. Move coin from `## Active Coins` to `## Removed` with strikethrough and reason.
2. **`03-Strategies/token-watchlist.md`** — Standalone reference. Strike through the row in the holdings table.
3. **`03-Strategies/cron-jobs.md`** — If there are pending research tasks for the token, cancel them with strikethrough.
4. **CMC watchlist** (manual) — The actual CoinMarketCap account watchlist at `coinmarketcap.com/watchlist/67453707ad745f0bbd4ad54f`. User must remove manually or via API.

### Removal reason format:
```
- ~~TICKER~~ — Project Name, brief description. Removed Mon YYYY — reason. Revisit condition if applicable.
```

### Pitfall:
Don't forget to check for hardcoded references in cron job prompts (the `prompt_preview` field). The cron job reads from the vault config file, so removing from the config is usually sufficient — but verify no symbol is hardcoded in the prompt text itself.

## Known Rate Limits & Pitfalls

- **CoinGecko free tier:** ~10-30 calls/min. Batch IDs. If 429, wait 60s.
- **CoinGecko on Cloudflare:** Website scraping blocked. Use API only.
- **CoinGecko IDs ≠ ticker symbols:** Always verify the CoinGecko ID via `/search` endpoint before adding tokens. Examples: LAND (not LSRWA), PROPS (not PROP). Wrong IDs silently return empty results.
- **DexScreener:** Native assets (AVAX, BTC) don't work by symbol — use pair address or contract address.
- **Forex via stablecoins:** USDT/PHP ≈ USD/PHP. Small spread (~0.1%) but acceptable for analysis.
- **X posts:** Browser may hit login walls. Snapshot usually still contains the post text.
- **Web search APIs unreliable in Hermes:** Brave API key often unset, Google blocks bot traffic, DuckDuckGo shows CAPTCHAs. Default to DeFiLlama API + terminal curl for crypto research. See `references/defillama-api.md` for patterns.
- **Browser bot detection:** CoinGecko, DeFiLlama website, and Google all use Cloudflare/bot protection. Use their REST APIs directly via curl instead of scraping.

## Example: Full Market Check

```bash
# 1. Crypto prices
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,avalanche-2&vs_currencies=usd&include_24hr_change=true"

# 2. Forex for travel
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=php,eur,thb"

# 3. Your LP pool
curl -s "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea"
```
