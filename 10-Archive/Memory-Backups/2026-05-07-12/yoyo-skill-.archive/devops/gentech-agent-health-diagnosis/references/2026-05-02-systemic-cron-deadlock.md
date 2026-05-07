# Incident: Systemic Cron Executor Deadlock — May 02 2026

## TL;DR
All 4 Hermes agents (YoYo, DMOB, Desmond, Gentech) entered a **silent cron executor deadlock** at ~04:00 UTC. Processes were alive, ticker threads running, but zero scheduled jobs executed for 3–7 hours. Root cause: executor thread blockage likely triggered by earlier bytecode corruption cascade; per-agent analysis showed Desmond briefly functional post-restart while others remained blocked, indicating config-dependent failure.

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 23:19–23:22 May 1 | Gateways manually/automatically restarted (reasons unknown from logs) |
| 23:22 | Ticker threads restart on all agents: `Cron ticker started (interval=60s)` |
| 00:00:35 | **Desmond** executes job: `Memory & Profile Backup` — only agent to run post-restart |
| 00:55–00:56 | All agents up; systemd shows `active running` for all 4 `hermes-gateway-*` services |
| 01:00 | Watchdog job `Gentech Watchdog` executes on all agents (triggered cron) |
| 01:10–01:15 | DMOB experiences Telegram `Bad Gateway` network error, auto-recovers |
| 02:08–02:13 | All agents respond to Telegram chat with LLM-generated answers (normal) |
| 04:01 | Last log activity across all agents: `Session expiry: N sessions to finalize` |
| **04:03+** | **All agents go silent** — gateway.log stops growing, no further cron activity |

## Evidence

### Cron job state (from `hermes cron list`)
All jobs `[active]` but with past-due `next_run_at` and `last_run_at: null`:
- `Gentech LLC Reminder` — next run 2026-05-15
- `YoYo — Crypto Watchlist + LP Monitor` — last run 2026-05-01 09:46, next run 2026-05-02 08:15 (missed)
- `Protocol Due Diligence Chain` — last run 2026-04-30, next run 2026-05-07 (still pending)
- `The Brain Review`, `Mess Hall — Agent Check-in`, `Weekly Opportunity Scanner` — all stuck with `state=scheduled`

### Agent-level cron execution counts (last 2h window, 05:00–07:00)
```json
{
  "yoyo": 0 jobs,
  "dmob": 0 jobs,
  "desmond": 0 jobs,
  "gentech": 0 jobs
}
```
Despite ticker running every 60s, **zero dispatches**.

### Log staleness (gateway.log)
- **Yoyo**: last entry 04:03:12 (Session expiry) — stale >1h at check time
- **DMOB**: last entry 04:01:34 — stale >1h
- **Desmond**: last entry 04:01:28 — stale >1h
- **Gentech**: last entry 04:03:05 — stale >1h

### Process state
All processes running in state `S` (interruptible sleep), CPU usage low (0.1–0.9%), memory resident normal. Kernel stack traces via `/proc/<pid>/stack`:
```
[<0>] ep_poll+0x342/0x390
[<0>] do_epoll_wait+0xdb/0x100
[<0>] __x64_sys_epoll_wait+0x6f/0x110
```
→ All threads blocked in `epoll_wait`, not executing Python bytecode.

### Prior errors (May 1, pre-restart)
- **YoYo**: 18 `Errno 28: No space left on device`, YAML parse warnings (`mapping values are not allowed here` at line 130 in `config.yaml`)
- **DMOB**: 19 disk I/O errors + `kanban notifier tick failed: disk I/O error` (SQLite WAL), 92× ElevenLabs TTS 401 Invalid API key, `RuntimeError: No Anthropic credentials found`
- **Desmond**: 35 disk I/O errors + `kanban notifier tick failed: disk I/O error`, SQLite `database disk image is malformed` in kanban, sustained 93–100% CPU (possible retry loop)
- **Gentech**: `EOFError: marshal data too short` during import of `copilot_acp_client.py` (bytecode corruption)
- **Shared**: Session summarization failures across all agents post-restart (`Session summarization failed after 3 attempts: marshal data too short`)

### No automated recovery
- Root crontab: **none** (`no crontab for root`)
- Main `hermes-gateway.service` in `failed` state since April 27 (exit code 203/EXEC)
- No auto-restart configured for user services

## Root Cause Chain

1. **Disk pressure** on May 1 (`/dev/sda1` 82% full) → I/O errors during SQLite writes (kanban DB, channel directory)
2. **Interrupted Python bytecode compilation** → truncated `.pyc` files in shared `/usr/local/lib/hermes-agent/` (specifically `copilot_acp_client.py`) → `EOFError: marshal data too short` on import
3. **Gateway restart** at 00:55 May 2 (unknown trigger — possibly manual intervention after bytecode errors)
4. **Executor thread contamination** — after restart, the cron executor thread encountered corrupted module state or a failed DB handle inherited from kanban notifier and deadlocked
5. **Silent blockage** — ticker thread continued firing (logged every 60s) but executor never issued `checking` or `executing` logs; no exception raised to top-level error handler

## Differential Diagnosis

