# DexScreener API — Endpoint Behavior Notes

**Observed Date:** 2026-05-04

## Pool Data Endpoints Tried

For AVAX/USDC pool on Avalanche (address: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`) on LFJ/Trader Joe:

### Failed Endpoints
1. `https://api.dexscreener.com/latest/dex/pools/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea`
   - **Response:** 301/Cloudflare challenge → HTML error page (`<title>Error</title>`, Cloudflare JS challenge script)
   - **Note:** Returns Tengine/nginx 301 → Cloudflare interstitial, not JSON

2. `https://openapi.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea`
   - **Response:** Empty body (no content)
   - **Note:** May be disabled endpoint or requires different path structure

### Working Fallback
- CMC Pro API `https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest` with symbol list → reliable JSON price data
- Used for: spot price range checks when DEX pool API unavailable

## Recommendation for Skill Implementers
- **Primary path:** Always attempt CMC Pro API first (requires API key in `cmc_config.json`)
- **Secondary path:** If pool data available, query DexScreener (try both endpoints with 5s timeout)
- **Fallback path:** If both fail, use CMC spot price and clearly mark `(using CMC fallback)` in report
- **Do not hard-require pool API** — LP status can be determined solely from range vs spot price