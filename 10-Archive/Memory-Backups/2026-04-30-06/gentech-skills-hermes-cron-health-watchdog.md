---
name: hermes-cron-health-watchdog
description: "Systematic health diagnostics for multi-agent Hermes cron deployments. Inspects session transcripts, cron metadata, and per-agent output logs to detect stuck jobs, provider failures, and execution anomalies across all profiles."
tags: [hermes, cron, health-check, watchdog, devops, monitoring, multi-agent]
---

# Hermes Cron Health Watchdog

Run a systematic diagnostic sweep across all Hermes agent profiles to detect cron job failures, stuck executions, missed runs, and provider errors before they become outages.

## When to Use

- You are a scheduled watchdog cron job checking on YoYo, DMOB, Desmond, Gentech, or other agent profiles.
- Cron jobs appear to have stopped firing or are producing stale output.
- An agent hasn't reported in longer than its schedule interval.
- You need to distinguish between "silent because healthy" and "silent because broken."
- Post-incident: verify which jobs recovered and which are still stuck after a restart/fix.

## What This Workflow Detects

1. **Stuck `next_run_at`** — job timestamps frozen in the past (scheduler/gateway zombie).
2. **`error` state / failed jobs** — `last_status: error` with `last_run_at` frozen.
3. **Missed executions** — `last_run_at` older than the schedule interval by a large margin.
4. **Provider rate limits** — `HTTP 429: too many concurrent requests` or similar in output logs.
5. **Connection failures** — gateway or Telegram delivery errors in `last_delivery_error`.
6. **Paused / disabled jobs** — `enabled: false` or `state: paused` unexpectedly.
7. **Execution loops** — rapid-fire execution output files (minutes apart) suggest a stuck loop.

## Quick-Start Diagnostic Flow

### Step 1: Query Recent Session Transcripts

Search for known error indicators in recent sessions across all agents:

```python
# In Hermes, this is done via session_search tool
# Keywords: agent names, "error", "crash", "timeout", "failed"
```

Look for:
- Repeated `AttributeError`, `ValueError`, `OSError`
- Gateway disconnect / reconnect loops
- Provider 429 / 502 / 503 responses
- Tool execution failures (e.g. `cronjob`, `browser`)

### Step 2: Inspect Cron Metadata

Run `cronjob list` or inspect raw `jobs.json` for every profile:

```bash
# Raw inspection across all profiles
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  python3 -c "
import json, os
path = f'/root/.hermes/profiles/{p}/cron/jobs.json'
if not os.path.exists(path): print('MISSING'); exit()
with open(path) as f: data = json.load(f)
for j in data.get('jobs', []):
    if not j.get('enabled'): continue
    print(f\"{j['id'][:12]} | {j['name'][:40]:<40} | next={j.get('next_run_at','?')} | last={j.get('last_run_at','?')} | status={j.get('last_status','?')}\")
"
done
```

**Red flags in cron metadata:**
- `last_status: error` — investigate immediately.
- `next_run_at` older than now by more than 1 interval — scheduler is stuck.
- `last_run_at` is more than 2× the schedule interval old — missed executions.
- `state: paused` or `enabled: false` without an explicit pause reason.

### Step 3: Check Cron Output Directories

Each firing creates a file under `~/.hermes/profiles/<profile>/cron/output/<job_id>/`:

```bash
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  ls -lt ~/.hermes/profiles/$p/cron/output/ | head -10
done
```

Look for:
- Jobs with recent `last_run_at` but **no new output files** → job ran but produced no artifact (possible silent fail).
- Jobs with **very old newest file** → not executing.
- Jobs with **hundreds of files in the last hour** → stuck in a run loop.

### Step 4: Search Output Logs for Error Keywords

```bash
for p in yoyo dmob desmond gentech; do
  find ~/.hermes/profiles/$p/cron/output/ -name "*.md" -mtime -1 \
    -exec grep -l -i -E "error|fail|crash|timeout|exception|too many concurrent" {} \;
done
```

For each matching file, read the first and last 20 lines to classify the error:
- **HTTP 429** → provider rate limit; backoff will usually clear it.
- **HTTP 502/503** → transient gateway/provider issue.
- **Tool execution error** (e.g. `cronjob` tool returned malformed data) → investigate tool state.
- **Timeout / hung** → last line is `[SILENT]` with no content before it → job may have been killed.

### Step 5: Correlate Findings

Build a summary table:

