# 2026-05-03 — Nous OAuth Refresh Silent-Failure Fix

## Context
**Script:** `refresh_nous_oauth.py`
**Job ID:** `286d9b3925b4` ("Nous OAuth Proactive Refresh")
**Schedule:** `*/10 * * * *` (every 10 minutes)
**Problem:** When the Nous OAuth token expired and the refresh token was revoked, the script returned exit code 1 (failure). This caused the cron job to be marked "error" and triggered automated P0 incident alerts via Gentech Watchdog and the incident response skill.

## The Change

### Before
```python
print(json.dumps(status, indent=2))
return 0 if status["success"] else 1
```
Exit code behavior:
- Token expired → `success=false` → exit 1 → cron job "error" → incident alert 🚨

### After
```python
print(json.dumps(status, indent=2))
if status.get("needs_reauth"):
    return 0  # expected maintenance state, stay silent
return 0 if status["success"] else 1
```
Exit code behavior:
- Token expired → `needs_reauth=true` → exit 0 → cron job "ok" → no automated alert ✅
- Human still sees `needs_reauth: true` in saved output, knows to run `hermes model`

## Files Modified
- `/root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py` (active copy)
- `/root/.hermes/profiles/dmob/scripts/refresh_nous_oauth.py`
- `/root/.hermes/profiles/desmond/scripts/refresh_nous_oauth.py`
- `/root/.hermes/profiles/yoyo/scripts/refresh_nous_oauth.py`
- `/root/.hermes/scripts/refresh_nous_oauth.py` (global fallback)
- `/root/vaults/gentech/00-System/agent-profiles/gentech/scripts/refresh_nous_oauth.py` (canonical)
- `/root/.hermes/profiles/gentech/skills/autonomous-ai-agents/hermes-auth-incident-response/scripts/refresh_nous_oauth.py`

## Verification

**Manual test:** The script can be run directly; check exit code and JSON:
```bash
~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
echo $?  # should be 0 even if "needs_reauth": true
```

**Cron log check:**
```bash
cat ~/.hermes/profiles/gentech/cron/jobs.json | jq '.[] | select(.id=="286d9b3925b4")'
# last_status should be "ok" after the fix, not "error"
```

## The Skill This Fed
This incident revealed the need for a general design pattern: **maintenance cron scripts should exit 0 for expected manual-action states**. That pattern is now captured in the `maintenance-cron-script-design` skill so future scripts are built correctly from the start.

## Key Takeaway
- Exit code 1 = something is broken (page someone)
- Exit code 0 = script ran to completion, regardless of whether the outcome was "all good" or "human needs to do X"
- The JSON output tells you which case you're in; the exit code keeps the automation quiet.
