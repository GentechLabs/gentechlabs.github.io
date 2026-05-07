---
name: gentech-watchdog
description: Gentech Watchdog health check procedure — systematic audit of YoYo, DMOB, Desmond, and Gentech agent fleets to detect crashes, stuck processes, missed cron executions, and systemic failures
triggers:
  - keywords: ["watchdog", "health check", "agent status", "gentech audit", "check yoyo dmob desmond gentech", "system health"]
  - intent: "audit Gentech agent fleet"
  - always_required: true  # This skill MUST be loaded for watchdog tasks
related_skills:
  - agent-health-audit
reference_files:
  - references/watchdog-findings-2026-05-06.md
  - references/watchdog-findings-2026-05-07.md
---

# Gentech Watchdog

The Gentech Watchdog is a scheduled cron job that performs comprehensive health checks on the four core Hermes agents: YoYo, DMOB, Desmond, and Gentech. This skill defines the systematic audit procedure to verify operational status and detect issues before they cause downtime.

## Trigger Conditions

This skill MUST be loaded when:
- The cron job `gentech-watchdog` executes (scheduled every 5 minutes)
- User explicitly requests a "watchdog", "health check", or "audit" of the Gentech agent fleet
- Any query that lists the four agents for health review

## Audit Procedure

The watchdog follows a multi-source verification workflow:

### 0. Quick Fleet Overview (run first)
```bash
hermes status
```
This single command shows: model/provider config, all API key states, auth provider status (including Nous Portal revocation), messaging platform health, gateway service status, scheduled job count, and active session count. Use it as the starting diagnostic before deep-diving.

### 1. Gateway Process Verification
```bash
ps aux | grep "hermes_cli.main" | grep -E "yoyo|dmob|desmond|gentech"
```
- All four agents should have active gateway processes
- Check PID, start time, and resource usage
- Look for recent restarts or crashes

### 2. Session Log Freshness Check
```bash
find /root/.hermes/profiles/*/sessions -name "*.jsonl" -mtime -1 | wc -l
```
- Verify that recent sessions exist (within last 24 hours)
- No sessions may indicate cron failures or agent crashes

### 3. Cron Log Analysis
```bash
# Check per-agent cron.log for standalone script errors
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  log="/root/.hermes/profiles/$agent/cron.log"
  if [ -f "$log" ]; then
    tail -20 "$log" | grep -i "error\|fail\|exception\|traceback" | tail -3
  else
    echo "(no cron.log)"
  fi
done
```
- Standalone cron scripts (not Hermes agent runs) write errors to `cron.log`, NOT `gateway.log`
- `gateway.log` captures Hermes agent-level errors; `cron.log` captures script-level crashes (NameError, ImportError, etc.)
- Also check gateway logs for recurring error patterns:
```bash
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  log="/root/.hermes/profiles/$agent/logs/gateway.log"
  if [ -f "$log" ]; then
    tail -30 "$log" | grep -i -E "error|fail|exception|traceback|revoked|404|401|NameError" | tail -5
  fi
done
```
- Pay special attention to:
  - "AAE config missing" (HOME path issues)
  - "Refresh session has been revoked" (auth failures)
  - "No LLM provider configured" (config issues — cron context may differ from interactive gateway)
  - "Couldn't find that, sorry" (vision tool errors)
  - "Flood control exceeded" (Telegram rate limiting — usually transient)

### 3b. Cron Job Status Check
```bash
hermes cron list
```
- Scan the job list for `error:` suffixes on `Last run:` lines
- Error classes to watch for:
  - `No LLM provider configured` — cron daemon context lacks provider config; most common with custom endpoint models
  - `HTTP 429: quota exhausted` — provider rate limit; often transient
  - `401 - API key invalid` — credential expiry/revocation
  - `I/O operation on closed file` — session database corruption
  - `ValueError` / `NameError` — script-level bugs in standalone cron scripts
- Cross-reference error timestamps with known provider outage windows to distinguish systemic vs per-job failures

### 3c. Script Bug Verification
When a script error is found in cron.log, check if the bug has been fixed since:
```bash
# Compare script modification time with last successful cron run
stat -c '%y' /root/.hermes/profiles/<agent>/scripts/<script>.py
# Then check cron.log for success entries after that timestamp
grep "✅\|success" /root/.hermes/profiles/<agent>/cron.log | tail -3
```
If the script was modified after the last error, the bug may already be resolved — verify with the next cron execution.

