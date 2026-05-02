---
date: 2026-05-02
thread: https://t.me/c/2351090362/10742
decision: D5 Milestone Tracking Consolidated
author: Jordan (via voice)
status: approved
---

## Decision Summary

**Consolidate D5 milestone tracking into ONE unified script** (`d5-master-cron.py`).

### Scope
- Merge LP alert logic from AAE monitor into the master cron
- Add `--json` flag for structured output
- Track D5 milestone dynamically: total goal, current capital, remaining distance
- **Capital-add detection**: when Jordan deposits (e.g., $50 tonight), script recalculates progress-to-goal automatically

### Rationale
- Single file to maintain and debug
- No sync issues between separate trackers
- Progress always reflects actual balance state

### Implementation Notes
- State file tracks previous balance; compute delta on each run
- On delta > threshold, emit updated "distance to goal" in JSON and summary
- JSON schema: `{ d5_goal, current_capital, remaining, last_deposit_amount, deposit_detected }`

### Handoff
➡️ **dmoB** (GenTech Labs) — implement capital-add detection logic in `d5-master-cron.py`

---
*Gentech — Building the future, one milestone at a time*