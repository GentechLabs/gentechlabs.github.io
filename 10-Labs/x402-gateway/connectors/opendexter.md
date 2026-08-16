# Connector: OpenDexter / Dexter — x402 API Marketplace (MCP)

> **Source:** https://open.dexter.cash/mcp
> **Verified live:** 2026-08-03 (OpenDexter v0.5.0)
> **Status:** ✅ Verified — read-only search proven working

## What it catalogs

An **x402 API marketplace** exposed as an MCP server. Agents discover paid APIs via
natural-language search, inspect exact pricing, and (with an authenticated wallet)
pay-per-call via x402. Directly in our lane — we build x402 gateways.

## The 5 tools

| Tool | Auth | Purpose |
|---|---|---|
| `x402_search` | noauth | Natural-language marketplace search. Read-only, free, never pays. |
| `x402_check` | noauth/oauth2 | Inspect exact endpoint + request shape before paying. Quote-only anonymous. |
| `x402_access` | noauth | Wallet-gated API access (SIWS proof, not payment). |
| `x402_wallet` | oauth2 | View Dexter payment wallet (passkey; no private key exposed). |
| `dexter_portfolio` | oauth2 | Governed asset portfolio for authenticated session. |

## The settle→index flow (the key gotcha)

- **Settle through the Dexter facilitator** → the marketplace **auto-catalogs** you.
  This is the important part: you don't submit a separate listing form. If your
  gateway settles via the Dexter facilitator, you appear in `x402_search` results
  automatically.
- **Quality score** is computed per listing (e.g. q92, q98) — verified, live
  resources rank higher. Keep your endpoint up and your `PAY.md` accurate.

## Verified live listings (Aug 3)

- **Crypto Price Feed** (x402.shizu.me, verified, q92)
- **Solana Token Safety Check** (x402-endpoints.onrender.com, verified, q98)
- **Wallet Analytics API** (gateway.spraay.app, verified, q91)
- Image Gen (Xona), DefiLlama prices, etc.

## Gotchas we hit

1. **No separate listing form** — you get listed by settling through the Dexter
   facilitator. If you're not appearing in search, check which facilitator your
   gateway uses.
2. **Paid tools need OAuth/passkey wallet** — `x402_search` is free/noauth, but
   `x402_wallet` and `dexter_portfolio` need an authenticated session. No private
   key is ever exposed (passkey-based).

## Our status

- Registry row 4g verified Aug 3 (endpoint live, tools enumerated).
- Funding path identified (0x7ebff owner wallet).
- **Aug 12:** 0.005 USDC self-payment through Dexter's facilitator succeeded
  (tx on Base, eip155:8453). Root-cause fix: removed em-dash from challenge
  description (broke Node `btoa()`).
- **Aug 16 (ROOT CAUSE FOUND):** Our gateway was NOT appearing in `x402_search`
  despite the Aug 12 settlement because **our gateway settles Base proofs via
  the CDP facilitator, NOT the Dexter facilitator.** OpenDexter only auto-catalogs
  gateways that settle through `x402.dexter.cash`. CDP/GoPlausible/PayAI
  settlements do NOT trigger cataloging.
- **Aug 16 (FIX SHIPPED):** Added `verify_proof_via_dexter()` to the gateway
  (`server.py`) — routes Base (`eip155:8453`) proofs through the Dexter
  facilitator when `X402_USE_DEXTER=1` (or `PAYMENT_VERIFY_MODE=dexter`).
  Dexter supports Base with the `exact` scheme, no API key. 8/8 new tests pass
  (45 total). **Next:** set `X402_USE_DEXTER=1` on the gateway service, then
  trigger a real Base settlement through Dexter → OpenDexter auto-catalogs us.
  Re-check `x402_search` ~24h after.
