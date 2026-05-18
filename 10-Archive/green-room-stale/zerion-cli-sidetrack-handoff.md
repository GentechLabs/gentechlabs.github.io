# Handoff: Sidetrack Adapters — PRIORITY LOCKED
**From:** Desmond (Creative)
**To:** DMOB (Labs)
**Date:** May 5, 2026
**Status:** 🔴 ACTIVE — Start tomorrow

---

## Decision
**Jordan locked in Option B: Zerion CLI ($5K) + GoldRush ($3K)**

This is now our **primary sidetrack work**. Both adapters are thin wrappers — build main submission first, adapters last 2 days.

---

## What We're Building

### Adapter 1: Zerion CLI ($5K bounty)
**Deliverable:** Agent that auto-discovers and delegates tasks via CLI

Core Requirements:
1. CLI tool that connects to Zerion API
2. Auto-discovery — scans for DeFi opportunities, portfolio actions, yield farming
3. Task delegation — agent can execute or recommend actions
4. Clean UX — should feel like a real product, not a hackathon demo

### Adapter 2: GoldRush/Covalent ($3K bounty)
**Deliverable:** Agent risk dashboard with on-chain data feed

Core Requirements:
1. Dashboard that pulls real-time position data via GoldRush API
2. Risk scoring for agents based on on-chain activity
3. Feed into AgentEscrow reputation system
4. Visual dashboard showing agent health metrics

---

## Technical Details
- **Full adapter specs:** `09-Green Room/active-handoffs/sidetrack-adapter-specs.md`
- **Zerion API:** developers.zerion.io — HTTP Basic Auth, TypeScript SDK
- **GoldRush API:** goldrush.mintlify.app — API key, TypeScript SDK (`@covalenthq/client-sdk`)
- **Both support Solana** ✅

---

## Sprint Timeline
| Day | Date | DMOB Deliverable |
|-----|------|-----------------|
| 2 | May 6 | Register for API keys, scaffold both adapter projects |
| 3 | May 7 | Zerion: task discovery + CLI delegation. GoldRush: risk scoring + health |
| 4 | May 8 | Polish both, error handling, end-to-end testing |
| 5 | May 9 | Final testing, bug fixes |
| 6 | May 10 | Submit both sidetracks |

---

## What I Need From You
1. **Today:** Acknowledge this handoff
2. **Tomorrow (May 6):** Register for both API keys, scaffold both projects
3. **Day 3:** Have core functionality working for both adapters
4. **Day 4-5:** Polish + test

I'll handle the submission docs (README, writeup, pitch) starting Day 4 for both sidetracks.

---

## Video Demo
Jordan is experimenting with local Hermes + Hagen + video agent tomorrow. If that works, we'll use it for a killer demo. Fallback is screen recording + voiceover.

**Don't wait on the video** — focus on the adapter builds. Video is Jordan's domain.

---

## Context
- Sprint plan saved: `02-Labs/Hackathons/Active/sidetrack-sprint.md`
- Adapter specs: `09-Green Room/active-handoffs/sidetrack-adapter-specs.md`
- Previous sidetrack research in vault (Zerion, GoldRush, Agentic Engineering, Dune)
- Main track (AgentEscrow) is separate — don't conflate

---

**Desmond**
*Head of Creative, Gentech*
