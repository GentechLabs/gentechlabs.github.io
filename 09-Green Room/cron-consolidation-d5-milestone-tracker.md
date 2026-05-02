# Green Room Handoff — Desmond → DMOB & YoYo
## Topic: Cron Duplication Audit + D5 Milestone Tracker Consolidation
## Date: 2026-05-02
## From: Desmond (Creative)
## To: DMOB (Code), YoYo (Ops)

---

## 🔍 Situation Summary

Jordan identified **cron job duplication** and wants a single consolidated D5 Milestone Tracker that:
1. Tracks the LP position actively (like LP Position Monitor does)
2. **5-minute breakout confirmation** — light warning → red alert escalation (already in lp-range-monitor-v3)
3. **Fee efficiency edge detection** — when efficiency hits ~30% (curve shape), trigger rebalance suggestion
4. **Smart DCA** — down on lower edges + bid-ask spread opportunity signals
5. **Single source of truth** — retire duplicate jobs

### Current State from Vault Manifest (`03-Strategies/cron-jobs.md`)

| Job | Schedule | Notes |
|-----|----------|-------|
| `8ae8a04f3b71` | Every 10 min (6–23 UTC) | LP Position Monitor + Alerts (YoYo) |
| `33b3c40539b2` | 3×/day (9,15,21 UTC) | DeFi Dashboard (YoYo) |
| `2563e78bcf72` | Hourly | DeFi Milestone tracker — alerts only if efficiency <30% |
| `915b1df66348` | Every 2h (4:30–16:30 UTC) | Crypto Watchlist (YoYo) |
| `862ae0c1f85d` | Every 2h | CMC Watchlist + Market News |
| `f930f56d082a` | Hourly (7–21 ET) | Gentech Crypto Watchlist (CMC) |

### Problem Identified (from bug report `d5-master-cron-bug-report-2026-04-27.md`)

Three sources of truth:
- **Docs** say: job `7180d8a26738` (unified D5 Master Cron, 4×/day) — sole Strategies cron
- **Hermes actual** (then): jobs `1f10f10b2a07` + `504ac01d54ed` still active
- **Script file**: `d5-master-cron.py` (exists, has hardcoded stale POOL data)

Also: `d5-master-cron.py` hardcodes `position_usd=83.92` but live config says `$134.94` — bug confirmed.

---

## ✅ What Needs to Happen

### Phase 1 — Script Consolidation (DMOB)

**Goal:** Replace all overlapping LP/cron scripts with a single `d5-milestone-tracker.py` that:

1. **Loads live config** from `.lfj-aae-config.json` (NOT hardcoded) — bug fix
2. **Integrates**:
   - CMC watchlist (d5-master-cron feature)
   - LP range + fee efficiency + P&L (v3 feature)
   - Milestone tracking (v3 feature)
   - 5-min breakout escalation (v3 feature, kept)
   - **Edge threshold:** alert/recommend rebalance when efficiency ≤ 30% (tighter than current <75% generic warning)
   - **Smart DCA recommendations** based on efficiency zone:
     - ≥ 70% (center/curve): Full DCA ($50) — "position healthy, keep DCA'ing"
     - 50–70% (mid): Reduced DCA ($30) — "still earning, not chasing"
     - 30–50% (low): Micro-DCA ($20) + "watch for rebalance — price near edge"
     - < 30% (edge/crash): Micro-DCA ($10) + "urgent rebalance needed"
   - **Bid-ask awareness** (if data available): when down on lower edge, flag "buying opportunity"
3. **Quiet hours:** 23:00–6:30 ET (from `quiet_hours` in config)
4. **State persistence** in `~/.hermes/scripts/.d5-milestone-state.json`
5. **Exit codes:** 0 = silent, 1 = error, special ALERT/MILESTONE prefixes for routing

**Deliverable:** `d5-milestone-tracker.py` (replaces d5-master-cron.py + lp-range-monitor-v3.py as the canonical)

### Phase 2 — Cron Job Cleanup (YoYo with DMOB review)

