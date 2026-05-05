# Handoff: Zerion CLI Sidetrack — PRIORITY LOCKED
**From:** Desmond (Creative)
**To:** DMOB (Labs)
**Date:** May 5, 2026
**Status:** 🔴 ACTIVE — Start tomorrow

---

## Decision
**Jordan locked in Option B: Zerion CLI ($5K bounty)**

This is now our **primary sidetrack**. Drop other sidetrack research and focus here.

---

## What Zerion CLI Needs
**Bounty:** $5,000
**Deliverable:** Agent that auto-discovers and delegates tasks via CLI

### Core Requirements
1. **CLI tool** that connects to Zerion API
2. **Auto-discovery** — scans for DeFi opportunities, portfolio actions, yield farming
3. **Task delegation** — agent can execute or recommend actions
4. **Clean UX** — should feel like a real product, not a hackathon demo

### Technical Notes
- Zerion has API endpoints for portfolio data, DeFi positions, token info
- Need to research exact API surface (auth, rate limits, endpoints)
- CLI framework: likely Node.js or Python with click/typer
- Agent logic: rule-based + LLM-assisted for complex decisions

---

## Sprint Timeline
| Day | Date | DMOB Deliverable |
|-----|------|-----------------|
| 2 | May 6 | Scaffold project, Zerion API research + integration |
| 3 | May 7 | Core task discovery + delegation logic |
| 4 | May 8 | Polish, error handling, CLI UX |
| 5 | May 9 | Final testing, bug fixes |
| 6 | May 10 | Submit |

---

## What I Need From You
1. **Today:** Acknowledge this handoff
2. **Tomorrow (May 6):** Start scaffolding — project structure, API research
3. **Day 3:** Have core functionality working
4. **Day 4-5:** Polish + test

I'll handle the submission docs (README, writeup, pitch) starting Day 4.

---

## Video Demo
Jordan is experimenting with local Hermes + Hagen + video agent tomorrow. If that works, we'll use it for a killer demo. Fallback is screen recording + voiceover.

**Don't wait on the video** — focus on the CLI build. Video is Jordan's domain.

---

## Context
- Sprint plan saved: `02-Labs/Hackathons/Active/sidetrack-sprint.md`
- Previous sidetrack research in vault (Zerion, GoldRush, Agentic Engineering, Dune)
- Main track (Hermes) is separate — don't conflate

---

**Desmond**
*Head of Creative, Gentech*
