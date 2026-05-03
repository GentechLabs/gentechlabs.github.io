# Systemic Correlation Detection — Watchdog Session 2026-05-02

**Discovered:** May 2, 2026 during cluster-wide health check of YoYo, DMOB, Desmond, Gentech.

**Why this matters:** Single-agent diagnostics miss fleet-wide cascades. When multiple agents fail in the same way simultaneously, the root cause is almost always shared (credentials, disk I/O, orchestrator signal, update deployment) rather than isolated agent bugs.

---

## Pattern 1: Cron Executor Deadlock

**Signature:** `Cron ticker started` appears in logs, but `dispatching cron job` / `Job ... scheduled` never appears (or appears >4h stale).

**Root causes:**
- Executor thread blocked on un-awaited I/O or lock
- `jobs.json` schema corruption (missing `profile`, `script`, or `task_id` fields makes jobs unrunnable)
- Python event loop stall from unhandled exception in tick handler
- Scheduler thread crashed but ticker thread kept running (partial subsystem failure)

**Detection recipe:**
```bash
# 1. Confirm ticker alive
grep -h "Cron ticker started" /root/.hermes/profiles/*/logs/gateway.log | tail -4

# 2. Check for actual dispatches
grep -h "dispatching cron job\|Job.*scheduled" /root/.hermes/profiles/*/logs/gateway.log | tail -10

# 3. Cross-check jobs.json schema validity
python3 -c "
import json, re
for agent in yoyo dmob desmond gentech; do
  j = json.load(open(f'/root/.hermes/profiles/{agent}/cron/jobs.json'))
  bad = [x for x in j.get('jobs',[]) if not all(k in x for k in ['profile','script','task_id'])]
  if bad: print(f'{agent}: {len(bad)} corrupt jobs')
done
"
```

**Recovery:**
```bash
# Restart every gateway to break the deadlock
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway restart
done

# Verify ticker AND dispatches resuming
grep -h "Cron ticker started\|dispatching cron job" /root/.hermes/profiles/*/logs/gateway.log | tail -20
```

If corrupt `jobs.json` found:
```bash
# Backup and rebuild
cp /root/.hermes/profiles/<agent>/cron/jobs.json ~/jobs.json.bak
# Recreate missing jobs via hermes cron add or restore from known-good backup
```

---

## Pattern 2: Fleet-Wide Credential Cascade

**Signature:** All (or majority) of agents log the identical auth error within 1 hour.

### TTS Provider (ElevenLabs) 401 Outage

**Error pattern:**
```
elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
```

**Affected:** All 4 agents (YoYo, DMOB, Desmond, Gentech) on May 2, 2026.

**Cause:** Shared `ELEVENLABS_API_KEY` either:
- Expired (subscriptal lapsed)
- Rotated manually elsewhere
- Reached usage quota (character limit)
- IP/geo restrictions applied by provider

**Remediation:**
```bash
# 1. Rotate key in all agent environments
export ELEVENLABS_API_KEY="new_key_here"
# Update ~/.hermes/profiles/*/.env or systemd Environment= lines

# 2. Immediate workaround — disable TTS cluster-wide
for agent in yoyo dmob desmond gentech; do
  yq eval '.tools.tts.enabled = false' -i /root/.hermes/profiles/$agent/config.yaml
done

# 3. Restart gateways
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway restart
done
```

### Anthropic API Missing

**Error pattern:**
```
RuntimeError: No Anthropic credentials found. Set ANTHROPIC_API_KEY or switch provider with `hermes model`.
```

**Cause:** `ANTHROPIC_API_KEY` unset in agent environment, or profile-specific `.env` not sourced by gateway process.

**Detect fleet-wide:**
```bash
for agent in yoyo dmob desmond gentech; do
  grep -q "ANTHROPIC_API_KEY" /root/.hermes/profiles/$agent/.env 2>/dev/null && echo "$agent: KEY PRESENT" || echo "$agent: MISSING"
done
```

**Fix:** Populate `.env` in each profile directory; restart gateways.

### OpenCode-Go Missing API Key

**Error pattern:**
```
RuntimeError: Provider 'opencode-go' is set in config.yaml but no API key was found. Set the OPENCODE_GO_API_KEY environment variable, or switch to a different provider with `hermes model`.
```

