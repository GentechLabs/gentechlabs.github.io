---
name: gentech-agent-health-diagnosis
description: Systematic diagnostic workflow to determine why Hermes agent gateways are down — distinguishes between stale locks, auth failures, revoked tokens, and config issues before attempting recovery
tags:
  - debugging
  - troubleshooting
  - agent-monitoring
  - health-check
related_skills:
  - devops/gentech-agent-reactivation
trigger: "agent gateway down investigation OR routine health check OR simultaneous multi-agent crash analysis"
---

# Diagnose Hermes Agent Gateway Health Issues

**Purpose:** Determine the root cause of dead/failing agent gateways before attempting recovery. Saves time by identifying the actual problem (stale locks, auth revocation, InvalidToken, config errors) vs. guessing.

**When to use:**
- `ps aux` shows no `hermes gateway run` processes
- Telegram agents not responding
- Watchdog cron reports failures
- Gateways crash immediately on startup
- `errors.log` contains Python bytecode errors or process-list corruption
- Provider authentication failures (Nous, Anthropic, ElevenLabs) block agent operation
- You need to know *why* agents are down before fixing

---

## Diagnostic Workflow

### Phase 1 — Quick Process Check

```bash
# Check for any running gateway processes
ps aux | grep -E '(hermes|gateway)' | grep -v grep

# Check for Hermes agent main process (the CLI itself)
ps aux | grep hermes-agent | grep -v grep
```

**Expected output when healthy:**
```
root  <PID>  ...  /root/.hermes/hermes-agent/venv/bin/python3 /root/.local/bin/hermes gateway run
```

**If nothing:** Gateways are completely down → proceed to Phase 2.

#### Distinguishing Active vs Idle vs Stuck

When gateways are running but you suspect they may be stuck (no responses, cron jobs not firing), verify actual activity:

```bash
# Check if gateway.log is still being written to
log="/root/.hermes/profiles/<agent>/logs/gateway.log"
if [ -f "$log" ]; then
  before=$(wc -c <"$log")
  sleep 5
  after=$(wc -c <"$log")
  if [ "$after" -gt "$before" ]; then
    echo "✓ Log is growing — agent is active"
  else
    echo "⚠️ Log stagnant — agent may be idle or executor blocked"
  fi
fi

# Cross-check kanban DB modification time (dispatcher activity)
kanban="/root/.hermes/profiles/<agent>/kanban.db"
if [ -f "$kanban" ]; then
  db_age=$(( $(date +%s) - $(stat -c %Y "$kanban") ))
  if [ "$db_age" -lt 120 ]; then
    echo "✓ kanban.db modified recently (${db_age}s ago) — dispatcher active"
  else
    echo "⚠️ kanban.db stale (${db_age}s old) — dispatcher may be blocked"
  fi
fi
```

**Interpretation:**
- Logs growing normally → agent active, not stuck.
- Logs stagnant **and** kanban.db stale → executor thread likely blocked (common causes: SQLite lock, disk I/O error, bytecode corruption). Proceed to Phase 7 (Cron Subsystem Stall) and check for kanban notifier I/O errors.
- Logs stagnant **but** kanban.db fresh → agent idle (no jobs queued). Normal.

---

### Phase 1.5 — Transcript-Only Search Pitfall (Critical)

**⚠️ WARNING:** `session_search` queries against conversation transcripts are **not reliable** for real-time health detection. Agents can be critically degraded while still generating no transcript sessions (errors live only in `errors.log` and `gateway.log`).

**False-negative scenario observed (May 2, 2026):**
- Early health checks queried transcripts with `"yoyo errors crashes"` etc.
- Transcript search returned **zero results** → premature `STATUS:OK` output
- Direct log analysis minutes later revealed: authentication failures, cron job blocks, gateway crashes, and bytecode corruption

**Correct workflow:**
1. **Always** inspect raw log files regardless of transcript search results
2. Use `ps aux` to verify process liveness (not just gateway.pid)
3. Check `errors.log` last 50 lines for active error patterns
4. Check `gateway.log` for recent lifecycle events (stopped/started/cron ticker)
5. Only use transcript search for **historical pattern identification**, not current health

**Never** rely solely on `session_search` for operational monitoring. Persisted logs are the source of truth.

---

### Phase 2 — Lock File Forensics

Lock files persist after process death and block restarts.

```bash
# Check gateway.pid (main single-process lock)
cat /root/.hermes/gateway.pid 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "No main gateway.pid"

# Check per-profile gateway.pid files
for agent in yoyo dmob desmond; do
  pid_file="/root/.hermes/profiles/$agent/gateway.pid"
  if [ -f "$pid_file" ]; then
    echo "$agent: $(cat $pid_file)"
    pid=$(cat $pid_file | python3 -c "import sys,json; print(json.load(sys.stdin)['pid'])")
    if ! ps -p $pid > /dev/null 2>&1; then
      echo "  ⚠️ PID $pid is DEAD (stale lock)"
    else
      echo "  ✅ PID $pid is running"
    fi
  else
    echo "$agent: no gateway.pid"
  fi
done

# Check Telegram platform scoped locks (critical!)
ls -la /root/.local/state/hermes/gateway-locks/
```

**Stale lock signs:**
- `gateway.pid` references a PID that `ps -p` can't find
- Lock files exist but no corresponding processes
- `gateway_state.json` says `"gateway_state": "running"` but process not in `ps aux`

**If stale locks found → clear them:**
```bash
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock
```

**Then attempt restart** and check if they stay up. If they crash again → Phase 3.

---

### Phase 3 — Log Analysis (Critical — gateway.out vs agent.log)

**⚠️ gateway.out is often stale** — it retains old error banners from previous runs because log file isn't truncated on restart. **Use agent.log as source of truth.**

```bash
# Check main agent.log for recent activity (last 5 minutes)
tail -50 /root/.hermes/logs/agent.log | grep -E '(ERROR|WARNING|error|exception|fail|invalid)' | tail -20

# Also check timestamp of last entry
tail -1 /root/.hermes/logs/agent.log
```

