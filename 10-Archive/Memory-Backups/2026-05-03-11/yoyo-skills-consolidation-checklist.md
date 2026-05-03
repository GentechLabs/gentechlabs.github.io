# Consolidation Checklist — Runbook

**Trigger**: Two or more cron jobs monitoring same LP/watchlist with overlapping logic

## Pre-Consolidation Audit

- [ ] Inventory all active jobs in `hermes-brain/profiles/<profile>/cron/jobs.json`
- [ ] Identify redundant jobs (same data source, same Telegram channel)
- [ ] Document each job's: schedule, data sources, thresholds, output format
- [ ] Calculate wasted API calls (e.g., 4 jobs × Birdeye requests = 4× rate limit usage)
- [ ] Note any hardcoded values that drift (e.g., `d5-master-cron.py` had $83.92 hardcoded vs live $134.94)

## Design Phase

- [ ] Define unified scope (what gets merged, what stays separate)
- [ ] Choose smart features to add:
  - [ ] Debounce (5-min breakout confirmation)
  - [ ] Efficiency zones (≥70% center, 50–70% mid, 30–50% low, <30% edge)
  - [ ] Tiered DCA amounts ($50/$30/$20/$10)
  - [ ] Quiet hours respect (23:00–6:30 ET silent)
  - [ ] State persistence via `.json` files in `$HERMES_HOME/home/.hermes/scripts/`
- [ ] Confirm Telegram destination (Strategies group: -1002916759037)

## Build Phase

- [ ] Create script in vault: `03-Strategies/scripts/<name>.py`
- [ ] Implement Hermes path resolution (`HERMES_HOME` → `home/.hermes/scripts/`)
- [ ] Add config loader from `.json` (no hardcoding)
- [ ] Implement state file read/write with `.state.json` naming
- [ ] Add quiet hours check at top of main loop
- [ ] Test locally with `python <script>.py` (dry-run mode if available)
- [ ] Archive old scripts to `<name>.archive-YYYY-MM-DD.py`
- [ ] Update/create doc page `03-Strategies/<name>.md` with features table

## Sync & Approval Phase

- [ ] Copy script to hermes-brain: `profiles/<profile>/home/.hermes/scripts/`
- [ ] `chmod +x` the script
- [ ] Commit to hermes-brain repo with clear message
- [ ] Create approval request in `00-HQ/Approvals/YYYY-MM-DD-<topic>-consolidation.md`
- [ ] Include: problem statement, old jobs list, new job schedule, benefits summary
- [ ] Tag approver (Jordan)
- [ ] **WAIT** — do NOT touch jobs.json yet

## Deploy Phase (after approval)

- [ ] Update `hermes-brain/profiles/<profile>/cron/jobs.json`:
  - Remove old job entries (by ID or name)
  - Add new consolidated job entry with corrected schedule
- [ ] Validate JSON syntax (`python -m json.tool jobs.json`)
- [ ] Commit: `deploy(cron): activate <name> (approval #ref)`
- [ ] Restart Hermes gateway: `hermes gateway restart --profile <profile>`
- [ ] Verify job appears in `hermes gateway jobs --profile <profile>`
- [ ] Wait for first scheduled run (or trigger manually if supported)
- [ ] Confirm Telegram message received in Strategies group
- [ ] Check state file created with correct data structure
- [ ] Archive handoff to `03-Strategies/handoffs/`

## Post-Mortem

- [ ] Compare API call volume before/after (should drop ~70% for 4→1 consolidation)
- [ ] Document any unexpected behavior (e.g., state file conflicts, timezone issues)
- [ ] Update this checklist based on lessons learned

---

## D5 Milestone Tracker — Instance Record

- **Date consolidated**: 2026-05-02
- **Old jobs retired**:
  1. `d5-master-cron.py` (hardcoded $83.92 bug)
  2. `lp-range-monitor-v2.py` (old Birdeye-only)
  3. `lp-range-monitor-v3.py` (tiered alerts)
  4. Multiple CMC watchlist jobs (Hermes job IDs: 1f10f10b2a07, 915b1df66348, 862ae0c1f85d)
- **New script**: `d5-milestone-tracker.py` (419 lines)
- **New schedule**: 4× daily @ 08:15, 12:15, 16:15, 20:15 ET
- **Approval**: `2026-05-02-d5-milestone-tracker-consolidation.md` (pending Jordan)
- **Status**: ⏳ Approved in principle, NOT LIVE (hermes-brain not synced)

---

*Template: Use this checklist for any future cron consolidation. Copy to new file and customize.*