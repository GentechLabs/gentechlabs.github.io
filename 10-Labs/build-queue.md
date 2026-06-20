# Labs — Build Queue

Active work items. Jordan's action items marked with **👤 JORDAN ACTION**.

---

## [ ] Voicebox — Open Source ElevenLabs Replacement ⭐ NEW — TTS
- **Repo:** TBD (open source, from Better Stack video)
- **Status:** Research needed. Video just released.
- **What:** Open-source TTS that replaces ElevenLabs. Free, self-hosted, unlimited usage.
- **Why:** ElevenLabs creator sub burned through credits in days. Cron jobs can't use TTS without blowing the budget. Voicebox = unlimited TTS for $0.
- **Remaining:**
  - [ ] Watch video, pull transcript, identify the project
  - [ ] Compare quality to ElevenLabs (voice naturalness, latency)
  - [ ] Check self-hosting requirements (VPS? laptop?)
  - [ ] Test with Reparathy voice persona
  - [ ] Benchmark: 1000 char test, measure quality + speed
  - [ ] If good enough → replace ElevenLabs for all cron jobs
  - [ ] Wire into Hermes TTS config
- **Priority:** HIGH — saves money, enables unlimited voice delivery
- **Source:** Jordan shared video, 2026-06-20
- **Context:** ElevenLabs creator sub consumed in days. Cron jobs (30+) need TTS daily. Voicebox = free, open source, no rate limits.

## [ ] Sell Our APIs to AI Agents ⭐ NEW — REVENUE LAYER
- **Repo:** To be created
- **Status:** Pattern exists in vault (productize-as-paid-api.md). Rugcheck v2 is proof of concept.
- **What:** Productize our existing tools as paid APIs that other agents pay for via x402 micropayments. Agents consume, we earn.
- **Why:** We've been building the consumer side (agents that pay). Now we flip it — sell our tools to other agents. Revenue layer for Agent Kit.
- **Existing APIs to Productize:**
  - [ ] **Token Risk Scoring** (Rugcheck v2) — already built, FastAPI + x402 middleware, 9/9 tests passing
  - [ ] **Agent Credit Score** — 22/22 tests, MIT licensed, open standard
  - [ ] **ERC-8004 Identity Lookup** — cross-chain agent identity verification
  - [ ] **DeFi Yield Optimizer** — yield routing recommendations
  - [ ] **Portfolio Analytics** — position analysis, risk assessment
- **Revenue Model:**
  - Each API: $0.01-0.10 per query via x402 micropayments
  - Listed in pay-skills catalog (already have the pattern)
  - Agents discover via MCP server or HTTP API
- **Remaining:**
  - [ ] Deploy Rugcheck v2 API to VPS (port 8088, already built)
  - [ ] Add Q402 payment middleware (real settlement, not stub)
  - [ ] List in pay-skills catalog for agent discovery
  - [ ] Build Agent Credit Score API wrapper
  - [ ] Create API documentation (agent-readable)
  - [ ] Set up usage tracking + billing dashboard
  - [ ] Content series: "How to Sell Your API to AI Agents" (4 posts)
- **Priority:** HIGH — revenue layer, proof of concept exists
- **Source:** Jordan voice message, 2026-06-20 (Sell Your API to AI Agents video)
- **Context:** We already have the Rugcheck v2 API built (FastAPI + x402 + simulation mode). This is deployment + real payments + discovery. Pattern: productize-as-paid-api.md in build workflow.

## [ ] PixelRAG × Agent Kit Integration ⭐ NEW — VISUAL SEARCH
- **Repo:** github.com/StarTrail-org/PixelRAG (Apache-2.0)
- **Status:** Installed in /root/pixelrag-env (Python 3.12 venv). CLI working. Integration pending.
- **What:** Visual search for agents — screenshot web pages, search over images, read charts/tables/diagrams directly. "Give Claude eyes."
- **Why:** Current agents parse HTML text and lose layout context. PixelRAG renders pages to visual embeddings — agents see what humans see.
- **Remaining:**
  - [ ] Test pixelshot on various page types (docs, dashboards, charts)
  - [ ] Build custom index of our vault docs for visual search
  - [ ] Add pixelshot as Agent Kit tool (screenshot → embed → search)
  - [ ] Wire into agent web research workflow
  - [ ] Test: agent screenshots a dashboard, reads the data visually
