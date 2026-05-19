# Gentech Task Board

## 📄 Communication Protocol

**HQ = Default conversation space.** All general chat, alerts, and cross-team coordination happens here.

**Specialized groups = Work only.** Labs, Entertainment, Strategies groups are for focused workstreams. No general chat in those groups.

**Smart Routing:**
- Route work to specialized groups when it requires focused execution
- Keep alerts, quick questions, and coordination in HQ
- Green Room = war room during active work sessions
- Mess Hall = status updates and stopping points

**Enforcement:** Cron job `d31c330959de` (Handoff Enforcement Monitor) runs every 15 min. ACK deadline: 5 min. Escalation: 15 min. Stalled: 24h. Agents must check green room before responding — no exceptions.

## Markers
- **[P]** Priority — active sprint, deadline approaching
- **[X]** Discard — skipped or dropped
- **[Q]** Queue — valid but no deadline, waiting for trigger

## Status
- ⏳ Pending | 🔄 In-Progress | ✅ Done | ❌ Cancelled

---

## 🔴 ACTIVE SPRINT — Week of Apr 20

*One build, three pitches. Same code, different narratives.*

### Dmob — Code (Labs)
- [x] **[X]** ARC Hackathon — AgentEscrow + x402 nanopayments | **Due: Apr 25** | ❌ **WITHDRAWN (Apr 22)** — see `arc-salvage-log.md`
- [ ] **[P]** **Solana Frontier** — PRIMARY focus. Identify tracks, build plan, start execution | **Due: May 11** | 🟥 **ACTIVE**
- [ ] **[P]** **Kite AI Hackathon** — PRIMARY focus alongside Solana Frontier | **Due: May 11** | 🟥 **ACTIVE**
- [x] **[X]** ETHGlobal Open Agents — DROPPED. Assets salvaged to `10-Archive/Salvaged-Assets/ethglobal-patterns/`. Focus on Solana Frontier.
- [x] **[X]** Nous Hermes Creative — SKIPPED per Jordan
- [x] **[X]** Dev3pack Global — SKIPPED per Jordan
- [x] **[X]** Norris Research Hackathon — SKIPPED per Jordan (Apr 25)
- [x] **[X]** ElevenHacks #6-9 — SKIPPED per Jordan (Apr 25)
- [x] **[X]** GenLayer Builder — PAUSED per Jordan (Apr 25), may resume post-May 11
- [ ] **[Q]** Dynamic burn rate smart contract feasibility — on-chain revenue tracking, gas optimization | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** claude-obsidian integration evaluation — vault linting, hot cache compatibility | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** Opportunity monitoring cron expansion — grants, audit marketplace, tool alternatives | **Due: TBD** | ⏳ Pending

### HQ / Cross-Team
- [ ] **[P]** **Platform Orchestration Thesis** — agent brainstorm on network effects, ecosystem integration, squad monetization | **Due: Apr 25** | 🟡 Agents pinged (Strategies, Labs, Entertainment)

### Jordan — Sign-ups + Ops (HQ)
- [x] **[P]** Colosseum registration — arena.colosseum.org | **Due: Apr 20** | ✅ Done (Apr 21)
- [ ] **[P]** Google OAuth setup — add test user, paste code | **Due: Apr 20** | ⏳ Pending
- [x] **[X]** ETHGlobal Open Agents — sign up + claim 0G tokens + KeeperHub API key | **Due: Apr 24** | ❌ **DROPPED** — not beginner-friendly
- [ ] **[Q]** Beam Grant Application — review draft | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** ETHGlobal NY — sign up | **Due: May 30** | ⏳ Pending

### Desmond — Content + Submissions (Entertainment)
- [x] **[X]** ARC submission materials — README, pitch deck, demo script | **Due: Apr 25** | ❌ **CANCELLED** — ARC withdrawn, assets salvaged to `arc-salvage-log.md`
- [ ] **[Q]** Kite AI submission materials — README, demo outline | **Due: May 11** | ⏳ Pending
- [x] **[X]** ETHGlobal submission materials — DROPPED. See `10-Archive/Salvaged-Assets/ethglobal-patterns/`.
- [ ] **[Q]** Surge Ignition Race — monitor Season 2 launch, prepare GenTech Hub profile | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** Gentech evolution documentation — multi-agent story, customizations, originality | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** Bin-AMM content series — explainer thread on LFJ Liquidity Book, why Gentech is building in-house, custom LP visualizations | **Due: Post-hackathon sprint** | ⏳ Pending | Source: Dmob scoping doc (`/root/aae-contracts/docs/bin-amm-scoping.md`)

