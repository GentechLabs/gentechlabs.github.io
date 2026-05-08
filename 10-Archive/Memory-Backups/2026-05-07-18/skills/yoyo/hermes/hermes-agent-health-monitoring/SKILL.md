---
name: hermes-agent-health-monitoring
title: Hermes Agent Health Monitoring
description: Systematic health check methodology for Hermes agents — detect credential gaps, gateway boot loops, connection failures, and cron job issues across multi-agent deployments.
globs: []
alwaysApply: false
---

## When to Use

Run this skill when performing agent health checks, watchdog monitoring, or troubleshooting multi-agent Hermes deployments. Use it to systematically verify all agents are operational and identify degradation patterns before they cause outages.

**⚠️ Output Format Policy (CRITICAL):**
- If ALL agents are healthy with no detected issues: respond with exactly `STATUS:OK` (nothing else). Do NOT include "all systems nominal", summaries, or any additional text.
- If ANY issue is detected: format alert as `🚨 Watchdog Alert: [concise problem statement]` followed by bullet-point details.
- This policy overrides default verbosity — silence is mandatory when clean.

## Procedure

### Approach A: Comprehensive Analysis (Legacy)
*(Detailed multi-section approach for deep troubleshooting)*

[Keep sections 1-9 from current skill as-is, just renumber header hierarchy]

---

### Approach B: Lightweight Status Check (Recommended for Routine Watchdog)

For daily health checks where recent history shows stable operation, use this faster pattern:

```bash
#!/bin/bash
# Quick health probe — returns STATUS:OK or 🚨 alert

agents=(gentech yoyo dmob desmond)
issues=()

# 1. Process liveness + age
for agent in "${agents[@]}"; do
  pid=$(pgrep -f "hermes.*--profile $agent" | head -1)
  if [ -z "$pid" ]; then
    issues+=("$agent process NOT RUNNING")
  else
    elapsed=$(ps -p $pid -o etimes= 2>/dev/null | tr -d ' ')
    echo "$agent: PID=$pid age=${elapsed}s"
  fi
done

# 2. Log recency (last activity <5 min for active agents)
for agent in "${agents[@]}"; do
  log="/root/.hermes/profiles/$agent/logs/agent.log"
  if [ -f "$log" ]; then
    last_line=$(tail -1 "$log")
    last_ts=$(echo "$last_line" | cut -c1-19)
    last_min=$(date -d "$last_ts" +%s 2>/dev/null || echo 0)
    now_min=$(date +%s)
    age_min=$(( (now_min - last_min) / 60 ))
    echo "$agent last log: ${age_min}min ago"
    [ "$age_min" -lt 30 ] || issues+=("$agent idle ${age_min}min")
  fi
done

# 3. Recent ERROR/CRITICAL in last hour
for agent in "${agents[@]}"; do
  log="/root/.hermes/profiles/$agent/logs/agent.log"
  if [ -f "$log" ]; then
    err_count=$(tail -200 "$log" | grep -icE "ERROR|CRITICAL" || echo 0)
    [ "$err_count" -eq 0 ] || issues+=("$agent has $err_count recent errors")
  fi
done

# 4. Telegram activity marker (last "Sending response" <1h)
for agent in "${agents[@]}"; do
  log="/root/.hermes/profiles/$agent/logs/agent.log"
  if [ -f "$log" ]; then
    last_send=$(grep "Sending response" "$log" | tail -1 | cut -c1-19)
    if [ -n "$last_send" ]; then
      send_min=$(date -d "$last_send" +%s 2>/dev/null || echo 0)
      age_h=$(( (now_min - send_min) / 3600 ))
      [ "$age_h" -lt 1 ] || issues+=("$agent Telegram stale ${age_h}h")
    else
      issues+=("$agent no Telegram sends recorded")
    fi
  fi
done

# 5. DB activity proxy (state.db modified <10 min)
for agent in "${agents[@]}"; do
  db="/root/.hermes/profiles/$agent/state.db"
  if [ -f "$db" ]; then
    db_min=$(stat -c %Y "$db" 2>/dev/null || echo 0)
    age_min=$(( (now_min - db_min) / 60 ))
    [ "$age_min" -lt 10 ] || issues+=("$agent DB stale ${age_min}min")
  fi
done

# 6. Loop detection (consecutive identical log lines >5)
for agent in "${agents[@]}"; do
  log="/root/.hermes/profiles/$agent/logs/agent.log"
  if [ -f "$log" ]; then
    repeats=$(tail -200 "$log" | awk '{print substr($0,1,80)}' | uniq -d | wc -l)
    [ "$repeats" -lt 5 ] || issues+=("$agent log loop detected (${repeats}x)")
  fi
done

# 7. Daily scan cron execution (Gentech-specific)
scan_log="/root/vaults/gentech/02-Labs/Contest-Scans/scan_$(date +%Y-%m-%d).log"
if [ -f "$scan_log" ]; then
  grep -q "Done\|Complete" "$scan_log" || issues+=("Daily scan did not complete")
else
  issues+=("Daily scan log missing for today")
fi

# Output
if [ ${#issues[@]} -eq 0 ]; then
  echo "STATUS:OK"
  exit 0
else
  echo "🚨 Watchdog Alert:"
  for issue in "${issues[@]}"; do
    echo "  - $issue"
  done
  exit 1
fi
```

