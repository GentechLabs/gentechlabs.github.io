---
name: gentech-enterprise-agent-monitoring
domain: devops
tags:
  - gentech
  - monitoring
  - health-check
  - operations
  - cron
status: active
version: 0.1.0
description: >-
  Systematic operational health monitoring for Gentech enterprise agents
  (YoYo, DMOB, Desmond, Gentech). Detects stale executions, authentication
  failures, service degradation, and process liveness through cron output
  analysis, error log inspection, and gateway verification.
---

## Purpose

Detect and diagnose operational failures in Gentech AI agents before they impact delivery. This skill provides a repeatable health check pattern that identifies:

- **Cron staleness** — agents not executing scheduled tasks
- **Authentication breakdowns** — revoked tokens, missing credentials, API key expiry
- **Service degradation** — external API failures (ElevenLabs, Anthropic, etc.)
- **Process health** — zombie gateways, hung sandboxes, resource exhaustion
- **Log accumulation** — error flood detection

## When to Run

- **Scheduled watchdog cadence** (every 4–6 hours during business hours)
- **Pre-meeting/or sync validation** (confirm all agents are alive before coordination)
- **Post-deployment** (after credential rotation, gateway updates)
- **Alert-triggered** (when handoffs go stale or sprint items block)

## Execution Pattern

### Phase 1 — Cron Execution Staleness Check

Inspect `/tmp/<agent>_cron.txt` files for last successful run timestamps.

**Command:**
```bash
for agent in desmond dmob gentech yoyo; do
  echo "=== $agent ==="
  grep -i "Last run:" /tmp/${agent}_cron.txt | tail -1
done
```

**What to look for:**
- Timestamp older than 24h → **STALE** (agent not executing)
- Error suffix after timestamp → note the failure mode
- Missing cron file altogether → agent never initialized

**Pattern:** `Last run: TIMESTAMP STATUS` where STATUS is `ok` or `error: MESSAGE`

**Red flags:**
- `RuntimeError: Refresh session has been revoked` → re-authenticate via `hermes model`
- `No Anthropic credentials found` → set `ANTHROPIC_TOKEN` or run `claude /login`
- `Agent completed but produced empty response` → model timeout/misconfiguration

### Phase 2 — Gateway Process Liveness

Verify gateway processes are running (they should be, even if cron is stale):

```bash
ps aux | grep hermes_cli.main | grep -E '(desmond|dmob|gentech|yoyo).*gateway'
```

Expected: 4 processes, each in `Ssl` sleep state with stable memory (~700–900 MB RSS).

**Check:**
- Process present? ✓
- CPU% reasonable (<2% idle)? ✓
- Memory stable? ✓
- Age (`etime`) matches expected uptime? ✓

If process missing → agent gateway down, requires restart.

### Phase 3 — Error Log Accumulation

Check `/tmp/*_errors.txt` for ballooning size (>150KB indicates repeated failures).

```bash
ls -lh /tmp/*_errors.txt 2>/dev/null | awk '$5+0 > 150 {print}'
```

If found, inspect recent lines:
```bash
tail -500 /tmp/dr_errors.txt | grep -i "error\|exception\|traceback" | tail -10
```

**Key exception types:**
- `RuntimeError: Event loop is closed` → asyncio cleanup issue (non-blocking but noisy)
- `elevenlabs.core.api_error.ApiError: 401` → TTS API key invalid
- Model auth errors → `hermes model` re-auth needed

### Phase 4 — Service-Specific Failure Detection

**TTS/GenAI services:** Scan syslog for ElevenLabs/Anthropic failures in last 15 min:

```bash
tail -100 /var/log/syslog | grep -iE '(elevenlabs|anthropic).*(error|401|403|failed)'
```

**Telegram connectivity:** Verify no connection errors in gateway logs (check Hermes telemetry).

**Cron scheduler:** Confirm cron daemon is active and hermes crontab exists:
```bash
crontab -l | grep hermes
# Should show entries; if empty, agent cron not installed
```

### Phase 5 — Sandbox/Subprocess Hang Detection

Check for runaway sandbox processes with high CPU:

```bash
ps aux | awk '$3 > 60 && /python.*script.py/ {print}'
```

If found, inspect parent PID to identify which agent spawned it. Kill if orphaned (`kill -9 PID`).

### Phase 6 — Socket/Availability Verification

Hermes agents use Unix domain sockets for RPC. Check for stale socket files in `/tmp/hermes_rpc_*.sock`. Presence without active listener → stale gateway restart needed.

## Output Format

Report in **Machine-Parseable Table** (for scripting) or **Human Summary** (for Mess Hall).

**Table template:**
```
AGENT | CRON_STALE | GATEWAY_UP | AUTH_OK | LAST_ERROR | HOURS_AGO
------|------------|------------|---------|------------|---------
Yoyo  | YES (>24h) | RUNNING    | FAILED  | 401 TTS    | 51
DMOB  | YES (>72h) | RUNNING    | FAILED  | Revoked    | 193
...
```

**Flag legend:**
- 🟢 HEALTHY (cron <24h, gateway up, no recent errors)
- 🟡 DEGRADED (cron stale but gateway alive, recoverable)
- 🔴 CRITICAL (cron dead >72h, auth revoked, or gateway down)
- ⚪ UNKNOWN (missing data, check manually)

## Recovery Playbook Mapping

| Failure Mode | Recovery Skill |
|--------------|----------------|
| `Refresh session has been revoked` | `gentech-agent-reactivation` |
| `No Anthropic credentials found` | `gentech-agent-reactivation` (auth setup) |
| Gateway process missing | `gentech-agent-reactivation` (restart) |
| Cron file missing | `gentech-agent-reactivation` (reinstall cron) |
| TTS 401 errors | Update ElevenLabs API key in agent environment |
| Error log ballooning | Investigate specific exception via `gentech-agent-health-diagnosis` |

## Common Pitfalls

- **Gateway running ≠ cron executing:** Gateway process may stay alive but cron scheduler disabled or credential-expired. Always check cron file timestamps.
- **Stale cron output files:** `/tmp/<agent>_cron.txt` may contain OLD data if agent hasn't written recently. Verify file mtime matches last run timestamp.
- **Error log noise vs signal:** `RuntimeError: Event loop is closed` is benign cleanup noise; ignore. Actual failures have "error:" or "ApiError" prefixes.
- **Sandbox CPU spin:** High-CPU sandbox process often is a self-diagnostic script (like this watchdog) running inside Hermes. Check command line before killing.
- **Socket file residue:** `/tmp/hermes_rpc_*.sock` files persist after gateway crash. Delete when restarting gateway.

## Automation Hook

This check can be wrapped as a Hermes cron itself (e.g., `gentech-enterprise-health-watchdog`) to automatically post alerts to Mess Hall or Telegram when agents go stale.

**Suggested schedule:** Every 4 hours.

## Related Skills

- `gentech-coordination-audit` — task/handoff coordination health (workflow layer)
- `gentech-agent-health-diagnosis` — Hermes infrastructure gateway troubleshooting
- `gentech-agent-reactivation` — recovery procedures for offline agents
