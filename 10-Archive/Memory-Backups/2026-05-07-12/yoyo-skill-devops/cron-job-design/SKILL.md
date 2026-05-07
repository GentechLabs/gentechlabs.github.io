---
name: cron-job-design
description: Design patterns for robust cron jobs — exit code semantics, silent operational states, JSON output vs alerting separation, and maintenance-mode scripting
triggers:
  - phrase: "design cron job|silent cron|cron exit code|make cron silent|cron noise"
  - context: "building automation scripts|deploying scheduled jobs|script error handling"
  - tools: ["crontab", "cron", "scheduled tasks", "systemd timers"]
---

# Cron Job Design — Exit Codes, Silent States, and Alerting Hygiene

## Principle

**Cron alerting systems treat non-zero exit codes as failures.** Design your scripts accordingly:

| Condition | Exit Code | Telegram Alert? | When to use |
|-----------|-----------|-----------------|-------------|
| Success / task completed | `0` | ❌ No | Normal operation |
| Expected operational state requiring manual intervention (e.g., token expiry, quota exceeded, maintenance mode) | `0` | ❌ No *(silent)* | Known conditions that aren't script failures |
| Unexpected error (network, crash, invalid input) | `1` (or `2` for critical) | ✅ Yes | Real infrastructure problems |

## Core Pattern — Two-Layer Reporting

```python
import json
import sys

def main():
    status = {
        "success": False,
        "needs_manual_action": False,  # expected operational state
        "critical": False,             # unexpected error
        "message": "",
        "details": {}
    }

    try:
        # ... do work ...
        status["success"] = True
        status["message"] = "Task completed"
    except ExpectedCondition as e:
        # Known/expected situation — not a bug, just needs human action
        status["success"] = False
        status["needs_manual_action"] = True
        status["message"] = str(e)
    except Exception as e:
        # Unexpected — this is a failure
        status["success"] = False
        status["critical"] = True
        status["message"] = f"Unexpected error: {e}"
        import traceback
        status["traceback"] = traceback.format_exc()[:500]

    # JSON for logging/monitoring (always printed)
    print(json.dumps(status, indent=2))

    # Exit code for cron alerting
    if status.get("critical"):
        sys.exit(1)
    if not status.get("success") and not status.get("needs_manual_action"):
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
```

## When to Use Silent Mode (`exit 0`)

- Token refresh failures requiring `hermes model` re-auth
- API rate limits reached (quota reset scheduled)
- Scheduled maintenance windows
- Dependency unavailable but known (e.g., external service down for planned upgrade)
- Configuration missing that requires admin attention (not a script bug)

## When to Alert (`exit 1`)

- Network failures (timeouts, connection errors)
- Invalid/malformed input data
- Missing files or permissions errors
- Unexpected API response formats
- Unhandled exceptions
- Script crashes

## Monitoring Strategy

Since silent-mode conditions return exit code `0`, they won't trigger cron failure alerts. Monitor via:

1. **Log scraping** — Watch for `"needs_manual_action": true` in script output logs
2. **Watchdog agent** — Run a separate health-check script that parses JSON output from silent jobs and escalates if `needs_manual_action` persists beyond threshold
3. **State files** — Have the script write a `.state` file; monitor its age/freshness separately

## Pitfalls

- **Don't silo all errors as "expected."** Reserve `needs_manual_action` for truly anticipated conditions with clear recovery steps.
- **Don't exit 0 on partial failures.** If the script's core function failed unexpectedly, that's an alert.
- **Document the exit code contract.** Every cron job should have a companion note in the vault explaining its exit code semantics.
- **Keep JSON output consistent** even when silent — monitoring tools may parse it.

## Integration with Hermes

- Cron delivery `local` + exit code `0` on `needs_reauth` → no Telegram noise
- JSON output still captured in Hermes logs (`~/.hermes/logs/cron.log`) for post-mortem
- Pair with `Gentech Watchdog` for proactive health checking across all profiles

## References

- **Real-world implementation:** `/root/vaults/gentech/00-HQ/03-Projects/Proactive-Nous-OAuth-Refresh.md`
- **Applied pattern:** `/root/vaults/gentech/00-System/agent-profiles/*/scripts/refresh_nous_oauth.py`
- **Exit code standards:** `0` = success/OK, `1` = general error, `2` = misuse of shell command (reserved for critical)

### Skill Support Files

- `templates/silent-automation-template.py` — boilerplate for new silent-mode cron scripts
- `references/oauth-refresh-silent-mode.md` — detailed implementation notes and state matrix
