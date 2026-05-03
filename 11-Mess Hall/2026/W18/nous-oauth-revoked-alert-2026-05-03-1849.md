# Gentech Daily Sync — 2026-05-03

## Flags Raised

🔴 **CRITICAL: Nous OAuth session revoked** — All Hermes-Nous integrations offline, data collection failing.

**Status:** ACTIVE (pending manual re-authentication)  
**Detected:** 2026-05-03 18:49 UTC  
**Incident:** [Full log → 00-HQ/Operations/Infrastructure-Issues.md](00-HQ/Operations/Infrastructure-Issues.md)

### Immediate Action Required

**Owner:** @DMOB (Hermes infra lead)  
**Action:** Complete Nous Portal OAuth re-authentication.

1. Visit verification URL (within 10 minutes):  
   👉 https://portal.nousresearch.com/manage-subscription?user_code=FEE7-FXQ2

2. After completing browser auth, run the completion script:  
   ```bash
   /root/.hermes/profiles/gentech/scripts/complete_nous_device_flow.sh
   ```

3. Verify tokens renewed:  
   ```bash
   ~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
   ```

   Expected: `"success": true` with `"needs_reauth": false`

### Technical Notes

- Refresh token fully revoked; automated refresh cannot recover
- Device code flow initiated with `no_browser=True` at 18:49 UTC
- Code expires at 18:59 UTC
- Cron delivery set to `local` mode to suppress group noise
- Affected downstream: Kite AI hackathon checks, LayerZero DVN monitor, social monitors

### Incident Timeline

- 18:49 UTC — Token expired, refresh script returned `needs_reauth: true`
- 18:49 UTC — Device code initiation attempted; verification data generated
- Awaiting human completion via browser → DMOB to run completion script

---

*This alert generated automatically by Gentech cron health-check at 18:49:14 UTC.  Incident ID: 2026-05-03-1849*

