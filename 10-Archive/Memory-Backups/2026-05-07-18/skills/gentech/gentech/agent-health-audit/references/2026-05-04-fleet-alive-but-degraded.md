# May 04, 2026 — Fleet Alive But Degraded

**Session**: cron_9ecfada01952 (May 04, 2026 ~00:55 UTC)
**Watchdog**: Gentech (this agent)
**Agents audited**: YoYo, DMOB, Desmond, Gentech

---

## Executive Summary

All four agents had **running gateway processes and were actively responding to Telegram messages**, but **critical service failures** rendered them functionally degraded:

- **TTS fleet-wide**: ElevenLabs quota exceeded (0 credits)
- **LLM auth fleet-wide**: Nous Portal tokens missing or expired
- **DMOB credential gap**: ANTHROPIC_TOKEN absent from `.env`
- **Cron orphaning**: Several agent jobs not in active registry or failing
- **Master service dead**: hermes-gateway.service failed since April 27 (but per-agent manual gateways running)

**Bottom line**: Alive ≠ healthy. A process can be running and responding while core dependencies (APIs, auth, cron) are broken.

---

## Findings per Agent

### YoYo
- **Process**: Running (PID 440490), responding to Telegram
- **Errors**: ElevevLabs 401 quota_exceeded (TTS broken)
- **Auth**: No Nous access_token (only refresh_token); provider state likely uninitialized
- **Cron**: `faed4f588aef` active but last run errored with "Hermes is not logged into Nous Portal"
- **Notes**: Earlier bytecode corruption (May 2) appears resolved by disk cleanup, but process likely still holding in-memory corruption from before restart

### DMOB
- **Process**: Running (PID 440307), responding to Telegram
- **Errors**: ElevenLabs 401 quota_exceeded; `RuntimeError: No Anthropic credentials found`
- **Auth**: No Nous access_token (only refresh_token)
- **Credentials**: `.env` contains ELEVENLABS_API_KEY but no ANTHROPIC_TOKEN/ANTHROPIC_API_KEY
- **Cron**: Several jobs showing auth errors (e.g., Sunday Skill Update, LayerZero DVN)

### Desmond
- **Process**: Running (PID 440291), responding to Telegram
- **Errors**: ElevenLabs 401 quota_exceeded; vision tool 404s (historical)
- **Auth**: No Nous access_token (only refresh_token)
- **Notes**: TTS broken; appears to be falling back to alternative providers for LLM calls (gateway responses still working)

### Gentech
- **Process**: Running (PID 440281), systemd-managed
- **Errors**: ElevenLabs 401 quota_exceeded
- **Auth**: access_token present but **expired** (2026-05-03T22:11:54 UTC)
- **Cron**: Watchdog itself active (`9ecfada01952`, last run ok at 00:47)

---

## Patterns Identified

### Pattern: Alive But Degraded
**Symptom**: Gateway process running, Telegram messages being sent/received, but core functionality broken (TTS fails, LLM calls fail, cron jobs error).

**Root causes** (often co-occurring):
1. Shared provider quota exhausted (ElevenLabs `quota_exceeded`)
2. OAuth access token expired/revoked; refresh_token may still be present but unusable
3. Missing required env vars (Anthropic) even though process runs
4. Stale in-memory bytecode or config from before restart

**Checklist**:
- [ ] Verify error.log contains only recent errors (last 5–30 min)
- [ ] Confirm `auth.json` has valid `access_token` and `expires_at` in future
- [ ] Check `.env` for required provider keys (ELEVENLABS_API_KEY, ANTHROPIC_TOKEN, etc.)
- [ ] Validate process environment actually loaded the keys: `tr '\0' '\n' < /proc/<pid>/environ | grep -i <key>`
- [ ] If bytecode corruption previously occurred, ensure gateway was restarted **after** `__pycache__` cleanup

### Pattern: Quota Exceeded Shared Provider Failure
**Symptom**: All agents log `ApiError: status_code: 401` with body `{'status': 'quota_exceeded', ...}` from the same provider (ElevenLabs).

**Diagnosis**:
```bash
for a in yoyo dmob desmond gentech; do
  echo "=== $a ==="
  grep -m1 "quota_exceeded" /root/.hermes/profiles/$a/logs/errors.log 2>/dev/null
done
```

**Fix**:
1. Top up the shared account or rotate to a different provider account
2. Update `ELEVENLABS_API_KEY` in all affected `.env` files
3. Restart all gateways (`.env` read at startup; no hot-reload)
4. Validate: `tail -50 errors.log | grep -c quota_exceeded` → should be 0

**Note**: `invalid_api_key` vs `quota_exceeded` require different fixes (rotate key vs top up quota). Check error body text, not just status code.

