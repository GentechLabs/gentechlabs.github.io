# Bytecode Corruption & Session Database Recovery

## Symptom Pattern

`EOFError: marshal data too short` errors in agent logs, particularly during session search or Watchdog cron runs:

```
2026-05-02 00:35:59,106 WARNING [...] root: Session summarization failed after 3 attempts: marshal data too short
Traceback (most recent call last):
  File "/usr/local/lib/hermes-agent/tools/session_search_tool.py", line 226, in _summarize_session
    exec(compile(session_bytes, ...))
EOFError: marshal data too short
```

**Key indicators**:
- Affects YoYo and Gentech primarily (session-heavy agents)
- Triggers during `session_search_tool` or any tool that loads session state
- Error message exact: `marshal data too short`
- Often appears after unclean gateway shutdown or disk pressure event

## Root Cause Chain

1. **Trigger**: Gateway killed during session write (SIGKILL, power loss, disk full)
2. **Corruption**: Python `.pyc` bytecode cache in `/usr/local/lib/hermes-agent/agent/__pycache__/` truncated (common: `*.cpython-311.pyc` size 0 or suspiciously small like 448 bytes instead of 30K+)
3. **Propagation**: Import of corrupted module fails, causing `EOFError`; session DB write may be interrupted, causing SQLite corruption
4. **Manifest**: 
   - SessionSearchTool failures (Watchdog cron job broken)
   - Agent log flooded with repeated EOFError stack traces
   - Gateway may exit with code 1 if error unhandled

## Diagnostic Sequence

```bash
# Step 1: Count EOFError occurrences per agent
for agent in yoyo dmob desmond gentech; do
  count=$(grep -c "marshal data too short" /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null || echo 0)
  echo "$agent: $count corruption errors"
done

# Step 2: Inspect .pyc file sizes in agent module cache
find /usr/local/lib/hermes-agent/agent/__pycache__ -name "*.pyc" -exec ls -lh {} \; | sort -k5 -h

# Step 3: Identify anomalous files (size < 1KB is suspicious)
find /usr/local/lib/hermes-agent/agent/__pycache__ -name "*.pyc" -size -1k -print

# Step 4: Cross-reference error timestamp with .pyc modification time
stat /usr/local/lib/hermes-agent/agent/__pycache__/gemini_native_adapter.cpython-311.pyc

# Step 5: Check session DB integrity (if SQLite used)
sqlite3 /root/.hermes/profiles/yoyo/home/sessions.db "PRAGMA integrity_check;"
```

## Recovery Procedure

**Phase 1 — Stop all gateways (prevent concurrent writes):**

```bash
# Graceful stop
for agent in yoyo dmob desmond gentech; do
  hermes gateway stop --profile $agent 2>/dev/null || true
done

# Force kill if needed
pkill -f "hermes.*gateway run"
sleep 2
```

**Phase 2 — Purge corrupted bytecode cache:**

```bash
# Remove ALL .pyc files — they will regenerate on next import
rm -f /usr/local/lib/hermes-agent/agent/__pycache__/*.pyc

# Verify removal
ls /usr/local/lib/hermes-agent/agent/__pycache__/*.pyc 2>/dev/null | wc -l  # should be 0
```

**Phase 3 — Session database reset (if integrity check fails):**

```bash
# Backup first
for agent in yoyo dmob desmond gentech; do
  db="/root/.hermes/profiles/$agent/home/sessions.db"
  if [ -f "$db" ]; then
    cp "$db" "$db.bak-$(date +%s)"
  fi
done

# If PRAGMA integrity_check returns "malformed" or non-ok:
#   Option A: Clear session state (losss of recent conversation history)
sqlite3 /root/.hermes/profiles/yoyo/home/sessions.db "DELETE FROM sessions;"

#   Option B: Restore from recent backup
cp /root/vaults/gentech/backups/sessions-yoyo-20260501.db /root/.hermes/profiles/yoyo/home/sessions.db
```

**Phase 4 — Restart gateways and verify:**

```bash
for agent in yoyo dmob desmond gentech; do
  hermes gateway run --replace --profile $agent &
done

# Wait 60s then check for new errors
sleep 60
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent recent errors ==="
  tail -30 /root/.hermes/profiles/$agent/logs/errors.log | grep -i "error\\|marshal" || echo "clean"
done
```

## Prevention

- **Never kill -9 gateway**: Use `hermes gateway stop` or `systemctl stop hermes-gateway` for graceful shutdown; allows session flush.
- **Disk space buffer**: Keep root partition < 75% full to avoid I/O truncation during writes.
- **Regular .pyc regeneration**: Add cron job to clear `__pycache__` weekly during low-usage window (safe; Python recreates on demand).
- **Session DB backups**: Daily snapshots to `/root/.hermes/backups/sessions/` with retention of 7 days.

## Related Watchdog Patterns

- **Cron executor deadlock** co-occurs with bytecode corruption: cron ticker starts but executor thread aborts during session load.
- **Cron database corruption** may appear simultaneously if disk pressure affected multiple write paths.
- **TTS failures (401)** are independent but compound alert noise; fix separately after bytecode recovery.

## Verification Checklist

- [ ] No `marshal data too short` in last 100 log lines per agent
- [ ] `.pyc` directory contains files > 10KB (normal range 20K–80K)
- [ ] Session DB `PRAGMA integrity_check` returns `ok`
- [ ] Cron executor runs visible in `agent.log` (`executing job` lines)
- [ ] Gateway uptime > 10 minutes without restart