### YoYo — Research + Strategy (Strategies)
- [ ] **[P]** Beams SDK research — L2 Risk + L3 Brain + L6 Orchestration | **Due: Apr 20** | 🔄 Dmob picking up (consolidated analysis in `02-Labs/Beams-Research.md`)
- [ ] **[Q]** ETHGlobal competitor research — monitor submissions, track sponsor updates | **Due: ongoing** | ⏳ Pending
- [ ] **[Q]** Dynamic burn rate competitive analysis — AgentFi/DeFi parallels | **Due: TBD** | ⏳ Pending

---

## 🟢 WAITING ON TRIGGER

→ *May 11: Kite AI + Solana Frontier submission deadlines*

---

## 🟥 ACTIVE SPRINT — Week of May 19 (W21)

*Post-Kite AI. Focus on active hackathons with approaching deadlines.*

### Priority Hackathons

- [ ] **[P]** **Agora Agents ($50K)** — PRIMARY active build | **Due: May 25** | 🟥 6 days
- [ ] **[P]** **Arbitrum Open House ($415K)** — Registration due May 25 | **Due: May 25** | 🟥 6 days
  - AI Agentic track: $15K buildathon + $20K founder house
  - Fit: DeFi Signal Agent → AI Agentic
- [ ] **[Q]** **Mantle Turing Test 2026 ($120K+)** — Phase II | **Due: Jun 15** | 🟡 27 days
  - Tracks: AI Trading & Strategy, Agentic Economy
  - Fit: DeFi Signal Agent → AI Trading or Agentic Economy
- [ ] **[Q]** **Swarms ACM** — May 27 | 🟢 Monitor
- [ ] **[Q]** **Bags FM** — Jun 1 | 🟢 Monitor
- [ ] **[Q]** **Superteam Solana Bounty ($2.4K)** | 🟢 Needs deadline research

### Completed Builds

- [x] **AgentCash** — x402 payment discovery layer | Built May 19 | ✅ Complete
  - Registry + marketplace for API providers with x402 pricing
  - Next.js 14 + SQLite + ampersend SDK
  - Consider for Agora/Arbitrum submission angle

### Kite AI Status

- [x] **Kite AI Hackathon** — Deadline May 17 passed | 🟡 Awaiting results

## ❌ DISCARDED

- [x] **[X]** ElevenHacks #4 (Kiro + ElevenLabs) — missed voting window | ✅ Skipped
- [x] **[X]** ElevenHacks #6-9 (Zed / v0 / Cursor / Stripe × ElevenLabs) — SKIPPED per Jordan (Apr 25) — focus restraint
- [x] **[X]** Norris Research Hackathon — SKIPPED per Jordan (Apr 25)

## ✅ COMPLETED

- [x] GenLayer SDK deep-dive — 575 lines analyzed | Desmond | Apr 19
- [x] ETHGlobal Open Agents — 44/44 tests passing, 3 contracts + deploy script ready | Dmob | Apr 17
- [x] ETHGlobal Open Agents — DemoScript.s.sol (end-to-end demo flow) | Dmob | Apr 18

---

## Sprint Flow

```
Apr 25-May 11: Kite AI + Solana Frontier ← Dmob codes, Desmond packages
May 11:    SUBMIT BOTH
```

**NOTE:** All other hackathons dropped (Apr 25). Focus narrowed to two submissions.

---

## Department Quick Reference

| Dept | Admin | Group | Domain |
|------|-------|-------|--------|
| **Strategies** | YoYo | Telegram: Strategies | Research, LP, DeFi, market analysis |
| **Labs** | Dmob | Telegram: Labs | Code, contracts, builds, hackathons |
| **Entertainment** | Desmond | Telegram: Entertainment | Content, social, branding, posts |
| **HQ** | Jordan | Telegram: HQ | Dispatch, decisions, coordination |
