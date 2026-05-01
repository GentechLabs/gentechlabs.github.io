---
name: hermes-cron-audit
description: "Audit, diagnose, and fix broken Hermes cron jobs across all agent profiles. Covers stale jobs, auth failures, duplicate removal, and cross-profile cleanup."
version: 1.0.0
author: DMOB
tags: [hermes, cron, audit, devops, multi-agent, maintenance]
related_skills: [hermes-cron-consolidation, hermes-brain-backup]
---

# Hermes Cron Job Health Audit

Full audit pass across all Hermes agent profiles to find and fix broken cron jobs. Different from `hermes-cron-consolidation` (which merges specific jobs) — this is the "everything is broken, find and fix it all" workflow.

## When to Use

- Jordan says "fix all broken cron jobs" or "audit cron jobs"
- After a gateway restart that may have missed scheduled windows
- Periodic maintenance (monthly or after major changes)
- When jobs stop firing without obvious errors

## Quick Health Check (One-Liner)

For a fast status overview across all profiles without deep inspection:

```bash
for profile in dmob yoyo desmond gentech; do
  echo "=== $profile ==="
  cat /root/.hermes/profiles/$profile/cron/jobs.json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    status = j.get('last_status', 'never') or 'never'
    enabled = '✓' if j.get('enabled', True) else '✗'
    schedule = j.get('schedule', {})
    sched = schedule.get('expr', schedule.get('kind', '?')) if isinstance(schedule, dict) else str(schedule)
    name = j.get('name', 'unnamed')[:45]
    script = j.get('script')
    script_note = ''
    if script:
        import os
        exists = os.path.exists(f'/root/.hermes/scripts/{script}')
        script_note = f' [script: {\"✓\" if exists else \"✗ MISSING\"}]'
    print(f'  {enabled} {status:6} {sched:25} {name}{script_note}')
" 2>/dev/null
done
```

This shows: enabled/disabled, last status, schedule, name, and whether referenced scripts exist.

## Steps

### 1. List All Profiles and Their Jobs

Cron jobs are **profile-scoped** — each agent (DMOB, YoYo, Desmond, Gentech) has its own scheduler.

```bash
for profile in dmob yoyo desmond gentech; do
  echo "=== $profile ==="
  hermes --profile $profile cron list 2>&1
done
```

Capture: job IDs, names, schedules, `last_run_at`, `last_status`, `last_delivery_error`.

### 2. Identify Broken Jobs

Common failure patterns:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `last_run_at` stale (days/weeks old) | Gateway restart missed windows | `hermes --profile X cron run <job_id>` |
| `last_run_at: null` (never ran) | Job created but scheduler didn't pick it up | Trigger manually, check schedule syntax |
| `error` in `last_status` | Script bug, API failure, parse error | Check error message, fix script or prompt |
| `last_delivery_error` | Telegram group ID wrong, bot kicked | Verify delivery target |
| Duplicate jobs across profiles | Consolidation didn't clean up all copies | Remove duplicates, keep canonical |
| `ok` status but wrong output | Prompt drift: prompt was updated after last run, so run output used old version. Or agent ignored prompt and hallucinated data. | Compare stored run output prompt vs current `jobs.json` prompt. If different, next scheduled run will use correct version. If same, agent is not following instructions — harden prompt. |
| **`Script not found` error** | **Script was renamed/moved but cron config still references old name.** Common after vault reorganization or manual renames. | **Find the actual script with `search_files(path="/root", pattern="<script-name>", target="files")`. Copy it to the expected path: `cp <actual-path> <expected-path>`. Test with `python3 <expected-path>`.** |

### 3. Diagnose "Wrong Output" Issues

When a job runs (`last_status: ok`) but the output is wrong:

**Check the stored run output** — each run saves a markdown file with the prompt that actually executed:

```bash
ls -lt /root/.hermes/profiles/<profile>/cron/output/<job_id>/
cat /root/.hermes/profiles/<profile>/cron/output/<job_id>/<latest>.md
```

The output file contains both the **Prompt** section (what the agent received) and the **Response** section (what it produced). Compare the Prompt section against the current `jobs.json` prompt:

```bash
python3 -c "
import json
with open('/root/.hermes/profiles/<profile>/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    if j.get('id') == '<job_id>':
        print(j['prompt'])
        break
"
```

