# OpenDexter — x402 API Marketplace (MCP)

**Source:** https://open.dexter.cash/mcp
**Date:** 2026-08-03 (verified live)
**Server:** OpenDexter v0.5.0 — MCP server for discovering and paying for x402 APIs

---

## What it is

An **x402 API marketplace** exposed as an MCP server. Agents discover paid APIs via natural-language search, inspect exact pricing, and (with an authenticated wallet) pay-per-call via x402. **Directly in our lane** — we build x402 gateways.

## Tools (5 total)

| Tool | Auth | Purpose |
|---|---|---|
| `x402_search` | noauth | Natural-language marketplace search. Read-only, free, never pays. |
| `x402_check` | noauth/oauth2 | Inspect exact endpoint + request shape before paying. Quote-only anonymous. |
| `x402_access` | noauth | Wallet-gated API access (SIWS proof, not payment). |
| `x402_wallet` | oauth2 | View Dexter payment wallet (passkey; no private key exposed). |
| `dexter_portfolio` | oauth2 | Governed asset portfolio for authenticated session. |

## Verified working (read-only search)

`x402_search` returns real, verified listings with quality scores:
- **Crypto Price Feed** (x402.shizu.me, verified, q92)
- **Solana Token Safety Check** (x402-endpoints.onrender.com, verified, q98)
- **Wallet Analytics API** (gateway.spraay.app, verified, q91)
- Image Gen (Xona), DefiLlama prices, etc.

The marketplace is live and populated with verified x402 resources — this is a **real distribution channel for our own x402 services**, not vaporware.

## Relevance to GenTech

This is the **same distribution play** as Monid, Syra, pay-skills, 8004scan — a marketplace where our x402 services should be listed so agents can discover + pay for them. We already have 60+ x402-ready API dirs and a `PAY.md` program.

**Key insight:** OpenDexter is both a **place to list our services** AND a **working reference** for the x402 marketplace pattern we keep building toward.

## Integration options

1. **Register as a provider / list our services** — get GenTech's APIs (crypto-price, token-security, wallet-analytics, etc.) discoverable here. Need to find the provider/submission flow (dexter.cash or api.dexter.cash).
2. **Register the MCP server in Hermes** — so we can search/check x402 APIs as a tool. Endpoint is live and works.
3. **Cross-reference** — check if our existing services are already listed; if not, that's the listing gap.

## Status

🔭 **Exploration.** Endpoint verified live, tools enumerated, search proven working. Not yet registered in Hermes (OAuth/passkey wallet flow needed for paid tools; search is free/noauth).
**Next:** determine the provider-submission flow to list our x402 services; cross-ref against marketplace-audit.md.
