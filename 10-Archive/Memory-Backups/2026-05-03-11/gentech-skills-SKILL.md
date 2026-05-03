---
name: agent-health-audit
description: Systematic health checks across Hermes agent fleets — detect crashes, stuck processes, missed cron executions, and systemic failures
triggers:
  - keywords: ["health check", "agent status", "watchdog", "fleet health", "audit agents", "check yoyo dmob desmond gentech"]
  - intent: "audit"  # when user wants to verify operational status
  - always_required: false
---

# Agent Health Audit

A disciplined, multi-source verification workflow for checking the operational status of Hermes agents. This skill prevents false negatives by cross-referencing process tables, log freshness, cron execution, and resource constraints.

## Trigger Conditions

Load this skill when:
- User asks to "check health" or "audit" any agent/fleet
- Watchdog/cron job needs to verify agent status
- Investigating "why isn't my agent running" or "cron didn't execute"
- Proactive health monitoring required

Do NOT load for: single-agent troubleshooting with a known error (use specific debug skills instead).

## Methodology

### Phase 1 — Process Liveness Verification
**Never trust `pgrep` alone** — stale PIDs can linger in process tables during rapid restarts. Use this hierarchy:

1. `ps aux | grep -E 'hermes.*<agent>|<agent>.*gateway'` — check actual command lines
2. `pgrep -f 'hermes.*<agent>'` — get PIDs
3. **Validate each PID**: `ps -p <pid> -o pid,stat,etime,cmd` — confirm process exists and is not Zombie (Z) or Uninterruptible (D)
4. **Cross-check with log freshness**: Compare gateway.log modification time vs last log entry timestamp. If `now - last_entry > 300s` and process appears running, it's likely a dead process with stale log file handle.

**Red flags**: PID not found in `ps`, state includes `Z` or `D`, log modification age > 5 minutes with no entries.

### Phase 2 — Error Pattern Recognition
Scan logs in this order, marking severity:

**FATAL/IMMEDIATE** (alert):
- `EOFError.*marshal data too short` → bytecode corruption (requires restart + cleanup)
- `status=203/EXEC` in systemd → service path misconfiguration
- `Process not found` when gateway claims running → phantom process
- `sqlite3.DatabaseError: file is not a database` → session DB corruption

**DEGRADED** (investigate):
- `401 Invalid API key` (ElevenLabs) → credential rotation needed
- `No Anthropic credentials found` → missing env vars
- `Bad Gateway`/`Connection refused` → network/telegram issues
- `last_run_at: null` for cron jobs → dispatch pipeline blocked
- `Auxiliary session_search.*connection error on auto` → auto provider endpoint unreachable; auxiliary client falling back to alternative providers (e.g., nous/google). Indicates misconfigured or unreachable default provider in agent config.yaml (`auxiliary.auto.provider`).

**NORMAL** (no alert):
- `INFO gateway.platforms.telegram: [Telegram] Disconnected` — graceful disconnect, expected
- `Cron ticker started` — normal operation
- `INFO gateway.run: Press Ctrl+C to stop` — manual run indicator

**Implementation**: Always check both `gateway.log` (last 100–200 lines) AND `errors.log` (full tail). Use `grep -i` with patterns: `error|exception|crash|fatal|failed|marshal|401|403|404|timeout|connection refused|no such file|database error`.

### Phase 3 — Cron Execution Verification
**Jobs can be "scheduled" but never execute** if the master cron service is down. Do not trust `last_run_at` in storage alone.

1. Check master service: `systemctl --user status hermes-gateway.service`
   - If `Active: failed` with exit code `203/EXEC` → ExecStart path likely wrong
   - If `disabled` → won't auto-restart on failure

2. Verify cron daemon is actually running: `ps aux | grep -E 'hermes.*cron|schedule|scheduler'`
   - Expect a persistent cron/scheduler process. If absent, dispatch is dead.

3. Check each agent's cron.log (if exists): `/root/.hermes/profiles/<agent>/logs/cron.log`
   - If no cron.log exists, cron may not be configured for that agent

4. Correlate: Compare `jobs.json` `last_run_at` vs actual cron.log entries. If `last_run_at` is null but job is `enabled: true` and `state: scheduled`, the dispatch pipeline is broken.

### Phase 4 — Systemic Issue Detection
Look for fleet-wide patterns that affect multiple agents:

