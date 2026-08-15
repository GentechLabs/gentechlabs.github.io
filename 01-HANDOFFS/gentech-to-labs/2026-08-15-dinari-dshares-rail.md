# From Gentech — Dinari dShares Tokenized Equity Rail (Labs handoff)

**Date:** 2026-08-15
**Source:** Avalanche X post + Dinari docs/API research
**Status:** ✅ GREENLIT by Jordan — scaffold as treasury integration candidate.

## The opportunity
Dinari (dShares) opened **724 tokenized US stocks/ETFs — full S&P 500 — to US investors**, settling on the **Dinari Financial Network (DFN)**, an **Avalanche L1** omni-chain orderbook. Also live on Arbitrum, Base, Plume; Solana imminent. Each dShare backed 1:1, dividends + corporate actions preserved.

**Why it matters:** a tokenized-equity rail on our home chain (Avalanche), complementing the Solana/Robinhood rails. Adds an equity leg to the Agentic Treasury alongside perps + LP positions. Self-custodied wallets are supported — fits the AAE pattern.

## Integration surface (verified from docs)
- **SDKs:** `@dinari/api-sdk` (JS/TS), `dinari-api-sdk` (Python), Java, Go.
- **API:** `api-enterprise.sbt.dinari.com` (sandbox) — Orders, Accounts, Entities, KYC, Portfolio, Cash, Dividends, Interest, Stock data, Quotes, Market hours, Websockets (draft).
- **Order types:** Market + Limit, via Managed Orders (Dinari creates tx) or Proxied/EIP-155 (self-custodied, we sign).
- **Sandbox faucet:** mints 1,000 mockUSD for testing — no real money needed to validate.
- **Auth:** API Key ID + Secret (headers `X-API-Key-Id`, `X-API-Secret-Key`) from Partners dashboard.

## Proposed build
`dinari-rail` integration:
1. Python SDK wrapper — order placement (market/limit), portfolio + dividend reads, cash balances.
2. Wire into Agentic Treasury as an equity leg.
3. Test in **sandbox** with the faucet before any real money.

## Blockers / human-gated
- **Jordan:** Partners signup (https://partners.dinari.com/auth/register), sandbox API key, entity + KYC. Production key stays private.
- **Labs:** needs the sandbox key to scaffold + test. Can start the wrapper structure now (SDK install, client, order/portfolio stubs) without the key.

## Full intel
`Treasury/dinari-dshares-rail.md` in the vault.
