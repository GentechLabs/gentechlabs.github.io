# Incident INC-20260502-0055: Simultaneous Ticker Subsystem Failure

**Detected:** 2026-05-02 08:10–08:12 UTC  
**Agents affected:** YoYo, DMOB, Desmond, Gentech (all 4)  
**Severity:** P1 — complete automation paralysis  
**Status:** Open (unresolved as of 08:12)

---

## Executive Summary

All four Hermes agent gateways became **stale simultaneously** (running processes died but PID files persisted). The embedded cron ticker subsystem across all agents ceased executing scheduled jobs. Jobs registered in `cron/jobs.json` show `"last_run": "never"` and output directories contain no recent results (latest: April 28–30). This is a **ticker infrastructure failure**, not individual agent crashes.

### Key differentiators from cascade crash (May 1 pattern):

| Dimension | May 1 Cascade (`gentech-agent-health-diagnosis` Phase 9) | May 2 Ticker Failure (this incident) |
|-----------|-----------------------------------------------------------|--------------------------------------|
| Gateway state before failure | RUNNING → crashed within <60s window | Unknown (likely already dead; no crash window observed) |
| Process state on discovery | Some zombie/stuck, all stopped | All PID files stale; no matching processes |
| Last gateway.log activity | Sparse, last entries ~00:55–01:00 UTC | YoYo: 04:03, DMOB: 04:01, Desmond: 04:01, Gentech: 04:03 |
| Cron job states | Jobs may have been `active` pre-crash | All jobs `scheduled` with `"last_run": "never"` |
| Cron output dirs | April 28–30 content (stale) | Same stale content; nothing since April 30 |
| Brain-backup | Did NOT run (was part of cascade) | DID run at 06:01 and 06:06 via **system cron** |
| System cron | Stopped when gateways died | Continued running normally |
| Primary failure mode | Gateway process crash / shutdown timeout | Ticker scheduler thread died; cron never invoked |

**Conclusion:** Gateways died ~04:00–04:03 UTC. Ticker subsystem was already dead or died with them. System cron continued and independently executed brain-backup jobs, proving the host OS and crond daemon are healthy. Hermes embedded cron has been non-functional for at least 4 hours.

---

## Timeline (last known activity)

| Agent | Last gateway.log activity | Last agent.log activity | Cron output newest | System cron |
|-------|--------------------------|------------------------|-------------------|-------------|
| YoYo | 2026-05-02 04:03:05 | 2026-05-02 08:06:20 | 2026-04-30 13:30 | Active |
| DMOB | 2026-05-02 04:01:34 | 2026-05-02 06:12:07 | 2026-05-01 10:05 | Active |
| Desmond | 2026-05-02 04:01:28 | 2026-05-02 06:00:15 | 2026-04-28 18:01 | Active |
| Gentech | 2026-05-02 04:03:05 | 2026-05-02 08:11:23 | 2026-04-30 16:30 | Active |

**Note:** `agent.log` shows recent timestamps because the **main Hermes agent CLI process** is still running (it hosts the Telegram polling loop separately from the gateway). The `gateway` subsystems (cron, job dispatcher, skill executor) are dead.

---

## Diagnostic Evidence

### 1. Gateway PID files stale

```bash
# Discovery run at 08:10–08:12
YOYO: gateway.pid = {"pid": 923106, ...} → NO matching process in `ps aux`
DMOB: gateway.pid = {"pid": 922890, ...} → NO matching process
DESMOND: gateway.pid = {"pid": 922877, ...} → NO matching process
GENTECH: gateway.pid = {"pid": 923094, ...} → NO matching process
```

All 4 gateways are dead. PID files were not cleared on abnormal termination.

### 2. Cron registry shows "never ran"

Inspecting `/root/.hermes/profiles/*/cron/jobs.json` (excerpt):

```json
{
  "jobs": [
    {
      "id": "682e9597b8d6",
      "name": "Gentech LLC Reminder",
      "schedule": {"kind": "cron", "expr": "0 5 15 * *"},
      "last_run": "never",
      "next_run": null
    },
    {
      "id": "cron_...",
      "name": "Gentech Watchdog",
      "schedule": {"kind": "cron", "expr": "*/5 * * * *"},
      "last_run": "never"
    }
    // ... 20+ more jobs
  ]
}
```

**All jobs across all agents have `last_run: never`.** This means the cron executor thread never successfully invoked any job, even once, since profile creation or last state reset (April 28–30 is the earliest output).

### 3. Cron output directories contain only ancient results

