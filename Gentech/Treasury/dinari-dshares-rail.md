# Dinari dShares — Tokenized Equity Rail (Treasury Intel)

**Date:** 2026-08-15
**Source:** Avalanche X post (https://x.com/i/status/2088289307287253371) + Dinari docs/API research
**Status:** ✅ GREENLIT by Jordan — add as treasury integration candidate, hand off to Labs to scaffold.

## What it is
- **Dinari (dShares)** — B2B enterprise API for tokenized US stocks/ETFs. **724 assets, full S&P 500**, now open to eligible US investors.
- Each dShare backed **1:1** by the underlying security in custody; preserves **dividends, voting rights (where permissible), corporate actions**.
- Settles on the **Dinari Financial Network (DFN)** — an **Avalanche L1** omni-chain orderbook. Also live on Arbitrum, Base, Plume; **Solana imminent**.
- Validators/custody: Gemini, BitGo, VanEck. Dinari is a Registered Transfer Agent (SEC 17A(c)); Dinari Securities LLC is a Registered Broker-Dealer (FINRA/SIPC).

## Why it fits the treasury
- **Self-custodied wallets supported** — an agent can hold dShares in its own wallet and place orders via Dinari smart contracts or *Proxied Orders*. This is the Agentic Treasury pattern, not a custodial walled garden.
- **Cash leg is USD+** (yield-bearing stablecoin) — treasury can hold yield-bearing cash *and* equity exposure on the same rail.
- **On our home chain** (Avalanche) — complements the Solana/Robinhood rails. Adds a tokenized-equity leg alongside perps + LP positions.

## Integration surface (verified from docs)
- **SDKs:** `@dinari/api-sdk` (JS/TS), `dinari-api-sdk` (Python), Java, Go.
- **API:** `api-enterprise.sbt.dinari.com` (sandbox) — Orders, Accounts, Entities, KYC, Portfolio, Cash, Dividends, Interest, Stock data, Quotes, Market hours, Websockets (draft).
- **Order types:** Market + Limit, across Managed Orders (Dinari creates tx) and Proxied/EIP-155 (self-custodied, we sign).
- **Sandbox faucet:** mints 1,000 mockUSD for testing — no real money needed to validate.
- **Auth:** API Key ID + API Secret Key (headers `X-API-Key-Id`, `X-API-Secret-Key`), from Partners dashboard.

## Honest caveats
- **KYC/AML gating** — requires an entity + identity verification. **Human-gated (Jordan only).**
- **API integration, not a pure on-chain swap** — needs Partners account + API keys.
- **Managed vs self-custodied** is a real design choice: managed = simpler/more custodial; self-custodied = more aligned with AAE, more work.

## Proposed build (for Labs)
`dinari-rail` integration:
1. Python SDK wrapper (order placement market/limit, portfolio + dividend reads, cash balances).
2. Wire into Agentic Treasury as an equity leg.
3. Test in **sandbox** with the faucet before any real money.

## Jordan signup checklist (human-gated)
1. Create Partners account: https://partners.dinari.com/auth/register
2. Generate API key (sandbox env first) — save Key ID + Secret.
3. Complete entity + KYC.
4. Share sandbox key with Labs to scaffold; keep production key private.

## Next actions
- **Jordan:** Partners signup + sandbox API key + KYC.
- **Labs:** scaffold `dinari-rail` (Python SDK, sandbox test with faucet).
- **Gentech:** track as treasury integration candidate; revisit for production once sandbox validated.
