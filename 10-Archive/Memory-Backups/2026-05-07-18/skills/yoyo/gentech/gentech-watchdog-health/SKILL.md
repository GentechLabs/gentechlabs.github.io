---
name: gentech-watchdog-health
category: gentech
description: Systematic health check methodology for Gentech Hermes agents — detect crashes, auth failures, cron deadlocks, bytecode corruption, and fleet-wide correlated failures. Used by the Gentech Watchdog cron job.
triggers:
  - scheduled-cron
  - health-check-request
  - anomaly-detection
outputs:
  - status-report
  - alert-if-degraded
requirements:
  - hermes-agent-installed
  - root-access-to-vault
---

# Gentech Watchdog — Agent Health Check

## Purpose

Detect and report critical degradation across Gentech Hermes agents (YoYo, DMOB, Desmond, Gentech) before they cause production outages. This skill implements a **fleet-aware** diagnostic strategy that distinguishes isolated agent failures from systemic infrastructure issues.

**Core principle:** Check process liveness **and** functional capability. A running gateway process is not sufficient; we validate message responsiveness, cron execution, and authentication validity.

## When to Run

- **Scheduled:** Every 4 hours via cron (automated watchdog)
- **On-demand:** When Slack/Telegram reports agent unresponsiveness
- **Post-incident:** After any gateway restart or deployment

## Quick Pre-flight (30 seconds)

Gather baseline state before deep investigation:

```bash
# 1. Are gateways running?
ps aux | grep 'hermes_cli.main --profile' | grep -v grep

# 2. Last message times?
for p in yoyo dmob desmond gentech; do
  echo "[$p] $(tail -3 /root/.hermes/profiles/$p/logs/gateway.log | grep 'Sending response' | tail -1)"
done

# 3. Cron jobs enabled?
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | "\(.profile) \(.schedule.display) enabled=\(.enabled) last=\(.last_run_at)"'

# 4. Error log velocity (last 50 lines)
for p in yoyo dmob desmond gentech; do
  echo "[$p] $(tail -50 /root/.hermes/profiles/$p/logs/errors.log | grep -c ERROR)"
done
```

If all agents show **zero recent errors**, **gateway logs show responses within the last hour**, AND **latest organic sessions completed normally**, return `STATUS:OK` immediately.

### Organic Session Validation (critical)

**⚠️ Pitfall discovered (2026-05-03):** Cron sessions and watchdog subagent sessions frequently contain expected tool errors that do NOT reflect primary agent health. Always validate the agent's **latest organic session** (non-cron, initiated by human or scheduled task) to confirm the agent produces correct conclusions.

```bash
# For each agent: find latest non-cron session and verify it ended normally
for p in yoyo dmob desmond gentech; do
  echo \"=== $p ===\"

  # Find latest organic session (exclude session_cron_* files)
  latest_organic=$(ls -t /root/.hermes/profiles/$p/sessions/session_*.json 2>/dev/null | grep -v session_cron_ | head -1)

  if [ -z \"$latest_organic\" ]; then
    echo \"  WARNING: No organic sessions found (only cron/subagent activity)\"
    continue
  fi

  # Check if session ended with normal assistant response (not tool error)
  last_msg=$(tail -5 \"$latest_organic\" | grep '\"role\": \"assistant\"' | tail -1)

  if echo \"$last_msg\" | grep -q '\"tool_calls\"'; then
    echo \"  OK: Last organic session ended with tool calls (normal)\"
  elif echo \"$last_msg\" | grep -q '\"content\": \"\"' || [ -z \"$last_msg\" ]; then
    echo \"  WARNING: Last organic session empty or incomplete — agent may be stuck\"
  else
    echo \"  OK: Last organic session completed with text response\"
  fi

  # Show session timestamp
  echo \"  Latest organic: $(basename \"$latest_organic\")\"\ndone
```

**Failure signatures:**
- No organic sessions exist, only cron/watchdog → agent not responding to real requests
- Latest organic session ended with `tool_calls` pointing to us (watchdog subagent) → watchdog creating its own feedback loop
- Latest organic session empty or truncated → agent crashed mid-execution

