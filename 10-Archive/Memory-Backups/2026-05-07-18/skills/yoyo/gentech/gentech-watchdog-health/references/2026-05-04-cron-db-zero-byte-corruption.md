# Cron Database 0-Byte Corruption — Structural Scheduler Failure

**Detected:** 2026-05-04 00:15 UTC
**Affected:** `/root/.hermes/cron/jobs.db` and `/root/.hermes/cron/cron.db`
**Severity:** P0 — Scheduler state tracking completely lost; job execution history not being persisted

---

## Executive Summary

The global Hermes cron database files are **0 bytes** despite active cron job executions:
- `jobs.db`: 0 bytes
- `cron.db`: 0 bytes  
- `jobs.json`: 6,065 bytes (intact source of truth)

**Impact:**
- Job execution history is not being persisted
- Scheduler may have unreliable state tracking
- Recovery actions (re-queuing failed jobs, deduplication) may be impaired
- Diagnostic queries against the runtime DB return empty results
- **BUT:** Cron jobs are still executing — the in-memory scheduler is functional using `jobs.json` as source

**Critical distinction:** The **source of truth** is `jobs.json`. The runtime database (`jobs.db`, `cron.db`) is a performance optimization that can be safely deleted and will be rebuilt from `jobs.json` on gateway restart.

---

## Root Cause

The cron executor maintains two SQLite databases:
1. **`jobs.db`** — compiled/optimized job registry (derived from jobs.json)
2. **`cron.db`** — execution history and state tracking

Both have been truncated to 0 bytes. Possible causes:
- Filesystem corruption during disk pressure event (May 1, disk at 82%)
- Abrupt process termination while DB was being written
- Inode exhaustion preventing file growth
- Bug in Hermes cron persistence layer

**Why this is survivable:** The gateway reads `jobs.json` on startup and repopulates the runtime DB if it's missing or corrupt. However, **while gateways are running**, the in-memory state is correct and jobs are executing. The risk is that manually inspecting `jobs.db` for diagnostics will yield no data, and if all gateways stop simultaneously, the scheduler may struggle to recover its previous state.

---

## Diagnostic Commands

### Check DB file sizes
```bash
ls -la /root/.hermes/cron/jobs.db /root/.hermes/cron/cron.db
# Expected: > 0 bytes. If 0 → corruption.
```

### Verify schema integrity (if non-zero)
```bash
sqlite3 /root/.hermes/cron/jobs.db "SELECT name FROM sqlite_master WHERE type='table';"
# Should list tables. Empty result on 0-byte file or corrupt DB.
```

### Confirm scheduler is using in-memory state (not DB)
```bash
# Check gateway logs for recent job executions (bypass DB)
tail -20 /root/.hermes/profiles/yoyo/logs/gateway.log | grep 'Running job'
# If you see execution logs, the cron executor is working from memory/jobs.json
```

### Detect cascading corruption (other DBs affected?)
```bash
# Check agent kanban DBs for corruption
for p in yoyo dmob desmond gentech; do
  db="/root/.hermes/profiles/$p/kanban.db"
  if [ -f "$db" ]; then
    result=$(sqlite3 "$db" "PRAGMA integrity_check;" 2>&1)
    echo "[$p] $db: $result"
  fi
done
```

---

## Recovery Procedure

**Precondition:** All agents are currently running and executing cron jobs. This fix is **preventative** — we're restoring diagnostic visibility and ensuring clean shutdown/restart cycles.

### Safe recovery (no downtime required):
1. **Stop all gateways gracefully** (to ensure clean state write)
```bash
for p in yoyo dmob desmond gentech; do
  hermes --profile $p gateway stop
done
# Wait 30 seconds for shutdown
```

