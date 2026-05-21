# 💡 Green Room — Ideas

<!-- Checkbox list of things to explore. Check when done, move to archive when stale. -->

## Agent Economy Platforms (Participation + Revenue)

- [ ] **Bankr Agent Launch** (Added May 21)
  - Purpose: Learn the game by playing it — revenue + intel + community presence
  - What we get: token launch fees, swap fees, UX gap intelligence, user empathy
  - Strategy: participate now, build the better version for AAE
  - Status: Queued — research onboarding flow, timeline, requirements

- [ ] **Swarms Launchpad Monetization** (Added May 21)
  - Purpose: Get listed + monetized on Swarms marketplace
  - Runbook ready: `09-Green Room/runbooks/swarms-acm-runbook.md`
  - Deadline: May 27, 2026 (hackathon submission)
  - Status: Queued — execute runbook (token launch → marketplace publish → demo → submit)

## Hackathons & Bounties

- [ ] **Superteam Solana Bounty** (Added May 14)
  - Category: Autonomous on-chain agent workflows
  - Stack: SAP (identity), x402 payments, OOBE + Ace
  - Prize: $2,400 across two categories
  - Status: Needs deadline research — add to roster if 5+ days remaining
  - Priority: Research deadline, then decide

- [ ] **Arbitrum Open House London** (Added May 18)
  - Buildathon: Started May 25, online 3 weeks
  - Founder House: July 10-12, London (in-person)
  - Prize: $415K total ($70K buildathon + $120K founder house + $30K grants + $195K Robinhood Chain)
  - AI Agentic Category: $15K buildathon + $20K founder house
  - Fit: DeFi Signal Agent → AI Agentic track
  - Priority: HIGH — deadline approaching, strong alignment

- [ ] **Mantle Turing Test 2026** (Added May 18)
  - Phase II deadline: June 15, 2026
  - Prize: $120K+ ($100K Phase II + $20K Phase I)
  - Tracks: AI Trading & Strategy, Agentic Economy, AI × RWA
  - Fit: DeFi Signal Agent → AI Trading or Agentic Economy
  - Priority: HIGH — 27 days to deadline, natural fit

## Product Ideas

- [ ] **Voice-Cloned Learning Companions** (Added May 21)
  - ADHD-focused education vertical — voice clone teaches via kid's interests
  - Market: 6.1M ADHD kids in US, $20B AI education market by 2027
  - First case study: Christel's 10-year-old son (awaiting interests/profile)
  - DeFi angle: stablecoin subs → learn-to-earn → tutor marketplace → full DeFi stack
  - Design doc: `09-Green Room/designs/voice-cloned-learning-companions.md`
  - Status: Awaiting Christel's input on son's interests + education profile
  - Priority: HIGH — real user, real need, first-mover advantage in voice + neurodivergent

- [ ] **Voice-first travel agent** — expand Let's FG into a paid service
- [ ] **Agent payment router** — x402 protocol for recurring agent payments
- [ ] **Agent Repairathy** (Added May 19)
  - Slogan: "I've built the agents to help repair you, to help get you back on track."
  - Therapeutic Layer (Layer 10 or 11 in multi-agent stack)
  - Emotional wellness companion — daily check-ins, journaling, habit nudging, emotional baseline tracking
  - Market: AI therapy apps $50B by 2028, 100M+ users
  - Competitors: Ash (talktoash.com, launched May 11), AVA CALM (launched May 11)
  - Risk: Illinois/Nevada banned AI psychotherapy — position as wellness/coaching, not therapy
  - Hackathon fit: QVAC (privacy-first local AI), Google Cloud Rapid Agent, Arbitrum Open House
  - Status: Concept phase — need to define Layers 1-9, choose target hackathon

## Gaming (Side Projects)

- [ ] **AI Companions in Gaming** (Added May 18)
  - Market: AI companion apps $220M+ in 2025, up 64% YoY
  - Revenue per download doubled ($0.52 → $1.18), Character.AI hit $500M annual
  - Gap: Most AI companions are text-based chat; gaming-specific companions barely touched
  - Use case: In-game AI companions for NPC interaction, strategy, narrative
  - Status: Watch for Web3 gaming hackathons — build when opportunity aligns

## Browser Cloaking Infrastructure (Added May 21, 2026)

- [ ] **Multi-chain browser fingerprinting & wallet isolation** (Non-Solana chains)
  - Krexa's browser tooling covers Solana — that's primary for v1
  - Base, Somnia, and other EVM chains need custom fingerprinting + wallet isolation
  - No one else has built this — potential first-mover advantage
  - Use case: agent wallet isolation, anti-detection, per-chain session management
  - Status: Future roadmap item — not hackathon priority, but worth building when we expand beyond Solana
  - Competitive moat: cross-chain browser cloaking doesn't exist as a product yet

## AAE LP Management (May 16, 2026)

- [ ] **Subscription tier differentiation — Autonomous LP Defense**
  - Free tier: static range, manual rebalance, basic alerts (set & hope)
  - Paid tier: active defense — knife-fall detection → auto-exit to USDC → support/resistance discovery → autonomous re-entry
  - Core value prop: the "brain layer" that manages risk vs. just reporting it
  - Differentiation: most LP tools are passive dashboards; AAE acts autonomously
  - Trigger rules: "check every 10min, confirm breakdown over 5min, then execute"
  - Status: Validated against real market event (AVAX drop below $9.30 range floor)

## AAE Infrastructure Plays

- [x] **AAE Credit Layer — Infrastructure** (Added May 21)
  - Concept: Cross-chain credit/reputation layer for autonomous agents
  - Pitch: "Chainlink gives prices. We give trust scores."
  - Components: agent credit scoring, on-chain reputation, lending/borrowing between agents, risk assessment
  - Moat: First-mover in cross-chain reputation portability (t54 does credit, we do trust)
  - Revenue: Score API access, premium data, score licensing, dispute fees
  - Status: ✅ Research complete (Pyth, UMA, Chainlink CCIP, ERC-8004, competitive landscape)
  - Architecture doc: `09-Green Room/designs/aae-credit-layer-infra.md`
  - Key finding: Don't build ON Pyth, build LIKE Pyth (pull oracle pattern). UMA OOv3 for disputes. CCIP for cross-chain delivery. ERC-8004 for identity layer.
  - Priority: HIGH — ready for Phase 2 (plan) when Jordan greenlights build

## AEG — Agent Economy Gaming (Added May 21)

- [x] **Phase 1 MVP Built** (May 21)
  - Repo: github.com/ProtoJay4789/AEG
  - Engine: MarketEngine, Portfolio, ReputationManager, GasPenaltyManager, BotAdvisor
  - UI: Dark theme trading dashboard, canvas chart, bot advisor chat
  - Tests: 53/53 passing
  - Status: Phase 1 complete — ready for Phase 2 (leverage mechanics, advanced bots, multiplayer)