- **Shared credential failures**: Same error (e.g., `elevenlabs 401`) across all agents → rotate shared API key
- **Bytecode corruption**: Multiple agents showing `marshal data too short` → run `find /usr/local/lib/hermes-agent -name "*.pyc" -delete`, then restart all gateways
- **Disk pressure**: Check `df -h /` — if >80%, corruption risk high
- **Master service failure**: If `hermes-gateway.service` failed, ALL cron dispatch is blocked regardless of individual agent health.
- **Auto-provider connectivity**: Repeated `connection error on auto` in agent logs → auxiliary client cannot reach configured default provider; check `auxiliary.auto.provider` in agent `config.yaml` and verify endpoint reachability.
- **Cron pipeline blockage**: Jobs present in `jobs.json` but absent from `hermes cron list` output, or `last_run_at` remains null → cron scheduler not loading all jobs; check cron daemon process and service status.

## Advanced Diagnostic Patterns

**Bytecode corruption detection (Python marshal errors)**:
- Corrupted `.pyc` files often have wrong magic numbers. Python 3.11 magic: `33 0d 0d 0a` (hex `\x33\x0d\x0d\x0a`). Common corruption signature: `a70d0d0a`.
- Find all corrupted caches: `find /usr/local/lib/hermes-agent -name "*.pyc" -exec python3 -m py_compile {} \; 2>&1 | grep -i marshal` or check magic directly: `xxd -l 4 <file>` should show `33 0d 0d 0a`.
- Deletion alone is insufficient; running processes hold corrupted bytecode in memory. Must restart ALL gateways after cleanup.

**Credential failure patterns**:
- ElevenLabs TTS: `elevenlabs.core.api_error.ApiError: status_code: 401` with `'Invalid API key'` — rotate immediately across all agents
- Anthropic: `hermes_cli.auth.AuthError: No Anthropic credentials found` — check profile `.env` for `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY`

**Telegram connection health**:
- Normal: `Connected to Telegram (polling mode)` followed by periodic messages
- Degraded: `Telegram network error: Bad Gateway`, `Connection refused`, repeated disconnect/reconnect cycles in short timeframe
- Inactive: No gateway.log entries for >5 minutes while process claims running → stale file handle, process likely dead

**Log staleness detection**:
- Compare gateway.log modification time vs last log entry timestamp within the file. If file modified >5 min ago but latest entry is older, process likely died without log rotation.
- Check agent.log modification age: if >10 min with no entries while systemd shows active, process may be hung (D-state) or zombie.

## Output Discipline

**Silence Rule**: If all agents healthy (processes running, no errors, cron executing), respond exactly: `STATUS:OK` and nothing else.

**Alert Format**: Only when real problems detected. Use one-line summary with critical details, e.g.:

```
🚨 Watchdog Alert: YoYo, DMOB, Desmond gateways down (PIDs not found); master cron service failed since Apr 27 (ExecStart path wrong); fleet TTS broken (invalid ElevenLabs key); DMOB missing ANTHROPIC_TOKEN.
```

**Common Pitfalls**

1. **Stale PID assumptions**: A PID from `pgrep` may belong to a previous crashed instance that hasn't been reaped. Always validate with `ps -p <pid>`.

2. **Log file vs process mismatch**: Log file can be old while a new process writes to a new file (log rotation). Check both modification time and last log entry content for recent timestamps.

3. **Confusing normal disconnects with failures**: Telegram \"Disconnected\" at graceful shutdown is INFO level, not ERROR. Only actual connection failures (`Bad Gateway`, `Connection refused`) matter.

4. **Ignoring systemd state**: An agent may have a manually started gateway that appears running, but the systemd unit is failed. That means no automatic restart on reboot/failure.

5. **Cron storage vs execution**: `jobs.json` / `hermes cron list` shows what *should* run; cron.log shows what *did* run. Always check both.

6. **`pgrep` cache returning stale PIDs**: During rapid restart scenarios, `pgrep -f` can return PIDs that no longer exist (cached from previous process table scans). Always validate each PID with `ps -p <pid>` and discard any that don't resolve to a live process.

7. **Profile directory absence**: An agent may appear \\\"down\\\" because `~/.hermes/profiles/<agent>` was deleted, not because the gateway crashed. When no process is found, always check: `ls /root/.hermes/profiles/<agent>` before attempting restart. Missing profile requires recreation/restoration, not just process launch.

