---
date: 2026-08-10
status: active
last-updated: 2026-08-10 00:15 UTC (EOD Aug 9 ET sweep)
---

# 🧠 Considerations — Open Decisions

> Decision points requiring Jordan's input. Updated from brain snapshot context.

## 🚨 Urgent — DEADLINES APPROACHING

- [ ] 🚨 **Algorand First-Mover Play (Aug 6)** — **✅ COMPOSITE ENTRY SHIPPED (Aug 7).** Context-weight "Recently Done" confirms the Algorand Global x402 Challenge — Composite Entry ($100K + 500K ALGO) is shipped. **Jordan: (1) provide Algorand wallet address so X402_PAYTO_ALGORAND goes live (zero code change), (2) confirm late-leaderboard eligibility or mark dead** (original deadline Jul 31 passed, no registration on file).
- [ ] 🚨 **Keeperhub Agents Onchain #80** — **JORDAN CONFIRMED GO.** **✅ PROOF TRANSFER COMPLETE Aug 8:** Real 0.01 USDC on-chain transfer from KeeperHub wallet to Treasury CDP (TX 0x88fe6c9a...b1df, Base, block 49682145, success). Wallet funded. **REMAINING: film demo video + assemble GitHub submission (README, video, live tx link). Deadline Aug 13.**
- [ ] 🚨 **Algorand Global x402 Challenge #82** — **⚠️ DEADLINE PASSED Jul 31.** $100K + 500K ALGO. No record of registration on file. **Jordan: confirm if registered / still eligible for late leaderboard, or mark dead.** *(Now tied to the Algorand First-Mover Play above.)*
- [x] 🚨 **Arc Programmable Money Hackathon** — **⚠️ DEADLINE TODAY Aug 9 — ✅ SHIPPED.** ArcAgentWallet.sol deployed on testnet, 57/57 tests pass, repo public. **BUILD COMPLETE + VERIFIED Aug 8. MARKED SHIPPED by labs Aug 9.** → Move to Recently Resolved after midnight.
- [ ] 🚨 **AI Factory Hackathon #79** — **⚠️ DEADLINE TOMORROW Aug 10.** lablab.ai × NativelyAI. **MARKED SHIPPED by labs Aug 9.** Jordan: confirm submission status.

## 🔴 High Priority

- [ ] **Super Arcade Tennis #73 production deploy** — Code done and live on dev at arcade.gentechlabs.net. **Jordan: (a) deploy production build, (b) wire crypto payments?**
- [ ] **FrameForge #71** — AI Storyboard Service (previs pipeline). Spec at 09-Green Room/specs/. **Jordan: direction decision?** (Proven on KAGE film — ready to productize.)
- [ ] **Open Generative AI #77** — Self-host AI media studio (400+ models). **Jordan: go/no-go?**

## 🟡 Medium Priority

- [x] **Voice Stack: LiveKit vs Pipecat** — ✅ GO (Jordan Aug 5). Evaluate LiveKit Agents. — LiveKit Agents (12.4k⭐, Apache-2.0, realtime voice AI framework) is a potential alternative/complement to our current **Pipecat 1.5.0** + custom `pipecat-x402-processor`. LiveKit strengths: native MCP support, self-hostable full stack (LiveKit server = widely-used WebRTC media server), telephony/SIP, semantic turn detection, built-in test/judge framework. We're already invested in Pipecat (voice-agent-config + speech-engine skills, Jocelyn pipeline, x402 processor). **Jordan: evaluate LiveKit Agents as the voice layer for agent deployments, or stay on Pipecat?** Source: github.com/livekit/agents, Aug 4.

