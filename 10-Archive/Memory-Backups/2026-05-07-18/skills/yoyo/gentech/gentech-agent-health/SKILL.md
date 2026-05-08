---
name: gentech-agent-health
description: Systematic health check methodology for Gentech Hermes agents (YoYo, DMOB, Desmond, Gentech)
version: 1.1.0
author: YoYo (Gentech Strategies)
license: MIT
---

# Gentech Agent Health Check

Specialized health monitoring for the 4 Gentech Hermes agents across gateway integrity, kanban DB health, Telegram connectivity, cron job execution, and response latency.

## When to Use

- After agent restarts or system updates
- When response times degrade
- When cron jobs appear stuck or overdue
- Following network/disk issues
- Periodic proactive monitoring (daily/weekly)

## Prerequisites

- Access to agent profile directories at `/root/.hermes/profiles/<agent>/`
- Python 3.11+ with sqlite3 module
- `ps` and `lsof` system utilities

## Health Check Procedure

### 0. Cron Executor Liveness Check (CRITICAL FIRST STEP)

Before checking individual agents, verify the cron subsystem is actually dispatching jobs:

**Step A: Check for active cron daemon (there is no separate hermes-cron process):**
```bash
ps aux | grep -E 'hermes.*cron' | grep -v grep
```
Expected output: **nothing** — the cron ticker runs inside each gateway process. Presence of a standalone hermes-cron process indicates a misconfiguration.

**Step B: Verify ticker is alive in each gateway:**
```bash
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep -E 'Cron ticker started' /root/.hermes/profiles/$agent/logs/gateway.log | tail -1
done
```
Look for recent timestamps (within last 5 minutes). Missing ticker start = cron subsystem not running.

**Step C: Verify actual job dispatches (not just ticker):**
```python
import json, re, os
from datetime import datetime

base = '/root/.hermes/profiles'
for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    # Check jobs.json for last_run_at
    with open(f'{base}/{agent}/cron/jobs.json') as f:
        jobs = json.load(f).get('jobs', [])
    
    # Check gateway.log for actual dispatch events (best effort)
    log_path = f'{base}/{agent}/logs/gateway.log'
    with open(log_path) as f:
        log_content = f.read()
    
    dispatches = len(re.findall(r'dispatching cron job|job started', log_content, re.I))
    ticker_starts = len(re.findall(r'Cron ticker started', log_content))
    
    # Check freshness via cron output directory (MOST RELIABLE)
    out_dir = f'{base}/{agent}/cron/output/'
    if os.path.exists(out_dir):
        output_files = []
        for root, dirs, files in os.walk(out_dir):
            for fname in files:
                if fname.endswith('.md'):
                    fp = os.path.join(root, fname)
                    output_files.append((os.path.getmtime(fp), fp))
        
        if output_files:
            newest = max(output_files, key=lambda x: x[0])
            age_min = (datetime.now().timestamp() - newest[0]) / 60
            print(f"{agent.upper()}:")
            print(f"  Jobs in registry: {len(jobs)}")
            print(f"  Ticker start events: {ticker_starts}")
            print(f"  Total dispatches (log): {dispatches}")
            print(f"  Latest cron output: {age_min:.0f}min old")
            
            if age_min > 65:
                print(f"  ❌ CRON STALLED — no output in >65 minutes")
            elif age_min > 25:
                print(f"  ⚠️  STALE — output >25min old")
            else:
                print(f"  ✅ FRESH — cron executing")
        else:
            print(f"{agent.upper()}: No cron output files — executor may be dead")
    else:
        print(f"{agent.upper()}: No cron output directory")
    
    # Cross-check with jobs.json last_run_at
    never_run = [j for j in jobs if j.get('last_run_at') is None]
    stale_jobs = [j for j in jobs if j.get('last_run_at') and 
                  (datetime.now() - datetime.fromisoformat(j['last_run_at'])).total_seconds() > 7200]
    if never_run:
        print(f"  ⚠️ NEVER RUN: {len(never_run)}/{len(jobs)} jobs show last_run_at=null")
    if stale_jobs:
        print(f"  ⚠️ STALE: {len(stale_jobs)} jobs last run >2h ago")
```

**Deadlock signature:** Ticker start events exist but `dispatches == 0` OR all jobs show `last_run_at == null` for >2 hours despite being enabled and past their schedule. The cron executor thread is not调度 jobs despite ticker running.

**Complete subsystem failure (worse than deadlock):** No "Cron ticker started" events at all in gateway.log for >10 minutes after gateway boot. This indicates the cron module failed to initialize. Check for `import hermes_cron` errors in gateway.log. Fix: ensure cron support installed, set `cron_enabled: true` in config.yaml, and restart gateway.

**Immediate action if deadlocked:** Restart all gateways (`hermes -p <profile> gateway restart`) and verify `hermes cron list` shows active schedules. If jobs.json shows corrupt entries (missing `profile` or `script` fields), repair via `hermes cron add` or restore from backup.

**Output file freshness rule:** Cron output files (`.md`) are the ground-truth indicator of job execution. Gateway.log dispatch records are helpful but can be missing if logging fails. Always prioritize output file timestamps.

**May 4, 2026 observation:** YoYo produced 27 watchdog outputs in 2h (fresh), while DMOB produced only 1 output 1.9h old and Desmond 1 output 0.9h old — indicates per-agent cron executor variance, not fleet-wide deadlock.

### 1. Agent Process Verification

Confirm all 4 agents are running:

```bash
ps aux | grep 'hermes.*gateway run'
```

Expected: 4 processes with profiles `yoyo`, `dmob`, `desmond`, `gentech`.

### 2. Gateway Log Freshness

Check each agent's `logs/gateway.log` for recent activity:

```python
import os, glob
from datetime import datetime

base = '/root/.hermes/profiles'
for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    log = f'{base}/{agent}/logs/gateway.log'
    stat = os.stat(log)
    age_sec = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds()
    print(f"{agent}: gateway.log last write {age_sec/60:.0f}min ago")
```

**Thresholds:**
- `< 5 min`: ✅ Healthy
- `5–30 min`: ⚠️ Stale (check for idle periods)
- `> 30 min`: ❌ STALLED (gateway not writing logs)

### 2a. Authentication Provider Verification

**Why:** A misconfigured or missing `active_provider` prevents agents from dispatching to their LLM backend, causing silent task failures. Cron jobs that depend on Nous Portal may fail with `No access token found` or `Refresh session has been revoked` even when the provider appears configured.

**Check:** Verify each agent's `auth.json` contains a valid, active provider assignment:

```python
import json

base = '/root/.hermes/profiles'
for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    with open(f'{base}/{agent}/auth.json') as f:
        auth = json.load(f)
    active = auth.get('active_provider', '')
    nous_ok = 'nous' in active.lower()
    print(f"{agent.upper()}: active_provider={active!r}, OK={nous_ok}")
```

**Failure signature:**
- `active_provider: null` or `active_provider: None` → agent cannot select a model provider
- `active_provider` set but credential pool missing the provider key → auth incomplete
- `active_provider` set to a provider not in credential pool → runtime errors

**Gentech-specific bug (May 3, 2026):** Gentech's `auth.json` showed `active_provider: None` while all other agents had `nous`. This prevented Gentech from executing any Nous-dependent tasks. Fix: set `"active_provider": "nous"` in `/root/.hermes/profiles/gentech/auth.json` and restart gateway.

**Post-fix validation:**
```python
# 1. Verify active_provider is set
# 2. Check Nous token exists in credential pool under key 'nous'
# 3. Run refresh script: python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
#    Expected: {"success": true, "needs_reauth": false}
# 4. Restart gateway: hermes -p gentech gateway restart
```

**Related:** See also Section 9 (Authentication & Credential Health) for Nous OAuth token expiry and refresh workflow.

