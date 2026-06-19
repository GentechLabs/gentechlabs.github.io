# Green Room — Ideas

Ideas from real conversations with real people.

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