- [ ] **Narrative Rotation cron — CMC key not loaded in pre-run** — The weekly `narrative-rotation.py` pre-run hit HTTP 401 on every CoinMarketCap fetch (wrote all-zero JSON: BTC $0.00, all narratives "Cooling" score +0.0). Root cause: the inline pre-run step doesn't read `/root/.hermes/scripts/cmc_config.json` (which holds a working `coinmarketcap_api_key`). The 2026-08-02 run was rebuilt manually from the CMC Pro endpoint and pushed. **Jordan: confirm the cron pre-run is fixed to load the CMC key (or switch to CoinGecko free API) so next week's run is real, not zeros.**
- [x] **Syra Marketplace #76** — ✅ GO (Jordan Aug 5). Register x402 services on syraa.fun. — Register x402 services on syraa.fun. Easy win. **Jordan: go/no-go?**
- [x] **Kite AI (#78)** — ✅ RESOLVED (Aug 5): Jordan confirmed. Kite **Agent Passport** integration was **already done** (`10-Labs/kite-passport-hermes` — Hermes skill + GenTech Shop services in Kite catalog + Q402 receipts). The **Kite AI Global Hackathon 2026** (the queue item) **already concluded** — finale aired, winners announced. No pending entry. Removed from active consideration.
- [ ] **AI Factory Hackathon #79** — lablab.ai × NativelyAI, Aug 3-10. **Jordan: register?**
- [x] **GenTech Academy #81** — ✅ GO (Jordan Aug 5). — Initial repo live at `ProtoJay4789/gentech-academy`. Module 1 (AI on Grid) + Module 2 (Visual Pipeline) shipped. Module 3 (AI + 3D Engines / Kimi K3 content creation) next. **Jordan: direction — Blender MCP workflow or Kimi K3 frame critic loop?**
- [ ] **Kimi K3 Content Pipeline #82** — Frame critic + prompt engineer loop for Seedance. Test when wallet funded. Kimi K3 available via BlockRun ($3/$15 per M tokens, 1M context, vision). **Jordan: fund wallet → test frame consistency feedback loop.**
- [ ] **CockroachDB × AWS — Agentic Memory #83** — $8.75K, Aug 18 deadline. Persistent memory + MCP Server. **Jordan: register?**

- [ ] **Bug Bounties Comeback?** — We stopped because AI agents couldn't produce solid PoCs ("proof of LOC"). open·kritt (Kritt-ai, Blockian team) now handles that: scan agents run as root in disposable containers (compile/run tests/build exploits) and post-scripts emit PoCs via `_reserved_poc` + reports. **Jordan: test on our own repos first (build-queue #34), then decide if we point it at Immunefi targets for bounty revenue.**

- [ ] **ego-lite browser — WATCH (Aug 10)** — Shared-logged-in-browser for agents (citrolabs, MIT, 9.5k★). Purpose-built for the #20 auto-apply gap (login-walled Lever/Greenhouse/Workday + form submission). **BUT macOS-only today; our VPS is Linux → can't run yet.** Windows/Linux on roadmap. **Action when it ships cross-platform:** re-evaluate as (1) AI Job Search auto-apply completion, (2) login-gated marketplace/dashboard unblocker, (3) GTA layer-2 authorized-proxy enabler (browser surface). Full eval in `09-Green Room/ideas.md` (Aug 10). **Jordan: watch for cross-platform release; don't block #20 on it.**

## 🎓 Learning Track — AWS + Cyfrin Updraft (Aug 3)

Jordan's commitment (more free time this week due to reduced work hours). Work BOTH in parallel alongside job apps + hackathons. **⚠️ Check-in was due Sunday (Aug 9) — status unknown.**

- [ ] **AWS Solutions Architect Associate (SAA-C03)** — Amazon subsidizes the exam. 2-3 week focused sprint. Credential value for the "cloud engineering" half. Not a daily-tooling shift (we run VPS/nginx/Cloudflare) — a resume + credential unlock.
- [ ] **Cyfrin Updraft — Solidity/security-audit track** (Patrick Collins). Deep multi-week curriculum. Highest differentiation value — unlocks paid smart-contract audits ($1K-5K/audit) via the x402 gateway. Complements our `solidity-security`, `audit-fix-verify`, `solana-anchor-development` skills.

**Sequencing note:** Finish active hackathons first (Arc Aug 9, DataHub Aug 10, Keeperhub Aug 13, CockroachDB Aug 18) → AWS cert → Cyfrin as the differentiator. Both now on the website roadmap (gentechlabs.net → Phase 5 — Credential Depth).

## 🎮 Gaming Lane — Gears of War E-Day (Aug 3)

Jordan's decision on the Gears E:D beta: **NOT pre-ordering for beta access.** Early Access (Aug 6) is Horde-only — not interested. Will wait for the **Open Beta (Aug 13–17, Versus 4v4 + Horde Siege, everyone).** This is a marketing-noise-vs-value case: pre-order perk was weak (paying for 3 days of a mode he doesn't play).