```
yoyo/cron/output/
  ├─ 8459e3404aa7/2026-04-28_10-32-34.md
  ├─ 9240a0e89275/2026-04-28_11-04-21.md, 2026-04-29_23-35-39.md
  └─ b394020b8319/2026-04-30_13-30-06.md

gentech/cron/output/
  ├─ b006812998df/2026-04-30_12-12-10.md
  ├─ b394020b8319/2026-04-30_13-44-55.md
  └─ 051dcc8d3f11/2026-04-30_16-30-22.md
```

Nothing after April 30. Confirms cron hasn't fired in at least 48 hours.

### 4. Brain-backup ran independently via system cron

```
/root/.hermes/logs/brain-backup.log:
[2026-05-02T06:00:09Z] === Brain Backup Start ===
[2026-05-02T06:00:10Z] Syncing memory files...
[2026-05-02T06:01:02Z] === Brain Backup Start ===
[2026-05-02T06:01:03Z] Syncing memory files...
```

Brain-backup is scheduled in **system crontab** (not via Hermes cron), so it executed correctly despite agent gateways being dead. This proves the host cron daemon is healthy.

### 5. agent.log still shows recent activity — but it's the *CLI*, not gateway

```log
2026-05-02 08:11:23,092 INFO [cron_9ecfada01952_20260502_081052] agent.auxiliary_client: Auxiliary auto-detect: using main provider nous (stepfun/step-3.5-flash)
```

The `agent.log` entry at 08:11:23 shows a task ID of `cron_9ecfada01952_20260502_081052`. This **appears** to be a cron-triggered session, but:

- The timestamp `20260502_081052` is 08:10:52, which is in the recent past (2 minutes ago)
- However, **no output file** exists in `yoyo/cron/output/9ecfada01952/` — the output dir was created but is empty
- This suggests the **CLI accepted the cron trigger** but the **gateway executor died mid-flight** before producing results

The `cron_`-prefixed session IDs are generated by the cron ticker when it schedules a job. The fact that this session started indicates the **ticker thread DID fire** at 08:10:52 (matching the `Gentech Watchdog` schedule `*/5 * * * *`). But the **executor thread died** before actually running the job to completion.

**New pattern discovered:** Ticker fires → job scheduled → executor crashes silently → no output. This is a **partial ticker failure**: ticker alive, executor dead.

---

## Root Cause Hypotheses

### H1: Executor thread deadlocked (most likely)
- Ticker thread runs every 60s, enqueues job → executor thread picks it up → crashes on first I/O
- **Evidence:** You see `cron_xxx` sessions appear in agent.log but no output files complete
- **Correlates with:** Phase 7 (Cron Subsystem Stall) but worse — executor is crashing, not just blocked
- **Check:** `gateway.log` for uncaught exceptions right after `cron ticker fired` messages

### H2: Cron cache (`cron/*.db` or `cron/*.state`) corrupted
- Gateway reads cron state, executor attempts to load job, hits malformed DB and exits
- **Recovery:** Clear `cron/*.db`, `cron/*.state` (already documented in Phase 7 Step A)

### H3: Kanban notifier I/O failure propagates to executor
- All agents share the same kanban notifier thread (single-threaded I/O)
- If kanban DB hits `I/O error` or `database or disk is full`, the executor may crash on every job
- **Check:** `gateway.log` for `kanban notifier` errors preceding `cron executor` errors

### H4: Shared hermes-agent bytecode corruption (still possible)
- If `.pyc` files corrupted, **specific code paths** (cron executor) could fail while others (Telegram polling, CLI) work
- **Check:** Look for `marshal data too short` errors in `journalctl` filtered by agent PIDs
- **Test:** Clear all `__pycache__` and `.pyc`, restart gateways

### H5: Provider auth pipeline desynchronization
- All 4 agents use the same Nous/StepFun model credentials via shared `auth.json`
- If token expired **but Telegram still polls**, the gateway would accept cron triggers but crash when executor tries to call provider
- **Check:** `errors.log` for `Refresh session has been revoked` or `No access token found`
- **Test:** Run `hermes model` to refresh Nous auth; then restart gateways

---

## Immediate Diagnostic Commands (run now)