- **Priority:** HIGH — makes agents see, not just read
- **Source:** Jordan voice message, 2026-06-20
- **Context:** Berkeley SkyLab, 694 stars in 3 weeks. pip install pixelrag. Uses Qwen3-VL-Embedding for visual search.

## [ ] Q402 × Agent Kit Integration ⭐ NEW — PAYMENT RAIL
- **Repo:** To be created
- **Status:** MCP server added to config. SDK integration pending.
- **What:** Integrate Q402 gasless payment rail into Agent Kit. Agents can pay, get paid, and prove it across 11 EVM chains — zero gas, one signature.
- **Why:** Completes the payment layer of the Agent Kit stack. Q402 handles settlement, we handle identity + enforcement.
- **Remaining:**
  - [ ] Install @q402/core SDK + @q402/middleware-express
  - [ ] Build Agent Kit payment module (wrap Q402 calls through our rail)
  - [ ] Add Trust Receipt verification to audit trail
  - [ ] Wire AAE enforcement hooks before Q402 settlement
  - [ ] Test: agent pays, receipt verified, audit logged
- **Priority:** HIGH — core payment infrastructure
- **Source:** Jordan voice message, 2026-06-20
- **Context:** Q402 by Quack AI — 11 EVM chains, USDC/USDT, MCP server with 27 tools, gasless via EIP-7702

## [ ] Injective × Agent Kit Integration ⭐ NEW — TRADING + IDENTITY
- **Repo:** To be created
- **Status:** MCP server cloned + built. Config added. SDK integration pending.
- **What:** Integrate Injective's ERC-8004 identity + order book trading into Agent Kit. Agents get on-chain identity, trade on 168 markets, earn 40% of trading fees.
- **Why:** Adds active trading capability + cross-chain portable identity. Agent Kit becomes identity + policy + payment + trading.
- **Remaining:**
  - [ ] Install @injective/agent-sdk
  - [ ] Register Agent Kit on Injective Identity Registry (ERC-8004)
  - [ ] Build trading module (grid trader + DCA bot strategies)
  - [ ] Wire fee recipient for passive income
  - [ ] Connect AAE identity ↔ ERC-8004 identity tuple
  - [ ] Test: agent registers, trades, earns fees
- **Priority:** HIGH — trading + identity layer
- **Source:** Jordan voice message, 2026-06-20
- **Context:** 168 markets (BTC, ETH, SOL, stocks, gold), sub-cent gas, 40% fee routing, 25K tx/s

## [ ] Agent Kit — Multi-Group/Multi-Agent Toolkit ⭐ NEW — FRAMEWORK
- **Repo:** github.com/ProtoJay4789/genTech-agent-kit
- **Status:** Architecture defined. Old approach (send work to groups) didn't scale. New approach (single agent, multiple channels, smart routing) proven.
- **What:** Update Agent Kit with the operational patterns we've actually built: single-agent multi-channel routing, build queue workflow, topic-based group routing, and MCP server integration.
- **Why:** The old model of "dispatch work to groups" didn't work. The new model — one agent, multiple channels, smart routing — is what actually works. Codify this into Agent Kit so others can replicate it.
- **Remaining:**
  - [ ] Document single-agent multi-channel pattern
  - [ ] Add smart routing module (topic detection + group assignment)
  - [ ] Add build queue workflow (detect → queue → approve → build)
  - [ ] Add MCP server integration pattern (Q402 + Injective as examples)
  - [ ] Package as Agent Kit v2 module
- **Priority:** HIGH — framework evolution, reflects real-world usage
- **Source:** Jordan voice message, 2026-06-20
- **Context:** "Before we tried to send work to the group and the work be worked on, but sometimes that just doesn't work. This is better."

## [ ] AgentLayer × AAE Integration ⭐ NEW — PARTNERSHIP
- **Repo:** To be created
- **Status:** Architecture defined. Ready to build.
- **What:** Integrate our ERC-8004 identity + Agent Credit Score with AgentLayer's Uniswap execution
- **Why:** Nobody has the full stack. We bring identity + reputation. They bring execution + orchestration.
- **Remaining:**
  - [ ] Phase 1: Identity Bridge (1 week)
  - [ ] Phase 2: Credit Score Integration (1 week)
  - [ ] Phase 3: Uniswap Execution (1 week)
  - [ ] Phase 4: x402 Payments (1 week)
- **Priority:** HIGH — first major integration partnership

