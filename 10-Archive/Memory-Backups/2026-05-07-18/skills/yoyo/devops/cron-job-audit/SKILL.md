---
name: cron-job-audit
description: Systematic audit of Hermes cron job configurations — find broken scripts, delivery errors, stale references, and scheduling issues before they cause silent failures.
version: 1.0.0
author: YoYo
license: MIT
metadata:
  hermes:
    tags: [cron, maintenance, audit, devops, scheduled-jobs]
triggers:
  - cron job health check
  - scheduled job audit
  - cron maintenance
  - "check all cron jobs"
  - weekly cron review
  - cron broken
  - cron job failures
---

# Cron Job Audit

Systematically check all Hermes cron jobs for broken configurations, missing scripts, delivery errors, and scheduling anomalies. Run this weekly or when cron jobs are suspected of failing silently.

## When to Use

- Weekly/biweekly maintenance window
- After gateway restarts or system updates
- When jobs report errors or don't fire as expected
- When adding/removing scripts referenced by cron jobs
- User reports "cron jobs not working"

## Steps

### 1 — List All Jobs

```bash
hermes cron list
```

Capture the full output. Note:
- Job IDs, names, schedules, delivery targets
- `last_run_at` timestamps (when did each last fire?)
- `last_status` and `last_delivery_error` fields
- Any `script` references
- Jobs with `state: "paused"` or `enabled: false`

### 2 — Check for Broken Script References

```bash
# Find all jobs with script references
hermes cron list 2>/dev/null | grep -A2 "Script:"

# For each script path, verify it exists
# Cron job scripts are relative to $HERMES_HOME/scripts/
ls -la ~/.hermes/scripts/cron/skills-update-github-check.sh 2>/dev/null
```

**Pitfall:** A job can reference a non-existent script and still appear "active" — it just won't execute the script. The job runs but produces no useful context for the prompt.

**Fix:** Either create the missing script, remove the `script` field from the job, or disable the job.

### 3 — Check Delivery Targets

```bash
hermes cron list 2>/dev/null | grep "Deliver:"
```

Verify each delivery target exists:
- Telegram targets: use `send_message(action="list")` to see available targets
- Local/origin targets: should work if gateway is running
- Mismatched chat IDs will cause silent delivery failures

### 4 — Check for Jobs That Should Have Run But Haven't

Look for jobs where:
- `enabled: true` AND `state: "scheduled"` (job is active)
- `last_run_at` is older than expected based on schedule
- `next_run_at` is in the past (job should have fired)

**Pitfall:** `last_run_at: null` does NOT mean broken. It means the job has never run — which is normal if:
- The job was recently created
- The gateway was recently restarted and the job hasn't hit its trigger time yet
- The job's schedule hasn't been reached since creation

**Check:** Compare `last_run_at` against the schedule. A daily job that last ran 8+ days ago is suspicious. A monthly job that hasn't run yet is fine.

### 5 — Verify Script Output (If Scripts Exist)

For jobs with scripts, run the script manually to check output:

```bash
bash ~/.hermes/scripts/cron/your-script.sh 2>&1
echo "Exit code: $?"
```

**Pitfall:** A script can run successfully (exit code 0) but produce useless output. Example: a script scanning for git-based skills will output "ALL_CAUGHT_UP" if there are no git skills — technically correct but not useful.

### 6 — Fix Identified Issues

Common fixes:
- **Broken script reference:** `cronjob(action="update", job_id="X", script="")` to remove
- **Useless script:** Remove script reference and rewrite prompt to be self-contained
- **Delivery error:** Update delivery target or fix Telegram bot token
- **Paused job:** `cronjob(action="resume", job_id="X")`
- **Stale schedule:** `cronjob(action="update", job_id="X", schedule="...")` to fix cron expression

### 7 — Final Verification

```bash
hermes cron list
```

Confirm:
- No `script` fields pointing to missing files
- No `last_delivery_error` values
- No `last_status: "error"` values
- All delivery targets are valid

## Pitfalls

| Issue | Symptom | Fix |
|-------|---------|-----|
| Script finds 0 results | Job runs, outputs "ALL_CAUGHT_UP" or empty | Remove script reference, rewrite prompt |
| Script path relative to wrong dir | Script reference exists but can't resolve | Check `$HERMES_HOME/scripts/` for actual location |
| Jobs don't run after gateway restart | `last_run_at` is days/weeks old | Normal if schedule hasn't been reached; force-run with `cronjob(action="run", job_id="X")` to verify |
| Delivery to wrong chat | Job runs but message goes to wrong place | Check chat IDs with `send_message(action="list")` |
| Monthly jobs appear "never run" | `last_run_at: null` for monthly schedule | Expected if job is between scheduled days |

## Maintenance Schedule

- **Weekly:** Run steps 1-4, quick scan
- **After gateway restart:** Run step 4 to check for missed runs
- **After adding/removing scripts:** Run step 2
- **Monthly:** Full audit including step 5

## Related Skills

- `devops/gentech-agent-reactivation` — Bulk cron resumption after downtime
- `autonomous-ai-agents/hermes-agent` — Cron CLI reference and scheduling
- `devops/telegram-send-from-cron` — Sending messages from cron contexts