```bash
# 1. Check executor crash traces
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent gateway.log — last 50 lines ==="
  tail -50 /root/.hermes/profiles/$agent/logs/gateway.log | grep -E 'cron|executor|exception|error|traceback' | tail -10
  echo
done

# 2. Scan for any marshal errors via journalctl (gateway PIDs from gateway.pid)
for agent in gentech yoyo dmob desmond; do
  pid_file="/root/.hermes/profiles/$agent/gateway.pid"
  if [ -f "$pid_file" ]; then
    pid=$(python3 -c "import json; print(json.load(open('$pid_file'))['pid'])" 2>/dev/null)
    echo "=== $agent (PID $pid) — journalctl marshal errors ==="
    journalctl --since today | grep "python\[$pid\]" | grep -E 'marshal data too short|exception|error' | tail -5 || echo "None found"
    echo
  fi
done

# 3. Check for kanban notifier I/O errors in gateway logs
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent kanban errors ==="
  grep -E 'kanban|notifier|I/O|sqlite|OperationalError|database is full' \
    /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null | tail -5
  echo
done

# 4. Verify system disk health (inodes, space)
df -h /root
df -i /root

# 5. Check if hermes-agent package was updated recently
ls -la /usr/local/lib/hermes-agent | head -20
git -C /usr/local/lib/hermes-agent log --oneline -5 2>/dev/null || echo "No git history (not a git install?)"

# 6. Check gateway.lock directory for Telegram locks
ls -la /root/.local/state/hermes/gateway-locks/ 2>/dev/null || echo "No gateway-locks dir"
```

---

## Recovery Playbook (tentative — await root cause)

If H1/H2/H3 executor crash is confirmed:

```bash
# Step 1: Stop all gateways (force kill if PID files stale)
pkill -9 -f "hermes gateway run" 2>/dev/null || true
sleep 2

# Step 2: Clear ALL gateway locks and state
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/*.lock

# Step 3: Clear cron caches (forces state reload)
for agent in gentech yoyo dmob desmond; do
  rm -f /root/.hermes/profiles/$agent/cron/*.db 2>/dev/null
  rm -f /root/.hermes/profiles/$agent/cron/*.state 2>/dev/null
  # Also clear corrupted .pyc if any marshal errors seen
  find /root/.hermes/profiles/$agent -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
done
# Clear shared agent bytecode cache too (if marshal errors present)
find /usr/local/lib/hermes-agent -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 4: Sequential restart with 10s stagger (longer than usual due to suspected executor cold-start cost)
AGENTS=(yoyo dmob desmond gentech)
for agent in "${AGENTS[@]}"; do
  profile="/root/.hermes/profiles/$agent"
  echo "Starting $agent..."
  HERMES_HOME="$profile" nohup \
    /usr/local/lib/hermes-agent/venv/bin/python3 \
    /usr/local/bin/hermes gateway run \
    >> "$profile/logs/gateway.out" 2>&1 &
  sleep 10  # 10s stagger
done

# Step 5: Wait and verify
sleep 30

# Check processes
ps aux | grep 'hermes gateway run' | grep -v grep | wc -l  # should be 4

# Check for stale PIDs again
for agent in gentech yoyo dmob desmond; do
  pid_file="/root/.hermes/profiles/$agent/gateway.pid"
  if [ -f "$pid_file" ]; then
    pid=$(python3 -c "import json; print(json.load(open('$pid_file'))['pid'])" 2>/dev/null)
    if ! ps -p $pid > /dev/null 2>&1; then
      echo "⚠️  $agent PID $pid still DEAD after restart"
    else
      echo "✓ $agent PID $pid running"
    fi
  fi
done

# Step 6: Check cron executor logs
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent cron activity post-restart ==="
  grep -E 'cron ticker|checking jobs|executing job|Running job' \
    /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null | tail -10
  echo
done

# Step 7: Check if first cron job executed
sleep 65  # wait for next tick (Gentech Watchdog every 5 min; ticker interval 60s)
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent after 65s ==="
  ls -la /root/.hermes/profiles/$agent/cron/output/ 2>/dev/null || echo "No output dir"
done
```

**Success criteria:**
- All 4 gateways running with fresh PIDs
- `gateway.log` shows both `cron ticker started` AND `checking X jobs` → `executing job` lines
- New output directories created in `cron/output/` with timestamps after restart
- Watchdog job completes and reports healthy status in Mess Hall

**If recovery fails:** Escalate to full reactivation procedure (`devops/gentech-agent-reactivation`), but **DO NOT** just `gateway stop && gateway start` — the kill-switch will just resurrect dead state. Must clear caches and state first.

---

## Correlation Matrix

| Symptom | gateway.log | agent.log | cron/output | system cron | Likely cause |
|---------|-------------|-----------|-------------|-------------|--------------|
| Gateways running, cron never fired | shows `ticker started` but no `checking` | maybe old entries | all old, no new | runs normally | Executor thread dead/crashed (H1, H2, H3) |
| Gateways running, cron fires but jobs fail | `executing` → `exception` | errors after `Running job` | has new but partial | irrelevant | Job-specific error (provider auth, profile config) |
| Gateways dead, cron not running | last entry hours ago | last entry hours ago | all old | runs normally | Gateway process crashed (ticker + executor died) |
| Gateways dead, cron running via system-cron | N/A | has `cron_` sessions | all old | irrelevant | CLI-only mode (gateway dead but cron triggers accepted by fallback?) |

