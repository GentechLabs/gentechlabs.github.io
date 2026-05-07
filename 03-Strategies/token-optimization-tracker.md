# Token Optimization Tracker

## Orchestrator Pattern Implementation — Started 2026-05-07

### Architecture Change
- **Before**: 4 agents always-on, each loading full context (~10-20K tokens per message)
- **After**: Gentech as orchestrator/router, specialists on-demand only
- **Target**: 60-70% reduction in idle token burn

---

## Baseline Metrics (Pre-Implementation)

### Cron Jobs by Agent
| Agent | Total Jobs | Active | Failing | Notes |
|-------|-----------|--------|---------|-------|
| YoYo | 4 | 1 | 3 | Auth revoked on 3 jobs |
| DMOB | 8 | 3 | 5 | Deadlock issues, auth failures |
| Desmond | 3 | 1 | 2 | DB corruption, auth failures |
| Gentech | 31 | ~15 | ~16 | Way too many, many overlapping |
| **Total** | **46** | **~20** | **~26** | |

### Duplicate DeFi Milestone Jobs (Critical)
- YoYo: `Defi Milestone` (every 10 min, 6-23 UTC)
- DMOB: `Defi Milestone — Morning` (8:30 UTC) + `Defi Milestone — Evening` (21:00 UTC)
- Desmond: `Defi Milestone — LP Monitor` (8:15, 12:15, 16:15, 20:15 UTC)
- Gentech: `DeFi Milestones` (8:15, 12:15, 16:15, 20:15 UTC)

**→ Consolidation target: 1 job, YoYo's existing script, run from Gentech profile**

### Auth Failures
- Omni-Summary: `RuntimeError: Refresh session has been revoked`
- Portfolio Site: Same auth error
- College.xyz: Same auth error
- Multiple DMOB/Desmond jobs: Same pattern

---

## Daily Tracking

### 2026-05-07 (Implementation Day)
- [ ] Update YoYo SOUL.md — on-demand behavior
- [ ] Create specialist memory templates
- [ ] Consolidate DeFi Milestone jobs (4 → 1)
- [ ] Fix auth failures where possible
- [ ] Set up metrics collection cron job

---

## Weekly Metrics

| Week | Total Tokens (est) | Idle Burn | Active Work | Savings vs Baseline |
|------|-------------------|-----------|-------------|---------------------|
| May 5-11 | TBD | TBD | TBD | — |

---

## Agent Memory Files

Specialist context lives in vault, not Hermes memory:
- `03-Strategies/agent-memory/yoyo-context.md` — YoYo's working context
- `03-Strategies/agent-memory/dmob-context.md` — DMOB's working context  
- `03-Strategies/agent-memory/desmond-context.md` — Desmond's working context
