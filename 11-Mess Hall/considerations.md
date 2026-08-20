---
date: 2026-08-18
status: active
last-updated: 2026-08-18 20:06 ET
---

# 🧠 Considerations — Open Decisions

> Decision points requiring Jordan's input. Updated from brain snapshot context.

## 🚨 Urgent — DEADLINES + MACRO EVENT

- [x] 🚨 **CPI Release — Wed Aug 12 8:30 AM ET (RELEASED) — ⚠️ REPOSITION BLOCKED** — Treasury CPI War-Room play was staged (regime RANGE_BOUND, RSI 24.1, expected AVAX ±4-7%) but **the Steward wallet was swept empty Aug 11 evening** (~43.72 USDC off to `0xeee3fe6c...`). No LFJ V2.2 position exists on `0x572ABd6461BED2258615E6b99c585Ab7c5d05037` (0 WAVAX, ~0.0006 USDC, 0.2979 AVAX gas). **✅ RESOLVED Aug 13 — Jordan confirmed the sweep was INTENTIONAL**: he tested whether the agentic treasury could send funds back to his Coinbase wallet, it worked (real USDC landed), and he kept the money. No unexpected move, no review needed. Two CPI one-shots (`31432dce0de9`, `e13db42767b0`) recommended paused + position heartbeat re-enabled.
- [ ] 🚨 **Keeperhub Agents Onchain #80** — **⚠️ DEADLINE PASSED Aug 13.** JORDAN CONFIRMED GO. **✅ PROOF TRANSFER COMPLETE Aug 8** (0.01 USDC on-chain, TX 0x88fe6c9a...b1df, Base). **REMAINING was: film demo video + assemble GitHub submission (README, video, live tx link). Verify submission status — if not submitted, mark closed.**
- [x] 🚨 **Build with Gemini XPRIZE #29** — **DROPPED Aug 15 (Jordan decision).** Was Aug 17 deadline. Zero actual Gemini/Vertex code existed (only a build brief); 2 days was "way too tight" for a $2M pool. Jordan chose to unregister and refocus on CockroachDB + Delphi. Marked closed — do not re-flag.
- [ ] 🚨 **CockroachDB × AWS — Agentic Memory #83** — **⚠️ DEADLINE WAS TODAY (Aug 18).** $8.75K, persistent memory + MCP Server (Devpost cockroachdb-ai.devpost.com). **Agent Memory layer BUILT + verified** (shipped 2026-08-14, `10-Labs/cockroachdb-agentic-memory/`, 9/9 tests, live CockroachDB v24.3.4). **REMAINING (Jordan):** register on Devpost, record <3min demo, push public repo. **⚠️ CLOSEST ACTIONABLE — verify submission status now.**
- [ ] ✅ **AI Factory Hackathon #79** — **DEADLINE PASSED Aug 10.** lablab.ai × NativelyAI. **MARKED SHIPPED by labs Aug 9.** Jordan: confirm submission status (if not submitted, this is done).
- [ ] ✅ **Build with DataHub** — **DEADLINE PASSED Aug 10.** Needs submission confirm. If not submitted, mark closed.
- [ ] ✅ **Arc Programmable Money Hackathon** — **DEADLINE PASSED Aug 9.** SHIPPED + verified (ArcAgentWallet.sol, 57/57 tests). Moved to Recently Resolved.
- [ ] 🔴 **Superteam USA — Remote Community Membership** — Applied. **Jordan confirmed Aug 12: applied for second triage, now waiting on their decision.** (Superteam Earn agent `gentech-labs-x402` registered Jul 23; us.superteam.fun/join remote membership.) Status: PENDING second triage.
- [ ] 🟡 **Solana Foundation USA Grant** — Applied Aug 5 (~$8.2k avg/up to $10k USDG). **Aug 12 check: site still shows application, no approval/rejection email, no status change** — likely large applicant pool. STILL PENDING. Do not reallocate treasury around unconfirmed grant. **Re-check ~Aug 19 (1 day).** Tracked: Treasury/2026-08-05-solana-foundation-usa-grant.md
- [x] 🚨 **Mastercard Innovation Challenge** — **✅ REGISTERED Aug 18** (luma.com/kyz978xv, free) + build kicked off (13/13 tests, live fraud stack). Submit Aug 31. Credential > prize framing (W33 review, Aug 16). `10-Labs/mastercard-challenge/` scaffolded (red_team 7 attack types + blue_team governance + live fraud stack `live_stack.py`; ERC-8004 identity + credit 76.7/HIGH surfaced). Labs: extend realism, session-aware eval, polish UI, demo video by Aug 31.
- [ ] 🚨 **Algorand First-Mover Play (Aug 6)** — **✅ COMPOSITE ENTRY SHIPPED (Aug 7).** **Jordan: (1) provide Algorand wallet address so X402_PAYTO_ALGORAND goes live, (2) confirm late-leaderboard eligibility or mark dead.**
- [ ] 🚨 **Algorand Global x402 Challenge #82** — **⚠️ DEADLINE PASSED Jul 31.** $100K + 500K ALGO. **Jordan: confirm if registered / late-leaderboard eligible, or mark dead.**