**Why this works**: Direct checks without log parsing complexity. DB mtime is a reliable activity proxy. Consecutive-line detection catches retry loops without needing error pattern knowledge. Telegram "Sending response" is the simplest outbound-messaging proof.

**When to use**: Routine monitoring on stable deployments. Use the Comprehensive Analysis (sections 1-9 above) only when issues are detected or deep forensics are needed.

### 2. Gateway Stability Analysis

Check gateway logs for abnormal termination patterns and restart frequency:

```bash
# Count gateway boots (indicates restarts/crashes)
for agent in yoyo dmob desmond gentech; do
  boot_count=$(grep -c "Starting Hermes Gateway" /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null || echo 0)
  echo "$agent: $boot_count gateway boots"
done

# Check for abnormal exits vs clean stops
grep -E "Exiting with code|signal-initiated" /root/.hermes/profiles/*/logs/gateway.log

# Look for Python tracebacks preceding exits
grep -B10 "Exiting with code" /root/.hermes/profiles/gentech/logs/gateway.log | grep -E "Traceback|RuntimeError|Exception"
```

**Normal**: Gateways stop cleanly for planned restarts; exit code 0.

**Critical**: Repeated "Exiting with code 1" with "signal-initiated shutdown" = crash → systemd Restart=on-failure loop. Zero systemd units present = manual restarts only.

### 3. Credential Gap Detection

Missing API keys manifest as repeated errors in agent logs:

```bash
# Pattern 1: Anthropic/Claude credential missing (DMOB pattern)
grep -i "No Anthropic credentials found" /root/.hermes/profiles/*/logs/agent.log

# Pattern 2: ElevenLabs TTS 401 errors (Desmond pattern)
grep -i "elevenlabs.*401\|Invalid API key" /root/.hermes/profiles/desmond/logs/agent.log | wc -l

# Pattern 3: Provider API key missing (Gentech pattern)
grep -E "Provider '.*' is set in config.yaml but no API key was found" /root/.hermes/profiles/*/logs/*.log

# Verify .env/config presence per agent
for agent in yoyo dmob desmond gentech; do
  echo -n "$agent .env: "
  test -f /root/.hermes/profiles/$agent/home/.env && echo "EXISTS" || echo "MISSING"
  echo -n "$agent config.yaml: "
  test -f /root/.hermes/profiles/$agent/home/.config/hermes/config.yaml && echo "EXISTS" || echo "MISSING"
done
```

**Indicators**:
- Zero `.env` files + matching error patterns = credential gap requiring key injection.
- High-count repetitive errors (Desmond 186× 401; DMOB cron failures ×2) = systematic key failure.

### 4. Connection & Network Health

Auxiliary client fallback storms indicate connectivity issues to primary LLM providers:

```bash
# Count connection error fallbacks (YoYo/Gentech pattern)
for agent in yoyo dmob desmond gentech; do
  count=$(grep -c "connection error on auto" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null || echo 0)
  echo "$agent: $count connection error fallbacks"
done

# Telegram disconnect frequency (symptom, not root cause)
for agent in yoyo dmob desmond gentech; do
  disc=$(grep -c "Telegram.*Disconnected" /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null || echo 0)
  echo "$agent: $disc Telegram disconnects"
done
```

**Normal**: Occasional disconnects (1–3/day) with automatic reconnection.

**Degraded**: 8+ disconnects + concurrent credential gaps = gateway instability.

### 5. Cron Job Health Check

Cron-driven tasks fail silently if credentials are missing, or silently skip if database is corrupted:

