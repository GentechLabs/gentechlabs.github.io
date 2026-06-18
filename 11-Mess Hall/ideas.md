# Mess Hall — Ideas

Ideas from real conversations with real people.

---

## [ ] 🏆 GenTech DeFi Model — Fine-Tuned Financial AI
- **Added:** 2026-06-18
- **Source:** Jordan brainstorming session → "We could train our own decentralized model"
- **What:** Fine-tune an open-source LLM on our proprietary DeFi data to create a specialized financial advisor model
- **Training data:** LP position history, fee patterns, IL scenarios, market reactions (FOMC, narrative rotations), yield farming decisions, dashboard metrics
- **Top models to fine-tune:**
  - DeepSeek R1 Distill (32B) — $30-60 via QLoRA, 85%+ MATH, reasoning-focused
  - Qwen3 (30B-A3B) — $20-40 via QLoRA, efficient MoE
  - DeepSeek V3.2 (685B) — $50-100 via QLoRA, best open math (90.2%)
- **Revenue model:** 
  - **API Key Selling** (validated by Tao) — sell access to our fine-tuned model via API keys. Other agents pay to query our model for DeFi intelligence.
  - **x402 Micropayments** ($0.01-0.05/query) — pay-per-use, no account needed
  - **EvoMap Capsules** — publish model as Capsule, earn credits per use
  - **Agent Kit Skill** — bundle into premium skill, one-time purchase ($10-50)
- **The flywheel:** Our data → train model → model attracts users → more data → better model
- **External access:** Anyone can use GenTech's DeFi intelligence without running our full agent stack
- **Status:** Research complete. Ready to prototype fine-tune with existing vault data for under $50.
- **Priority:** 🏆 Milestone (could become core GenTech product — "ChatGPT for DeFi")
- **Connection:** Complements Agent Kit (AI layer), EvoMap (distribution), Sana (spending earnings)

---

## [ ] GenTech Wallet + Sana Integration
- **Added:** 2026-06-18
- **Source:** @sanafionchain tweet → "Agentic Economy Stack"
- **What:** Integrate Sana's banking/card infrastructure into GenTech Agent Kit wallet
- **Sana provides:** Visa/Mastercard, bank accounts, KYC compliance, fiat on/off ramp
- **GenTech provides:** Crypto wallet, DeFi yield farming, x402 micropayments, USDC earning engine
- **Combined value:** "Your agent earns yield. You spend it anywhere with a card."
- **Status:** Research needed — evaluate Sana's API, licensing, fees
- **Priority:** High (completes the full earn → store → spend loop)

---

## [ ] EvoMap Integration
- **Added:** 2026-06-18
- **Source:** YouTube (James Pelton) → evomap.ai
- **What:** "AI Self-Evolution Infrastructure" — agent experience marketplace where agents publish learned patterns as reusable "Capsules" and earn credits/reputation
- **Stats:** 190.7B tokens saved, 1.1M assets published, 96.24% search hit rate
- **Integration path:** Register as node (free, 100 starter credits), publish our proven patterns (DeFi monitoring, dashboard templates, portfolio sync), earn revenue when others use them
- **Evolver CLI:** `npm install -g @evomap/evolver` → register, heartbeats, task claiming, publishing
- **Why:** Perfect alignment with Agent Kit philosophy ("one learns, all inherit"). Could be distribution channel for GenTech modules + passive income stream
- **Connection:** Multi-platform token strategy (Bankr, Swarms, Hive, EvoMap)
- **Status:** Research complete. Ready to register and test with 2-3 Capsules.
- **Priority:** Medium-High (natural extension of swarm/marketplace strategy)

---

## [ ] GenTech Agent Kit Installer
- **Added:** 2026-06-16
- **Source:** Jordan voice message
- **What:** One-click desktop installer for Windows/Mac/Linux that packages Hermes + GenTech profile + skills + cron jobs + dashboard
- **Why:** Makes the Agent Kit distributable. Hard to copy because it's tied to local Hermes setup.
- **Layers to include:**
  - Hermes Agent CLI auto-install
  - Pre-loaded GenTech skills and cron jobs
  - Wallet setup wizard
  - DeFi dashboard + LP monitor
  - GitHub backup/sync config
  - Skill marketplace / installer
  - Agent health dashboard
- **Target user:** Power users and hackathon builders who want their own agent running locally
- **Status:** Concept — needs spec
- **Priority:** High (builds on current work)

---

