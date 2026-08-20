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
| 2 | 8004scan.io (ERC-8004 registry) | https://8004scan.io/agents?chain=43114 · agent #1770 | GenTech Labs identity, 16 x402 endpoints, feedback | 🟢 LIVE (Avalanche, owner 0x7ebff188f2Eba16518C02864589b1403a5d1296a). **Metadata URI re-pointed Aug 11 → https://gentechlabs.net/.well-known/gentech-avax-metadata.json** (was rate-limited personal GitHub → 404 → AgentScan blanks). **Image field fixed Aug 12** — was pointing to rate-limited `raw.githubusercontent.com/.../gentech-logo.png` (404); re-pointed to `https://gentechlabs.net/gentech-logo.png` (self-hosted, 200 verified). | 2026-08-12 |
| 3 | api.gentechlabs.net (gateway) | https://api.gentechlabs.net | paid x402 services, /.well-known/x402, bazaar manifest | 🟢 LIVE — bazaar manifest **v9.1.0, 9 services, 7 chains** (verified 2026-08-15). **FULLY CDP-COMPLIANT Aug 15** — fixed discovery schema (GET→pathParams) + nginx proxy_buffer 16k (was dropping 402). CDP validate now `valid:true, simulation:accepted`. | 2026-08-15 |
| 4 | gentechlabs.net | https://gentechlabs.net | Landing page, links to gateway + kit | 🟢 | 2026-08-02 |
| 4b | Games API (deal-tracker) | api.gentechlabs.net/v1/games/* (port 8080) | deal search, price-watch, release-radar, preorder-advisor | 🟢 LIVE + real data (was stub `[]`, fixed Aug 3) | 2026-08-03 |
| 4c | Crypto Price API | api.gentechlabs.net/v1/price (port 8082) | real-time crypto prices | 🟢 LIVE (was placeholder, fixed Aug 3) | 2026-08-03 |
| 4d | Gas Price API | api.gentechlabs.net/v1/gas (port 8084) | live gas prices (eth/base/polygon) | 🟢 LIVE (was all-zero placeholder, fixed Aug 3) | 2026-08-03 |
| 4e | Token Security API | api.gentechlabs.net/v1/score (port 8086) | Solana token risk scoring → Rugcheck engine | 🟢 LIVE (was placeholder, now proxies Rugcheck, fixed Aug 3) | 2026-08-03 |
| 4f | Agent Search API (search.gentechlabs.net) | https://search.gentechlabs.net | standalone Exa/Grok/Surf search | ⚫ DISABLED (dead shell — no provider keys; port conflict with gateway agent_discovery) | 2026-08-04 |
| 4g | **OpenDexter (x402 marketplace)** | https://open.dexter.cash/mcp | x402 API marketplace MCP — discover + pay x402 APIs (x402_search/check/access/wallet) | 🔭 EXPLORED Aug 3 — endpoint verified live, tools enumerated, search proven. **Jordan wants us listed here.** Next: find provider-submission flow to list our services. | 2026-08-03 |
| 4h | **AgentLux (agentlux.ai)** | https://agentlux.ai/agents/0x7ebff188f2Eba16518C02864589b1403a5d1296a | Agent-native work/payment network on Base. Identity + services marketplace + x402. **First-Hire Guarantee: first quality listing gets a platform-funded escrowed hire within 24h, paid in USDC.** | 🟢 **LIVE (Aug 12)** — agent `9fed6922-48d0-4ed6-975a-c828bdf02446` registered (wallet 0x7ebf…96a), provider profile public, **DeFi LP analysis + token security listing LIVE** (id 6581ec2d-7041-4d86-8571-19548b83bec6, $15, public). Auth via free challenge-sign (JWT /root/.blockrun/agentlux-token, 1hr). **First-Hire Guarantee armed — watch for hire request ~24h.** Fully autonomous (no human key). | 2026-08-12 |
| 4i | **AgentCash (agentcash.dev)** | https://agentcash.dev · docs https://agentcash.dev/docs/sell-to-agents | x402/MPP discovery layer — "one balance, every API" for agents (Claude, Cursor, Codex, Hermes). 3,200+ premium APIs, 1.1M+ paid calls, $100K onboarding bonus. Sellers publish `/openapi.json` with `x-payment-info` + 402 responses → auto-discoverable. | 🟢 **LIVE (Aug 14)** — discovery-gated (no registration form; the listing IS our gateway). Wired `x-guidance` + `x-payment-info` (x402 protocol) into `api.gentechlabs.net/openapi.json` (v9.1.0), restarted x402-api.service, verified 200 + 402 flow intact. Fully autonomous. Income = settled USDC to our wallet (on-chain scan covers it). Re-check ~24h for our origin in AgentCash search. | 2026-08-14 |

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
| 7 | Agentic.Market (Bazaar) | https://agentic.market | Auto-indexed when CDP facilitator settles a payment | 🔴 NOT-INDEXED despite real settlement — **CDP platform gap, not our config** (Aug 11). **Aug 15: gateway now FULLY CDP-COMPLIANT** (`valid:true, simulation:accepted` after schema + nginx fixes) but STILL `index:null`. Confirmed upstream CDP bug (x402-foundation#3045). Posted contribution documenting our clean v2 control case. **Decision (Jordan Aug 11): stop burning settlements on this lever — pivot to x402scan + OpenDexter.** Re-check only if CDP fixes indexing. | 2026-08-15 |

## 🟡 PENDING / WATCHLIST

| # | Platform | Notes | Action needed |
|---|----------|-------|---------------|
| 8 | x402.org / x402scan | Standard x402 scanner — check if we appear | Verify listing after fix settles |
| 8b | **Syra (syraa.fun)** | https://syraa.fun/marketplace | x402 marketplace | ⏳ CURATED/PARTNER — no self-serve provider flow. Confirmed Aug 11 via docs.syraa.fun. Syra catalog = own routes + named partners (Nansen, Jupiter, Squid, RISE, Purch Vault). Seller must be onboarded by Syra team. Action: Jordan reach out to Syra team directly, OR deprioritize. Their facilitator failover (Dexter→GoPlausible→PayAI) corroborates our multi-facilitator mapping. |
| 8c | **OpenDexter** | https://open.dexter.cash/mcp | x402 API marketplace MCP — get our services listed | 🟢 **SETTLED Aug 12** — 0.005 USDC self-payment through Dexter's facilitator succeeded (tx on Base, eip155:8453). **Root-cause fix: removed em-dash (—) from gateway challenge description** — broke Node `btoa()` ("Invalid character") for all x402 clients. Gateway restarted (x402-api.service). Settlement now triggers auto-cataloging — **re-check ~24h for our gateway to appear in x402_search.** | 2026-08-12 |
| 9 | signal402 / other x402 directories | Was submitted earlier — verify status | Check + update |
| 10 | MCP directories (mcp-directory, etc.) | Our mcp-directory service reports ok — confirm which directories list us | Audit + collect URLs |
| 11 | **Freelance AI (by PayAI)** | https://build.avax.network/integrations/payai | Decentralized agent marketplace where AI agents hire/work for each other, x402 (Solana, Base, Avalanche). PayAI = the facilitator behind our WURK flow. | ✅ **COVERED (Aug 12)** — PayAI is the x402 *facilitator*, not a registerable seller marketplace. Our Avalanche rail already settles via PayAI (see server.py rail config). No separate seller onboarding exists — a payable x402 endpoint IS the listing, which we have. No action. | 2026-08-12 |
| 12 | **BotWork** | https://www.botwork.network/ | P2P AI-agent freelance network (libp2p task protocol), escrow on Base L2, 90/5/5 split. TS SDK `npx botwork init`. Agents bid on tasks, deliver, get paid. Sell-side fit for GenTech dev/analysis agents. | Discovered 2026-08-05 (income scan). Open-entry, MIT SDK. List an agent via SDK. |
| 13 | **Amadeus Protocol — Agent Hub** | https://thegrid.id (amadeus_protocol) | AI agent marketplace (built on Bitte.ai infra) for trading/DeFi automation/investment agents. Cross-chain (Sui, Solana, ETH). Sell-side: list DeFi/analytics agents. | Discovered 2026-08-05 (income scan). Check registration flow before committing. |
| 14 | **BountyBook** | https://www.bountybook.ai · API https://api.bountybook.ai | Agent-first task marketplace on Base (x402/USDC). 181 jobs, 118 open, $638 available, avg $12.68/hr, 4% fee. REST API, no browser — identity = ETH key. | 🟢 **AGENT WALLET LIVE (Aug 11)** — throwaway agent wallet `0x80dD...1e47` generated + auth'd (token /root/.blockrun/bountybook-token, 1hr expiry, refresh via /tmp/bb-auth/auth.js). Claim+submit flow proven end-to-end. **⛔ NEVER PAID OUT (Aug 12) — PARK IT.** Reproduced code_test verifier crash (`required_fields.length` vs `required_files` → `undefined.length`; `checksFailed:["ipfs_fetch"]`) on the exact documented inline payload twice. Lifetime code_test settlements 0/32. Non-code verified jobs show `payout_status=failed`, no tx, treasury 0x1bc6...72f2b zero lifetime USDC outflows on Base — **no USDC has EVER moved**. Operator's $150 fix offer (job 8a7bd232) claimed by another agent. IPFS pinning does NOT help (server-side spec bug). No public GitHub. Contact: Discord discord.gg/BXKTe44Y, X @_ptonik. Re-check ~Aug 19: if verified jobs start showing payout_tx_hash, becomes best autonomous rail. Full diag: 09-Green Room/bountybook-full-diagnosis-2026-08-12.md |
| 15 | **Nevermined** | https://nevermined.ai · app https://nevermined.app | Sell-side AI-payments infra: register your service/API as a merchant, connect Stripe/Braintree, and get paid by AI agents (metered, x402-powered). PSP-agnostic. Partners: AWS, Visa, Mastercard, Exa. Live 1.2M requests/day, 342 active agents. | 🟢 **LIVE (Aug 12) — 5 services registered on mainnet.** token_security, market_intel, defi_lp_analytics, wallet_analysis, nft_search ($0.01–0.02/call). Settlement wallet 0x7ebf…96a, USDC on Base. Agent/plan IDs in `/root/.blockrun/nevermined-ids`. API key stored `/root/.blockrun/nevermined-api-key`. **Next: verify discovery indexing + watch for paid calls.** |
| 16 | **Agent402 (agent402.app)** | https://agent402.app · intel https://intel.agent402.app | "Agentic commerce platform" — demand-intelligence for the agent economy: real-time signal feed (30k+ signals, 30+ sources) mapped against live x402 supply (Coinbase CDP, PayAI, Agentic Market). Surfaces coverage gaps + buildable opportunities. | Discovered 2026-08-12 (income scan). NOT a pure listing marketplace — it's an intelligence/coverage tool. Use it to find which DeFi/analytics categories have weak supply where we could ship first, and to verify our x402 presence per-facilitator. Contact `hello@agent402.app` for partner access. |
| 17 | **Agoragentic (agoragentic.com)** | https://agoragentic.com · API https://agoragentic.com/api | Marketplace where AI agents sell to each other. 97% payout, Base L2 USDC. One-call registration (`POST /api/quickstart`), free first listing slot, $1 refundable sybil bond. 997 agents, 68 public services. | 🟡 **REGISTERED (Aug 12)** — agent `32e94bca-4911-45ed-a21d-1ae681ba736e` + API key saved `/root/.blockrun/agoragentic-creds`. **⛔ PAID EXECUTION FROZEN** (`platform_custody_frozen`: no x402 challenges, no settlement, no wallet provisioning — read-only). Re-check before listing; when unfrozen, list our DeFi/x402 services. |
| 18 | **Agent Bazaar (agentbazaar.dev)** | https://agentbazaar.dev · docs https://docs.agentbazaar.dev | Permissionless agent commerce on Solana. No SOL, no wallet setup, platform pays gas, 97% keep. ERC-8004 identity + A2A endpoint + email inbox per agent. | 🔴 **BROKEN (Aug 12)** — register endpoint 404s (`/agents/register` returns NOT_FOUND even via official SDK). Experimental near-zero volume (site shows -3 agents, -$0.05 volume). Parked — revisit only if it matures. |
| 19 | **Toku (toku.agency)** | https://toku.agency · docs https://toku.agency/docs | AI agent marketplace — agents register via API, list services priced in real USD, get hired by humans (Stripe) or agents (wallet). 85% payout, Stripe Connect withdrawal. | ✅ **REGISTERED + 2 SERVICES LIVE (Aug 13/15)** — agent `cmsrlcezo0003l704nj9wg0dm` (GenTech Labs, slug gentech-labs). Services: AI DeFi Market Analysis, x402 API Gateway. **Aug 15: profile improved** — webhook + avatar + email set (setup 2/5→4/5). Profile: toku.agency/agents/gentech-labs. | 2026-08-15 |
| 20 | **dealwork.ai** | https://dealwork.ai · skill https://dealwork.ai/skill.md | Hybrid work marketplace where humans AND AI agents hire each other. Escrow-protected, outcome-based. 3% AI-to-AI fee, 10% otherwise. | ✅ **REGISTERED + 2 LISTINGS LIVE (Aug 13/15)** — agent `3166b64e-bb21-47dd-acda-bf0c59c92e63`, API key + HMAC saved, identityKey `gentech-labs-vps-2026`. **Aug 15: created 2 listings** — x402 API Gateway (fixed $0.01), AI DeFi Market Analysis (fixed $0.02). | 2026-08-15 |
| 21 | **APIHub (apihub.io)** | https://apihub.io · llms https://apihub.io/llms.txt | x402 API marketplace for AI agents — discover, pay for, consume APIs with one integration. USDC on Base. MCP + REST. | ✅ **REGISTERED + 7 x402 APIs LIVE (Aug 13)** — agent `85888284-3f6b-4985-bbbe-cca75e2d632e`. Listed: SIE embeddings, x402-bazaar, token_security, market_intelligence, agent_discovery, defi_lp_analytics, wallet_analysis — all verified x402-protected (HTTP 402 → ready). API key `ahk_cx67YH2p...` saved. |
| 22 | **RelAI (relai.fi)** | https://relai.fi · llms https://relai.fi/llms.txt | x402 protocol marketplace for pay-per-call API micropayments. Solana/Base/SKALE/Avalanche/ETH/Polygon USDC. | ✅ **REGISTERED + API CREATED (Aug 13/15)** — service key `sk_live_92544c...` saved. **Aug 15: created API** `GenTech x402 Gateway` (apiId 1786824987416, base, relai facilitator, x402 v2, status pending). | 2026-08-15 |
| 23 | **Apify Store (apify.com)** | https://apify.com/partners/actor-developers | Largest marketplace of web-automation tools for AI. 20,000+ Actors now x402-payable (USDC on Base, June 2026). Sellers publish "Actors" (containerized scrapers), earn per-run. $1.4M paid out last month; many devs earn $3k+. | Discovered 2026-08-14 (income scan). **NEEDS HUMAN** — requires Apify account login + Actor packaging (Docker/containerized scraper, not our x402 gateway model). Pay-per-event/result, 20% commission. Add to Jordan's action list if we want a scraping-actor presence. |
| 24 | **Fetch.ai Agentverse (agentverse.ai)** | https://agentverse.ai · docs https://uagents.fetch.ai | Decentralized agent registry + marketplace (2.7M agents). Agents register on Almanac contract, list services, get paid in FET micro-payments. | Discovered 2026-08-14 (income scan). **NEEDS HUMAN + FUNDING** — requires FET token to register on Almanac (spending money, different protocol from x402/USDC). Not a fit for our USDC rails. Skip unless Jordan wants a FET presence. |
| 25 | **0xWork (0xwork.org)** | https://0xwork.org · API https://api.0xwork.org/manifest.json · CLI `npm i -g @0xwork/cli` | On-chain USDC task marketplace on Base. ERC-8004 identity, USDC escrow (TaskPool.sol), x402 micropayments, XMTP/WebSocket/REST task push. CLI/SDK/scaffold. 559 agents, $8,014 paid out, avg bounty $50, 5% fee (2% for $AXOBOTL holders). | Discovered 2026-08-17 (income scan). **NEEDS FUNDING** — on-chain registration requires 10,000 $AXOBOTL stake (AgentRegistry.register) + task claims stake 10% of bounty in $AXOBOTL. Not autonomous without token funding. Strong fit (code/research/data categories). Add to Jordan's action list. | 2026-08-17 |
| 26 | **OpenTask (opentask.ai)** | https://opentask.ai · docs https://opentask.ai/docs · MCP https://opentask.ai/mcp | Agent-to-agent task marketplace with USDC escrow. Hosted MCP + OAuth (DPoP) + REST/OpenAPI + A2A Agent Cards. 4.5% platform fee. "Autonomous agents can continue without signing in." 15 tasks/1,851 offers/8 contracts in 30d. | Discovered 2026-08-17 (income scan). **NEEDS HUMAN (OAuth approval)** — device-authorization flow requires owner to approve scopes in browser after login. Stage the MCP connection; Jordan approves once. | 2026-08-17 |
| 27 | **ugig.net** | https://ugig.net · skill https://ugig.net/skill.md · CLI `curl -fsSL https://ugig.net/install.sh` | Gig marketplace for AI agents + humans. USDC payouts (usdc_pol/sol/eth), API + CLI, agent-first (`account_type:"agent"`). Free tier, $9/mo Pro. | Discovered 2026-08-17 (income scan). **NEEDS HUMAN (email confirm)** — signup requires email verification before API key creation. Stage the signup script; Jordan confirms email once. | 2026-08-17 |
| 28 | **AgentPact (agentpact.xyz)** | https://agentpact.xyz · api api.agentpact.xyz · mcp mcp.agentpact.xyz/mcp | Open agent-to-agent marketplace on Base. Agents publish offers, claim needs, settle USDC escrow on-chain. MCP + REST + npm `@agentpact/sdk`. | **✅ REGISTERED + API KEY (Aug 17)** — `POST /api/auth/register {agentId, name}` with our existing agent UUID `9fed6922-48d0-4ed6-975a-c828bdf02446` returned apiKey `b3c5a531...c57d55` (saved). Live offers verified via GET. Offer-posting needs `descriptionMd` + `category` fields. Free tier, no wallet required to start. Autonomously actioned. | 2026-08-17 |
| 29 | **the402.dev (x402 endpoint directory)** | https://the402.dev · submit https://the402.dev/submit · api https://api.the402.dev | Auto-indexed directory of 13,938 x402 endpoints (each answers with a payment challenge, price, network). Sellers submit a URL, verified by real HTTP request before listing. | ✅ **OUR ENDPOINT LISTED (Aug 17)** — `https://api.gentechlabs.net/v1/market` auto-listed after `/submit` (verified in `/api/listings?q=gentechlabs`, total:1). 13,938 endpoints listed. Fully autonomous — submit any paid endpoint URL. | 2026-08-17 |
| 30 | **Agent Hansa (agenthansa.com)** | https://www.agenthansa.com · llms-full https://www.agenthansa.com/llms-full.txt · MCP `npx agent-hansa-mcp` | Quest-based agent marketplace (A2A task mesh). Agents register via one POST, browse quests, earn USDC. CLI + MCP. | 🔭 EXPLORED (Aug 17) — `POST /api/agents/register` returns `challenge_required` (solvable math CAPTCHA: answer then `/api/agents/register/verify`). **Zero-sum payout model** (~70% to winning alliance, 25% to 1st) — many submitters earn nothing. Autonomous registration possible; low priority (competitive, not work-for-pay). | 2026-08-17 |
| 31 | **Clustly (clustly.ai)** | https://clustly.ai · docs https://www.clustly.ai/docs · llms.txt https://clustly.ai/llms.txt | Task marketplace on Solana (Base L2 supported). Single-POST agent registration, browse/claim/submit tasks, USDC escrow, 4% fee, no KYC. ~71 agents. | 🔭 EXPLORED (Aug 17) — **documented register endpoint returns Next.js shell (404/HTML), not the API** — the real endpoint may be on a different host or the docs are stale. Needs verification before committing; per docs fully autonomous if the real endpoint is found. Add to verify list. | 2026-08-17 |
| 32 | **Polygon Agentic Services (agentic-services.polygon.technology)** | https://agentic-services.polygon.technology · docs https://docs.polygon.technology/payment-services/agentic-payments/agentic-services | Official Polygon x402 marketplace of paid APIs (search, inference, scraping, automation, comms). Pay-per-call USDC on Polygon (eip155:137). Catalog via `/SKILL.md` + `/api/discover/routes`. | 🔭 EXPLORED (Aug 17) — **seller path = wrap existing endpoint + set price**, hosted by Polygon's resource server (not a self-serve form). Standard x402 v2. Moderate friction. Watchlist. | 2026-08-17 |
| 33 | **Own gateway skill.md (PRIMARY distribution channel)** | https://api.gentechlabs.net/skill.md | Buy-side integration: any agent `set up https://api.gentechlabs.net/skill.md` → discover + pay our 11 x402 services. Mirrors Syra's pattern (api.syraa.fun/skill.md). | 🟢 **LIVE (Aug 20)** — deployed, HTTP 200 text/markdown, verified. This is the demand-side play: agents auto-discover us via skill.md, no directory listing required. | 2026-08-20 |

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

*Last updated: 2026-08-17 (marketplace scanner — added AgentPact #28 REGISTERED, the402.dev #29 LISTED, Agent Hansa #30, Clustly #31, Polygon Agentic Services #32 to watchlist)*

| **Solana Homebase** | https://github.com/Gentech-Labs/solana-homebase | Agentic Treasury orchestrator — Solana homebase (Superteam tranche-2 MVP) | 🟢 PUBLIC + LIVE (Aug 5) | 2026-08-05 |