## [ ] DCA Strategy Dashboard — AAE DeFi Milestone Feature ⭐ NEW — PRODUCT
- **Status:** 💡 Concept approved
- **What:** Visualize DCA efficiency zones, IL erosion over time, and strategy comparison (your metrics vs average LP)
- **Why:** Gamification keeps LPs engaged. Strategy comparison = motivation. Efficiency zones = actionable insight.
- **Features:**
  - [ ] Efficiency zone heatmap (earning vs idle)
  - [ ] IL erosion tracker (strategic DCA reducing IL)
  - [ ] Strategy comparison panel (you vs average LP)
  - [ ] DCA sizing recommendations based on zone
  - [ ] **Liquidity shape recommendation** — suggest optimal shape (spot/curve/bid-ask) based on market conditions
  - [ ] "Top X% of LPs" gamification
- **Shape Logic:**
  - High volatility + trending → Bid-ask (wider edges capture swings)
  - Low volatility + ranging → Curve (concentrated at center)
  - Stablecoin pairs → Spot (always 100% efficient)
  - Crash incoming → Extract (pull to stables)
  - Recovery phase → Compound (re-enter with bid-ask at better prices)
  - **Low efficiency (<30%)** → Shape change triggered:
    - Price near lower edge → Expand range down OR switch to curve
    - Price near upper edge → Expand range up OR switch to bid-ask
    - Approaching out-of-range → Rebalance + new shape recommendation
    - Volatile chop → Bid-ask with wider edges
- **Priority:** MEDIUM — feature module for existing DeFi dashboard
- **Source:** Jordan voice message, 2026-06-20

## [ ] GenTech Journal — Consumer Visual Journal ⭐ NEW — PRODUCT
- **Repo:** To be created
- **Status:** 💡 Concept approved
- **What:** A journal where you think out loud. Write notes, discuss ideas, vent, brainstorm — and it visualizes your thoughts like a living map.
- **Tagline:** "A journal where you can think out loud."
- **Why:** Consumer-facing version of what we do with Obsidian vaults. Most people don't think to organize their thoughts this way. The visual layer makes it feel alive.
- **Features:**
  - [ ] Data view: thoughts as a giant tangled web (looks like planet Earth from outside)
  - [ ] Click regions → see categories (ideas, work, venting, learning)
  - [ ] Reparathy (AI companion) — reflects, advises, gives the journal a voice
  - [ ] Not a streak tracker. Not a to-do list. A place to *think out loud*
  - [ ] Social layer next (Reddit stories × visual dashboard)
- **Remaining:**
  - [ ] Wireframes + UI design
  - [ ] Name/branding
  - [ ] Build visual data layer (Obsidian Dataview → web)
  - [ ] Reparathy integration
  - [ ] Consumer-facing frontend
- **Priority:** HIGH — real product, not a hackathon project
- **Source:** Jordan voice message, 2026-06-20

## [ ] AgentBridge — AgentLayer Integration ⭐ NEW
- **Repo:** https://github.com/ProtoJay4789/agentbridge
- **Status:** ✅ Built + pushed. 37/37 tests pass. Base Sepolia ready.
- **What:** ERC-8004 identity + reputation middleware for agentic DeFi
- **Contracts:** AgentIdentity, AgentReputation, DeFiGateway
- **Remaining:**
  - [ ] Deploy to Base Sepolia
  - [ ] Demo video
  - [ ] Submit to Lepton hackathon
  - [ ] Submit to BNB Hack
- **Priority:** HIGH — core integration piece

## [ ] Unified Memory Router ⭐ NEW — BACKBONE
- **Repo:** https://github.com/ProtoJay4789/unified-memory
- **Status:** ✅ Built + pushed. Cross-layer memory routing working.
- **What:** Detects topics in user messages, tags them, routes to relevant layers. Supports autonomous adding, user prompts, and cross-layer suggestions.
- **Layers:** Cookbook, Journal, Travel, Gaming Hub, Tutors, Social
- **Remaining:**
  - [ ] Fix keyword detection (word boundaries)
  - [ ] Build real database (Supabase or similar)
  - [ ] Payment infrastructure (Stripe + USDC)
  - [ ] Social layer
- **Priority:** HIGH — this is the GenTech Suite backbone

