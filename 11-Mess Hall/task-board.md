# Gentech Task Board

*Updated: 2026-04-20 11:45 UTC*

**Rule:** HQ = dispatch. Work happens in departments. Track assignments here.
**Org Chart:** `01-GenTech HQ/Org Chart.md` — see reporting structure and accountability protocol.
**Dashboard:** `01-GenTech HQ/Org Agent Board.html` — interactive visualization of org + tasks + handoffs.

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
- [ ] **[P]** Kite AI Hackathon — 14/14 tests ✅ (fixed daily reset bug) | **Due: Apr 26** | 🟡 Needs demo scope
- [ ] **[Q]** ETHGlobal Open Agents — 0G Storage + KeeperHub integration | **Due: May 3** | ⏳ Pending
- [ ] **[Q]** Dynamic burn rate smart contract feasibility — on-chain revenue tracking, gas optimization | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** claude-obsidian integration evaluation — vault linting, hot cache compatibility | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** Opportunity monitoring cron expansion — grants, audit marketplace, tool alternatives | **Due: TBD** | ⏳ Pending

### Jordan — Sign-ups + Ops (HQ)
- [x] **[P]** Colosseum registration — arena.colosseum.org | **Due: Apr 20** | ✅ Done (Apr 21)
- [ ] **[P]** Google OAuth setup — add test user, paste code | **Due: Apr 20** | ⏳ Pending
- [ ] **[P]** ETHGlobal Open Agents — sign up + claim 0G tokens + KeeperHub API key | **Due: Apr 24** | ⏳ Pending
- [ ] **[Q]** Beam Grant Application — review draft | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** ETHGlobal NY — sign up | **Due: May 30** | ⏳ Pending

### Desmond — Content + Submissions (Entertainment)
- [x] **[X]** ARC submission materials — README, pitch deck, demo script | **Due: Apr 25** | ❌ **CANCELLED** — ARC withdrawn, assets salvaged to `arc-salvage-log.md`
- [ ] **[Q]** Kite AI submission materials — README, demo outline | **Due: Apr 26** | ⏳ Pending
- [ ] **[Q]** ETHGlobal submission materials — README, narrative, demo video script, partner prize apps | **Due: May 3** | ⏳ Pending
- [ ] **[Q]** Gentech evolution documentation — multi-agent story, customizations, originality | **Due: TBD** | ⏳ Pending
- [ ] **[Q]** Bin-AMM content series — explainer thread on LFJ Liquidity Book, why Gentech is building in-house, custom LP visualizations | **Due: Post-hackathon sprint** | ⏳ Pending | Source: Dmob scoping doc (`/root/aae-contracts/docs/bin-amm-scoping.md`)

### YoYo — Research + Strategy (Strategies)
- [ ] **[P]** Beams SDK research — L2 Risk + L3 Brain + L6 Orchestration | **Due: Apr 20** | 🔄 Dmob picking up (consolidated analysis in `02-Labs/Beams-Research.md`)
- [ ] **[Q]** ETHGlobal competitor research — monitor submissions, track sponsor updates | **Due: ongoing** | ⏳ Pending
- [ ] **[Q]** Dynamic burn rate competitive analysis — AgentFi/DeFi parallels | **Due: TBD** | ⏳ Pending

---

## 🟡 WAITING ON TRIGGER

→ *Apr 26: After ARC + Kite submit — full pivot to ETHGlobal Open Agents (Apr 26 → May 3)*
→ *Next ElevenHacks sprint: Watch for announcement (YoYo monitors)*

## ❌ DISCARDED

- [x] **[X]** ElevenHacks #4 (Kiro + ElevenLabs) — missed voting window | ✅ Skipped

## ✅ COMPLETED

- [x] GenLayer SDK deep-dive — 575 lines analyzed | Desmond | Apr 19
- [x] ETHGlobal Open Agents — 44/44 tests passing, 3 contracts + deploy script ready | Dmob | Apr 17
- [x] ETHGlobal Open Agents — DemoScript.s.sol (end-to-end demo flow) | Dmob | Apr 18

---

## Sprint Flow

```
Apr 22-26: Kite ← Dmob codes, Desmond packages  
Apr 26:    Kite SUBMIT
Apr 26-May 3: ETHGlobal ← full team pivot
May 3:     ETHGlobal SUBMIT (4 PM UTC)
```

**NOTE:** ARC hackathon withdrawn (Apr 22). AgentEscrow assets salvaged for other projects.

---

## Department Quick Reference

| Dept | Admin | Group | Domain |
|------|-------|-------|--------|
| **Strategies** | YoYo | Telegram: Strategies | Research, LP, DeFi, market analysis |
| **Labs** | Dmob | Telegram: Labs | Code, contracts, builds, hackathons |
| **Entertainment** | Desmond | Telegram: Entertainment | Content, social, branding, posts |
| **HQ** | Jordan | Telegram: HQ | Dispatch, decisions, coordination |
