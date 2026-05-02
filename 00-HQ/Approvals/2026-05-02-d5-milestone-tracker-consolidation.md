# Approval: D5 Milestone Tracker Cron Consolidation

**Submitted by:** Desmond (Gentech Creative) with DMOB (Code) & YoYo (Ops)
**Date:** 2026-05-02
**Priority:** Medium

---

## Summary

Consolidate 4 overlapping cron jobs into **one unified D5 Milestone Tracker** that combines LP position monitoring, CMC watchlist, fee efficiency tracking, and smart DCA signals. This eliminates duplication, fixes a hardcoded config bug, and implements the smarter LP monitoring rules Jordan outlined (5-minute breakout confirmation, 30% efficiency edge threshold, bid-ask awareness).

---

## Details

### Problem
Multiple cron jobs monitor the same LFJ AVAX/USDC LP position + CMC watchlist:
- `d5-master-cron.py` (hardcoded stale data: $83.92 vs live $134.94)
- `lp-range-monitor-v2.py` (old, Birdeye-based)
- `lp-range-monitor-v3.py` (tiered alerts, milestones)
- Multiple CMC watchlist jobs (Hermes jobs `1f10f10b2a07`, `915b1df66348`, `862ae0c1f85d`)

These run on different schedules and duplicate effort.

### Solution
Create **`d5-milestone-tracker.py`** as the single canonical LP + milestone monitor:

**Integrates:**
- CMC watchlist (7 coins, ≥3% movement threshold)
- LP range + fee efficiency + P&L (from v3)
- D5 milestone ladder (Scout → Freedom)
- **5-min breakout escalation** (warning → red if still out)
- **30% efficiency edge threshold** — rebalance recommendation zone
- **Shape-aware DCA zones:**
  - ≥ 70% → Full $50 DCA (center/curve)
  - 50–70% → $30 DCA (mid zone)
  - 30–50% → $20 micro-DCA + edge watch
  - < 30% → $10 micro-DCA + urgent rebalance
- **Bid-ask spread awareness** (if data available)
- Quiet hours: 23:00–6:30 ET (config-driven)

**Live config source:** `.lfj-aae-config.json` (no hardcoded POOL dict)

**New Hermes cron job (single):**
- Name: `D5 Milestone Tracker`
- Schedule: 08:15, 12:15, 16:15, 20:15 ET (4×/day)
- Delivery: Strategies group (-1002916759037)

**Retire:**
- `1f10f10b2a07` — "CMC Crypto Watchlist" (errored)
- `915b1df66348` — "Crypto Watchlist" (redundant)
- `862ae0c1f85d` — "CMC Watchlist + Market News" (redundant)

**Keep as fallback (Jordan decision needed):**
- `8ae8a04f3b71` — "LP Position Monitor + Alerts" (every 10 min, currently active). Should we retire this too, or keep as backup?

### Files Changed
- **NEW:** `03-Strategies/scripts/d5-milestone-tracker.py` (canonical)
- **ARCHIVED:** `lp-range-monitor-v2.py` → `lp-range-monitor-v2.py.archive-2026-05-02`
- **ARCHIVED:** `lp-range-monitor-v3.py` → `lp-range-monitor-v3.py.archive-2026-05-02`
- **UPDATED:** `03-Strategies/cron-jobs.md` manifest

### State Files
- **NEW STATE:** `~/.hermes/scripts/.d5-milestone-state.json`
- **Legacy reads:** `.lfj-range-state.json`, `.lfj-milestone-tracker.json` (v3 state, for migration)

---

## What We Need

- [ ] **Jordan approval** to retire duplicate cron jobs (`1f10f10b2a07`, `915b1df66348`, `862ae0c1f85d`) and establish `D5 Milestone Tracker` as the sole CMC+LP milestone monitor
- [ ] **Decision:** Retire `8ae8a04f3b71` (10-min LP Position Monitor) or keep as fallback?
- [ ] **YoYo execution** — update Hermes scheduler with new job ID, remove retired jobs
- [ ] **DMOB sign-off** on consolidated script logic (alert prefixes, state migration, efficiency thresholds)

---

## Alternatives Considered

1. **Patch `d5-master-cron.py` in-place** — keep file name, just fix bug + add edge thresholds. Pro: minimal vault churn. Con: file name implies "master cron" but it's now also the LP tracker — semantic confusion.

2. **Keep both `d5-master-cron.py` and `lp-range-monitor-v3.py` with harmonized thresholds** — separate concerns (CMC+LP vs pure LP). Pro: specialisation. Con: still two files, still harder to maintain → defeats consolidation.

3. **Create `d5-milestone-tracker.py`** (chosen) — fresh canonical script, clear purpose. Pros: intentional architecture, one source of truth, Jordan's "D5 milestone" naming. Con: requires DMOB review but that's expected.

---

*Coordinated by Desmond (Creative). Technical implementation: DMOB. Cron operations: YoYo. Final approval: Jordan.*
