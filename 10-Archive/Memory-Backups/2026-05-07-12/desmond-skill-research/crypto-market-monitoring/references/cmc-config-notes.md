---
title: CMC Watchlist Configuration Notes
date: 2026-05-03
source: session — cmc-watchlist scraper missing, manual implementation
---

## CMC Pro API Setup
API Key: ff52c5f015c3490da49adf12513a6d55 (stored in ~/.hermes/scripts/cmc_config.json)

Key locations:
- ~/.hermes/scripts/cmc_config.json — runtime config
- /root/vaults/gentech/00-HQ/config/cmc-api-key.env — vault backup
- exported as CMC_API_KEY in ~/.bashrc

Watchlist ID: 67453707ad745f0bbd4ad54f (name: "Bullish")

Core tickers & CMC IDs:
  BTC: 1 | SOL: 5426 | LINK: 1975 | AVAX: 5805 | TAO: 22974
  XAUt: 5176 | BEAM: 28298 | COQ: 25967 | ARENA: 29335 | PROPS: 29618 | LAND: 24405

## Endpoints

Quotes Latest (multi-id):
  GET https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest
  Query: id=1,5426,1975,5805,22974,5176,2828&convert=USD
  Headers: X-CMC_PRO_API_KEY: <key>
  Response path: data[cmc_id].quote.USD.{price,percent_change_1h,percent_change_24h,percent_change_7d,volume_24h,market_cap}

Fallback — CoinGecko (public):
  GET https://api.coingecko.com/api/v3/simple/price
  Query: ids=bitcoin,solana,chainlink,avalanche-2,bittensor,tether-gold,beam-2
        &vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true
  Note: No 1h or 7d data from free tier

## Watchlist Script Behavior
- Schedule: Hourly 7 AM–9 PM UTC (cmc-watchlist.py cron)
- Threshold: Only reports if any coin moved ≥1.5% since last check
- State file: ~/.hermes/scripts/.cmc-watchlist-hourly-state.json
- Fallback chain: CMC → CoinGecko → error JSON
- Output: JSON with significant_movement flag and per-coin formatted strings

## Price Formatting Helper
def format_price(symbol, price):
    if price >= 1000:   return f"${price:,.0f}"
    elif price >= 1:    return f"${price:.2f}"
    elif price >= 0.01: return f"${price:.4f}"
    else:               return f"${price:.6f}"

## Discrepancies Found 2026-05-03
- DexScreener pool API for AVAX/USDC LFJ returned 404
- Trader Joe direct pool endpoint also unavailable
- Resolution: Use CMC spot price as proxy fallback; document clearly in report
- State file location: ~/.hermes/scripts/.lfj-aae-state.json was empty, actual state in .lfj-position-state.json
</content>