**Note:** Session files with `.jsonl` extension and "Extra data" parse errors during bulk scanning are **false positives** — they represent multi-line JSONL records that need line-by-line parsing, not corruption. Always parse individual session files directly rather than concatenating them.

---

## Systematic Diagnostic Steps (ordered by cost → detail)

### Step 0: Watchdog Self-Check (prevent monitoring blind spots)

The watchdog itself can degrade (empty responses, session corruption, auth failures, cron executor deadlock). **Always verify self-liveness before trusting other checks** — a compromised monitor creates a blind spot.

```bash
# Check most recent watchdog session health
latest_watchdog=$(ls -t /root/.hermes/profiles/yoyo/sessions/session_cron_9ecfada01952_*.json 2>/dev/null | head -1)

if [ -n "$latest_watchdog" ]; then
  echo "Latest watchdog session: $(basename $latest_watchdog)"
  
  # Check 1: Did watchdog produce any assistant responses at all?
  assistant_count=$(grep -c '"role": "assistant"' "$latest_watchdog" 2>/dev/null || echo "0")
  echo "Assistant messages: $assistant_count"
  
  # Check 2: Any non-empty assistant responses (actual output)?
  nonempty=$(grep -c '"content": "[^"]"' "$latest_watchdog" 2>/dev/null || echo "0")
  echo "Non-empty responses: $nonempty"
  
  # Check 3: Did watchdog make tool calls (expected for health checks)?
  tool_calls=$(grep -c '"tool_calls": \[' "$latest_watchdog" 2>/dev/null || echo "0")
  echo "Tool call blocks: $tool_calls"
  
  # Failure: 0 tool calls but >5 assistant messages → watchdog stuck in loop
  # Failure: 0 non-empty responses → watchdog producing blank output
  # Failure: session file size < 1KB → watchdog crashed early
else
  echo "WARNING: No watchdog sessions found — watchdog cron may not be firing"
fi

# Cross-check: Are cron jobs actually dispatching?
# (faster than checking full DB — just look for recent output files)
find /root/.hermes/cron/output -name "*.json" -mmin -10 2>/dev/null | wc -l
```

**Failure signatures:**
- `"status": null` or missing in session JSON → watchdog never completed
- `0` non-empty assistant responses despite `assistant_count > 5` → blank output loop
- `"tool_calls_made": 0` with many messages → watchdog stuck before taking action
- Session file `< 1KB` → early crash
- **No recent cron output files** (`find /root/.hermes/cron/output -mmin -10` returns 0) → **cron executor deadlocked or auth-blocked**

**🔄 Cascading failure detection rule:** If **≥3 agents** show the same error pattern within a 10-minute window, assume **systemic issue** (auth, shared library, disk pressure) — investigate root cause first, agent-specific fixes second.

**Action:** If watchdog self-degraded, switch to **direct terminal diagnostics** (bypass hermes_cli) and flag for immediate investigation — the monitoring system is compromised.

**⚠️ Pitfall discovered (2026-05-03):** The coordination board (`11-Mess Hall/agent-coordination-board.md`) may display agents as `OFFLINE` even when gateway processes are actively running. The board reflects **reporting artifacts** (stale check-in timestamps from failed heartbeats) not actual process liveness. Always ground-truth with `ps aux | grep hermes_cli.main` before concluding agents are down. See `references/2026-05-03-coordination-board-artifact.md`.

**⚠️ Pitfall discovered (2026-05-03):** Cron sessions and watchdog subagent sessions frequently contain **expected tool errors** (auth failures, missing credentials) that do NOT reflect primary agent health. Always validate the agent's **latest organic session** (non-cron, initiated by human or real scheduled task) to confirm the agent produces correct conclusions. See Step 0a.

#### Step 0b: Cron Output Liveness Check (critical)

Cron output files are the most reliable indicator that scheduled jobs are actually executing and completing.

```bash
# Check for recent cron output across all profiles (last 10 minutes)
for agent in yoyo dmob desmond gentech; do
  recent=$(find /root/.hermes/profiles/$agent/cron/output -type f -mmin -10 2>/dev/null | wc -l)
  echo "[$agent] Recent output files (10m): $recent"
done

# If all agents show 0 recent files but gateways are running → cron executor stalled or auth-blocked
```