### 3. Error Rate Analysis

Scan last 300 lines of each gateway log:

```python
with open(log) as f:
    lines = f.readlines()[-300:]

errors = [l for l in lines if 'ERROR' in l]
criticals = [l for l in lines if 'CRITICAL' in l]
exceptions = [l for l in lines if 'Exception' in l or 'Traceback' in l]
```

**Action:** Any errors → extract timestamps, patterns, and stack traces.

### 4. TTS Service Health Check (ELEVENLABS)

ElevenLabs TTS failures are currently fleet-wide and block voice responses.

**Detection pattern:**
```python
import re
from collections import Counter

for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    log = f'/root/.hermes/profiles/{agent}/logs/errors.log'
    with open(log) as f:
        content = f.read()
    
    # Count recent TTS auth failures
    tts_401 = len(re.findall(r'elevenlabs.*?status_code.*?401', content[-5000:]))
    tts_other = len(re.findall(r'tts_tool.*?failed', content[-5000:]))
    
    print(f"{agent.upper()}: {tts_401} ElevenLabs 401 errors (last 5000 chars), {tts_other} other TTS failures")
```

**Indicators of fleet-wide outage:**
- All 4 agents showing 15+ TTS 401 errors in the last 100 error log lines
- Error message: `ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}`
- Affects `tts_tool` across all voice-enabled interactions

**Remediation:**
1. Rotate `ELEVENLABS_API_KEY` in all agent environments
2. Restart gateways after key update
3. Temporary mitigation: disable TTS via `tts_provider: null` in agent configs or switch fallback provider

**Temporary disable TTS in config.yaml:**
```yaml
tools:
  tts:
    provider: null  # or 'elevenlabs'/'openai' if rotating keys
    enabled: false   # set to false to skip TTS entirely
```

**Reference:** `references/elevenlabs-tts-401-errors.md`

### 4. Kanban DB Health (DMOB & Desmond)

Kanban dispatcher failures manifest as `sqlite3.OperationalError: disk I/O error` or `database is locked`.

**Check DB state:**

```python
import sqlite3

db_path = f'{base}/{agent}/kanban.db'
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM tasks")  # Should be > 0 if active
cursor.execute("PRAGMA journal_mode")        # Should return 'wal'
cursor.execute("PRAGMA integrity_check")     # Should return 'ok'

conn.close()
```

**Failure signature:**
- `tasks` count = 0 AND last DB modification > 24h → **kanban dispatcher is dead**
- `journal_mode` query raises `OperationalError: disk I/O error` → underlying disk/FS issue
- `integrity_check` ≠ 'ok' → DB corruption

**Recovery:**
```bash
# Restart affected gateway
hermes -p <profile> gateway stop
hermes -p <profile> gateway start

# If DB locked/corrupt:
rm /root/.hermes/profiles/<agent>/kanban.db  # Deleted-but-open safe; process recreates on restart
```

**Cron DB corruption detection:** Jobs missing `profile` or `script` fields are unrunnable. Cross-check `hermes cron list` output against raw `jobs.json`. Repair by adding correct values or recreate via `hermes cron add`.

**Error recency check:** Distinguish historical from active errors. Compare timestamp of last ERROR vs last INFO line; if last ERROR > 1h old but INFO activity is recent, errors are stale.

**Fleet-wide correlation:** If >50% of agents show the SAME error type within 1 hour, treat as shared infrastructure failure (e.g., TTS API, disk I/O, network) — fix globally, not per-agent.

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `kanban dispatcher: tick failed` + `disk I/O error` | SQLite DB locked due to unclosed connections or disk pressure | Restart gateway; if persists, delete `kanban.db` (recreates empty) |
| `kanban DB 0 tasks, 26h stale` | Dispatcher crashed and never recovered | Restart gateway; verify cron ticker starts |
| `Chat not found` (Gentech) | Bot expelled from group or chat ID mismatch | Re-invite bot to `-1003863540828`; verify `allowed_chat_ids` in config |
| `Fleet-wide TTS 401 (all agents)` | Shared ElevenLabs API key expired/revoked | Rotate `ELEVENLABS_API_KEY` in all agent environments; disable TTS temporarily if needed | Restart gateways after key update |\n| `Cron executor deadlocked (ticker but 0 job dispatches)` | Scheduler thread stalled or cron subsystem crashed | Restart all agent gateways; verify `hermes cron list --verbose` shows active schedules; check for corrupt `jobs.json` schema |\n| `All cron jobs missing required 'task_id' field` | Cron job database corruption or incomplete migration | Recreate jobs via `hermes cron add` with proper task context; validate jobs schema against contract |\n| `All cron jobs status = 'unknown' (no updates)` | Cron ticker not dispatching to executor | Same as executor deadlock — restart gateways, inspect `agent.log` for `cron.executor` events |\n| `Refresh session has been revoked` | Hermes Nous Portal session expired | Run `hermes model` in each agent profile to re-authenticate |\n| `EOFError: marshal data too short` | Python bytecode cache corruption (`__pycache__/*.pyc`) | Delete all `__pycache__` directories under `/usr/local/lib/hermes-agent/`; restart gateways |\n| `sqlite3.OperationalError: database disk image is malformed` | SQLite DB corruption (kanban or session store) | Stop gateway; delete corrupted DB (recreates empty); restart gateway |\n
| `Flood control exceeded` | Too many Telegram messages in short window | Stagger cron schedules; consolidate notifications |
ERROR gateway.platforms.telegram: [Telegram] Failed to send Telegram message: Chat not found
telegram.error.BadRequest: Chat not found
```

**Root causes:**
- Bot removed from target group
- Bot blocked by user
- Chat ID changed (unlikely for groups)
- Bot lacks `can_send_messages` permission

**Diagnose:**
1. Check agent config for `allowed_chat_ids` or group references
2. Verify bot still in group: search logs for inbound messages from that chat (should still appear)
3. Re-invite bot to group if missing

**Flood control detection:**
```python
flood_events = [l for l in log_content if 'Flood control exceeded' in l]
if len(flood_events) > 10:
    print(f"⚠️  Telegram rate limits hit: {len(flood_events)} events")
```

**Mitigation:** Spread cron job schedules, reduce message frequency, or switch to bulk summary mode.

### 5. Cron Job Contract Validation

**Check for missing `task_id` field (systemic corruption indicator):**

```python
import json

base = '/root/.hermes/profiles'
for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    with open(f'{base}/{agent}/cron/jobs.json') as f:
        jobs = json.load(f).get('jobs', [])
    
    without_task_id = [j for j in jobs if 'task_id' not in j]
    if without_task_id:
        print(f"{agent.upper()}: {len(without_task_id)}/{len(jobs)} jobs missing 'task_id' — CONTRACT VIOLATION")
        print(f"  Example: {without_task_id[0].get('id')} — {without_task_id[0].get('name','')[:50]}")
```

**Impact:** Jobs without `task_id` cannot be tracked in kanban, fail silently, and break the cron execution contract. This often accompanies broader cron subsystem deadlock.

**Repair:** Re-add jobs via `hermes cron add` with proper task context, or regenerate from source if jobs.json is corrupted.

**Job status audit:**

```python
statuses = {}
for j in jobs:
    s = j.get('status', 'unknown')
    statuses[s] = statuses.get(s, 0) + 1
print(f"Status breakdown: {statuses}")
```

All-`unknown` status across the fleet indicates the cron scheduler isn't updating job states — another deadlock signal.

### 6. Telegram Rate Limiting & Flood Control

Telegram flood control throttles message sending when rate limits are exceeded, causing response delays and message backoffs.

**Detection pattern:**
```python
for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    log_path = f'/root/.hermes/profiles/{agent}/logs/gateway.log'
    with open(log_path) as f:
        log_content = f.read()
    
    flood_events = re.findall(r'Telegram flood control.*?retrying in (\d+\.?\d*)s', log_content)
    recent = [e for e in flood_events if float(e.group(1)) > 0][-20:]  # last 20 backoffs
    
    if len(recent) > 10:
        print(f"{agent.upper()}: ⚠️  {len(recent)} flood control events in recent history")
        print(f"  Backoff pattern (last 5): {[float(e.group(1)) for e in recent[-5:]]} seconds")