This incident matches the **"Gateways dead, cron not running"** quadrant, but with the nuance that **the CLI thread remains alive** (agent.log gets `cron_` prefixed sessions). The cron ticker is **not running**; those `cron_` sessions come from **direct manual/cron-trigger invocation paths** that don't require the executor.

---

## Detection Rule (for future Watchdog runs)

Add this check to the Watchdog skill:

```yaml
checks:
  - name: "cron_executor_health"
    description: "Ensure cron ticker AND executor are both active"
    test: |
      # Check if ticker is alive (gateway.log has recent 'ticker started')
      ticker_recent=$(grep -c 'Cron ticker started' /root/.hermes/profiles/*/logs/gateway.log | tail -1)
      # Check if executor dispatched (gateway.log has 'checking' or 'executing')
      executor_recent=$(grep -c -E 'checking|executing job' /root/.hermes/profiles/*/logs/gateway.log | tail -1)
      if [ "$ticker_recent" -gt 0 ] && [ "$executor_recent" -eq 0 ]; then
        echo "⚠️ T ticker alive but executor deadlocked/crashed"
        exit 2
      elif [ "$ticker_recent" -eq 0 ]; then
        echo "⚠️ Ticker subsystem not running at all"
        exit 2
      else
        echo "✓ Cron subsystem healthy"
        exit 0
      fi
    interval: "*/5 * * * *"
```

---

## Lessons Learned

1. **Split health model**: Gateway health is not binary. Separate monitoring dimensions:
   - **CLI process** (Telegram poller, command responder) — can stay alive while gateway dies
   - **Gateway subsystem** (cron ticker + job executor) — dies independently
   - Check **both** in health checks, not just `ps aux | grep gateway`

2. **`last_run: never` is a critical red flag** — not "cron not due yet." Means ticker never successfully completed a cycle since state initialization (April 28–30).

3. **System cron vs embedded cron** — Brain-backup running proved host cron works. This immediately isolates the problem to Hermes embedded scheduler, not host OS.

4. **Gateway PID JSON format** — Already known, but reinforced. A script that tries `kill $(cat gateway.pid)` will silently fail because the file content is `{"pid": 123, ...}` not `123`. Always parse with `json.load()`.

5. **gateway.pid becomes stale but not cleared** — When gateway dies abnormally (SIGKILL, power loss), the PID file remains. Health check must cross-validate `ps aux` vs `gateway.pid` contents.

---

## Open Questions (require deeper investigation)

1. **Why did ticker/executor die?** Still unknown as of 08:12. Need gateway.log crash traces.
2. **Did this happen during/after a specific cron job run?** The `The Brain — Daily` was scheduled for 16:00 UTC yesterday; may have been running at ~04:00 when failure occurred.
3. **Is this reproducible?** Attempting restart now may just resurrect broken state. Must clear caches first (Phase 7 Step A).
4. **Disk I/O health?** Run `dmesg | tail -20` to check for I/O errors; inode exhaustion could explain DB corruption.
5. **Shared Python venv corruption?** All agents use same `/usr/local/lib/hermes-agent/venv/`. If that venv's `.pyc` files corrupted, all agents suffer same executor crash.

---

## Action Items

- [ ] **A1.** Run diagnostic commands above, capture gateway.log crash tail
- [ ] **A2.** Check `journalctl -n 100` for kernel I/O errors or OOM kills
- [ ] **A3.** If marshal errors found → clear all `__pycache__` per Phase 3.5
- [ ] **A4.** If cron cache corruption → clear `cron/*.db` and `cron/*.state` per Phase 7
- [ ] **A5.** Restart gateways with 10s stagger (extended from 5s)
- [ ] **A6.** After restart, verify first complete job run (output file created)
- [ ] **A7.** If restart fails to revive cron executor → escalate to `devops/gentech-agent-reactivation` with full state dump

---

## References

- Skill: `gentech-agent-health-diagnosis` — Primary diagnostic playbook
- Skill: `devops/gentech-agent-reactivation` — Heavyweight recovery procedures
- Session: 2026-05-02 — Watchdog health check discovery transcript
- Related: `references/2026-05-01-multi-agent-failure-patterns.md` (bytecode corruption + cascade crash patterns)
- Related: `references/2026-05-02-bytecode-corruption-yoyo-gentech.md` (marshal errors investigation)

---

**Classification:** P1 — Total automation paralysis  
**Blame:** Ticker scheduler subsystem (cron executor) — all agents simultaneously affected  
**Status:** OPEN — awaiting gateway log analysis and cache-clear restart
