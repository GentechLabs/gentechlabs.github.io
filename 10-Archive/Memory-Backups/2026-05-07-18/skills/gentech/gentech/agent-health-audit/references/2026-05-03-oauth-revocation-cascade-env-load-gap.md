# Watchdog Reference: 2026-05-03 — OAuth Revocation Cascade & TTS Env Loading Gap

**Session**: Cron-triggered Gentech Watchdog health check (May 3, 2026, 16:17 UTC)
**Agents audited**: Gentech, YoYo, DMOB, Desmond

---

## Critical Findings

### 1. Fleet-Wide OAuth Session Revocation (CRITICAL)
**Signature in logs**:
```
RuntimeError: Refresh session has been revoked Run `hermes model` to re-authenticate.
```

**Auth state fingerprint** (`/root/.hermes/auth.json`):
```json
{
  "tokens": { "expires_at": null },
  "agent_keys": []
}
```

**Impact**:
- All Nous-dependent cron jobs will fail once current tokens expire
- `Nous OAuth Proactive Refresh` job itself fails (circular dependency)
- Agents fall back to alternative providers (e.g., stepfun) but reliability degraded
- Telegram connectivity degrades as provider auth fails chain reaction

**Remediation**: Each agent profile must run `hermes model` to re-authenticate with Nous Portal. No automatic recovery path.

---

### 2. TTS Service Failure — Environment Loading Gap
**Observed**: ElevenLabs API key present in `.env` files across all profiles:
```
ELEVENLABS_API_KEY=bb158b2f8063a7d10519ffb3a349d168195f67c9fe5698532e5c191d70298674
```

But **absent from running process environment**:
```
/root/.hermes/profiles/dmob/gateway.pid (PID 292967): ELEVENLABS key NOT found in process environment
/root/.hermes/profiles/desmond/gateway.pid (PID 292951): ELEVENLABS key NOT found
/root/.hermes/profiles/yoyo/gateway.pid (PID 292984): ELEVENLABS key NOT found
/root/.hermes/profiles/gentech/gateway.pid (PID 307708): ELEVENLABS key NOT found
```

**Result**: DMOB & Desmond actively logging TTS 401 errors (23 and 15 respectively in last 200 log lines); Gentech/YoYo not currently logging TTS errors likely due to lower recent voice usage.

**Root cause hypothesis**: Gateways were started before `.env` files were updated with the current ElevenLabs key. `.env` is read at process startup only; no hot-reload.

**Verification command**:
```bash
# Check what ELEVENLABS key (if any) a running process sees
tr '\0' '\n' < /proc/$(cat /root/.hermes/profiles/<agent>/gateway.pid | jq -r .pid)/environ | grep -i elevenlabs
```

**Fix**: Restart all agent gateways after confirming `.env` contains valid key. Key validity confirmed via direct API test (curl returned 200).

---

### 3. DMOB Missing Anthropic Credentials
**Discovery**: DMOB `.env` contains no `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY`.
**Impact**: Any Anthropic-dependent cron jobs (e.g., "Defi Milestone") will fail with `RuntimeError: No Anthropic credentials found`.
**Action required**: Add valid Anthropic API key to `/root/.hermes/profiles/dmob/.env` and restart DMOB gateway.

---

### 4. Cron Pipeline Actually Running (Contrary to Earlier Hypotheses)
**Evidence**: All agent profiles show recent `last_run_at` timestamps:
- Gentech: 31 jobs, recent runs at 2026-05-03T11:45–16:11
- YoYo: 27 jobs, recent runs at 2026-05-03T11:45–16:15
- DMOB: 8 jobs, recent runs at 2026-05-03T11:44–12:00
- Desmond: 6 jobs, recent runs at 2026-05-03T10:00–12:00

**Conclusion**: Cron scheduler IS firing jobs. The earlier "never executed" findings from May 2 were accurate for that snapshot, but the system has been restarted/recovered since. The master `hermes-gateway.service` unit remains FAILED, but agents were manually started with `--replace` and cron operates within those processes.

---

