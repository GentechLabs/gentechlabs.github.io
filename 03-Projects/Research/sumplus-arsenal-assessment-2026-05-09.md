# Sumplus Arsenal — Deep Dive Assessment

**Source:** [Sumplus Arsenal on ClawHub](https://clawhub.ai/skills?search=sumplus) | [Sumplus Docs](https://docs.sumplus.xyz) | [Arsenal API](https://arsenal.sumplus.xyz)
**Date:** 2026-05-09
**Tags:** #defi #ai-agents #skills-marketplace #api #multi-chain

---

## TL;DR
Sumplus Arsenal is a hosted DeFi execution API for AI agents — an "app store" for blockchain operations. 70 skills across 8+ chains. REST API with skill discovery + execution. Requires API key. Many skills are Arsenal-hosted (they run the RPC infrastructure). Relevant for our Solana and Ethereum DeFi work.

---

## What It Is
A skill registry + execution layer where AI agents can discover and run pre-built DeFi integrations via a simple REST API. Built by Sumplus, a CeDeFi yield protocol (aUSD/saUSD stablecoins). Arsenal is their agent-facing product.

**Base URL:** `https://arsenal.sumplus.xyz`
**Auth:** `Authorization: Bearer {ARSENAL_API_KEY}`
**Install (OpenClaw):** `openclaw skills install sumplus-arsenal`

## How It Works

1. **Search** — `GET /api/skills?search={intent}&limit=5` — find the right skill
2. **Execute** — `POST /api/execute` with `skill_id` + `input` params
3. **Rate** — Optional feedback loop for skill quality

Every skill has a `schema.input` defining what params it accepts and `schema.output` defining what comes back.

## Chain Coverage (70 skills total)

### Solana (2 skills) — ⭐ Relevant to us
- **Jupiter Aggregator** — DEX aggregator, best-price swap quotes
- **Raydium DEX** — Native AMM + CLMM, top trading pairs

### Ethereum (23 skills) — ⭐ Relevant to us
- **Uniswap V3** — Quotes, build transactions, pool info
- **Aave v3** — Lending markets, supply/withdraw/borrow/repay
- **Lido** — Liquid staking
- **Pendle v4** — Yield trading
- **Curve** — Stable swaps
- **Morpho Blue** — Direct lending markets
- **DefiLlama** — Read-only yield/portfolio data
- **Token Prices** — CoinGecko-powered
- **Wallet Manager** — Multi-chain balance queries (Alchemy)

### Bridges (7 skills) — ⭐ Useful
- **Wormhole** — Cross-chain lock/mint
- **Stargate V2** (LayerZero) — Unified liquidity bridge
- **Across Protocol** — Fast optimistic relayer
- **CCTP** (Circle) — USDC native bridge
- **deBridge DLN** — Order-book bridge
- **XLayer Bridge** — OKX L2 ↔ Ethereum

### Perpetuals & Market Data (3 skills)
- **GMX** — Perpetuals on Arbitrum/Avalanche
- **dYdX v4** — 290+ perpetual markets
- **Hyperliquid** — #1 decentralized perps

### Sui (10 skills)
- Cetus CLMM, Scallop, Suilend, NAVI, Aftermath, etc.
- Several in DEMO MODE

### Base (3 skills)
- Moonwell (lending), Aerodrome (DEX), Base SOP

### BSC (2 skills)
- PancakeSwap V3, StableStock (tokenized RWA)

### Optimism (1 skill)
- Velodrome V2

## Red Flags / Concerns

1. **ClawScan flagged** — "Skill flagged — review recommended" on ClawHub. Security scans passed (VirusTotal benign, static analysis benign) but ClawScan wants manual review.
2. **API key required** — No free tier documented. Need to register for access.
3. **Some skills in DEMO MODE** — Cetus CLMM, SUI Blockchain Toolkit, Sumplus Yield Optimizer return example data, not live.
4. **Main product is yield protocol** — Arsenal is a side product of Sumplus (CeDeFi stablecoin yield). Not a dedicated infrastructure company.
5. **Low adoption** — 0 downloads, 184 views on ClawHub. Very new.
6. **sumplus.xyz main site is down** — Returns NOT_FOUND. Docs site works.

## Relevance to GenTech / AAE

### What Overlaps
- **Solana DeFi** — Jupiter + Raydium could simplify swap execution for AAE
- **Ethereum DeFi** — Uniswap, Aave, Lido integrations for portfolio management
- **Cross-chain bridges** — Multiple options for multi-chain strategies
- **Market data** — Token prices, perpetuals data, DefiLlama
- **MCP compatible** — Designed for AI agent consumption

### What Doesn't Fit
- **Sui-heavy** — 10 of 70 skills are Sui, which we don't use
- **Demo mode skills** — Not production-ready
- **No Solana lending** — Missing Solend/MarginFi integrations
- **No LFJ/TJ** — No Trader Joe / LFJ integration (our primary DEX)
- **Centralized dependency** — All execution goes through their API

### Verdict: **Watch** 🟡

Interesting concept but too early for production use. The API-first approach is clean and the REST interface is agent-friendly. However:
- We already have direct integrations (LFJ, Jupiter, etc.)
- Low adoption + demo mode skills = risk
- Sumplus main product (yield protocol) is unrelated to our needs
- Worth revisiting when they have more Solana skills and proven uptime

## Action Items
- [ ] Register for API key to test live execution
- [ ] Test Jupiter Aggregator and Raydium skills on Solana
- [ ] Monitor for LFJ/Trader Joe integration
- [ ] Revisit in 30 days for adoption metrics

## Sources
- ClawHub: https://clawhub.ai/skills?search=sumplus
- Arsenal API: https://arsenal.sumplus.xyz
- Sumplus Docs: https://docs.sumplus.xyz
- X/Twitter: @SumPlusReal
