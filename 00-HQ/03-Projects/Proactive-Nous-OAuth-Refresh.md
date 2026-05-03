---
title: Proactive Nous OAuth Refresh
description: Automated token refresh for Nous Portal OAuth credentials to prevent expiry across all Hermes profiles
created: 2026-05-03
status: active
owner: gentech
tags: [oauth, maintenance, nous, tokens, cron]
---

# Proactive Nous OAuth Refresh

## Purpose

Automatically refresh Nous Portal OAuth tokens before they expire to maintain uninterrupted service across all Hermes agent profiles (Gentech, YoYo, DMOB, Desmond).

## Problem

Nous Portal OAuth tokens have a limited lifetime (typically 24 hours for access tokens, longer for refresh tokens). When tokens expire:

- All LLM API calls fail with 401 errors
- Cron jobs that require LLM inference stop working
- Voice and other provider tools fail
- Gateway message processing breaks

The `Hermes Agent Daily Sync Check` and other critical jobs depend on valid Nous authentication.

## Solution

A cron job runs every 10 minutes (`*/10 * * * *`) that executes `refresh_nous_oauth.py`. The script:

1. Checks current token expiry time
2. If within the **skew window** (2 minutes before expiry) or already expired, automatically refreshes using the stored refresh token
3. Writes updated tokens back to the profile's `auth.json`
4. Returns JSON status report for monitoring

## Configuration

### Cron Job Details

| Field | Value |
|-------|-------|
| **Name** | Nous OAuth Proactive Refresh |
| **Schedule** | `*/10 * * * *` (every 10 minutes) |
| **Profile** | gentech |
| **Script** | `refresh_nous_oauth.py` |
| **Deliver** | local (no external delivery) |

### Script Location

```
/root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
```

**Executable:** `-rwxr-xr-x` (755)

### Auth Storage

Tokens are stored in the profile-specific auth file:

```
/root/.hermes/profiles/gentech/auth.json
```

Format (Hermes v2+):
```json
{
  "version": 2,
  "providers": {
    "nous": {
      "access_token": "...",
      "refresh_token": "...",
      "expires_at": "2026-05-03T17:45:12.198597+00:00",
      "agent_key_expires_at": "2026-05-04T13:16:13.569Z",
      ...
    }
  },
  ...
}
```

**Important:** Each profile has its own `auth.json`. Do NOT use `/root/.hermes/auth.json` (that's for the default profile only).

## Monitoring

### Pre-run Check (Cron Wrapper)

Before executing the refresh script, a pre-run check validates token freshness:

```json
{
  "success": true,
  "message": "Tokens are fresh",
  "tokens": {
    "access_token_preview": "eyJhbG...NiIs...",
    "refresh_token_present": true,
    "expires_at": "2026-05-03T17:45:12.198597+00:00",
    "agent_key_expires_at": "2026-05-04T13:16:13.569Z"
  },
  "needs_reauth": false,
  "critical": false,
  "hermes_home": "/root/.hermes/profiles/gentech",
  "remaining_seconds": 899
}
```

### Cron Job Status

```bash
# List all cron jobs and filter for OAuth
hermes cron list | grep -i 'oauth'

# Check recent runs
hermes cron list --all | grep 'Nous OAuth'

# View job details (by ID)
hermes cron show 286d9b3925b4
```

### Manual Verification

```bash
# Run the refresh script manually (with proper HERMES_HOME)
HERMES_HOME=/root/.hermes/profiles/gentech \
  python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
```

Expected output on success:
```json
{
  "success": true,
  "message": "Tokens are fresh",
  "remaining_seconds": 862,
  "needs_reauth": false
}
```

## Troubleshooting

### Tokens Need Re-authentication

If the script returns `"needs_reauth": true` or error `"Refresh session has been revoked"`:

1. Re-authenticate the profile:
   ```bash
   hermes model  # Select Nous Portal provider
   # or explicitly
   hermes login --provider nous
   ```

2. Complete the OAuth device code flow in your browser

3. Verify credentials are active:
   ```bash
   hermes auth list
   ```

4. Restart the gateway to clear stale state:
   ```bash
   hermes gateway restart --profile gentech
   ```

5. Confirm the cron job succeeds on next tick

### Cron Job Not Running

If the job shows no recent activity:

1. Verify the job is active:
   ```bash
   hermes cron list | grep '286d9b3925b4'
   ```

2. Check cron daemon is running:
   ```bash
   systemctl --user status hermes-cron
   ```

3. Force a manual run:
   ```bash
   hermes cron run 286d9b3925b4
   ```

### Script Not Found

The cron job resolves script paths relative to the profile's `scripts/` directory. If the script is missing:

```bash
# Re-deploy from vault (if available)
cp /root/vaults/gentech/00-HQ/03-Projects/refresh_nous_oauth.py \
   /root/.hermes/profiles/gentech/scripts/
chmod +x /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
```

## Alerting

The following jobs depend on valid Nous OAuth and will fail if tokens expire:

- **Mess Hall — Daily Rotation** (0 3 * * *)
- **Mess Hall — Post-Shift** (0 12 * * 0-3)
- **Kite AI Hackathon Submission Check** (0 10 * * *)
- **Brain Backup → GitHub** (0 */6 * * *)
- **Weekly Skills Update Check** (0 9 * * 0)

Monitor these jobs' `last_run_status`. If any show `error: 401`, trigger OAuth refresh verification immediately.

## Behavior Change — Silent Mode (2026-05-03)

The refresh script now operates in **silent mode** for expected operational states:

- **`needs_reauth: true`** → exit code `0` (no alert). This is an expected condition requiring manual `hermes model` re-authentication, not a script failure.
- **`success: true`** → exit code `0` (no alert). Tokens are fresh.
- **Unexpected errors** (network failures, `critical: true`, exceptions) → exit code `1` (alert).

This prevents Telegram noise when tokens naturally expire and need manual re-auth, while still surfacing real infrastructure problems.

### Verify Silent Behavior

```bash
# Simulate "needs_reauth" state — should exit 0, no alert
HERMES_HOME=/root/.hermes/profiles/gentech \
  python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
echo "Exit code: $?"   # Expect: 0 even if needs_reauth=true

# Check the JSON output
#   {"success": false, "needs_reauth": true, ...}  ← still reported
#   but cron will NOT flag it as a failure
```

### Post-Fix Checklist

1. ✅ Scripts updated across all profiles: `gentech`, `yoyo`, `desmond`, `dmob`
2. ✅ Exit code logic: `needs_reauth` → `0` (silent), unexpected errors → `1` (alert)
3. ✅ Documentation updated to reflect silent mode
4. ⬜ Wait for next token expiry to confirm silent operation (no false-positive alerts)

> **Last Updated:** 2026-05-03 — Wrapper script added for quiet-hours silence (11 PM–6:30 AM EST). Cron job now uses `refresh_nous_oauth_quiet_wrapper.py` which suppresses output during quiet hours.