```

**Correlated symptoms:**
- `gateway.platforms.telegram: [Telegram] Telegram flood control on send` warnings in gateway.log
- Response times ballooning (>100s) due to retry backoffs
- Multiple consecutive retry attempts with increasing delays (3–19s typical)
- Agent appears 'stuck' but actually throttling outbound messages

**Severity thresholds:**
- `> 5 events/hr` → warning, investigate message frequency
- `> 15 events/hr` → critical, stagger schedules or consolidate notifications

**Mitigation:**
1. Spread cron job schedules to avoid simultaneous Telegram sends
2. Reduce notification chatter (batch updates, summarize)
3. Check if Telegram bot is in rate-limited mode due to recent spam reports
4. Consider switching to alternative delivery channels for bulk notifications

**Historical note (May 2, 2026):** Desmond showed 14 flood control warnings, Gentech 4, DMOB 1 in a single 100-line window — indicating system-wide Telegram rate limit pressure.

### 6a. Telegram "Chat not found" Error — Permanent vs Transient

**Error signature:** `telegram.error.BadRequest: Chat not found` when bot attempts to send a message.

**Two failure modes:**

| Mode | Root Cause | Recovery |
|------|------------|----------|
| **Permanent** | Bot expelled from group, blocked by user, or never joined | 1. Manually re-invite bot to group<br>2. Verify bot has `can_send_messages` permission<br>3. Restart gateway to reinitialize chat context |
| **Transient** | Gateway restart/restart caused bot's Telegram session to reset; bot is in group but not yet authorized to send | 1. Send any inbound message to bot first (triggers reconnect)<br>2. Check logs for successful inbound → outbound message flow<br>3. Error typically clears on next outbound send after ~30s |

**Detection (May 3, 2026 incident pattern):**
```python
# Check if error cluster coincides with recent gateway restart
import subprocess, re

log = subprocess.run(['tail', '-n', '200', '/root/.hermes/profiles/gentech/logs/gateway.log'],
                     capture_output=True, text=True).stdout

restart_time = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?gateway.run: Starting Hermes Gateway', log)[-1]
chat_errors_after = [l for l in log.split('\n') if 'Chat not found' in l and l.startswith('2026-') and l > restart_time]

if len(chat_errors_after) > 0:
    # Look for successful sends *after* the errors
    sends_after = [l for l in log.split('\n') if 'Sending response' in l and l.startswith('2026-') and l > restart_time]
    if sends_after:
        print("Transient: errors occurred but subsequent sends succeeded — bot recovered")
    else:
        print("Permanent: no successful sends since restart — bot likely removed from group")
```

**Diagnostic checklist:**
- [ ] Confirm bot still in target group (manual verification in Telegram)
- [ ] Check gateway.log for ANY successful `Sending response` entries after last restart
- [ ] If inbound messages appear but outbound fails with "Chat not found", bot is in group but lacks permission
- [ ] If no inbound activity, bot may be disconnected entirely — check `Connected to Telegram` line

**Recovery steps (Gentech, May 3, 2026):** Gateway restart at 12:24:30 cleared transient "Chat not found" errors; successful sends observed at 12:37 and 12:47. Root cause: Telegram polling session reset during restart created a temporary auth window where the bot's chat membership was not yet recognized. Solution: wait 1–2 minutes after restart OR send an inbound message to trigger chat resolution.

**Mitigation for future:** Deploy a startup warm-up routine that sends a silent `/start` or health-check message to the primary chat after gateway boot to establish chat session immediately.

**Detect fleet-wide ElevenLabs TTS failures:**

```python
import re

for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    log = f'/root/.hermes/profiles/{agent}/logs/errors.log'
    with open(log) as f:
        content = f.read()
    
    tts_errors = re.findall(r'elevenlabs.*?status_code.*?(\d{3})', content)
    if tts_errors:
        recent = tts_errors[-5:]
        print(f"{agent}: Recent TTS errors: {recent}")
```

**401 Unauthorized** → API key expired/rotated. Update `ELEVENLABS_API_KEY` in agent environment and restart gateways.

**Mitigation while fixing:** Disable TTS fallback by setting `tts_provider: null` in agent configs, or switch to alternative TTS (OpenAI, Google).

### 7. TTS Service Health Check (ELEVENLABS)

ElevenLabs TTS failures are currently fleet-wide and block voice responses.

**Detection pattern:**
```python
import re
from collections import Counter

for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    log = f'/root/.hermes/profiles/{agent}/logs/errors.log'
    with open(log) as f:
        content = f.read()
    
    # Count recent TTS auth failures in last 5000 chars
    tts_401 = len(re.findall(r'elevenlabs.*?status_code.*?401', content[-5000:]))
    tts_other = len(re.findall(r'tts_tool.*?failed', content[-5000:]))
    
    print(f"{agent.upper()}: {tts_401} ElevenLabs 401 errors (last 5000 chars), {tts_other} other TTS failures")
```

**Indicators of fleet-wide outage:**
- All 4 agents showing 15+ TTS 401 errors in the last 100 error log lines
- Error message: `ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}`
- Affects `tts_tool` across all voice-enabled interactions

**Remediation:**
1. Rotate `ELEVENLABS_API_KEY` in all agent environments
2. Restart gateways after key update
3. Temporary mitigation: disable TTS via `tts_provider: null` in agent configs or switch fallback provider

**Temporary disable TTS in config.yaml:**
```yaml
tools:
  tts:
    provider: null  # or 'elevenlabs'/'openai' if rotating keys
    enabled: false   # set to false to skip TTS entirely
```

**Reference:** `references/elevenlabs-tts-401-errors.md`

### 10. Tool-Gateway (Firecrawl) Availability Check

**Purpose:** Detect if the tool-gateway service is running, which is required for Firecrawl web search and other tool integrations.

**Why this matters:** When tool-gateway is down, ALL agents fail with `Firecrawl client initialization failed: missing direct config and tool-gateway auth` errors. This is a system-level failure, not an agent-specific one.

**Detection:**
```python
import subprocess

# Check for tool-gateway process
result = subprocess.run(
    ['ps', 'aux'], capture_output=True, text=True
)
tool_gateway_running = any('tool-gateway' in line.lower() or 'toolgateway' in line.lower() 
                         for line in result.stdout.split('\n'))

# Check for expected listening ports (usually 3000, 8080, or 5000)
port_check = subprocess.run(
    ['netstat', '-tlnp'], capture_output=True, text=True
)
listening_on_expected = any(port in port_check.stdout for port in ['3000', '8080', '5000'])

if not tool_gateway_running:
    print("🚨 CRITICAL: tool-gateway process is NOT running")
    print("   Impact: All agents lose Firecrawl/web search capability")
    print("   Recovery: hermes tool-gateway start (or systemctl --user start hermes-tool-gateway)")
else:
    print("✅ tool-gateway is running")
    
if not listening_on_expected:
    print("⚠️  tool-gateway not listening on expected ports")