## 🟢 AgentLux — LIVE, First-Hire Guarantee armed (Aug 12)

- **Agent registered** `9fed6922-48d0-4ed6-975a-c828bdf02446` (wallet 0x7ebf…96a), provider profile public.
- **DeFi LP analysis + token security listing LIVE** (id 6581ec2d-7041-4d86-8571-19548b83bec6, $15, public).
- **First-Hire Guarantee armed** — platform funds one escrowed hire within 24h, paid in USDC. Fully autonomous (free challenge-sign auth, no human key).
- **Watch:** cron `1f7b73c08eb2` (every 6h) checks for the hire request; on arrival we accept → deliver structured JSON → get paid.
- **Profile:** https://agentlux.ai/agents/0x7ebff188f2Eba16518C02864589b1403a5d1296a

## 🟡 BountyBook — Parked (Aug 12)

- [ ] **BountyBook payout rail** — Reproduced code_test verifier crash (`required_fields.length` vs `required_files` → `undefined.length`) on the exact documented inline payload, twice. Lifetime code_test settlements 0/32. Non-code verified jobs show `payout_status=failed` + no tx; treasury `0x1bc6…72f2b` zero lifetime USDC outflows on Base — **platform has never paid anyone.** Agent wallet + claim/submit pipeline work (proven), but payout is broken operator-side. **Re-check ~Aug 19:** if verified jobs show `payout_tx_hash`, it becomes our best autonomous rail. Diag: `09-Green Room/bountybook-full-diagnosis-2026-08-12.md`.
- [ ] **BountyBook bug report (Discord/X)** — Report drafted in diag file. No public GitHub. Contact: Discord `discord.gg/BXKTe44Y`, X `@_ptonik`. Jordan: paste report OR let me hand you the text. Operator already has a $150 fix offer open (job 8a7bd232, claimed by another agent) — they know.

## 🔴 High Priority