### Pattern: Nous OAuth Access Token Missing/Expired Fleet-Wide
**Symptom**: All agents show `needs_reauth: true` or missing `access_token` in `auth.json`. Gateway still runs but LLM-dependent jobs fail with "Hermes is not logged into Nous Portal."

**Detection**:
```bash
for a in yoyo dmob desmond gentech; do
  echo "=== $a ==="
  python3 -c "
import json
with open(f'/root/.hermes/profiles/$a/auth.json') as f:
    d = json.load(f)
nous = d.get('providers', {}).get('nous', {})
print(' auth_type:', nous.get('auth_type'))
print(' access_token:', 'access_token' in nous)
print(' refresh_token:', 'refresh_token' in nous)
if 'expires_at' in nous:
    print(' expires_at:', nous['expires_at'])
"
done
```

**Recovery**:
1. Run `hermes model` interactively for each agent profile (requires manual auth)
2. After re-auth, verify: `providers.nous.access_token` present, `expires_at` in future, `needs_reauth: false`
3. Run proactive refresh script: `~/.hermes/profiles/<agent>/scripts/refresh_nous_oauth.py` → expect `{"success": true, "needs_reauth": false}`
4. Validate cron jobs resume execution

**Important**: OAuth revocation (refresh_token invalid) requires full re-authentication. Expired access_token alone may auto-refresh if refresh_token still valid.

---

## Commands Run This Session

```bash
# Process table
ps aux | grep hermes

# Systemd status (global + per-agent)
systemctl --user status hermes-gateway.service
systemctl --user status hermes-gateway-yoyo.service
systemctl --user status hermes-gateway-dmob.service
systemctl --user status hermes-gateway-desmond.service
systemctl --user status hermes-gateway-gentech.service

# Error log tail (last 20 lines) per agent
tail -n 20 /root/.hermes/profiles/yoyo/logs/errors.log
tail -n 20 /root/.hermes/profiles/dmob/logs/errors.log
tail -n 20 /root/.hermes/profiles/desmond/logs/errors.log
tail -n 20 /root/.hermes/profiles/gentech/logs/errors.log

# Active cron list
hermes cron list

# Cron output directory check
ls -la /root/.hermes/cron/output/

# Auth.json inspection per agent (Python + jq attempted)
cat /root/.hermes/profiles/yoyo/auth.json | head -5
cat /root/.hermes/profiles/dmob/auth.json | head -5
cat /root/.hermes/profiles/desmond/auth.json | head -5
cat /root/.hermes/profiles/gentech/auth.json | python3 -m json.tool | head -10

# DMOB .env check
cat /root/.hermes/profiles/dmob/.env | grep -i anthropic

# Master cron jobs.json peek
head -n 100 /root/.hermes/cron/jobs.json

# Recent session search (no May 04 post-00:55 activity found)
session_search --query "May 04 2026 session after 00:55 error crash yoyo dmob desmond gentech"
```

---

## New / Updated Pitfalls to Embed

1. **"Process running ≠ service functional"** — Always check error.log for recent provider errors even if gateway is up and Telegram is responding.

2. **"Quota exceeded is a shared-state failure"** — When multiple agents use the same provider quota, exhaustion affects all simultaneously. Audit all agents, not just the one reporting the error.

3. **"Access token expiry can be silent until first LLM call"** — Some agents may not attempt LLM calls for minutes/hours after reboot. A running process does not guarantee valid tokens. Existence of `refresh_token` alone is not sufficient; check `access_token` and `expires_at`.

4. **"Cron orphaning can occur even with running gateways"** — Jobs may fail due to auth state, not scheduler state. Check job-specific `last_error` field and agent logs, not just `last_run_at`.

5. **"TTS failure may look like network errors"** — Always read the error body: `quota_exceeded` vs `invalid_api_key` have different fixes.

---

## Recommended Follow-ups (Not In Scope of This Skill)

- **Credential rotation**: Update ElevenLabs key across all `.env` files and restart all gateways
- **Nous re-authentication**: Run `hermes model` for each agent to mint fresh access tokens
- **DMOB Anthropic**: Add `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY` to `/root/.hermes/profiles/dmob/.env`
- **Master service repair**: Fix ExecStart path in `/root/.config/systemd/user/hermes-gateway.service` and restart to restore unified cron supervision
- **Bytecode cache restart**: Even after disk cleanup, restart YoYo & Gentech to flush in-memory corruption (unknown if still present)

---

## Related Sessions

- May 02–03, 2026: Full fleet collapse with bytecode corruption, master service failure, OAuth revocation (see references/*.md)
- This session (May 04): Fleet alive but degraded; persistent auth + quota issues