```

**Cross-agent error correlation:** Verify all agents show the same `Firecrawl client initialization failed` error pattern within the same time window. Universal occurrence across yoyo/dmob/desmond/gentech confirms tool-gateway outage vs local config issue.

**Recovery sequence:**
1. Check tool-gateway config exists: `ls /root/.hermes/tool-gateway/` or `~/.config/hermes/tool-gateway/`
2. Start service: `hermes tool-gateway start` or `systemctl --user start hermes-tool-gateway`
3. Verify process: `ps aux | grep tool-gateway`
4. Verify port listening: `netstat -tlnp | grep -E '3000|8080|5000'`
5. Test recovery: Run a Firecrawl-dependent script manually (e.g., `kite-hackathon-checks.py`) and confirm exit code 0
6. Restart agent gateways to refresh tool connections: `hermes -p <agent> gateway restart`

**Related cron job:** `Tool-Gateway Auto-Start` in Gentech cron should auto-recover, but verify it's enabled and the script exists at `/root/.hermes/profiles/gentech/scripts/tool_gateway_monitor.py`.

### 11. Missing Skill Detection (Cron Job Silent Failures)

**Symptom:** Cron jobs silently skipped with log entry: `Skill 'X' not found, skipping` or `skill not found, skipping`.

**Why this matters:** Missing skills cause cron jobs to fail silently without raising alerts in the Watchdog. Jobs show as "enabled" in `hermes cron list` but never actually execute.

**Detection:**
```python
import json, re

agents = ['yoyo', 'dmob', 'desmond', 'gentech']
missing_skills = {}

for agent in agents:
    log_path = f'/root/.hermes/profiles/{agent}/logs/gateway.log'
    with open(log_path) as f:
        log_content = f.read()
    
    # Find recent "skill not found" errors
    skill_errors = re.findall(r"Skill '([^']+)' not found, skipping", log_content)
    if skill_errors:
        missing_skills[agent] = skill_errors
        print(f"{agent.upper()}: Missing skills detected — {skill_errors}")
    else:
        print(f"{agent.upper()}: No missing skill errors in recent logs")

# Summary
total_missing = sum(len(v) for v in missing_skills.values())
if total_missing > 0:
    print(f"🚨 Fleet-wide: {total_missing} skill resolution failures across {len(missing_skills)} agents")
```

**Common missing skills (May 3, 2026):**
- `cmc-watchlist-scraper` — referenced by YoYo's crypto watchlist cron
- `crypto-monitoring-cron` — referenced by YoYo's LP monitor cron
- Both indicate incomplete skill migration or vault sync issues

**Immediate remediation:**
1. Search vault for skill directories: `find /root/vaults/gentech -type d -name "cmc-watchlist-scraper*"`
2. If skill exists in vault but not installed: `hermes skill install cmc-watchlist-scraper`
3. If skill missing entirely: restore from backup or recreate as new skill under `gentech-skills/`
4. After skill installation, restart agent gateway to refresh skill registry: `hermes -p <agent> gateway restart`

**Prevention:** Add a pre-cron-execution skill resolution check to the Watchdog — before each cron tick, verify all scheduled job skills exist in the agent's skill registry. Fail fast and alert if any are missing.

### 12. Kanban DB Health (DMOB & Desmond)

Kanban dispatcher failures manifest as `sqlite3.OperationalError: disk I/O error` or `database is locked`.

**Check DB state:**
```python
import sqlite3, os

base = '/root/.hermes/profiles'
for agent in ['dmob', 'desmond']:
    db_path = f'{base}/{agent}/kanban.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")  # Should be > 0 if active
        count = cursor.fetchone()[0]
        cursor.execute("PRAGMA journal_mode")        # Should return 'wal'
        journal = cursor.fetchone()[0]
        cursor.execute("PRAGMA integrity_check")     # Should return 'ok'
        integrity = cursor.fetchone()[0]
        conn.close()
        print(f"{agent.upper()}: tasks={count}, journal_mode={journal}, integrity={integrity}")
    else:
        print(f"{agent.upper()}: kanban.db NOT FOUND")
```

**Failure signature:**
- `tasks` count = 0 AND last DB modification > 24h → **kanban dispatcher is dead**
- `journal_mode` query raises `OperationalError: disk I/O error` → underlying disk/FS issue
- `integrity_check` ≠ 'ok' → DB corruption

**Recovery:**
```bash
# Restart affected gateway
hermes -p <profile> gateway stop
hermes -p <profile> gateway start

# If DB locked/corrupt:
rm /root/.hermes/profiles/<agent>/kanban.db   # Deleted-but-open safe; process recreates on restart
```

**Cron DB corruption detection:** Jobs missing `profile` or `script` fields are unrunnable. Cross-check `hermes cron list` output against raw `jobs.json`. Repair by adding correct values or recreate via `hermes cron add`.

**Error recency check:** Distinguish historical from active errors. Compare timestamp of last ERROR vs last INFO line; if last ERROR > 1h old but INFO activity is recent, errors are stale.

**Fleet-wide correlation:** If >50% of agents show the SAME error type within 1 hour, treat as shared infrastructure failure (e.g., TTS API, disk I/O, network) — fix globally, not per-agent.

### 13. Gateway Process vs PID File Liveness

PID files can become stale during crashes. Always cross-check with live process table:

```python
import json, subprocess

agents = {
    'yoyo': '/root/.hermes/profiles/yoyo/gateway.pid',
    'dmob': '/root/.hermes/profiles/dmob/gateway.pid',
    'desmond': '/root/.hermes/profiles/desmond/gateway.pid',
    'gentech': '/root/.hermes/profiles/gentech/gateway.pid'
}

for agent, pid_file in agents.items():
    with open(pid_file) as f:
        pid_data = json.load(f)
    recorded_pid = pid_data['pid']
    
    # Check if process actually running
    result = subprocess.run(['ps', '-p', str(recorded_pid), '-o', 'stat='], 
                          capture_output=True, text=True)
    actual_state = result.stdout.strip()
    
    if not actual_state:
        print(f"{agent.upper()}: gateway.pid records PID {recorded_pid} but process NOT RUNNING — STALE PID FILE")
    else:
        print(f"{agent.upper()}: PID {recorded_pid} active, state {actual_state}")
```

**Historical vs active errors:** To distinguish old from new, compare error log timestamp vs last INFO timestamp:

```python
from datetime import datetime, timedelta

def last_log_timestamp(log_path, line_filter=None):
    lines = open(log_path).readlines()[::-1]  # reverse scan
    for line in lines:
        if line_filter and line_filter not in line:
            continue
        m = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if m:
            return datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
    return None

for agent in agents:
    err_ts = last_log_timestamp(f'/root/.hermes/profiles/{agent}/logs/errors.log', line_filter='ERROR')
    info_ts = last_log_timestamp(f'/root/.hermes/profiles/{agent}/logs/gateway.log', line_filter='INFO')
    
    if err_ts and info_ts:
        age_min = (datetime.now() - err_ts).total_seconds() / 60
        if age_min > 60 and info_ts > err_ts:
            print(f'{agent.upper()}: Last error {age_min:.0f}min old but recent INFO activity — errors are STALE')
```

### 14. Overdue & Stalled Handoff Detection

**Pattern:** Items in `11-Mess Hall/approvals.md` or handoff tables marked `⏳ Pending` or `Overdue` for >6 days indicate process breakdowns.

**Detection:**
```python
import re
from datetime import datetime, timedelta

handoff_file = '/root/vaults/gentech/11-Mess Hall/approvals.md'
with open(handoff_file) as f:
    content = f.read()

# Find overdue items (older than 6 days)
now = datetime.now()
overdue_items = []

for line in content.split('\n'):
    if '⏳' in line or 'Overdue' in line or 'Overdue' in line.lower():
        # Extract date if present
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
        if date_match:
            item_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
            days_overdue = (now - item_date).days
            if days_overdue > 6:
                overdue_items.append({'line': line[:100], 'days': days_overdue})

if overdue_items:
    print(f"🚨 {len(overdue_items)} handoffs overdue >6 days")
    for item in overdue_items[:5]:
        print(f"  [{item['days']}d] {item['line']}")
