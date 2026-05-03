# Session Reference — 2026-05-02 Watchdog Run

**Context**: Scheduled cron health check targeting YoYo, DMOB, Desmond, Gentech. Second check of the day after earlier sessions identified systemic failures.

## Findings Summary

| Agent | Status | Process | Systemd | Notes |
|-------|--------|---------|---------|-------|
| Gentech | ✅ RUNNING | PID 1118093 | active (running) | Only active gateway; recent disconnections (26 in 2h) but still operational |
| YoYo | ❌ DOWN | none | inactive (dead) since 13:39 | Profile dir exists; shut down cleanly; never restarted |
| DMOB | ❌ DOWN | none | inactive (dead) since 15:38 | Clean shutdown at 15:38; no restart |
| Desmond | ❌ DOWN | none | inactive (dead) since 13:37 | Clean shutdown at 13:37; no restart |

## Critical Issues Discovered

### 1. Bytecode Corruption (Persistent)
- **Location**: `/usr/local/lib/hermes-agent/agent/__pycache__/` and `tools/__pycache__/`
- **Files affected**: 100 `.pyc` files with malformed headers
- **Magic number**: `a70d0d0a` (corrupted) vs expected Python 3.11 `33 0d 0d 0a`
- **Examples**: `gemini_schema.cpython-311.pyc`, `moonshot_schema.cpython-311.pyc`, `anthropic_adapter.cpython-311.pyc`
- **Impact**: Previously caused `EOFError: marshal data too short` during imports; files cleaned from disk but in-memory bytecode still corrupted in any running process
- **Status**: Files deleted in earlier session; no new corruption in last 30 min

### 2. Systemd Service State Disagreement
- `hermes-gateway-yoyo.service` — `inactive (dead)` (dead since 13:39)
- `hermes-gateway-dmob.service` — `inactive (dead)` (dead since 15:38)
- `hermes-gateway-desmond.service` — `inactive (dead)` (dead since 13:37)
- `hermes-gateway-gentech.service` — `active (running)`
- **Note**: Only Gentech process actually running (`ps aux` showed single hermes process)

### 3. Clean Shutdowns Without Restart
All three down agents show gateway.log entries:
```
INFO gateway.run: Stopping gateway...
INFO gateway.platforms.telegram: [Telegram] Disconnected from Telegram
INFO gateway.run: ✓ telegram disconnected
INFO gateway.run: Gateway stopped
INFO gateway.run: Cron ticker stopped
```
Followed by no subsequent \"Starting Hermes Gateway\" entries. Agents were terminated (likely via `--replace` or planned shutdown) and never relaunched.

### 4. TTS Credential Failure (Fleet-Wide)
- YoYo errors.log: `elevenlabs.core.api_error.ApiError: status_code: 401` — invalid API key
- DMOB errors.log: same ElevenLabs 401 pattern
- Desmond errors.log: same ElevenLabs 401 pattern
- **Impact**: Text-to-speech completely broken across fleet
- **Note**: Not currently generating new errors (credentials likely revoked/expired)

### 5. DMOB Missing Anthropic Credentials
- Error: `RuntimeError: No Anthropic credentials found`
- Root: No `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY` in `/root/.hermes/profiles/dmob/.env`
- **Impact**: Any job/tool requiring Anthropic LLM fails

### 6. Telegram Connection Noise (Gentech)
- 26 disconnect events in last 2 hours
- All appear to be normal gateway shutdown/restart cycles, not network failures
- Gateway remains connected and processing messages

## Commands That Revealed Issues

```bash
# 1. Active gateway count (only Gentech showed)
ps aux | grep hermes_cli.main | grep gateway

# 2. Systemd service states (authoritative source)
systemctl --user status hermes-gateway-yoyo.service
systemctl --user status hermes-gateway-dmob.service
systemctl --user status hermes-gateway-desmond.service
systemctl --user status hermes-gateway-gentech.service

# 3. PID validation cache trap
pgrep -f 'hermes.*yoyo'   # returned stale PIDs (1129000, etc.)
ps -p 1129000             # PID not found — cache artifact

# 4. Bytecode corruption detection (post-cleanup verification)
find /usr/local/lib/hermes-agent -name "*.pyc" -mmin -30  # no recent changes
xxd -l 4 /usr/local/lib/hermes-agent/agent/__pycache__/gemini_schema.cpython-311.pyc  # shows magic

# 5. Shutdown/restart forensics
tail -30 /root/.hermes/profiles/yoyo/logs/gateway.log
tail -30 /root/.hermes/profiles/dmob/logs/gateway.log

# 6. Error trend check (quiet vs active)
for a in yoyo dmob desmond gentech; do
  echo "=== $a ==="
  tail -5 /root/.hermes/profiles/$a/logs/errors.log
done

# 7. Recent log activity window
find /root/.hermes/profiles -path "*/logs/agent.log" -mmin -10 -exec ls -la {} \;

# 8. Systemd user unit overview
systemctl --user list-units --type=service --all | grep hermes
```

## Recovery Actions Taken

**None** — Watchdog in diagnostic-only mode this session. Findings reported for manual intervention.

## Required Interventions (Priority Order)

1. **Restart missing gateways** (YoYo, DMOB, Desmond):
   ```bash
   systemctl --user start hermes-gateway-yoyo.service
   systemctl --user start hermes-gateway-dmob.service
   systemctl --user start hermes-gateway-desmond.service
   # Or: hermes gateway start --profile <agent>
   ```

2. **Validate bytecode after restart**: Once gateways up, verify no marshal errors appear in errors.log. If they reappear, repeat bytecode deletion and restart all gateways.

3. **Rotate ElevenLabs API key** (affects all agents). Update in shared credential store or each agent's environment.

4. **Set DMOB Anthropic credentials**: Add to `/root/.hermes/profiles/dmob/.env`:
   ```
   ANTHROPIC_TOKEN=sk-ant-...
   ```

5. **Repair master cron service** (if not already fixed): Ensure `hermes-gateway.service` ExecStart path correct and service enabled to guarantee cron dispatch.

## Lessons & Detection Improvements

- Added `ps -p <pid>` validation step to catch stale `pgrep` cache results
- Must check BOTH process table AND systemd unit state — they can diverge
- Clean shutdown logs (`Gateway stopped`, `Cron ticker stopped`) + absence of restart = planned outage, not crash
- Bytecode corruption cleanup must be followed by process restart; disk cleanup alone doesn't fix in-memory bad bytecode
- Profile directory existence check prevents false \"process not found\" confusion

## Related Skills

- `agent-health-audit` — Updated with new pitfalls (stale PID cache, profile directory check, systemd vs ps divergence)