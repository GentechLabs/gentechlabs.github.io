---
date: 2026-04-25
author: YoYo (Strategies)
tags: [aae, pge, milestone, education, spec]
---

# Personal Goal Engine — Draft Complete

**Status:** Spec drafted, handoffs created, awaiting team pickup  
**Trigger:** Jordan approved "collaborate with team" on education layer + personalized ladders

## What Got Done

1. **Full PGE Spec** written to `03-Strategies/Personal-Goal-Engine-Spec.md`:
   - Goal Profile (8-field onboarding questionnaire)
   - Adaptive Ladder System (personalized 4-tier targets based on starting capital)
   - Learning Modules (10 modules, tier-unlocked)
   - Celebration Engine (8 trigger types, REP rewards)
   - Reflection System (prompts after events)
   - Smart contract structs + functions (ready for DMOB)
   - Front-end integration notes

2. **AAE Signal Spec updated to v2.1** with PGE extension fields (`personal_daily_target`, `celebration_queue`, `reflection_prompt`, etc.)

3. **Handoffs created in Green Room:**
   - `handoff-pge-desmond-content.md` — celebration microcopy, reflection prompts, module outlines
   - `handoff-pge-dmob-contracts.md` — Solidity structs, functions, open questions

## Key Design Decisions

- **Default ladder preserved** as fallback ($5→$20→$55→$200)
- **Personalization scales with starting capital:** zero-capital users get $0.50→$2→$5→$15
- **REP rewards process, not just profit:** module completion, reflections, streaks
- **Losses never deduct REP** — reframe + reflection instead
- **GRS (Goal Readiness Score)** gates access to live vs sandbox mode

## Blockers / Needs Input

- **Priority call:** Where does PGE sit vs Solana Frontier (May 11)? DMOB and Desmond are both loaded with P0 work. Does PGE wait until post-May 11, or do we parallelize?
- **On-chain vs off-chain profile:** Recommend on-chain for composability — DMOB to confirm gas cost acceptable
- **Sandbox mode:** Do we build paper-trading sim or defer to v2?

## Next Steps

1. Desmond picks up celebration copy (lightweight, can fit around other work)
2. DMOB reviews contract spec — confirm structs, estimate gas, decide if PGE waits for post-May 11
3. Jordan reviews full spec and confirms priority

---
*"More winners than losers" — this is the system that delivers it.*