## [ ] Education Layer — Tutors
- **Added:** 2026-06-12
- **Source:** Jordan's conversation with Cara at work
- **Problem:** Cara's son has trouble learning. Needs something visual and engaging.
- **Solution:** Dashboard where you can visually create learning content. Something pleasing for kids or adults.
- **Status:** Concept. Add to GenTech Suite as Tutors layer.
- **Connection:** GenTech Suite: Journal, Cookbook, **Tutors**, Gaming, Travels

---

## [ ] GenTech Suite — Full Vision
- **Added:** 2026-06-12
- **Layers:**
  - 🍳 Cookbook — food, recipes, cooking (Christel) ✅ LIVE
  - 📓 Journal — reflections, feelings, daily life (Jordan, Christel)
  - ✈️ Travel — trips, planning, restaurants (Jordan) ✅ LIVE
  - 🎮 Gaming — characters, builds, progression (Jordan, Vanito) ✅ LIVE
  - 💰 Finance — portfolio, yields, DeFi (Jordan) ✅ LIVE
  - 🎓 Tutors — learning, education, visual content (Cara's son) — Spec: ideas/education-layer-tutors.md
  - 🏆 Milestones — achievements, badges, prediction market — Spec: ideas/milestone-layer-achievements.md
  - 🎳 Activity/Hobby — animated achievements, scores, streaks — Spec: ideas/activity-hobby-layer.md
  - 🔧 Custom — user-defined dashboards, template marketplace — Spec: ideas/custom-layer-user-defined.md
- **Pricing:** Free (10/day), $5/mo single layer, $20/mo Agent Pass
- **Status:** Building. First profiles live. 4 specs written (Tutors, Milestones, Activity/Hobby, Custom).

---

## [ ] Agent-to-Human Microtasks (WURK.FUN)
- **Added:** 2026-06-11
- **Source:** Twitter/X post
- **What:** Hire humans for feedback, content, social proof via x402
- **Status:** Integrated. Skill created. Ready for testing.

---

## [ ] Coinbase for Agents
- **Added:** 2026-06-11
- **Source:** Twitter/X post
- **What:** Agent accounts, x402 payments, portfolio management
- **Status:** Monitoring. Validates our stack.

---

## [ ] Decentralized Travel Community — Agent Economy
- **Added:** 2026-06-14
- **Source:** Jordan inspired by PassportBros / Jeffrey AI
- **Problem:** PassportBros has 30K+ travelers but it's centralized — no ownership, no portability, no crypto rails
- **Solution:** Decentralized travel intelligence network with ERC-8004 identity, x402 micropayments, agent-augmented intel, on-chain reputation
- **Status:** Idea. Full spec: ideas/decentralized-travel-community.md
- **Hackathon fit:** Lepton (Jun 29) — Circle + Arc for x402 micropayments
- **Connection:** GenTech Suite: Travel layer + AAE positioning

---

## [ ] GenTech Suite — Unified Architecture
- **Added:** 2026-06-14
- **Source:** Jordan — "Travel is awesome, ties with Cookbook, agent economy"
- **Vision:** Everything connects through dashboard engine. Travel intel → Cookbook recipes → Agent economy
- **Key insight:** Food + Travel are natural partners. "Best pad thai in Bangkok" = Intel + Recipe + Price + Booking
- **Status:** Spec written. ideas/gentech-suite-unified-architecture.md
- **Hackathon fit:** Lepton (Jun 29) — unified travel + food intelligence
- **Connection:** GenTech Suite: Travel + Cookbook + Dashboard + AAE

---

## Compound vs. Extract Protocol (Flagship DeFi Module)
- **Added:** Jun 17, 2026
- **What:** LP profit extraction without closing position — compound or extract fees while keeping position active
- **Why:** Separates AAE from every other DeFi platform. Bankr/GOAT have basic tools, we have the AI brain.
- **Spec:** `09-Green Room/ideas/compound-extract-protocol.md`
- **Architecture:** `02-Labs/compound-extract/ARCHITECTURE.md`
- **Status:** SPEC COMPLETE → Building in Labs
- **Priority:** HIGH — Flagship Agent Kit DeFi module
- **Build timeline:** 2 weeks MVP, 6 weeks full product

---

## Agent Rug 2.0 — Agent Security Platform
**Added:** Jun 15, 2026
**Status:** Brainstorm

### Vision
Expand Agent Rug from malicious token scanner to full agent security platform.

### Core Layers
1. **Agent Verification** — Scan code for malware, drain patterns, suspicious permissions
2. **Contract Verification** — Match deployed contract to claimed source code
3. **Variant Detection** — Find hidden backdoors in "legitimate" agents

### Features
- Platform-based risk scoring (which launchpads are dangerous?)
- Contract age + behavior analysis
- Drain pattern detection (approvals, transfers, swaps)
- Community reputation tracking
- Real-time threat intelligence dashboard
- Draining event tracking
- Liquidation alerts
- Quantum readiness scores
- Attack pattern database

### Use Cases
- BYOS users verifying untrusted agents
- DeFi traders checking token safety
- Protocol teams auditing integrated agents
- Security researchers tracking attack patterns

### Revenue Angle
- Freemium: Basic scans free, deep scans paid
- Enterprise: Protocol integration API
- Data: Threat intelligence feeds

### Next Steps
- [ ] Research existing agent security tools
- [ ] Map attack vectors (wallet drainers, approval abusers, etc.)
- [ ] Design verification pipeline
- [ ] Build prototype for Agent Kit integration

---

## [ ] 🏆 Agent Kit v2 — Modular Agent Framework
- **Added:** 2026-06-18
- **Source:** Jordan brainstorming session → "What improvements for Agent Kit?"
- **What:** Modular, composable, self-healing agent framework that anyone can install, configure, and extend
- **Key features:**
  - **Modular Skill System** — Core + optional modules (defi, content, research, marketplace)
  - **Auto-Detection** — Detects Hermes, BlockRun, Obsidian, GitHub, Telegram and adapts
  - **Identity Persistence** — JSON-based identity survives session restarts
  - **Skill Marketplace** — Publish/install skills, earn credits, revenue sharing
  - **Health Dashboard** — Cron jobs, skills, memory, performance, platform status
  - **Multi-Profile** — One install, multiple agents (defi, content, research)
  - **Auto-Update** — Semantic versioning, rollback support
  - **Pre-Built Templates** — DeFi Farmer, Content Creator, Research Agent
  - **Documentation Site** — docs.gentech.dev with API reference
- **Revenue model:**
  - Free skills: 0 credits
  - Paid skills: 1-100 credits
  - Kit gets 10% platform fee
  - Auto-payout weekly (credits → USDC on Base)
- **Implementation roadmap:**
  - Phase 1 (Week 1-2): Core — modular layout, auto-discovery, identity persistence
  - Phase 2 (Week 3-4): Marketplace — skill packages, publish/install, credits
  - Phase 3 (Week 5-6): Operations — health dashboard, multi-profile, updates
  - Phase 4 (Week 7-8): Distribution — templates, docs site, community, launch
- **Success metrics:**
  - Install size (core) < 10MB
  - Startup time < 5s
  - 50+ marketplace skills in 3 months
  - 100+ active installations in 6 months
  - $500/mo revenue in 6 months
- **Spec:** `02-Labs/agent-kit/AGENT-KIT-V2-SPEC.md`
- **Status:** Spec complete → Ready to build
- **Priority:** 🏆 Milestone (core product for GenTech ecosystem)
- **Connection:** Complements Agent Kit (core), EvoMap (marketplace), Sana (revenue payouts)

---

## [ ] DeFi Model Training Pipeline — Ready for Sunday
- **Added:** 2026-06-18
- **Source:** Jordan brainstorming session → "How do we pay for training?"
- **What:** Complete training pipeline for fine-tuning DeepSeek R1 Distill 32B on DeFi data
- **Training data:**
  - 26 pairs total (5 LP management, 5 yield farming, 5 market analysis, 5 risk management, 5 portfolio optimization, 1 vault extraction)
  - Sources: Vault extraction + synthetic generation
- **Payment:** BlockRun Modal (USDC on Base, ~$30-60 for 1 hour on A10G GPU)
- **Scripts ready:**
  - `extract-training-data.py` — Extracts training pairs from vault
  - `generate-synthetic-data.py` — Generates synthetic DeFi Q&A pairs
  - `combine-training-data.py` — Combines all sources into final dataset
  - `finetune.py` — QLoRA fine-tuning script
  - `run-modal.py` — Modal runner for GPU training
- **Timeline:**
  - Jun 18-19: Prep training data ✅ (26 pairs ready)
  - Jun 22 (Sunday): Run fine-tune (need funds)
  - Jun 23-24: Test and deploy
  - Jun 25: Publish to EvoMap + API endpoint
- **Status:** Training data ready → Waiting for Sunday funding
- **Priority:** 🏆 Milestone (part of GenTech DeFi Model)
- **Connection:** Complements Agent Kit v2 (distribution), EvoMap (marketplace), Sana (revenue)