**Common causes:**
- **Prompt drift**: Prompt was updated after the last run → next run will be correct
- **Agent non-compliance**: Agent ignored prompt instructions (e.g., used wrong API, hallucinated data) → harden prompt with explicit constraints
- **Stale script**: Script referenced by prompt no longer exists or has wrong path → update script or prompt

### 3.5 Diagnose "Script Not Found" Issues

When a cron job error says `Script not found: /path/to/script.py`:

1. **Find the actual script** — it probably got renamed or moved:
   ```bash
   # Search all common script locations
   search_files(path="/root", pattern="<script-filename>", target="files")
   # Also check vault
   search_files(path="/root/vaults/gentech", pattern="<script-filename>", target="files")
   ```

2. **Copy to the expected path** — the cron config expects a specific path, so put the script there:
   ```bash
   cp /root/vaults/gentech/03-Strategies/scripts/<actual-script>.py /root/.hermes/profiles/<profile>/scripts/<expected-name>.py
   ```

3. **Test the script** — verify it runs from the new location:
   ```bash
   cd /root/.hermes/profiles/<profile>/scripts && python3 <script-name>.py
   ```

4. **If script reads config from a different path** — check the script's `CONFIG_FILE` variable. It may read from `~/.hermes/scripts/` which is different from the profile scripts directory. Verify both copies exist:
   ```bash
   ls -la /root/.hermes/scripts/<config-file>.json
   ls -la /root/.hermes/profiles/<profile>/scripts/<config-file>.json
   ```

**Pitfall:** Scripts in the vault (`03-Strategies/scripts/`) are the source of truth. Runtime copies in `~/.hermes/profiles/<profile>/scripts/` are deployments. Always copy from vault → runtime, never the reverse.

### 4. Test Stale Jobs Manually

```bash
hermes --profile <profile> cron run <job_id>
```

Wait for scheduler tick (up to 5 min for interval jobs, up to 60s for cron jobs), then verify:

```bash
hermes --profile <profile> cron list 2>&1 | grep -A 8 "<job_id>"
```

If `last_run_at` updates and `last_status` is `ok` → job is fine, just missed windows.

### 4. Fix Auth Failures

**Brain backup push failures** (`fatal: could not read Username`):

```bash
cd /root/hermes-brain-backup
git config credential.helper '!gh auth git-credential'
git push origin main
```

Requires `gh auth login` to be configured first.

**Telegram delivery failures:**
- Verify group ID in `deliver` field
- Check bot is still in the group
- Verify bot token hasn't rotated

### 5. Remove Duplicate Jobs

Jobs are often duplicated across profiles during consolidation. Keep the **canonical** version (usually YoYo for Strategies, DMOB for Labs).

```bash
hermes --profile <profile> cron remove <duplicate_job_id>
```

**Before removing, verify:**
- The canonical job exists and is running
- The duplicate has the same (or similar) schedule
- Vault docs reference the canonical job ID

### 6. Update Vault Docs

After cleanup, update all docs that reference job IDs:

```bash
search_files(path="/root/vaults/gentech", pattern="<old-job-id>", target="content")
```

Key files to check:
- `03-Strategies/cron-jobs.md` (canonical manifest)
- `02-Labs/cron-jobs-registry.md` ( Labs-specific)
- Any `current-jobs.json` or `cron-jobs.json`

### 7. Verify Final State

```bash
for profile in dmob yoyo desmond gentech; do
  echo "=== $profile ==="
  hermes --profile $profile cron list 2>&1
done
```

Confirm: no stale `last_run_at`, no errors, no obvious duplicates.

## Pitfalls

- **Gateway restart = missed windows.** Jobs with specific-hour schedules (e.g., `0 6,8,10 * * *`) will miss their slots if the gateway is down during those hours. Interval jobs (every 5m, 10m) recover automatically on next tick.
- **Manual triggers don't run immediately.** They queue for the next scheduler tick. Wait 30-60s before checking `last_run_at`.
- **Profile-scoped jobs.** The `cronjob()` tool only sees the current profile's jobs. Use `hermes --profile X cron list` for cross-profile views.
- **Doc drift.** Vault docs often list job IDs that no longer match the scheduler. Always verify against `hermes --profile X cron list`.
- **Duplicate job IDs in docs.** The `cron-jobs.md` manifest may reference IDs from removed/recreated jobs. Cross-check each ID.

## Frequency

- After any `hermes gateway restart` or server reboot
- Monthly as preventive maintenance
- When Jordan reports jobs not firing
