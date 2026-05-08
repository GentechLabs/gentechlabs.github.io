# 2026-05-04: Cron Ticker Silent Stall Detection

## Problem Statement

The Hermes cron ticker (APScheduler embedded in gateway) can **stop executing jobs** while the gateway process remains alive, continues responding to Telegram messages, and shows "Cron ticker started" in logs. This creates a **false positive healthy state** — agents appear running but scheduled tasks are not firing.

## Affected Components

- Hermes Gateway (all profiles): `hermes-cli.main --profile <agent> gateway run`
- Embedded APScheduler cron ticker
- Cron job dispatcher → agent execution pipeline

## Failure Mode: Silent Ticker Death

**Symptoms:**
1. Gateway process RUNNING (systemd active, PID stable)
2. Latest log entry RECENT (within minutes) — normal INFO-level activity
3. **No `[cron_<jobid>_<timestamp>]` markers in `agent.log` for >60 minutes**
4. Cron output directories STALE (latest file >30 minutes old)
5. No `executing cron job` or `job completed` events in gateway.log
6. Cron ticker "started" message present but no subsequent "running job" logs
7. Telegram responses still working (agent not globally hung)

**Distinguishing from Related Failures:**

| Condition | Cron Output | agent.log cron markers | Gateway log ticker | Process alive? |
|-----------|-------------|------------------------|-------------------|----------------|
| **Silent ticker stall** | Stale (old) | **Absent** for >60m | Shows "started" (old) | ✅ Yes |
| **Cron executor deadlocked** | Stale | Absent | No ticker events at all | ✅ Yes |
| **Auth-blocked jobs** | Recent but empty/failed | Present (failed exec) | Ticker active | ✅ Yes |
| **Gateway completely hung** | Stale | Absent | No new log entries | ❌ No |

## Detection Methodology (3-Layer Verification)

### Layer 1: Output File Recency (fast, coarse)

```bash
# Check cron output file modification times across all agents
for agent in yoyo dmob desmond gentech; do
  latest=$(find /root/.hermes/profiles/$agent/cron/output -type f -name '*.md' -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1)
  if [ -n "$latest" ]; then
    ts=$(echo $latest | cut -d' ' -f1)
    age=$(( $(date +%s) - ${ts%.*} ))
    echo "[$agent] Latest output: $(date -d @${ts%.*} '+%H:%M') (${age}s ago)"
  else
    echo "[$agent] NO OUTPUT FILES"
  fi
done
```

**Thresholds:**
- `< 5 min` → healthy
- `5–30 min` → stale, investigate
- `> 30 min` → **ticker likely dead** (if gateway still responsive)
- No output files at all → cron executor never ran or jobs disabled

### Layer 2: agent.log Cron Execution Trace (definitive)

agent.log contains **definitive `[cron_<jobId>_<timestamp>]` session markers** for every cron job execution. These are the most reliable proof that the ticker actually fired and dispatched a job to the agent runtime.

```bash
# Check for recent cron execution sessions in agent.log
for agent in yoyo dmob desmond gentech; do
  log="/root/.hermes/profiles/$agent/logs/agent.log"
  if [ -f "$log" ]; then
    # Count cron execution markers in last N lines
    recent=$(tail -2000 "$log" | grep -c '\[cron_[0-9a-f]\+_[0-9]\+\]')
    last_ts=$(tail -2000 "$log" | grep -o '\[cron_[0-9a-f]\+_[0-9]\+\]' | tail -1 | grep -o '[0-9]\{14\}')
    
    if [ -n "$last_ts" ]; then
      last_dt=$(echo $last_ts | sed 's/\(....\)\(..\)\(..\)_\(..\)\(..\)\(..\)/\1-\2-\3 \4:\5:\6/')
      age_min=$(( ( $(date +%s) - $(date -d "$last_dt" +%s) ) / 60 ))
      echo "[$agent] Last cron exec: $last_dt ($age_min min ago), markers in last 2000 lines: $recent"
    else
      echo "[$agent] NO cron exec markers in last 2000 log lines"
    fi
  fi
done
```

**Interpretation:**
- **>0 markers with recent timestamp (<30 min)** → ticker active ✓
- **0 markers but gateway log shows "Cron ticker started"** → ticker thread dead but process alive ✗ **SILENT STALL**
- Markers present but all >2h old → ticker stopped sometime ago

**Key insight:** The cron ticker thread can die silently without affecting the main gateway event loop. Telegram message handling continues because it runs on a separate thread/event loop. The ticker "started" message may be hours old with no subsequent job dispatch.

### Layer 3: Log Writing Liveness Test (live verification)

Confirm the gateway process is actively writing to its log files. A process that is completely hung will stop updating log file mtime/size.

```bash
# Quick 3-second liveness probe
for agent in yoyo dmob desmond gentech; do
  log="/root/.hermes/profiles/$agent/logs/gateway.log"
  if [ -f "$log" ]; then
    size1=$(stat -c %s "$log")
    sleep 3
    size2=$(stat -c %s "$log")
    [ $size2 -gt $size1 ] && echo "[$agent] ✅ Log writing active (+$((size2-size1)) bytes)" || echo "[$agent] ❌ NO LOG ACTIVITY — process likely hung"
  fi
done
```

**Warning:** This test disturbs the system minimally but should be used sparingly in production.

## Root Causes (observed)

1. **Cascading shutdown + incomplete restart** (May 3 23:33 event)
   - All agents stopped simultaneously via coordinated restart script
   - Post-restart: ticker thread initialized (`Cron ticker started`) but **scheduler never began firing jobs**
   - Suspected cause: cron state lockfile (`.tick.lock`) persisted across restart in corrupted/empty state
   - Evidence: `.tick.lock` file present with size 0 bytes after restart