- [ ] **Action:** Set up Gears E:D **price-watch** (standard edition deal) + **release/open-beta tracker** in shop/hub — catch the discount and the Aug 13–17 window.
- [ ] **Opportunity:** Gaming is the next service lane — package price-watch w/ auto-buy (x402), pre-order/access advisor, release radar (game-intelligence skill exists), meta/loadout intel, and gaming-commerce middleware (agent buying/selling keys+DLC+cosmetics through our x402 rail as fee-earning middleman).

### 🎴 Agent Prepaid Card / Virtual Card — Software Layer First (Aug 3)

**Jordan decision:** Build the **software layer** of the agent "virtual card" first — a funded agent wallet with delegated spending authority + caps, that transacts across rails without re-approving each payment. **NOT** physical plastic / network BIN / fiat settlement yet (that needs a licensed card issuer + KYC/AML partner — a wait item). Maybe a card-issuance partner like Santander/Baanx-style crypto card later. The software capability is already ~80% in our stack:
- **Q402 Agent Wallet** = the prepaid balance (USDC/USDT, 12 chains, per-tx + daily caps) ✅ live
- **EIP-7702 delegation + Zyfai session keys** = standing spend authority within caps ✅ live
- **Payment router (x402 / Q402 escrow / platform SDK)** = rail-agnostic "card" — spec'd in q402-escrow-integration ✅

**Build target (first shippable piece):** gaming price-watch with **auto-buy** that settles itself from a funded agent wallet — proves the software "card" model end-to-end.

- [ ] **Tier 1:** Wire `deal_tracker.py` CheapShark engine into live deal-tracker API (currently `v1/deals` returns `[]`) + add `v1/games/price-watch` endpoint. Gears E:D tracker rides on this.
- [ ] **Tier 2:** `v1/games/release-radar` + `v1/games/preorder-advisor` (the judgment service we did manually for Gears — differentiator).
- [ ] **Software "card":** hook price-watch auto-buy to funded Q402 agent wallet (delegated authority + caps) → settles itself on target price.
- [ ] **Wait item:** physical card / network BIN / fiat settlement — needs card-issuer partner. Partner when traction exists.

### 🔍 API Health Audit (Aug 3) — 3 live APIs return placeholders = $0 revenue

**Jordan's instinct was right:** empty/stub APIs can't earn. Full audit of all running services found:

**✅ HEALTHY (real data):**
- **deal-tracker-api** (8080) — v1/deals was a STUB returning `[]`; **NOW FIXED** with real CheapShark engine + 4 new gaming endpoints (price-watch, release-radar, preorder-advisor). 6 tests passing. Live.
- **rugcheck-api** (8088) — real Solana risk scoring, returns proper 402 payment challenge. Healthy.
- **x402 gateway backends** (agent_discovery, defi_lp_analytics, wallet_analysis, nft_search, treasury_defender, lineage_guard) — all call real external APIs (8004scan, DexScreener, Solana RPC, Magic Eden, Base RPC), return proper 402 challenges. Healthy.

**❌ PLACEHOLDER / DEAD (return hardcoded zeros — nobody would pay):**
- **crypto-price-api** (8082) — `/v1/price/{symbol}` returns `price:0.0, source:placeholder`
- **gas-price-api** (8084) — `/v1/gas` returns all-zero `{ethereum:0, base:0, polygon:0}`
- **token-security-api** (8086) — `/v1/score/{mint}` returns `score:0, level:unknown`

**⚠️ QUESTION:** agent-search-api `/root/agent-search-api/main.py` has real /search endpoints but port 8091 currently runs `x402-backend@agent_discovery` instead — need to verify its own systemd service exists.

**Action:** Logged as **build queue #34** (high priority, easy). Fix = wire real data (crypto → CoinGecko fallback, gas → Etherscan/live RPC, token-security → reuse working Rugcheck engine). **Jordan: confirm this goes on the build list.**

---