**Then check each profile's gateway.out ONLY for startup errors:**
```bash
for agent in yoyo dmob desmond; do
  echo "=== $agent gateway.out (last 30 lines) ==="
  tail -30 /root/.hermes/profiles/$agent/logs/gateway.out 2>/dev/null || echo "(no log file)"
  echo
done
```

**Error pattern recognition:**

| Error Message (from gateway.out) | Likely Cause | Next Step |
|---------------------------------|-------------|-----------|
| `PID file race lost to another gateway instance` | Concurrent startup conflict | Check for zombie gateways, clear PIDs/locks, restart sequentially |
| `Telegram bot token already in use (PID XXXX)` | Stale Telegram lock | Verify PID exists; if dead → clear locks (Phase 2) |
| `The token \\`<number>:***\\` was rejected by the server` / `InvalidToken` | **Revoked/expired bot token** | → Phase 4 (token check) |
| `Model 'X' not found` | Wrong model catalog ID | Check config.yaml model format (should be `stepfun/step-3.5-flash`) |
| `Refresh session has been revoked` | Nous OAuth refresh token expired | Full provider migration needed (see reactivation skill) |
| `No access token found for Nous Portal login` | Partial credential corruption (single agent) | Copy auth.json from healthy agent |
| `EOFError: marshal data too short` | **Corrupted Python bytecode (.pyc)** | Delete all `*.pyc` files and `__pycache__` dirs; restart gateways |
| `RuntimeError: Hermes is not logged into Nous Portal` | Expired/absent Nous Portal auth | Run `hermes model` to re-authenticate or copy valid auth.json |
| `RuntimeError: No Anthropic credentials found` | Missing ANTHROPIC_API_KEY env var | Set ANTHROPIC_TOKEN in profile `.env` or `config.yaml` provider section |
| ` ApiError: status_code: 401` from elevenlabs | Expired/invalid ElevenLabs API key | Refresh ELEVENLABS_API_KEY in profile config |
| `Telegram network error.*Bad Gateway` | Telegram API endpoint disruption or IP rate-limit/block | Check network connectivity to `api.telegram.org`; if transient, agent auto-retries. If persistent, verify no firewall/NAT blocking Telegram API. |
| `ps aux` process listings appear inside `errors.log` | **stderr/stdout stream pollution** — concurrent writes or FD collision | Truncate the corrupted error log; hunt for concurrent cron/worker writers sharing the same FD |

**If you see `InvalidToken` → immediate Phase 4.**

---

### Phase 3.5 — Bytecode Cache Corruption Detection (marshal data too short)

**Pattern:** Multiple agents simultaneously logging `EOFError: marshal data too short` and `Session summarization failed after 3 attempts: marshal data too short` in system journal (`journalctl`).

**Root cause:** Python bytecode cache (`.pyc`) corruption in the shared Hermes installation or profile-specific `__pycache__` directories. The error originates from `importlib._bootstrap_external` during module compilation when reading Marshal-formatted bytecode.

**Symptoms:**
- Errors appear across multiple agents within seconds of each other (correlated timing)
- Traceback shows: `File "<frozen importlib._bootstrap_external>", line 729, in _compile_bytecode` → `EOFError: marshal data too short`
- Session search/summarization features fail (the operation that triggered the import)
- Agents themselves may still be RUNNING (PID exists, CPU/MEM normal), but specific features are broken
- System journal (`journalctl --since today`) contains repeated `marshal data too short` entries per agent

**Diagnostic commands:**
```bash
# Check system journal for marshal errors in last 30 minutes
journalctl --since "30 min ago" | grep -E 'marshal data too short|Session summarization failed'

# Check WHICH agents are affected (by PID)
for agent in yoyo dmob desmond gentech; do
  pid_file="/root/.hermes/profiles/$agent/gateway.pid"
  if [ -f "$pid_file" ]; then
    pid=$(python3 -c "import json; print(json.load(open('$pid_file'))['pid'])")
    echo "=== $agent (PID $pid) ==="
    journalctl --since today | grep "python\\[$pid\\]" | grep -E 'marshal|summarization' | tail -5
  fi
done

# Check for corrupted .pyc files (mtime today, suspicious size 0 or tiny)
find /usr/local/lib/hermes-agent -name "*.pyc" -size -1k -newermt today 2>/dev/null
find /root/.hermes/profiles -type d -name "__pycache__" -exec ls -la {} \; 2>/dev/null | head -20
```

**Recovery procedure:**
```bash
# Step 1: Stop all affected gateways
pkill -f "hermes gateway run" 2>/dev/null || true
sleep 3

# Step 2: Clear ALL Python bytecode caches
find /usr/local/lib/hermes-agent -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /usr/local/lib/hermes-agent -name "*.pyc" -delete 2>/dev/null || true
find /root/.hermes/profiles -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /root/.hermes/profiles -name "*.pyc" -delete 2>/dev/null || true

# Also clear Hermes pycache root
rm -rf /root/.hermes/__pycache__ 2>/dev/null || true

# Step 3: Clear all stale locks (standard Phase 2)
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock

# Step 4: Restart sequentially (standard Phase 6)
AGENTS=(yoyo dmob desmond gentech)
for agent in "${AGENTS[@]}"; do
  profile="/root/.hermes/profiles/$agent"
  echo "Starting $agent..."
  HERMES_HOME="$profile" nohup \
    /root/.hermes/hermes-agent/venv/bin/python3 \
    /root/.local/bin/hermes gateway run \
    >> "$profile/logs/gateway.out" 2>&1 &
  sleep 5
done

# Step 5: Verify recovery
sleep 15
# Check for recurrence of marshal errors in journal
journalctl --since "5 min ago" | grep -E 'marshal data too short' && echo "⚠️ STILL CORRUPTED" || echo "✓ No marshal errors"
# Verify agents running
ps aux | grep 'hermes gateway run' | grep -v grep | wc -l
```

**Prevention & Monitoring:**
- Add watchdog check: scan `journalctl --since "10 min ago"` for `marshal data too short` per agent
- If detected on ANY agent, trigger automated cache clear + staggered gateway restart
- Monitor `.pyc` file sizes: zero-byte or truncated files indicate incomplete writes (disk pressure, NFS issues)
- Avoid concurrent Hermes package upgrades while gateways are running