### 5. Bytecode Corruption Cleared
**Earlier state** (May 2): Systemic `EOFError: marshal data too short` from corrupted `gemini_native_adapter.cpython-311.pyc` and `copilot_acp_client.cpython-311.pyc`.
**Current state**: No marshal errors in last 30 lines of any agent `errors.log`. Bytecode cache appears clean. Likely resolved by earlier deletion of `.pyc` files followed by gateway restarts (though at least one restart cycle required to flush in-memory corrupted bytecode).

---

## Operational Notes

### Gateway Process State
All four agents running as of 16:17 UTC:
```
gentech: PID 307708 (started 14:34:59)
yoyo:    PID 292984 (started 12:05:05)
dmob:    PID 292967 (started 12:05:00)
desmond: PID 292951 (started 12:04:59)
```

### Lock Files Present but Not Blocking
Each profile's `cron/.tick.lock` exists with age ~0.5–1.5 minutes, indicating active ticker operation.

### Log Freshness
- `gateway.log` files across all agents show recent activity (16:07–16:08 UTC inbound/response cycles)
- `errors.log` shows OAuth revocation errors as the dominant recent failure mode

---

## Recommended Immediate Actions

1. **Re-authenticate all agents** (OAuth revocation):
   ```bash
   hermes -p gentech model
   hermes -p yoyo model
   hermes -p dmob model
   hermes -p desmond model
   ```

2. **Rotate/restart TTS**:
   ```bash
   # Verify ElevenLabs key in all .env files, then:
   pkill -f "hermes.*gateway"
   # Restart each agent gateway
   /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile gentech gateway run --replace &
   # ... repeat for yoyo, dmob, desmond
   ```

3. **Fix DMOB Anthropic credentials**:
   ```bash
   echo "ANTHROPIC_API_KEY=<valid-key>" >> /root/.hermes/profiles/dmob/.env
   pkill -f "hermes.*dmob.*gateway"
   /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile dmob gateway run --replace &
   ```

4. **Repair master systemd unit** (optional but recommended for reboot resilience):
   ```bash
   sed -i 's|/root/.hermes/hermes-agent/venv/bin/python|/usr/local/lib/hermes-agent/venv/bin/python|' \
     /root/.config/systemd/user/hermes-gateway.service
   systemctl --user daemon-reload
   systemctl --user restart hermes-gateway.service
   ```

---

## Diagnostic Commands Used This Session

```bash
# 1. Verify master service state
systemctl --user status hermes-gateway.service --no-pager --output=json

# 2. Enumerate running gateway processes
ps aux | grep hermes | grep gateway

# 3. Parse gateway.pid files (JSON format)
for p in gentech yoyo dmob desmond; do
  cat /root/.hermes/profiles/$p/gateway.pid | jq -r '.pid'
done

# 4. Read process environment to verify API key loading
tr '\0' '\n' < /proc/<pid>/environ | grep -i elevenlabs

# 5. Check cron job registry freshness
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | {id, name, last_run_at}'

# 6. Profile-level cron job state (actual source of truth)
for p in gentech yoyo dmob desmond; do
  echo "=== $p ==="
  jq '.jobs[] | select(.enabled==true) | {name, last_run_at}' \
    /root/.hermes/profiles/$p/cron/jobs.json 2>/dev/null | head -5
done

# 7. Scan recent error patterns (last 30 lines)
for p in gentech yoyo dmob desmond; do
  echo "=== $p errors (last 30) ==="
  tail -30 /root/.hermes/profiles/$p/logs/errors.log | grep -i 'error\|exception\|401\|marshal\|revoked'
done

# 8. Validate ElevenLabs key via direct API
curl -s -o /dev/null -w '%{http_code}' \
  -H 'xi-api-key: <key>' https://api.elevenlabs.io/v1/voices

# 9. Check auth.json state
cat /root/.hermes/auth.json | jq '{tokens: {expires_at}, agent_keys: length}'

# 10. Verify log file modification vs content freshness
stat /root/.hermes/profiles/<agent>/logs/gateway.log
tail -1 /root/.hermes/profiles/<agent>/logs/gateway.log
```

---

**Status as of 2026-05-03T16:17 UTC**: Fleet operational but degraded. OAuth session revoked fleet-wide; TTS broken due to process env gap; DMOB missing Anthropic credentials. Cron jobs ARE executing despite systemd unit failure. Immediate re-auth and gateway restarts required.
