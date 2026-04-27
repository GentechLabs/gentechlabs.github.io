---
date: 2026-04-27
author: YoYo
source: proactive-audit
tags: [bug, cron, LP, D5]
---

# D5 Master Cron Bug Report — 2026-04-27

## Found During Proactive Scan

### 1. Hardcoded Stale Position Data in `d5-master-cron.py`

| Field | `d5-master-cron.py` (hardcoded) | `.lfj-aae-config.json` (live) | Delta |
|-------|----------------------------------|--------------------------------|-------|
| `position_usd` | 83.92 | 138.92 | -$55.00 |
| `range_low` | 9.33 | 9.32 | +$0.01 |
| `range_high` | 9.52 | 9.53 | -$0.01 |

**Impact:** Every D5 Master Cron report shows wrong position value ($83.92). Jordan sees stale data.

**Fix:** Load from `.lfj-aae-config.json` inside `build_lp()`. Do not hardcode.

### 2. Cron Job Desync — Docs ≠ System

Vault manifest (`03-Strategies/cron-jobs.md`) says:
- **Job `7180d8a26738`** = unified D5 Master Cron running 4×/day ✅ Active — sole Strategies cron

Hermes actual (`cronjob list`):
- Job `1f10f10b2a07` name: "YoYo — CMC Crypto Watchlist" — schedule `15 8,12,16,20 * * *` ✅ **Still active**
  - Last status: **error**
  - Calls OLD cmc-only script, not `d5-master-cron.py`
- Job `504ac01d54ed` name: "YoYo — Daily LP + D5 Milestone" — schedule `0 10 * * *` ✅ **Still active**
  - Last run: **never** (`last_run_at: null`)

**Impact:** Three sources of truth (docs, script file, hermes scheduler) disagree. Duplicate/alerts risk. Error on CMC watchlist may be why unified report never got promoted.

### 3. Previous CMC Cron Error Root Cause

Job `1f10f10b2a07` (CMC watchlist-only) had `last_status: error`. Likely transient API timeout — script itself works when run manually.

## Recommended Actions

1. **Patch `d5-master-cron.py`** — replace hardcoded `POOL` dict with `load_config()` reading `.lfj-aae-config.json`
2. **Retire duplicate Hermes jobs**
   - Remove or pause `1f10f10b2a07` (old CMC-only)
   - Remove `504ac01d54ed` (old daily LP)
   - Create ONE unified cron that calls `d5-master-cron.py` at the documented schedule
3. **Update `cron-jobs.md`** to match actual hermes job IDs after cleanup

---
*Route: Jordan approval needed? Low risk — I can patch the script file now. Hermes cron retire needs coordination with Gentech.*
