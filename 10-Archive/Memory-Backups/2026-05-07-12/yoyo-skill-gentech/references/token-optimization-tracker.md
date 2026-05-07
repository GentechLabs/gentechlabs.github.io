# Token Optimization Tracker

## Purpose
Track token usage and savings from the orchestrator pattern implementation.

## Baseline Metrics (Pre-Implementation — 2026-05-07)

### Cron Jobs by Agent
| Agent | Total Jobs | Active | Failing |
|-------|-----------|--------|---------|
| YoYo | 4 | 1 | 3 |
| DMOB | 8 | 3 | 5 |
| Desmond | 3 | 1 | 2 |
| Gentech | 31 | ~15 | ~16 |
| **Total** | **46** | **~20** | **~26** |

### Duplicate DeFi Milestone Jobs
- YoYo: Every 10 min (6-23 UTC)
- DMOB: Morning + Evening
- Desmond: 4x daily
- Gentech: 4x daily

**Consolidation target:** 1 job, YoYo's script, from Gentech profile

### Auth Failures
- 26 failing jobs burning tokens on retry loops
- Fix: `hermes model` re-auth on each profile

## Daily Tracking

Log daily token usage and routing accuracy:

| Date | Routes | Correct | Misroutes | Misses | Notes |
|------|--------|---------|-----------|--------|-------|
| 2026-05-07 | — | — | — | — | Implementation day |

## Weekly Review

Every Sunday, review:
1. Total token usage (from provider dashboard)
2. Routing accuracy (correct/misroutes/misses)
3. Cron job success rate
4. Specialist activation count

Target: 60-70% reduction in idle token burn vs baseline.