**✅ FIXED (Aug 3) — all 3 placeholder APIs now return live data:**
- **crypto-price-api** (8082) — CMC→CoinGecko fallback chain. Live: BTC $63.4K, ETH $1.86K. Test `test_crypto_api.py` (3 pass).
- **gas-price-api** (8084) — live RPC (eth/base) + Polygon gas station. Live: eth 0.09, base 0.01, polygon 405 gwei.
- **token-security-api** (8086) — now a thin proxy to the working Rugcheck engine (port 8088), returns proper 402 payment challenge. Test `test_token_security_api.py` (2 pass).

**✅ Pushed to kit + academy (Aug 3):**
- **agent kit:** `services/api-audit.py` — reusable API health auditor + documented in `services/README.md`. Committed to `Gentech-Labs/genTech-agent-kit` (verified via GitHub API).
- **academy:** Module 5 "Auditing Your APIs" — placeholder trap, audit recipe, reuse-don't-duplicate pattern, real incident. Committed to `ProtoJay4789/gentech-academy` (verified via GitHub API).

**⚠️ Agent-search-api still orphaned:** no systemd service; nginx routes `search.gentechlabs.net` → 8091 but that port runs the x402 agent_discovery backend. The standalone search API (real /search endpoints, EXA/GROK/SURF keys) isn't running. **Needs a port/service decision — flagged for Jordan.**

## ✅ Recently Resolved

- **Web tools down** — RESOLVED. Agent Reach is the default web backend. Firecrawl no longer needed.
- **OKX AI Genesis Hackathon #72** — Deadline passed Jul 27. No registration received.
- **Keeperhub Agents Onchain #80** — ✅ GO confirmed. PROOF TRANSFER COMPLETE Aug 8. Remaining: demo video + README. Deadline Aug 13.
- **Celo Agentic Payments Hackathon #69** — Researched (Jul 24). Ready to execute on go-ahead.
- **MengTo Fork #75** — Shipped (Jul 25).
- **x402 Gateway v7.0.0** — Deployed and verified.
- **CLARITY Act Compliance** — Badges live on all repos.
- **Stale PRs** — All 10 PRs confirmed still open (no action needed from us).

## 🆕 DeepSeek V4-Flash Official API — LIVE in public beta (Jul 31, 2026)