**Failure signature:** Zero output files in last 10–15 minutes across ≥2 agents with running gateways → cron scheduler not dispatching. Combine with Step 0 (watchdog self-check) to distinguish:
- **Watchdog degraded** → no output files for watchdog itself
- **Cron executor deadlocked** → watchdog runs but other jobs don't produce output
- **Auth-blocked fleet** → jobs run but fail before producing output (check file sizes: zero-byte files indicate early auth failure)

#### Step 0c: Cron Tick Lock Health Check (catch hung scheduler)

Each agent maintains a `.tick.lock` file in its cron directory. Lock age >60 seconds combined with absence of running job entry indicates a **stale lock** — the scheduler tick is not advancing.

```bash
# Check tick lock age and running state for each agent
for agent in yoyo dmob desmond gentech; do
  lock_file="/root/.hermes/profiles/$agent/cron/.tick.lock"
  jobs_file="/root/.hermes/profiles/$agent/cron/jobs.json"
  
  if [ -f "$lock_file" ]; then
    lock_age=$(( $(date +%s) - $(stat -c %Y "$lock_file") ))
    echo "[$agent] Lock age: ${lock_age}s"
    
    # Check if a job is actually running
    if [ -f "$jobs_file" ]; then
      running=$(python3 -c "import json; print('yes' if json.load(open('$jobs_file')).get('running') else 'no')" 2>/dev/null)
      echo "  Running job: $running"
    fi
    
    # Evaluate
    if [ $lock_age -gt 60 ] && [ "$running" = "no" ]; then
      echo "  ⚠️  STALE LOCK — cron tick hung, no active job"
    elif [ $lock_age -gt 60 ] && [ "$running" = "yes" ]; then
      echo "  ⚠️  LOCK STALE WHILE JOB RUNNING — job may be hung (>5min?)"
    else
      echo "  ✅ Lock fresh"
    fi
  else
    echo "[$agent] No lock file — cron may be disabled"
  fi
done
```

**⚠️ Pitfall discovered (2026-05-03):** A `.tick.lock` with **empty content** and age >60s is a signature of a **cascading shutdown + incomplete restart scenario**. The lock file exists but its contents are zero-length, indicating the lock was created but the process failed before writing its internal state. This pattern follows systemic failures that take down all gateways simultaneously (e.g., OAuth revocation, credential cascade). Recovery: Clear the stale lock (`rm $lock_file`) and verify the cron executor reinitializes on next tick.

**🔄 Cascading failure detection rule:** If **≥3 agents** show the same error pattern within a 10-minute window, assume **systemic issue** (auth, shared library, disk pressure) — investigate root cause first, agent-specific fixes second.

**Why:** Cron-triggered sessions and watchdog-initiated subagent calls inherit the watchdog's degraded auth state and toolchain limitations. An agent with 100 auth errors in its cron log may still be fully functional for real user interactions if its organic sessions complete successfully.

```bash
# For each agent: find latest NON-cron session and verify it ended normally
for profile in yoyo dmob desmond gentech; do
  echo "=== $profile ==="
  
  # Find latest organic session (exclude session_cron_* and session_subagent_* patterns)
  latest=$(ls -t /root/.hermes/profiles/$profile/sessions/session_*.json 2>/dev/null \
    | grep -v -E 'session_cron_|session_subagent_' | head -1)
  
  if [ -z "$latest" ]; then
    echo "  ⚠️  No organic sessions found — only cron/subagent activity"
    echo "  → Agent may not be responding to real requests"
    continue
  fi
  
  # Parse session metadata
  session_id=$(basename "$latest" .json)
  timestamp=$(echo "$session_id" | sed 's/^session_\([0-9_]\{14\}\)/\1/' | tr '_' '-')
  
  # Count messages and tool calls
  msg_count=$(python3 -c "import json; s=json.load(open('$latest')); print(len(s.get('messages',[])))" 2>/dev/null || echo "0")
  tool_count=$(python3 -c "import json; s=json.load(open('$latest')); print(sum(1 for m in s.get('messages',[]) if m.get('role')=='assistant' and m.get('tool_calls')))" 2>/dev/null || echo "0")
  status=$(python3 -c "import json; s=json.load(open('$latest')); print(s.get('status','unknown'))" 2>/dev/null || echo "parse_error")
  
  echo "  Session: $session_id"
  echo "  Status: $status, Messages: $msg_count, Tool calls: $tool_count"
  
  # Evaluate health
  if [ "$status" = "completed" ] || [ "$status" = "success" ]; then
    echo "  ✅ Organic session completed normally"
  elif [ "$msg_count" -gt 10 ] && [ "$tool_count" -eq 0 ]; then
    echo "  ❌ STUCK: >10 messages with 0 tool calls — agent looping"
  elif [ "$msg_count" -lt 3 ]; then
    echo "  ⚠️  SHORT: <3 messages — may have crashed early"
  else
    echo "  ℹ️  Status: $status — review manually"
  fi
done
```

