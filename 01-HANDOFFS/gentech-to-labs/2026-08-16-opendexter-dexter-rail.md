# Handoff — OpenDexter Listing (#41) — Dexter Facilitator Rail

**Date:** 2026-08-16
**From:** Gentech (nightly build)
**To:** Labs
**Status:** ✅ SHIPPED (code + tests) — ⏳ OPS REMAINING (deploy + trigger)

## What shipped

Root cause found for why GenTech's gateway is NOT appearing in OpenDexter
`x402_search` despite the Aug 12 self-payment:

**Our gateway settles Base proofs via the CDP facilitator, but OpenDexter only
auto-catalogs gateways that settle through the Dexter facilitator
(`x402.dexter.cash`).** CDP/GoPlausible/PayAI settlements do NOT trigger
cataloging. Dexter supports `eip155:8453` (Base) with the `exact` scheme, no
API key.

## Code shipped (`10-Labs/x402-gateway/server.py`)

- Added `DEXTER_FACILITATOR` constant (default `https://x402.dexter.cash`).
- Added `verify_proof_via_dexter()` — same `{x402Version, paymentPayload,
  paymentRequirements}` envelope as GoPlausible/PayAI paths; /verify then
  /settle, no auth.
- Wired routing: Base (`eip155:8453`) proofs route to Dexter when
  `X402_USE_DEXTER=1` (or `PAYMENT_VERIFY_MODE=dexter`). Default unchanged
  (CDP for Base).
- Tests: `test_dexter_rail.py` — 8/8 pass. Full suite 45/45 pass.

## OPS REMAINING (Labs)

1. Set `X402_USE_DEXTER=1` on the gateway service (x402-api.service) and restart.
2. Trigger a real Base settlement through the Dexter facilitator (self-payment
   via `dexter-verbose.mjs` or a real client call).
3. Re-check `x402_search` ~24h later — our gateway should auto-appear.

## Verification evidence

- `node dexter-search.mjs` (Aug 16): our gateway absent from all queries
  (token security, wallet analysis, gentech, api.gentechlabs.net).
- Dexter `/supported` returns `eip155:8453` (exact) — rail confirmed.
- Dexter `/verify` accepts the same envelope (returns 500 on fake proof lacking
  `permit2Authorization` — contract confirmed, real client proofs carry it).