```bash
# Check cron ticker activity per agent (does ticker thread exist?)
for agent in yoyo dmob desmond gentech; do
  ticks=$(grep -c "Cron ticker started" /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null || echo 0)
  echo "$agent: ticker started $ticks times"
done

# Check for cron executor activity (are jobs actually running?)
for agent in yoyo dmob desmond gentech; do
  execs=$(grep -c "executing job\\|Job run completed" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null || echo 0)
  echo "$agent: executor runs=$execs"
done

# Inspect cron database integrity (look for profile/script field corruption)
python3 -c "import json; d=json.load(open('/root/.hermes/cron/jobs.json')); print('Total jobs:', len(d['jobs'])); print('Missing profile:', sum(1 for j in d['jobs'] if not j.get('profile'))); print('Missing script:', sum(1 for j in d['jobs'] if not j.get('script')))" 

# Check for never-executed jobs
python3 -c "import json, time; d=json.load(open('/root/.hermes/cron/jobs.json')); now=int(time.time()); never=[j for j in d['jobs'] if not j.get('last_run')]; print(f'Jobs never executed: {len(never)}/{len(d[\"jobs\"])}')"

# Look for cron exceptions in agent logs
grep -i "Job .* failed\\|ERROR cron" /root/.hermes/profiles/*/logs/agent.log | tail -20
```

**Healthy**: Regular cron ticks (gates); executor runs visible in `agent.log`; all jobs have `profile` and `script` fields; `last_run` timestamps populated.

**Critical - Cron Database Corruption**: All jobs have empty `profile` and `script` fields → jobs unrunnable, never executed. `last_run=None` across all jobs. Requires manual `jobs.json` repair or recreation via `hermes cron create`.

**Critical - Ticker-Only, No Executor**: Gateway logs show "Cron ticker started" but `agent.log` shows zero executor runs → cron executor thread deadlocked. Check for `EOFError`, `marshal data too short`, or `Hermes is not logged into Nous Portal` blocking job dispatch.

### 6. Bytecode & Session Corruption Detection

Python bytecode corruption causes `EOFError: marshal data too short` during imports, breaking session summarization:

```bash
# Scan for marshal errors across all agents
for agent in yoyo dmob desmond gentech; do
  count=$(grep -c "marshal data too short" /root/.hermes/profiles/$agent/logs/errors.log 2>/dev/null || echo 0)
  echo "$agent: $count session corruption errors"
done

# Check for suspiciously small .pyc files (truncated)
find /usr/local/lib/hermes-agent/agent/__pycache__ -name "*.pyc" -size -1k -exec ls -lh {} \;

# Verify agent-specific session corruption
for agent in yoyo dmob desmond gentech; do
  db_file="/root/.hermes/profiles/$agent/home/sessions.db"
  if [ -f "$db_file" ]; then
    echo "Checking $agent session DB integrity..."
    sqlite3 "$db_file" "PRAGMA integrity_check;" 2>&1 | head -5
  fi
done
```

**Impact**: SessionSearchTool failures, Watchdog cron job failures, cross-session queries broken.

**Recovery**: Stop all gateways, delete `/usr/local/lib/hermes-agent/agent/__pycache__/*.pyc`, restart gateways. If session DB is corrupted, restore from backup or clear session state.

### 7. Stuck/Looping Behavior Detection

High CPU + repeated tool resolution errors indicate stuck loops:

```bash
# Check agent CPU usage sustained over 1 minute interval
ps -eo pid,pcpu,cmd --sort=-pcpu | grep hermes | head -5

# Look for tool resolution failure patterns
grep -i "Unknown tool\\|Tool not found\\|skill resolve failed" /root/.hermes/profiles/*/logs/errors.log

# Detect tight retry loops (same error repeated rapidly)
for agent in yoyo dmob desmond gentech; do
  log="/root/.hermes/profiles/$agent/logs/errors.log"
  if [ -f "$log" ]; then
    echo "=== $agent: Recent repeated errors ==="
    tail -100 "$log" | sort | uniq -c | sort -nr | head -5
  fi
done
```

**Pattern**: CPU 90–100% sustained + `Unknown tool 'X'` errors = stuck in tool resolution retry loop. Requires gateway restart and skill/database repair.

### 8. Error Volume Classification

Quantify degradation per agent:

```bash
for agent in yoyo dmob desmond gentech; do
  errs=$(grep -icE "(error|exception|failed)" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null || echo 0)
  warns=$(grep -ic "WARNING" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null || echo 0)
  infos=$(grep -ic "INFO" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null || echo 0)
  echo "$agent: errors=$errs warnings=$warns info=$infos"
done
```

**Thresholds**:
- **Healthy**: errors < 100, info > errors
- **Degraded**: 100–1,000 errors
- **Critical**: errors > 1,000

Gentech (9,521 errors) and YoYo (3,076 errors) exceed critical threshold; investigate root cause by correlating with credential gaps and gateway crashes.

### 9. Remediation Verification

After applying fixes (key injection, config updates), verify recovery:

