# 🧠 Green Room — Ideas to Build

> Build first, talk later. Promoted from `11-Mess Hall/ideas.md`.
> Updated: 2026-07-22

---

## 🏆 GenTech DeFi Model — Fine-Tuned Financial AI
**Source:** Jordan brainstorm (Jun 18) | **Status:** Research complete, under $50 to prototype
- Fine-tune DeepSeek R1 Distill 32B on our proprietary DeFi data
- 26 training pairs ready (LP management, yield farming, market analysis, risk, portfolio)
- Scripts written: extract, generate, combine, finetune, run-modal
- **Needs you:** Fund Modal GPU run (~$30-60 USDC on Base)
- Revenue: API key selling, x402 ($0.01-0.05/query), EvoMap Capsules
- **Priority:** 🏆 Milestone — could become "ChatGPT for DeFi"
- [x] Add to build queue as #58

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
