# 🚨 Infrastructure Alert — Nous OAuth Session Revoked

**Time:** 2026-05-04 00:30 UTC  
**Severity:** 🔴 CRITICAL  
**Owner:** @DMOB (Infrastructure Lead)  
**Status:** 🔄 AWAITING MANUAL `hermes model` RE-AUTH

---

## Executive Summary

Hermes OAuth session with Nous Portal has been revoked. The proactive refresh script (`refresh_nous_oauth.py`) returns `needs_reauth: true` and cannot recover programmatically. **All model-dependent cron jobs (8+) are currently failing** with 401/invalid API key errors. Fallback provider chain is empty (`fallback_providers: []`) — single point of failure.

---

## What Happened

| Check | Finding |
|-------|---------|
| **Access token state** | EXPIRED — expired 2026-05-03 22:11 UTC (~2h 20m ago) |
| **Refresh token state** | REVOKED — refresh endpoint returns `relogin_required: true` |
| **Refresh script** | ✅ Deployed at `~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py` |
| **Refresh job** | ✅ Scheduled `*/10 * * * *` — last run 2026-05-04 00:21 (returned `needs_reauth: true`, exit 0) |
| **Refresh attempt result** | `{"success": false, "needs_reauth": true, "message": "Refresh session has been revoked"}` |
| **Exit code behavior** | ⚠️ Returns `0` on both success and auth-failure — monitoring trap! |
| **Credential pool** | ⚠️ Shows `status=ok` (stale) while `providers.nous` tokens are actually invalid |
| **Fallback chain** | ❌ Empty (`fallback_providers: []`) — zero redundancy |
| **Pending device flow** | ✅ Cleaned stale `auth_pending_device_flow.json` (age ~342 min) |

**Root cause:** Refresh token explicitly revoked or long-term expiry beyond refresh window. Programmatic renewal impossible; requires interactive browser OAuth flow (`hermes model`).

---

## Impact: Affected Cron Jobs (8)

All `provider=nous` jobs failing. Next runs throughout today (03:00–12:00 UTC) will continue to fail until re-auth completes.

| # | Job Name | Last Run (UTC) | Next Run (UTC) | Error |
|---|----------|---------------|----------------|-------|
| 1 | YoYo — Crypto Watchlist + LP Monitor | 2026-05-03 20:15 | 2026-05-04 08:15 | "Hermes is not logged into Nous Portal" |
| 2 | Kite AI Hackathon Submission Check | 2026-05-03 11:52 | 2026-05-04 10:00 | HTTP 401 — invalid API key |
| 3 | Mess Hall — Daily Rotation | 2026-05-03 03:00 | 2026-05-04 03:00 | "not logged into Nous Portal" |
| 4 | Mess Hall — Break 2 | 2026-05-03 11:59 | 2026-05-07 10:00 | HTTP 401 — invalid API key |
| 5 | Mess Hall — Post-Shift | 2026-05-03 12:00 | 2026-05-04 12:00 | "Refresh session has been revoked" |
| 6 | Weekly Skills Update Check | 2026-05-03 11:54 | 2026-05-10 09:00 | HTTP 401 — invalid API key |
| 7 | LayerZero DVN Monitor | 2026-05-03 11:56 | 2026-05-04 09:00 | HTTP 401 — invalid API key |
| 8 | hackathon-bounty-monitor | 2026-05-03 11:56 | 2026-05-04 09:00 | HTTP 401 — invalid API key |

**Secondary impact:** Agent chat sessions may fail on Nous model calls; no fallback provider configured.

---

## Immediate Action Required

**Owner:** @DMOB  
**Priority:** P0 — entire inference pipeline offline

### Step 1: Interactive Re-Authentication (requires browser/TTY)

```bash
hermes model
```
Complete the Nous Portal OAuth consent screen in browser.

### Step 2: Verify Token Renewal

```bash
~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
# Expected: {"success": true, "needs_reauth": false, ...}
```

### Step 3: Confirm Token Details

```bash
python3 -c "import json; d=json.load(open('/root/.hermes/profiles/gentech/auth.json')); print('Expires:', d['providers']['nous']['expires_at'])"
# Should show timestamp ~30 days from now
```

### Step 4 (MANDATORY): Harden Fallback Chain

**Edit:** `~/.hermes/profiles/gentech/config.yaml`

```yaml
model:
  provider: auto   # Switch from 'nous' to enable fallback routing
fallback_providers:
  - ollama-cloud   # credential_pool shows status=ok, API key likely valid
  - opencode-go    # secondary fallback (currently quota-exhausted)
```

**Why mandatory:** Empty `fallback_providers` created single point of failure. This change ensures resilience against future provider outages.

---

## Monitoring Alert

⚠️ **GENTECH WATCHDOG COVERAGE GAP:** Current watchdog monitors agent session errors only — does **NOT** parse cron script output. The refresh cron job shows `last_status: ok` despite `needs_reauth: true` in JSON payload because both success and auth-failure exit with code `0`.

**Required fix:** Extend watchdog prompt to parse refresh script stdout (and/or check `auth.json` `providers.nous.expires_at` directly). Flag `needs_reauth: true` as P0.

---

## Technical Details

- **Auth file:** `/root/.hermes/profiles/gentech/auth.json`
- **Refresh script:** `/root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py`
- **Cron job ID:** `286d9b3925b4` ("Nous OAuth Proactive Refresh")
- **Config:** `/root/.hermes/profiles/gentech/config.yaml` (currently `fallback_providers: []`)
- **Device flow cleanup:** `auth_pending_device_flow.json` removed (age ~342 min) — prevents initiation conflicts

---

## Documentation

- Incident log: `00-HQ/Operations/Infrastructure-Issues.md` (active section)
- Post-mortem notes: `references/auth-incident-post-mortem-2026-05-04.md` (new)
- Alert file: `11-Mess Hall/2026/W18-2026/nous-oauth-revoked-alert-2026-05-04.md`
- Today's flags: `11-Mess Hall/2026/W18-2026/today.md`

---

## Forward Look

After re-auth completes, verify affected cron jobs resume `ok` status over next 2–3 cycles. The mandatory `fallback_providers` config change must be enforced; consider adding a Watchdog rule to detect empty fallback chains proactively. The exit code 0 monitoring gap should be addressed to catch future auth failures automatically.

— Gentech HQ, 2026-05-04 00:45 UTC
