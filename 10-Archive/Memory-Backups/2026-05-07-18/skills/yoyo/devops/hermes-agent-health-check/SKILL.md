---
name: hermes-agent-health-check
version: "1.0.0"
description: Systematic health check methodology for Hermes agents — cron verification, gateway state, auth health, crash detection
trigger:
  - health check
  - agent status
  - watchdog check
  - cron health
  - verify agent
steps:
  - Verify agent processes running and stable uptime (watch for dual-PID patterns indicating restarts)
  - Check gateway_state.json and gateway.log for recent activity
  - Inspect jobs.json last_run and last_status for errors
  - Search agent.log for cron.scheduler Running job messages to confirm dispatch
  - Scan errors.log for auth failures and missing credentials
  - Check auth.json credential_pool: provider last_status (exhausted/ok/None) to preempt failures
  - Verify Nous Portal token validity if provider=nous (device_code flow): last_status should not be None
  - Check Telegram platform state.json for connection_state and last_error (gateway.platforms.telegram)
  - Verify telegram channel directory writeability (watch for "No space left on device" warnings)
  - Aggregate recent errors from agent.log, errors.log, gateway.log
  - Detect stuck patterns: tool loops, rapid message cycles, EOF cache corruption
  - Verify missed runs by comparing schedule vs last_run timestamps
  - Check for invalid model/provider errors (404 model not found from OpenRouter)
  - Check for SessionDB or storage initialization failures ("database or disk is full")
  - Classify: GREEN healthy, YELLOW partial failure, RED systemic failure
pitfalls:
  - cron_* log prefix is context only; proof of execution is Running job message
  - Auth errors in jobs.json persist until successful re-run after credential fix
  - Ticker restart does not backfill missed schedules
  - Refresh session revoked requires hermes model re-auth
  - Shared Telegram groups mask per-agent failures — check each agent's logs separately
  - EOFError marshal data too short means delete __pycache__ and restart agent
  - Cron executor deadlock: ticker alive but dispatcher blocked → check for ZERO job executions via missing 'Executing job' log lines and no new session directories; requires simultaneous gateway restart of ALL agents to reset thread pool
  - False-positive cron status: hermes cron list may show 'ok' without actual execution; verify via gateway logs and session creation, not jobs.json alone
  - Cron daemon stopped: hermes-cron process may be dead while agents run; scheduled jobs freeze silently until daemon restarted
  - Model 404 errors: OpenRouter model not found indicates misconfigured AUXILIARY_MODEL or auto-detection selecting deprecated models; check .env and config.yaml provider settings
  - Storage cascade: I/O errors (Errno 5) plus "database or disk is full" warnings indicate underlying storage issues that break DB-backed features
references:
  - agent-cron-patterns.md
  - auth-error-signatures.md
  - gateway-state-verification.md
  - systemic-failure-detection.md
scripts:
  - verify-cron-executions.py
  - detect-stuck-ticker.sh
  - clear-hermes-cache.sh
  - detect-cron-deadlock.sh
  - detect-systemic-failure.py
---

# Hermes Agent Health Check

Systematic diagnostic methodology for verifying Hermes agent operational health.

## Core Principle

**Execution verification > ticker presence**. A running cron ticker does NOT guarantee jobs are executing. You must find evidence of actual job dispatch (cron.scheduler Running job log lines) and completion within the expected schedule window.

## Watchdog Monitoring Mode — Routine Multi-Agent Health Sweeps

**Purpose:** Proactive, parallel health scanning across all agents with alert-only reporting. Designed for scheduled cron execution (e.g., every 15 minutes) to detect systemic failures before they become incidents.

**When to use:**
- Automated watchdog cron job running health checks
- Need to verify all agents are operational with minimal noise
- Suspecting correlated failures (shared provider outages, API key issues)
- Require silent success reporting (only alert on problems)

**Workflow — Parallel Check → Aggregate → Alert-or-Silent:**