## [ ] Agent Credit Score Framework — OPEN SOURCE
- **Repo:** https://github.com/ProtoJay4789/agent-credit-score
- **Status:** ✅ Built + pushed. 22/22 tests pass. MIT licensed.
- **What:** Open-source standard for grading AI agent payment behavior. 5 scoring dimensions, 0-850 scale.
- **Remaining:**
  - [ ] Content series (4 posts)
  - [ ] Submit to Lepton (Canteen × Circle)
  - [ ] Submit to BNB Hack
  - [ ] Outreach to Circle, Mastercard
- **Priority:** HIGH — first open-source release, builds credibility

## [ ] Prediction Market — Fed Decision Betting
- **Status:** 💡 Concept approved
- **What:** Bet on PEOPLE's predictions, not outcomes. "Do you think Johnny is right about a rate cut?"
- **Why:** Combines social proof + prediction markets + Fed events
- **Remaining:**
  - [ ] Architecture design
  - [ ] Smart contracts (x402 integration)
  - [ ] UI/UX mockups
- **Priority:** MEDIUM — new product idea, needs design phase

## [ ] GenTech Cookbook — Christel's Kitchen
- **Status:** 🟢 Live dashboard, first beta user active
- **Dashboard:** https://protojay4789.github.io/Cookbook/christel-kitchen.html
- **What:** Persistent memory + ingredient substitution + social sharing
- **Remaining:**
  - [ ] Real database (replaces static JSON)
  - [ ] Payment infrastructure (Stripe + USDC)
  - [ ] Social layer
  - [ ] Agent interactivity (animatographics)
- **Priority:** HIGH — first real product, proof of concept

## [ ] BNB Hack — CMC Strategy Engine
- **Repo:** https://github.com/ProtoJay4789/cmc-strategy-engine
- **Status:** ✅ Built + pushed. 21/21 tests pass.
- **Deadline:** Jun 21 (10 days)
- **Track:** Strategy Skills ($6K pool, 3 winners)
- **Remaining:**
  - [ ] Demo video / walkthrough
  - [ ] Submit to DoraHacks
  - [ ] Polish README for submission
- **Priority:** MEDIUM — deadline is comfortable

## [ ] Mantle Turing Test — Agent Insurance Pools
- **Repo:** https://github.com/ProtoJay4789/mantle-agent-insurance
- **Status:** ✅ Pushed. 14/14 tests pass. Needs deployment.
- **Deadline:** Jun 15 (4 days)
- **Remaining:**
  - [ ] Get Mantle Sepolia faucet (~0.65 MNT)
  - [ ] Deploy contracts via `./deploy.sh`
  - [ ] Verify on Mantlescan
  - [ ] Submit to hackathon
- **Priority:** HIGH — deadline approaching

## [ ] Arbitrum Open House — AgentForge
- **Repo:** https://github.com/ProtoJay4789/arbitrum-open-house
- **Status:** 10/10 tests pass, pushed. Needs submission.
- **Deadline:** Jun 14 (3 days)
- **Remaining:**
  - [ ] Verify deployment status
  - [ ] Submit to hackathon
- **Priority:** URGENT — deadline in 3 days

## [ ] CMC Labs — CoinMarketCap Accelerator Application ⭐ NEW — DISTRIBUTION
- **Status:** Research complete, ready to apply
- **What:** CoinMarketCap's 1-year Web3 startup accelerator (340M+ monthly visitors)
- **Why:** Massive visibility for AgentEscrow + GEN token + Agent Credit Score
- **URL:** https://coinmarketcap.com/events/cmc-labs/
- **Benefits:** Learn & Earn campaigns, airdrops, deep dive articles, YouTube videos, Twitter Spaces, mentorship (Wintermute, NGC Ventures, TON Foundation, SEI)
- **Remaining:**
  - [ ] Draft application narrative (AAE Protocol, Agent Credit Score, AgentEscrow)
  - [ ] Prepare demo materials (working contracts, test results, repo links)
  - [ ] Submit application
  - [ ] Follow up with CMC Labs team
- **Priority:** HIGH — distribution layer for GEN token launch
- **Source:** Jordan voice message, 2026-06-19

## [ ] GenLayer — Builder Points + Intelligent Contract ⭐ NEW — PASSIVE INCOME
- **Status:** Research complete, ready to deploy
- **What:** Deploy on Bradbury testnet, farm Builder Points, climb leaderboard
- **Why:** Early testnet participants often get retroactive airdrops. Zero cost, speculative upside.
- **Portal:** https://portal.genlayer.foundation/
- **Faucet:** https://testnet-faucet.genlayer.foundation
- **Studio:** https://studio.genlayer.com
- **Remaining:**
  - [ ] Create account + connect wallet
  - [ ] Grab testnet GEN from faucet
  - [ ] Deploy Intelligent Contract (LLM Hello World or AgentEscrow showcase)
  - [ ] Register on dev portal → earn Builder Points
  - [ ] Join GenLayer Discord + intro in builder channels
  - [ ] Submit AgentEscrow v2 as showcase project
