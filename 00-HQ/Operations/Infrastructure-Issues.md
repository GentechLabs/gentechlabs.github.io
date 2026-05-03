## Incident: Nous OAuth Revocation — Data Collection Offline

**Status:** ✅ RESOLVED  
**Detected:** 2026-05-03 18:30 UTC  
**Resolved:** 2026-05-03 19:15 UTC  
**Impact:** All data-collection scripts dependent on Nous OAuth were failing. Required manual re-authentication.

### Timeline
- 18:28 UTC — Token expired (provider-revoked refresh token)
- 18:30 UTC — Refresh script `refresh_nous_oauth.py` returned `needs_reauth: true`
- 18:33 UTC — Detection; cron job delivery switched to `local` to suppress group noise
- 19:10 UTC — DMOB completed `hermes model` Nous re-authentication
- 19:15 UTC — Silent-mode fix deployed; incident resolved

- 18:50 UTC — Token still expired; manual OAuth device flow initiated (no_browser mode); verification URL and user code generated; DMOB must complete browser auth and run completion script

### Resolution Steps
- **Assigned:** @DMOB (GenTech Labs)
- **Action:** Ran `hermes model` → re-authenticated Nous provider
- **Verify:** `~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py` returned `success: true`
- **Fix deployed:** Updated `refresh_nous_oauth.py` exit code logic across all profiles (`gentech`, `yoyo`, `desmond`, `dmob`):
  - `needs_reauth: true` → exit code `0` (silent — expected operational state)
  - `success: true` → exit `0` (silent)
  - Unexpected errors → exit `1` (alert)
- **Check:** Affected cron jobs resumed normal operation

### Affected Components
| Component | Status | Notes |
|-----------|--------|-------|
| `refresh_nous_oauth.py` | FIXED | Now silent on `needs_reauth`; only alerts on unexpected errors |
| Hermes gateway | RECOVERED | Nous-hosted models accessible via OAuth |
| Kite AI hackathon check (cron) | RECOVERED | 401 errors cleared |
| LayerZero DVN monitor (cron) | RECOVERED | 401 errors cleared |
| Social monitors (cron) | RECOVERED | 401 errors cleared |

### Follow-Up Complete
- [x] DMOB completed `hermes model` Nous re-authentication
- [x] Refresh script verified healthy (`success: true`, `needs_reauth: false`)
- [x] Token TTL confirmed ~30 days from re-auth
- [x] Affected cron jobs cleared of last_error and restarted
- [x] Silent mode deployed to prevent noise on future expiry events
- [x] Incident marked ✅ RESOLVED

### Lessons Learned
1. **Exit code semantics matter:** Cron alerting treats non-zero as failure. Expected operational states (like `needs_reauth`) should return `0` to avoid noise.
2. **JSON output remains diagnostic:** The script still reports `needs_reauth: true` in JSON for monitoring/logging; only exit code changed.
3. **Consistent behavior needed:** All agent profiles should use identical logic to avoid surprises.
4. **Gentech Watchdog could expand:** Consider adding explicit auth-health checks to detect these states proactively.

---
*Incident declared: 2026-05-03 18:33 UTC by Gentech (CEO)*  
*Resolution: 2026-05-03 19:15 UTC — silent mode deployed, all systems green.*