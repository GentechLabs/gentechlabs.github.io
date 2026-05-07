# Agent Cron Patterns Reference

## Log Patterns for Cron Health Verification

### Evidence of Active Cron Execution

**Job dispatch** (PROOF of execution):
```
INFO cron.scheduler: Running job 'Gentech Watchdog' (ID: 9ecfada01952)
INFO cron.scheduler: Job '9ecfada01952': completed successfully
```

**Cron ticker lifecycle** (does NOT prove job execution):
```
INFO gateway.run: Cron ticker started (interval=60s)
INFO gateway.run: Cron ticker stopped
```
These only indicate the ticker thread is alive. **Critical**: Ticker running + zero "Running job" messages for >2x schedule window = **stuck cron**.

### Session Context vs Actual Execution

**Session ID in logs** (misleading if used alone):
```
INFO [cron_9ecfada01952_20260502_022040] agent.auxiliary_client: Auxiliary auto-detect...
```
The `[cron_9ecfada01952_...]` prefix is a **logging context** injected when a cron job spawns a session. It does NOT mean the job successfully executed or completed. Always verify by finding the actual `cron.scheduler: Running job` line earlier in the log for the same timestamp window.

### Normal Cron Timeline (healthy agent)

```
HH:MM:SS,ms INFO gateway.run: Cron ticker started (interval=60s)
HH:MM:SS,ms INFO cron.scheduler: Running job 'Job Name' (ID: abc123)
HH:MM:SS,ms INFO [cron_abc123_...] agent.auxiliary_client: Auxiliary auto-detect...
HH:MM:SS,ms INFO cron.scheduler: Job 'abc123': completed successfully
```

### Stuck Cron Signatures

**Pattern A** — Ticker restarts repeatedly with no job dispatch:
```
INFO gateway.run: Cron ticker stopped
INFO gateway.run: Cron ticker started (interval=60s)
```
(Repeated every ~60s with ZERO "Running job" messages between restarts)

**Pattern B** — Jobs.json shows errors but ticker never retries:
```json
{
  "last_run_at": "2026-04-24T12:00:00Z",
  "last_status": "error",
  "last_error": "RuntimeError: Refresh session has been revoked"
}
```
No subsequent `Running job` entry in agent.log for same job ID.

### Auth Error Cascade

Refresh session revoked appears in BOTH places:
- errors.log: `ERROR cron.scheduler: Job 'Mess Hall — Mid-Shift' failed: RuntimeError: Refresh session has been revoked`
- agent.log: May show followed by immediate job abort without tool execution

**Correction required**: Run `hermes model` and re-authenticate the affected provider (OpenRouter, Claude, etc.). Jobs will continue to fail until session refreshed.

### DMOB-Specific Pattern (May 02 2026)

```
DMOB cron activity on May 02:
  2026-05-02 00:55:15,688 INFO gateway.run: Cron ticker stopped
  2026-05-02 00:55:18,759 INFO gateway.run: Cron ticker started (interval=60s)
```
NO subsequent `cron.scheduler: Running job` entries for any job. Ticker is alive but **dispatcher not firing**.

### Schedule Frequency Checks

| Schedule | Max expected gap before investigation |
|----------|----------------------------------------|
| */5 * * * * (5 min) | 15 minutes no execution → stuck |
| 0 */6 * * * (6 hours) | 18 hours no execution → stuck (but verify ticker) |
| 0 10,18 * * * (twice daily) | 36 hours no execution → stuck |

**Key**: Always compare against `last_run_at` in jobs.json AND presence of "Running job" in agent.log. If jobs.json shows old last_run but agent.log shows NO cron_* sessions at all in the expected window → ticker not dispatching.