**Cron executor health:** Always validate that the ticker's `"Cron ticker started"` message is followed by `"checking X jobs"` within 60s; absence indicates executor thread blockage (disk I/O, database lock, or bytecode corruption). See Phase 7.

---

## Phase 11 — Database Integrity Verification

SQLite corruption can silently break kanban dispatch, session summarization, and cron state. Add this check to your standard health diagnostic, especially after any gateway crash or I/O error.

**Quick integrity check for all key DBs:**

```bash
python3 - <<'PY'
import sqlite3, glob, sys
db_paths = [
    '/root/.hermes/state.db',
    '/root/.hermes/kanban.db',
    '/root/.hermes/cron/jobs.db',
]
for db in db_paths:
    try:
        conn = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
        result = conn.execute('PRAGMA integrity_check').fetchone()
        conn.close()
        if result and result[0] == 'ok':
            print(f'✓ {db}: ok')
        else:
            print(f'✗ {db}: {result}')
    except sqlite3.DatabaseError as e:
        print(f'✗ {db}: DatabaseError — {e}')
    except Exception as e:
        print(f'? {db}: {e}')
PY
```

**Interpretation:**
- `ok` → Database file structurally sound
- `database disk image is malformed` or any non-`ok` result → corruption detected; restore from backup or rebuild (see `gentech-agent-reactivation` for state recovery)

**If corruption found:**
1. Stop all gateways (`pkill -f "hermes gateway run"`)
2. Backup corrupted DBs (for forensics): `cp state.db state.db.corrupted.$(date +%s)`
3. Remove corrupted files; gateways will recreate fresh ones on restart
4. Restart gateways sequentially; verify state re-initialization in logs

---

## Quick Diagnostic Cheatsheet (Modern Error Patterns)

---

### Phase 4 — Telegram Token Validation

**Context:** Hermes agents use per-agent Telegram bot tokens stored in profile `.env` files (NOT in `auth.json` or `config.yaml`). When Telegram revokes a bot token (suspension, manual revocation by @BotFather, or security rotation), gateways reject it with `InvalidToken` and exit.

**Locate tokens in profile .env files:**
```bash
for agent in yoyo dmob desmond; do
  env_file="/root/.hermes/profiles/$agent/.env"
  echo "=== $agent .env ==="
  if [ -f "$env_file" ]; then
    grep -E 'TELEGRAM_BOT_TOKEN' "$env_file" || echo "No TELEGRAM_BOT_TOKEN found"
  else
    echo ".env file not found"
  fi
done
```

