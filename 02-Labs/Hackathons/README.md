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
- [ ] `[P]` **Kite AI Global** — May 17 (extended) | 💰 TBA | Kite AI | GenLayer enforcement | 🟡 ACTIVE

## Upcoming

*(none — focused on May 11 submissions only)*

## Discarded / Skipped

- [ ] `[X]` **ETHGlobal Open Agents** — May 3 | 💰 $50K | DROPPED — looking for experienced builders, not beginner-friendly
- [ ] `[X]` **ARC Hackathon** — Apr 25 | 💰 $10K | Past deadline / withdrawn
- [ ] `[X]` **ElevenHacks #4 (Kiro + ElevenLabs)** — Apr 20 | 💰 $11,980 | Voting closes too soon, no submission ready
- [ ] `[X]` **ElevenHacks #0-3** | Past | Ended
- [ ] `[X]` **Dev3pack Global** — May 8-10 | 💰 TBA | SKIPPED per Jordan — not registered, unclear prize
- [ ] `[X]` **Nous Hermes Creative** — ~16 days | 💰 $25K | SKIPPED per Jordan
- [ ] `[X]` **ElevenHacks #6-9** — Apr 30 / May 7 / May 14 | 💰 ~$36K | SKIPPED per Jordan — focus on Kite AI + Solana Frontier
- [ ] `[X]` **Norris Research Hackathon** | SKIPPED per Jordan

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
THIS WEEK (Apr 24-30): KITE AI + SOLANA FRONTIER SPRINT
├── Kite AI Global
│   ├── Core: AgentEscrow + GenLayer enforcement + Kite chain
│   ├── DMOB: Fix test fixtures, deploy to Kite testnet
│   └── Submit → Kite portal + demo video
└── Solana Frontier
    ├── Start AgentRegistry + JobEscrow (Anchor)
    └── Demo videos per sidetrack

Week of May 4-10
├── Solana: Final programs + tests
├── Kite: Polish + final submission
└── **May 11: SUBMIT BOTH**
```

---

## Links
- Master Plan: `02-Labs/GenTech-Agent-Economy-Master-Plan.md`
- Layer Architecture: `02-Labs/AAE-Layers-Overview.md`
- Build Plan: `02-Labs/AE-Build-Plan.md`
- Superteam Earn Sidetrack Map: `02-Labs/Hackathons/Superteam-Earn-Sidetrack-Map.md`

---

#hackathon #tracker #index
