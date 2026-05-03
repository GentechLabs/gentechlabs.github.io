# May 2, 2026 Fleet Health Incident — Reference Case Study

**Auditor**: Gentech Watchdog (cron)
**Scope**: YoYo, DMOB, Desmond, Gentech gateways + master cron service
**Severity**: Fleet-critical (3/4 agents down, cron pipeline blocked)

## Executive Summary

Systemic infrastructure collapse affecting all four agents. Root causes:
1. Master `hermes-gateway.service` failed (ExecStart path misconfigured) → cron dispatch blocked fleet-wide
2. Systemic Python bytecode corruption from disk pressure → EOFError marshal exceptions in YoYo/Gentech
3. Fleet-wide TTS failure (shared invalid ElevenLabs API key)
4. DMOB missing Anthropic credentials
5. Orphaned cron jobs (never executed since Apr 30 creation)

**Status at time of audit**: Only Gentech gateway operational; YoYo, DMOB, Desmond processes crashed.

## Detailed Findings

### 1. Master Service Failure (ROOT CAUSE)

**File**: `/root/.config/systemd/user/hermes-gateway.service`

```
ExecStart=/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
                                          ^^^^^^^^^ WRONG PATH
```

**Correct**: `/usr/local/lib/hermes-agent/venv/bin/python`

**Evidence**:
```bash
$ systemctl --user status hermes-gateway.service
× hermes-gateway.service - Hermes Agent Gateway - Messaging Platform Integration
     Active: failed (Result: exit-code) since Mon 2026-04-27 22:18:36 UTC
     Main PID: 11902 (code=exited, status=203/EXEC)

Apr 27 22:18:05 ...: hermes-gateway.service: Main process exited, code=exited, status=203/EXEC
Apr 27 22:18:36 ...: Start request repeated too quickly. (restart counter 7)
```

**Impact**: All cron job dispatches blocked. Jobs exist in `jobs.json` but never loaded into active scheduler.

**Fix**:
```bash
sudo sed -i 's|/root/.hermes/hermes-agent/venv/bin/python|/usr/local/lib/hermes-agent/venv/bin/python|' /root/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
systemctl --user restart hermes-gateway.service
```

### 2. Bytecode Corruption (YoYo & Gentech)

**Pattern**: `EOFError: marshal data too short` during imports of `agent.copilot_acp_client` and `agent.gemini_native_adapter`.

**Malformed `.pyc` header example**:
- File: `/usr/local/lib/hermes-agent/agent/__pycache__/gemini_native_adapter.cpython-311.pyc`
- Size on disk: 16,384 bytes
- Header claimed source size: ~1.77 GB (impossible)
- Actual source file: ~22 KB

**Count**: 100+ corrupted files in `/usr/local/lib/hermes-agent/agent/__pycache__/`

**Root cause**: Disk pressure (82% usage on `/dev/sda1`, 157G/193G) likely interrupted pyc writes.

**Fix**:
```bash
# Delete all corrupted bytecode
find /usr/local/lib/hermes-agent -name "*.pyc" -delete

# Restart ALL agent gateways to flush in-memory cache
# (Corrupted bytecode remains in memory until process restart)
```

### 3. Fleet-Wide TTS Failure

**Error** (all agents):
```
elevenlabs.core.api_error.ApiError: status_code: 401
body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
```

**Shared key** (found in config): `ff52c5f015c3490da49adf12513a6d55` (likely a CoinMarketCap key misconfiguration)

**Impact**: Text-to-speech completely non-operational across all agents.

**Fix**: Rotate ElevenLabs API key in shared TTS configuration or per-agent environment.

### 4. DMOB Credential Gap

**Missing**: `ANTHROPIC_TOKEN` / `ANTHROPIC_API_KEY` in `/root/.hermes/profiles/dmob/.env`

**Error**:
```
RuntimeError: No Anthropic credentials found
```

**Impact**: Any LLM-dependent cron jobs for DMOB fail (e.g., "Labs Daily Standup", "Defi Milestone").

**Fix**:
```bash
echo "ANTHROPIC_TOKEN=<valid_token>" >> /root/.hermes/profiles/dmob/.env
# or ensure token is imported from shared env
```

### 5. Orphaned Cron Jobs

All four primary agent jobs created on Apr 30 never executed:

| Agent | Job Name | Job ID | `last_run_at` | Expected Schedule |
|-------|----------|--------|---------------|------------------|
| YoYo | LP Watchlist Check | `a47474bb0f0c` | null | 4× daily (08:00,12:00,16:00,20:00) |
| DMOB | Labs Daily Standup | `ec74c26ad123` | null | daily |
| Desmond | Creative Sync | `64cfa447b338` | null | daily |
| Gentech | HQ Daily Update | `c578000c1d4a` | null | daily |