**Failure signatures:**
- **No organic sessions exist** → agent not responding to real requests (only cron/watchdog traffic)
- **Latest organic session `status` = `error`/`aborted`/`parse_error`** → agent crashing mid-execution
- **>10 messages with 0 tool calls** → agent stuck in dialogue loop, not taking action
- **Session files with `.jsonl` extension showing "Extra data: line 2 column 1"** → **NOT corruption** — these are multi-record JSONL files that require line-by-line parsing; ignore during bulk scans
- **Latest organic session timestamp >24h old** → agent silent to real input

**Note:** Always parse individual session files directly (`json.load(open(file))`) rather than concatenating them. JSONL session logs contain one JSON object per line; attempting to parse the whole file as a single object will raise false "corruption" errors. See `references/2026-05-03-jsonl-parsing-pitfall.md`.

**🔄 Cascading failure detection rule:** If **≥3 agents** show the same error pattern within a 10-minute window, assume **systemic issue** (auth, shared library, disk pressure) — investigate root cause first, agent-specific fixes second.

---

#### Step 0a: Cron Output Liveness Check (critical)

Cron output files are the most reliable indicator that scheduled jobs are actually executing and completing.

```bash
# Check for recent cron output across all profiles (last 10 minutes)
for agent in yoyo dmob desmond gentech; do
  recent=$(find /root/.hermes/profiles/$agent/cron/output -type f -mmin -10 2>/dev/null | wc -l)
  echo "[$agent] Recent output files (10m): $recent"
done

# If all agents show 0 recent files but gateways are running → cron executor stalled or auth-blocked
```

**Failure signature:** Zero output files in last 10–15 minutes across ≥2 agents with running gateways → cron scheduler not dispatching. Combine with Step 0 (watchdog self-check) to distinguish:
- **Watchdog degraded** → no output files for watchdog itself
- **Cron executor deadlocked** → watchdog runs but other jobs don't produce output
- **Auth-blocked fleet** → jobs run but fail before producing output (check file sizes: zero-byte files indicate early auth failure)

### Step 1: Error Log Pattern Analysis (fast)

Read the last 100–200 lines of each `errors.log`. Categorize and quantify patterns.

**Core method:** For each log file, extract **only the error line prefix** (timestamp + level + message) and group identical prefixes using a frequency counter. This reveals **burst errors** (same exception repeating >3 times within 10 minutes) which indicate agent-specific degradation rather than fleet-wide issues.

```bash
# Burst detection: count identical error lines in last 200
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  log="/root/.hermes/profiles/$agent/logs/errors.log"
  
  # Extract error line prefixes (strip variable parts like request IDs)
  tail -200 "$log" 2>/dev/null | \
    sed -E 's/([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*ERROR.*/\1\t\0/' | \
    sort | uniq -c | sort -rn | head -10
done
```

**Interpretation:**
- **>5 identical errors** (same exception same module) in 200 lines = **agent-specific failure** (e.g., stuck tool call, bad API key)
- **Multiple different errors** at similar frequencies = systemic (auth, disk, network)
- **Burst clustered within a 10-minute window** — correlate with cron output timestamps to determine if it's a single bad job run