### 4. Authentication Status Check
```bash
hermes auth status nous
hermes auth status elevenlabs
```
- Ensure primary providers are authenticated
- Re-login if showing "logged out"

### 5. LLM Provider Configuration
```bash
cat /root/.hermes/config.yaml | grep -A10 "llm:"
```
- Verify that a primary LLM provider is configured
- Nous should be the default provider

### 6. Vision Tool Configuration
```bash
cat /root/.hermes/config.yaml | grep -A5 "vision:"
```
- Check provider settings
- Verify endpoint availability

### 7. System Resource Check
```bash
df -h /root
free -h
```
- Ensure sufficient disk space and memory
- Resource exhaustion can cause agent failures

## Success Criteria

The audit passes if:
- All four gateway processes are running
- At least one session exists in the last 24 hours for each agent
- No critical errors in cron logs (AAE config, auth revoked, LLM config)
- Primary auth providers are authenticated
- LLM provider is configured
- System resources are adequate

## Failure Protocol

If any check fails:
1. Log detailed error messages to the watchdog report
2. Send immediate alert to Mess Hall with "🚨 Watchdog Alert"
3. Include specific error messages and remediation steps
4. Continue monitoring while issues are being resolved

## Reporting Format

The watchdog generates a structured report with:
- Executive summary
- Detailed findings with error messages
- Diagnostic commands used
- Recommended remediation steps
- Timestamp and cron job ID

## Integration

This skill is automatically triggered by the Gentech Watchdog cron job. It references the `agent-health-audit` skill for additional audit procedures and uses the `watchdog-findings-2026-05-06.md` and `watchdog-findings-2026-05-07.md` reference files for issue-specific diagnostics.

**Recommended diagnostic flow for watchdog runs:**
1. `hermes status` — quick fleet overview (provider, auth, gateway, jobs, sessions)
2. `ps aux | grep hermes_cli.main` — verify all 4 gateway processes alive
3. `hermes cron list` — scan for `error:` suffixes on job last-run lines
4. Per-agent `cron.log` check — standalone script errors (NameError, ImportError)
5. Per-agent `gateway.log` check — agent-level errors (auth, Telegram, provider)
6. **Temporal comparison** — load previous findings file (`references/watchdog-findings-YYYY-MM-DD.md`) and compare current state against it to distinguish NEW issues from known/ongoing ones
7. **Imminent failure detection** — for each failing cron job, check `Next run:` timestamp. If a job with an unresolved error is scheduled to run soon, it will likely fail again — note this but don't re-alert if already documented
8. Script verification — if script bug found, check modification time vs last success to see if already fixed
9. **Decision gate** — deliver alert or `STATUS:OK` per silence/report rules

## Alert-vs-Suppress Decision Guide

Not every error warrants an alert. Apply this filter:

| Condition | Action |
|-----------|--------|
| New error type not in previous findings | ALERT immediately |
| Same error repeated from previous findings, no fix attempted | SUPPRESS (STATUS:OK) — already documented |
| Error resolved since last findings (job now showing `ok`) | SUPPRESS — resolution is the news, not the old error |
| Imminent failure (failing job scheduled to run today) | SUPPRESS if already documented; ALERT only if this is the first detection |
| Gateway crash / process restart / Telegram disconnect | ALERT immediately regardless of history |
| Auth revocation affecting cron but not gateways | SUPPRESS if gateways healthy and interactive sessions working |

**Rationale:** Re-alerting on known issues wastes Jordan's attention. The watchdog's value is detecting *changes* — new failures, escalations, or resolutions — not restating yesterday's findings.

## Time-Windowed Gateway Log Check

When checking gateway logs for errors, filter to a narrow time window (e.g., last 1 hour) to distinguish fresh errors from stale ones:

```bash
# Check only the last hour of gateway logs
for agent in yoyo dmob desmond gentech; do
  log="/root/.hermes/profiles/$agent/logs/gateway.log"
  if [ -f "$log" ]; then
    grep "$(date -d '1 hour ago' '+%Y-%m-%d %H:')" "$log" | grep -i -E "error|fail|exception" | tail -3
  fi
done
```

Stale errors in the last-30-lines tail may look alarming but are often days old. The time-window check prevents false alarms.

## Maintenance

The skill should be updated whenever:
- New failure modes are discovered
- Diagnostic procedures change
- Remediation steps are improved
- Integration with other tools is added