# Orchestrator Pattern — Implementation Plan

**Started**: 2026-05-07
**Status**: Phase 1 — Pilot (YoYo)

---

## Phase 1: Pilot (Today)
- [x] Create token optimization tracker
- [x] Create specialist memory files
- [x] Update YoYo SOUL.md — on-demand behavior
- [x] Create smart routing rules (`00-HQ/smart-routing-rules.md`)
- [x] Update Gentech SOUL.md — orchestrator routing brain
- [ ] Verify YoYo responds only when routed to
- [ ] Set up metrics collection

## Phase 2: Cron Consolidation (This Week)
- [ ] Consolidate DeFi Milestone jobs (4 → 1)
  - Keep: YoYo's `d5-lp-consolidated.py` script
  - Remove: DMOB morning/evening, Desmond LP monitor, Gentech DeFi Milestones
  - Move to: Gentech profile (single source of truth)
- [ ] Fix auth failures
  - Run `hermes model` on YoYo profile to re-auth
  - Run `hermes model` on DMOB/Desmond profiles
- [ ] Remove deadlocked/duplicate jobs

## Phase 3: Full Rollout (Next Week)
- [ ] Update DMOB SOUL.md — on-demand behavior
- [ ] Update Desmond SOUL.md — on-demand behavior
- [ ] Update Gentech SOUL.md — orchestrator routing logic
- [ ] Add Gentech to all Telegram groups (Labs, Strategy, Content, Entertainment)
- [ ] Remove specialist auto-responders from shared groups

## Phase 4: Monitoring & Optimization (Ongoing)
- [ ] Weekly token usage review
- [ ] Adjust model tiers based on task complexity
- [ ] Refine routing rules based on failures
- [ ] Track savings vs baseline

---

## Routing Rules (for Gentech SOUL.md)

| Request Type | Route To | Vault Folder |
|-------------|----------|--------------|
| DeFi/LP/portfolio | YoYo | 03-Strategies/ |
| Smart contracts/security | DMOB | 03-Projects/ |
| Content/social/submissions | Desmond | 06-Content/ |
| Coordination/approval | Gentech | 11-Mess Hall/ |
| Emergency/blocked | Jordan | 00-HQ/ |

---

## Success Metrics

| Metric | Baseline | Target | Current |
|--------|----------|--------|---------|
| Cron jobs | 46 | <20 | 46 |
| Idle agents | 4 | 1 (Gentech) | 4 |
| DeFi Milestone jobs | 4 | 1 | 4 |
| Auth failures | 26 | 0 | 26 |
| Token burn (est daily) | TBD | -60% | TBD |