**Source:** [DeepSeek announcement tweet](https://x.com/i/status/2083084415157022911) — 2.46M views, 16K likes. Docs: api-docs.deepseek.com

### What changed
- Official API live at api.deepseek.com, native **Responses API** support, fully adapted for **Codex**
- Agent capabilities massively upgraded vs V4-Pro-Preview (Flash-0731 vs Pro-Preview):
  - DeepSWE: **54.4 vs 12.8** (4.2x)
  - Terminal Bench 2.1: **82.7 vs 72.1**
  - Cybergym: **76.7 vs 52.7**
  - Toolathlon-Verified: **70.3 vs 55.9**
  - Agents' Last Exam: **25.2 vs 16.5**
  - AutomationBench: **25.1 vs 12.8**
  - DSBench-FullStack: **68.7 vs 41.8**
  - DSBench-Hard: **59.6 vs 31.1**
- DeepSeek docs now list **Hermes Agent** as an official agent integration (install → setup → select DeepSeek provider)

### Why this matters to us
- We already run on `deepseek/deepseek-v4-flash` (Nous provider) — this is a massive capability jump for the same tier we use daily
- Our DEV tier (develop-and-verify pipeline) is DeepSeek V4 Flash — stronger agentic coding = faster build queue
- **Decision to consider:** switch from Nous provider to direct DeepSeek API (api.deepseek.com, sk- key) for lower cost / official support? Also evaluate Z.AI / Ollama Cloud in the same pass.
- Codex CLI integration now officially supported — our codex delegation path gets a free upgrade

**Status:** ☑️ tracked — **Jordan: evaluate provider switch vs current Nous setup (open question)**

## 🆕 DeepSeek Code — dedicated coding agent (Harness framework) coming

**Source:** [tweet](https://x.com/i/status/2083851157324046649) (Priya @Priyannkaaaa, Aug 2) + corroborated by ChainCatcher ("Insiders: DeepSeek is forming a Harness team") and SCMP ("DeepSeek's Harness team races to recruit talent"). No official DeepSeek repo yet — org still shows infra only (FlashMLA, DeepEP, DeepGEMM, DeepSpec).

### What's known
- DeepSeek building a dedicated AI coding agent **positioned directly against Claude Code and OpenAI Codex**
- Powered by **DeepSeek Harness** — long-running agent workflows with memory + repository awareness (planning, tool use, code execution)
- **V4-Flash's recent benchmarks were already evaluated using DeepSeek Harness** — it's core to their roadmap, not an experiment
- Closed beta expected to begin soon

### Why this matters to us
- We run on DeepSeek V4-Flash daily — a first-party DeepSeek coding agent is the cheapest, most native delegation backend we could add to the fleet (we already have Claude Code / Codex / OpenCode skills)
- DeepSeek Harness (memory + repo awareness + long-running workflows) is the same architecture our self-evolution harness uses — third-party validation of our design
- The benchmark numbers in the V4-Flash section above were produced by this harness — that's the quality ceiling we can expect

**Status:** 🔭 watch — when closed beta opens, evaluate as 4th delegation backend (build-queue #36)

## 💰 Pricing & Subscription Philosophy — Minara Case Study (Aug 3)

**Source:** We installed the Minara "free skill" (Minara-AI/skills) on Aug 3; it turned out to be a **trojan subscription funnel** — free CLI + skill install, then paywalled behind a $20–50/mo plan just to access the API key. Uninstalled. This validates the market AND our differentiation.

### What Minara proves about the market
- People **pay $20–50/mo** for exactly what GenTech builds — a crypto AI CFO: wallet, trading, market analysis, x402. Demand is proven and monetizable.
- Their moat is thin: a CLI + skill wrapping an API. **We ARE the rails** (x402 middleware), not a walled subscription.

### Jordan's pricing stance (verbatim intent)
- ✅ **Open agentic treasury** — happy for people to use it; we make money on **swap fees / per-tx fees** (yield-farming model), NOT subscriptions.
- 🤔 **Only subscriptions we'd honor:** premium **integrations** — e.g. **Narrative Rotation** already built, and a **"bring-your-own news feed"** plug-and-play (connect your favorite news source / bird's-eye-style connectors). These are the legit subscription surface.
- 🎯 **If we ever do a subscription:** $10–15–20 range. NOT $20–50. Jordan explicitly rejected the $20/$50 tier as too high.

### Action items
- [ ] Define the **BYO-news-feed integration** as a concrete paid feature (narrative rotation already exists — productize as the anchor).
- [ ] Revisit GenTech revenue model around **per-tx fees + low-cost integrations**, document as the core monetization thesis (aligns with memory: GenTech = x402 fee-earning middleman).
- [ ] Log Minara as a **competitor reference** in research — their pricing page is a live signal for what the market tolerates.

**📄 Full spec:** `09-Green Room/specs/gentech-subscription-tiers.md` — open core (per-tx) + premium integration tiers ($10–15–20/mo). **Sequencing (Jordan, Aug 3):** build the agentic treasury (GTA) fully first → subscriptions come later. Spec kept as idea bank, not a build target.

## 🚀 GTA — Action Items (Aug 3, for tomorrow)
- [ ] **Robinhood KYC + OAuth** (Jordan) — perp leg for basis arb. One-time in-app.
- [ ] **Fund Coinbase wallet** (Jordan) — moves spot leg from dry-run to real execution.
- [ ] **Composio fork decision** (Jordan + Gentech) — GTA authorized-proxy layer: build on open `ComposioHQ/composio` SDK (their cloud for OAuth tokens, fast) vs self-host auth backend (full custody, the trust moat). Research: `09-Green Room/specs/gta-composio-research.md`.

## 🔗 Related

- [[brain-snapshot-2026-07-28]] — Full context snapshot
- [[context-weight]] — Auto-generated project overview
- [[build_queue.json]] — v52, 30 items
- [x] Bankr API key wired into revenue monitor (bk_usr_...37XZ, saved to profile .env). Bankr wallet EVM 0x99ae... SOL 6mcf... — currently $0 across 9 chains. Distinct from x402 revenue wallet (0x7ebf...). Monitor now reports Bankr portfolio each run.
