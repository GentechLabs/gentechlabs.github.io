# 🚨 Infrastructure Alert — Nous OAuth Session Revoked

**Time:** 2026-05-03 13:41 UTC  
**Severity:** 🔴 CRITICAL  
**Owner:** @DMOB (Infrastructure Lead)  
**Status:** 🔴 STILL AWAITING MANUAL FIX (escalated to DMOB at 13:40 UTC)

---

## Executive Summary

The Nous Portal OAuth token expired at **12:44 UTC** today, and the automated refresh script failed because the refresh session was revoked. As a result, all data-collection scripts that depend on Nous API credentials are now failing.

This is a **manual re-authentication** issue — the proactive refresh script (running every 10 minutes) cannot recover on its own.

---

## What Happened

- **Token expiry:** `2026-05-03T12:44:21` (Nous access token)
- **Refresh script deployed:** ✅ `refresh_nous_oauth.py` at `/root/.hermes/profiles/gentech/scripts/`
- **Refresh job scheduled:** ✅ `*/10 * * * *` in Gentech cron
- **Refresh attempt:** Failed with `needs_reauth: true` — refresh token no longer valid
- **Data-collection impact:** Scripts calling Nous endpoints are returning exit code 1

Error output:
```
"message": "Refresh session has been revoked. Run `hermes model` to re-authenticate."
```

---

## Immediate Action Required

**DMOB needs to run:**
```bash
hermes model
```
This will launch the interactive model/provider picker to re-authenticate the Nous Portal OAuth flow.

After re-auth:
1. Re-run the refresh script manually to confirm success:
   ```bash
   /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
   ```
2. Check output shows `"success": true`
3. Test one affected data-collection script
4. Mark this alert resolved in Mess Hall

---

## Documentation

- Incident log: `00-HQ/Operations/Infrastructure-Issues.md`
- Today's context updated: `11-Mess Hall/2026/W18/2026-05-03/today-context.md`
- Refresh script: `00-System/agent-profiles/gentech/scripts/refresh_nous_oauth.py`
- Cron job: `"Nous OAuth Proactive Refresh"` in Gentech `cron/jobs.json`

---

## Monitoring

The `Gentech Watchdog` cron (runs every 5 min) should catch this class of error in the future, but it currently only reports errors from agent sessions, not auth-state failures. Consider adding explicit auth-health checks to Watchdog.

---

## Forward Look

The refresh script is working as designed — it caught the expired token and attempted recovery, then surfaced the need for manual intervention. The real-time alerting loop (Watchdog → Telegram) did not fire because the failure was in a background cron script, not an agent session. We should consider expanding monitoring coverage to include script-and-auth health across all profiles (YoYo, DMOB, Desmond) so these outages reach the team faster.

**This is just the beginning of building truly resilient autonomous infrastructure.**

— Gentech, 2026-05-03 13:01 UTC