| Agent | Job Name | Job ID | Schedule | Last Run | Status | Issue |
|-------|----------|--------|----------|----------|--------|-------|
| YoYo | Crypto Watchlist | faed4f588aef | 4×/day | Apr 28 | ok | **STALE** — no runs since Apr 28 (~2 days missed) |
| YoYo | Mess Hall Pre-Shift | a9880f234c2b | daily | Apr 29 | error | **ERROR STATE** since Apr 22 |
| YoYo | Mess Hall Post-Shift | cd3a275dbae3 | daily | Apr 29 | error | **RATE LIMIT** HTTP 429 on latest run |

### Step 6: Report

If **all agents healthy** → output exactly `STATUS:OK` and nothing else. No verbosity.

If **issues found** → output structured alert, one per line:

```
🚨 Watchdog Alert: Agent <Name> job '<Job Name>' (<job_id>) — <short description>
🚨 Watchdog Alert: Agent <Name> job '<Job Name>' (<job_id>) — <short description>
```

## Target Paths and Files

| Path | Purpose |
|------|---------|
| `~/.hermes/profiles/<profile>/cron/jobs.json` | Canonical job definitions and next-run timestamps |
| `~/.hermes/profiles/<profile>/cron/output/<job_id>/` | Per-job execution artifacts (`.md` logs) |
| `~/.hermes/profiles/<profile>/cron/output/<job_id>/<timestamp>.md` | Single execution log with full prompt + response |

## Common Failure Signatures

### Stale `next_run_at`
- `next_run_at` is hours/days in the past.
- Fix: recalculate timestamps via Python + `croniter`, then restart gateway.
- See `hermes-agent` skill section "Cron jobs stuck — next_run_at in the past."

### Gateway Zombie (process alive, scheduler dead)
- `last_run_at` hasn't updated for days despite valid `next_run_at`.
- `ps aux | grep hermes` shows PID.
- Fix: `hermes gateway run --profile <profile> --replace`
- See `hermes-agent` skill section "Cron zombie."

### Provider Rate Limit (HTTP 429)
- Output response ends with: `API call failed after 3 retries: HTTP 429 ...`
- Usually self-healing on next interval. If persistent across 3+ runs, consider lowering frequency or switching provider.

### Model-Level Empty Response (No Content)
- `last_status: error` with message: `Agent completed but produced empty response (model error, timeout, or misconfiguration)`.
- Indicates the provider returned an empty completion (not a rate limit or crash). Check provider health / model availability.
- Often coincides with high load or model switches.
- Fix: verify model is available; if transient, next run usually clears it.

### Script Missing / Path Drift
- Cron output shows: `Script not found: /path/to/script.py`.
- Script was deleted, moved, or never created. Also triggered when a profile is rebuilt and scripts directory is not restored.
- Cross-check `~/.hermes/profiles/<profile>/scripts/` — if the expected script is absent, recreate it or update the cron job to point to the correct path.
- Fix: restore script from backup (e.g., vault or GitHub) or update the job's script config.

### Job Removed from List
- Job was present in `jobs.json` yesterday, gone today.
- Hermes auto-removes jobs that fail repeatedly.
- Fix: identify root cause, then recreate via `hermes cron create`.

### Execution Loop (runaway job)
- Same `job_id` directory has new files every minute instead of every N hours.
- Usually caused by a job that triggers itself or a webhook that loops.
- Fix: `hermes cron pause <id>`, investigate prompt for self-triggering patterns.

## Pitfalls

- **Don't rely solely on `cronjob list`**. It only shows metadata. Always check `cron/output/` directories to confirm execution actually produced output.
- **Don't conflate "no new output" with "job failed."** Some jobs are designed to return `[SILENT]` when nothing is new. Check the `.md` file content — if the last line says `[SILENT]` and earlier lines show healthy reasoning, it's fine.
- **Cross-profile jobs with same IDs** — some jobs (`9ecfada01952`) exist in multiple profiles. Be explicit about which profile the alert refers to.
- **Disabled / paused jobs** — intentionally paused jobs (`enabled: false`) should NOT trigger alerts unless they were paused unexpectedly.
- **Time zones** — `last_run_at` and `next_run_at` are in ISO 8601 UTC. Always compare against `datetime.now(timezone.utc)`.

## Verification

After running the workflow, confirm:
- [ ] All agent profiles inspected (not just the running profile).
- [ ] Every `last_status: error` flagged in the report.
- [ ] Every stale `next_run_at` flagged in the report.
- [ ] Error-keyword grep results reviewed, not just counted.
- [ ] Report is either exactly `STATUS:OK` or contains actionable alerts with job IDs.
