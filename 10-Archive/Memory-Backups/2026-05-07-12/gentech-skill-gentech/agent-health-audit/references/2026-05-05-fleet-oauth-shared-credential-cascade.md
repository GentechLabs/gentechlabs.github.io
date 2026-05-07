# 2026-05-05: Fleet-Wide Shared OAuth Credential Cascade

**Watchdog**: Gentech (May 5, 2026 03:43 UTC)

##Executive Summary

All four agents (YoYo, DMOB, Desmond, Gentech) share identical Nous OAuth credentials in their `auth.json` files. The shared access token expired `2026-05-04T14:56:57` (~13 hours before this check), causing fleet-wide model 404 errors and functional paralysis despite gateways remaining running and Telegram connections appearing active.

## Evidence

### Credential Identity Confirmation

All agents report the same `refresh_token` prefix:

```
yoyo:    refresh_token prefix=rt_O13KZOcbM08e_bWEhYCIIXzdBzG
dmob:    refresh_token prefix=rt_O13KZOcbM08e_bWEhYCIIXzdBzG
desmond: refresh_token prefix=rt_O13KZOcbM08e_bWEhYCIIXzdBzG
gentech: refresh_token prefix=rt_O13KZOcbM08e_bWEhYCIIXzdBzG
```

Full credential pool entry shows identical `id: dd3bca`, `label: device_code`, `agent_key_id: cmorb5rmt000qji08se9tja02` across all profiles.

### Access Token Expiry

All agents share the same `expires_at: 2026-05-04T14:56:57.210470+00:00` (expired). `agent_key_expires_at: 2026-05-05T14:41:57.790Z` remains valid but is unusable without a valid access token.

### Error Pattern (Last 6 Hours)

| Agent | Error Count | Dominant Error |
|-------|------------|----------------|
| Yoyo  | 131        | `ModelNotFound_404: nousresearch/trinity-large-thinking` |
| DMOB  | 66         | Mix of 404 and `AUTH_Other` (ElevenLabs quota) |
| Desmond| 62        | Mix of 404 and `AUTH_Other` |
| Gentech| 67        | 404 + Telegram `Chat not found` |

All agents show the same 404 error body: `"Model 'nousresearch/trinity-large-thinking' not found"` — note this is a misconfigured model ID combined with expired OAuth; see `agent-health-audit` model deprecation patterns for the prefix fix (`arcee-ai/trinity-large-thinking`), but OAuth must be fixed first.

## Timeline

- `2026-05-04 14:41:58` — OAuth device-code flow completed; refresh token minted (`rt_O13KZOcbM08e_bWEhYCIIXzdBzG...`)
- `2026-05-04 14:56:57` — Access token expires (lifetime 900s / 15 min). No proactive refresh occurred (job may be broken or token revoked)
- `2026-05-05 00:00:00` — First observed 404 model errors in logs (agents attempt inference with expired token → provider returns 404)
- `2026-05-05 03:43` — Watchdog audit confirms fleet-wide credential sharing and expiry

## Impact

- **All cron jobs blocked**: Any job requiring LLM inference fails at first provider call
- **Direct messages failing**: Agents cannot generate assistant responses; session completeness = 0% across fleet
- **Telegram**: Gentech additionally blocked by `Chat not found` (separate issue); other agents show flood-control incidental
- **Skills**: Desmond and DMOB also missing skills (`cmc-watchlist-scraper`, `crypto-monitoring-cron`) causing additional cron skips

## Recovery Procedure

**Per agent** (do not skip any):

1. Run interactive re-authentication:
   ```bash
   hermes model --provider nous
   ```
   Follow device-code flow in browser/terminal to obtain fresh tokens.

2. Verify `auth.json` updated:
   ```bash
   python3 -c "import json; d=json.load(open('/root/.hermes/profiles/<agent>/auth.json')); print(d['credential_pool']['nous'][0]['expires_at'])"
   ```
   Should show a future timestamp (now + ~15 min).

3. Restart gateway:
   ```bash
   hermes gateway stop --profile <agent>
   hermes gateway run --profile <agent> --replace
   ```

4. Validate:
   ```bash
   tail -20 /root/.hermes/profiles/<agent>/logs/errors.log | grep -i 'not logged into Nous'
   ```
   Should return no lines. Check cron execution resumes within schedule interval.

## Root Cause Analysis

**How did sharing happen?**
Likely scenario: Initial agent provisioning ran `hermes model` once under a single profile, then the entire `~/.hermes/` directory (or just `auth.json`) was duplicated or cloned to other profile directories. This created independent files with identical credential content. Each profile's OAuth state is now decoupled but seeded from the same source.

**Why didn't proactive refresh recover?**
The refresh token may have been revoked server-side, or the refresh endpoint returned an error that wasn't handled. The `refresh_nous_oauth.py` script (if present) would have failed with `Refresh session has been revoked` on any attempt after expiry.

## Prevention

1. **Independent OAuth per agent**: Each profile must complete its own device-code flow. Do not copy `auth.json`.
2. **Credential isolation**: Consider registering separate Nous applications per agent (different `client_id`) to prevent single-point-of-failure.
3. **Watchdog alert**: Add health-check that flags when `refresh_token` prefixes are identical across ≥3 agents.
4. **Proactive refresh monitoring**: Ensure `Nous OAuth Proactive Refresh` cron job is registered and executing; it should automatically refresh access tokens before expiry. If missing, create it.

## Follow-up Tasks

- [ ] Re-authenticate all four agents via `hermes model`
- [ ] Restart all gateways post-reauth
- [ ] Fix model ID misconfiguration in each agent's `config.yaml` (`nousresearch/trinity-large-thinking` → `arcee-ai/trinity-large-thinking`)
- [ ] Restore missing skills for DMOB (`cmc-watchlist-scraper`) and Desmond (`crypto-monitoring-cron` or equivalent) from vault
- [ ] Resolve Gentech Telegram `Chat not found` — re-invite bot or update chat ID
- [ ] Verify DMOB has required `ANTHROPIC_TOKEN` in `.env`
- [ ] After recovery, run health check again to confirm `STATUS:OK`

## See Also

- `agent-health-audit` patterns:
  - Auth Revocation Cascade Detection
  - OAuth session state fingerprint
  - Auth state desynchronization
  - Model Provider Deprecation Cascade (for the secondary misconfiguration)
  - Telegram "Chat not found" Access Failure (Gentech-specific)
