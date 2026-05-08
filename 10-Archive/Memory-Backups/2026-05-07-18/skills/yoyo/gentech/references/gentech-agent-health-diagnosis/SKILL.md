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
| `ps aux` process listings appear inside `errors.log` | **stderr/stdout stream pollution** — concurrent writes or FD collision | Truncate corrupted error log; investigate concurrent cron/worker writers |

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
- If detected on ANY agent, trigger automated cache clear + staggered restart
- Monitor `.pyc` file sizes: zero-byte or truncated files indicate incomplete writes (disk pressure, NFS issues)
- Avoid concurrent Hermes package upgrades while gateways are running

**Correlation with Phase 7 (Cron stalls):** Bytecode corruption can cause cron executor thread to crash silently, creating a combined failure mode: gateways RUNNING but cron NOT executing. After clearing cache and restarting, verify both gateway connectivity AND cron executor activity.

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

**Diagnostic commands:**

```bash
# 1. Check if cron executor thread is actually dispatching
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent ==="
  grep -E 'cron ticker|cron executor|checking jobs|executing job|pausing' \
    /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null | tail -20
done

# 2. Check if jobs are loaded and due
hermes cron list

# 3. Check gateway.log for executor lifecycle messages
# Look for: "Cron executor started", "checking X jobs", "executing job", "job completed"
# vs just "Cron ticker started" (ticker only) with no executor follow-through

# 4. Verify embedded cron is actually polling
# The ticker should log every 60s. If you see ticker starts but NO "checking" messages,
# the executor thread is blocked/deadlocked after ticker fires.
```

**Common causes:**
1. **Threading/async blockage** — Executor thread deadlocked on I/O (kanban notifier disk I/O errors, SessionDB full warnings)
2. **Database lock** — SQLite `journal_mode=WAL` failure or disk full (`[Errno 28] No space left on device`)
3. **SessionDB corruption** — `Failed to initialize SessionDB — session will NOT be indexed for search: database or disk is full`
4. **Provider resolution failure cascade** — Repeated model-not-found/auth failures blocking executor loop
5. **Gateway restart race** — Ticker restarted but executor thread never reattached to job queue

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
grep -E 'Running job.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' \
  /root/.hermes/profiles/*/logs/agent.log 2>/dev/null | tail -10
```

**Success criteria:**
- Gateway log shows "checking X jobs" followed by "executing job" (not just "ticker started")
- `agent.log` shows `Running job` entries with recent timestamps
- Past-due jobs transition from `scheduled` → `active` and eventually `completed`/`failed`
- Watchdog job no longer reports cron subsystem failure

**If stall persists after restart:** The executor thread is hitting a hard exception/dispatch error. Check `gateway.log` for uncaught tracebacks or kanban notifier I/O errors (dmob/desmond had `PRAGMA journal_mode=WAL` disk I/O failures). May need to disable kanban dispatcher temporarily or fix underlying DB/storage issue.

---

## Phase 8 — Multi-Agent Correlation Analysis

When multiple agents fail in the same timeframe, look for shared infrastructure dependencies:

**Common failure points across all agents:**
1. **Nous Portal OAuth** — All agents using `stepfun/step-3.5-flash` share the same Nous auth token. If it expires/revokes, all fail simultaneously.
2. **Cron subsystem** — Embedded in each gateway. If there's a bug in the scheduler (e.g., job executor thread blockage), it affects all agents.
3. **Telegram platform** — All agents use Telegram delivery. If Telegram API rate-limits or blocks the user's IP, all fail.
4. **Disk I/O / storage** — Shared `/root` filesystem. Disk full, I/O errors (WAL failures), or inode exhaustion cascade to all agents.
5. **Python bytecode cache** — Corrupted `.pyc` files in shared agent installation affect all profiles using that Python venv.

**Correlation diagnostic:**

```bash
# Check if failures line up temporally
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent last 10 ERROR/CRITICAL entries ==="
  grep -E 'ERROR|CRITICAL' /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null | tail -10
  echo
done

# Check shared resource health
df -h /root
df -i /root  # inode usage
ls -la /root/.hermes/ | head -20  # check for stale lock files

# Check if all agents point to the same Nous auth
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent nous auth ==="
  ls -la /root/.hermes/profiles/$agent/auth.json 2>/dev/null || echo "No auth.json"
done
```

**If all agents failed simultaneously:**
- Inspect `/root/.hermes/logs/agent.log` for system-wide events (provider outage, disk full, network partition)
- Check `hermes-agent` package updates (may have broken compatibility)
- Review `/root/.hermes/profiles/*/logs/gateway.log` for concurrent crash signals

**If failures staggered:**
- Each agent degraded independently (likely config-specific: missing API keys, revoked tokens, exceeded quotas)
- Check agent-specific `.env` files for TTS/custom provider credentials

---

## Phase 9 — Multi-Agent Cascade Crash Pattern Detection

**Pattern discovered:** All gateways crash within a short window (<60s) and one or more requires SIGKILL due to `TimeoutStopSec` exceeded. This is distinct from staggered independent failures.

**Symptoms:**
- `journalctl` shows 3–4 `Stopping hermes-gateway-*` entries within 60 seconds
- One gateway logs `State 'stop-sigterm' timed out. Killing.` and exits with `status=9/KILL`
- All gateways subsequently restart (systemd auto-restart) and become healthy within 2 minutes
- Post-crash, `ps aux` shows all gateways running with normal CPU/MEM; no lingering zombies
- No auth errors, `InvalidToken`, or `marshal data too short` errors present during cascade

**Diagnostic checklist:**

```bash
# 1. Verify cascade timing
journalctl -n 200 --no-pager | grep -E 'Stopping|Started hermes-gateway' | tail -20

