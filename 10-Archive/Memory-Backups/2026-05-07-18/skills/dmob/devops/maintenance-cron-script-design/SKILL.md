---
name: maintenance-cron-script-design
description: "Design cron/maintenance scripts that handle expected failures silently (exit 0) while surfacing actionable flags in structured output"
version: 1.0.0
author: Gentech Labs
license: MIT
metadata:
  hermes:
    tags: [cron, maintenance, devops, monitoring, silent-failure]
    homepage: https://github.com/NousResearch/hermes-agent
related_skills: ["hermes-maintenance-scripts", "hermes-auth-incident-response"]
---

# Maintenance Cron Script Design Pattern

When writing cron scripts for proactive maintenance (token refresh, health checks, cleanup jobs), distinguish between **expected failure states** (normal operational events that require manual action but aren't "incidents") and **unexpected errors** (actual script breakage). Return exit code `0` for the former to avoid automated incident noise; surface the condition in the script's structured output for visibility.

## Core Principle

```
Expected maintenance state (e.g., token revoked, service temporarily down, quota exceeded)
  → exit 0 + structured flag in stdout (e.g., "needs_reauth": true)
  → Cron job marked "ok" (no automated alerts)
  → Human checks logs/output to see the flag and takes manual action

Unexpected error (bug, crash, misconfiguration, unhandled exception)
  → exit 1
  → Cron job marked "error" → triggers automated incident response
```

## Checklist for Script Authors

### 1. Identify failure modes in your script
Before writing, list every reason your script might "fail":
- Token expired / refresh token revoked (OAuth)
- Service returns 429/503 (rate limit / maintenance)
- External API quota exceeded
- Resource not found (already cleaned up)
- Dependency unavailable (transient network blip)
- Configuration missing/invalid
- Unexpected data format / schema change

### 2. Categorize each as "expected" or "unexpected"
| Expected (silent exit 0) | Unexpected (noisy exit 1) |
|------------------------|--------------------------|
| OAuth token needs manual re-auth | Script crashes with traceback |
| API rate-limited (429) with retry exhausted | Invalid API key / auth misconfig |
| Service temporarily down (503) with max retries exceeded | Script invoked with wrong arguments |
| Resource already in desired state (no-op) | File not found that SHOULD exist |
| Quota exceeded (billing issue) | Database connection failure (should be stable) |
| Recurring task that legitimately has nothing to do | Unhandled exception |

**Rule of thumb:** If a human needs to act but it's not a *system breakage*, it's expected.

### 3. Structure your output
Even on silent exit, print structured output (JSON preferred) so humans can see what happened:
```python
status = {
    "success": False,           # Did the script achieve its goal?
    "needs_manual_action": True,# Flag for human intervention
    "action_type": "reauth",    # "reauth", "retry_later", "check_quota", etc.
    "message": "OAuth token fully revoked; run `hermes model` to re-authenticate.",
    "next_steps": ["hermes model", "verify: ~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py"],
    "script": "refresh_nous_oauth.py",
    "timestamp": "...",
}
print(json.dumps(status, indent=2))
sys.exit(0 if status["needs_manual_action"] else (1 if not status["success"] else 0))
```

### 4. Exit code logic template
```python
def main():
    status = {...}  # build status dict
    print(json.dumps(status, indent=2))

    if status.get("needs_manual_action"):
        return 0  # Expected maintenance condition — stay silent
    return 0 if status["success"] else 1  # Only real errors are noisy
```

**Do NOT** do this:
```python
# WRONG — makes cron job fail for expected conditions
if not success:
    return 1  # This triggers incident alerts for routine maintenance
```

### 5. Document the contract
At the top of your script:
```python
"""
Exit codes:
  0 - Script ran (even if manual action needed; see "needs_manual_action" flag)
  1 - Unexpected error (crash, misconfiguration, bug)

Any non-zero exit will trigger automated incident responses.
"""
```

## Integration with Watchdog / Monitoring

Watchdog agents should be configured to:
1. Parse cron job `last_error` and `last_status` fields
2. For jobs marked "ok", optionally inspect the saved output (JSON) for `needs_manual_action` flags
3. Only raise alerts for:
   - Jobs with `last_status="error"` (exit 1)
   - Jobs with `needs_manual_action=true` that persist beyond a grace period

## Examples

### OAuth Refresh (this session's fix)
```python
# Script: refresh_nous_oauth.py
except AuthError as e:
    status["success"] = False
    status["needs_reauth"] = e.relogin_required  # expected condition
    status["message"] = str(e)

# Exit: 0 if needs_reauth, else 1 on unexpected failure
if status.get("needs_reauth"):
    return 0  # Token expiry is expected — don't noise the monitors
return 0 if status["success"] else 1
```

### Health Check with Service Down
```python
status = {
    "success": False,
    "needs_manual_action": True,
    "action_type": "service_down",
    "message": "API endpoint returned 503; service maintenance in progress.",
    "retry_after": "2026-05-03T20:00:00Z",
}
sys.exit(0)  # Don't page anyone for scheduled maintenance
```

### Cleanup Job — Nothing to Do
```python
status = {
    "success": True,
    "needs_manual_action": False,
    "message": "No stale files found; disk usage nominal.",
    "files_cleaned": 0,
}
sys.exit(0)  # Quiet success
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Returning exit 1 for token expiry because "it failed" | Exit 0 + `needs_manual_action=true` in JSON |
| Forgetting to update exit logic after adding a new failure mode | Revisit the categorization table whenever you add a new error path |
| Watchdog alerting on every `needs_manual_action` | Build in a grace period; not every re-auth needs paging |
| Script exit 0 but still sends a Telegram message via `deliver` | Use `deliver: local` for maintenance scripts; keep post-success notifications separate |

## When to Change Your Mind

If an "expected" condition starts happening frequently (e.g., OAuth tokens expiring weekly), it's a signal the refresh logic is broken, not that manual re-auth is routine. Temporarily make it noisy (exit 1) to investigate, then revert to silent once diagnosed and either fixed or confirmed as a true manual-maintenance edge case.
