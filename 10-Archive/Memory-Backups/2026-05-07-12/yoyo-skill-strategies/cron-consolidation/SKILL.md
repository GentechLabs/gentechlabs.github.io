---
name: cron-consolidation
description: Consolidate overlapping cron jobs into unified trackers with vault→hermes-brain sync and deployment workflow
triggers:
  - "consolidating multiple cron jobs"
  - "redundant cron jobs monitoring same data"
  - "unify overlapping scheduled tasks"
  - "vault to hermes-brain sync for scripts"
  - "cron job deployment workflow"
stage: strategies
author: YoYo
last_updated: 2026-05-02
priority: high
---

# Cron Job Consolidation — Strategies Department

**Purpose**: Replace multiple overlapping cron jobs with a single unified tracker, deployed via vault→hermes-brain sync with proper approval flow.

---

## 📋 When to Use

Use this skill when:
- 2+ cron jobs monitor the same LP position, watchlist, or metric
- Jobs run on different schedules causing duplicate alerts
- Hardcoded configs drift from live data
- You need to consolidate before adding new features

**Do NOT use for**: One-off script fixes, simple cron edits, or non-departmental system cron.

---

## 🔄 Consolidation Workflow

### Phase 1 — Audit & Design
1. **Inventory active jobs**
   - Check `hermes-brain/profiles/<profile>/cron/jobs.json` for current jobs
   - Identify duplicates monitoring same data sources
   - Note schedules, recipients (Telegram groups), and output formats

2. **Document overlap**
   - List what each job does
   - Highlight redundant API calls/data fetches
   - Note any divergent outputs (different thresholds, formats)

3. **Design unified tracker**
   - Single source of truth for all merged data
   - Smart alerting (debounce, efficiency zones, tiered thresholds)
   - Respect quiet hours per department standards
   - Read config from ` .json` files in `$HERMES_HOME/home/.hermes/scripts/` (never hardcode)

### Phase 2 — Build & Archive
4. **Create canonical script** in vault: `03-Strategies/scripts/<name>.py`
   - Hermes-aware path resolution via `HERMES_HOME` env var
   - State file management in `$HERMES_HOME/home/.hermes/scripts/`
   - Telegram delivery to Strategies group (-1002916759037)
   - Follow `01-Agency/cron-job-standards.md` (human-readable prompts, no code blocks)

5. **Archive old scripts**
   - Move retired scripts to `<name>.py.archive-YYYY-MM-DD`
   - Keep in vault for audit trail

6. **Update documentation**
   - Create/update `03-Strategies/<name>.md` with features, schedule, config
   - Reference new canonical script path

### Phase 3 — Sync & Approval
7. **Sync vault → hermes-brain**
   - Copy new script to `/root/repos/hermes-brain/profiles/<profile>/home/.hermes/scripts/`
   - Commit with message: "feat(cron): consolidate <jobs> → <unified-tracker>"
   - **Do NOT modify jobs.json yet** — approval gate

8. **Submit approval request**
   - Create file in `00-HQ/Approvals/YYYY-MM-DD-<topic>-consolidation.md`
   - Document old jobs retired, new job schedule, benefits
   - Include script diff summary
   - Assign to Jordan for sign-off

### Phase 4 — Deploy
9. **On approval**:
   - Update `hermes-brain/profiles/<profile>/cron/jobs.json`
   - Remove old job entries, add new consolidated job with schedule
   - Commit: "deploy(cron): activate <unified-tracker> (approval #ref)"
   - Restart hermes gateway for profile: `hermes gateway restart --profile <profile>`
   - Verify first run within 5 minutes

10. **Post-deploy validation**
    - Check state files updated: `$HERMES_HOME/home/.hermes/scripts/.<name>-state.json`
    - Confirm Telegram message delivered to Strategies group
    - Archive old jobs.json entries to `03-Strategies/handoffs/` for audit

---

## ⚠️ Pitfalls & Gotchas

| Pitfall | Why It Happens | Fix |
|---------|----------------|-----|
| **Scripts synced but jobs.json unchanged** | Forgetting step 9 after approval | Add checklist item: "Update jobs.json" in approval template |
| **Hardcoded stale data** | Copying old values into new script | Use `.json` config files, fetch live data |
| **Hermes path resolution broken** | Using absolute paths or wrong `HERMES_HOME` | Always use `hermes_path()` helper; test with `echo $HERMES_HOME` |
| **Quiet hours ignored** | Not checking timestamp before sending | Add `if 23 <= hour < 6:30: return silent` early exit |
| **State file collisions** | Multiple jobs writing same state file | Namespace: `.d5-lp-state.json`, `.lfj-range-state.json` |
| **Old jobs keep running** | Cron jobs cached in hermes gateway | Restart gateway after jobs.json change |

---

## 📁 Reference Structure

```
03-Strategies/
├── scripts/
│   ├── d5-milestone-tracker.py        # Canonical unified script
│   ├── d5-master-cron.py              # Retired → archive
│   └── .d5-lp-state.json              # State (auto)
├── D5-Milestone-Tracker-Consolidation.md  # Feature doc
├── handoffs/
│   └── third-break-handoff-2026-05-02.md  # Deployment handoff
└── references/
    ├── vault-hermes-sync.md           # Sync mechanics (this file family)
    └── consolidation-checklist.md    # Pre-flight checklist template
```

**Support files**:
- `references/vault-hermes-sync.md` — detailed sync mechanics, commands, validation
- `references/consolidation-checklist.md` — actionable checklist template for any consolidation

---

## 🔗 Related Skills

- `hermes-agent-sync-management` — diagnose sync status issues
- `strategies/lp-monitoring` — LP position tracking patterns (efficiency zones, DCA)
- `devops/cron-job-audit` — audit existing cron configurations

---

## 📊 Success Metrics

- **Jobs reduced**: 4 → 1 (D5 consolidation)
- **API calls saved**: ~70% (eliminated duplicate Birdeye/CMC fetches)
- **Alert noise**: Reduced (smart debounce, quiet hours respected)
- **Deployment time**: <1 hour from approval to live (after practice)

---

*Updated: 2026-05-02 | Pattern validated on D5 Milestone Tracker deployment*