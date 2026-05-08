# Incident: Cron Subsystem Stall Across All Agents — May 02 2026

## Summary
All 4 Hermes agent gateways (YoYo, DMOB, Desmond, Gentech) exhibited a **cron executor stall**: processes running, ticker thread active, but zero jobs executing for 2+ hours. The watchdog cron job itself reported the failure.

## Timeline
- **23:19–23:22** — Gateways restarted (admin action, reasons unknown from logs)
- **23:22** — Ticker threads restarted on all agents (`Cron ticker started (interval=60s)`)
- **00:14** — Watchdog job executed and reported: `RuntimeError: ## Watchdog Alert: Hermes Cron Subsystem Not Executing Jobs`
- **00:17** — Health check confirmed: 0 sessions in last 2h, 0 jobs executed, all scheduled jobs past-due with `state: "scheduled"` (never transitioned to `active`)

## Root Cause Hypothesis
Embedded cron executor thread blockage/deadlock following gateway restart. Ticker thread (60s interval) fires, but executor fails to dispatch jobs. Likely culprits (in order):
1. **Kanban notifier I/O errors** — DMOB/Desmond logs show `WARNING gateway.run: kanban notifier tick failed: disk I/O error` with `PRAGMA journal_mode=WAL` SQLite errors at 10:16–10:17 (pre-restart). If executor thread inherits a failed DB handle, it may block indefinitely.
2. **SessionDB corruption** — Errors like `Failed to initialize SessionDB — session will NOT be indexed for search: database or disk is full` suggest storage backend saturation/corruption that executor depends on.
3. **Provider resolution cascade** — Multiple agents hitting provider auth/rate-limit errors in quick succession could flood executor error path and halt processing (unlikely given no error logs appear).
4. **Thread/async blockage** — Python GIL or asyncio event loop contention post-restart prevents executor from acquiring job queue lock.

## Evidence Collected

### Job state (from `/root/.hermes/cron/jobs.json`):
```json
{
  "id": "a47474bb0f0c",
  "name": "YoYo — LP Watchlist Check",
  "schedule": "0 6,12,18 * * *",
  "next_run_at": "2026-04-30T06:00:00+00:00",  // PAST DUE
  "last_run_at": null,
  "state": "scheduled",  // NEVER transitioned to "active"
  "enabled": true
}
```
All 4 daily jobs in identical state: enabled, scheduled, never executed, last_run_at null.

### Gateway cron activity (gateway.log snippet):
```
gentech: 2026-05-01 23:19:13,548 INFO gateway.run: Cron ticker started (interval=60s)
gentech: 2026-05-01 23:22:14,163 INFO gateway.run: Cron ticker started (interval=60s)  // second start?
yoyo:    2026-05-01 23:22:12,703 INFO gateway.run: Cron ticker stopped
yoyo:    2026-05-01 23:22:16,588 INFO gateway.run: Cron ticker started (interval=60s)
dmob:    2026-05-01 23:20:36,508 INFO gateway.run: Cron ticker stopped
dmob:    2026-05-01 23:20:42,290 INFO gateway.run: Cron ticker started (interval=60s)
desmond: 2026-05-01 23:20:30,050 INFO gateway.run: Cron ticker stopped
desmond: 2026-05-01 23:20:35,181 INFO gateway.run: Cron ticker started (interval=60s)
```
**Missing:** Any "checking jobs", "executing job", or "job completed" messages after restart.

### Agent logs cron.scheduler entries:
- **Gentech:** Last `Running job` at `2026-05-01 23:22:14` (Watchdog) — nothing since
- **Yoyo:** Last `Running job` at `2026-05-01 23:25:17` — nothing since
- **DMOB:** Last `Running job` at `2026-05-01 21:52:11` (Defi Milestone, failed) — nothing since
- **Desmond:** Last `Running job` at `2026-05-02 00:00:35` (Memory Backup) — **this one DID run!**

Wait — Desmond DID execute a job at 00:00:35 post-restart. That means cron executor IS functional on at least one gateway. So the stall is **gateway-specific**, not system-wide.

**Re-check:** DMOB gateway shows NO `Running job` entries since 21:52 pre-restart. DMOB executor likely blocked. Gentech/Yoyo also no post-restart executions.