**⚠️ Pitfall discovered (2026-05-03):** ElevenLabs TTS quota exhaustion produces identical `status_code: 401, quota_exceeded` errors across all agents simultaneously. This is a **systemic third-party service failure**, not an agent-specific bug. Count identical errors across ≥3 agents to distinguish shared dependency failures from isolated agent issues. See `references/2026-05-03-elevenlabs-cascade-quota-exhaustion.md`.

---

Authentication failures block all LLM-dependent operations. Check each agent's auth state and expiry.

---

### Step 2: Cron Executor Health (critical)

All agents share the global cron executor. Check:

```bash
# Is the cron DB accessible?
ls -la /root/.hermes/cron/jobs.db  # should be >0 bytes

# Are jobs structurally valid? (check for required fields)
jq '.jobs[] | select(.profile == null or .script == null or .task_id == null) | "\(.name): profile=\(.profile) script=\(.script) task_id=\(.task_id)"' /root/.hermes/cron/jobs.json

# Are jobs actually dispatching?
jq '.jobs[] | "\\(.name) last_run=\\(.last_run_at) next=\\(.next_run_at) enabled=\\(.enabled)"' /root/.hermes/cron/jobs.json

# Any lockfiles stuck?
ls -la /root/.hermes/cron/*.lock
```

**Failure signatures:**
- `jobs.db` = 0 bytes → **FATAL** cron DB corrupted
- Any job with `profile: null`, `script: null`, or `task_id: null` → **STRUCTURAL** cron DB corruption (jobs.json malformed)
- All jobs show `last_run: null` with past-due `next_run` → executor deadlocked
- No `scheduler.log` activity in 30 min → cron thread not executing

**Recovery (structural corruption):**
```bash
# If jobs.json has missing required fields, rebuild it from canonical source:
# 1. Stop all gateways
pkill -f 'hermes_cli.main --profile'

# 2. Inspect jobs.json structure
jq '.jobs[] | {id, name, profile, script, task_id}' /root/.hermes/cron/jobs.json

# 3. If profile/script/task_id are all null, jobs.json is structurally corrupt.
#    Restore from vault backup or rebuild manually with required fields.
#    REQUIRED FIELDS: id, name, profile, script, task_id, schedule, prompt

# 4. After fixing jobs.json, restart gateways
```

**Recovery (DB corruption only, jobs.json valid):**
Stop all gateways → delete `jobs.db` → restart gateways (recreates from `jobs.json`).

---

### Step 3: Authentication Status (LLM-blocking)

All LLM-dependent cron jobs and agent tool calls fail without valid credentials.

**Primary check — Nous Portal (affects fleet-wide):**
```bash
# Check auth state per profile
for p in yoyo dmob desmond gentech; do
  echo \"=== $p ===\"
  if [ -f /root/.hermes/profiles/$p/auth.json ]; then
    # Check 1: Providers array exists and is non-empty
    providers=$(python3 -c \"import json; print(len(json.load(open('/root/.hermes/profiles/$p/auth.json')).get('providers',{})))" 2>/dev/null || echo \"0\")
    echo \"  Provider count: $providers\"
    
    # Check 2: Nous token expiry
    expiry=$(python3 -c \"import json, datetime; d=json.load(open('/root/.hermes/profiles/$p/auth.json')); np=d.get('providers',{}).get('nous',{}); print(np.get('expires_at',0))\" 2>/dev/null)
    if [ \"$expiry\" != \"0\" ]; then
      exp_dt=$(date -d \"@$expiry\" 2>/dev/null || echo \"Invalid\")
      echo \"  Nous expires: $exp_dt\"
    else
      echo \"  Nous: NO TOKEN in providers config\"
    fi
    
    # Check 3: Active provider
    active=$(python3 -c \"import json; print(json.load(open('/root/.hermes/profiles/$p/auth.json')).get('active_provider','none'))\" 2>/dev/null)
    echo \"  Active provider: $active\"
  else
    echo \"  ❌ NO auth.json\"
  fi
done

# Quick validation: run refresh script
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py 2>&1 | grep -E 'success|needs_reauth|Hermes is not logged'
```

**Secondary check — provider config:**
```bash
grep -E 'provider|api_key' /root/.hermes/profiles/*/config.yaml | grep -v '#'
```

