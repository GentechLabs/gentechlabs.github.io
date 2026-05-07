# CoinGecko Free API — Behavior Notes

**Observed Date:** 2026-05-05

## Endpoint Used
```
GET https://api.coingecko.com/api/v3/simple/price
  ?ids=bitcoin,solana,chainlink,avalanche-2,bittensor,pax-gold,beam-2
  &vs_currencies=usd
  &include_24h_change=true
```

## Known ID Mapping for Watchlist

| Symbol | CoinGecko ID | Notes |
|--------|-------------|-------|
| BTC | `bitcoin` | Standard |
| SOL | `solana` | Standard |
| LINK | `chainlink` | Standard |
| AVAX | `avalanche-2` | Note the `-2` suffix |
| TAO | `bittensor` | **NOT `tao-bittensor`** — that returns `{}` |
| XAUt | `pax-gold` | Pax Gold tracks gold price |
| BEAM | `beam-2` | Note the `-2` suffix |

## ID Discovery
When an ID returns empty `{}`, use the search endpoint to find the correct ID:
```
GET https://api.coingecko.com/api/v3/search?query=<name>
```
Returns a `coins` array with `id`, `name`, `symbol` fields. The `id` field is what you pass to the price endpoint.

## Rate Limits
- Free tier: ~10-30 requests/minute (unofficial, no guarantees)
- If rate limited, responses may be empty or return 429
- No API key required for free tier

## Response Format
```json
{
  "bitcoin": {"usd": 81255, "usd_24h_change": 3.027},
  "solana": {"usd": 85.64, "usd_24h_change": 2.086}
}
```
- `usd_24h_change` is a float percentage (e.g., 3.03 = +3.03%)
- Missing coins in response = wrong ID (returns silently, no error key)

## Fallback Approach
1. Try CMC Pro API first (if key available)
2. Fall back to CoinGecko free API with known-correct IDs
3. If CoinGecko returns empty for a coin, run `/api/v3/search?query=<symbol>` to find correct ID
4. If all APIs fail, use browser_navigate to CoinGecko website and scrape