```

**Action:** Escalate to team lead; investigate blocker (missing approvals, dependency chains, agent inactivity).

### 15. Cron Job Overlap Detection

**Pattern:** Multiple cron jobs with overlapping responsibilities create waste and can trigger race conditions.

**Detection:**
```python
import json
from datetime import datetime, timedelta

base = '/root/.hermes/profiles'
overlap_candidates = []

for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    with open(f'{base}/{agent}/cron/jobs.json') as f:
        jobs = json.load(f).get('jobs', [])
    
    # Group by schedule similarity (same minute patterns)
    schedules = {}
    for j in jobs:
        schedule = j.get('cron', '')
        if schedule:
            schedules.setdefault(schedule, []).append(j['name'])
    
    for schedule, names in schedules.items():
        if len(names) > 1:
            overlap_candidates.append({'agent': agent, 'schedule': schedule, 'jobs': names})

if overlap_candidates:
    print("⚠️  Overlapping cron jobs detected:")
    for c in overlap_candidates:
        print(f"  {c['agent']} @ {c['schedule']}: {c['jobs']}")
```

**Consolidation target:** Merge into single consolidated cron job per logical domain (e.g., one `d5-milestone-tracker.py` replacing 4 separate LP/crypto monitoring jobs).

**Current state (May 3, 2026):** YoYo has 4 overlapping jobs still running — consolidate per `09-Green Room/cron-consolidation-d5-milestone-tracker.md`.

Python bytecode corruption causes `EOFError: marshal data too short` and `ImportError` failures that break agent functionality.

**Detection:**
```python
import subprocess, os

# Scan for invalid .pyc files in hermes-agent installation
result = subprocess.run(
    ["find", "/usr/local/lib/hermes-agent", "-name", "*.pyc", 
     "-exec", "file", "{}", "\\;"],
    capture_output=True, text=True
)

# Filter for files not recognized as valid Python bytecode
corrupted = [line for line in result.stdout.split('\n') 
             if 'Python compiled bytecode' not in line and line.strip()]
if corrupted:
    print(f"⚠️  CORRUPTED BYTECODE FILES DETECTED:")
    for c in corrupted[:10]:
        print(f"  {c}")