**Cause:** `OPENCODE_GO_API_KEY` unset. May appear isolated (only in agent using that provider) but can cascade if all agents configured identically.

---

## Pattern 3: Coordinated Restart Waves

**Signature:** All gateways log `Exiting with code 1` and `Cron ticker started` within a 30-second window.

**Interpretation:**
| Timing pattern | Likely cause |
|---|---|
| Exits cluster ±5s, starts spread over ±2 min | `hermes update` or `git pull` + pip install triggered mass restart |
| All exit simultaneously with no subsequent start | External orchestrator (MCP client / CI pipeline) killed them |
| Exits spread over minutes with no clear pattern | Independent resource exhaustion (OOM, disk full) |

**Detect:**
```python
import re, json
from datetime import datetime, timedelta

logs = {}
for agent in agents:
    log = open(f'/root/.hermes/profiles/{agent}/logs/gateway.log').read()
    exits = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Exiting with code 1', log)
    starts = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Cron ticker started', log)
    logs[agent] = {
        'exits': [datetime.strptime(e, '%Y-%m-%d %H:%M:%S') for e in exits],
        'starts': [datetime.strptime(s, '%Y-%m-%d %H:%M:%S') for s in starts]
    }

# Compare last exit across all agents
last_exits = [v['exits'][-1] for v in logs.values() if v['exits']]
if max(last_exits) - min(last_exits) < timedelta(seconds=30):
    print('Coordinated exit wave — investigate orchestrator logs (/var/log/syslog, journalctl for "hermes update")')
```

**Correlated evidence to check:**
- `/root/.hermes/update.log` or similar update logs
- Cron job that runs `hermes update` (likely Gentech — HQ Daily Update)
- Recent Git commit timestamps matching restart window

---

## Pattern 4: Shared Storage/Corruption Cascade

**Signature:** Multiple agents report `disk I/O error`, `No space left on device`, or `database disk image is malformed` within the same hour.

**Root cause:** Disk pressure from one agent's log growth saturates inodes or fills partition, causing cascading failures across all agents sharing the same root filesystem.

**Detect:**
```bash
# 1. Check disk health system-wide
df -h /
df -i /

# 2. Correlate I/O errors across agent logs
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep -i "disk I/O error\|no space left\|malformed" /root/.hermes/profiles/$agent/logs/*.log 2>/dev/null | tail -5
done

# 3. Check largest log files (likely culprit)
du -sh /root/.hermes/profiles/*/logs/*.log | sort -rh | head -10
```

**Recovery sequence:**
```bash
# A. Stop all gateways to freeze state
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway stop
done

# B. Reclaim space — rotate/compress logs, clear caches
find /root/.hermes/profiles -name "*.log" -size +50M -exec gzip {} \;
find /root/.hermes/profiles -name "*.pyc" -delete
rm -rf /root/.hermes/profiles/*/cache/*

# C. Repair corrupted DBs (kanban, sessions)
sqlite3 /root/.hermes/profiles/desmond/kanban.db "PRAGMA quick_check;"
sqlite3 /root/.hermes/profiles/gentech/sessions/sessions.db "PRAGMA integrity_check;"
# If corrupt, move aside and let gateway recreate
mv /root/.hermes/profiles/desmond/kanban.db /root/.hermes/profiles/desmond/kanban.db.corrupt
mv /root/.hermes/profiles/gentech/sessions/sessions.db{,.corrupt}

# D. Restart gateways sequentially
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway start
done
```

**Prevention:** Implement log rotation: `logrotate` config for `/root/.hermes/profiles/*/logs/*.log` with `size 50M` and `rotate 5`.

---

## Pattern 5: Telegram Network Instability Cluster

**Signature:** Multiple agents log `Bad Gateway` or `httpx.ReadError` within a few minutes, indicating upstream Telegram API disruption (not per-agent network issues).

**Detect:**
```bash
# Count network errors per agent in last hour
for agent in yoyo dmob desmond gentech; do
  count=$(grep -c "Telegram network error\|Bad Gateway\|httpx.ReadError" /root/.hermes/profiles/$agent/logs/gateway.log)
  echo "$agent: $count network errors"
done

# Check for simultaneous occurrences
grep -h "Telegram network error" /root/.hermes/profiles/*/logs/gateway.log | cut -c1-19 | sort | uniq -c | sort -rn
```