**Failure signatures:**
- `access_token_expiry` in past or `"last_status": null` → **Need `hermes model` re-auth**
- `"needs_reauth": true` from refresh script → **Manual re-authentication required**
- Empty `providers: []` in auth.json → **Systemic auth corruption; requires full re-auth**
- `"Hermes is not logged into Nous Portal"` → **Auth completely missing**
- Missing Anthropic/ElevenLabs keys in config → **No LLM/TTS capability**
- **Cascading pattern:** Firecrawl, web_search, and all LLM tool calls fail simultaneously across all agents when Nous auth expires.

**Recovery:** Run `hermes model` for each affected profile to refresh Nous auth. Rotate any expired external API keys.

**⚠️ Systemic OAuth cascade failure pattern (2026-05-03):** When Nous Portal OAuth refresh token expires/revoked, ALL agents sharing that credential set fail simultaneously with correlated signatures:

**Tier 1 — Immediate error spike (within 5 min):**
- Gateway logs: `Firecrawl client initialization failed: missing direct config and tool-gateway auth` (every agent)
- Cron jobs: `RuntimeError: Refresh session has been revoked` (all LLM-dependent jobs)
- Refresh script: Returns `{ "success": false, "needs_reauth": true }` repeatedly

**Tier 2 — Service degradation (15–30 min):**
- All Mess Hall scheduled delivery stops (pre-shift/mid-shift/post-shift)
- Error counts in each agent's `errors.log` spike 20–50 lines in <10 min
- `auth.json` shows `providers: []` (empty) — token fully evicted from credential pool
- "Nous OAuth Proactive Refresh" cron job may disappear from `cron/jobs.json` (structural corruption)

**Tier 3 — Fleet impact (>30 min):**
- No Telegram responses from any agent (all tool calls blocked)
- Watchdog self-degradation (cannot re-auth via cron; requires interactive TTY)
- Coordination board shows all agents `OFFLINE` despite gateway processes running

**Root cause:** Refresh token revoked server-side; automated refresh cannot recover. Requires manual `hermes model` interactive OAuth in a TTY session.

**Diagnostic checklist:**
```bash
# 1. Check auth.json providers field (empty = systemic)
for p in yoyo dmob desmond gentech; do
  python3 -c "import json; d=json.load(open('/root/.hermes/profiles/$p/auth.json')); print('$p providers:', len(d.get('providers',{})))"
done

# 2. Verify refresh script fails identically across fleet
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
python3 /root/.hermes/profiles/yoyo/scripts/refresh_nous_oauth.py 2>/dev/null || true

# 3. Check cron registry integrity
hermes cron list | grep -i 'nous\|oauth\|watchdog\|mess hall' || echo "CRON REGISTRY SUSPECT"

# 4. Confirm no pending device flow tokens blocking re-auth
find /root/.hermes -name "*device*" -o -name "*auth_code*" 2>/dev/null | head -5
```

See `references/2026-05-03-nous-oauth-cascade-failure.md` for full timeline, root cause analysis, and recovery playbook.

---

### Step 4: Gateway Process & Resource Health

Even if processes run, they may be stuck.

```bash
# Process list with resource usage
ps aux | grep 'hermes_cli.main --profile' | grep -v grep

# Check for sustained high-CPU (>50% for >1m) → infinite retry loop
top -b -n1 | grep hermes
```

**Failure signatures:**
- CPU >70% for 5+ minutes with minimal log output → **stuck retry loop**
- Process repeatedly SIGTERM'd in logs → **crash-restart cycle** (check `gateway.log` for `exit code 1`)
- Memory leak (RSS steadily growing across restarts) → **needs restart + cache clear**

**Recovery:** Stop gateway, clear caches (`find /usr/local/lib/hermes-agent -name "*.pyc" -delete`), restart.

---

### Step 5: Bytecode & Asset Corruption

Hermes uses compiled Python bytecode. Corruption breaks imports globally.

