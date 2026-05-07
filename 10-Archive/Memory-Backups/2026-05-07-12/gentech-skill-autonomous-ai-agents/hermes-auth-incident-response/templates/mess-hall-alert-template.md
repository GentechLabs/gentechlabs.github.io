# 🚨 Infrastructure Alert — <PROVIDER> OAuth <STATUS>

**Time:** <YYYY-MM-DD HH:MM UTC>  
**Severity:** 🔴 CRITICAL / 🟡 DEGRADED  
**Owner:** @<ROLE> (Infrastructure Lead)  
**Status:** 🔄 AWAITING MANUAL FIX / ✅ RESOLVED

---

## Executive Summary

<One-sentence summary of what broke and impact.>

---

## What Happened

- **Token expiry:** `<ISO timestamp>` (<Provider> access token)
- **Refresh script:** ✅ Deployed at `<script-path>` / ❌ Missing
- **Refresh job:** ✅ Scheduled `<schedule>` / ❌ Not scheduled
- **Refresh attempt:** Failed with `needs_reauth: true` — refresh token invalid
- **Impact:** Scripts calling <Provider> endpoints exit code 1

Error output (from failing script):
```
"message": "..."
```

---

## Immediate Action Required

**<Role> needs to run:**
```bash
hermes model
```
(Or appropriate re-auth command for provider.)

**After re-authentication, verify:**
```bash
<script-path-to-refresh>
```
Expected output: `"success": true` with fresh token details.

---

## Documentation

- Incident log: `00-HQ/Operations/Infrastructure-Issues.md`
- Today's context: `11-Mess Hall/YYYY/W##/YYYY-MM-DD/today-context.md`
- Refresh script: `<vault-path-to-script>`
- Cron job: `"<Job Name>"` in `<profile> cron/jobs.json`

---

## Monitoring

The `<Watchdog Name>` cron (runs every N min) should catch this class of error. Current status: <status>.

---

## Forward Look

<Optional: one sentence about resilience improvement or pattern recognition.>

— <Your Name>, <Timestamp>