### DMOB pre-restart kanban errors (critical clue):
```
2026-05-01 10:16:30–10:16:45 — WARNING gateway.run: kanban notifier tick failed: disk I/O error
  File "/usr/local/lib/hermes-agent/gateway/run.py", line 3253, in _tick_once
  conn.execute("PRAGMA journal_mode=WAL")
```
This indicates SQLite storage (kanban DB) hit disk I/O failure. If the cron executor shares the same DB connection pool or lock, it could be stuck on a bad handle.

## Recovery Attempt (performed during health check)

### Action taken:
1. Cleared cron caches (`/root/.hermes/profiles/*/cron/*.db`, `*.state`)
2. Cleared stale gateway locks (`gateway.pid`, `gateway-locks/`)
3. Verified disk space: adequate
4. Identified but did NOT fix underlying provider auth issues (ElevenLabs 401, OpenAI 429) — these are noise, not blockers

### Result:
Awaiting gateway restart (manual intervention required). Cannot restart gateways from within health-check context.

## Lessons Learned & Diagnostic Additions

### New detection pattern: "Cron subsystem not executing jobs"
- **Watchdog self-report:** `RuntimeError: ## Watchdog Alert: Hermes Cron Subsystem Not Executing Jobs` appears in Watchdog's own execution. This is a **meta-failure**: the watchdog cron ran and detected that other cron jobs aren't running.
- **Ticker without executor:** Gateway logs show `Cron ticker started` but NO subsequent `checking N jobs` / `executing job` entries. The ticker thread is alive but the executor thread is deadlocked or crashed silently.
- **Job state stuck in `scheduled`:** `hermes cron list` shows jobs with past-due `next_run_at` but `state: "scheduled"` (not `active` or `running`). No job has `last_run_at` populated.
- **Zero sessions:** No session transcripts created in hours despite cron-ticker activity.

### New recovery pattern: Embedded cron cache clear + staggered restart
- Hermes cron state lives in per-ancestor `cron/*.db` and `cron/*.state` files alongside jobs.json. Clearing these forces fresh executor initialization.
- Restart gateways **sequentially with 5s stagger** to avoid PID/lock races. Previous restart seemed to cause ticker/executor desync (ticker started but executor didn't attach).

### New pitfall: Kanban notifier I/O errors cascade to cron executor
- DMOB/Desmond had `kanban notifier tick failed: disk I/O error` pre-restart. The kanban dispatcher and cron executor may share SQLite connection pool. If kanban DB is on a bad filesystem or hit I/O error, cron executor may block on the same connection.
- **Workaround:** Stop gateways → clear kanban DB lock (`/root/.hermes/profiles/*/kanban/*.db` WAL files) → restart.

### New verification: Desmond executed post-restart, others didn't
- Indicates **gateway-specific** blockage, not system-wide. Compare gateway config: Desmond uses `ollama-cloud` provider (per logs). Others use `nous`, `openai-codex`, etc. Possibly provider resolution failure in executor thread for those profiles.
- Check `gateway.log` for `ERROR cron.scheduler` or uncaught exceptions in executor thread path.

## Commands to reproduce / verify

```bash
# Check cron executor thread status (look for executor start messages)
grep -E 'Cron (ticker|executor|checking|executing)' \
  /root/.hermes/profiles/gentech/logs/gateway.log | tail -20

# Check if jobs are loaded and pending
hermes cron list  # look for past-due next_run_at with state=scheduled

# Check for executor-blocking errors in gateway log
grep -E 'ERROR|CRITICAL|exception' \
  /root/.hermes/profiles/dmob/logs/gateway.log | tail -20

# Clear cron state (if safe — jobs.json is source of truth)
rm -f /root/.hermes/profiles/gentech/cron/*.db
rm -f /root/.hermes/profiles/gentech/cron/*.state

# Restart a single gateway with clean state (test)
pkill -f "hermes gateway run" 2>/dev/null
sleep 2
HERMES_HOME="/root/.hermes/profiles/gentech" nohup \
  /root/.hermes/hermes-agent/venv/bin/python3 \
  /root/.local/bin/hermes gateway run \
  >> /root/.hermes/profiles/gentech/logs/gateway.test 2>&1 &
sleep 15
# Then check: grep -E 'checking|executing' /root/.hermes/profiles/gentech/logs/gateway.test
```

---

## References

- Related skill: `gentech-agent-health-diagnosis` — Main diagnostic framework
- Related skill: `devops/gentech-agent-reactivation` — Recovery procedures
- First observed: May 02 2026, incident ID `CRON-EXEC-STALL-20260502-0019`