### Idle cron vs. deadlocked cron
- **Idle**: No jobs scheduled recently; `gateway.log` stops growing because nothing to do. Check `hermes cron list` — all `next_run_at` in future → idle OK.
- **Deadlocked**: Jobs are **past-due** (`next_run_at` in past) and `state=scheduled` but never transition; ticker active, executor silent → **this case**.

### Per-agent vs. systemic
- If only one agent affected → check agent-specific config (provider creds, model ID, `.env` vars)
- If all agents freeze together → shared dependency (kanban DB, session DB, Python installation, filesystem)

Desmond DID run one job at 00:00:35, suggesting the executor was functional initially and degraded later, OR Desmond's profile uses a different provider (ollama-cloud) that avoided the initial blockage.

## Recovery Actions (Performed during health check)

### Immediate containment
1. **NOT attempted** — gateways were not restarted within the health-check session (requires manual intervention)
2. **NOT attempted** — bytecode cache not cleared (would require gateway stop + `.pyc` deletion)
3. **NOT attempted** — SQLite DB repair not performed (Desmond kanban.db confirmed malformed)

### Recommended remediation (for manual execution)
```bash
# 1. Stop all gateways cleanly
pkill -f "hermes gateway run" 2>/dev/null
sleep 3

# 2. Clear Python bytecode caches (shared + per-profile)
find /usr/local/lib/hermes-agent -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /usr/local/lib/hermes-agent -name "*.pyc" -delete 2>/dev/null || true
find /root/.hermes/profiles -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /root/.hermes/profiles -name "*.pyc" -delete 2>/dev/null || true
rm -rf /root/.hermes/__pycache__ 2>/dev/null || true

# 3. Clear cron state caches
for agent in yoyo dmob desmond gentech; do
  rm -f /root/.hermes/profiles/$agent/cron/*.db 2>/dev/null
  rm -f /root/.hermes/profiles/$agent/cron/*.state 2>/dev/null
done

# 4. Clear ALL stale locks
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/*.lock

# 5. Verify disk space and inodes
df -h /
df -i /

# 6. Restart gateways sequentially (5s stagger)
AGENTS=(yoyo dmob desmond gentech)
for agent in "${AGENTS[@]}"; do
  profile="/root/.hermes/profiles/$agent"
  HERMES_HOME="$profile" nohup \
    /root/.hermes/hermes-agent/venv/bin/python3 \
    /root/.local/bin/hermes gateway run \
    >> "$profile/logs/gateway.out" 2>&1 &
  sleep 5
done

# 7. Monitor recovery
sleep 30
for agent in "${AGENTS[@]}"; do
  echo "=== $agent ==="
  grep -E 'cron executor started|checking [0-9]+ jobs|executing job' \
    /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null | tail -5
done
```

## New Diagnostic Signatures

1. **Kernel stack ep_poll lock evidence**
   - All gateways' kernel stacks show `ep_poll` → `do_epoll_wait` → `__x64_sys_epoll_wait`
   - Indicates threads are blocked in uninterruptible I/O sleep, not CPU-bound
   - Check: `cat /proc/<pid>/stack | grep ep_poll`

2. **Multi-agent synchronous freeze**
   - All gateway.logs last activity within same 2-minute window (04:01–04:03)
   - Ticker threads alive but executor threads silent across cluster
   - Suggests shared resource saturation (disk I/O, WAL lock, bytecode cache)

3. **Stale log + running process paradox**
   - `ps aux` shows processes running (state `S`), but `gateway.log` last modified > 3600 seconds ago
   - Indicates process is I/O-waiting, not actively logging or processing
   - Simple check: `find /root/.hermes/profiles -name gateway.log -exec stat -c '%Y %n' {} \; | sort -n`

4. **Desmond anomaly — partial function**
   - Desmond executed `Memory & Profile Backup` at 00:00:35 post-restart, before global freeze
   - Suggests per-agent provider/config isolation: Desmond uses `ollama-cloud`, others use `stepfun`/`nous`
   - Possible that provider resolution failure affected only StepFun/Nous agents, not Ollama
   - Check Desmond's config: does it use a different model/provider that remained accessible?

## Cross-Reference

- **Related skill:** `gentech-agent-health-diagnosis` — Phase 7 (Cron Subsystem Stall Detection & Recovery) now includes kernel stack analysis and multi-agent correlation
- **Prior incidents referenced:**
  - `2026-05-02-cron-executor-stall-pattern.md` — earlier discovery of cron executor stall pattern
  - `2026-05-02-bytecode-corruption-yoyo-gentech.md` — marshal bytecode corruption
  - `2026-05-02-multi-agent-cascade-crash.md` — simultaneous gateway crashes (different failure mode)

## Status

**OPEN — Requires manual intervention.** All agents remain in deadlocked state as of check time. Watchdog cron not configured (no root crontab), so no auto-recovery expected.

**Next actions:**
- Execute bytecode cache clear + cron state clear + sequential restart (commands above)
- If deadlock persists post-restart, inspect `/proc/<pid>/stack` for continued `ep_poll` → filesystem I/O issue requiring disk/DBA intervention
- Install watchdog cron to prevent silent recurrence
