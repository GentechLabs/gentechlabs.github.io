# 2026-05-04 — YoYo Duplicate Cron Execution Detection

**Agent**: YoYo
**Job**: D5 Milestone + LP Monitor (`defi-milestone-tracker.py`)
**Job IDs observed**: `9ecfada01952` (system cron), `3258c64b` (internal Hermes cron)
**Schedule**: Expected */10 minutes; actual ~*/5 minutes due to duplication
**Severity**: Medium (noise, wasted resources, confusing logs)
**Status**: Open (requires removal of one trigger)

## Symptom

YoYo cron sessions appearing every 5 minutes instead of every 10. Analysis of last 10 sessions showed:

```
session_cron_9ecfada01952_20260504_175032.json  (17:50:34)
session_cron_3258c64b_20260504_175032.json       (17:50:33)  ← same minute
session_cron_9ecfada01952_20260504_174531.json  (17:45:32)
session_cron_9ecfada01952_20260504_174029.json  (17:40:31)
session_cron_3258c64b_20260504_174029.json       (17:40:31)  ← same minute
... repeating pattern ...
```

Average interval computed from last 20 sessions: ~4 minutes (expected 10).

## Root Cause

Two independent cron triggers executing the same script:

1. **System crontab** (root user, `/var/spool/cron/crontabs/root`):
   ```
   */10 * * * * HERMES_HOME=/root/.hermes/profiles/yoyo /usr/bin/env python3 /root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py >> /root/.hermes/profiles/yoyo/cron.log 2>&1
   ```

2. **Internal Hermes cron job** (YoYo profile, `/root/.hermes/profiles/yoyo/cron/jobs.json`):
   - Job ID: `3258c64b`
   - Name: "Defi Milestone"
   - Schedule: `*/10 6-23 * * *`
   - Script: `/root/.hermes/scripts/d5-lp-consolidated.py` (symlink/copy of same tracker)

Both schedules are `*/10`, but because they are offset by a few seconds (system cron fires at :00, :10, :20...; internal Hermes cron fires slightly after the tick), they cluster into apparent 5-minute spacing. The session prefix differs (`9ecfada01952` = system cron wrapper, `3258c64b` = internal Hermes cron).

## Detection Method

```python
from pathlib import Path
from datetime import datetime, timezone

agent_dir = Path("/root/.hermes/profiles/yoyo/sessions")
cron_sessions = sorted(agent_dir.glob("session_cron_*.json"), key=lambda p: p.stat().st_mtime)
times = [datetime.fromtimestamp(s.stat().st_mtime, tz=timezone.utc) for s in cron_sessions[-20:]]
intervals = [(times[i+1] - times[i]).total_seconds() / 60 for i in range(len(times)-1)]

avg_interval = sum(intervals) / len(intervals)
print(f"Average interval: {avg_interval:.1f} min (expected ~10)")

# Count distinct job ID prefixes in filenames
prefixes = set()
for s in cron_sessions[-50:]:
    # prefix is part between "session_cron_" and first underscore after
    name = s.name  # e.g., session_cron_9ecfada01952_20260504_175032.json
    # extract the first hex segment
    import re
    m = re.match(r'session_cron_([a-f0-9]+)_', name)
    if m:
        prefixes.add(m.group(1))
print(f"Distinct prefixes: {prefixes}")
```

If `len(prefixes) > 1` and average interval ≈ expected_interval / 2 → duplicate execution.

## Remediation

Choose one mechanism:

**Option A — Keep Hermes internal cron (recommended)**:
- Remove system crontab entry: `crontab -e` (as root) and delete the `*/10 * * * * HERMES_HOME=... defi-milestone-tracker.py` line
- Keep internal Hermes cron job `3258c64b` active
- Benefits: Integrated logging, exit code handling, Telegram delivery built-in, graceful error handling

**Option B — Use system crontab only**:
- Delete Hermes internal cron job: `hermes cron delete 3258c64b` (or delete from `/root/.hermes/profiles/yoyo/cron/jobs.json` and restart YoYo gateway)
- Keep system crontab entry
- Drawbacks: Less integrated; script must handle all output/retry itself

**Validate fix**:
```bash
# Wait 30 min then check interval drift
python3 -c "…interval script above…"
# Should show ~10 min average
```

## Related Patterns

- `agent-health-audit` → Pattern: Duplicate Cron Execution Detection
- `cron-job-audit` (if present) → cross-check job registry consistency
