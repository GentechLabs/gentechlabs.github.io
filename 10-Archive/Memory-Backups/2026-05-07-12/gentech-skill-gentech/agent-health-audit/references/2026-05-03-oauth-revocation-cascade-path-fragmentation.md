---
date: 2026-05-03
detected_by: Gentech Watchdog
severity: P0
status: Active (resolved after re-auth)
incidents:
  - "Nous OAuth Session Revoked — ACTIVE"
  - "Nous OAuth Revocation — ACTIVE"
  - "Nous Portal OAuth Session Revoked (RE-ACTIVATED)"
---

# Incident: May 3, 2026 — Nous OAuth Revocation Cascade + Model Support Mismatch

## TL;DR
Fleet-wide failure of all Nous-dependent cron jobs caused by OAuth refresh token revocation. Compounded by a `stepfun/step-3.5-flash not supported` error after re-auth attempt. Additionally discovered YoYo's D5 monitoring script failing due to AAE config path fragmentation across HERMES profiles.

**Impact time**: ~11:50 UTC — ongoing through 21:41 UTC
**Affected agents**: All 4 (Gentech, YoYo, DMOB, Desmond)
**Jobs failing**: 13+ cron jobs including D5 monitoring, Mess Hall rotations, Kite AI monitor, LayerZero DVN monitor, social briefing, hackathon submission check, skills update

## Error Manifestation Pattern

### Phase 1 — Auth Failure Surge (~11:50–12:00 UTC)
Multiple jobs simultaneously began failing with:
```
RuntimeError: Hermes is not logged into Nous Portal. Run `hermes model` to re-authenticate.
```
And:
```
RuntimeError: Error code: 401 - {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds...'}
```

Error clusters appeared in:
- `/root/.hermes/logs/errors.log`
- Individual agent cron logs (`/root/.hermes/profiles/yoyo/cron.log`)
- `hermes cron list` output (last_run status fields)

### Phase 2 — Refresh Script Exhaustion (~19:00–21:00 UTC)
The proactive refresh job `refresh_nous_oauth.py` started returning:
```json
{"success": false, "needs_reauth": true, "error": "Refresh session has been revoked"}
```
And later:
```
RuntimeError: Model stepfun/step-3.5-flash not supported
```
Combined, these blocked any automatic recovery. The 429 rate-limit on device code endpoint prevented programmatic re-auth.

### Phase 3 — Secondary Failures
- **YoYo D5 monitoring**: Separate issue — `AAE config missing` path error, 3 repeated failures in cron.log
- **Mess Hall rotation jobs**: `ValueError: I/O operation on closed file.` (appeared in Break 1, Break 2, Break 3, Pre-Shift, Post-Shift, social-briefing) — likely related to gateway instability during auth cascade
- **Agent coordination**: All agents marked OFFLINE on coordination board as of May 3 morning (Sunday, expected but handoff acks still pending)

## Root Causes Identified

### Primary: OAuth Session Revocation
- Refresh token expired or was manually revoked from Nous Portal
- `auth.json` showed `tokens.expires_at` in past (2026-05-03T18:28:26Z)
- Device flow attempts hit rate limits (429)
- Affects **all** Hermes profiles sharing the same Nous credentials

### Secondary: Model Support Withdrawal
When `hermes model` was attempted (~21:36 UTC), the configured model `stepfun/step-3.5-flash` was no longer supported by the provider, creating compound error: valid credentials but unusable model selection.

### Tertiary: State File Path Fragmentation (YoYo-specific)
`d5-lp-consolidated.py` hardcoded path `/root/home/.hermes/scripts/.lfj-aae-config.json` (note `/root/home/` vs correct `/root/.hermes/`). Actual config exists at `/root/.hermes/scripts/.lfj-aae-config.json` and is symlinked per-profile at `/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json`.

## Recovery Steps Taken

