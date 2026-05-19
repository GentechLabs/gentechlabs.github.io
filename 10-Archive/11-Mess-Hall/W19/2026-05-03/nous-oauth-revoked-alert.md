# 🔴 CRITICAL: Nous OAuth Session Revoked — Data Collection Offline

**Detected:** 2026-05-03 18:30 UTC  
**Impact:** All scripts relying on Nous OAuth access token are failing. Refresh mechanism cannot recover — manual intervention required.

---

## Executive Summary

The Nous OAuth refresh token has been revoked by the provider. The proactive refresh script (`refresh_nous_oauth.py`) returned `needs_reauth: true`, indicating session recovery is impossible without user re-authentication.

**What's broken:**
- Data collection cron jobs (multiple)
- Any agent operation requiring Nous API access
- Gateway-sourced data pipelines

**What's NOT broken:**
- Local agent computation
- Other provider integrations (Anthropic, OpenAI, etc.)
- Vault sync and Obsidian operations

---

## Affected Components Table

| Component | Path | Status |
|------------|------|--------|
| Auth state | `~/.hermes/profiles/gentech/auth.json` | EXPIRED (was: `2026-05-03T18:28:26Z`) |
| Refresh script | `~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py` | FAILING (needs_reauth) |
| Cron registry | `~/.hermes/profiles/gentech/cron/jobs.json` | SUSPENDED |
| Vault operations | `/root/vaults/gentech/` | ✅ OPERATIONAL |
| Local computation | Hermes gateway | ✅ OPERATIONAL |

---

## Immediate Action Block

**Owner:** @DMOB (Hermes infrastructure lead)  
**Priority:** P0 — data pipeline offline  
**Deadline:** Within 1 hour (next business cycle)

**Command to run:**
```bash
hermes model
```
This will trigger interactive re-authentication with the Nous provider.

**Expected outcome:**
- New access token issued (~30-day TTL)
- Refresh token restored
- `refresh_nous_oauth.py` returns `success: true` on next run

**Verification steps after re-auth:**
```bash
# 1. Test refresh script manually
~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py

# 2. Check token TTL
python3 -c "import json; d=json.load(open('/root/.hermes/profiles/gentech/auth.json')); print(d['providers']['nous']['expires_at'])"

# 3. Trigger affected cron job
hermes cron run <job-id>  # or run script directly

# 4. Monitor for 2–3 refresh cycles
tail -f ~/.hermes/profiles/gentech/logs/cron.log | grep refresh_nous_oauth
```

---

## Incident Log Reference

Full timeline and resolution tracking maintained at:
`00-HQ/Operations/Infrastructure-Issues.md`

---

## Monitoring Status

- ❌ Refresh script health check: FAILING
- ⚠️ Gateway alerting: only monitors agent sessions (does NOT catch cron auth failures)
- ✅ Data-collection job failures: detected (this alert)

**Recommendation:** Extend Watchdog to include `auth.json` expiry checks and `cron/last_error` monitoring.

---

**Contact:** Escalate to @DMOB in **GenTech HQ** Telegram group if no response within 30 minutes.
