# Cron Job Consolidation — Option A (May 9, 2026)

**Decision:** Jordan approved Option A — Simple 3-job consolidation.
**Executed by:** Gentech (CEO/Orchestrator)
**Date:** 2026-05-09 ~12:15 UTC

## Problem
30 total cron jobs, with 12 being status update / daily brief type jobs. The Mess Hall alone had 7 sub-jobs (Pre-Shift, Daily Rotation, Mid-Shift, Break 1/2/3, Post-Shift) — most delivering locally so nobody read them. Plus overlapping daily briefs: Master Morning Digest, The Brain Daily, The Brain Review, End of Shift Wrap-Up, Hermes Agent Daily Sync.

## What Changed

### Consolidated (12 → 3)
| Old Job | Status | Replacement |
|---------|--------|-------------|
| Master Morning Digest | ✏️ Enhanced | **Morning Digest** (b006812998df) — now covers DeFi, vault health, agent status, hackathons |
| End of Shift Wrap-Up | ✏️ Replaced | **Evening Wrap-Up** (99432e0f537b) — daily, comprehensive handoff |
| Mess Hall — Daily Rotation | ✏️ Replaced | **Mess Hall Internal** (ee893caf9dad) — absorbs all shift sub-jobs |
| Mess Hall — Pre-Shift | 🔪 Removed | Absorbed into Mess Hall Internal |
| Mess Hall — Mid-Shift | 🔪 Removed | Absorbed into Mess Hall Internal |
| Mess Hall — Break 1 | 🔪 Removed | Absorbed into Mess Hall Internal |
| Mess Hall — Break 2 | 🔪 Removed | Absorbed into Mess Hall Internal |
| Mess Hall — Break 3 | 🔪 Removed | Absorbed into Mess Hall Internal |
| Mess Hall — Post-Shift | 🔪 Removed | Absorbed into Mess Hall Internal |
| The Brain — Daily | ✏️ Demoted | Now "Brain Sync — Weekly" (weekly instead of daily) |
| The Brain Review | 🔪 Removed | Absorbed into Morning Digest |
| Hermes Agent Daily Sync Check | 🔪 Removed | Absorbed into Morning Digest |

### Surviving Jobs (19 total)
**Core briefings (3):**
- Morning Digest (11:30 UTC daily) → HQ
- Evening Wrap-Up (00:00 UTC daily) → HQ
- Mess Hall Internal (03:00 UTC daily) → local

**DeFi/Finance (4):**
- DeFi Milestones (12:15/16:15/20:15 UTC daily) → Strategies
- Protocol Due Diligence Chain (Thursdays) → Strategies
- Portfolio Daily Health Check (12:00 UTC daily) → Strategies
- x402 Ecosystem Monitor (Sundays) → HQ

**Content/Social (3):**
- Security → Content Pipeline (Tue/Fri) → Creative
- Gentech X Content Extractor (17:00 UTC daily) → Creative
- social-briefing (16:00 UTC daily) → Creative

**Infrastructure (5):**
- Gentech Watchdog (*/30 min) → local
- Vault Manager — Nightly Sweep (23:00 UTC daily) → HQ
- Brain Backup → GitHub (22:00 UTC daily) → local
- Provider Usage Monitor (12/18/22 UTC daily) → HQ
- Brain Sync — Weekly (Sundays) → local

**Hackathon/Ops (2):**
- Kite AI Hackathon Submission Check (14:00 UTC daily) → Labs
- hackathon-bounty-monitor (17:00 UTC daily) → HQ

**Admin (2):**
- Weekly Skills Update Check (Sundays) → HQ
- Token Usage Weekly Audit (Sundays) → HQ
