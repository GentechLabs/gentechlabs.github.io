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

**NOTE:** All other hackathons dropped (Apr 25). Focus narrowed to W21 active builds.

---

## Department Quick Reference

| Dept | Admin | Group | Domain |
|------|-------|-------|--------|
| **Strategies** | YoYo | Telegram: Strategies | Research, LP, DeFi, market analysis |
| **Labs** | Dmob | Telegram: Labs | Code, contracts, builds, hackathons |
| **Entertainment** | Desmond | Telegram: Entertainment | Content, social, branding, posts |
| **HQ** | Jordan | Telegram: HQ | Dispatch, decisions, coordination |