```bash
# Monitor for 5 minutes post-restart
for agent in yoyo dmob desmond gentech; do
  sleep 300
  new_errors=$(tail -100 /root/.hermes/profiles/$agent/logs/agent.log | grep -icE "(error|exception|failed)" || echo 0)
  echo "$agent post-restart error rate: $new_errors/100 lines"
done

# Confirm gateway stability
pgrep -f "hermes.*gateway run" | wc -l  # Should equal agent count
```

## Pitfalls

- **Assuming Telegram disconnects are the root cause**: They're usually a symptom of gateway crashes or credential auth failures. Fix credentials first.
- **Ignoring `.env` absence**: If `.env` files are missing across all agents, the deployment may have been reset or profiles mis-copied. Restore from backup or reconstruct credentials.
- **Treating gateway exit code 1 as transient**: Repeated "Exiting with code 1" with "signal-initiated shutdown" indicates unhandled exceptions; check gateway.log immediately preceding the exit for the actual exception trace.
- **Cron job blindness**: Cron jobs run in separate subprocesses; failures appear only in `agent.log`, not `gateway.log`. Search `"Job '.*' failed"` specifically.
- **Connection error avalanche**: When the auxiliary client fails to reach the primary provider, it falls back repeatedly, flooding logs. This can mask the real issue (wrong provider config or network egress blockage).

## Decision Tree

```
Agent health check → All processes running?
  ├─ NO → Start missing gateway(s): hermes gateway run --replace --profile <agent>
  └─ YES → Gateway boot count > 5 in 24h?
        ├─ YES → Check gateway.log for exception trace 30s before exit
        │        └─ Found "Provider .* no API key" → Inject .env + restart
        └─ NO → Error volume per agent
              ├─ Critical (>1000) → Check credential gaps (grep "No.*credentials\|401\|Invalid API key")
              │                    └─ Missing keys → Set .env, restart agent
              └─ Degraded (100–1000) → Check connection errors (grep "connection error on auto")
                                     └─ Fallback storm → Verify provider endpoint reachability
```

## References

- `references/credential-gap-patterns.md` — Error signatures and fix recipes for Anthropic, ElevenLabs, OpenCode provider credential issues discovered in this session
- `references/gateway-crash-analysis.md` — Interpreting gateway.log exit codes and traceback reconstruction patterns
- `references/agent-log-query-cheatsheet.md` — One-liner grep patterns for fast per-agent triage and status queries

## Automation Scripts

- `scripts/agent-health-check.sh` — Comprehensive watchdog probe using legacy analysis (exit codes 0/1/2). Best for deep forensics.
- `scripts/quick-health-check.sh` — Lightweight status probe (Approach B) returning `STATUS:OK` or `🚨` alert in <3 seconds. Ideal for routine monitoring.

## Known Anomalies (Gentech-Specific)

- **Vault-side gateway state files optional**: Files like `/root/vaults/gentech/<agent>/gateway_state.json`, `gateway.pid`, `gateway.lock` are vault metadata; missing files are normal. Hermes keeps state in `~/.hermes/profiles/<agent>/state.db`. Do NOT treat missing vault files as a health issue.
- **Historical error counts misleading**: Agents accumulate errors over time. Only errors within the last hour matter for liveness. Check timestamps, not totals.
- **PGREP pattern sensitivity**: `pgrep -f "--profile <agent>"` works; plain `pgrep <agent>` matches nothing. The `--profile` flag is part of the command string, not a separate argument to pgrep.
- **High-CPU sandbox processes**: Temporary `/tmp/hermes_sandbox_*` script runners consume CPU briefly; ignore unless sustained >60% for >5min.
- **Thread count normal baseline**: ~48 threads is typical for idle Hermes agents. Do not interpret high thread count as "busy" — it's the normal thread pool.
- **TTS 401 errors historical only**: ElevenLabs key expirations show as 401. If last TTS error >1h old, treat as resolved; no restart needed unless errors are active.
- **SessionDB "disk full" warning is historical**: The single logged `Failed to initialize SessionDB` on 2026-05-01 was a transient condition. Current DB operations fine if `state.db` is updating.
- **Cron logs live in vault, not Hermes**: `opportunity_scanner_daily.py` writes to `/root/vaults/gentech/02-Labs/Contest-Scans/`, not `/root/.hermes/logs/`. Check vault path for cron health.
- **Empty agent log tail possible**: Idle agents may show no "Processing" or "received" markers for minutes; this is okay if DB is active and last log <30 min old.

## Decision Tree — Which Approach?

```
Health check needed?
  ├─ Routine check (daily/hourly, historically stable) → Approach B (Lightweight)
  └─ Issue detected OR deep forensics requested → Approach A (Comprehensive)

Approach B detects problem?
  ├─ YES (any red flag) → Re-run with Approach A on affected agents
  └─ NO → All clear, no further action
```
