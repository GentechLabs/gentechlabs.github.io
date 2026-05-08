# ElevenLabs TTS 401 Error Pattern

**Detected:** May 2, 2026 — YoYo & Gentech agents
**Severity:** HIGH — voice responses completely fail, text fallback only

## Error Signature

```
ERROR tools.tts_tool: TTS generation failed (elevenlabs): status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': '...'}}
```

**Log locations:**
- YoYo: `/root/.hermes/profiles/yoyo/logs/errors.log` (8030 error keywords, 5 TTS 401s in last 2h)
- Gentech: `/root/.hermes/profiles/gentech/logs/errors.log` (15112 error keywords, 6 TTS 401s in last 2h)

## Root Cause

ElevenLabs API key invalid/expired or environment variable not loaded in gateway process.

**Key observation:** Both agents configure `elevenlabs` provider with `voice_id` and `model_id` in `config.yaml`, but:
- No `ELEVENLABS_API_KEY` found in environment (`env | grep ELEVEN` → 0 results)
- No key in `config.yaml` (correct — should be env-only)
- Gateway processes started without the env var, causing immediate 401 on every TTS call

## Diagnostic Checklist

1. **Check active environment for ElevenLabs key:**
   ```bash
   systemctl show-environment | grep -i eleven
   sudo -u root env | grep -i eleven
   ```

2. **Verify agent config references the correct provider:**
   ```bash
   grep -A5 'elevenlabs:' /root/.hermes/profiles/yoyo/config.yaml
   ```

3. **Check gateway process environment (live):**
   ```bash
   cat /proc/923106/environ | tr '\0' '\n' | grep -i eleven
   cat /proc/923094/environ | tr '\0' '\n' | grep -i eleven
   ```

4. **Confirm it's not a rate-limit error:** 401 = auth failure; 429 = rate limit.

## Recovery Path

**Option A — Restart gateway with env loaded (temporary):**
```bash
# Stop gateways
hermes -p yoyo gateway stop
hermes -p gentech gateway stop

# Export key in same shell that launches gateway
export ELEVENLABS_API_KEY="eleven_xxxxxxxx"
hermes -p yoyo gateway run --replace &
hermes -p gentech gateway run --replace &
```

**Option B — Systemd user service persistent fix (recommended):**
```bash
# Edit systemd user environment
systemctl --user edit hermes-gateway-yoyo
systemctl --user edit hermes-gateway-gentech

# Add:
[Service]
Environment="ELEVENLABS_API_KEY=eleven_xxxxxxxx"
EnvironmentFile=/root/.hermes/profiles/yoyo/.env  # if .env exists

# Reload and restart
systemctl --user daemon-reload
systemctl --user restart hermes-gateway-yoyo hermes-gateway-gentech
```

**Option C — Fallback to alternative TTS provider (immediate):**
Edit `/root/.hermes/profiles/<agent>/config.yaml`:
```yaml
tts:
  provider: openai  # or mistral, xai, edge
  openai:
    model: gpt-4o-mini-tts
    voice: alloy
```
Gateway restart required: `hermes -p <agent> gateway restart`

## Agent-Specific Impact

| Agent | Gateway PID | Uptime | TTS Errors (2h) | Status |
|-------|-------------|--------|-----------------|--------|
| YoYo   | 923106      | 12h    | 5               | DEGRADED |
| Gentech| 923094      | 12h    | 6               | DEGRADED |
| DMOB   | 922890      | 12h    | 0 (no elevenlabs configured) | OK |
| Desmond| 922877      | 12h    | 0 (no elevenlabs configured) | OK |

## Prevention

- **ENV file per agent:** `/root/.hermes/profiles/<agent>/.env` with `ELEVENLABS_API_KEY`
- **Gateway manager should source per-agent .env before launching** — if this broke after a restart, the env loading mechanism needs audit.
- **Monitor:** Add TTS error rate (>5/day) to agent health check alerts.

## Related Observations

- DMOB and Desmond do not use ElevenLabs (no `elevenlabs` block in their configs) — unaffected.
- Both failing agents share same gateway parent process model; check if Hermes gateway launcher dropped env var loading in vX.Y.Z.
- Consider feature flag to disable TTS on sustained 401s rather than spam error logs.
