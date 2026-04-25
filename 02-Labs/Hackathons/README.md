# 🏆 Hackathon & Bounty Tracker

**Last updated:** 2026-04-19
**Strategy:** Build once (core agent layer), submit everywhere (swap chain/adapter)

**Legend:**
- `[P]` = Priority — actively building
- `[Q]` = Queue — scoped but waiting on higher priority
- `[X]` = Discard — not pursuing

---

## Active (Deadline Soon) — Ordered by Due Date

- [ ] `[P]` **Solana Frontier + Sidetracks** — May 11 | 💰 $680K+ | Solana | All 5 layers | 🔴 PRIMARY
- [ ] `[P]` **Kite AI Global** — May 11 | 💰 TBA | Kite AI | GenLayer enforcement | 🟡 ACTIVE

## Upcoming

- [ ] `[Q]` **ElevenHacks #6 (Zed + ElevenLabs)** — Apr 23 start | 💰 $10K + credits | Voice AI | 🔲 Build ready — AAE Trading Arena concept locked
- [ ] `[Q]` **ElevenHacks #7 (v0 + ElevenLabs)** — Apr 30 | 💰 $6,780 | Voice AI | ⏳ Upcoming
- [ ] `[Q]` **ElevenHacks #8 (Cursor + ElevenLabs)** — May 7 | 💰 TBD | Voice AI | ⏳ Upcoming
- [ ] `[Q]` **ElevenHacks #9 (Stripe + ElevenLabs)** — May 14 | 💰 $18,980 | Voice AI | ⏳ Upcoming

## Monitor for Future Seasons

- [ ] `[Q]` **Surge Ignition Race** — S1 ended Apr 24 | 💰 $250K | Build-in-public | 👁️ Watch for Season 2 — 300+ founders, perfect for Kite AI / AAE traction demos

## Grants (Rolling)

- [ ] `[P]` **Beam Foundation Grant** — Rolling | 💰 TBD | Beam (AVAX subnet) | 🟡 Draft ready
- [ ] `[P]` **Superteam AE Grant** — Rolling | 💰 ~200 USDG | Solana | 🟢 Part of Frontier
- [ ] `[Q]` **AVAX Retro9000** — Jul 14 | 💰 $75K | Avalanche | L1+Full Stack | 🔵 Planning

## Discarded / Skipped

- [ ] `[X]` **ETHGlobal Open Agents** — May 3 | 💰 $50K | DROPPED — looking for experienced builders, not beginner-friendly
- [ ] `[X]` **ARC Hackathon** — Apr 25 | 💰 $10K | Past deadline / withdrawn
- [ ] `[X]` **ElevenHacks #4 (Kiro + ElevenLabs)** — Apr 20 | 💰 $11,980 | Voting closes too soon, no submission ready
- [ ] `[X]` **ElevenHacks #0-3** | Past | Ended
- [ ] `[X]` **Dev3pack Global** — May 8-10 | 💰 TBA | SKIPPED per Jordan — not registered, unclear prize
- [ ] `[X]` **Nous Hermes Creative** — ~16 days | 💰 $25K | SKIPPED per Jordan

## Grants Applied

*(none yet)*

## Completed

*(none yet)*

---

## Core Reuse Strategy

All submissions share the same 5-layer architecture. Only the **adapter layer** (chain SDK, specific API) changes:

```
┌─────────────────────────────────────┐
│   CORE (reusable everywhere)        │
│   Agents, Registry, Marketplace     │
├─────────────────────────────────────┤
│   ADAPTER (swap per hackathon)      │
│   Solana Anchor / EVM Solidity /    │
│   Kite SDK / specific API           │
└─────────────────────────────────────┘
```

## Sprint Schedule: Focus

```
THIS WEEK (Apr 24-26): KITE AI SPRINT
├── Kite AI Global (Submit Apr 26)
│   ├── Core: AgentEscrow + GenLayer enforcement + Kite chain
│   ├── Dmob: Fix test fixtures, deploy to Kite testnet
│   └── Submit → Kite portal + demo video
└── ElevenLabs Hackathon — scoping + prep

Week of Apr 27 - May 3
├── Norris Research Hackathon — scoping + prep
├── Solana: Start AgentRegistry + JobEscrow (Anchor)
├── ElevenHacks #6 scoping (if pursued)
└── Beam grant polish + submit

Week of May 4-10
├── Solana: Final programs + tests
├── Dev3pack (if pursuing)
├── Demo videos per Frontier sidetrack
└── **May 11: SUBMIT FRONTIER EVERYTHING**
```

---

## Links
- Master Plan: `02-Labs/GenTech-Agent-Economy-Master-Plan.md`
- Layer Architecture: `02-Labs/AAE-Layers-Overview.md`
- Build Plan: `02-Labs/AE-Build-Plan.md`
- Superteam Earn Sidetrack Map: `02-Labs/Hackathons/Superteam-Earn-Sidetrack-Map.md`

---

#hackathon #tracker #index