8. **Process-state vs systemd disagreement**: A gateway may appear running in `ps aux` while its systemd unit is `inactive (dead)` or `failed`. This indicates a manually started process outside systemd supervision, meaning no auto-restart on reboot. Always check BOTH `ps` and `systemctl --user status hermes-gateway-<profile>.service`.

9. **Cron list command incompleteness**: `hermes cron list` may omit some scheduled jobs or show stale `last_run_at` values. Cross-check with raw `jobs.json` entries and verify actual execution via cron output files in `/root/.hermes/cron/output/`.

10. **Shared credential propagation gaps**: Shared API keys (e.g., ElevenLabs) must be updated in ALL agent `.env` files, not just one. Validate across all profiles after rotation.

## Recovery Sequence (when problems detected)

1. **Restart crashed gateways** (in dependency order if shared resources):
   ```bash
   pkill -f "hermes.*<agent>.*gateway"
   /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile <agent> gateway run --replace
   ```

2. **Fix master service** (if failed):
   ```bash
   # Edit ExecStart path
   sudo sed -i 's|/root/.hermes/hermes-agent/venv/bin/python|/usr/local/lib/hermes-agent/venv/bin/python|' /root/.config/systemd/user/hermes-gateway.service
   systemctl --user daemon-reload
   systemctl --user restart hermes-gateway.service
   ```

3. **Clear bytecode corruption** (if marshal errors present):
   ```bash
   find /usr/local/lib/hermes-agent -name "*.pyc" -delete
   # Then restart ALL agent gateways to flush in-memory cache
   ```

4. **Rotate credentials** (TTS 401):
   - Update ElevenLabs API key in shared config or per-agent env
   - Add missing ANTHROPIC_TOKEN to DMOB `.env`

5. **Validate recovery**: Re-run this audit skill after each fix to confirm resolution.

## Reference: Key Commands

```bash
# Process verification
ps aux | grep hermes
pgrep -f 'hermes.*<agent>'
ps -p <pid> -o pid,stat,etime,cmd

# Log inspection
tail -200 /root/.hermes/profiles/<agent>/logs/gateway.log
tail -100 /root/.hermes/profiles/<agent>/logs/errors.log

# Service status
systemctl --user status hermes-gateway.service

# Cron job inspection
hermes cron list  # (or read jobs.json if CLI fails)
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | select(.name|test("YoYo|DMOB|Desmond|Gentech"))'

# Bytecode cleanup
find /usr/local/lib/hermes-agent -name "*.pyc" -delete

# Gateway restart
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile <agent> gateway run --replace

# Profile directory verification
ls -la /root/.hermes/profiles/<agent>  # confirm existence before restart

# Bytecode corruption scan (find all marshal errors)
find /usr/local/lib/hermes-agent -name "*.pyc" -exec python3 -m py_compile {} \; 2>&1 | grep -i marshal

# Check specific .pyc magic number (Python 3.11 should be 33 0d 0d 0a)
xxd -l 4 /usr/local/lib/hermes-agent/agent/__pycache__/some_file.cpython-311.pyc

# Systemd user services overview
systemctl --user list-units --type=service --all | grep hermes

# Validate a specific PID exists
ps -p <pid> -o pid,stat,etime,cmd 2>/dev/null || echo "PID not found"

# Count recent disconnects in gateway.log (last 2h)
grep -i disconnect /root/.hermes/profiles/<agent>/logs/gateway.log | tail -10
```

## Support Files

### Reference Case Studies
- `references/2026-05-02-watchdog-3-down.md` — May 2, 2026 run: 3/4 gateways down, systemd state divergence, bytecode corruption persistence, stale PID cache trap, recovery checklist
- `references/2026-05-02-fleet-collapse.md` — Full incident writeup: master service failure, bytecode corruption, credential rot, recovery steps

### Automation Scripts
- `scripts/verify_fleet_health.py` — Automated PASS/FAIL health checker; suitable for cron execution every 5 minutes; exit codes: 0=OK, 1=degraded, 2=critical

## Related Skills

- `agent-coordination` — For multi-agent orchestration beyond health checks
- `system-health` — System-level diagnostics (disk, memory, services)