**Why**: Master service failure prevented job registration into active cron registry. Jobs exist in `jobs.json` but never loaded.

**Verification**: Check each agent's `cron.log` — none exist, confirming cron never ran.

### 6. Process Liveness Summary (at audit time)

| Agent | Gateway Running? | PID | Network Active? | Notes |
|-------|-----------------|-----|-----------------|--------|
| YoYo | ❌ No | — | No | Process table showed stale PID 1128490 earlier; actual process not found |
| DMOB | ❌ No | — | No | Crashed; last gateway.log entry: "Stopping gateway..." |
| Desmond | ❌ No | — | No | Last entry: "Exiting with code 1" at 00:55 |
| Gentech | ✅ Yes | 1118093 | Yes | Stable, responding, sending Telegram messages |

**Note**: `pgrep` can return stale/stale PIDs during rapid restart scenarios. Always validate with `ps -p <pid>` and check gateway.log last entry timestamp.

## Timeline of Key Events

- **Apr 27**: `hermes-gateway.service` first fails (ExecStart path error). Restart attempts exhausted.
- **Apr 30**: Agent cron jobs created. Never execute due to master service down.
- **May 01 23:20 UTC**: Coordinated gateway restart attempt (likely system update). All agents stop simultaneously. YoYo/DMOB/Desmond fail to relaunch; Gentech survives.
- **May 02 10:17**: Bytecode corruption timestamps; likely disk pressure event.
- **May 02 13:00–15:00**: TTS errors spike as agents attempt speech generation with invalid key.
- **May 02 15:38**: Audit run — YoYo/DMOB/Desmond gateways still down.

## Recovery Checklist

- [ ] Fix master service ExecStart path and restart service
- [ ] Delete corrupted `.pyc` files fleet-wide
- [ ] Restart YoYo, DMOB, Desmond gateways (Gentech already running)
- [ ] Rotate ElevenLabs API key (all agents)
- [ ] Add ANTHROPIC_TOKEN to DMOB `.env`
- [ ] Verify cron jobs actually execute (check cron.log within 1 hour)
- [ ] Monitor disk usage; free space if >80%
- [ ] Re-run `agent-health-audit` to confirm all green

## Post-Mortem Recommendations

1. **Service resilience**: Enable `Restart=always` in systemd unit for hermes-gateway.service
2. **Credential rotation alerts**: Add monitoring for 401 errors from shared services (TTS, LLM APIs)
3. **Disk pressure guardrail**: Auto-alert at 75% usage; implement log rotation
4. **Health dashboard**: Export agent status metrics to a visible dashboard (not just cron alerts)
5. **Cron delivery confirmation**: Require cron jobs to write heartbeats to a known location; alert if missing

## Diagnostic Command Cheatsheet

See main SKILL.md for standard workflow. Incident-specific commands:

```bash
# Check if cron daemon is actually running (not just systemd unit)
ps aux | grep -E 'hermes.*cron|schedule|scheduler'

# Confirm master service path
systemctl --user cat hermes-gateway.service | grep ExecStart

# Find all .pyc files with suspicious size (possible corruption)
find /usr/local/lib/hermes-agent -name "*.pyc" -exec ls -lh {} \; | awk '$5 ~ /[1-9]\.[0-9]+G/ {print}'

# Cross-check cron job existence vs execution
jq '.jobs[] | select(.name|test("YoYo|DMOB|Desmond|Gentech"))' /root/.hermes/cron/jobs.json
ls -la /root/.hermes/profiles/*/logs/cron.log 2>/dev/null

# Determine if a PID is stale (no associated process)
ps -p <pid> >/dev/null || echo "STALE PID"
```

## Error Signature Reference

| Error | Meaning | Action |
|-------|---------|--------|
| `EOFError: marshal data too short` | Bytecode corruption | Delete `.pyc`, restart gateway |
| `status=203/EXEC` (systemd) | ExecStart path wrong | Fix path, daemon-reload, restart |
| `ApiError: 401` (ElevenLabs) | Invalid API key | Rotate key |
| `No Anthropic credentials found` | Missing token | Add to `.env` |
| `last_run_at: null` (scheduled jobs) | Cron dispatch blocked | Fix master service |
| `Shutdown diagnostic — other hermes processes running` | Another agent still active | Wait for drain or force kill |
| `gateway drain timed out after 60.0s` | Agent not responding to shutdown | Force kill, investigate stuck agent |

---

**Document version**: 2026-05-02
**Audit session**: cron_9ecfada01952_20260502_*
**Next review**: After recovery complete