# 2. Check if any gateway exceeded its stop timeout
journalctl -n 200 --no-pager | grep -i 'timed out\\|killing process'

# 3. Look for upstream stop initiator
# Search for "stop hermes-gateway" or "gateway stop" commands in the pre-cascade window
journalctl -n 300 --no-pager | grep -E 'stop hermes-gateway|gateway stop' | grep -v 'Stopping'

# 4. Check for concurrent cron/background activity that might have triggered it
# E.g., brain backup, update scripts, health-check loops that called "stop-all"
journalctl -n 500 --no-pager | grep -E 'brain-backup\\|update\\|health-check\\|watchdog' | tail -10
```

**Root cause hypotheses (in descending probability):**

| # | Hypothesis | Evidence to gather | Recovery |
|---|-------------|-------------------|----------|
| 1 | **Coordinated restart command** — Someone/something ran `hermes gateway stop --all` or `systemctl --user stop hermes-gateway-*` | Check shell history (`/root/.bash_history`) for `stop` commands at ~00:55 UTC; check cron logs for watchdog scripts that call gateway stop | No special action; treat as intentional maintenance |
| 2 | **Kanban notifier I/O hang** — All gateways share the same kanban notifier thread; a disk I/O error or SQLite lock blocked shutdown cleanly | Scan pre-cascade `gateway.log` for `kanban notifier` errors, `sqlite3.OperationalError`, `I/O error` | Increase `TimeoutStopSec` to 180s; fix underlying storage; restart sequentially |
| 3 | **Cron executor deadlock propagation** — The embedded cron executor thread blocked on a shared resource, causing all gateways to be unresponsive and triggering a restart | Check if `Cron ticker started` appears without `checking jobs` in pre-cascade logs; look for executor exception tracebacks | Clear cron cache (Phase 7 Step A); restart sequentially |
| 4 | **Shared hermes-agent package update** — Background upgrade replaced `.pyc` files; running gateways detected version mismatch and exited | Check `/root/.hermes/logs/update.log` for pip/uv activity around 00:50–00:55 | Reinstall package cleanly, restart all |

**Detection rule for monitoring:**
```
ALERT: Multi-agent cascade crash detected
IF (count distinct hermes-gateway-* 'Failed' events in 120s >= 3)
THEN page on-call engineer
```

**Post-cascade verification:**
- Confirm all gateways running: `ps aux | grep 'hermes gateway run' | wc -l` == 4
- Check for recurring errors: `journalctl --since "2 min ago" | grep -E 'ERROR|Failed'`
- Verify cron resumed: `grep -E 'cron executor started|checking jobs' /root/.hermes/profiles/*/logs/gateway.log`
- If any agent still in restart loop (>3 attempts in 5 min), proceed to full reactivation (see reactivation skill)

---

## Phase 10 — Gateway Stop-Timeout Anomalies

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