```bash
#!/usr/bin/env bash
# watchdog-health-check.sh — Multi-agent parallel health sweep
# Returns: 0 if all healthy (silent), 1 if issues found (prints alert)

set -euo pipefail

AGENTS=(yoyo dmob desmond gentech)
ALERTS=()

# 1. Parallel process check (all must be running)
for agent in "${AGENTS[@]}"; do
  if ! pgrep -f "hermes.*$agent.*gateway run" > /dev/null; then
    ALERTS+=("${agent}: gateway process NOT running")
  fi
done

# 2. Error pattern scanning — look for systemic failures in last 30 min
# Pattern A: TTS provider failures (ElevenLabs 401, gTTS errors, etc.)
TTS_FAILURES=0
for agent in "${AGENTS[@]}"; do
  count=$(grep -cE 'elevenlabs.*status_code: 401|tts.*failed|ApiError.*401' \
    "/root/.hermes/profiles/${agent}/logs/errors.log" 2>/dev/null || echo 0)
  TTS_FAILURES=$((TTS_FAILURES + count))
done
if [ "$TTS_FAILURES" -ge 4 ]; then
  ALERTS+=("SYSTEMIC TTS FAILURE: ${TTS_FAILURES} errors across agents — ElevenLabs API key likely invalid")
fi

# Pattern B: Telegram connectivity failures (flood control, network errors)
for agent in "${AGENTS[@]}"; do
  if grep -qE 'Telegram.*flood control|Telegram network error|httpx.ReadError' \
    "/root/.hermes/profiles/${agent}/logs/errors.log" 2>/dev/null; then
    ALERTS+=("${agent}: Telegram connectivity issues detected")
  fi
done

# Pattern C: Auth revoked / provider invalid (Nous, Anthropic, OpenRouter)
for agent in "${AGENTS[@]}"; do
  if grep -qE 'Refresh session has been revoked|No Anthropic credentials|Model .* not found|Invalid token' \
    "/root/.hermes/profiles/${agent}/logs/errors.log" 2>/dev/null; then
    ALERTS+=("${agent}: Provider auth/model failure")
  fi
done

# 3. Cron execution verification — check for recent job dispatches
for agent in "${AGENTS[@]}"; do
  if ! grep -qE 'Running job [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' \
    "/root/.hermes/profiles/${agent}/logs/agent.log" 2>/dev/null; then
    ALERTS+=("${agent}: No cron job execution in last hour — possible dispatcher stall")
  fi
done

# 4. Resource health baseline
if [ $(df -h /root | awk 'NR==2 {print $5}' | sed 's/%//') -gt 85 ]; then
  ALERTS+=("DISK PRESSURE: /root >85% used")
fi

# 5. Output — silent if healthy, alert if issues
if [ ${#ALERTS[@]} -eq 0 ]; then
  # STATUS:OK — silent exit as per specification
  exit 0
else
  echo "🚨 Watchdog Alert: Health check failed"
  for msg in "${ALERTS[@]}"; do
    echo "  • $msg"
  done
  exit 1
fi
```

**Key design choices:**
- **Alert-only output:** If all agents healthy, script exits 0 with NO stdout (system can interpret silence as OK). Only problems are printed.
- **Parallel scanning:** All agents checked simultaneously; no sequential dependencies.
- **Pattern-based detection:** Looks for common failure signatures across error logs (401s, network errors, auth revocations).
- **Cron execution proof:** Requires `Running job` log evidence, not just ticker presence.
- **Exit codes:** 0 = healthy (silent), 1 = issues found (alert printed), 2 = script error.

**Alert classification:**

| Severity | Condition | Action |
|----------|-----------|--------|
| RED | Any agent process missing OR no cron executions for 2+ hours | Immediate page |
| YELLOW | Systemic API failure across ≥3 agents (e.g., TTS 401, Telegram flood) | Notify channel |
| INFO | Single agent auth error (Nous/Anthropic) | Ticket for maintainer |

**Integration:** Schedule via cron (e.g., `*/15 * * * * /path/to/watchdog-health-check.sh`). Capture stdout/stderr to log; only email/page on non-zero exit.

**False positive prevention:**
- Do NOT alert on stale `gateway.out` error banners — always use `agent.log` timestamps
- Do NOT alert on `cron ticker started` alone — require `Running job` evidence
- Ignore errors older than 1 hour (use `--since "1 hour ago"` where possible)

**Multi-agent cascade detection:**
If all agents went down within a 2-minute window, look for shared dependency failures:
```bash
# Check if all agents logged errors within same 60s window
for agent in "${AGENTS[@]}"; do
  last_error=$(tail -1 "/root/.hermes/profiles/${agent}/logs/errors.log" | cut -c1-19)
  echo "${agent}: ${last_error}"
done
# If timestamps cluster → shared cause (disk, network, provider outage)
```

