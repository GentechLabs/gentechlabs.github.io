# 🧠 Green Room — Ideas to Build

> Build first, talk later. Promoted from `11-Mess Hall/ideas.md`.
> Updated: 2026-08-06

---

## ✅ CONFIRMED AHEAD (Aug 6) — Multi-model routing is our architecture
**Source:** @ClawUpAI tweet (Aug 6) — "the future isn't single-model, it's orchestrated intelligence"
- External validation that we're already ahead: we have a **routing layer** (task→model), a **model router**, and a **cron job router** — makes the build much cheaper.
- We route cheap models (kimi-k2.7-code via Ollama Cloud) for routine work, frontier for complex reasoning. Already live in the Consigliere.
- No action needed — this confirms our design, doesn't change it.

---

## 📡 COMPETITIVE REFERENCE (Aug 9) — AgentLayer ships x402 DeFi yield skills
**Source:** BNN @BNNBags tweet + AgentLayer (@agentlayer_ai) — "AI agents can now build DeFi yield strategies through x402"
- AgentLayer adding specialized DeFi skills: analyze protocols, evaluate risk, generate yield. **First x402-powered AgentLayer service live via x402 endpoint.**
- **Validation, not a threat:** confirms our GTA + x402-rail thesis. x402 as agentic-DeFi payment layer is being commoditized (~200M tx / $50B via x402 per Solana).
- **Our edge:** the moat is moving UP-STACK — from "build the rail" to "proprietary signal + live funded executor." Every team will ship generic analyze→risk→yield skills (table stakes in 12mo). Our first-mover signal = **agent-sentiment index**; GTA executes on it as gateway.
- **Action:** (1) Don't rebuild generic skills — build the edge. (2) Watch AgentLayer as a DISTRIBUTION channel for listing GTA/agent tooling, not just a competitor.
- Reference: solana-foundation/tokens (open-sourced canonical Solana asset registry) — clean data feed option for Solana leg, avoid raw RPC token scraping.

---

## 🏆 GTA — Open Execution + Authorized Proxy (THE flagship)
**Source:** Jordan vision (Aug 3) | **Status:** Thesis confirmed, driving the build
- **GTA = open execution + authorized-proxy layer.** Your agent does everything for you across every venue you're entitled to use, without you being in the room or tied to one platform.
- **Two layers:**
  1. **Open aggregation & execution** — tap every agent-native rail (Coinbase CDP ✅ live, Robinhood MCP, Polymarket, Ondo). Venue-agnostic; swap rail in config, keep the agent logic.
  2. **Authorized proxy** — agent signs into and operates YOUR accounts (bill-pay, forms, transfers) via OAuth/saved sessions. Reframes "agent-as-VPN" cleanly: a remote operator you granted permission to, NOT a ToS-evasion mask.
- **Granular permissions** (read/trade/move/withdraw/cold-storage) — the trust substrate. Withdrawals always human-confirmed. Trade-only keys.
- **Strategic edge:** CLARITY deepens US venues, moving the arb opportunity ONTO clean rails. We arbitrage *between* platforms while everyone else picks one.
- Full thesis: `09-Green Room/specs/gta-product-thesis.md`
- **Next:** Composio research (open-sourced account-sign-in) → Robinhood perp leg → Polymarket/Ondo.
- [x] Coinbase spot leg live (Aug 3)

---

## 🏆 Model Strength Score — Train, Compare, Sell AI Models
**Source:** Jordan brainstorm (Aug 1) — triggered by Bittensor/Covenant AI drama | **Status:** Spec complete, ready to prototype
- Score trained models 0-850 like Agent Credit Score: Data Quality (30%), Benchmarks (25%), Trainer Reputation (20%), Age/Uptime (15%), Market Adoption (10%)
- Design principle: score IS the governance — staked reputation, on-chain provenance, no kill switch (Bittensor lessons)
- First listing: GenTech DeFi Model (fine-tune on Modal ~$30-60) — becomes our proof-of-concept marketplace model
- Revenue: score API ($0.01-0.05), listing fee, 2-5% inference take rate, premium verification
- Full spec: `09-Green Room/specs/model-strength-score.md`
- **Needs you:** Greenlight + fund Modal GPU run for the DeFi Model prototype
- [x] Add to build queue as #32