```bash
# Check for truncated .pyc files (< expected size)
find /usr/local/lib/hermes-agent/agent/__pycache__ -name "*.pyc" -size -50k -exec ls -la {} \;

# Recompute expected size: compare .pyc to .py source
for f in /usr/local/lib/hermes-agent/agent/__pycache__/*.pyc; do
  src="${f%.cpython-311.pyc}.py"
  if [ -f "$src" ]; then
    pyc_size=$(stat -c%s "$f")
    py_size=$(stat -c%s "$src")
    if [ $pyc_size -lt $((py_size/2)) ]; then
      echo "CORRUPT: $f ($pyc_size vs $py_size)"
    fi
  fi
done
```

**Failure signature:** `EOFError: marshal data too short` in logs + `.pyc` significantly smaller than source `.py`.

**Recovery:** `find /usr/local/lib/hermes-agent -name "*.pyc" -delete` → restart gateways (rebuilds caches).

---

### Step 6: Database Integrity

Kanban and state DB corruption prevents task scheduling.

```bash
# Verify SQLite DBs
for p in yoyo dmob desmond gentech; do
  db="/root/.hermes/profiles/$p/kanban.db"
  if [ -f "$db" ]; then
    sqlite3 "$db" "PRAGMA integrity_check;" 2>&1 | grep -v ok && echo "CORRUPT: $db"
  fi
done

# Check global cron DB
sqlite3 /root/.hermes/cron/jobs.db "PRAGMA integrity_check;" 2>&1
```

**Failure signature:** `database disk image is malformed` or `PRAGMA integrity_check` returns error.

**Recovery:** Restore from backup if available, or delete (Kanban will recreate; cron DB must be rebuilt from `jobs.json`).

---

### Step 7: Connection & Liveness

Confirm agents are actually responding to Telegram.

```bash
# Count recent responses (last hour)
for p in yoyo dmob desmond gentech; do
  count=$(grep -c 'Sending response' /root/.hermes/profiles/$p/logs/gateway.log)
  last=$(grep 'Sending response' /root/.hermes/profiles/$p/logs/gateway.log | tail -1 | cut -d' ' -f1-2)
  echo "[$p] $count responses total, last: $last"
done
```

**Failure signature:** No responses in last 60 minutes despite gateway process running → **agent stuck/idle**.

---

## Common Failure Patterns (Fleet-Wide)

| Pattern | Signature | Likely Root Cause | Recovery |
|---------|-----------|-------------------|----------|
| **Auth cascade** | All agents: `Refresh session has been revoked` OR `needs_reauth: true` in refresh script output; Firecrawl errors across fleet | Nous Portal token expired/revoked | Run `hermes model` per profile; re-run refresh script |
| **OAuth cascade failure** | All agents: `auth.json` shows `providers: []`, refresh script returns `needs_reauth: true`, Firecrawl/web tool errors fleet-wide, cron jobs failing with `Hermes is not logged into Nous Portal` | Refresh token revoked server-side; device flow rate-limited; requires interactive TTY re-auth | Run `hermes model` in TTY; if rate-limited, wait 15 min; verify with refresh script; restart cron registry |
| **Cron executor deadlock** | `jobs.db` = 0 bytes; all jobs `last_run: null` with past-due `next_run` | Scheduler thread crashed or DB locked | Stop gateways → truncate `jobs.db` → restart gateways |
| **Bytecode plague** | `EOFError: marshal data too short` across multiple profiles | Shared library `.pyc` truncated during update | Purge `/usr/local/lib/hermes-agent/__pycache__/` recursively |
| **Crash-restart storm** | 30+ `SIGTERM`/`exit code 1` in gateway.log per hour | Resource exhaustion (disk/memory) or credential panic | Clear disk space, rotate keys, restart clean |
| **Correlated silence** | No Telegram responses for 45+ min but gateways running | Auth + cron deadlock combo → no tasks executed | Re-auth + cron DB repair together |

**⚠️ Cascading failure detection rule:** If **≥3 agents** show the same error pattern within a 10-minute window, assume systemic issue (auth, shared library, disk pressure) — investigate root cause first, agent-specific fixes second.

**See `references/2026-05-03-nous-oauth-cascade-failure.md` for the full OAuth cascade incident timeline, diagnostic checklist, and step-by-step recovery playbook.**

---

## OUTPUT FORMAT (STRICT)

The Watchdog's output **MUST** be one of these two exact strings — no markdown, no explanation, no headers, no extra whitespace:

