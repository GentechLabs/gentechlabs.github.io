# 🧠 Green Room — Ideas to Build

> Build first, talk later. Promoted from `11-Mess Hall/ideas.md`.
> Updated: 2026-07-22

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

## Ready to Test (skills exist, need execution)
- [ ] **WURK.FUN microtasks** — Agent-to-human microtask skill, ready to test
- [ ] **Coinbase for Agents** — Monitoring, validate our stack fits

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
