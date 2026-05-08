# Auth Incident Post-Mortem: 2026-05-04

**Incident:** Nous OAuth refresh token revoked — primary provider offline  
**Detected:** 2026-05-04 00:30 UTC (scheduled cron wake-up)  
**Resolved:** Pending DMOB manual `hermes model` re-auth

---

## New Observations (not in playbook v1.0.0)

### 1. Refresh Script Exit Code 0 Trap (CRITICAL MONITORING GAP)

**Finding:** `refresh_nous_oauth.py` returns exit code `0` for both success and `needs_reauth` states.

```json
# Success (tokens fresh)
{"success": true, "needs_reauth": false, ...}

# Auth failure (needs manual intervention)
{"success": false, "needs_reauth": true, "message": "Refresh session has been revoked"}
# Both cases → exit 0
```

**Impact:** Cron job `last_status` shows `ok` even when auth fails. Gentech Watchdog (monitoring agent sessions only) does NOT catch this. No automated alert triggered.

**Required fix:**
- Monitoring must parse JSON stdout from refresh script and flag `needs_reauth: true` as P0.
- Alternatively, modify refresh script to exit 1 on `needs_reauth: true` (breaking change; may affect existing cron monitoring assumptions).

**Action taken (2026-05-04):** Escalated via Mess Hall alert to @DMOB; documented in incident log.

---

### 2. Credential Pool Status Is Stale (Auth State Edge Case)

**Finding:** `auth.json` `credential_pool.nous[0].last_status == "ok"` while `providers.nous` entry had:
- `access_token` present but `expires_at` in past (expired ~2h 20m ago)
- `refresh_token` present but refresh endpoint returned `relogin_required`
- Actual auth state: **fully revoked**

**Conclusion:** `credential_pool` tracks *historical* auth success, not *current* token validity. Never use `credential_pool.*.last_status` to decide if tokens are good.

**Correct check:**
```python
prov = auth_data['providers'].get('nous', {})
if not prov.get('access_token'):
    # tokens missing → needs auth
if datetime.fromisoformat(prov['expires_at']) < now:
    # expired → try refresh; if refresh fails with relogin_required → needs auth
```

---

### 3. Affected Cron Jobs Inventory (8+ failures)

All provider=nous jobs failing with either:
- `RuntimeError: Hermes is not logged into Nous Portal. Run \`hermes model\` to re-authenticate.`
- `RuntimeError: Error code: 401 - {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds...'}`

| # | Job Name | Last Run (UTC) | Next Run (UTC) | Error Snippet |
|---|----------|---------------|----------------|---------------|
| 1 | YoYo — Crypto Watchlist + LP Monitor | 2026-05-03 20:15 | 2026-05-04 08:15 | "not logged into Nous Portal" |
| 2 | Kite AI Hackathon Submission Check | 2026-05-03 11:52 | 2026-05-04 10:00 | HTTP 401 invalid API key |
| 3 | Mess Hall — Daily Rotation | 2026-05-03 03:00 | 2026-05-04 03:00 | "not logged into Nous Portal" |
| 4 | Mess Hall — Break 2 | 2026-05-03 11:59 | 2026-05-07 10:00 | HTTP 401 invalid API key |
| 5 | Mess Hall — Post-Shift | 2026-05-03 12:00 | 2026-05-04 12:00 | "Refresh session has been revoked" |
| 6 | Weekly Skills Update Check | 2026-05-03 11:54 | 2026-05-10 09:00 | HTTP 401 invalid API key |
| 7 | LayerZero DVN Monitor | 2026-05-03 11:56 | 2026-05-04 09:00 | HTTP 401 invalid API key |
| 8 | hackathon-bounty-monitor | 2026-05-03 11:56 | 2026-05-04 09:00 | HTTP 401 invalid API key |

**Note:** Job 4 (Break 2) next run is 2026-05-07 due to Thursday-only schedule (`0 10 * * 4-6`).

---

### 4. HERMES_HOME Path Quirk (Canonical Resolution)

**Observed paths:**
```
$HERMES_HOME (env):          /root/.hermes/profiles/gentech/home/.hermes/profiles/gentech
realpath($HERMES_HOME):      /root/.hermes/profiles/gentech/home/.hermes/profiles/gentech
auth.json actual location:   /root/.hermes/profiles/gentech/auth.json  ← NOT under nested path
```

The `auth.json`, `scripts/`, `cron/` all live at the *parent* `/root/.hermes/profiles/gentech`, not in the nested `$HERMES_HOME`. Scripts use `os.environ.get("HERMES_HOME")` which resolves to the nested path incorrectly.