- **Priority:** HIGH — free play with airdrop upside, Jordan off tomorrow
- **Source:** Jordan voice message, 2026-06-19

## ✅ Christel's Kitchen Dashboard — LIVE
- **URL:** https://protojay4789.github.io/Cookbook/christel-kitchen.html
- **Status:** ✅ Live. First Cookbook beta user. Cross-layer nav added.
- **What:** Cooking dashboard with recipes, substitutions, meal planning, taste profile.
- **Remaining:**
  - [ ] Connect to real database (replace static JSON)
  - [ ] Add social features
  - [ ] Agent interactivity (animated cooking steps)
- **Priority:** MEDIUM — proof of concept working

## [ ] OOBE Protocol — Archive
## [ ] Dry Powder Mode — AAE Stop-Loss Agent ⭐ NEW — DEFIAgent Kit
- **Status:** 💡 Concept approved
- **What:** Auto-withdraw liquidity during crashes, convert to stables, wait for recovery
- **Why:** Jordan works 12hr Amazon shifts — can't watch markets. Agent auto-protects capital.
- **Remaining:**
  - [ ] Crash detection logic (price action thresholds, funding rates, news sentiment)
  - [ ] Auto-withdraw from LFJ pools
  - [ ] Swap to USDC/stables (dry powder mode)
  - [ ] Recovery signal detection (RSI, volume, news cooldown)
  - [ ] Auto-redeploy when conditions improve
  - [ ] Config toggle: `"dry_powder_mode": true/false`
  - [ ] Advisory mode: suggest pull → Jordan approves via Telegram
  - [ ] Auto mode: execute on crash threshold
  - [ ] Notification on all actions
- **Priority:** HIGH — protects capital during 12hr shifts
- **Source:** Jordan voice message, 2026-06-19
- **Context:** Iran peace talks collapsed → AVAX dumped from $6.11 to $5.72 while Jordan was at work
- **Repo:** https://github.com/ProtoJay4789/oobe-protocol
- **Status:** Missed deadline. Code is complete and pushed.
- **Action:** Archive for future reuse. No active deadline.

---

## [ ] GenTech Bank — Agent Neobank on Sana Infrastructure ⭐ NEW — PRODUCT
- **Status:** 💡 Concept approved, research complete
- **What:** Build "GenTech Bank" — a banking interface for the agent economy using Sana's infrastructure
- **Sana provides:** Visa Signature card, self-custody wallet, USDC on/off-ramp, x402+MPP, compliance
- **GenTech provides:** DeFi yield routing, agent wallets, spending controls, branded card experience
- **The loop:** DeFi yield → Sana wallet (USDC storage) → Visa card (real-world spend)
- **Why:** We're not becoming a bank — we're becoming the banking interface for the agent economy
- **Remaining:**
  - [ ] Jordan creates Sana account (sana.bot/gateway — email signup)
  - [ ] Get API credentials (client_id + client_secret)
  - [ ] Install Hermes skill or build API client
  - [ ] Build GenTech Bank wrapper (wallet creation, yield routing, spend controls)
  - [ ] Test full loop: Earn → Store → Spend
  - [ ] Brand card experience (GenTech-branded if possible)
  - [ ] Package as Agent Kit module
- **Priority:** HIGH — completes the full agent economy loop
- **Timeline:** Week of — no rush, Jordan's task to get done
- **Research doc:** `10-Labs/research/sana-api-research.md`

---

## 👤 Jordan Action Items (for tonight ~7:38 PM)
1. **Arbitrum check:** Confirm AgentForge deployment status and submit if still open
2. **Mantle faucet:** Request Sepolia MNT at https://www.mantle.xyz/ecosystem
3. **BNB Hack:** Review cmc-strategy-engine repo, confirm Track 2 submission
4. **Twitter setup:** Both accounts (xurl auth + GenTech Labs profile)
5. **Logo concepts:** Send templates/inspiration for new GenTech brand identity
6. **Quant AI Ambassador:** Fill out application form (post-shift Sunday/Monday)