1. **Manual re-auth initiated**: `hermes model` run on Gentech profile at 21:36 UTC (PID 370053) to re-authenticate with Nous Portal
2. **Gateway restart**: Required after re-auth to inject new credentials into all gateway processes
3. **Pending**: Verification that all cron jobs resume successful execution after credentials + model selection corrected

## Verification Checklist (Post-Recovery)

After DMOB completes OAuth re-auth and model selection:
- [ ] Run `hermes model` interactively and select a supported Nous model (not `step-3.5-flash` if withdrawn)
- [ ] Restart all gateways: `pkill -f hermes_cli.main` then restart each profile
- [ ] Verify `auth.json` has fresh `expires_at` > now + 20 days
- [ ] Run `refresh_nous_oauth.py` manally: expect `{"success": true, "needs_reauth": false, "remaining_seconds": >300}`
- [ ] Manually trigger one affected job: `hermes cron run "YoYo — Crypto Watchlist + LP Monitor"` and confirm output
- [ ] Check `/root/.hermes/profiles/yoyo/cron.log` — last entry should be `ok` not `ERROR`
- [ ] Fix YoYo D5 path: Update `d5-lp-consolidated.py` or create missing symlink:  
  `ln -sf /root/.hermes/scripts/.lfj-aae-config.json /root/.hermes/profiles/yoyo/home/.hermes/scripts/`
- [ ] Clear `I/O operation on closed file` errors by ensuring stable gateway uptime (no mid-job restarts)

## Reference Commands

```bash
# Check auth status across all profiles
hermes status

# Re-authenticate (must be interactive)
export HERMES_HOME=/root/.hermes/profiles/gentech
hermes model

# Verify OAuth refresh script
~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py

# List failing cron jobs directly
hermes cron list | grep -A2 'error:'

# Check YoYo cron log
tail -20 /root/.hermes/profiles/yoyo/cron.log

# Fix path fragmentation (run per-agent as needed)
mkdir -p /root/.hermes/profiles/yoyo/home/.hermes/scripts
ln -sf /root/.hermes/scripts/.lfj-aae-config.json \
       /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json

# Restart all gateways cleanly
for agent in gentech yoyo dmob desmond; do
  pkill -f "hermes.*$agent.*gateway" || true
  /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile $agent gateway run --replace &
done
sleep 5

# Verify model support (list available Nous models)
hermes model list
```

## Key Lessons Learned

1. **OAuth revocation affects all agents instantly** — there is no graceful degradation; every Nous-dependent job fails with 401. Recovery requires manual intervention per profile.
2. **Model deprecation can mask as auth failure** — the error `Model ... not supported` appears alongside or after 401s; always read the full error text before assuming credentials are the only problem.
3. **Path hardcoding creates hidden fragilities** — the YoYo D5 script had a hardcoded config path using `/root/home/` symlink target rather than the actual install path. This went undetected until the script started executing after consolidation.
4. **Cron failures cascade into file handle errors** — The `I/O operation on closed file` appeared in Mess Hall jobs possibly because the gateway restarted mid-execution during the auth recovery attempts, closing stdout/stderr prematurely.
5. **Silent weekend agent OFFLINE state** — All agents were already OFFLINE on May 3 morning (Sunday expected), but handoff acknowledgments were still pending. Weekend cadence should not block critical handoffs.

## Follow-up Actions (Unresolved as of incident writeup)

- [ ] **DMOB**: Complete `hermes model` re-auth on Gentech profile (assigned)
- [ ] **YoYo**: Fix AAE config path bug in `d5-lp-consolidated.py` OR ensure symlink exists across all relevant profiles
- [ ] **DMOB**: Verify and acknowledge pending handoffs H2026-05-02-01 and H2026-05-02-02
- [ ] **Desmond**: Refresh master-todo.md from Apr 25 baseline ( stale)
- [ ] **All agents**: Confirm census check-in on coordination board after recovery

## Related Skill Updates

- `agent-health-audit`: Added pitfall entries for OAuth+model support compound failure, config path fragmentation, cron file-handle errors
- New diagnostics reference added under this incident ID for future audit trail consistency