**Expected format:**
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_TOKEN_YOYO=1234567890:ABC...   # agent-specific variant
TELEGRAM_ALLOWED_USERS=7105876857
TELEGRAM_HOME_CHANNEL=-100XXXXX
```

**Verify token validity (without exposing it):**
```bash
# Extract just the bot ID (number before colon) to check if format looks right
grep -oE 'TELEGRAM_BOT_TOKEN=[0-9]+:' /root/.hermes/profiles/*/.env
```

**If tokens are present but rejected → they are revoked.** Telegram has invalidated them.

**Recovery path:**
1. Create 3 new bots via @BotFather (one per agent)
2. Update each profile's `.env` with the new token
3. Clear all gateway locks (Phase 2)
4. Restart gateways sequentially (Phase 5)

---

### Phase 5 — Verify Profile Integrity

Before restarting, ensure profiles are structurally sound:

```bash
# Check config.yaml exists and has provider/model
for agent in yoyo dmob desmond; do
  config="/root/.hermes/profiles/$agent/config.yaml"
  echo "=== $agent config.yaml ==="
  if [ -f "$config" ]; then
    grep -E '^(model|provider|base_url):' "$config" | head -5
  else
    echo "❌ config.yaml missing"
  fi
  
  # Check auth.json exists and has nous provider
  auth="/root/.hermes/profiles/$agent/auth.json"
  if [ -f "$auth" ]; then
    python3 -c "import json; a=json.load(open('$auth')); print('Providers:', list(a.get('providers',{}).keys()))"
  else
    echo "❌ auth.json missing"
  fi
done

# Verify auxiliary_client.py is valid (not corrupted)
python3 -m py_compile /root/.hermes/profiles/yoyo/home/auxiliary_client.py 2>&1 && echo "yoyo: OK" || echo "yoyo: CORRUPT"
```

**Red flags:**
- Missing `auth.json` → copy from `~/.hermes/auth.json`
- `auxiliary_client.py` syntax error → replace from `/root/.hermes/hermes-agent/agent/auxiliary_client.py`
- `home/.hermes` symlink broken → `ln -sf /root/.hermes $PROFILE_HOME/home/.hermes`

---

### Phase 6 — Restart & Verify

After fixing the root cause:

```bash
# Kill any lingering gateways
pkill -f "hermes gateway run" 2>/dev/null || true
sleep 2

# Clear ALL stale artifacts
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock

# Start gateways sequentially with 4s stagger
AGENTS=(yoyo dmob desmond)
for agent in "${AGENTS[@]}"; do
  profile="/root/.hermes/profiles/$agent"
  echo "Starting $agent..."
  HERMES_HOME="$profile" nohup \
    /root/.hermes/hermes-agent/venv/bin/python3 \
    /root/.local/bin/hermes gateway run \
    >> "$profile/logs/gateway.out" 2>&1 &
  sleep 4
done

# Wait for startup
sleep 10

# Verify running
ps aux | grep 'gateway run' | grep -v grep

# Check agent.log for successful connections
tail -20 /root/.hermes/logs/agent.log | grep -E '(telegram connected|Cron ticker started|ERROR)'
```

**Success indicators:**
- 3 gateway processes running (different PIDs)
- `agent.log` shows `✓ telegram connected` with recent timestamp
- No ERROR lines in last 2 minutes of agent.log
- Watchdog cron (every 15min) will report "All agents healthy"

---

## Decision Tree Summary

```
Gateways down?
├─ Check processes → None running
├─ Check lock files → Stale PIDs?
│  └─ YES → Clear locks → Attempt restart
│     └─ Crashes again → Check logs
├─ Check logs (gateway.out)
│  ├─ "PID file race" → Concurrent startup; kill all, restart sequentially
│  ├─ "Telegram bot token already in use" → Stale Telegram lock; clear it
│  ├─ "InvalidToken" / "token was rejected" → **TOKEN REVOKED** → Phase 4
│  ├─ "Model not found" → Wrong model ID in config.yaml
│  └─ "Refresh session revoked" → Nous OAuth expired → full provider migration
└─ Check .env for TELEGRAM_BOT_TOKEN (if InvalidToken)
   └─ Token present but rejected → Must regenerate via @BotFather
```

---

| `ps aux` process listings appear inside `errors.log` | "Log parser is broken" | Truncate the corrupted error log; hunt for concurrent cron/worker writers sharing the same FD |
| Error log > 100KB with no recent truncation | "Old issues, ignore" | **Check agent.log instead** — error.log may be stale; use timestamps to filter |
| Log files not growing while processes run | "Agents are stuck/hung" | Check kanban.db modification time; agents may be idle. If cron jobs are past-due and kanban.db is stale, executor blocked — investigate disk I/O, SQLite lock, or bytecode corruption. |

---

## Related Skills

- `devops/gentech-agent-reactivation` — Recovery procedures after root cause is identified
- `devops/hermes-provider-migration` — OAuth token revocation (Nous Portal) recovery
- `devops/hermes-vision-debug` — Debugging vision/photo analysis failures (different domain)

## Reference Materials

- `references/2026-05-02-multi-agent-cascade-crash.md` — INC-20260502-0055: All 4 gateways crashed simultaneously; Gentech required SIGKILL after 91s stop timeout; cascade pattern analysis and detection rule
- `references/2026-05-02-cron-executor-stall-pattern.md` — Cron subsystem stall detection: ticker running but executor deadlocked; jobs stuck in `scheduled` state; recovery via cron cache clear + staggered gateway restart
- `references/2026-05-02-systemic-cron-deadlock.md` — **NEW:** May 02 2026 systemic deadlock: all 4 agents freeze simultaneously; kernel stack `ep_poll` evidence; per-agent functional variance (Desmond ran, others stuck); no automated recovery; multi-agent correlation and post-restart executor failure patterns
- `references/2026-05-02-bytecode-corruption-yoyo-gentech.md` — Marshal bytecode cache corruption pattern: `EOFError: marshal data too short` during session summarization; detection via journalctl PID filtering; systematic cache clear + restart recovery; correlation with cron stalls
- `references/2026-05-02-routine-health-check-no-issues.md` — Routine multi-agent health check (2026-05-02): all agents healthy; confirmed log stagnation was idle state not hung; past May 1 disk I/O and channel errors resolved; YoYo config.yaml syntax errors corrected
- `references/2026-05-01-multi-agent-failure-patterns.md` — Incident digest: simultaneous multi-agent crash patterns discovered across Gentech, YoYo, DMOB, Desmond (bytecode corruption, process-list pollution, provider auth pipeline failures)

## Notes

**Discovered 2026-04-22:** Telegram bot token revocation is a silent killer — gateways fail with `InvalidToken` and exit immediately. Tokens are stored in profile `.env` files, not in `auth.json`. The fix requires manual @BotFather interaction; no automated recovery exists.

**Log hygiene:** Always check `agent.log` for current state. `gateway.out` may contain pre-restart error banners that are no longer relevant due to log file reuse.

---

## Quick Diagnostic Cheatsheet (Modern Error Patterns)

```bash
# Check if any agent is currently running
ps aux | grep 'hermes gateway run' | grep -v grep

# Scan all agents for bytecode corruption (marshal error)
grep -r 'marshal data too short' /root/.hermes/profiles/*/logs/ 2>/dev/null

# Scan for process-list pollution in error logs (noise)
for a in gentech yoyo dmob desmond; do
  count=$(grep -c '^  root  [0-9]' /root/.hermes/profiles/$a/logs/errors.log 2>/dev/null || echo 0)
  echo "$a: $count process-list lines"
done

# Identify which providers each agent is trying to use
for a in gentech yoyo dmob desmond; do
  echo "=== $a ==="
  grep -E ' Nous|Anthropic|elevenlabs|stepfun|minimax|openrouter' /root/.hermes/profiles/$a/logs/errors.log 2>/dev/null | head -3
done

# Check last gateway lifecycle event per agent
for a in gentech yoyo dmob desmond; do
  echo "=== $a ==="
  grep -E '(Gateway stopped|Exiting with code|Scheduler started)' /root/.hermes/profiles/$a/logs/agent.log | tail -3
done
```

**Interpretation:**
- `marshal data too short` present → **bytecode corruption** → clear `.pyc` caches
- `Nous Portal` / `hermes model` errors → **Nous auth expired** → re-login via `hermes model`
- `No Anthropic credentials` → **missing ANTHROPIC_TOKEN** → set in `.env` or `config.yaml`
- `status_code: 401` from elevenlabs → **TTS key invalid** → refresh `ELEVENLABS_API_KEY`
- Model `not found` errors (minimax, open3.5, etc.) → **provider catalog deprecation** → verify model exists on provider site, update `config.yaml` model ID
- `ps aux` lines in errors → **log FD collision** → truncate log; hunt for concurrent cron/worker writers

---

## Phase 7 — Cron Subsystem Stall Detection & Recovery

**Critical pattern:** Gateway processes are RUNNING but scheduled jobs are NOT executing despite the ticker reporting "Cron ticker started".

**Symptoms:**
- `ps aux` shows all 4 gateway processes running
- Each gateway.log shows `Cron ticker started (interval=60s)` (repeatedly)
- `hermes cron list` shows jobs with past-due `next_run_at` (e.g., `2026-05-02T00:15:00+00:00`) but `state: "scheduled"` (not `active`)
- Zero recent sessions (no job-triggered work in 2+ hours)
- `agent.log` has NO `Running job` entries since gateway restart
- Watchdog job itself reports failure: `RuntimeError: ## Watchdog Alert: Hermes Cron Subsystem Not Executing Jobs`