```

**Alternative check via error logs:**
```bash
grep -r "EOFError: marshal data too short" /root/.hermes/profiles/*/logs/errors.log
```

**Common corruption patterns:**
- Error: `EOFError: marshal data too short` — .pyc truncated or incomplete write
- `.pyc` size much smaller than corresponding `.py` source file
- Magic number mismatch (e.g., `a70d0d0a` vs expected `0x33 0x0d 0x0d 0x0a` for Python 3.11)

**Recovery:**
```bash
# Stop all gateways first
for agent in yoyo dmob desmond gentech; do
    hermes -p $agent gateway stop
done

# Remove all bytecode caches
find /usr/local/lib/hermes-agent -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Restart gateways (fresh .pyc generation)
for agent in yoyo dmob desmond gentech; do
    hermes -p $agent gateway start
done
```

**Prevention:** Ensure adequate disk space (`df -h` shows >10% free) and graceful shutdowns. Bytecode corruption often follows disk pressure events (`Errno 28: No space left on device`).

### 9. Authentication & Credential Health

**Nous Portal OAuth token health check (POST-REFRESH VALIDATION):**

The proactive refresh script (`refresh_nous_oauth.py`) may report `needs_reauth: true` even after manual `hermes model` re-authentication if the Nous Portal session wasn't properly persisted. Always verify tokens are actually saved to `auth.json`, not just that the refresh script exits without error.

**Detection (multi-layer):**
```python
import json, os

agents = ['yoyo', 'dmob', 'desmond', 'gentech']
oauth_healthy = {}

for agent in agents:
    auth_file = f'/root/.hermes/profiles/{agent}/auth.json'
    try:
        with open(auth_file) as f:
            auth = json.load(f)
        # Handle both auth shapes: {'nous': {...}} or {'nous_tokens': {...}}
        tokens = auth.get('nous', {}) or auth.get('nous_tokens', {})
        has_token = 'access_token' in tokens and tokens.get('access_token')
        expires_str = tokens.get('expires_at', 'N/A')
        oauth_healthy[agent] = {'has_token': has_token, 'expires': expires_str}
        status = '✅ VALID' if has_token else '❌ MISSING'
        print(f"{agent.upper()}: {status} (expires: {expires_str[:16] if expires_str != 'N/A' else 'N/A'})")
    except Exception as e:
        oauth_healthy[agent] = {'error': str(e)}
        print(f"{agent.upper()}: ERROR reading auth — {e}")

# Cross-agent health summary
healthy_count = sum(1 for v in oauth_healthy.values() if v.get('has_token'))
if healthy_count < len(agents):
    print(f'🚨 FLEET OAUTH DEGRADED: {healthy_count}/{len(agents)} agents have valid Nous tokens')
```

**Fleet-wide OAuth revocation pattern (detected May 4, 2026):** When ALL agents show `access_token: MISSING` simultaneously AND the proactive refresh job reports `"Refresh session has been revoked"`, this indicates a fleet-wide revocation event, not isolated agent issues.

**Confirmation checklist:**
- [ ] Check `auth.json` in every agent: `access_token` field absent or very short (<10 chars)
- [ ] Check `refresh_token` field: also missing or empty (revoked sessions invalidate both)
- [ ] Run refresh script manually: `python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py`
  - Expected failure: `{"success": false, "message": "Refresh session has been revoked", "needs_reauth": true}`
- [ ] Check error logs for `RuntimeError: Refresh session has been revoked` repeated in all agents
- [ ] Cross-check token expiry timestamps: if all show same expiry window (e.g., 2026-05-03 22:11:54 UTC), shared token batch expired

**Recovery (manual):** Run `hermes model` in each agent profile **interactively** (cannot be scripted in cron). After each re-auth, verify tokens saved to `auth.json` and refresh script returns `{"success": true, "needs_reauth": false}`.

**Critical distinction:** `needs_reauth: true` from the refresh script indicates the current session is invalid **AND** the refresh token is no longer usable. This is **not recoverable** by automated refresh — it requires **manual** `hermes model` to re-establish the Nous Portal OAuth flow from scratch.

**Post-recovery verification:** After running `hermes model` in each agent profile, immediately verify:
```bash
# 1. Check auth.json actually contains nous_tokens
python3 -c "import json; a=json.load(open('/root/.hermes/profiles/yoyo/auth.json')); print('nous_tokens' in a and 'access_token' in a.get('nous_tokens',{}))"

# 2. Run refresh script and expect {"success": true, "needs_reauth": false}
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py

# 3. Test a Nous-dependent script (e.g., kite-hackathon-checks.py)
python3 /root/vaults/gentech/02-Labs/scripts/kite-hackathon-checks.py
```

**Silent failure mode (May 3, 2026 incident):** DMOB successfully ran `hermes model` but tokens were not persisted to `auth.json`. Root cause was traced to Hermes provider state not committing to disk after interactive re-auth. Workaround: Run `hermes model` **twice** (first to authenticate, second to commit session), or manually verify and re-run the refresh script until it returns success.

**Fleet-wide credential cascade:** If all 4 agents show identical OAuth failures within a 1-hour window, treat as shared credential revocation rather than per-agent issue. Corrective action: Run `hermes model` sequentially in **each** agent profile (yoyo, dmob, desmond, gentech) to re-establish Nous Portal sessions individually.

**Reference:** See `references/fleet-wide-nous-oauth-revocation-2026-05-04.md` for full incident case study.

### 10. gateway.pid File Verification vs Process Liveness

PID files can become stale during crashes. Always cross-check with live process table:

```python
import json, subprocess

agents = {
    'yoyo': '/root/.hermes/profiles/yoyo/gateway.pid',
    'dmob': '/root/.hermes/profiles/dmob/gateway.pid',
    'desmond': '/root/.hermes/profiles/desmond/gateway.pid',
    'gentech': '/root/.hermes/profiles/gentech/gateway.pid'
}

for agent, pid_file in agents.items():
    with open(pid_file) as f:
        pid_data = json.load(f)
    recorded_pid = pid_data['pid']
    
    # Check if process actually running
    result = subprocess.run(['ps', '-p', str(recorded_pid), '-o', 'stat='], 
                          capture_output=True, text=True)
    actual_state = result.stdout.strip()
    
    if not actual_state:
        print(f"{agent.upper()}: gateway.pid records PID {recorded_pid} but process NOT RUNNING — STALE PID FILE")
    else:
        print(f"{agent.upper()}: PID {recorded_pid} active, state {actual_state}")
```

**Historical vs active errors:** To distinguish old from new, compare error log timestamp vs last INFO line:
```python
import datetime
last_error = extract_timestamp(last_error_line)
last_info = extract_timestamp(last_info_line)
if last_error < (datetime.now() - datetime.timedelta(hours=1)) and last_info > last_error:
    print("Errors are stale; agent is currently healthy")
```

**Overdue detection:**

```python
import json
from datetime import datetime, timezone

with open(f'{base}/{agent}/cron/jobs.json') as f:
    jobs = json.load(f)

now_utc = datetime.now(timezone.utc)
overdue = []
for j in jobs['jobs']:
    nxt = j.get('next_run_at')
    if nxt and j.get('enabled') and not j.get('paused_by_system'):
        nxt_dt = datetime.fromisoformat(nxt.rstrip('Z'))
        if nxt_dt.tzinfo is None:
            nxt_dt = nxt_dt.replace(tzinfo=timezone.utc)
        if nxt_dt < now_utc:
            overdue.append(j['name'])
```

**Corruption detection (unrunnable jobs):**
```python
# Cross-check hermes cron list against raw jobs.json
import subprocess
result = subprocess.run(['hermes', 'cron', 'list'], capture_output=True, text=True)
visible_ids = re.findall(r'^[a-f0-9]+', result.stdout, re.MULTILINE)

with open(f'{base}/{agent}/cron/jobs.json') as f:
    jobs = json.load(f)

# Jobs that exist in JSON but don't appear in hermes cron list may have missing required fields
# Specifically check for jobs where 'profile' or 'script' is null/None
corrupt = []
for j in jobs.get('jobs', []):
    if j.get('profile') is None or j.get('script') is None:
        corrupt.append(j['id'])
```
**Action:** Jobs with missing `profile` or `script` fields are unrunnable. Repair by adding correct values or recreate via `hermes cron add`.

**Paused job inspection:**
```python
paused = [j for j in jobs['jobs'] if j.get('state') == 'paused']
for j in paused:
    print(f"PAUSED: {j['name']} — reason: {j.get('paused_reason','sys')}")
```

**Action:** Unpause via `hermes cron resume <ID>` or investigate system-initiated pauses.

### 7. Response Time Trend Analysis

Extract all `response ready:` entries:

```python
import re
responses = []
for line in log_lines:
    if 'response ready:' in line:
        m = re.search(r'time=([\d.]+)s', line)
        if m:
            responses.append(float(m.group(1)))

avg = sum(responses[-20:]) / 20
max_dur = max(responses)
slow_ratio = sum(1 for d in responses if d > 60) / len(responses)
```

**Degradation thresholds:**
- `avg > 60s`: ⚠️ Performance issue
- `max > 300s`: 🔴 Severe stall
- `slow_ratio > 0.5`: Systematic slowness

### 8. Session Error Rate

Check last 24h of session files:

```python
sess_files = glob.glob(f'{base}/{agent}/sessions/*.jsonl')
recent = [s for s in sess_files if datetime.fromtimestamp(os.path.getmtime(s)) > 
          (datetime.now() - timedelta(hours=24))]

error_sessions = 0
for s in recent:
    with open(s) as f:
        if 'error' in f.read().lower():
            error_sessions += 1

print(f"Error session ratio: {error_sessions}/{len(recent)}")
```

**If > 70%**: Investigate common error patterns across sessions (search for recurring exception types).

### 9. Connection Stability

Count disconnects/reconnects:

```python
disconnects = log_content.count('Telegram disconnected')
reconnects = log_content.count('Telegram polling resumed')
print(f"{agent}: {reconnects} reconnects, {disconnects} disconnects")
```

Repeated disconnects (>5/day) indicate network instability or Telegram API issues.

---

## Common Failure Modes & Fixes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `kanban dispatcher: tick failed` + `disk I/O error` | SQLite DB locked due to unclosed connections or disk pressure | Restart gateway; if persists, delete `kanban.db` (recreates empty) |
| `kanban DB 0 tasks, 26h stale` | Dispatcher crashed and never recovered | Restart gateway; verify cron ticker starts |
| `Chat not found` (Gentech) | Bot expelled from group or chat ID mismatch | Re-invite bot to `-1003863540828`; verify `allowed_chat_ids` in config |
| `response time > 300s` | LLM provider latency or tool execution stall | Check model provider status; review tool call churn in session files |
| `Flood control exceeded` | Too many Telegram messages in short window | Stagger cron schedules; consolidate notifications |
| `gateway.log stale >30min` | Gateway process dead or I/O-blocked | `hermes -p <profile> gateway restart` |
| `100% sessions contain errors` | Systematic exception in a frequently-used skill | Identify top error pattern from session files; disable/update skill |
| `All agents: Firecrawl client initialization failed` | Tool-gateway service down or not running | `hermes tool-gateway start`; verify listening on ports 3000/8080/5000; restart agent gateways |
| `All agents: nous_tokens MISSING from auth.json` | Nous OAuth revoked; manual re-auth state not persisted to disk | Run `hermes model` in each agent profile (may need twice); verify tokens saved to `auth.json`; confirm refresh script returns `{"success": true}` |

## Quick Diagnostic Script

Save as `scripts/agent_health.py` within this skill and run:

```bash
python3 scripts/agent_health.py
```

Outputs a one-line status per agent: `OK | DEGRADED | CRITICAL | STALLED`.

### Recommended agent_health.py contents

```python
#!/usr/bin/env python3
"""Gentech agent fleet health check — produces concise status line per agent."""
import json, os, re, subprocess, sys
from datetime import datetime, timedelta

AGENTS = ['yoyo', 'dmob', 'desmond', 'gentech']
BASE = '/root/.hermes/profiles'
NOW = datetime.now()

def check_auth(agent):
    auth_file = f'{BASE}/{agent}/auth.json'
    try:
        with open(auth_file) as f:
            auth = json.load(f)
        tokens = auth.get('nous', {}) or auth.get('nous_tokens', {})
        return bool(tokens.get('access_token'))
    except: return False

def check_cron_freshness(agent):
    out_dir = f'{BASE}/{agent}/cron/output/'
    if not os.path.exists(out_dir): return None, 999999
    files = []
    for root, dirs, filenames in os.walk(out_dir):
        for f in filenames:
            if f.endswith('.md'):
                fp = os.path.join(root, f)
                files.append((os.path.getmtime(fp), fp))
    if not files: return None, 999999
    mtime, _ = max(files)
    age_min = (NOW.timestamp() - mtime) / 60
    return "fresh" if age_min < 25 else "stale", age_min

def check_error_rate(agent):
    err_log = f'{BASE}/{agent}/logs/errors.log'
    try:
        with open(err_log) as f:
            content = f.read()
        # Count recent TTS 401 errors (indicator of service outage)
        tts_401 = len(re.findall(r'elevenlabs.*?status_code.*?401', content[-5000:]))
        return tts_401
    except: return 999

def check_gateway_freshness(agent):
    gw_log = f'{BASE}/{agent}/logs/gateway.log'
    try:
        stat = os.stat(gw_log)
        age_min = (NOW.timestamp() - stat.st_mtime) / 60
        return age_min
    except: return 999

results = {}
for agent in AGENTS:
    auth_ok = check_auth(agent)
    cron_status, cron_age = check_cron_freshness(agent)
    error_count = check_error_rate(agent)
    gw_age = check_gateway_freshness(agent)
    
    # Determine overall status
    if not auth_ok:
        status = "CRITICAL"
    elif error_count > 50:
        status = "DEGRADED"
    elif cron_status == "stale" and cron_age > 90:
        status = "STALLED"
    elif gw_age > 30:
        status = "STALLED"
    else:
        status = "OK"
    
    results[agent] = status
    print(f"{agent.upper():10s}: {status:10s}  (auth={auth_ok}, cron={cron_status or 'n/a'} [{cron_age:.0f}min], errors={error_count}, gw={gw_age:.0f}min)")

# Summary line
critical = [a for a,s in results.items() if s == "CRITICAL"]
if critical:
    print(f"\n🚨 FLEET CRITICAL — OAuth revoked? Check: {', '.join(critical.upper())}")
    sys.exit(2)
elif any(s == "STALLED" for s in results.values()):
    print("\n⚠️  FLEET DEGRADED — cron/gateway stalls detected")
    sys.exit(1)
else:
    print("\n✅ FLEET OK")
    sys.exit(0)
```

**Use in cron:** Add to Watchdog job: `python3 /root/.hermes/profiles/gentech/skills/gentech-agent-health/scripts/agent_health.py` and parse exit code.

## Advanced: Systemic Correlation Diagnostics

When individual agent checks reveal matching failure patterns across the fleet, escalate to systemic analysis. This distinguishes isolated agent bugs from shared infrastructure/credential cascades.

### Cron Subsystem Complete Failure (Distinct from Deadlock)

**CRITICAL DISTINCTION:** A deadlock shows an active ticker thread but zero dispatches. A complete subsystem failure is more severe: the cron executor is not running at all, `hermes_cron` module is missing, and no job dispatches occur ever.

**Detect complete failure:**
- Step A: Check for cron_enabled in configs (should be present; if absent, cron is disabled at the gateway level)
- Step B: Try importing hermes_cron module (`python3 -c "import hermes_cron"` — should succeed; ModuleNotFoundError = broken installation)
- Step C: Verify no standalone hermes-cron process exists (expected — cron runs inside gateway; but the *module* must be importable)
- Step D: Check gateway logs for "Cron ticker started" (presence proves cron subsystem was initialized) vs absence (cron never started)
- Step E: Cross-check jobs.json for `last_run_at` — if all jobs show `null` AND gateway uptime > 10 minutes, cron never executed

**Current fleet state (May 3, 2026):** All 4 agents have `cron_enabled` unset in config.yaml and fail `import hermes_cron` with ModuleNotFoundError. Gateways start with cron ticker thread running (after 12:05 and 12:24 restarts) but the executor thread immediately fails due to missing module, causing total job blackout.

**Remediation:**
1. Verify Hermes installation integrity (`hermes version` should show v0.12.0+; check /usr/local/lib/hermes-agent completeness)
2. If hermes_cron module missing, reinstall or repair Hermes agent package
3. Set `cron_enabled: true` in each agent's config.yaml and restart gateways
4. Confirm cron dispatches resume by checking `hermes cron list --verbose` shows recent `last_run_at` timestamps

**Difference from deadlock:** In deadlock, ticker is alive but executor thread stalled; jobs.json is valid but dispatches=0. In complete failure, the cron module cannot be imported, ticker may not start, and jobs.json may be orphaned. Recovery requires re-enabling cron in config and/or repairing installation, not just a gateway restart.

### Cron Deadlock Detection (Ticker Running But No Job Dispatches)

**Pattern:** Gateway logs show `Cron ticker started` but zero job dispatches for >2 hours despite past-due schedules.

**Detect:**
```python
import re
from datetime import datetime, timedelta

for agent in ['yoyo','dmob','desmond','gentech']:
    log = open(f'/root/.hermes/profiles/{agent}/logs/gateway.log').read()
    last_ticker_start = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Cron ticker started', log)[-1]
    last_dispatch = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*dispatching cron job', log)[-1] if re.findall('dispatching cron job', log) else None

    if last_ticker_start and not last_dispatch:
        ticker_age = datetime.now() - datetime.strptime(last_ticker_start, '%Y-%m-%d %H:%M:%S')
        if ticker_age > timedelta(hours=2):
            print(f'{agent.upper(): CRITICAL — cron ticker active but never dispatched a job}')
    elif last_ticker_start and last_dispatch:
        dispatch_age = datetime.now() - datetime.strptime(last_dispatch, '%Y-%m-%d %H:%M:%S')
        if dispatch_age > timedelta(hours=4):
            print(f'{agent.upper(): WARNING — last dispatch >4h ago despite ticker running}')
```

**Immediate action:** Restart ALL gateways simultaneously. Verify `hermes cron list --verbose` shows active schedules. Inspect `jobs.json` for schema corruption (missing `profile`, `script`, or `task_id` fields).

### API Credential Cascade Detection

**Pattern:** Multiple agents show identical auth error types within the same time window, indicating a shared credential (API key, provider token) has expired or been revoked.

**Detect fleet-wide TTS failure:**
```python
from collections import Counter
import re

error_patterns = {}
for agent in ['yoyo','dmob','desmond','gentech']:
    log = open(f'/root/.hermes/profiles/{agent}/logs/errors.log').read()
    recent = log[-10000:]  # last ~10k chars
    tts_401 = bool(re.search(r'elevenlabs.*?status_code.*?401', recent))
    anthropic_missing = bool(re.search(r'No Anthropic credentials found', recent))
    opencode_no_key = bool(re.search(r"Provider 'opencode-go'.*no API key", recent))
    error_patterns[agent] = {'tts_401': tts_401, 'anthropic': anthropic_missing, 'opencode': opencode_no_key}

# Cross-agent correlation
if sum(1 for v in error_patterns.values() if v['tts_401']) >= 4:
    print('🚨 FLEET-WIDE TTS FAILURE — rotate ELEVENLABS_API_KEY across all agents')
if sum(1 for v in error_patterns.values() if v['anthropic']) >= 3:
    print('🚨 ANTHROPIC CREDENTIALS MISSING in most agents — restore ANTHROPIC_API_KEY')
```

**Cross-check within same log stream** (some errors may be logged in gateway.log instead of errors.log):
```python
for agent in agents:
    log = open(f'/root/.hermes/profiles/{agent}/logs/gateway.log').read()
    # look for repeated identical error lines in a 5-minute window
    lines = log.split('\n')
    for i, line in enumerate(lines):
        if 'ERROR' in line and 'status_code: 401' in line:
            window = '\n'.join(lines[i:i+20])  # next 20 lines (~seconds)
            if window.count('status_code: 401') >= 5:
                print(f'{agent}: clustered auth failures = systemic')
```

**Remediation:**
1. Rotate the shared API key in all agent environments (`~/.hermes/profiles/*/.env` or config)
2. Restart gateways to force credential reload
3. Temporary mitigation: disable affected tools in config (`tts_provider: null`, `llm_provider: fallback`)

### Gateway Restart Correlation

**Pattern:** All agents show near-simultaneous exit/restart timestamps within a 1-minute window, indicating an orchestrated update or systemic trigger (not independent crashes).

**Detect:**
```python
from datetime import datetime

