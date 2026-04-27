---
date: 2026-04-25
author: YoYo (Strategies)
tags: [academy, pge, education, collaboration]
---

# GenTech Academy + PGE Integration — Status

**Trigger:** Jordan voice memo — "Work with Desmond on learning module scripts, add this to the GenTech Academy."

## What I Found

Desmond already built a **user-facing Academy** at `05-Learning/GenTech-Academy/`:
- 5 completed modules in Foundations tier (Modules 1–5)
- REAP format: Realize → Explain → Act → Prove
- 20-module curriculum roadmap across 4 tiers
- Written for Jordan + rookies, voice-optimized for commute listening

## What I Built

**`02-Labs/PGE-Academy-Modules.md`** — 10 detailed content scripts for the PGE Learning Track:
- Modules 1–3: Scout tier (LP basics, shapes, IL)
- Modules 4–6: Raider tier (DexScreener, multi-shape, gas)
- Modules 7–8: Warlord tier (portfolio, custom ranges)
- Modules 9–10: Sovereign tier (risk management, system building)

Each module includes:
- Opening hook (30 sec)
- Concept breakdowns with live data references
- Interactive elements (simulators, sandboxes, calculators)
- Key takeaways
- REP rewards (10–50 per module)

**Academy curriculum updated** at `02-Labs/Labs_Academy_Curriculum.md`:
- Added Module 3: PGE Mindset Track
- Added Module 4: Content & Communication
- Extended exercise pipeline with "The Simulate" and "The Build"

## Handoff Created

`09-Green Room/handoff-pge-academy-desmond.md`
- Priority review order: Modules 1–3 (first impression), then Module 10 (capstone)
- Asks Desmond for: voice/tone pass, reflection prompts, Jordan story insertion points
- Notes that Desmond's existing 05-Learning modules are the user-facing layer — my scripts are source material

## Reconciliation Strategy

| Layer | Location | Purpose |
|-------|----------|---------|
| User-facing micro-lessons | `05-Learning/GenTech-Academy/` | Desmond's REAP format, 5-min lessons |
| Content scripts / source | `02-Labs/PGE-Academy-Modules.md` | Full scripts, simulators, sandboxes |
| Curriculum map | `02-Labs/Labs_Academy_Curriculum.md` | High-level module mapping + exercise pipeline |

**Decision needed:** Do we:
1. Merge my detailed scripts into Desmond's REAP format for Modules 6–20?
2. Keep my scripts as "instructor edition" and Desmond's as "student edition"?
3. Have Desmond rewrite Modules 1–3 using my scripts as source material?

My recommendation: Option 2. Desmond's REAP format is perfect for users. My scripts are the "director's cut" — source material for building REAP modules, simulators, and sandbox logic. No need to duplicate — just align on what content goes into which tier.

## Next Steps

1. **Desmond** reviews `handoff-pge-academy-desmond.md` — voice/tone pass on Scout tier
2. **Desmond** decides whether to adapt my scripts for Modules 6–20 or maintain his own roadmap
3. **YoYo** available to build the interactive simulators (IL calculator, shape simulator, portfolio builder) as standalone web components
4. **Jordan** — if you want to start learning, Modules 1–3 in `05-Learning/GenTech-Academy/` are ready now

---
*Academy status: Foundations tier complete. Strategy tier in progress. PGE source material drafted and ready for Desmond's review.*
