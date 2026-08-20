# AgentCash / Demand-Site Discovery — OpenAPI Compliance Fix

**Date:** 2026-08-20

## What was done
Rebuilt the `/openapi.json` handler in `x402-gateway/server.py` so it generates
per-service path entries from the live bazaar manifest (`SERVICES`), instead of
the old generic `/v1/{service}/{path}` catch-all.

## Why (AgentCash discovery spec, read at agentcash.dev/docs/discovery)
AgentCash is the primary "big boy" demand channel (distributes to Claude,
Cursor, Codex + every agent on x402/MPP; 959K+ paid calls). Its discovery
precedence:
1. `/openapi.json`
2. Correct 402 header response

The old spec failed AgentCash's probe on:
- **Input/Output Schema Missing** — generic `/v1/{service}/{path}` had no input/output schema per endpoint
- **No Payment Modes Detected** — only one generic `x-payment-info`
- **`x-discovery.ownershipProofs`** — was entirely missing

## Changes applied
- `openapi` → 3.1.0 (was 3.0.0)
- `info.title`/`description` now pulled from manifest
- Added `x-discovery.ownershipProofs: ["gentechlabs-erc8004-1770"]`
- Per-service paths built from `SERVICES`, each carrying:
  - real `x-payment-info` price (`price_usd` from manifest, formatted to 6 decimals)
  - `x402` protocol
  - `402` response (Payment Required)
  - input `parameters` for path params (`{address}`, `{symbol}`, etc.)
  - request body examples for `agent_research` and `deal_tracker` (fixes "Expected 402, got 400")
- Skip services with no price (treasury_defender currently has `price_usd: null`)

## Verified
- Gateway restart → `active`, health `{status: ok, services: 11}`
- `/openapi.json` → openapi 3.1.0, title/version correct, `x-discovery` present, **10 paid endpoints with `x-payment-info`** (up from 1 generic)
- `/v1/market/price/BTC` → 402 with full `payment-required` + `www-authenticate` headers (discovery precedence #2 intact)

## Files touched
- `/root/vaults/gentech/10-Labs/x402-gateway/server.py` (openapi handler, lines ~881-938)

## Next steps
- ✅ **AgentCash discovery verified end-to-end** (`agentcash@0.17.0 discover`):
  - `found: true`, `source: openapi`, `trustTier: ownership_verified`
  - 17 total endpoints, **10 paid (x402)** correctly identified
  - `ownershipProofs: ["gentechlabs-erc8004-1770"]` read by agentcash
  - All 10 paid endpoints listed with correct paths
- ✅ AgentCash has NO registration form — it's discovery-based, indexes from `/openapi.json` + correct 402.
- Confirm x402scan picks up the new spec (their crawler reads `/.well-known/x402` + `openapi.json`); it auto-indexes from the discovery contract.
- Consider adding `x-discovery.ownershipProofs` to the bazaar manifest itself (not just openapi).