restart_times = {}
for agent in agents:
    log = open(f'/root/.hermes/profiles/{agent}/logs/gateway.log').read()
    exits = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Exiting with code 1', log)
    starts = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Cron ticker started', log)
    restart_times[agent] = {'exits': [datetime.strptime(e[0], '%Y-%m-%d %H:%M:%S') for e in exits[-5:]],
                            'starts': [datetime.strptime(s[0], '%Y-%m-%d %H:%M:%S') for s in starts[-5:]]}

# Check if last restart wave was coordinated
all_last_exits = [v['exits'][-1] for v in restart_times.values() if v['exits']]
if max(all_last_exits) - min(all_last_exits) < timedelta(seconds=30):
    print('🚨 Coordinated restart wave detected — likely update-triggered or orchestrator signal')
    print(f'  Exits: {[e.strftime("%H:%M:%S") for e in all_last_exits]}')
```

**Interpretation:**
- If exits cluster within 1 minute but starts are staggered (>5 min spread), agents are failing to auto-restart (check systemd/cron).
- If both exits and starts are clustered, an external orchestrator (update script, deployment pipeline) intentionally recycled them.

### Profile Directory Existence Validation

**Pattern:** Gateway processes may be alive but non-functional if their profile directories were deleted/moved (e.g., during cleanup or migration). Gateway will start, fail to find config, and exit silently.

**Detect:**
```python
import os