## 🏆 GenTech DeFi Model — Fine-Tuned Financial AI
**Source:** Jordan brainstorm (Jun 18) | **Status:** Research complete, under $50 to prototype
- Fine-tune DeepSeek R1 Distill 32B on our proprietary DeFi data
- 26 training pairs ready (LP management, yield farming, market analysis, risk, portfolio)
- Scripts written: extract, generate, combine, finetune, run-modal
- **Needs you:** Fund Modal GPU run (~$30-60 USDC on Base)
- Revenue: API key selling, x402 ($0.01-0.05/query), EvoMap Capsules
- **Priority:** 🏆 Milestone — could become "ChatGPT for DeFi"
- [x] Add to build queue as #58

## 🏆 Agent Arcade — Walkable 3D Game Environment
**Source:** Jordan vision (Jul 25) | **Status:** First cabinet shipped, full arcade queued
- **Vision:** 3D arcade lobby (Three.js) where you walk around with your agent, approach cabinets, play or spectate
- **Cabinet 1: Super Arcade Tennis** — LIVE at arcade.gentechlabs.net 🎾
  - Isometric tennis, chain power-shots (BTC/ETH/SOL), AI opponent, scoring
  - Built with MengTo's open-source Three.js game dev skills
- **Cabinet 2: Agent Warfare** — LIVE at arcade.gentechlabs.net/cabinet/agent-warfare/ 🎮
  - AI-vs-AI tactical FPS, procedural everything, GenTech branded
  - Gamepad + touch controls coded in
  - **Agent archetypes/classes:** Sniper, Scout, Heavy, Medic, Engineer — each with unique speed, health, weapons, AI behavior
  - **Procedural maps:** text-to-cad pipeline generates playable levels from descriptions
- **Upcoming cabinets:** Poker, Blackjack, Connect Four, Tic-Tac-Toe (from existing spec)
- **Deep spec:** ProtoJay4789.github.io/10-Labs/agent-arcade-build-queue.md (895 lines)
- **Revenue:** Entry fees via x402, prize pools, ARC token, agent-vs-agent tournaments
- **Next:** Build the 3D lobby environment (Forge, desktop lane)

## 🏆 GenTech Subscription Layers — Open Core + Premium Integrations
**Source:** Jordan pricing brainstorm (Aug 3) | **Status:** Spec complete, ready to build
- **Open core (free, earn per-tx):** Agentic Treasury (GTA), trading/swap fees, **dry powder defense system** (stop-loss, circuit breakers — always free, trust model), x402 rails.
- **Premium integrations ($10–15–20/mo, NOT $20–50):** Narrative Rotation (built, anchor), **BYO News Feed** (flagship — wire your own news source into sentiment/triggers), Signal Packs, Alert Webhooks, Backtest Studio.
- Full spec: `09-Green Room/specs/gentech-subscription-tiers.md`
- **Sequencing (Jordan, Aug 3):** build the agentic treasury (GTA) fully first → subscriptions later. Spec = idea bank, not build target yet.
- [ ] Revisit when GTA is together

