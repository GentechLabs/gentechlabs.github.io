---
name: cmc-watchlist-scraper
description: Fetch coin data from CoinMarketCap watchlists (public or private)
category: research
---

# CoinMarketCap Watchlist Scraper

Fetch coin prices, market cap, and % changes from CMC watchlist URLs.

## Problem
CMC watchlists require auth — `web_extract` returns `Unauthorized` (AUTH_ERROR). Browser automation is the reliable fallback.

## Steps

1. **Try web_extract first** (might work for public lists, often fails):
   ```
   web_extract(["https://coinmarketcap.com/watchlist/<id>"])
   ```

2. **If auth error, use browser**:
   ```
   browser_navigate("https://coinmarketcap.com/watchlist/<id>")
   ```

3. **Extract structured data via JS console** (more reliable than vision for tables):
   ```
   browser_console(expression='JSON.stringify([...document.querySelectorAll("table tbody tr")].map(r => { const cells = r.querySelectorAll("td"); return cells.length > 2 ? { rank: cells[1]?.textContent?.trim(), name: cells[2]?.textContent?.trim(), price: cells[3]?.textContent?.trim(), change24h: cells[5]?.textContent?.trim(), change7d: cells[6]?.textContent?.trim() } : null }).filter(Boolean))')
   ```

4. **If more than ~10 rows**, scroll down first then re-run JS:
   ```
   browser_scroll(direction="down")
   browser_console(expression=<same JS>)
   ```

## Known CoinGecko ID Mappings (for fallback)
Some tickers don't match CoinGecko IDs:

| Ticker | CoinGecko ID |
|--------|-------------|
| AVAX | `avalanche-2` |
| TAO | `bittensor` |
| XAUt | `tether-gold` |
| BEAM | `beam-2` |
| COQ | `coq-inu` |
| PROPS | `propbase` |
| XAG (Silver) | ❌ No CoinGecko ID — `"silver"` is unrelated worthless token. Use CMC browser scrape or note unavailable. |

## Pitfalls
- Vision analysis (`browser_vision`) can fail on CMC pages — JS extraction is more reliable
- Prices shift between calls (live data) — don't use for precise comparison
- Page layout may change — if JS returns empty, re-snapshot and adjust cell indices
- "12 coins in total" text confirms full list loaded; check row count matches

## Output Format
Returns JSON array:
```json
[
  {"rank": "1", "name": "BitcoinBTC", "price": "$75,354.43", "change24h": "0.20%", "change7d": "6.29%"},
  ...
]
```