**NEW — Cron jobs never executed pattern (detected 2026-05-02):**
- `hermes cron list` returns jobs where `last_run_at: null` (never run since creation)
- `next_run_at` values are in the past (e.g., `2026-04-30T07:00:00+00:00`) — jobs are critically overdue
- Gateway log shows repeated `Cron ticker started/stopped` cycles but **zero** entries containing `cron executor started`, `checking jobs`, or `executing job`
- Cron ticker thread alive but executor thread never dispatches (deadlocked at startup or blocked on shared resource)

**Diagnostic commands:**

```bash
# 1. Check cron job database state
hermes cron list --verbose

# 2. Look for executor lifecycle events in gateway.log (not just ticker)
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent cron executor activity ==="
  grep -E 'cron executor|checking [0-9]+ jobs|executing job|pausing exec' \
    /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null | tail -10
done

# 3. Verify if any jobs have ever run (check agent.log for job execution markers)
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent job execution history ==="
  grep "Running job" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null | tail -5
done

# 4. Check for executor-blocking errors in gateway.log
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent executor-blocking errors ==="
  grep -E ' executor deadlock|blocking|deadlock|I/O error|disk I/O error|locked' \
    /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null | tail -5
done
```

**Common causes:**
1. **Threading/async blockage** — Executor thread deadlocked on I/O (kanban notifier disk I/O errors, SessionDB full warnings)
2. **Database lock** — SQLite `journal_mode=WAL` failure or disk full (`[Errno 28] No space left on device`)
3. **SessionDB corruption** — `Failed to initialize SessionDB — session will NOT be indexed for search: database or disk is full`
4. **Provider resolution failure cascade** — Repeated model-not-found/auth failures blocking executor loop
5. **Gateway restart race** — Ticker restarted but executor thread never reattached to job queue
6. **Cron state corruption** — Embedded cron cache/state files inconsistent with jobs.json (can happen after crash)

**Diagnostic commands:**

```bash
# 1. Check cron executor thread status (look for executor lifecycle messages)
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent ==="
  grep -E 'cron ticker|cron executor|checking jobs|executing job|pausing|executor started' \
    /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null | tail -20
done

# 2. Check if jobs are loaded and due
hermes cron list

# 3. Kernel stack analysis — detect if executor thread is stuck in I/O wait
for pid in $(pgrep -f "hermes gateway run"); do
  echo "PID $pid:"
  cat /proc/$pid/stack 2>/dev/null | grep -E 'ep_poll|schedule|wait' || echo "  (stack not available)"
done
# If you see `ep_poll` repeatedly, the thread is blocked in uninterruptible I/O sleep

# 4. Verify log recency — a completely stale gateway.log (>1h) while process runs is a red flag
find /root/.hermes/profiles -name "gateway.log" -exec stat -c '%Y %n' {} \; | sort -n

# 5. Compare per-agent executor activity
# Desmond ran a job at 00:00:35 post-restart while others didn't — suggests per-agent config/provider blockage
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent last Running job ==="
  grep "Running job" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null | tail -1
done
```

**Quick decision tree:**
- Ticker logs present + **zero** `checking`/`executing` logs over multiple intervals → Executor deadlocked or crashed
- Any `Running job` entries in last 60 min → Executor functional; investigate individual job errors instead
- Multiple agents freeze simultaneously within minutes → Likely shared resource (kanban DB, session DB, bytecode cache)

**Common causes:**
1. **Threading/async blockage** — Executor thread deadlocked on I/O (kanban notifier disk I/O errors, SessionDB full warnings)
2. **Database lock** — SQLite `journal_mode=WAL` failure or disk full (`[Errno 28] No space left on device`)
3. **SessionDB corruption** — `Failed to initialize SessionDB — session will NOT be indexed for search: database or disk is full`
4. **Provider resolution failure cascade** — Repeated model-not-found/auth failures blocking executor loop
5. **Executor thread exception** — Unhandled exception in cron executor silently kills the thread while ticker continues; common triggers: corrupted bytecode during job import (`EOFError: marshal data too short`), database handle failure inherited from kanban notifier, missing provider credentials during job initialization
6. **Gateway restart race** — Ticker restarted but executor thread never reattached to job queue
7. **Cron state corruption** — Embedded cron cache/state files inconsistent with jobs.json (can happen after crash)
2. **Database lock** — SQLite `journal_mode=WAL` failure or disk full (`[Errno 28] No space left on device`)
3. **SessionDB corruption** — `Failed to initialize SessionDB — session will NOT be indexed for search: database or disk is full`
4. **Provider resolution failure cascade** — Repeated model-not-found/auth failures blocking executor loop
5. **Gateway restart race** — Ticker restarted but executor thread never reattached to job queue

**Recovery steps:**

```bash
# Step A: Clear embedded cron state (safe — jobs.json is source of truth)
**Recovery steps:**

```bash
# Step A: Clear embedded cron state (safe — jobs.json is source of truth)
# Stop all gateways
pkill -f "hermes gateway run" 2>/dev/null || true
sleep 3

# Clear per-agent cron caches/state (forces fresh load on restart)
for agent in gentech yoyo dmob desmond; do
  rm -f /root/.hermes/profiles/$agent/cron/*.db 2>/dev/null
  rm -f /root/.hermes/profiles/$agent/cron/*.state 2>/dev/null
done

# Clear all stale locks
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/*.lock

# Step B: Fix underlying issues before restart
#  - Clear disk space if needed (df -h)
#  - Delete corrupted bytecode (.pyc/__pycache__) if marshal errors present
#  - Fix provider auth (hermes model, set ANTHROPIC_TOKEN, etc.)
#  - Repair corrupted SQLite DBs (kanban.db) if integrity_check fails

# Step C: Restart gateways sequentially (prevents PID file races)
AGENTS=(yoyo dmob desmond gentech)
for agent in "${AGENTS[@]}"; do
  profile="/root/.hermes/profiles/$agent"
  echo "Starting $agent..."
  HERMES_HOME="$profile" nohup \
    /root/.hermes/hermes-agent/venv/bin/python3 \
    /root/.local/bin/hermes gateway run \
    >> "$profile/logs/gateway.out" 2>&1 &
  sleep 5  # 5s stagger to avoid lock contention
done

# Step D: Verify cron executor resumed
sleep 15

# Check for executor activity (should see "checking" and "executing" lines)
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent cron activity ==="
  grep -E 'checking|executing|pausing|tick' \
    /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null | tail -10
done

# Check agent.log for recent job runs
echo "=== Recent job executions ==="
grep -E 'Running job.*[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' \
  /root/.hermes/profiles/*/logs/agent.log 2>/dev/null | tail -10