2. **Backup corrupted DBs** (for potential post-mortem)
```bash
mkdir -p /root/vaults/gentech/10-Archive/cron-db-corruption-2026-05-04
cp /root/.hermes/cron/jobs.db /root/vaults/gentech/10-Archive/cron-db-corruption-2026-05-04/jobs.db.0byte
cp /root/.hermes/cron/cron.db  /root/vaults/gentech/10-Archive/cron-db-corruption-2026-05-04/cron.db.0byte
```

3. **Delete the 0-byte files**
```bash
rm /root/.hermes/cron/jobs.db /root/.hermes/cron/cron.db
```

4. **Restart all gateways**
```bash
for p in yoyo dmob desmond gentech; do
  hermes --profile $p gateway run --replace &
done
# Wait 10 seconds for initialization
```

5. **Verify DB reconstruction**
```bash
ls -la /root/.hermes/cron/jobs.db /root/.hermes/cron/cron.db
# Both files should now be > 0 bytes
sqlite3 /root/.hermes/cron/jobs.db "SELECT COUNT(*) FROM jobs;" 2>&1
# Should return a positive integer (job count)
```

6. **Validate execution history**
```bash
# Check that new run records are being created
sqlite3 /root/.hermes/cron/cron.db "SELECT job_id, status, created_at FROM job_runs ORDER BY created_at DESC LIMIT 5;" 2>&1
```

---

## Prevention & Monitoring

### Add to gentech-watchdog-health pre-flight:
```bash
# Step 0d: Cron DB file health
check_cron_db_health() {
  local jobs_db="/root/.hermes/cron/jobs.db"
  local cron_db="/root/.hermes/cron/cron.db"
  
  if [ ! -f "$jobs_db" ] || [ ! -f "$cron_db" ]; then
    echo "❌ CRITICAL: Cron DB files missing"
    return 1
  fi
  
  local jobs_size=$(stat -c%s "$jobs_db")
  local cron_size=$(stat -c%s "$cron_db")
  
  if [ "$jobs_size" -eq 0 ] || [ "$cron_size" -eq 0 ]; then
    echo "❌ CRITICAL: Cron DB 0-byte corruption detected (jobs.db=${jobs_size}b cron.db=${cron_size}b)"
    return 1
  fi
  
  echo "✅ Cron DB healthy (jobs.db=${jobs_size}b cron.db=${cron_size}b)"
  return 0
}
```

### Watchdog alert thresholds:
- `jobs.db` or `cron.db` size == 0 bytes → `🚨 Watchdog Alert: Cron DB corruption detected — scheduler state tracking lost`
- DB file missing entirely → `🚨 Watchdog Alert: Cron database files deleted — scheduler in unknown state`
- DB size shrinks >50% between checks → `🚨 Watchdog Alert: Cron DB contracting — possible filesystem corruption`

---

## Related Incidents

This 0-byte DB corruption co-occurred with:
- **May 1 disk pressure event** — root partition at 82%, I/O errors in agent logs
- **May 3 Nous OAuth cascade** — all gateways restarted simultaneously; DBs may have been truncated during forced shutdown

**Correlation hypothesis:** A systemic event (possibly disk-full condition or SIGKILL during DB write) is corrupting multiple persistence layers simultaneously (cron DB, kanban DB, session files).

**Action:** Run integrity checks on all SQLite databases fleet-wide.

---

## Quick Reference

| Symptom | Root Cause | Recovery |
|---------|-----------|----------|
| `jobs.db` = 0 bytes, cron jobs still running | DB truncated but scheduler uses memory/jobs.json | Stop gateways → delete 0-byte files → restart |
| `sqlite3 job.db` error: `no such table` | DB is empty or corrupted | Delete and rebuild |
| No recent entries in `job_runs` table | DB not being written OR queries hitting stale copy | Verify gateway is writing; check DB freshness with `stat` |
| `jobs.db` growing but `SELECT` returns nothing | DB is actually a pipe/device masquerading as file (rare) | Verify regular file with `file /root/.hermes/cron/jobs.db` |

**Never manually edit `jobs.db` or `cron.db`** — they are derived state. If corrupted, delete and let the gateway rebuild.