**Telemetry:** Consider emitting structured JSON for dashboarding:
```json
{
  "timestamp": "2026-05-02T11:45:00Z",
  "agents_checked": 4,
  "alerts": [
    {"agent": "yoyo", "type": "tts_failure", "count": 12}
  ],
  "status": "YELLOW"
}
```

## Quick Reference

- All 4 agent processes running? `ps aux | grep hermes`
- Gateway logs show recent Telegram activity (last 10 min)?
- Each agent's agent.log contains `cron.scheduler: Running job` entries in last hour?
- No `Refresh session has been revoked` errors in errors.log?
- jobs.json last_run timestamps within schedule expectations?
- No `EOFError: marshal data too short` in recent logs?
- No `cron ticker stopped` without subsequent `started`?

## Decision Matrix

| Condition | Classification |
|-----------|----------------|
| All agents have recent job executions within schedule, no blocking errors | STATUS:OK |
| Some agents have failed cron jobs but ticker still dispatching, auth errors present but not blocking all | YELLOW |
| Any agent with ticker running but zero job executions for >2x expected window, or repeated gateway crashes | RED |

## Common Findings & Remedies

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Ticker running, no jobs dispatched | Cron scheduler thread died silently | hermes gateway restart for affected agent |
| "Refresh session revoked" | Provider OAuth token expired | hermes model to re-authenticate |
| "No Anthropic credentials" | Missing ANTHROPIC_TOKEN env var | Export token, restart agent |
| EOFError marshal data | Corrupted .pyc cache | Delete __pycache__ dirs, restart agent |
| Telegram Bad Gateway | Telegram API outage or rate-limit | Transient; monitor for recurrence |
| Chat not found (Telegram) | Bot not in target group or wrong chat ID | Verify bot membership and TELEGRAM_HOME_CHANNEL |

## Advanced Diagnostics — Systemic Corruption

When basic health checks pass but agents remain degraded, run systematic corruption detection:

**1. Bytecode corruption** (EOFError: marshal data too short):
  - Compare .pyc file sizes to source: `.pyc < 2KB` or `< 10% source size = corrupt`
  - Check Python magic number (first 4 bytes): Python 3.11 expects `0x330d0d0a`
  - Fix: `find /usr/local/lib/hermes-agent -name '__pycache__' -exec rm -rf {} +` then restart all agents

**2. Cron database corruption** (global jobs.db = 0 bytes):
  - Global DB at `/root/.hermes/cron/jobs.db` should be >4KB non-zero
  - Verify with: `sqlite3 /root/.hermes/cron/jobs.db "PRAGMA integrity_check;"`
  - If 0 bytes or integrity_check fails, cron subsystem dead — requires daemon restart

**3. Coordinated gateway restarts** (all agents crash within seconds):
  - Extract gateway stop/start events from each agent's gateway.log
  - Correlate timestamps — if all within 2-minute window, suspect shared dependency outage
  - Common triggers: disk pressure (82%+ used), auth expiry (Nous Portal), network partition

**4. Credential pool exhaustion**:
  - Inspect each agent's `auth.json` → `credential_pool` entries
  - `last_status: "exhausted"` = quota exceeded; `last_status: null` = never validated
  - Missing key in `.env` but present in credential_pool → stale config; restart agent to re-read env

**5. Error pattern taxonomy**:
  - `sqlite3.OperationalError: database disk image is malformed` → kanban DB or session DB corrupted; export data, delete db, restart to recreate
  - `openai.NotFoundError: 404` → model name invalid; check `OPENROUTER_MODEL` or `DEFAULT_MODEL` env vars
  - `elevenlabs.core.api_error.ApiError: status_code: 401` → ElevenLabs key invalid; rotate key in `.env`
  - `telegram.error.BadRequest: Chat not found` → bot not member of target group; add bot or correct chat ID

Use the `detect-systemic-failure.py` script for automated scanning of all these patterns.

## Post-Diagnosis Actions

1. If cron stuck: Stop ticker, restart gateway process
2. If auth errors: Re-authenticate affected provider(s), clear last_error from jobs.json by allowing job re-run
3. If corrupted cache: Clear pyc, restart agent
4. If credentials missing: Add to .env or config.yaml, restart agent
