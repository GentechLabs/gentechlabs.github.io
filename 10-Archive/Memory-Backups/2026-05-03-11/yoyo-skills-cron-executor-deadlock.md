# Cron Executor Deadlock — Detection & Recovery

## Failure Mode
The Hermes cron ticker thread starts successfully, but the job dispatcher thread pool becomes blocked, resulting in **zero job executions** across all agents despite gateways running and reporting healthy.

## Detection

### Primary Evidence
```bash
# 1. No new session directories created
find /root/.hermes/sessions -type d -mmin -60  # returns empty

# 2. No "Executing job" entries in gateway logs since restart
grep -r "Executing job" /root/.hermes/profiles/*/logs/gateway.log | grep "2026-05-02 0[3-9]:"  # no matches

# 3. jobs.json shows next_run advanced but last_run stale
hermes cron list  # shows upcoming runs but last_run timestamps not updating

# 4. Gateway logs show ticker started but no subsequent cron activity
grep "Cron ticker started" /root/.hermes/profiles/*/logs/gateway.log  # present
grep "cron.scheduler: Running job" /root/.hermes/profiles/*/logs/gateway.log  # absent after restart
```

### Secondary Indicators
- Recent disk I/O errors or `Errno 28` in agent error logs
- Corrupted Python bytecode (`EOFError: marshal data too short`) in multiple agents
- SQLite database corruption (`database disk image is malformed`)
- Simultaneous gateway restart events across all agents within a 3-minute window
- Error log contamination (process-list lines appearing in errors.log) suggesting file descriptor leaks

## False-Positive Traps
- `hermes cron list` may report `Last run: ... ok` even when no execution occurred — this is a status reporting bug; trust gateway logs and session directories, not jobs.json
- Ticker log message ("Cron ticker started") only confirms thread launch, not ongoing dispatch
- Gateway process running ≠ cron executor functional

## Common Root Causes (Observed)
1. **Disk pressure** (≥80% root usage) → SQLite I/O errors → thread pool deadlock
2. **Bytecode corruption** in shared modules (e.g., `copilot_acp_client.py`) → import exceptions during session creation → executor crash loop suppressed by error handler
3. **Shared session database corruption** → all agents fail session summarization step → cron jobs hang at Phase 3
4. **Prior gateway crash** leaving thread pool in inconsistent state; auto-restart brings process up but executor initialization fails silently

## Recovery Procedure

### Immediate (5 min)
1. Stop all gateways simultaneously:
```bash
systemctl --user stop hermes-gateway-yoyo.service
systemctl --user stop hermes-gateway-dmob.service
systemctl --user stop hermes-gateway-desmond.service
systemctl --user stop hermes-gateway-gentech.service
```

2. Clear corrupted bytecode caches:
```bash
find /usr/local/lib/hermes-agent -name "*.pyc" -delete
find /root/.hermes -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

3. Restart all gateways in order (DMOB/Gentech last):
```bash
systemctl --user start hermes-gateway-yoyo.service
sleep 2
systemctl --user start hermes-gateway-desmond.service
sleep 2
systemctl --user start hermes-gateway-dmob.service
sleep 2
systemctl --user start hermes-gateway-gentech.service
```

4. Verify executor recovery:
```bash
# Within 5 minutes, confirm session directories appear
find /root/.hermes/sessions -type d -mmin -10
# Check gateway logs for "cron.scheduler: Running job"
grep "cron.scheduler: Running job" /root/.hermes/profiles/gentech/logs/gateway.log | tail -5
```

### If Deadlock Persists
- Check for lingering Python processes (`ps aux | grep hermes`) and kill all before restart
- Repair corrupted databases: `sqlite3 /root/.hermes/sessions/sessions.db "PRAGMA integrity_check;"`
- Free disk space: `apt-get clean && journalctl --vacuum-time=1d`
- Re-authenticate all agents: `hermes model` per profile

## Monitoring
Create a Watchdog cron job that fails if no session directories created in last 90 minutes:
```bash
if [ -z "$(find /root/.hermes/sessions -type d -mmin -90)" ]; then
  echo "CRON DEADLOCK DETECTED — no sessions in 90m" | telegram-send
fi
```
