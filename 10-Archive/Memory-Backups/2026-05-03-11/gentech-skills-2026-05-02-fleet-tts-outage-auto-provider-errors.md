# Watchdog Alert Reference — May 2, 2026

## Trigger
Scheduled cron job (`Gentech Watchdog`, ID: `9ecfada01952`, schedule: `*/5 * * * *`) executed health audit on agents YoYo, DMOB, Desmond, Gentech.

## Findings Summary

### Critical — TTS Infrastructure Outage
- **Agents affected**: YoYo (481 × 401), DMOB (278 × 401), Desmond (220 × 401)
- **Symptom**: `elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}`
- **Root cause**: Shared ElevenLabs API key `bb158b2f8063a7d10519ffb3a349d168195f67c9fe5698532e5c191d70298674` invalid (revoked/expired on ElevenLabs side)
- **Validation**: `curl -H "xi-api-key: <key>" https://api.elevenlabs.io/v1/user` returns `missing_permissions` error (key exists but lacks `user_read`; TTS endpoint returns 401 invalid)
- **Fix**: Rotate ElevenLabs key in all agent `.env` files: `/root/.hermes/profiles/{yoyo,dmob,desmond,gentech}/.env` → update `ELEVENLABS_API_KEY=...`
- **Verification**: Run TTS generation test: `echo "test" | hermes tts --provider elevenlabs` should succeed (200 OK, return audio file)

### Degraded — Auxiliary Auto-Provider Connection Failures
- **Agents affected**: YoYo (433 recent connection errors), Gentech (358 recent connection errors)
- **Symptom**: `Auxiliary session_search: connection error on auto — falling back to nous (google/gemini-3-flash-preview)`
- **Interpretation**: The configured `auxiliary.auto.provider` endpoint is unreachable; agent falls back to hardcoded nous/google provider. This bypasses intended provider selection logic.
- **Likely cause**: Network/firewall blocking, misconfigured provider URL, or upstream service outage.
- **Check**: Inspect agent `config.yaml` → `auxiliary.auto.provider` setting; verify connectivity to that endpoint.
- **Status during alert**: No recent errors in last minute (errors were recurring earlier; may be transient or resolved).

### Cron Pipeline — Previously Broken, Now Operational
- **Discovered**: Four department-specific cron jobs (`jobs.json`) had `last_run_at: null` and had never executed despite being `active`.
- **Root cause**: `hermes cron list` showed different job IDs than those in `jobs.json`; the cron scheduler was not loading the agency jobs.
- **Current status**: Watchdog cron (`9ecfada01952`) running every 5 min; YoYo LP Watchlist (`faed4f588aef`) last run `2026-05-02T20:18:51 ok`.

### Historical Context (Earlier in Session)
- Bytecode corruption (`marshal data too short`) cleared; gateways restarted.
- Systemd services now active for all four agents (gentech since 15:39, yoyo/dmob/desmond since 20:17 UTC).
- No recent errors in last 5 min (since 22:25).

## Error Count Snapshot (as of 22:31 UTC)
| Agent   | Total 401/TTS errors | Recent errors (22:25–22:31) |
|---------|---------------------|-----------------------------|
| YoYo    | 481                 | 0                           |
| DMOB    | 278                 | 0                           |
| Desmond | 220                 | 0                           |
| Gentech | 30                  | 0                           |

## Key Commands Used in This Audit
```bash
# 1. Verify gateway processes across profiles
systemctl --user status hermes-gateway-{yoyo,dmob,desmond,gentech}.service

# 2. Check error patterns by agent
grep -c '2026-05-02 22:3' /root/.hermes/profiles/{yoyo,dmob,desmond,gentech}/logs/errors.log
grep '401' /root/.hermes/profiles/<agent>/logs/errors.log | tail -1

# 3. Validate ElevenLabs key via curl
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user

# 4. Check auxiliary auto provider connection errors
tail -2000 /root/.hermes/profiles/{yoyo,gentech}/logs/agent.log | grep -i 'connection error on auto' | wc -l

# 5. Inspect cron job execution state
hermes cron list
grep -A 3 '"name":.*YoYo\|DMOB\|Desmond\|Gentech' /root/.hermes/cron/jobs.json

# 6. Correlate log freshness vs process liveness
stat -c '%y' /root/.hermes/profiles/<agent>/logs/errors.log
```

## Follow-up Actions Required
1. **Immediate**: Rotate ElevenLabs API key in all agent `.env` files and restart TTS-dependent workflows.
2. **Investigate**: Why was the ElevenLabs key invalidated? Check ElevenLabs dashboard for quota limits, key revocation, or permission changes.
3. **Monitor**: Auto-provider connection errors — may indicate upstream provider outage or config drift.
4. **Prevent**: Add cron job execution verification to future Watchdog runs (ensure `last_run_at` advances within expected window).

## Skill References
- `agent-health-audit` — Systematic health check methodology and recovery procedures
- `system-health` — System-level resource and service diagnostics