```

**Pre-recovery check:** Before restarting, verify deadlock scope. Check each `agent.log` for any `Running job` entry within the last hour. If ANY agent shows recent execution, that agent's executor is functional — investigate per-agent job failures instead of full cluster restart. This can pinpoint provider/credential issues vs. systemic blockage.

**Post-recovery verification:**
- `agent.log` shows `Running job` entries with timestamps within 10 minutes of gateway restart
- `gateway.log` contains `cron.scheduler: checking X jobs` followed by `executing job` lines
- Past-due jobs transition from `scheduled` → `active` → `completed`/`failed` within expected windows
- Watchdog job next run reports `ok` (monitor for 2 consecutive cycles)
- If deadlock persists after restart, check `/proc/<pid>/stack` for `ep_poll` — indicates I/O wait on underlying storage (kanban DB, session DB); may need DB repair, disk space recovery, or kanban notifier disablement

**If stall affects only subset:** Restart only the blocked agents; leave functional ones undisturbed. Compare blocked vs. functional agent configs (provider, model, `.env` vars) to isolate the trigger.

**Success criteria:**
- Gateway log shows "checking X jobs" followed by "executing job" (not just "ticker started")
- `agent.log` shows `Running job` entries with recent timestamps
- Past-due jobs transition from `scheduled` → `active` and eventually `completed`/`failed`
- Watchdog job no longer reports cron subsystem failure

**If stall persists after restart:** The executor thread is hitting a hard exception/dispatch error. Check `gateway.log` for uncaught tracebacks or kanban notifier I/O errors (dmob/desmond had `PRAGMA journal_mode=WAL` disk I/O failures). May need to disable kanban dispatcher temporarily or fix underlying DB/storage issue.

---

## Phase 8 — Runtime Health Metrics & Degradation Detection

**Purpose:** When gateways are running and responding to messages, but you suspect hidden degradation (slow responses, silent failures, partial functionality).

**Key metrics to check:**

```bash
# 1. Agent response time analysis (from gateway.log)
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent response times (last 30 min) ==="
  grep 'response ready: time=' /root/.hermes/profiles/$agent/logs/gateway.log \
    | tail -10 | sed 's/.*time=//' | sed 's/s.*//' | awk '{sum+=$1; count++} END {if(count) printf "Avg: %.1fs, Max: %.1fs, Count: %d\n", sum/count, max, count}'
done

# 2. Error rate per agent (last 30 min)
for agent in gentech yoyo dmob desmond; do
  count=$(grep -c 'ERROR' /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null || echo 0)
  echo "$agent: $count ERROR entries in errors.log"
done

# 3. Failed API calls by provider
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent provider errors (last 20) ==="
  grep -E 'status_code: 401|NotFoundError|AuthenticationError|InvalidToken' \
    /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null | tail -5
done

# 4. Cron job execution audit (are scheduled jobs actually firing?)
echo "=== Cron execution audit (last 2 hours) ==="
for agent in gentech yoyo dmob desmond; do
  count=$(grep -c 'Running job' /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null || echo 0)
  echo "$agent: $count job executions (agent.log)"
done
```

**Degradation thresholds:**
- **Response time > 60s avg** for >10 consecutive messages → investigate (likely retry storms, auth failures, model timeouts)
- **Zero cron executions** for >2 hours with past-due jobs → **Phase 7 (Cron stall)**
- **ERROR count increasing** in errors.log with no corresponding fix → likely credential rot or persistent infrastructure issue
- **Provider 401/404 errors** > 5 occurrences → **Phase 11 (Credential audit)**

**Quick degradation verdict:**
```bash
# One-liner health summary
for agent in gentech yoyo dmob desmond; do
  last_line=$(tail -1 /root/.hermes/profiles/$agent/logs/gateway.log)
  last_error=$(grep 'ERROR' /root/.hermes/profiles/$agent/logs/errors.log | tail -1)
  echo "$agent: gateway=$(echo $last_line | cut -c1-50)... errors=$(grep -c ERROR errors.log || echo 0)"