**Root cause:** Cron sets HERMES_HOME to profile directory, but some Hermes internals resolve it to an additional `/home/.hermes/profiles/gentech` component. The refresh script properly uses `HERMES_HOME` env var but still hits the right `auth.json` because the file lives at the parent.

**Risk:** Scripts that construct paths as `$HERMES_HOME/auth.json` will look in the wrong place.

**Mitigation:**
- Always use `realpath "$HERMES_HOME"` and verify file existence before operations.
- Consider hardcoding the canonical path `/root/.hermes/profiles/gentech` for Gentech-specific maintenance scripts.
- Document this quirk per profile: `references/hermes-home-path-quirk-2026-05-04.md` (this file).

**Action taken:** Refactored diagnostic code to use explicit canonical path `/root/.hermes/profiles/gentech` after discovering `realpath` returned nested path.

---

### 5. Missing Cleanup Script Reference

The skill references `scripts/cleanup_stale_nous_flows.py` in Quick Diagnostic step 4, but this script was **not present** in `$HERMES_HOME/scripts/`.

**Current state:** Manual `rm -f` cleanup performed instead.

**Action:** Add script creation to skill's `scripts/` directory as a support file, or update Quick Diagnostic to use inline cleanup commands (chosen: inline commands for simplicity).

---

### 6. Empty `fallback_providers` Systemic Vulnerability (PREVENTION)

**Root cause:** `config.yaml` had `fallback_providers: []`. When primary provider (nous) went down, zero fallback → total outage.

**Mandatory post-recovery:** After DMOB completes `hermes model`, edit `config.yaml`:
```yaml
model:
  provider: auto   # NOT 'nous' — enables fallback chain
fallback_providers:
  - ollama-cloud   # credential_pool shows health=ok
  - opencode-go    # secondary (currently exhausted, may recover)
```

**Verification:** After config change, deliberately simulate Nous outage (temporary) and confirm gateway falls over to `ollama-cloud` automatically.

---

## Cron Job Error Classification

### Auth-related errors categorized:
1. **"Hermes is not logged into Nous Portal"** — gateway detects missing provider tokens; thrown before API call
2. **HTTP 401 "API key is invalid, blocked or out of funds"** — gateway attempted call with stale/invalid token; provider rejected
3. **"Refresh session has been revoked"** — refresh script detected `relogin_required` during token renewal

All trace back to same root: OAuth session fully revoked.

---

## Recovery Path Decision (2026-05-04)

**Device flow NOT attempted** because:
- Refresh token present but invalid; device flow would initiate fresh OAuth (same as `hermes model` but programmatic)
- Device code endpoint likely rate-limited from repeated refresh failures
- Manual `hermes model` is faster and recommended per playbook

**If DMOB unavailable for interactive re-auth**, fallback to device flow with outer timeout guard:
```bash
timeout 30s python3 -c "import sys; sys.path.insert(0, '/usr/local/lib/hermes-agent'); from hermes_cli.auth import _nous_device_code_login; r = _nous_device_code_login(open_browser=False, timeout_seconds=5); print(r)"
# Save output, send verification_uri_complete + user_code to DMOB
```

---

## Vault Documentation Updated

- Incident log: `00-HQ/Operations/Infrastructure-Issues.md` (appended re-detection at 2026-05-04 00:30 UTC)
- Mess Hall alert: `11-Mess Hall/2026/W18-2026/nous-oauth-revoked-alert-2026-05-04.md`
- Today's flags: `11-Mess Hall/2026/W18-2026/today.md`

---

## Open Questions (Post-Mortem)

1. **Why did the refresh token get revoked?** Token lifetime is ~30 days; obtained 2026-05-03 11:59 UTC, revoked by 2026-05-04 00:30 (~13h total). Unusually short. Possible causes:
   - Explicit revocation from Nous Portal (user action)
   - Provider-side security policy (suspicious activity, IP change)
   - Concurrent refresh attempts triggered rate-limit → revocation (unlikely, would be temporary)
   - Bug in refresh script causing invalid refresh requests?

2. **Why was `fallback_providers` empty?** Config vulnerability known from prior incident (2026-05-03). Was the mandated post-recovery config change missed?

3. **Watchdog coverage gap:** Why didn't Gentech Watchdog alert on cron job auth failures? Its prompt only scans agent session transcripts, not cron `last_error` fields.

---

**Prepared:** 2026-05-04 00:45 UTC  
**Next check:** Watch for DMOB re-auth completion; verify refresh script success at next 10-min interval.
