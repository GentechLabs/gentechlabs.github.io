---
name: crypto-watchlist-monitor
description: Monitor crypto token prices, volume, and news using CoinMarketCap API and CoinDesk via browser automation.
tags: [crypto, defi, monitoring, watchlist, prices, cron]
---

# Crypto Watchlist Monitor

## What Works
- **CoinMarketCap API** (preferred for cron jobs) — direct API calls, no browser needed
- **CoinDesk**: Use `browser_navigate` to `https://www.coindesk.com/` for news sentiment

## What Doesn't Work
- `web_extract` on CoinGecko API or CoinMarketCap pages — returns "Unauthorized" (bot protection)
- `web_search` may fail depending on provider auth status
- TheBlock is Cloudflare-hardened — blocked on current setup
- Vision tool with MiMo v2 Pro — text-only model, can't see images. Use mimo-v2-omni for vision.

## CMC API (Preferred — use for cron jobs)
- **API Key:** `[CMC-API-KEY-REDACTED]` (in `/root/.hermes/.env` as `COINMARKETCAP_API_KEY`)
- **Quote endpoint:** `https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC,SOL,LINK,AVAX,TAO,XAUt,BEAM&convert=USD`
- **Watchlist endpoint:** `https://pro-api.coinmarketcap.com/v1/watchlist/list?id=[CMC-WATCHLIST-ID-REDACTED]` (may not work on free tier)
- **Vault source:** `/root/vaults/gentech/03-Strategies/token-watchlist.md` — check for newly added tokens before running
- **CMC Watchlist URL:** https://coinmarketcap.com/watchlist/[CMC-WATCHLIST-ID-REDACTED]

### Parsing CMC API Response
```python
import json
data = json.loads(response)['data']
for symbol, info in data.items():
    price = info['quote']['USD']['price']
    chg24 = info['quote']['USD']['percent_change_24h']
    chg7d = info['quote']['USD']['percent_change_7d']
    mcap = info['quote']['USD']['market_cap']
    print(f"{symbol}: ${price:,.2f} | 24h: {chg24:+.1f}% | 7d: {chg7d:+.1f}%")
```

### API Response Notes
- All of Jordan's watchlist tokens work with the API (BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM)
- XAUt returns large price (gold-backed ~$4,800) — format accordingly
- BEAM returns small price (~$0.002) — use more decimal places

## Jordan's Watchlist
**Tokens:** BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM
**Source:** `03-Strategies/token-watchlist.md` in vault
**Do NOT hardcode tokens** — always read from vault or pull from CMC watchlist

## LP Position Integration
When combining watchlist with LP monitoring:
- **Pool:** AVAX/USDC `0x864d4e5Ee7318e97483DB7EB0912E09F161516EA` (Trader Joe / LFJ on Avalanche)
- **Range:** 9.00–9.40
- Check AVAX price from CMC API against range
- Report: in/out of range, earning fees or not

## Cron Job Ownership
- **YoYo runs YoYo's crons only** — don't create duplicate watchlist jobs in other agent profiles
- **Watchlist cron:** `faed4f588aef` in YoYo profile, every 2h (7AM–9PM UTC)
- **LP spot-check:** `c2c2e40b440e` in YoYo profile, hourly at :30, silent unless alert
- When watchlist runs, include LP data — consolidated report, no overlap

## Browser Fallback (if API fails)
Use `browser_navigate` to CMC, then `browser_console` with JS extraction:

```javascript
(() => {
  const rows = document.querySelectorAll('table tbody tr');
  const data = [];
  rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length > 5) {
      data.push({
        name: cells[2]?.textContent?.trim(),
        price: cells[3]?.textContent?.trim(),
        h24: cells[5]?.textContent?.trim(),
        d7: cells[6]?.textContent?.trim(),
        vol: cells[8]?.textContent?.trim()
      });
    }
  });
  return data.slice(0, 30);
})()
```

## Alert Thresholds
- ⚠️ 24h change > ±5%
- 🔥 7d change > ±10%