done
```

---

## Phase 9 — Credential & API Key Audit

**NEW (2026-05-02):** Silent credential failures are a top cause of agent degradation. Agents continue running but specific features (TTS, cron jobs requiring Anthropic, Nous auth) fail with 401/403 errors. DMOB, Desmond, and Gentech all suffered from invalid ElevenLabs API keys; DMOB also lacked ANTHROPIC_TOKEN.

**Required checks:**

```bash
# 1. Check each agent's .env for critical API keys
agents=(yoyo dmob desmond gentech)
for agent in "${agents[@]}"; do
  env_file="/root/.hermes/profiles/$agent/.env"
  echo "=== $agent credential audit ==="
  if [ -f "$env_file" ]; then
    for key in ANTHROPIC_TOKEN ELEVENLABS_API_KEY ELEVENLABS_API_KEY_VOICE OPENAI_API_KEY GITHUB_PAT; do
      if grep -q "^$key=" "$env_file"; then
        val=$(grep "^$key=" "$env_file" | cut -d= -f2)
        if [ ${#val} -gt 10 ]; then
          echo "  ✓ $key present (${val:0:8}...)"
        else
          echo "  ⚠️  $key present but value seems short/invalid: '$val'"
        fi
      else
        echo "  ✗ $key MISSING"
      fi
    done
  else
    echo "  ❌ .env file not found"
  fi
done

# 2. Check for repeated 401/403 errors in recent logs (last 30 min)
since=$(date -d '30 min ago' '+%Y-%m-%d %H:%M')
for agent in gentech yoyo dmob desmond; do
  count=$(grep -c "since \"$since\"" /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null || echo 0)
  # Actually count lines with 401/403 after timestamp
  count=$(grep -E "status.code.*40[13]" /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null | wc -l)
  echo "$agent: $count auth errors (401/403) in errors.log"
done

# 3. Validate ElevenLabs key format (should be long hex/alpha string)
for agent in dmob desmond gentech; do
  key=$(grep '^ELEVENLABS_API_KEY=' /root/.hermes/profiles/$agent/.env 2>/dev/null | cut -d= -f2)
  if [ -n "$key" ]; then
    len=${#key}
    if [ $len -lt 20 ]; then
      echo "$agent: ElevenLabs key suspiciously short ($len chars) — likely invalid"
    else
      echo "$agent: ElevenLabs key length OK ($len chars)"
    fi
  fi
done
```

**Credential health thresholds:**
- `ANTHROPIC_TOKEN` **missing** → cron jobs requiring Anthropic will fail immediately (DMOB case)
- `ELEVENLABS_API_KEY` returning 401 → TTS tool unusable; invalid key likely needs regeneration from ElevenLabs dashboard
- `OPENAI_API_KEY` returning 401 → all LLM calls fail; agent partially or fully degraded
- `Nous Portal` auth expired → `hermes model` re-authentication required; session summarization broken

**Immediate fixes:**
- **Missing ANTHROPIC_TOKEN**: Add `ANTHROPIC_TOKEN=<key>` to the agent's `.env` and restart gateway
- **Invalid ElevenLabs key**: Regenerate in ElevenLabs console → update all affected agent `.env` files (currently dmob, desmond, gentech share the same broken key)
- **Expired Nous auth**: Run `hermes model` as the agent user to re-auth; copies `auth.json` to profile

---

## Phase 10 — Response Time & Quality-of-Service Monitoring

**NEW (2026-05-02):** Response time degradation is an early indicator of executor blockage or provider issues, even when agents appear "up". DMOB averaged **96s** per response during the incident vs. normal 16-24s.

**Monitoring procedure:**

```bash
# Extract recent response times (last 50 messages) per agent
for agent in gentech yoyo dmob desmond; do
  log="/root/.hermes/profiles/$agent/logs/gateway.log"
  echo "=== $agent response time trend (last 10) ==="
  grep 'response ready: time=' "$log" | tail -10 | \
    sed 's/.*time=\([0-9.]*\)s.*/\1/' | \
    awk '{if (NR==1) {min=max=$1; sum=$1} else {if($1<min)min=$1; if($1>max)max=$1; sum+=$1} } END {printf "min=%.1fs max=%.1fs avg=%.1fs\n", min, max, sum/NR}'
done

# Check for timeouts (>60s) — indicates retry storms or provider unavailability
for agent in gentech yoyo dmob desmond; do
  timeouts=$(grep 'response ready: time=[6-9][0-9]\|time=[1-9][0-9][0-9]' \
    /root/.hermes/profiles/$agent/logs/gateway.log | wc -l)
  echo "$agent: $timeouts responses >60s in last 200 lines"
done
```

**Interpretation:**
- **Avg > 40s with rising trend** → executor blocked or provider latency (check kanban DB age, disk I/O)
- **Any response > 120s** → likely hit 120s timeout and retried (DMOB showed 260s total due to retries)
---

## Phase 11 — Provider & Model Health Verification

Agents depend on external LLM providers. When a provider is down or model ID is invalid, the agent logs repeated auth/not-found errors, which can cascade into executor blockage and cron stalls.

**Provider status check:**

```bash
# Scan for provider-specific error patterns across all agents
echo "=== Provider error summary (last 50 lines) ==="
for agent in gentech yoyo dmob desmond; do
  echo "--- $agent ---"
  # OpenAI/StepFun errors
  grep -E 'openai|stepfun|status.code.*[45][0-9]{2}' \
    /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null | tail -5
  # Anthropic errors
  grep -i 'anthropic' \
    /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null | tail -3
  # Nous auth errors
  grep -i 'nous|refresh session|Nous Portal' \
    /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null | tail -3
  # ElevenLabs TTS errors
  grep -i 'elevenlabs|TTS' \
    /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null | tail -3
done
```

**Provider health indicators:**
- **StepFun/OpenAI**: `status_code: 404` with "Couldn't find that, sorry" → model ID invalid or not accessible
- **Anthropic**: `No Anthropic credentials found` → missing `ANTHROPIC_TOKEN`
- **Nous**: `Refresh session has been revoked` → OAuth token expired, need full `hermes model` re-auth
- **ElevenLabs**: `status_code: 401` → API key invalid or revoked

**Fixes by provider:**
- **StepFun**: Verify model in `config.yaml` is valid (e.g., `stepfun/step-3.5-flash`); test with `hermes model list`
- **Anthropic**: Set `ANTHROPIC_TOKEN` in agent `.env`; verify via `hermes models`
- **Nous**: Run `hermes model` as agent user to refresh OAuth session
- **ElevenLabs**: Regenerate API key in ElevenLabs dashboard; update all agent `.env` files

**Model validation test (per agent):**
```bash
# Quick dry-run: ask agent to list available models (non-destructive)
HERMES_HOME="/root/.hermes/profiles/yoyo" \
  /root/.hermes/hermes-agent/venv/bin/python3 \
  /root/.local/bin/hermes model list 2>&1 | head -10
```

---

## Phase 12 — Multi-Agent Crisis Recovery Checklist

When ALL agents are simultaneously degraded (as detected on 2026-05-02):

**Simultaneous failures checklist:**
- [ ] **Stop all gateways** (`pkill -f "hermes gateway run"`; verify no lingering processes)
- [ ] **Clear ALL Python bytecode caches** (shared installation + per-profile `__pycache__`)
- [ ] **Clear ALL cron state files** (`/root/.hermes/profiles/*/cron/*.db`, `*.state`, `*.lock`)
- [ ] **Clear ALL stale locks** (`gateway.pid`, `telegram-bot-token-*.lock`)
- [ ] **Verify disk space** (`df -h /` — ensure >15% free; clear if >85%)
- [ ] **Audit critical credentials** (Phase 11) — at minimum:
  - ANTHROPIC_TOKEN for DMOB
  - ElevenLabs API keys for all three TTS-enabled agents
  - Nous Portal auth for YoYo & Gentech
- [ ] **Fix configuration errors** (e.g., YoYo `config.yaml` YAML syntax)
- [ ] **Restart gateways sequentially** with 5s stagger (from slowest to fastest or alphabetical)
- [ ] **Wait 30s** then verify:
  - [ ] All 4 gateways running (`ps aux | grep gateway run | wc -l == 4`)
  - [ ] No marshal bytecode errors in `journalctl --since "5 min ago"`
  - [ ] Cron executor activity present in each gateway.log (`checking`/`executing` lines)
  - [ ] Past-due jobs transitioning to `active` state (`hermes cron list`)
  - [ ] Response times normalized (< 40s avg)
  - [ ] No new ERROR entries in `errors.log`

---

## Phase 13 — Kanban Database Integrity & I/O Error Recovery

**Observed pattern (May 1):** Disk exhaustion caused SQLite `disk I/O error` and `database disk image is malformed` in Desmond and Gentech kanban DBs.

**Diagnostic:**
```bash
# Check kanban DB integrity for all agents
for agent in gentech yoyo dmob desmond; do
  db="/root/.hermes/profiles/$agent/kanban.db"
  echo "=== $agent ==="
  sqlite3 "$db" "PRAGMA integrity_check;" 2>&1
  sqlite3 "$db" "PRAGMA quick_check;" 2>&1
done
```

**If corruption detected:**
```bash
# Option 1: Restore from backup (if exists)
ls -la /root/.hermes/profiles/*/kanban.db.backup* 2>/dev/null

# Option 2: Export and rebuild (if no backup but DB readable)
sqlite3 /root/.hermes/profiles/desmond/kanban.db ".backup '/tmp/desmond_kanban_recovered.db'"
# Then replace corrupted DB
cp /tmp/desmond_kanban_recovered.db /root/.hermes/profiles/desmond/kanban.db

# Option 3: If DB unrecoverable, clear and restart with empty DB
# WARNING: Loses all kanban tasks; use only as last resort
rm /root/.hermes/profiles/desmond/kanban.db
# Restart agent — it will recreate an empty DB
```

**Prevention:**
- Monitor disk space: alert if >85%
- Ensure kanban notifier thread not blocked on I/O (check gateway.log for `kanban notifier tick failed`)
- Use `PRAGMA journal_mode=WAL` for better concurrency (should be default)

---

## Decision Tree Summary (Expanded)

```
Gateways down?
├─ Check processes → None running
├─ Check lock files → Stale PIDs?
│  └─ YES → Clear locks → Attempt restart
│     └─ Crashes again → Check logs (Phase 3)
├─ Check logs (gateway.out)
│  ├─ "PID file race" → Concurrent startup; kill all, restart sequentially
│  ├─ "Telegram bot token already in use" → Stale Telegram lock; clear it
│  ├─ "InvalidToken" / "token was rejected" → TOKEN REVOKED → Phase 4
│  ├─ "Model not found" → Wrong model ID in config.yaml
│  ├─ "Refresh session revoked" → Nous OAuth expired → full provider migration
│  ├─ "EOFError: marshal data too short" → Bytecode corruption → Phase 3.5
│  └─ "No Anthropic credentials" / "401" → Credential failures → Phase 11
└─ Check .env for TELEGRAM_BOT_TOKEN (if InvalidToken)
   └─ Token present but rejected → Must regenerate via @BotFather

Gateways running but cron jobs never firing?
├─ hermes cron list → last_run_at: null for all jobs? → YES
├─ gateway.log → Cron ticker started but NO "executing job" entries? → YES
├─ Check kanban.db modification time → stale (>2min)? → YES
│   └─ Cron executor blocked → Phase 7 (clear cron state + restart)
└─ Check response times → elevated (>60s)? → Phase 10

Single agent degraded (slow, TTS broken, auth failures)?
├─ Check response time trend → elevated? → Phase 10
├─ Check errors.log for provider 401s → Yes → Phase 11 (credential audit)
└─ Check config.yaml for that agent → syntax errors? → fix and restart

**Pattern:** One or more gateways consistently exceed `TimeoutStopSec` (default 90s), requiring SIGKILL. Indicates blocked shutdown cleanup (kanban notifier flush, cron cache write, SessionDB commit).

**Diagnostic:**
```bash
# Check for timeout events
journalctl -n 200 --no-pager | grep -i 'State .stop-sigterm. timed out'
journalctl -n 200 --no-pager | grep -i 'Killing process.*with signal SIGKILL'
```

**Immediate mitigation:**
- Increase systemd user service timeout: edit `~/.config/systemd/user/hermes-gateway-*.service` and add:
  ```
  [Service]
  TimeoutStopSec=180
  ```
- Reload systemd: `systemctl --user daemon-reload`
- Restart gateway: `systemctl --user restart hermes-gateway-<agent>`

**Long-term:** Identify blocking resource (kanban DB, cron state, network I/O) and fix; do not just extend timeout indefinitely.

---

## Decision Tree Summary

```
Gateways down?
├─ Check processes → None running
├─ Check lock files → Stale PIDs?
│  └─ YES → Clear locks → Attempt restart
│     └─ Crashes again → Check logs
├─ Check logs (gateway.out)
│  ├─ "PID file race" → Concurrent startup; kill all, restart sequentially
│  ├─ "Telegram bot token already in use" → Stale Telegram lock; clear it
│  ├─ "InvalidToken" / "token was rejected" → **TOKEN REVOKED** → Phase 4
│  ├─ "Model not found" → Wrong model ID in config.yaml
│  └─ "Refresh session revoked" → Nous OAuth expired → full provider migration
└─ Check .env for TELEGRAM_BOT_TOKEN (if InvalidToken)
   └─ Token present but rejected → Must regenerate via @BotFather
```

**Cascade-specific path:**
```
Multiple gateways failed together?
├─ Check timing cluster (<60s window) → YES
├─ Did any timeout (>90s)? → YES → Phase 10 (stop-timeout anomaly)
├─ Look for upstream stop initiator → None found → Likely shared resource hang (kanban/cron)
└─ Recovery: clear caches + sequential restart with 10s stagger
```