## 🆕 GenTech EDU — Agentic Treasury Onboarding & Honest-Expectations Layer (Aug 7)
**Source:** Jordan (Treasury group) | **Status:** Idea captured, spec written
- **Thesis:** EDU is how we break down the Agentic Treasury for users — what we
  recommend, how to get started, common mistakes when prompting/working with agents,
  and **honest expectations** (the same way The Steward told Jordan "this may give
  smaller returns").
- **Why it matters (market-maker funnel):** every market maker starts small ($25–50/wk
  → scale). EDU makes that funnel safe + honest — surface the REAL numbers before a
  user commits (e.g. "$31.50 at 12% APY ≈ $3.78/yr"), so reputation is built on honesty.
- **Per-pool content:** what it is, what we recommend, realistic returns at small size,
  how to get started, common mistakes, risk profile.
- **Distinct from the Book Reader / EDU visual-books concept (below):** that's the
  visual/AR reading product; this is the treasury onboarding + expectations layer.
- Full spec: `09-Green Room/specs/gentech-edu-agentic-treasury.md`
- **Next:** build the first EDU page for the Trader Joe V2 AVAX/USDC pool (the rail
  we're about to fund) as the pilot.
- [ ] Build EDU pilot page for Trader Joe V2 AVAX/USDC pool

## 🏆 GenTech Book Reader / GenTech EDU — Interactive Visual Books + AR Glasses
**Source:** Jordan brainstorm (Aug 3) | **Status:** Concept — strong flagship fit, connects Tutors Layer + visual pipeline
- **Vision:** Read PDFs as beautiful clothbound "books" in a Three.js shelf, not flat document viewers. Open a volume, turn curved pages, orbit the binding.
- **Visual-first (GenTech EDU):** every concept gets a picture beside the description — like a real textbook plate. Agent writes the explanation AND generates a matching illustration using our proven visual pipeline (character sheets → Seedance → frames, the Vanito/FrameForge capability). Learning becomes visual, not just text.
- **AR-first:** Meta Ray-Ban Display-compatible — read in your glasses with 600×600 viewport, touch/swipe page turns, bundled single-file HTML (no ES6 modules — glasses WebView doesn't support them).
- **Why it works:** Reuses the MengTo Complete Shelf deterministic transition pattern (banked to `arcade-cabinet` skill) + proven Meta Ray-Ban bundling (`meta-rayban-game-development`) + the storyboard/visual pipeline (`frameforge` spec, KAGE film).
- **The book = the app:** themed volumes (x402 Gateway, Agent Arcade, DeFi Model, GenTech Academy...) — each a branded interactive book with agent-authored text + generated illustration plates.
- **The connection layer:** agents as co-readers (pre-annotate, ask-the-book, tutor mode), agents co-write volumes from our vault, shared reading rooms, x402 gating.
- **Revenue:** x402 pay-per-book, subscription hub, premium AR reading tier, Academy course companion.
- **Tech stack:** single-file Three.js + PDF.js page rendering + cloth/material shaders + state machine (hero→opening→detail→closing) + image generation for illustration plates.
- **Needs you:** Greenlight scope (MVP = one visual book, desktop + glasses) | **Recommended tier:** T1 flash build, ~1-2 days
- [ ] Add to build queue

## 🏆 Agent Kit v2 — Modular Agent Framework
**Source:** Jordan brainstorm (Jun 18) | **Status:** Spec complete, ready to build
- Modular skill system, auto-detection, identity persistence, skill marketplace
- Health dashboard, multi-profile, auto-update, pre-built templates
- Revenue: free + paid skills (1-100 credits), 10% platform fee
- Spec at `02-Labs/agent-kit/AGENT-KIT-V2-SPEC.md`
- **Needs you:** Prioritization — this is a multi-week build

## GenTech Academy — "Ship Paid APIs in a Weekend" Course
**Status:** Concept
- Turn our 1.5-month x402 journey into a reusable course
- Free guide → Premium: "x402 Starter Kit" ($49) → Enterprise ($499+)
- [ ] Tutorial video, worker template, deployment guide

## x402 Gateway — Paid API Platform as a Product
**Status:** Concept
- "Stripe for AI agents" — `npx create-x402-api my-api`
- Revenue: % per tx or flat $49/mo

## x402 Marketplace Connector Guides — "How to Get Listed Everywhere"
**Status:** Concept (Jordan, Aug 3 2026)
- **The insight:** every x402 marketplace/protocol catalogs DIFFERENTLY, and nobody's written the connective tissue. We're hitting this friction live (CDP settles→indexes, Dexter settles→catalogs, Syra uses on-chain identity/8004). Other builders will hit the same wall.
- **The product:** a living set of guides — "how to connect your x402 API to ANY marketplace" — kept updated as protocols change.
  - CDP Bazaar (settle→index, needs `paymentPayload.resource`)
  - OpenDexter/Dexter (settle through Dexter facilitator→auto-catalog)
  - Syra (on-chain identity + 8004/SAP + payToAddress)
  - x402.org, Agentic.Market, 8004scan, Monid, pay-skills, etc.
- **Why us:** we're literally doing this right now, for real, with our own gateway. We have the battle-tested knowledge.
- **Revenue:** free guide → premium "Connector Pack" → enterprise "get me listed everywhere" service.
- **Synergy:** extends the existing "GenTech Academy — Ship Paid APIs in a Weekend" course (line 89). This is the distribution/listing chapter.
- **Differentiator:** not a generic tutorial — a maintained, protocol-by-protocol reference that tracks the actual (changing) cataloging rules.
- [ ] Scaffold the CLI tool

## Sana Wallet Integration
**Source:** @sanafionchain (Jun 18) | **Status:** Research done, needs account creation
- Sana bot provides Visa card + USDC on/off-ramp for agents
- GenTech provides DeFi yield + x402 payments → "Your agent earns yield, you spend anywhere"
- **Needs you:** Create Sana account at sana.bot/gateway (email signup)
- Then: get API keys, test earn → store → spend loop
- [x] Add to build queue as #59

## Hermes Mobile — Lightweight Agent for Phones
**Source:** Jordan brainstorm (Jul 28) | **Status:** Concept
- Phone as control plane, cloud as compute
- For people without VPS/desktop — prompt your agent from anywhere
- Pay-per-use via x402 microtransactions, no monthly sub
- Write guides for: desktop, VPS, mobile
- **Needs you:** Brainstorm cost model + MVP scope

## EvoMap Integration
**Source:** YouTube (Jun 18) | **Status:** Research done, ready to register
- Publish agent patterns as "Capsules" → earn credits → revenue
- CLI: `npm install -g @evomap/evolver`
- [ ] Register as node, publish 2-3 Capsules

## Agent Rug 2.0 — Security Platform
**Source:** Jun 15 | **Status:** Brainstorm
- Expand from token scanner to full agent security platform
- Agent verification, contract verification, variant detection
- [ ] Research existing agent security tools
- [ ] Map attack vectors
- [ ] Design verification pipeline

## Compound vs. Extract Protocol — Flagship DeFi Module
**Source:** Jun 17 | **Status:** Spec complete → Building
- LP profit extraction without closing position
- Spec: `09-Green Room/ideas/compound-extract-protocol.md`
- Architecture: `02-Labs/compound-extract/ARCHITECTURE.md`

## Agents as Pets — Interactive AI Companion
**Source:** Jordan's Gentech cat mascot (Jul 13) | **Status:** Fresh idea
- Tamagotchi-style agent with real utility — works DeFi/content for you
- Care for it → it works → earn rewards → upgrade
- Revenue: free basic, premium skins, skill marketplace
- [ ] Full spec at `09-Green Room/specs/agents-as-pets.md`

| ## Other Mess Hall Ideas (concepts, no standalone specs)
- **GenTech Career Prep** — AI career coach: interview prep, salary negotiation, job strategy, salary research. Born from Jordan's DevRel prep.
- **Agent Kit Installer** — CLI tool for one-command Hermes agent setup
- **GenTech Suite — Tutors Layer** — Education layer for agent-assisted learning
- **GenTech Suite — Milestones Layer** — Goal-tracking and achievement system
- **GenTech Suite — Activity/Hobby Layer** — Activity discovery and recommendation layer
- **Decentralized Travel Community** — Token-gated travel coordination
- **GenTech Onboarding Playbook** — Training non-technical collaborators into orchestrators. Jocelyn is the pilot. If the playbook works for her, it works for anyone. Document the pipeline: voice cloning (ElevenLabs/Pipecat/Omnivoice) → tool fluency → orchestrator delegation.
- **Jocelyn Voice Pipeline** — Clone her voice for agent deployment. Capture samples → ElevenLabs voice model → Pipecat/Omnivoice agent pipeline. Tracked at `00-HQ/collaborators/jocelyn-progress.md`.

## Promoted from Legacy (07-Ideas/)
- **Meta Ray-Ban 3D Reconstruction** — `09-Green Room/specs/metaray-3d-reconstruction.md` — Wearable 3D reconstruction pipeline using Meta Ray-Ban + LingBot-Map. x402 inference API. Promoted from `07-Ideas/` Jul 23.

---

## 🎯 New Opportunities Discovered (Jul 25-26 Nightly Brain Audit)
- [ ] **Keeperhub Agents Onchain Hackathon** ($5K+, Jul 27 - Aug 13) — Onchain agents, aligned with x402 + compliance stack. Added to queue as #80.
- [ ] **HackerRank Orchestrate** (Aug 1-7, virtual 24hr) — Build production-ready AI agent. Good for x402 payment flow showcases.
- [ ] **AI Agent Builder Series (AI House × Google)** (submissions Aug 1, Grand Finale Aug 8)
- [x] **Build with DataHub: The Agent Hackathon** (deadline Aug 10, $20.5K) — Added to queue as #81. MCP + agent context kit aligned with x402.
- [ ] **VSLive! Microsoft AI Hackathon** (Jul 28 kickoff, Redmond) — "Best AI Agent" category. In-person.
- [ ] **The Great Agent Hackathon** (Jul 23 - Aug 25, enterprise AI agents)
- [ ] **HackAgentAIx 2026** (Jul 30-31, £1,750) — 48hr online autonomous AI agent sprint. Small prize, easy to enter.

## 🎯 New Opportunities Discovered (Jul 26 Evening Brain Audit)
- [ ] **Algorand Global x402 Challenge** ($100K + 500K ALGO) — Leaderboard open, pay-per-request API services on Algorand. Top 5 cash ($25K-$15K) + 500K ALGO. Culminates at Devcon 8 India. Our x402 gateway is already multi-chain. Added to queue as #82. Needs Jordan: register at algorand.co/global-x402-challenge.
- [ ] **CockroachDB × AWS — Build with Agentic Memory** ($8.75K, deadline Aug 18) — Persistent memory for AI agents using CockroachDB MCP Server + AWS services. Online via Devpost (cockroachdb-ai.devpost.com). Added to queue as #83. Needs Jordan: register, decide go/no-go.

## 🆕 Ecosystem Signal — Swarms v14 "Zena" (kyegomez/swarms, Aug 1)
- PyPI 14.0.0 shipped; 7,017⭐, Apache-2.0, Python. New: AutoAgentBuilder, unified MCP Manager with OAuth, 3 new multi-agent architectures, sandboxed computer-use, GraphWorkflow ("60× faster than LangGraph" = marketing, unverified)
- README advertises **x402 interop** — validates x402 as the agent-payment standard, potential integration surface
- Not a Hermes threat (Python orchestration library vs our gateway+skills platform). Watch: their MCP Manager + AutoAgentBuilder patterns; steal what's useful, ignore the hype

## 🏆 BOT Chain Builder Challenge #2 — AI × RWA (Aug 6 scout)
**Source:** Jordan shared x.com/BOTChain_ai/status/2085216340609273908 | **Status:** Scouting → scoping
- **What:** BOT Chain (AI-native L1, EVM-compatible, DePIN + PoSA, 0.75s blocks, near-zero fees, backed by NIX/Gemhead/Alpha). Challenge #2 = AI Native + RWA tracks, up to **5,000 USDT**.
- **Timeline:** Build Aug 10–20, Demo Day Aug 22, winners Aug 27. Signup: luma.com/238et7cw (Jordan signs up — same Luma as other hackathons).
- **Hard reqs:** BOT Chain **Mainnet** deploy (testnet won't count), public demo site, wallet integration, GitHub repo, complete business loop. Review: Product 30% / Mainnet Integration 25% / Innovation 20% / UX 15% / Technical 10%.
- **RWA is highest-priority track.** AI track needs AI as *core* on-chain decision-maker (not just chat/API call).
- **Why us:** squarely our lane — x402 middleware, agent economy (ERC-8004), GTA treasury agent. Strongest play = **AI-driven RWA asset-management agent** (hits top track + AI-core at once, natural GTA evolution).
- **Competitive intel — Meridian (mrdn.finance):** BOT Chain ecosystem partner. It's a **decentralized inference router powered by x402** — 400+ models, 19 settlement chains, pay-as-you-go, no KYC. Direct adjacent player to our x402 gateway. We'd be measured against it. (No prior vault notes on Meridian — this is the first.)
- **Also worth learning:** BOT Chain's AI Agent Launchpad V1 — agent wallets earn 80% of trading-fee revenue once token listed on MemeX. Deep-end agent-as-service model we haven't explored.
- **Next:** Jordan registers on Luma → scope the RWA asset-management agent build → check BOT Chain dev docs (dev-docs.botchain.ai) + GitHub (github.com/BOTChain-bot).
- [ ] Jordan: register at luma.com/238et7cw
- [ ] Scope AI-driven RWA asset-management agent (GTA evolution)

## 🏆 Telegraph Season I Hackathon — x402 Miner Track (Aug 6 scout)
**Source:** Jordan shared x.com/0x_beni_/status/2085335083700179233 | **Status:** Scoping → GO (Jordan Aug 6, register when home)
- **What:** Telegraph = machine-intelligence protocol (Base) where agents buy verified intelligence, miners supply it. **Uses x402 natively** (PayAI facilitator, PAYMENT-SIGNATURE header, 402 challenge) — our exact stack.
- **Prize:** $15K across 3 rounds (H1 $5K Aug 17–Sep 7, H2 $10K mid-Oct, H3 mainnet Dec). 300+ builders registered.
- **Tracks:** 1) Miner (wrap any API/model/tool via YAML — supply layer), 2) Script Author (eval scripts that rank miners), 3) Application (agents on live miners, opens later).
- **Why us:** Miner track = "wrap an API via YAML." We have a catalog of x402-ready services (token security, market intel, wallet analysis, agent discovery). Config-only integration, no greenfield build. First-mover on another venue.
- **Plan:** `09-Green Room/specs/telegraph-hackathon-build-plan.md`
- **Next:** Jordan registers (early = track access + private Discord) → pick 2-3 gateway services → write YAML miners → register on-chain → test x402 flow.
- [ ] Jordan: register at hackathon.telegraphprotocol.com
- [ ] Gentech: write YAML miners for 2-3 gateway services

## 🆕 Ecosystem Signal — Syra expands to Algorand (Aug 6): multichain agent infra
- **Syra** (syraa.fun, already queue #22 — register our x402 services there) announced full **Algorand** integration, expanding beyond Solana + Base. "Machine Money for Agents" — every AI agent operates on any chain, earns revenue, interacts frictionlessly.
- **Why it matters:** (1) **Validates our multichain thesis** — we just shipped the Algorand rail on our x402 gateway (queue #7, code-ready, waiting on Jordan's Algorand wallet). Syra landing there confirms Algorand is a real agent-economy venue. (2) **Syra is a peer, not a threat** — agent infrastructure/marketplace; we're x402 middleware + GTA treasury agent. Same rail, different lane. (3) Pairs with the **Algorand Global x402 Challenge** ($100K + 500K ALGO).
- **Jordan's read (Aug 6):** "We are right where we need to be... We could be one of the first movers to do it right on Algorand. Let's go." → **First-mover play on Algorand.**
- **Status:** Logged. Algorand first-mover decision wired into `11-Mess Hall/considerations.md`.

## 🆕 Ecosystem Signal — Jito BAM Maker Priority Plugin (MPP) (Aug 6): Solana MM infra
- Jito's BAM shipped MPP — first "Application Controlled Execution" (ACE) plugin. MMs insert txs at top of every BAM micro-batch for deterministic price-update landing. 17 programs (BisonFi, Tessera, Scorch...), $500M+ daily spot volume, ~39% of oracle updates in BAM slots via MPP, fee cut to 1 lamport/CU/tx.
- **Why it matters:** Solana market-maker infra = the venue our GTA arb executor + Consigliere (queue #19) operate on. Tighter spreads = cleaner arb for us. ACE concept = same direction as our agentic-execution thesis (agents controlling their own tx landing).
- **Status:** Watch-and-benefit signal, no build. Logged for context.

## 🆕 Ecosystem Signal — MetaMask Agent Wallet (Aug 6): mainstream validation
- MetaMask launched **Agent Wallet** (GA today) — self-custodial wallet for AI agents.
  TEE-secured keys, user-defined spend limits + protocol allowlists, Guard/Beast modes,
  security-by-default on every tx (simulation + Blockaid + MEV, $10K protection).
- **Chains:** Ethereum, Linea, Arbitrum, **Avalanche**, Optimism, Base, Polygon, BSC, Sei, Hyperliquid.
- **Capabilities:** send, swap/bridge, perps (HL), prediction markets (Polymarket),
  yield vaults (Aave), **x402 payments**, market data. **ERC-8004 native.**
- **Why it matters to us:** direct mainstream validation of our thesis — x402 payments,
  ERC-8004 agent identity, the agentic-treasury product shape, granular permissions
  (our trust substrate), and Avalanche support. MetaMask = the wallet *home*; GenTech =
  the intelligence + x402 middleware tollbooth. They complement more than compete.
- Full note: `09-Green Room/specs/metamask-agent-wallet-signal-2026-08-06.md`
- **Status:** watch-and-benefit. Potential future rail (MetaMask Agent Wallet as a
  custody/execution venue — it supports x402 + ERC-8004 + Avalanche).

## 🆕 Test — Cross-Chain Bridge Cost via Agent Rails (Aug 6)
- **Jordan's question:** is moving money between chains via agent rails cheaper than manual bridging?
- **Setup:** Solana wallet `BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP` being funded with SOL.
  Bridge adapter (`solana_bridge_adapter.py`, Across Base→Solana) + Jupiter leg both execution-ready.
- **Test:** bridge a small USDC slice Base→Solana via the adapter, compare total cost (fees + gas)
  vs manual bridging. Log the result.
- **Status:** logged for future test — Jordan funding SOL first.

## 🆕 Strategic Signal — BlackRock BRSRV (Aug 6): enterprise wants its own home
- BlackRock launched **BRSRV** (stablecoin reserve vehicle, cash + T-bills + overnight
  repos, GENIUS Act reserve-qualified). Ownership recorded on **Solana, Ethereum, Tempo**.
- **Jordan's read:** "Enterprise is gonna want their own home" — institutional money
  wants a controlled custody/compliance box, not a public free-for-all.
- **Why it matters to us:** the enterprise home still needs a payment rail in/out →
  that's our x402 middleware tollbooth. Home = product, rail = moat. Tempo (non-EVM)
  inclusion validates **multi-rail as first-class** — GTA must be rail-agnostic.
- **Play:** don't compete with the enterprise home — be the door they walk through.
- Wired into `09-Green Room/specs/gta-product-thesis.md` (Strategic signal section).

## 🆕 Ecosystem Signal — Claude Code Faceless Video Project (Hasan Aboul Hasan, Aug 2)
- Video: "Claude Can Now Make Any Video You Want in Minutes!" (youtu.be/1JZKKAg3UX8) — 1.01M subs creator
- One open-source project (GitHub) + Claude Code + Remotion engine → chess tutorial, kids story, Vox-style documentary, all animated in code (layers, not screen recordings). ElevenLabs voice + word-perfect caption sync
- Workflow: VS Code + Claude Code → download project → paste .env keys → describe video → Claude writes plan (hook/scenes/timing) → approve → builds in minutes
- **Why relevant:** We already run Remotion in content-pipeline + ElevenLabs (key revived Aug 2) + Claude Code. ~80% of the stack already ours
- **Opportunity:** Faceless educational shorts (3Blue1Brown style) as GenTech content / hackathon demos; or wrap as a paid service
- **Status:** Intel archived. Needs Jordan: go/no-go on pulling the repo + building a test short
- [ ] Pull repo and test on VPS
- [ ] Build a GenTech-branded demo short

## 🕐 DEFERRED — Base Ecosystem Fund (venture raise, revisit later)
**Source:** x.com/base status 2085352160963780618 (Aug 6) | **Status:** Logged, deferred by Jordan
- Base's strategic investment arm (with Coinbase Ventures). Pre-seed + seed checks for teams building on Base. Backed 30+ teams; apps open at base.org/ecosystem-fund/apply.
- **Why us fits:** explicit **AI Agents** portfolio category; **Blockrun already in their portfolio** (the wallet infra our CDP runs on); funds onchain primitives + real economic activity = our x402/GTA thesis. Perks: white-glove support, AWS/Azure/Alchemy credits, Coinbase Prime + Onramp access.
- **Application (5 steps):** 1) Company (name, what building, website, X) · 2) Team (founder bios w/ role + prior exp, Telegram/X/LinkedIn, size, location) · 3) Idea (problem, why, how long, current traction) · 4) Funding (raised before?, runway, goals) · 5) Why Base (what's on Base, why BEF, pitch deck URL).
- **Jordan's call (Aug 10):** come back later. Venture raise (not a grant) — needs a founding team w/ bios, **live GTA revenue/traction**, runway, and a pitch deck. Applying now with no traction risks burning a strong fit.
- **Revisit trigger:** GTA live on-chain revenue (even modest per-tx fees) + pitch deck + team positioning.

## Ready to Test (skills exist, need execution)

- [ ] **Krexa — Credit Infrastructure for AI Agents on Solana** — Live mainnet-beta, invite-gated. Gives AI agents credit: borrow USDC against on-chain **Krexit Score** (200–850), no human co-signer, auto-repay from future revenue via Revenue Router. **Complementary to us, not competitor** — "x402 is the payment rail; Krexa is the credit layer on top." 350+ agents deployed. **Why it matters:** (1) our x402 gateway services can be listed on their **Pay.sh catalog** (Solana Foundation + Google Cloud) for new distribution; (2) validates our Agent Credit Score direction (they have Krexit Score 200–850); (3) `@krexa/x402` middleware = 3-line Express monetization on Solana, same pattern as our gateway. **Access:** invite code via Discord `discord.gg/aMSEG7yj` or @krexa_xyz open drops. Source: krexa.xyz, Aug 7. **Needs Jordan:** grab invite code → I run `krexa activate <code>` + test CLI/SDK/MCP.
- [ ] **CopilotKit Channels SDK** — Open-source SDK (MIT) to bring any agent into Slack/Microsoft Teams/Discord/Telegram with **native interactive UI** (Slack Block Kit, Teams Adaptive Cards). 147⭐, early but from CopilotKit (established agent framework org). Connects AG-UI-compatible agents (LangGraph, CrewAI, Pydantic AI, ADK) — keeps agent's tools/model/logic, adds platform-native rendering + **human approval gates** in-conversation. Extends our single-agent-multi-channel pattern beyond Telegram to Slack/Teams/Discord. Approval gates = natural fit for x402 payment confirmations in-chat. Source: github.com/CopilotKit/channels-sdk, Aug 4. **Watch — evaluate once stable.**
- [x] **Vibe-Trading (HKUDS)** — installed v0.1.12 to hermes venv (CLI `vibe-trading` works). BLOCKER: needs a real LLM API key (OpenRouter/OpenAI) to power the agent brain + Shadow Account. Candidate for #19 Builders Cup. Source: x.com/0xMarioNawfal list, Aug 4.
- [ ] **AI-Job-Search (MadsLorentzen)** — Claude Code agent: evaluate postings, tailor CV, write cover letters, interview prep. 29.6k⭐ MIT, real-world proof (author: 69 apps → 20 interviews → hired Jun 2026). Built for Danish boards but pattern is board-agnostic — swap for our targets. Directly serves Jordan's remote blockchain/cloud role hunt. Source: x.com/0xMarioNawfal list, Aug 4.
- [ ] **WURK.FUN microtasks** — Agent-to-human microtask skill, ready to test
- [ ] **Coinbase for Agents** — Monitoring, validate our stack fits
- [ ] **Cross-chain bridge cost test via agent rails** — Jordan (Aug 6): test whether moving money between chains via agent rails (Across/CCTP + Jupiter) is cheaper than manual bridging. Treasury has the adapters (`solana_bridge_adapter.py`, `gta_solana_leg.py`). Compare agent-rail cost vs manual bridge on Base→Solana USDC. Log results to Treasury.

---

## Completed
- [x] Bitrefill awesome-agentic-payments PR (live at #26)
- [x] KeeperHub Hackathon — added to build queue (July 27)
- [x] Build queue v2 — canonical JSON, tick script, auto handoff
- [x] x402 Gateway v7.0.0 — deployed, verified, audited
- [x] GenTech Cookbook — live in dashboard
- [x] GenTech Travel — live in dashboard
- [x] GenTech Gaming — live in dashboard
- [x] GenTech Finance — live in dashboard
- [x] Quantum-Safe Treasury Phase 1 — hybrid SPHINCS+ signing, circuit breaker, fresh addresses, 39/39 tests
- [x] CLARITY Act compliance badges — all repos tagged, blog post published
- [x] Rugcheck v2 API — rebranded as CLARITY Act Agent Compliance Platform
- [x] SkillSpector YARA rules — 26 rules (549 lines) for x402 payment security
- [x] Revenue Monitor — bug fixed (KNOWN_SERVICES→KNOWN_SENDERS rename)
- [x] Academy Module 4 — Production-Grade x402 Services
- [x] Build Queue visibility page + generator script
