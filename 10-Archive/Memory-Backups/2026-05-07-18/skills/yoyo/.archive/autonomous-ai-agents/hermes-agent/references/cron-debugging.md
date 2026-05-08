# Hermes Cron Subsystem — Diagnostic Reference

## Quick Diagnosis Flow

```bash
# 1. Are gateways running?
pgrep -f "hermes.*gateway run"

# 2. Does each gateway see the cron ticker?
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent ==="
  tail -20 ~/.hermes/profiles/$agent/logs/gateway.log | grep -i "cron ticker"
done

# 3. Are any job-checking logs present?
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent ==="
  grep -ic "checking\|executing job" ~/.hermes/profiles/$agent/logs/gateway.log || echo "0"
done

# 4. Inspect job states (disabled/paused?)
python3 -c "
import json, glob
for p in ['gentech','yoyo','dmob','desmond']:
    d = json.load(open(f'/root/.hermes/profiles/{p}/cron/jobs.json'))
    bad = [j for j in d['jobs'] if not j['enabled'] or j['state']=='paused']
    if bad:
        print(f'{p}: {len(bad)} disabled/paused jobs')
        for j in bad[:3]:
            print(f\"  - {j['name']} [{j.get('schedule','')}] state={j['state']}\")
"

# 5. Check for overdue jobs not firing
python3 -c "
import json, datetime
d = json.load(open('/root/.hermes/profiles/gentech/cron/jobs.json'))
now = datetime.datetime.now(datetime.timezone.utc)
due = [j for j in d['jobs'] if j.get('next_run_at') and datetime.datetime.fromisoformat(j['next_run_at'].rstrip('Z')) < now]
print(f'Overdue jobs (should have fired): {len(due)}')
for j in due:
    print(f\"  {j['name']} -> next={j['next_run_at']} last={j.get('last_run_at')} enabled={j['enabled']} state={j['state']}\")
"

# 6. Search gateway.log for cron executor errors
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent ==="
  grep -i \"error\\|exception\\|blocked\\|cron\" ~/.hermes/profiles/$agent/logs/gateway.log | tail -20
done
```

## Typical Cron Job JSON Skeleton

```json
{
  "id": "682e9597b8d6",
  "name": "Job Name",
  "prompt": "What to do",
  "schedule": {
    "kind": "cron",
    "expr": "0 5 * * *",
    "display": "0 5 * * *"
  },
  "enabled": true,
  "state": "scheduled",
  "next_run_at": "2026-05-02T05:00:00+00:00",
  "last_run_at": null,
  "last_status": null,
  "last_error": null,
  "action_type": "message",      // critical: "message" or "run_script"
  "deliver": "telegram:-1003863540828",
  "model": "stepfun/step-3.5-flash",
  "provider": "nous"
}
```

**Key fields**:
- `action_type`: if missing, job is silently skipped
- `enabled`: must be `true`
- `state`: should be `"scheduled"` (not `"paused"` or `"failed"`)
- `next_run_at`: ISO timestamp; if in past and job is enabled, ticker should fire it
- `deliver`: Telegram chat ID; if invalid, delivery fails but job still executes

## Cron Ticker vs Executor Separation

The gateway log sequence **should** look like:
```
... gateway.run: Cron ticker started (interval=60s)
... cron.scheduler: Checking scheduled jobs at 2026-05-02T00:15:00Z
... cron.executor: Executing job 'Gentech Watchdog' (ID: ...)
... cron.delivery: Delivered to telegram:-100386354028
```

If you see **ticker started** but **no "Checking scheduled jobs"** lines, the executor thread is not running or is blocked.

## Recovery Commands

```bash
# Clean gateway restart (recommended first step)
hermes -p gentech gateway stop
hermes -p gentech gateway start

# If jobs are paused but should be enabled
hermes cron resume <job-id>

# Force-recompute next_run_at for all jobs (re-schedule from now)
# WARNING: resets timing; use sparingly
python3 -c "
import json, datetime, glob
for p in ['gentech','yoyo','dmob','desmond']:
    path = f'/root/.hermes/profiles/{p}/cron/jobs.json'
    d = json.load(open(path))
    changed = False
    for j in d['jobs']:
        if j.get('next_run_at'):
            j['next_run_at'] = None  # let scheduler recompute on next tick
            changed = True
    if changed:
        json.dump(d, open(path, 'w'), indent=2)
        print(f'{p}: cleared next_run_at for {sum(1 for j in d[\"jobs\"] if j.get(\"next_run_at\") is None)} jobs')
"

# Verify after restart: watch gateway.log for 2-3 minutes
tail -f ~/.hermes/profiles/gentech/logs/gateway.log
```

## Distinguishing Hermes Cron vs System Cron

Some scheduled tasks (like brain backup) may be driven by **system cron** rather than Hermes internal cron:

- **Hermes cron**: jobs defined in `~/.hermes/profiles/*/cron/jobs.json`, executed by gateway process, sessions logged in `~/.hermes/sessions/`
- **System cron**: systemd timers or crontab entries that call `hermes` CLI directly; may not create session files

If a job appears in `brain-backup.log` but not in `hermes cron logs`, check system crons:
```bash
crontab -l 2>/dev/null || echo "no user crontab"
systemctl list-timers --all | grep -i hermes
```

## Known Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Ticker starts, no job logs | Event loop blocked by another tool | Restart gateway; check for long-running terminal/web tasks |
| `hermes cron list` empty | Cron executor thread dead; gateway needs restart | `hermes gateway restart` |
| Jobs overdue but `next_run_at` is ancient (e.g., Apr 22) | Job was paused when due; resuming doesn't backfill; next_run stuck in past | Manually set `next_run_at` to a near-future time or clear it to force recompute |
| No `action_type` in job JSON | Job created via malformed manual edit | Add `"action_type": "message"` to job object in jobs.json |
| repeated "database or disk is full" | SQLite disk full / inode exhaustion; I/O blocked | Check disk (`df -h`) and inodes (`df -i`); clean logs or increase quota |