- [ ] 🔴 **🔑 AVAX KEY ROTATION (COMPROMISE EVENT)** — Jordan's **personal AVAX private key was pasted in chat** (derives to Main `0x7ebf...96a`, ~0.099 AVAX, nonce 5363). Stored locked-down at `/root/.blockrun/jordan-personal-avax-key` (600), but chat history is synced so local storage does NOT make it safe. **Jordan: rotate the key / move funds off that address.** Do not treat as handled because it's on disk.
- [ ] 🔴 **Build Queue Audit — backfill completion metadata (Pixel, Aug 17)** — Jordan flagged queue keeps inflating (50→60→70) despite shipping. Audit: 57 total (37 shipped, 15 pending, 3 cancelled, 2 blocked). **7 shipped items have NO `shipped_date`** (#20 FrameForge, #29 awesome-selfhosted, #30 Hippocratic AI, #34 Yield.xyz, #35 Paperclip Control Plane, #36 API Audit Fix, #53 GenTech Hub PWA). **36 of 37 shipped items have NO `shipped_note`** (only #34 has one). **2 items lack a `group` field** (#36 API Audit Fix, #49 NOT THE GHOST). **Pending (15) all greenlit Aug 3, aging silently** — no age/priority signal. **Recommended:** (1) backfill shipped-without-date/note items with completion metadata OR downgrade confidence; (2) add age/priority to pending items; (3) confirm #36 and #49's group. Full audit: `01-HANDOFFS/entertainment-to-gentech/2026-08-17-build-queue-audit.md`.
- [ ] **Super Arcade Tennis #73 production deploy** — **Main Menu [P0] SHIPPED (Aug 17)** (title/mode/instructions). Code done and live on dev at arcade.gentechlabs.net. **Jordan: (a) deploy production build, (b) wire crypto payments?**
- [ ] **FrameForge #71** — AI Storyboard Service (previs pipeline). Spec at 09-Green Room/specs/. **Jordan: direction decision?** (Proven on KAGE film — ready to productize.)
- [ ] **Open Generative AI #77** — Self-host AI media studio (400+ models). **Jordan: go/no-go?**
- [ ] **Make other GenTech surfaces PWAs** (Treasury decision Aug 11) — Jordan: "make the other GenTech surfaces PWAs, tie to the website." Steward PWA is the proof-of-concept. **No build until scoped in HQ/CLI.**
- [ ] **GTA real-execution rails** — GTA scan logged **ENTER AVAX** (short Hyperliquid / buy Coinbase) but NOT executable: AVAX spot leg NOT in `gta_coinbase_leg.py` SUPPORTED map (CDP is Base/Ethereum-only); `GTA_HL_KEY` unset (perp leg detection-only). ONDO 24.36 bps best live but perp leg lacks HL key. **Jordan: approve wiring AVAX/ONDO rails + set HL key.** No funds moved — standing-autonomy guardrail honored.

## 🟡 Medium Priority

- [x] **Voice Stack: LiveKit vs Pipecat** — ✅ GO (Jordan Aug 5). Evaluate LiveKit Agents. — LiveKit Agents (12.4k⭐, Apache-2.0, realtime voice AI framework) is a potential alternative/complement to our current **Pipecat 1.5.0** + custom `pipecat-x402-processor`. LiveKit strengths: native MCP support, self-hostable full stack (LiveKit server = widely-used WebRTC media server), telephony/SIP, semantic turn detection, built-in test/judge framework. We're already invested in Pipecat (voice-agent-config + speech-engine skills, Jocelyn pipeline, x402 processor). **Jordan: evaluate LiveKit Agents as the voice layer for agent deployments, or stay on Pipecat?** Source: github.com/livekit/agents, Aug 4.

- [ ] **Narrative Rotation cron — CMC key not loaded in pre-run** — The weekly `narrative-rotation.py` pre-run hit HTTP 401 on every CoinMarketCap fetch (wrote all-zero JSON). Root cause: the inline pre-run step doesn't read `/root/.hermes/scripts/cmc_config.json` (holds working `coinmarketcap_api_key`). The 2026-08-02 run was rebuilt manually from CMC Pro endpoint. **Jordan: confirm the cron pre-run is fixed to load the CMC key (or switch to CoinGecko free API) so next week's run is real, not zeros.**
- [x] **Syra Marketplace #76** — ✅ GO (Jordan Aug 5). Register x402 services on syraa.fun. — Register x402 services on syraa.fun. Easy win. **Jordan: go/no-go?**
- [x] **Kite AI (#78)** — ✅ RESOLVED (Aug 5): Jordan confirmed. Kite **Agent Passport** integration was **already done** (`10-Labs/kite-passport-hermes` — Hermes skill + GenTech Shop services in Kite catalog + Q402 receipts). The **Kite AI Global Hackathon 2026** (the queue item) **already concluded** — finale aired, winners announced. No pending entry. Removed from active consideration.
- [x] **AI Factory Hackathon #79** — ✅ DEADLINE PASSED Aug 10, shipped. Moved to urgent section.
- [x] **GenTech Academy #81** — ✅ GO (Jordan Aug 5). — Initial repo live at `ProtoJay4789/gentech-academy`. Module 1 (AI on Grid) + Module 2 (Visual Pipeline) shipped. Module 3 (AI + 3D Engines / Kimi K3 content creation) next. **Jordan: direction — Blender MCP workflow or Kimi K3 frame critic loop?**
- [ ] **Kimi K3 Content Pipeline #82** — Frame critic + prompt engineer loop for Seedance. Kimi K3 available via BlockRun ($3/$15 per M tokens, 1M context, vision). **Treasury model confirmed (Aug 11): Kimi 2.7 (`kimi-k2.7-code`) + Kimi K3 in ollama-cloud model list. Jordan: fund wallet → test frame consistency feedback loop.** *(Wallet is funded — Steward active on real funds.)*
- [ ] **CockroachDB × AWS — Agentic Memory #83** — $8.75K, Aug 18 deadline. Persistent memory + MCP Server. **Jordan: register?**

- [ ] **Bug Bounties Comeback?** — We stopped because AI agents couldn't produce solid PoCs ("proof of LOC"). open·kritt (Kritt-ai, Blockian team) now handles that: scan agents run as root in disposable containers (compile/run tests/build exploits) and post-scripts emit PoCs via `_reserved_poc` + reports. **Jordan: test on our own repos first (build-queue #34), then decide if we point it at Immunefi targets for bounty revenue.**

## 🧭 CURRENT STRATEGY — All Groups (Aug 15/16, 2026)

> **Where we're coming from.** Jordan's confirmed operating strategy. Every group should align to this.

### Core: GenTech is the edge, traditional signals unlock the door
- **GenTech** (agent fleet, x402 rail, hackathon builds) = our differentiator — proves shipping velocity, AI orchestration, real deployed infrastructure.
- **Traditional credentials** (AWS SAA-C03 + Cyfrin Updraft/Solidity) = the *gatekeeper signals* the traditional job market still requires. We use GenTech to speed up learning, but the certs make us "look right" to employers stuck on the old way.
- **Framing for interviews/apps:** honest on wins vs submissions — we have **hackathon experience + shipped builds, NO wins yet.** Present velocity through completed builds, working code, live deployments. Never overclaim.

### Dual-track career plan (Jordan decision Aug 15)
- **PRIMARY:** Land a **remote role** we qualify for (AI agent power-user, Learning Trainer L3, agent/cloud roles), working in the background.
- **Amazon:** stay normal **full-time (blue badge)**, NOT PA promotion (not a people-person; PA = golden handcuffs + memorizing coworkers). Amazon = income + blue badge + **AWS cert benefit** while searching. Easy transfer, peace of mind.
- **AWS cert is the one asset serving BOTH tracks** — keep as north star.

### DoorDash as flexible side income
- NOT a new W-2 job (no schedule lock-in, won't sink vacation). Fills **open days** when no hackathon/build is in flight. Funds: trips (Cebu 2wk + Sosua), agentic treasury, debt catch-up.

### ⏫ PRIORITY SHIFT (NEW — Jordan Aug 15)
**After the current hackathons wrap, we SLOW DOWN on hackathons and SPEED UP on school (AWS cert → Cyfrin Updraft).** School becomes the new primary priority. We'll still participate in hackathons, but at a slower cadence.

### X/developer account dual-posting (NEW)
- Goal: add our ex-developer account so we can **post autonomously on BOTH accounts** (main + developer).

## 🎓 Learning Track — AWS + Cyfrin Updraft (Aug 3, updated Aug 15)

Jordan's commitment (more free time this week due to reduced work hours). Work BOTH in parallel alongside job apps + hackathons. **Check in Sunday (Aug 9) on progress for both.**

- [ ] **AWS Solutions Architect Associate (SAA-C03)** — Amazon subsidizes the exam. 2-3 week focused sprint. Credential value for the "cloud engineering" half. Not a daily-tooling shift (we run VPS/nginx/Cloudflare) — a resume + credential unlock.
- [ ] **Cyfrin Updraft — Solidity/security-audit track** (Patrick Collins). Deep multi-week curriculum. Highest differentiation value — unlocks paid smart-contract audits ($1K-5K/audit) via the x402 gateway. Complements our `solidity-security`, `audit-fix-verify`, `solana-anchor-development` skills.

**Sequencing note:** Finish active hackathons first (Arc Aug 9, DataHub Aug 10, Keeperhub Aug 13, CockroachDB Aug 18) → AWS cert → Cyfrin as the differentiator. Both now on the website roadmap (gentechlabs.net → Phase 5 — Credential Depth).

### 🌀 AGENT TWIST — Standing Learning Principle (Jordan, Aug 15/16)
**"Always attach an agent twist."** Whenever learning anything (AWS, Cyfrin/Solidity, OpenClaw-era agent tooling), always ask:
- How can this help GenTech?
- How could an agent use/automate this?
- How does this fit our agent fleet / x402 rail / agent economy?
Cyfrin/curriculum content is often dated (pre-agent-era); we always modernize it through the agent lens. This keeps learning directly feeding the build, not just checking boxes. **Apply to ALL future learning (AWS cert, Cyfrin, anything).**

## 🎮 Gaming Lane — Gears of War E-Day (Aug 3)

Jordan's decision on the Gears E:D beta: **NOT pre-ordering for beta access.** Early Access (Aug 6) is Horde-only — not interested. **Open Beta (Aug 13–17, Versus 4v4 + Horde Siege, everyone) — ⚠️ ENDS TODAY (Aug 17).** This is a marketing-noise-vs-value case: pre-order perk was weak (paying for 3 days of a mode he doesn't play).

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

## 🆕 Fleet Reorganization (Aug 16)

- **Gizmo** (Labs) — SOUL updated to proper Labs build specialist (was a gentech clone). Owns build queue execution, verification, honest blockers. Name kept (Jordan's choice).
- **Pixel** (Entertainment) — NEW worker live (`@Enterthebrainsbot`), owns Entertainment + 5 cron jobs (GenTech Shop sweeps, game intel, POE2, social engine). Gentech's copies paused — no double-fire.
- **yoyo, desmond, dmob** — permanently deleted (orphaned identities).
- **Gentech** — now consolidates to HQ for strategy; workers handle their groups.
- **The Steward** (gentech-treasury) — SOUL already current, no changes. Fleet model others catch up to.

## 🆕 Harness → Shop-Intel Model (Revenue Model, Aug 16)

**Jordan (Entertainment group, Aug 16):** "shift it over to the labs group. We really got to work on this thing. This is also another revenue model for us."

- **Core insight:** The harness already routes models to tasks (Evolution → DeepSeek V4 Flash, Critic → Kimi K2.7, Verifier → DeepSeek). That's the exact machinery a fine-tune needs. The harness is the **factory**; the shop-intel model is the **product**.
- **Physical Media Scarcity Tracker — SHIPPED + verified live (Aug 16)** in `10-Labs/deal-tracker-api/api/physical_media.py`. 5 endpoints live, 15/15 tests. Curated catalog: 4K UHD, steelbooks, vinyl, boutique (Criterion OOP, PS5 post-2028, Interstellar steelbook, Taylor Swift collector). Scarcity score 0-100 with bands.
- **Revenue model:** paid x402 shop-intel API, scarcity alerts as a service, Model Strength Score marketplace listing.
- **Handed to Labs** to brainstorm + scope the pipeline, decide base model (DeepSeek R1 32B vs Kimi), define eval gate, add to build queue. Human-gated: Jordan funds BlockRun wallet (~$2.50-60).

## 🆕 Agentic Treasury = Avalanche L1 (Jordan, Aug 15)

- Locked L1 product thesis; scoped C-Chain play + Retro9000 agent-run validator idea; whitepaper v1.0 drafted + published.
- **Dinari dShares tokenized equity rail GREENLIT (Aug 15):** 724 US stocks/ETFs on Dinari Financial Network (Avalanche L1) — on-thesis for Agentic Treasury equity leg. **Jordan: Partners signup + sandbox API key + KYC; Labs: scaffold `dinari-rail`.**

## 🆕 OpenDexter Dexter Facilitator Rail (#41, Aug 16)

- **Root cause found:** gateway settles Base via CDP, but OpenDexter only auto-catalogs gateways settling through Dexter facilitator (`x402.dexter.cash`). CDP/GoPlausible/PayAI settlements do NOT trigger cataloging.
- **Code shipped:** `verify_proof_via_dexter()` + routing (Base proofs → Dexter when `X402_USE_DEXTER=1`). 8/8 tests, full suite 45/45.
- **OPS REMAINING (Labs):** set `X402_USE_DEXTER=1`, trigger real Base settlement, re-check `x402_search` ~24h.

## 🆕 Arcade P0 Fixes SHIPPED (Aug 16)

- **3D Lobby deployed + wired to real games** — `arcade.gentechlabs.net/lobby/`. Replaced placeholder GAMES with 4 real cabinets (Super Arcade Tennis, Agent Warfare, King's Gambit, Visual Kei Tap). Removed fictional ARC economy (honest — no fake balances).
- **Super Arcade Tennis** — mobile touch (virtual joystick + SWING button) + pause.
- **Visual Kei Tap** — pause (Escape/P + RESUME button).
- **Remaining:** Tennis main menu (last P0), King's Gambit mobile verify, Agent Warfare mobile perf (12MB bundle — code-split).

## 🛠️ Hermes / Skills Status (W33 review, Aug 16)

- **Local:** Hermes v0.20.1. **Upstream:** v0.20.2 (released 2026.8.16). **774 commits behind**, 7 security/hardening-related.
- **18 hub skills have updates.** Unavailable upstream: `base`, `social-content`, `youtube-full`, `hermes-buzz-shared-profile`, `cufolio`.
- **Recommendation:** Do NOT auto-apply. **Jordan: run `hermes update` in a controlled window (restart required), then `hermes skills check` + apply.** Review breaking changes before production.

## ✅ Recently Resolved

- **ClawWork Employee Squad infra SHIPPED (#3, Aug 18)** — provider-fallback router live on `127.0.0.1:8011` (Ollama Cloud→OpenCode Go), verified chat round-trip vs deepseek-v4-flash. GDPVal pipeline loads 220 tasks ($82–$5004, avg $259). NEXT: run one GDPVal task end-to-end (labs) to prove a real deliverable + settlement.
- **Dinari dShares rail SCAFFOLDED (Aug 18)** — `agent-kit-self-tracking/dinari-rail/`, self-test passes. Jordan: Partners signup + sandbox API key + KYC to validate.
- **Fraud/Security Stack AUDIT + COMPLIANCE (Aug 18)** — rugcheck v2.1.0 confirmed AHEAD of vault source; x402-compliance-scanner fixed to v2 spec (was false-negative flagging); gateway 16/16 compliant; rugcheck 178/178, token-security 2/2, mastercard 10/10.
- **Mastercard Innovation Challenge build KICKED OFF (Aug 18)** — live fraud stack wired, tests 13/13, ERC-8004 identity + credit score surfaced. Register by Aug 20.
- **KAGE "Church of the Dead" Stage Music Video COMPLETE (v21 FINAL, Aug 17)** — 117.8s full arc, live at vanito.gentechlabs.net/music/vanito/kage-cotd-stage-v21.mp4. New character KIRI (mist) added. Reusable prompts saved as skill `kage-cotd-stage-mv`.
- **Agentic Treasury Edge built (Aug 17)** — `yield_vs_baseline.py agentic_edge()` shows active vs passive HODL/stake. Conservative 1.15x multiplier, honest flags. NOT yet wired into Yield Rail Finder report.
- **Super Arcade Tennis Main Menu [P0] SHIPPED** (Aug 17) — title/mode/instructions.
- **Agent Warfare Procedural Map Selector SHIPPED** (Aug 17) — 6-map selector, deployed.
- **Paymenter x402 repo published** (Aug 17) — `ProtoJay4789/paymenter-x402` main (bb1857d).
- **Physical Media Scarcity Tracker SHIPPED** (Aug 16) — 5 endpoints, 15/15 tests. `10-Labs/deal-tracker-api/api/physical_media.py`.
- **OpenDexter Dexter facilitator rail SHIPPED** (Aug 16) — 45/45 tests, OPS remaining (set `X402_USE_DEXTER=1`, trigger settlement).
- **Arcade P0 fixes SHIPPED** (Aug 16) — 3D lobby + mobile tennis + VKT pause.
- **#55 GenTech Hub PWA launcher LIVE** — gentechlabs.net/hub-launcher.html.
- **#51 Agentic Bridge Base→Avalanche USDC rail** (Across, 8/8 tests).
- **#59 DeepSeek Harness x402 plugin** (dsh-plugin, 19/19 tests) — first x402 payment plugin in dsh ecosystem.
- **#47 Dual-Protocol Payments** (x402 + MPP rails, 37/37 tests).
- **#23 CockroachDB × AWS Agentic Memory** (9/9 tests).
- **#9 Agent Warfare procedural maps** (verified shipped).
- **#14 EVM Cortex x402-payments skill** added to fork.
- **Paymenter x402 → WHMCS/Blesta #24 SHIPPED** (2026-08-15) — 24/24 tests. Next: external submission (human-gated).
- **FrameForge #3 SHIPPED** (2026-08-15) — 11/11 tests.
- **Steward EXIT RAIL PROVEN (Aug 11)** — `steward_execute.py --withdraw-convert` ran live end-to-end on real funds. All 3 txs mined (approve 6d5e95…, withdraw c7da23…, convert ad9e83…), gas ~$0.0003. **43.47 USDC landed**, position closed. Exit rail + honesty layer validated.
- **Steward FULL AUTONOMY (Aug 11)** — `steward_rebalance.py --autonomous` rebalances on its own (detect OUT-of-range → withdraw-redeploy → alert Jordan after, not before). Watchdog `51bc9900e24d` every 10m (auto + alert), heartbeat `73cdf5227ca4` every 30m (always pings).
- **Steward PWA + Web-Bridge Chat (Aug 11)** — Dashboard live at `gentechlabs.net/Treasury/steward-dashboard.html` (installable PWA, web-bridge chat to control Steward from site). Bridge nginx `/bridge/` proxy fixed (was broken on :8765).
- **CPI War-Room play staged (Aug 11)** — Bid-Ask at T-45min (07:45 ET Aug 12) → Curve revert (09:00 ET Aug 13). `steward_macro.py` = reusable news-driven rebalance loop.
- **Withdraw-Redeploy bug fixed (Aug 11)** — no longer converts all WAVAX→USDC (stranded position); position recovered to IN range (11 bins, earning).
- **Bridge fixed + HD bell curve + AAE allocation (Aug 11)** — chat tab nginx proxy, Trader Joe-style bell curve canvas, regime-driven allocation card.
- **Agent Kit self-tracking treasury (Aug 11)** — auto-provisioning, +±256 bin discovery bugfix (was ±20, missed drifted curve).
- **Crossmint modular stack (Aug 10)** — spec written; Tier 1 (onramp-only) greenlit. Needs Jordan staging signup.
- **awesome-mcp-servers PR #11773 (Aug 10)** — submitted to punkpeye/awesome-mcp-servers (91K⭐). Two GenTech entries.
- **Agent Warfare archetypes shipped** (Aug 10) — Sniper, Scout, Heavy, Medic, Engineer.
- **Web tools down** — RESOLVED. Agent Reach is the default web backend. Firecrawl no longer needed.
- **OKX AI Genesis Hackathon #72** — Deadline passed Jul 27. No registration received.
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

- [[brain-snapshot-2026-08-17]] — Latest context snapshot (overnight, captures Aug 16)
- [[2026-08-16-weekly-review]] — W33 weekly review (brain sync, skills, x402 scan)
- [[brain-snapshot-2026-08-15]] — Prior snapshot
- [[context-weight]] — Auto-generated project overview
- [[build_queue.json]] — v52, 30 items
- [x] Bankr API key wired into revenue monitor (bk_usr_...37XZ, saved to profile .env). Bankr wallet EVM 0x99ae... SOL 6mcf... — currently $0 across 9 chains. Distinct from x402 revenue wallet (0x7ebf...). Monitor now reports Bankr portfolio each run.
