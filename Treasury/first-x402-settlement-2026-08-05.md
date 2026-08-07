# First Real x402 Settlement — DONE (Aug 5/6)

**Date:** 2026-08-05 (late) / 2026-08-06 (00:54 UTC)
**What:** First real on-chain x402 payment settled through the CDP facilitator.
**Endpoint paid:** `https://api.gentechlabs.net/v1/market/price/ETH`
**Payer wallet:** GTA arb `0x3d117Bf42218c3244AA0Ad011E8651A615230eCb`
**Amount settled:** 0.005 USDC (0.481 → 0.476 on Base)
**Result:** 402 → 200 OK, real data returned (ETH $1908.24, CoinMarketCap)

## The blocker fixed
The x402-api gateway was running with **stale CDP credentials** (key `dcc952…` / secret `CjVkAQ…`), causing the CDP facilitator to reject its JWT → **401 Unauthorized**. The `.env` had the correct keys (`f341f8…` / `p97RW1…`). Fixed by **restarting x402-api.service** to load the correct credentials.

## What this unlocks
- **Agentic.Market** ($52M+ TPV, Coinbase-backed) — auto-indexes after settle (up to 6h)
- **OpenDexter** — settle→catalog path
- **Real traction** — "people are paying for our rails"

## Pending
- [x] Verify CDP Bazaar / Agentic.Market indexes us (check in ~6h)
- [x] Confirm the settlement tx hash on-chain (Basescan needs API key)
- [ ] **ROOT CAUSE FOUND (Aug 6):** `extensions.bazaar.info.input` was missing `type`/`method`/`bodyType` — the exact silent-non-indexing failure from x402-foundation issue #2207. Fixed in server.py (added `type:http, method:GET, bodyType:json` + proper input/output schema). Service restarted, fresh settlement landed 09:15 UTC with corrected extension. Indexing takes up to 6h — cron `9d2fe8b08291` verifies.

## Script
`/root/vaults/gentech/10-Labs/x402-gateway/cdp-settle/cdp-settle.mjs`