**Mitigation:** Agents auto-reconnect with exponential backoff; if errors persist >30 min across fleet, check:
- VPC/egress firewall rules (if in cloud)
- Telegram status page (https://telegram.org/)
- MTProto seed IPs (sometimes change; restart clears cache)

---

## Pattern 6: Profile Migration/Deletion Side Effects

**Signature:** Gateway process runs but never writes to its own logs; `ps aux` shows Python process but stale timestamp on `gateway.log`.

**Cause:** Profile directory was moved/deleted after gateway process was started. Gateway continues running in memory but cannot read/write config, spawn tools, or persist sessions; effectively a zombie.

**Detect:**
```bash
for agent in yoyo dmob desmond gentech; do
  pid=$(pgrep -f "hermes.*$agent" | head -1)
  if [ -n "$pid" ]; then
    log_age=$(stat -c %Y /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null || echo 0)
    now=$(date +%s)
    if [ $((now - log_age)) -gt 600 ]; then
      echo "$agent: process alive but gateway.log >10m stale — probable orphaned gateway"
    fi
  else
    echo "$agent: no gateway process running"
  fi
done

# Verify profile directory actually exists
ls -ld /root/.hermes/profiles/{yoyo,dmob,desmond,gentech}
```

**Fix:** Either restore profile directory from backup/version control, or cleanly stop the orphaned process and restart fresh:
```bash
# If profile directory truly deleted, kill orphan gateway and let systemd respawn with fresh profile
kill <PID>
# Ensure systemd unit exists and is enabled
hermes -p $agent gateway start
```

---

## Pattern 7: Configuration Fallback Storms

**Signature:** Repeated warnings like:
```
Failed to process config.yaml — falling back to .env / gateway.json values.
```

**Cause:** Syntax error in config.yaml (commonly incorrect YAML indentation, missing quotes, tab characters). Gateway falls back to stale default values, causing functionality degradation.

**Detect precisely:**
```bash
# Extract unique config parse errors from recent gateway logs
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep "Failed to process config.yaml" /root/.hermes/profiles/$agent/logs/gateway.log | tail -5
done

# Pinpoint the YAML error with line number
python3 -c "
import yaml, sys
agent = 'yoyo'  # change per agent
try:
    yaml.safe_load(open(f'/root/.hermes/profiles/{agent}/config.yaml'))
except yaml.YAMLError as e:
    print(f'{agent}: {e}')
    if e.context_mark:
        print(f'  Line {e.context_mark.line+1}, col {e.context_mark.column+1}')
"
```

**Common errors:**
- `mapping values are not allowed here` — stray colon after indented value; usually missing space after colon on previous line or tab character
- `could not find expected ':'` — forgot colon after key
- `unexpected end of stream` — file truncated

**Fix:** Run `yamllint`, correct line, gate restart:
```bash
yamllint /root/.hermes/profiles/yoyo/config.yaml
hermes -p yoyo gateway restart
```

---

## Pattern 8: Bytecode Cache Corruption

**Signature:** `EOFError: marshal data too short` or `ImportError: cannot import name` from files under `/usr/local/lib/hermes-agent/agent/__pycache__/`.

**Root cause:** Disk I/O error, power loss, or out-of-space during `.pyc` write truncates bytecode cache. Python interpreter later fails to unmarshal.

**Detect fleet-wide:**
```bash
# Count potentially corrupted .pyc files in agent installation (excluding site-packages)
find /usr/local/lib/hermes-agent -name '*.pyc' -not -path '*/site-packages/*' -exec sh -c '
  for f; do
    size=$(stat -c%s "$f")
    src="${f%.pyc}.py"
    if [ -f "$src" ]; then
      src_size=$(stat -c%s "$src")
      # heuristically: if .pyc < 1KB it's suspiciously small
      [ $size -lt 1024 ] && echo "SMALL: $f ($size bytes < $src_size source)"
    fi
  done
' sh {} + | head -20

# Or try loading each .pyc via marshal (slow)
python3 -c "
import marshal, sys, glob
corrupt = []
for f in glob.glob('/usr/local/lib/hermes-agent/agent/__pycache__/*.pyc', recursive=False):
    try:
        with open(f,'rb') as fh:
            data = fh.read()
        marshal.loads(data[16:])  # skip 16-byte header
    except Exception as e:
        corrupt.append((f, str(e)))
if corrupt:
    for path, err in corrupt[:10]:
        print(f'CORRUPT: {path} — {err}')
"
```

**Recovery (full fleet wipe):**
```bash
# Stop all gateways first
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway stop
done

# Purge all __pycache__ directories under hermes-agent
find /usr/local/lib/hermes-agent -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null

# Restart gateways (fresh .pyc generation on first import)
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway start
done

# Warm-up: make one API call per agent to trigger first import
hermes -p yoyo ask "ping"
```

---

## Pattern 9: Error Recency Misclassification

**Signature:** `errors.log` contains many ERROR lines but agent is actually responding to messages (recent INFO lines in gateway.log).

**Cause:** Gateway processes do not truncate error logs on restart; errors from previous process lifetime accumulate. Blindly counting errors overstates severity.

**Detect:**
```python
import re
from datetime import datetime, timedelta

def last_timestamp(lines, needle):
    for line in reversed(lines):
        if needle in line:
            m = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if m:
                return datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
    return None

for agent in agents:
    log = open(f'/root/.hermes/profiles/{agent}/logs/gateway.log').readlines()
    err_log = open(f'/root/.hermes/profiles/{agent}/logs/errors.log').readlines()
    last_info = last_timestamp(log, 'INFO')
    last_error = last_timestamp(err_log, 'ERROR')

    if last_error and last_info:
        gap = (last_info - last_error).total_seconds() / 60
        if gap > 60:
            print(f'{agent.upper(): Last error {gap:.0f}min old — errors are STALE, agent is currently active')
        else:
            print(f'{agent.upper(): Recent error (within 1min) — likely ACTIVE issue')
```

**Interpretation:** Old error + recent INFO = agent has recovered; new error + recent INFO = ongoing problem.

---

## Pattern 10: Database Corruption Fingerprints

**Signature:** `sqlite3.OperationalError: database disk image is malformed` or `database schema` mismatches.

**Causes:**
- Abrupt power loss during DB write (common with disk pressure)
- Sharing SQLite file across processes without WAL mode
- Disk reaching 100% during checkpoint

**Detect via SQLite PRAGMA (when sqlite3 CLI available):**
```bash
sqlite3 /root/.hermes/profiles/desmond/kanban.db "PRAGMA integrity_check;"
# Expected output: ok
```

**Detect via Python:**
```python
import sqlite3
try:
    conn = sqlite3.connect('file:/path/to/db?mode=ro', uri=True)
    conn.execute('PRAGMA integrity_check')
    print('DB OK')
except sqlite3.DatabaseError as e:
    print(f'DB CORRUPT: {e}')
```

**Repair path:**
1. Stop gateway (`hermes -p <agent> gateway stop`)
2. Run `sqlite3 <db> ".backup /tmp/repaired.db"` (may succeed even if corrupt)
3. If backup fails, move corrupt DB aside and let gateway recreate fresh DB
4. Restart gateway; verify kanban tasks re-appear (if using persistent kanban, restore from last backup)

---

## Pattern 11: Silent Profile Directory Loss

**Signature:** `ps aux` shows gateway process, gateway.log last write >30 min ago, `ls ~/.hermes/profiles/<agent>` fails (directory removed).

**Cause:** Cleanup script (cron, manual admin action) deleted profile directory while gateway was still running. Gateway becomes zombie — process alive but functionally dead.

**Detect:**
```bash
for agent in yoyo dmob desmond gentech; do
  if ! [ -d /root/.hermes/profiles/$agent ]; then
    echo "PROFILE MISSING: $agent"
    # Check if process still running
    pgrep -f "hermes.*$agent" && echo "  → zombie process detected"
  fi
done
```

**Fix:** Restore profile from version control/backup OR kill zombie and `hermes init --profile <agent>` then re-provision credentials.

---

## Pattern 12: Missing task_id Contract Violations

**Signature:** `jobs.json` entries lack `task_id` field, breaking kanban integration. Cron jobs with missing `task_id` fail silently, never appearing in Desmond's kanban board.

**Detect:**
```bash
python3 -c "
import json
for agent in yoyo dmob desmond gentech:
    with open(f'/root/.hermes/profiles/{agent}/cron/jobs.json') as f:
        data = json.load(f)
    bad = [j for j in data.get('jobs',[]) if 'task_id' not in j]
    if bad:
        print(f'{agent}: {len(bad)}/{len(data.get(\"jobs\",[]))} jobs missing task_id')
"
```

**Fix:** Recreate jobs via `hermes cron add` ensuring `--task-id` provided; or script migration to inject missing IDs based on agent+name hashing.

---

## Pattern 13: Python Import Chain Breakage from Partial Updates

**Signature:** Different agents show different error patterns after update — some work, some fail with `ImportError: cannot import name 'X' from 'hermes.agent'`.

**Cause:** Update process overwrote core hermes-agent installation but did not purge old `.pyc` caches everywhere. Bytecode from previous version mismatches new source signatures.

**Detect:**
```bash
# Check mismatch between .py and .pyc timestamps
find /usr/local/lib/hermes-agent -name '*.pyc' -exec sh -c '
  pyc="$1"; py="${pyc%.pyc}.py";
  [ -f "$py" ] || continue;
  pyc_mtime=$(stat -c%Y "$pyc"); py_mtime=$(stat -c%Y "$py");
  if [ "$pyc_mtime" -lt "$py_mtime" ]; then
    echo "STALE BYTECODE: $pyc older than $py"
  fi
' sh {} \;
```

**Fix:** Full bytecode purge (see Pattern 8 above) on all agents before restart.

---

## Decision Tree for Watchdog Response

```
Start: Multiple agents unhealthy?
  |
  ├─ Step 1: Check cron subsystem
  │   ├─ Is ticker running everywhere? → If NO → check gateway.liveness first
  │   ├─ Are jobs actually dispatching? → If NO → deadlock → restart ALL gateways
  │   └─ Any last_run_at advancing? → If stagnant → inspect jobs.json schema & executor thread stack
  |
  ├─ Step 2: Look for matching error patterns across >50% of agents
  │   ├─ Same HTTP status (401, 429, 502) in last hour? → fleet credential/provider issue
  │   ├─ Same exception type (EOFError, OperationalError)? → shared storage/corruption
  │   └─ Coordinated exit timestamps (±1min)? → orchestrator signal or update-triggered
  |
  ├─ Step 3: Check disk & DB health
  │   ├─ `df -h` shows <10% free? → reclaim space (logrotate, cache clear)
  │   ├─ `PRAGMA integrity_check` on kanban DBs → malformed? → delete/restore
  │   └─ Recent I/O errors in system logs? → fsck or underlying storage issue
  |
  ├─ Step 4: Check credential vault
  │   ├─ ELEVENLABS_API_KEY present in all .env files? → rotate if expiry suspected
  │   ├─ ANTHROPIC_API_KEY set? → restore from vault
  │   └─ OpenCode/OpenAI keys present? → update from environment
  |
  └─ Step 5: Restart & verify
       ├─ Stop ALL agents cleanly
       ├─ Purge bytecode caches (find __pycache__ -delete)
       ├─ Repair/restore corrupt DBs
       ├─ Start all agents
       └─ Validate: ticker started + one dispatch confirmed
```

---

## Session Evidence Log (May 2, 2026)

### Observed simultaneous failures

| Agent | TTS Errors (last hour) | Cron executor | Gateway restarts (past 4h) | Telegram disconnects |
|---|---|---|---|---|
| YoYo | 8× 401 | Deadlocked (ticker but 0 jobs) | 1 (SIGTERM at 13:38) | 0 |
| DMOB | 6× 401 | Deadlocked | 2 (SIGTERM at 15:38, auto respawn) | 1x "Bad Gateway" at 01:10 |
| Desmond | 5× 401 | Deadlocked | 1 (SIGTERM at 15:38, replaced) | 0 |
| Gentech | 5× 401 | Deadlocked | 1 (timeout at 15:39, auto-respawn) | 1x "Chat not found" + `httpx.ReadError` at 09:04/11:34 |

**Telemetry:** All gateways connected to Telegram, responding to user messages within 5–13 minutes last known activity. Ticker threads started at 20:17 but no job dispatches recorded since 15:38 (2+ hours prior).

**Conclusion:** Fleet is in degraded state — TTS completely non-functional, cron subsystem globally deadlocked, config syntax errors present. Recommend staged intervention: credential rotation → bytecode purge → gateway restart → cron verification.