- **Healthy fleet:** `STATUS:OK`
- **Degradation detected:** `🚨 Watchdog Alert: <single-line summary starting with capital letter, no line breaks>`

** NEVER:**
- Never add sections, bullet points, or formatting
- Never explain your reasoning or include analysis
- Never output `STATUS:OK` if any agent is degraded
- Never use `STATUS:DEGRADED` — that's a log-only internal state; the user only sees OK or Alert
- Never say "all systems nominal" or other verbose status

**User preference:** "Be quiet. Only speak up when something breaks." The alert line should be concise but descriptive enough to triage (e.g., `🚨 Watchdog Alert: Auth revoked fleet-wide — all cron jobs failing` or `🚨 Watchdog Alert: YoYo stuck in empty-response loop, 0 tool calls`).

---

## Decision Matrix: SILENT vs ALERT

| Condition | Output |
|-----------|--------|
| All gateways responding, cron jobs running, <5 errors in last 100 lines | `STATUS:OK` |
| Single agent with <50 errors, last response <30 min | `STATUS:DEGRADED` (log only, no alert) |
| ≥1 agent with no responses >60 min OR cron executor deadlocked OR auth revoked fleet-wide | `🚨 Watchdog Alert: <summary>` |
| Global infrastructure failure (bytecode corruption, DB corruption, disk full) | `🚨 Watchdog Alert: FLEET-WIDE FAILURE — <details>` |

**Never** send `STATUS:OK` with any of:
- Overdue cron jobs
- Auth failures >10 in last 100 lines
- Bytecode corruption present
- Gateway crash cycles >5 in last hour
- Watchdog's own sessions showing empty assistant responses (self-degradation)

---

## Recovery Playbook (Quick Reference)

1. **Auth revoked:** `hermes model` (re-authenticate Nous Portal)
2. **Cron DB dead:** Stop gateways → `> /root/.hermes/cron/jobs.db` → restart gateways
3. **Bytecode bad:** `find /usr/local/lib/hermes-agent -name "*.pyc" -delete` → restart
4. **Disk full:** `apt-get clean && journalctl --vacuum-time=1d` → clear /tmp
5. **Gateway crashing:** Check `gateway.log` for exit code; rotate API keys; restart
6. **Database malformed:** Restore from backup or delete (accept data loss for kanban; cron rebuild from jobs.json)

---

## Reference Commands & Paths

**Log locations:**
- Error logs: `/root/.hermes/profiles/<profile>/logs/errors.log`
- Gateway logs: `/root/.hermes/profiles/<profile>/logs/gateway.log`
- Agent logs: `/root/.hermes/profiles/<profile>/logs/agent.log`

**Cron files:**
- Jobs DB: `/root/.hermes/cron/jobs.json` (source of truth)
- Executor DB: `/root/.hermes/cron/jobs.db` (runtime state, can be 0 bytes if corrupted)
- Scheduler log: `/root/.hermes/cron/scheduler.log` (if exists)

**Process names:**
- Gateway: `python -m hermes_cli.main --profile <profile> gateway run`

**Agent profiles:** `yoyo`, `dmob`, `desmond`, `gentech`

---

## Future Automation Ideas

- [ ] Auto-reauth watch dog: detect `AuthError` → run `hermes model` unattended
- [ ] Cron DB watchdog: monitor `jobs.db` size; alert on 0 bytes
- [ ] Bytecode integrity checker: periodic `.pyc` vs `.py` size comparison
- [ ] Graceful degradation: if LLM auth fails, route to fallback provider automatically

## Diagnostic Scripts

The following helper scripts are available for rapid troubleshooting:

- `scripts/enumerate_failed_cron_jobs.py` — Aggregates cron job failure counts and 401 error velocities across all agent logs. Run with:
  ```bash
  python3 /root/.hermes/profiles/yoyo/skills/gentech/gentech-watchdog-health/scripts/enumerate_failed_cron_jobs.py
  ```
  Output includes sorted failed job list and per-agent 401 tallies. Useful for quickly identifying systemic vs isolated failures and tracking error velocity during incidents. Integrate into Step 1 pre-flight for quantitative severity.
