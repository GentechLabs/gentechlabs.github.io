# 2026-05-05: Cron Daemon Lifecycle Tracking — "Cron ticker stopped" While Gateway Running

**Watchdog**: Gentech (May 5, 2026 03:43 UTC)

## Context

During fleet health audit, DMOB and Desmond agent logs showed `Cron ticker stopped` messages followed by no subsequent `Cron ticker started`, even though gateway processes remained running. This indicates the internal cron scheduler thread died silently while the main gateway process stayed alive.

## Log Evidence

**DMOB** (`/root/.hermes/profiles/dmob/logs/agent.log`):
```
2026-05-05 02:26:56,791 INFO gateway.run: Cron ticker stopped
# (no further "Cron ticker started" lines appear after this)
```

**Desmond**:
```
2026-05-05 02:26:56,794 INFO gateway.run: Cron ticker stopped
# (no restart)
```

**YoYo & Gentech** show repeated `Cron ticker started` and no corresponding `stopped` — their cron daemons are healthy.

## Interpretation

- **Normal**: `Cron ticker started` appears once during gateway startup; `Cron ticker stopped` appears only during clean gateway shutdown.
- **Degraded**: `stopped` appears while gateway process is still running → the cron scheduler thread (a Python `threading.Thread` inside the gateway) exited unexpectedly. This is a **silent scheduler crash**.
- **Consequence**: The agent will not execute ANY cron jobs until the gateway is restarted. Direct message handling (via Telegram) may still work if the main event loop is unaffected.

## Why This Happens

The Hermes cron scheduler runs as a background thread within the gateway process. Unhandled exceptions inside the cron thread (e.g., a job that panics without `try/except`, a skill import error that bubbles up during job dispatch, or a hard crash in a scheduled script) can kill the thread while leaving the main process alive. The gateway does not automatically restart the cron thread after such a failure.

## Detection Checklist

```bash
# 1. Confirm process is still running
ps -p $(jq -r .pid /root/.hermes/profiles/<agent>/gateway.pid) -o pid,stat,etime,cmd

# 2. Check agent.log for lifecycle markers
grep 'Cron ticker' /root/.hermes/profiles/<agent>/logs/agent.log | tail -10

# 3. Count starts vs stops
started=$(grep -c 'Cron ticker started' /root/.hermes/profiles/<agent>/logs/agent.log)
stopped=$(grep -c 'Cron ticker stopped' /root/.hermes/profiles/<agent>/logs/agent.log)
echo "starts=$started stops=$stopped"

# 4. Check for actual job execution (if cron were alive)
grep -c '\[cron_' /root/.hermes/profiles/<agent>/logs/agent.log | tail -5
# If zero for many hours despite enabled jobs → cron dead
```

## Recovery

Restart the gateway to respawn the cron thread:

```bash
hermes gateway stop --profile <agent>
hermes gateway run --profile <agent> --replace
```

Post-restart verification:
- `grep 'Cron ticker started' agent.log` should show a fresh timestamp
- Within one schedule interval, first cron job should execute (check `[cron_<id>]` markers)
- Job output files should appear in `/root/.hermes/profiles/<agent>/cron/output/`

## Prevention

1. **Cron thread exception guarding**: Ensure all cron job dispatch paths wrap job execution in broad `try/except` so a single job crash cannot kill the scheduler thread.
2. **Health-check integration**: Add a watchdog cron job that verifies `[cron_<job_id>]` markers appear at the expected frequency for each agent; alert if silent for >2× max interval.
3. **Automatic restart policy**: Consider a wrapper script that monitors `agent.log` for `Cron ticker stopped` and automatically restarts the gateway if detected.

## Related

- `agent-health-audit` pattern: **Cron Daemon Lifecycle Tracking via agent.log Markers**
- See also: `references/2026-05-05-cron-execution-missing-configuration.md` for a related case where multiple agents had zero cron execution due to configuration gaps (DMOB/Desmond) and HOME path errors (YoYo).
