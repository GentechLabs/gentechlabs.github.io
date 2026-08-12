# GenTech Marketplace / Listing Registry

**Purpose:** Every marketplace, directory, website, or protocol where GenTech Labs is listed. One place to check when anything changes (new service, price change, rebrand, new chain, new endpoint) so we can update everywhere — no forgotten listings.

**The rule (Jordan, Aug 2 2026):** When we change ANYTHING about our services/brand/listing, update EVERY row here that's affected. The agent should prompt Jordan: "we changed X — want to go back and update Y?" if a row needs human action.

**How to use:**
- New listing → append a row with today's date
- Change to our services → scan this file, update each affected row
- Before a big change → this is the checklist

---

## 🟢 LIVE LISTINGS (verified)

| # | Platform | URL / Location | What's tracked | Status | Last verified |
|---|----------|---------------|----------------|--------|---------------|
| 1 | x402-list.com | https://x402-list.com/services/gentech-labs-x402-gateway | 6 endpoints, uptime, compliance, signability, price, traction | 🟢 ONLINE — page cache STALE (shows 6 services/Base; manifest has 8/6chains, will self-correct on ~5h rescan). Full sweep Aug 5 | 2026-08-05 |
| 2 | 8004scan.io (ERC-8004 registry) | https://8004scan.io/agents?chain=43114 · agent #1770 | GenTech Labs identity, 16 x402 endpoints, feedback | 🟢 LIVE (Avalanche, owner 0x7ebff188f2Eba16518C02864589b1403a5d1296a). **Metadata URI re-pointed Aug 11 → https://gentechlabs.net/.well-known/gentech-avax-metadata.json** (was rate-limited personal GitHub → 404 → AgentScan blanks). Now served from our own site, never rate-limited. | 2026-08-11 |
| 3 | api.gentechlabs.net (gateway) | https://api.gentechlabs.net | paid x402 services, /.well-known/x402, bazaar manifest | 🟢 LIVE — bazaar manifest **v9.1.0, 15+ endpoints, 7 chains** (verified 2026-08-11) | 2026-08-11 |
| 4 | gentechlabs.net | https://gentechlabs.net | Landing page, links to gateway + kit | 🟢 | 2026-08-02 |
| 4b | Games API (deal-tracker) | api.gentechlabs.net/v1/games/* (port 8080) | deal search, price-watch, release-radar, preorder-advisor | 🟢 LIVE + real data (was stub `[]`, fixed Aug 3) | 2026-08-03 |
| 4c | Crypto Price API | api.gentechlabs.net/v1/price (port 8082) | real-time crypto prices | 🟢 LIVE (was placeholder, fixed Aug 3) | 2026-08-03 |
| 4d | Gas Price API | api.gentechlabs.net/v1/gas (port 8084) | live gas prices (eth/base/polygon) | 🟢 LIVE (was all-zero placeholder, fixed Aug 3) | 2026-08-03 |
| 4e | Token Security API | api.gentechlabs.net/v1/score (port 8086) | Solana token risk scoring → Rugcheck engine | 🟢 LIVE (was placeholder, now proxies Rugcheck, fixed Aug 3) | 2026-08-03 |
| 4f | Agent Search API (search.gentechlabs.net) | https://search.gentechlabs.net | standalone Exa/Grok/Surf search | ⚫ DISABLED (dead shell — no provider keys; port conflict with gateway agent_discovery) | 2026-08-04 |
| 4g | **OpenDexter (x402 marketplace)** | https://open.dexter.cash/mcp | x402 API marketplace MCP — discover + pay x402 APIs (x402_search/check/access/wallet) | 🔭 EXPLORED Aug 3 — endpoint verified live, tools enumerated, search proven. **Jordan wants us listed here.** Next: find provider-submission flow to list our services. | 2026-08-03 |

## 📊 ACCURATE API INVENTORY (verified Aug 4, 2026)

The real, working, revenue-capable API surface. **This is the number to use** when counting "how many APIs are live."

**Via x402 gateway (api.gentechlabs.net, 8 services, all backends 🟢 ok):**
| # | Service | Endpoint | Backend port | Data source |
|---|---------|----------|--------------|-------------|
| 1 | token_security | /v1/token-security | 8088 (Rugcheck) | Solana risk scoring |
| 2 | market_intelligence | /v1/market | 8082 (crypto-price) | CoinMarketCap→CoinGecko |
| 3 | agent_discovery | /v1/agents/search | 8091 | 8004scan ERC-8004 registry |
| 4 | defi_lp_analytics | /v1/defi/lp | 8092 | DexScreener |
| 5 | wallet_analysis | /v1/wallet/portfolio | 8093 | Solana RPC + DexScreener |
| 6 | nft_search | /v1/nft/search | 8094 | Magic Eden |
| 7 | treasury_defender | /v1/defender | 8096 | RPC + DexScreener |
| 8 | lineage_guard | /v1/lineage | 8095 | DataHub GMS |

**Standalone APIs (direct subdomains):**
| # | API | Domain | Port |
|---|-----|--------|------|
| 9 | Games / Deals | deals.gentechlabs.net | 8080 |
| 10 | Crypto Price | prices.gentechlabs.net | 8082 |
| 11 | Gas Price | gas.gentechlabs.net | 8084 |
| 12 | Token Security (proxy) | security.gentechlabs.net | 8086 |
| 13 | Rugcheck | rugcheck.gentechlabs.net | 8088 |

**TOTAL: 13 live, working, revenue-capable APIs** (8 gateway services + 5 standalone). Plus the deal-tracker games API adds 4 gaming sub-endpoints (deals, price-watch, release-radar, preorder-advisor) on port 8080.

**DISABLED/DEAD (do not count):** Agent Search API (search.gentechlabs.net) — no provider keys, port conflict. ⚠️ deals.gentechlabs.net has an SSL/DNS cert gap (resolves to VPS direct IP, cert doesn't cover it) — works on localhost:8080 but public HTTPS fails; needs Cloudflare proxy toggle.


| 5 | GitHub — Gentech-Labs org | https://github.com/Gentech-Labs | programmable-money-x402, genTech-agent-kit, agent-credit-score (21 repos) | 🟢 PUBLIC + VISIBLE | 2026-08-02 |
| 6 | GitHub — ProtoJay4789 (personal) | https://github.com/ProtoJay4789 | All repos (kit, portfolio, etc.) | ⚠️ FLAGGED — web 404s despite public; use ORG URLs | 2026-08-02 |
| 7 | Agentic.Market (Bazaar) | https://agentic.market | Auto-indexed when CDP facilitator settles a payment | 🔴 NOT-INDEXED despite real settlement — **CDP platform gap, not our config** (Aug 11). Validation passes (200 + bazaarExtension), 0.025 USDC settled on Base (nonce 7), but search still `total:0`. Known bug x402-foundation#2112 (teams with 8+ settlements never indexed; `EXTENSION-RESPONSES` never emitted). **Decision (Jordan Aug 11): stop burning settlements on this lever — pivot to x402scan + OpenDexter.** Re-check only if CDP fixes indexing. | 2026-08-11 |

## 🟡 PENDING / WATCHLIST

| # | Platform | Notes | Action needed |
|---|----------|-------|---------------|
| 8 | x402.org / x402scan | Standard x402 scanner — check if we appear | Verify listing after fix settles |
| 8b | **Syra (syraa.fun)** | https://syraa.fun/marketplace | x402 marketplace | ⏳ CURATED/PARTNER — no self-serve provider flow. Confirmed Aug 11 via docs.syraa.fun. Syra catalog = own routes + named partners (Nansen, Jupiter, Squid, RISE, Purch Vault). Seller must be onboarded by Syra team. Action: Jordan reach out to Syra team directly, OR deprioritize. Their facilitator failover (Dexter→GoPlausible→PayAI) corroborates our multi-facilitator mapping. |
| 8c | **OpenDexter** | https://open.dexter.cash/mcp | x402 API marketplace MCP — get our services listed | 🔵 PIVOT TARGET (Aug 11). Indexes via a real settlement through **ITS** facilitator (separate from CDP). Verify our endpoints are recognized (`x402_check` → requiresPayment=True), then settle one payment through Dexter's facilitator to trigger cataloging. This is the working path — CDP/Agentic.Market is blocked (row 7). | 2026-08-11 |
| 9 | signal402 / other x402 directories | Was submitted earlier — verify status | Check + update |
| 10 | MCP directories (mcp-directory, etc.) | Our mcp-directory service reports ok — confirm which directories list us | Audit + collect URLs |
| 11 | **Freelance AI (by PayAI)** | https://build.avax.network/integrations/payai | Decentralized agent marketplace where AI agents hire/work for each other, x402 (Solana, Base, Avalanche). PayAI = the facilitator behind our WURK flow. Sell-side: list GenTech x402 services as freelance offerings. | Discovered 2026-08-05 (income scan). Open-entry (x402 standard, no stake). Register agents as sellers. |
| 12 | **BotWork** | https://www.botwork.network/ | P2P AI-agent freelance network (libp2p task protocol), escrow on Base L2, 90/5/5 split. TS SDK `npx botwork init`. Agents bid on tasks, deliver, get paid. Sell-side fit for GenTech dev/analysis agents. | Discovered 2026-08-05 (income scan). Open-entry, MIT SDK. List an agent via SDK. |
| 13 | **Amadeus Protocol — Agent Hub** | https://thegrid.id (amadeus_protocol) | AI agent marketplace (built on Bitte.ai infra) for trading/DeFi automation/investment agents. Cross-chain (Sui, Solana, ETH). Sell-side: list DeFi/analytics agents. | Discovered 2026-08-05 (income scan). Check registration flow before committing. |
| 14 | **BountyBook** | https://www.bountybook.ai · API https://api.bountybook.ai | Agent-first task marketplace on Base (x402/USDC). 181 jobs, 118 open, $638 available, avg $12.68/hr, 4% fee. REST API, no browser — identity = ETH key. | 🟢 **AGENT WALLET LIVE (Aug 11)** — throwaway agent wallet `0x80dD...1e47` generated + auth'd. Auth: GET /auth/nonce?address= → sign nonce with EIP-191 personal_sign → POST /auth/verify `{address, signature:0x-prefixed}` → Bearer token (saved /root/.blockrun/bountybook-token). Jobs claimable via authenticated API. |
| 15 | **Nevermined** | https://nevermined.ai · app https://nevermined.app | Sell-side AI-payments infra: register your service/API as a merchant, connect Stripe/Braintree, and get paid by AI agents (metered, x402-powered). PSP-agnostic. Partners: AWS, Visa, Mastercard, Exa. Live 1.2M requests/day, 342 active agents. | Discovered 2026-08-12 (income scan). Open-entry (register service, connect PSP). Strong fit — list our 13 x402 APIs (token security, DeFi intel, wallet analysis) as merchant services. SDK `@nevermined-io/payments`. |
| 16 | **Agent402 (agent402.app)** | https://agent402.app · intel https://intel.agent402.app | "Agentic commerce platform" — demand-intelligence for the agent economy: real-time signal feed (30k+ signals, 30+ sources) mapped against live x402 supply (Coinbase CDP, PayAI, Agentic Market). Surfaces coverage gaps + buildable opportunities. | Discovered 2026-08-12 (income scan). NOT a pure listing marketplace — it's an intelligence/coverage tool. Use it to find which DeFi/analytics categories have weak supply where we could ship first, and to verify our x402 presence per-facilitator. Contact `hello@agent402.app` for partner access. |

## ⚪ KNOWN BUT NOT PURSUED / OTHER

- Solana Foundation `pay` CLI (MPP/SIWX protocol) — separate protocol from x402, not applicable
- Pay skills catalog — MPP/SIWX based, not x402

---

## CHANGE PROTOCOL (run this on ANY service change)

1. Edit gateway/manifest → bump manifest version (currently 8.0.0)
2. Update this registry: mark affected rows, set "last verified" = today
3. Check x402-list.com (re-scans ~5h) — verify compliance chips still green
4. Check 8004scan — agent identity/metadata current?
5. If new service added → update manifest + x402-list endpoint list + this registry
6. If price changed → x402-list price chip + manifest prices
7. If brand/URL changed → EVERY row above + GitHub org description + landing page
8. If a real on-chain settlement lands → Agentic.Market auto-indexes (row 7 flips to LIVE)

**Prompt rule:** after any change, agent asks Jordan: "we changed X — want to go back and update [affected platforms]?" Do NOT silently skip rows.


| **Bankr (bankr.bot)** | Robinhood Chain + Base | LAUNCHED ✅ (Jul 22) | **$TREASURY token launched via Bankr** on Robinhood Chain: contract 0x56D03C0f4167cC2c26B781dE47E608d660F13ba3, 100B supply (85% LP / 15% creator vesting), claimable TREA ~39M (Revenue Monitor). PLUS gentech-x402-services SKILL.md published Aug 2 (Gentech-Labs/genTech-agent-kit/master/skills/bankr, 200) so Bankr agents can pay our 6 API services. Next: verify skill install + first paid API call; monitor TREA claims. | Verify skill discovery + first API settlement | 2026-08-02 (corrected — was already launched Jul 22) |

| **Treasury Defender (new service #7)** | Multi-chain | LIVE ✅ (Aug 2) | New paid x402 service (port 8096): classifies any token KNOWN/SUSPICIOUS (homoglyph detection + liquidity check), quarantines flagged tokens, returns safe burn calldata. 3 scam tokens from Jordan's Avalanche wallet already quarantined (ÚSDС, USḌC, UЅDС). Manifest v9.0.0. | Add to Bankr skill + x402-list rescan | 2026-08-02 |
---

*Last updated: 2026-08-12 (income scan — added Nevermined #15 + Agent402 #16 to watchlist; Hive scan: 2 open Token Launch tasks, both assigned, no auto-bids)*

| **Solana Homebase** | https://github.com/Gentech-Labs/solana-homebase | Agentic Treasury orchestrator — Solana homebase (Superteam tranche-2 MVP) | 🟢 PUBLIC + LIVE (Aug 5) | 2026-08-05 |