for agent in agents:
    profile_dir = f'/root/.hermes/profiles/{agent}'
    if not os.path.isdir(profile_dir):
        print(f'{agent.upper(): CRITICAL — profile directory missing: {profile_dir}')
    else:
        config_ok = os.path.isfile(f'{profile_dir}/config.yaml')
        if not config_ok:
            print(f'{agent.upper(): ERROR — config.yaml missing from profile directory')
```

**Symptom correlation:**
- Process alive but gateway.log not updating → check profile dir
- `hermes cron list` shows job but `hermes -p <agent> gateway status` says "no such profile"
- Systemd unit exists for agent but process immediately exits with code 1

**Fix:** Restore profile directory from backup or version control; recreate with `hermes init --profile <agent>` and re-provision credentials.

### YAML Syntax Error Detection

**Pattern:** Silent config fallback to `.env` occurs when `config.yaml` contains YAML syntax errors, causing degraded functionality (stale values, missing tools).

**Detect:**
```python
import subprocess, json

for agent in agents:
    result = subprocess.run(['python3', '-c',
        f'import yaml; yaml.safe_load(open("/root/.hermes/profiles/{agent}/config.yaml"))'],
        capture_output=True, text=True)
    if result.returncode != 0:
        err = result.stderr.strip()
        print(f'{agent.upper(): CONFIG PARSE ERROR — {err}')
        # Extract line number if mentioned
        import re
        m = re.search(r'line (\d+)', err)
        if m:
            print(f'  → Check line {m.group(1)} in config.yaml')
```

**Alternatively via agent logs:** Search for patterns:
```
Failed to process config.yaml — falling back to .env / gateway.json values. Error: mapping values are not allowed here
```

**Fix:** Run `yamllint` on config, correct indentation/colon spacing, verify all list items use `-` prefix and mappings use `key: value` with space after colon.

### Historical Error Recency Classification

**Pattern:** error.log may contain old failures from previous gateway generations. Distinguish active vs. stale errors.

**Detect:**
```python
from datetime import datetime, timedelta

def last_log_timestamp(log_path, line_filter=None):
    lines = open(log_path).readlines()[::-1]  # reverse scan
    for line in lines:
        if line_filter and line_filter not in line:
            continue
        # Extract ISO-ish timestamp: 2026-05-02 20:17:26,551
        m = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if m:
            return datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
    return None

for agent in agents:
    err_ts = last_log_timestamp(f'/root/.hermes/profiles/{agent}/logs/errors.log', line_filter='ERROR')
    info_ts = last_log_timestamp(f'/root/.hermes/profiles/{agent}/logs/gateway.log', line_filter='INFO')

    if err_ts and info_ts:
        age_min = (datetime.now() - err_ts).total_seconds() / 60
        if age_min > 60 and info_ts > err_ts:
            print(f'{agent.upper(): Last error {age_min:.0f}min old but recent INFO activity — errors are STALE')
```

## Pitfalls

- **Do not** delete `kanban.db` while gateway is running — stop gateway first (`hermes -p <profile> gateway stop`)
- **Do not** confuse `gateway.log` staleness with agent liveness — agents may process Telegram messages but not write logs if disk is full
- **Do not** ignore \"Chat not found\" as transient — it indicates bot was removed from group and requires manual re-invite
- **Do not** unpause cron jobs without verifying underlying issue is resolved (e.g., kanban failure would just re-pause them)
- **Always** check system disk space (`df -h`) and inode availability (`df -i`) before blaming application-level I/O errors
- **Do not** trust last error in errors.log as currently active — cross-check against recent INFO timestamps in gateway.log to classify as stale vs. ongoing
- **Do not** assume cron jobs are running because `Cron ticker started` appears in logs — verify actual dispatches exist; ticker thread may be alive while executor is deadlocked
- **When a credential error appears fleet-wide (same status code across all agents)**, check billing/account status first — individual agent fixes will not resolve a shared provider-side revocation
- **Do not** use `os.path.expanduser("~")` or `$HOME` in cron job scripts executed by Hermes — cron environment variables differ from interactive shells, causing path resolution to point to `/root/home` instead of `/root`. Always use absolute paths like `/root/.hermes/scripts/` or compute paths relative to `HERMES_HOME` env var set by the gateway: `os.path.join(os.environ.get("HERMES_HOME", "/root/.hermes"), "scripts")`

---

## Pitfalls

- **Do not** delete `kanban.db` while gateway is running — stop gateway first (`hermes -p <profile> gateway stop`)
- **Do not** confuse `gateway.log` staleness with agent liveness — agents may process Telegram messages but not write logs if disk is full
- **Do not** ignore "Chat not found" as transient — it indicates bot was removed from group and requires manual re-invite
- **Do not** unpause cron jobs without verifying underlying issue is resolved (e.g., kanban failure would just re-pause them)
- **Always** check system disk space (`df -h`) and inode availability (`df -i`) before blaming application-level I/O errors

## References

- `references/profile-deletion-incident-2026-05-02.md` — profile directory loss and gateway startup failure patterns
- `references/kanban-dispatcher-errors.md` — full error transcripts and recovery steps for DMOB/Desmond kanban failures (May 1–2, 2026)
- `references/gentech-telegram-chat-errors-2026-05-03.md` — "Chat not found" transient vs permanent differentiation, restart recovery pattern, and warm-up routine recommendations (observed May 3, 2026)
- `references/slow-response-investigation.md` — methodology for tracing >60s response times to tool calls and LLM latency
- `references/elevenlabs-tts-401-errors.md` — ElevenLabs TTS 401 auth failure pattern, environment variable debugging, provider fallback, and recovery procedures (detected May 2, 2026 — affects YoYo & Gentech)
- `references/systemic-correlation-detection.md` — fleet-wide failure pattern detection: cron deadlock, credential cascades, coordinated restart waves, shared storage corruption, Telegram network clusters, profile deletion side effects, bytecode cache corruption, and error recency classification (learned from May 2, 2026 watchdog session)
- `references/nous-portal-refresh-token-revocation-2026-05-03.md` — `Refresh session has been revoked` error pattern affecting cron jobs after token expiry; re-authentication via `hermes model` required
- `references/yoyo-cron-path-resolution-bug-2026-05-03.md` — Cron environment path resolution bug: `os.path.expanduser("~")` returning `/root/home` in cron context causing config file lookup failures; fix pattern for absolute path hardcoding or HERMES_HOME-aware resolution
- `references/fleet-wide-nous-oauth-revocation-2026-05-04.md` — May 4, 2026 incident: all 4 agents simultaneously lose Nous OAuth tokens (access & refresh missing); detection via auth.json absence and refresh job failure; requires manual `hermes model` re-authentication per profile
</content>