2. **Auth token revocation cascade** (May 3 morning)
   - DMOB first failure at 06:00: `Hermes is not logged into Nous Portal`
   - Progressively affected all agents throughout the morning
   - Caused cron jobs to fail **before** ticking (pre-execution auth check aborts)

3. **Credential pool exhaustion + rotation lock**
   - All provider credentials marked `exhausted` or `revoked`
   - Cron ticker continues but every job immediately fails auth → no successful execution
   - **Distinguish:** markers present in agent.log but all jobs fail instantly (check error patterns)

## Recovery Procedure

### Immediate Fix (preferred)

```bash
# 1. Clear stale tick lock if present (empty or old)
for agent in dmob desmond; do
  lock="/root/.hermes/profiles/$agent/cron/.tick.lock"
  if [ -f "$lock" ]; then
    size=$(stat -c %s "$lock")
    age=$(( $(date +%s) - $(stat -c %Y "$lock") ))
    if [ $size -eq 0 ] || [ $age -gt 120 ]; then
      echo "Removing stale $lock (size=$size, age=${age}s)"
      rm -f "$lock"
    fi
  fi
done

# 2. Restart affected gateways
systemctl --user restart hermes-gateway-dmob.service hermes-gateway-desmond.service

# 3. Wait 30 seconds, then verify ticker resumes
sleep 30
for agent in dmob desmond; do
  echo "=== $agent ==="
  tail -100 /root/.hermes/profiles/$agent/logs/gateway.log | grep "Cron ticker started"
done
```

### If restart doesn't revive ticker

```bash
# Full cron state reset (preserves jobs.json)
for agent in dmob desmond; do
  # Stop gateway first
  systemctl --user stop hermes-gateway-$agent.service
  
  # Remove cron runtime state (safe; recreates on restart)
  rm -rf /root/.hermes/profiles/$agent/cron/.tick.lock
  rm -rf /root/.hermes/profiles/$agent/cron/state/ 2>/dev/null || true
  
  # Restart
  systemctl --user start hermes-gateway-$agent.service
done
```

### Verification of Recovery

Within 5–10 minutes after restart, confirm:

1. **New `[cron_...]` markers** appear in agent.log (latest timestamp <2 min old)
2. **New output files** appear in cron/output/ directories
3. No `ticker stopped` messages without subsequent `ticker started` restart
4. Jobs transition from `last_run: null` to populated timestamps in `hermes cron list --verbose`

## Diagnostic Checklist Integration

Add to `gentech-watchdog-health` **Step 0c — Cron Tick Lock Health Check**:

```bash
# Extended check: ticker liveness
for agent in yoyo dmob desmond gentech; do
  log="/root/.hermes/profiles/$agent/logs/agent.log"
  echo "=== $agent ==="
  
  # 1. Check for cron execution markers in last 30 minutes
  thirty_min_ago=$(date -d '30 minutes ago' '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -v-30M '+%Y-%m-%d %H:%M:%S')
  recent_cron=$(grep -c '\[cron_[0-9a-f]\+_[0-9]\+\]' <(tail -2000 "$log") 2>/dev/null || echo 0)
  cron_markers_in_log=$(grep -o '\[cron_[0-9a-f]\+_[0-9]\+\]' <(tail -2000 "$log") 2>/dev/null | tail -1)
  
  if [ -z "$cron_markers_in_log" ]; then
    echo "  ❌ NO CRON MARKERS in agent.log — ticker may be dead"
  else
    last_ts=$(echo $cron_markers_in_log | grep -o '[0-9]\{14\}')
    last_dt=$(echo $last_ts | sed 's/\(....\)\(..\)\(..\)_\(..\)\(..\)\(..\)/\1-\2-\3 \4:\5:\6/')
    age_min=$(( ( $(date +%s) - $(date -d "$last_dt" +%s) ) / 60 ))
    echo "  Last cron exec: $last_dt ($age_min min ago)"
  fi
  
  # 2. Verify ticker thread state via gateway log
  gw_log="/root/.hermes/profiles/$agent/logs/gateway.log"
  ticker_start=$(grep "Cron ticker started" "$gw_log" | tail -1)
  ticker_stop=$(grep "Cron ticker stopped" "$gw_log" | tail -1)
  
  if [ -n "$ticker_start" ] && [ -z "$ticker_stop" ] && [ -z "$cron_markers_in_log" ]; then
    echo "  ❌❌❌ SILENT TICKER STALL: ticker started but never executed jobs"
  fi
done
```

## Related Incidents

- **2026-05-03 23:33** — Coordinated gateway restart storm; DMOB and Desmond tickers failed to recover
- **2026-05-03 morning** — OAuth revocation cascade; auth failures blocked cron before execution
- **2026-05-02** — Cron DB zero-byte corruption (different failure: executor completely dead)

## Patterns to Watch

| Pattern | Detection | Action |
|---------|-----------|--------|
| Ticker stopped + no restart in 60s | `grep "Cron ticker stopped" gateway.log` with no subsequent "started" within 60s | Restart gateway |
| Ticker started but zero cron markers in agent.log for >30 min | Compare last `[cron_...]` vs current time | Clear `.tick.lock`, restart |
| Output files stale but gateway active | `find cron/output -mmin +30` returns files | Same as above |
| Gateway log active but ticker events absent | `grep -c "Cron ticker" gateway.log` = 0 in last 1000 lines | Gateway process may be wrong version or cron disabled |

## Future Automation

- **Cron Ticker Heartbeat Monitor:** Simple script that runs every 5 min, checks for `[cron_...]` markers in last 10 min, alerts if absent.
- **Auto-recovery:** If silent stall detected ≥2 agents simultaneously, trigger coordinated gateway restart.
