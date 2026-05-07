# OAuth Refresh Silent Mode — Implementation Detail

**Date implemented:** 2026-05-03
**Profiles affected:** `gentech`, `yoyo`, `desmond`, `dmob`
**Script:** `refresh_nous_oauth.py`

## Problem

Original exit code logic:
```python
return 0 if status["success"] else 1
```

This treated `needs_reauth=True` (expected operational state) as a failure, triggering Telegram alerts every time the Nous OAuth token expired and required manual `hermes model` re-authentication.

## Solution

Exit code now distinguishes three states:

```python
if status.get("critical"):
    return 1                              # Unexpected — ALERT
if not status.get("success") and not status.get("needs_reauth"):
    return 1                              # Unexpected — ALERT
return 0                                 # Success OR needs_reauth — SILENT
```

### State Matrix

| `success` | `needs_reauth` | `critical` | Exit code | Meaning |
|-----------|----------------|------------|-----------|---------|
| ✅ true   | ❌ false       | ❌ false   | `0`       | Tokens fresh — silent |
| ❌ false  | ✅ true        | ❌ false   | `0`       | Refresh token revoked — silent (manual `hermes model` needed) |
| ❌ false  | ❌ false       | ✅ true    | `1`       | Critical/unexpected error — alert |
| ❌ false  | ❌ false       | ❌ false   | `1`       | Generic failure — alert |

## Verification

```bash
# Should exit 0 even when needs_reauth=true
HERMES_HOME=/root/.hermes/profiles/gentech \
  python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
echo $?   # → 0

# JSON output still reports the condition:
# {"success": false, "needs_reauth": true, "message": "..."}
```

## Monitoring

Silent-mode jobs (exit `0`) will **not** appear in cron failure summaries. To track when manual intervention is needed:

1. Parse cron logs for the job string "refresh_nous_oauth" and grep output for `"needs_reauth": true`
2. Add a separate Watchdog health check that runs the script and alerts if `needs_reauth=true` for > 1 hour
3. Use log-based monitoring (e.g., `journalctl -u hermes-cron | grep needs_reauth`)

## Related Decisions

- **Why not use exit code `2` for needs_reauth?** Cron alerting systems typically only care about `0` vs non-zero. Exit code `2` would still trigger alerts. The point is to *suppress* noise, not create a new alert tier.
- **Why keep JSON output?** JSON provides structured diagnostics for logs/monitoring without relying on exit codes.
- **Why not email instead of Telegram?** Email is still noise. The preferred workflow: Watchdog agent periodically scans all profiles' auth state and summarizes in the daily briefing if any need attention.

## References

- Script: `/root/vaults/gentech/00-System/agent-profiles/gentech/scripts/refresh_nous_oauth.py`
- Incident: `00-HQ/Operations/Infrastructure-Issues.md`
- Project: `00-HQ/03-Projects/Proactive-Nous-OAuth-Refresh.md`
- Skill: `cron-job-design` (this pattern)