**Retire these Hermes cron jobs** (duplicate/overlap):
- `1f10f10b2a07` — "CMC Crypto Watchlist" (old, errored, superseded)
- `915b1df66348` — "Crypto Watchlist" (redundant with consolidated D5)
- `862ae0c1f85d` — "CMC Watchlist + Market News" (redundant)
- Any other LP/watchlist job NOT `8ae8a04f3b71` (the 10-min LP Position Monitor — KEEP this as fallback)

**Create ONE unified D5 milestone job:**
- **Job name:** `D5 Milestone Tracker`
- **Schedule:** 4×/day at 08:15, 12:15, 16:15, 20:15 ET (Jordan's original D5 times)
- **Delivery:** Strategies group (-1002916759037)
- **Script:** `d5-milestone-tracker.py`

**QUESTION:** Keep `8ae8a04f3b71` (10-min LP Position Monitor) as a **fallback/backup**? Jordan's rule: no duplication. If D5 tracker is comprehensive, we may retire it too. Please advise.

### Phase 3 — Vault Sync (Desmond)

Once DMOB confirms script and YoYo confirms cron jobs updated:
1. Archive `lp-range-monitor-v2.py` → `lp-range-monitor-v2.py.archive-2026-05-02`
2. Archive `lp-range-monitor-v3.py` → `lp-range-monitor-v3.py.archive-2026-05-02`
3. Update `03-Strategies/cron-jobs.md` manifest:
   - Remove retired job rows
   - Add new D5 Milestone Tracker row (job ID + schedule)
   - Note: "Legacy LP Position Monitor `8ae8a04f3b71` retained as fallback" OR "Retired — superseded by D5"
4. Cross-link to new script header docblock
5. Update `01-Agency/cron-job-standards.md` examples if needed

---

## 🎯 Questions for DMOB

1. **Script approach:** Should I modify `d5-master-cron.py` in-place to add the 30% edge threshold + enhanced DCA zones, or create a fresh `d5-milestone-tracker.py` that supersedes both v2 and v3?
2. **Bid-ask data:** The `lp-aae-signal-monitor.py` may have bid-ask spread logic. Can we access this within the D5 tracker, or is that out of scope? (Jordan hinted at it.)
3. **Backward compatibility:** The `.lfj-range-state.json` and `.lfj-milestone-tracker.json` state files — should the new script read/write both, or migrate to a single `.d5-milestone-state.json`?
4. **ALERT prefixes:** Current v3 uses `ALERT:red_breakout_above|below`, `MILESTONE:$.2f`, `LOW_EFFICIENCY`, `SILENT`. Should D5 tracker adopt same format for compatibility?

---

## 🎯 Questions for YoYo

1. **Hermes cron registry:** Confirm the 4 active jobs above are actually running (especially `2563e78bcf72` hourly milestone tracker and the 2 watchlists). Any duplicates you see from your end?
2. **Retirement plan:** After D5 Milestone Tracker is live, should we also retire `8ae8a84f3b71` (10-min LP monitor) or keep as fallback? Jordan said "same rules that the LP tracker had" — does that mean keep LP tracker's schedule separate?
3. **Who runs the script?** The cron job should run as which profile (YoYo)? Script location: `~/.hermes/scripts/` symlinked from vault?

---

## 📋 Desmond's Next Steps (after DMOB/YoYo reply)

- [ ] Draft `d5-milestone-tracker.py` (or patch d5-master-cron.py) with consolidated logic
- [ ] Write approval note to `00-HQ/Approvals/` if Jordan signature needed for cron job retirement
- [ ] Update vault manifest (`03-Strategies/cron-jobs.md`)
- [ ] Archive old v2/v3 scripts with clear handoff notes
- [ ] notify Strategies group of consolidated D5 Tracker launch

---

**Route:** Creative owns documentation + script header/vault updates; DMOB owns code logic; YoYo owns Hermes cron operations.

*Tagging DMOB and YoYo — Desmond out.*
