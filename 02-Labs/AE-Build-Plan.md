# 🏗️ AAE Labs Build Plan — April-July 2026

**Last updated:** 2026-04-18
**Strategy:** Each hackathon validates one layer. Retro9000 = full stack on Avalanche.

---

## Sprint 1: Escrow + Marketplace (NOW → Apr 26)
**Targets:** ARC Hackathon, Kite AI

### ARC Hackathon (Apr 25-26) — Escrow Layer
**Contracts exist:** JobEscrow.sol ✅
**What's needed:**
- [ ] Polish JobEscrow for ARC compatibility
- [ ] ARC-specific tests (Circle escrow patterns)
- [ ] Demo: register → post job → escrow → complete → payout
- [ ] 2-min demo video
- [ ] README

### Kite AI (Apr 26) — Marketplace Layer
**Contracts exist:** AgentRegistry.sol, AgentMarketplace.sol ✅
**What's needed:**
- [ ] Adapt for Kite AI chain
- [ ] Agent discovery/search demo
- [ ] Full hire flow (marketplace → escrow)
- [ ] Demo video
- [ ] README

---

## Sprint 2: Brain + Risk Intel (Apr 27 → May 3)
**Target:** ETHGlobal Open Agents ($50K)

### New Contracts Needed
- [ ] **AgentRiskScore.sol** — health checks, performance tracking, risk scoring
- [ ] **AgentBrain.sol** — on-chain memory/learning, evolution tracking

### Deliverables
- [ ] Tests for both contracts
- [ ] Deploy to Sepolia
- [ ] Demo frontend (single HTML, dark theme, ethers.js)
- [ ] 2-min demo video
- [ ] GitHub polish

---

## Sprint 3: Social Layer (May 4 → May 8)
**Target:** Dev3pack Global

### New Contracts Needed
- [ ] **AgentSocialProfile.sol** — on-chain identity, endorsements, reviews

### Deliverables
- [ ] Agent voice introductions (ElevenLabs TTS — 4 voices ready)
- [ ] Social reputation graph demo
- [ ] Demo video
- [ ] README

---

## Sprint 4: Enforcement (May 9 → May 11)
**Target:** Solana Frontier ($230K+)

### New Contracts Needed (Anchor/Solana)
- [ ] **Enforcement program** — slashing, disputes, trust scores
- [ ] Cross-chain bridge concept (Solana enforcement ↔ Avalanche escrow)

### Deliverables
- [ ] Anchor program + tests
- [ ] Cross-chain demo
- [ ] Demo video
- [ ] README

---

## Sprint 5: Full Stack Integration (May 12 → Jul 14)
**Target:** Retro9000 ($75K)

### Integration
- [ ] Layer 1: Fee LP Auto-Balance (new — LFJ integration)
- [ ] Layer 2-5 + Escrow + Social: All prior sprints integrated
- [ ] Deploy to Fuji testnet (May)
- [ ] Deploy to Avalanche mainnet (Jun 1)
- [ ] Generate on-chain activity (Jun 15 - Jul 10)
- [ ] Submit Retro9000 application (Jun 15)
- [ ] Snapshot capture (Jul 14)

---

## Current Status
- 5 contracts live in ~/repos/AAE/
- 24 tests passing
- Deployment plan exists for Retro9000
- **IMMEDIATE FOCUS:** ARC + Kite AI (6-8 days away)

---

## What Jordan Needs To Do
1. **Register** for ETHGlobal Open Agents (if not done)
2. **Confirm** go/no-go on ARC + Kite AI (deadlines are tight)
3. **Fund** deployer wallet for Sepolia gas (ETHGlobal) + Fuji gas (Retro9000)
4. **Approve** this layer-to-hackathon mapping

## What Agents Do
- **D-Mob (Labs):** Build contracts, tests, deploy scripts
- **Desmond (Content):** Demo videos, READMEs, pitch narratives, Twitter/X content
- **YoYo (Strategies):** Research track requirements, judging criteria, competitive analysis
