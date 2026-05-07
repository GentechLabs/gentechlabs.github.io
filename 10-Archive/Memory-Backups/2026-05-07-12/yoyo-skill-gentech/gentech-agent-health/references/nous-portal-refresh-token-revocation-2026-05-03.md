# Nous Portal Refresh Token Revocation — Systemic Auth Cascade

**Date:** May 3, 2026  
**Session:** Gentech Watchdog health check (cron_9ecfada01952_20260503_114425)  
**Agents affected:** YoYo, DMOB, Desmond, Gentech (all profiles using `nous` provider)

---

## Error Signature

```
RuntimeError: Refresh session has been revoked
Run `hermes model` to re-authenticate.
```

Stack trace pattern:
```
File "/usr/local/lib/hermes-agent/hermes_cli/auth.py", line 2646, in _refresh_access_token
  raise AuthError(description, provider="nous", code=code, relogin_required=relogin)
hermes_cli.auth.AuthError: Refresh session has been revoked
```

Secondary variant (HTTP 401 from API):
```
RuntimeError: Error code: 401 - {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds. Please go visit the portal to sort that out: https://portal.nousresearch.com '}
```

---

## Trigger Conditions

1. **Refresh token reuse** — Another process (monitoring script, separate Hermes install, custom self-heal hook) called `POST /api/oauth/token` with the refresh token without persisting the rotated token back. Nous refresh tokens are single-use; concurrent mint attempts invalidate the session.

2. **External revocation** — Token manually revoked from Nous Portal dashboard or automated security policy (suspicious activity, IP change, rate-limit breach).

3. **Token expiry** — Access token lifetime exceeded (observed: access token expired 2026-05-01 23:24:26 UTC; API key expired 2026-05-02 23:09:26 UTC).

---

## Fleet-Wide Impact Pattern

- All agents using `nous` provider fail simultaneously (within 1–2 minutes)
- Cron jobs fail with empty responses or error states
- Gateway remains running and Telegram-connected, but LLM-dependent tasks blocked
- `hermes status` may incorrectly show "logged in" due to cached state; actual token is invalid

**Detect fleet-wide cascade:**
```bash
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep -E "Refresh session has been revoked|Hermes is not logged into Nous Portal" \
    /root/.hermes/profiles/$agent/logs/errors.log | tail -3
done
```

If all 4 agents show the same error within the last hour → systemic auth failure.

---

## Recovery Procedure

**Step 1 — Stop gateways (optional but recommended for clean state):**
```bash
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway stop
done
sleep 3
```

**Step 2 — Re-authenticate Nous Portal per agent:**
```bash
hermes -p yoyo model      # Follow device-code flow prompts
hermes -p dmob model
hermes -p desmond model
hermes -p gentech model
```

**Step 3 — Verify credential pool refreshed:**
```bash
hermes -p yoyo auth status
# Should show nous: "authenticated" with valid expiry
```

**Step 4 — Restart gateways:**
```bash
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway start
done
sleep 10
```

**Step 5 — Confirm cron recovery:**
```bash
hermes cron list | grep -E "error:|RuntimeError|401"
# Should show no auth-related errors
```

---

## Prevention & Hardening

1. **Avoid concurrent Hermes processes** — Only one Hermes gateway per profile should run at a time. Multiple processes contend for the same refresh token and cause reuse revocation.

2. **Disable external monitoring of auth.json** — Health-check scripts must use `hermes auth status` instead of reading `~/.hermes/auth.json` or calling `/api/oauth/token` directly.

3. **Add fallback provider in config.yaml** — Prevent single-point failure:
   ```yaml
   model:
     provider: auto  # Tries opencode-go, ollama-cloud, then nous
     providers:
       - nous
       - opencode-go
       - ollama-cloud
   ```

4. **Proactive token renewal** — Run `hermes model --renew` 24h before expiry:
   ```bash
   # Add to cron (system-level, outside Hermes):
   0 9 * * * /usr/local/bin/hermes -p yoyo model --renew 2>/dev/null || true
   ```

5. **Monitor auth status, not tokens** — Embed this check in watchdog cron:
   ```bash
   hermes auth status | grep -q "nous.*authenticated" || \
     echo "ALERT: Nous auth expired on $(hostname)" | \
     telegraph -G Gentech-Webhook
   ```

---

## Related Failures Observed May 3, 2026

- **7 cron jobs** failed with Nous auth errors: Gentech Watchdog, Brain Backup → GitHub, Mess Hall Post-Shift, D5 Milestone, x402 Ecosystem Monitor, LayerZero DVN Monitor, Weekly Skills Update Check
- **Coordinated crash cascade** at 11:52–11:56: all 4 gateways exited with TEMPFAIL/ signal 10 within 60 seconds, likely triggered by auth revocation propagating through shared provider client cache
- **Gateway restart loop**: After crash, gateways restarted but immediately hit auth error again, requiring manual `hermes model` intervention

---

## Detection Script

Save as `scripts/detect_nous_auth_cascade.py` in this skill and run:
```bash
python3 detect_nous_auth_cascade.py --agent-prefixes yoyo dmob desmond gentech
```

Outputs:
- `HEALTHY` — all agents authenticated
- `CASCADE_DETECTED` — all agents showing revoked refresh token
- `PARTIAL_OUTAGE` — subset of agents affected (check individually)
