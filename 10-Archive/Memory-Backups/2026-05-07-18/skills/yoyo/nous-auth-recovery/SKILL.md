---
name: nous-auth-recovery
category: devops
description: Diagnose and recover from Nous Portal authentication failures that cause cron jobs and agent sessions to fail.
---

# Nous Auth Recovery

Use when cron jobs start failing with "Refresh session has been revoked" or "AuthError" from the Nous provider, or when the user says their Nous sub was rejected/revoked.

## Diagnosis

1. Check `hermes status` - look for Nous Portal auth expiry
2. Check `hermes doctor` - look for auth provider warnings
3. Check gateway logs: `journalctl --user -u hermes-gateway --since "30 min ago" --no-pager -n 50`
   - Key error pattern: `AuthError: Refresh session has been revoked`
   - Key error pattern: `RuntimeError: Refresh session has been revoked Run hermes model to re-authenticate`

## Immediate Actions

1. **Broadcast to all Telegram groups** that agents are pausing for reconnection. Use these targets:
   - `telegram:Gentech HQ`
   - `telegram:Gentech Strategies`
   - `telegram:Gentech Labs`
   - `telegram:Gentech Entertainment`

2. **Pause all cron jobs** to stop error spam:
   - List jobs: `cronjob(action='list')`
   - Pause each: `cronjob(action='pause', job_id='<id>')` — use **direct parallel tool calls** (multiple `cronjob` actions in the same turn), NOT `delegate_task` (max 3 concurrent) nor `execute_code` with `terminal()` (Hermes tools aren't exposed as CLI commands in the shell context).

3. **Instruct user to re-authenticate**: They need to run `hermes model` interactively (browser-based OAuth required, cannot be done headlessly)

## After Re-authentication

1. **Broadcast restoration** to all 4 agent hubs (same targets as step 1) before resuming jobs — keeps teams in the loop.
2. Resume all paused cron jobs: use direct parallel `cronjob(action='resume', job_id='<id>')` calls.
3. Verify gateway logs show successful token refresh: `journalctl --user -u hermes-gateway --since "2 min ago" --no-pager -n 20 | grep -i "auth\|refresh"` — should be clean.
4. Spot-check a few recent cron job runs via `cronjob(action='list')` status.

## Bulk Operation Pattern

For pausing/resuming many jobs at once when the Hermes tools themselves are still functional:

```python
# Use execute_code with the tool-wrapper pattern:
from hermes_tools import cronjob
jobs = ["id1", "id2", ...]  # from cronjob(action='list')
for jid in jobs:
    cronjob(action='pause', job_id=jid)  # or 'resume'
# This works because hermes_tools exposes Hermes tools as Python functions
```

**Warning**: `terminal(command="hermes cronjob pause ...")` will fail — the Hermes CLI isn't in PATH inside the tool sandbox. Use the `cronjob` tool directly, either as parallel calls or within an `execute_code` Python script that imports `hermes_tools`.

## Notes

- The gateway service keeps running but sessions can't resolve credentials when auth is revoked
- Access tokens expire periodically (visible in `hermes status` as "Access exp"); refresh tokens can be revoked by Nous Portal ("Key exp") — auth fails when refresh itself is invalidated, not on access expiry
- LP Monitor (every 10 min) and Vault Manager (nightly) are typically the first to error when auth breaks
- Always pause **all** cron jobs (count varies; get exact list via `cronjob(action='list')`), since they all depend on the Nous model runtime; resuming only some leaves partial failure noise
- The `delegate_task` concurrency limit (default 3) makes it unsuitable for bulk cron operations; use parallel `cronjob` tool calls or an `execute_code` script that imports `hermes_tools.cronjob`
