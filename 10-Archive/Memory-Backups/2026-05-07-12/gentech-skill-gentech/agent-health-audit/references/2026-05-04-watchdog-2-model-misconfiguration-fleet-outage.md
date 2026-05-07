# Watchdog Alert: All Agents Blocked — Model Namespace Misconfiguration Cascade

**Date**: May 4, 2026  
**Severity**: CRITICAL (Fleet-wide outage)  
**Pattern**: Model Provider Deprecation Cascade + Differential Agent Recovery  
**Agents affected**: YoYo, DMOB, Desmond, Gentech (all profiles)  
**Status**: Resolved by config correction and gateway restart

---

## Executive Summary

All four Hermes agents (YoYo, DMOB, Desmond, Gentech) simultaneously failed with `RuntimeError: Error code: 404 — Model 'nousresearch/trinity-large-thinking' not found`. Root cause: fleet-wide model ID namespace misconfiguration — agents configured with `nousresearch/trinity-large-thinking` instead of the correct `arcee-ai/trinity-large-thinking`. No agent completed any task for 3+ hours. Desmond auto-recovered via auxiliary fallback; others remained stuck.

---

## Timeline

| Time (EDT) | Event |
|------------|-------|
| 17:00–21:00 | Gradual error accumulation across all agents (47 YoYo, 23 DMOB, 8 Desmond, 21 Gentech 404 errors) |
| 21:35 Last seen error | YoYo and Gentech still throwing 404; DMOB last INFO at 21:34 showing auxiliary fallback to `nous (stepfun/step-3.5-flash)`; Desmond last INFO at 20:15 also using fallback |
| Post-21:35 | Manual config correction applied; all gateways restarted |
| Post-restart | All agents resumed normal cron execution |

---

## Diagnostic Journey

### Phase 1 — Initial Screening
- Checked recent session transcripts for all four agents: consistent `[IMPORTANT: cron job]` messages, no obvious errors in previews
- Searched full transcript corpus for error keywords: `error`, `exception`, `crash`, `failed`, `traceback`, `timeout`, `connection failed`, `stuck`, `loop`, `hung` — found multiple recent sessions with these patterns

### Phase 2 — Log Deep Dive
Pulled last 100 lines from each agent's `agent.log`:
```
YOYO:  72 errors, 8 tracebacks, 31 "failed" in tail
DMOB:  48 errors, 5 tracebacks, 23 "failed"
DESMOND: 26 errors, 2 tracebacks, 14 "failed"
GENTECH: 23 errors, 5 tracebacks, 5 "failed"
```

**Key finding**: All tails ended with the identical error:
```
RuntimeError: Error code: 404 — {'status': 404, 'message': "Model 'nousresearch/trinity-large-thinking' not found..."}
```

### Phase 3 — Configuration Forensics
Checked all agent config files:
```
/root/.hermes/profiles/yoyo/config.yaml:         default: nousresearch/trinity-large-thinking
/root/.hermes/profiles/dmob/config.yaml:         default: nousresearch/trinity-large-thinking
/root/.hermes/profiles/desmond/config.yaml:      default: nousresearch/trinity-large-thinking
/root/.hermes/profiles/gentech/config.yaml:      default: nousresearch/trinity-large-thinking
/root/.hermes/config.yaml (global):              default: arcee-ai/trinity-large-thinking
```

**Confusion identified**: Global config already used the correct `arcee-ai/` prefix, but each agent's profile config overrode it with the wrong `nousresearch/` prefix.

### Phase 4 — Fleet State Verification
- **Process check**: All 4 gateway processes running (PIDs 865, 872, 880, 882), uptime ~5 hours (started 16:37)
- **Cron execution check**: System cron jobs confirmed running (defi-milestone-tracker and opportunity_scanner_daily output present)
- **Success count**: Zero successful task completions in the last 3 hours for any agent
- **Last log entry analysis**: Each agent's last line was an ERROR (not a recovery INFO), confirming blocked state

### Phase 5 — Recovery Potential Assessment
Examined last INFO line before final crash:
- **DMOB** (21:34): `INFO agent.auxiliary_client: Auxiliary auto-detect: using main provider nous (stepfun/step-3.5-flash)` — had switched to fallback
- **Desmond** (20:15): `INFO agent.auxiliary_client: Auxiliary auto-detect: using main provider nous (stepfun/step-3.5-flash)` — had switched to fallback
- **YoYo** (21:35): Last INFO was 21:35 but still ended in error — fallback may have been attempted but failed
- **Gentech**: Last INFO unclear from tail; final error suggests fallback not engaged

**Interpretation**: DMOB and Desmond likely auto-recovered via auxiliary fallback (different providers cached), while YoYo and Gentech remained stuck due to missing/blocked fallback paths.

---

## Root Cause Analysis

### What Happened
The configured model ID `nousresearch/trinity-large-thinking` does not exist in OpenRouter's catalog. The correct ID is `arcee-ai/trinity-large-thinking` (different organization prefix).

### Why It Cascaded Fleet-Wide
1. All agent profiles overrode the global correct config with an incorrect per-profile model
2. Fallback provider chain (`nous → openai → ollama`) failed because:
   - `nous` provider hit the same 404 (wrong model)
   - `openai` and `ollama` fallbacks were not configured (logged `unknown provider` / `provider not configured`)
3. No agent could initialize an LLM client; all LLM-dependent tasks (cron jobs, message responses) failed immediately

### Why Differential Recovery Occurred
Desmond and DMOB's auxiliary client successfully detected and switched to an available provider (likely `stepfun/step-3.5-flash` from global config inference) before the 404 errors overwrote the log, leaving a last-INFO marker of recovery. YoYo and Gentech either:
- Did not have a viable fallback configured
- Attempted fallback after the error state dominated
- Had the fallback attempt itself fail and not log a recovery INFO

---

## Detection Methodology Used

### 1. Multi-Source Correlation
Cross-referenced:
- Process table (`ps aux`) for liveness
- Log tail patterns (error density, last entry type)
- Configuration files (`config.yaml` model.default)
- Cron execution evidence (output files, session markers)

### 2. Last-Log-Entry Health判定
**Rule**: An agent's health is determined by its **most recent log entry**, not overall error count.
- Last entry = ERROR → agent currently blocked
- Last entry = INFO with recovery keywords (e.g., `Auxiliary auto-detect: using main provider`) → agent likely recovered
- Last entry = WARNING → degraded but may still function

### 3. Hourly Error Density Trends
Grouped errors by hour (`grep '21:'` etc.) to distinguish:
- Historical errors (accumulated but agent recovered since)
- Active errors (present in latest tail)

YoYo and Gentech showed active 404s in the 21:00 hour; DMOB and Desmond showed zero 404s in 21:00 hour.

### 4. Zero-Success Validation
Confirmed no agent had `SUCCESS` or `completed` markers in recent logs. Zero completions across fleet = confirmed outage.

### 5. Configuration Diff Against Global Default
Compared each agent's `config.yaml` against global `~/.hermes/config.yaml` to identify the specific override causing the failure.

---

## Recovery Actions Taken

### Step 1 — Model ID Correction
Updated all agent config files from `nousresearch/trinity-large-thinking` → `arcee-ai/trinity-large-thinking`:

```bash
for agent in yoyo dmob desmond gentech; do
  sed -i 's|nousresearch/trinity-large-thinking|arcee-ai/trinity-large-thinking|' \
    /root/.hermes/profiles/$agent/config.yaml
done
```

### Step 2 — Gateway Restart
Restarted all gateways to pick up new config:
```bash
pkill -f hermes.*gateway
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile yoyo gateway run --replace &
# repeated for dmob, desmond, gentech
```

### Step 3 — Validation
- Verified processes restarted with new PIDs
- Monitored logs for first successful cron job execution
- Confirmed `[cron_<id>]` entries with exit code 0 appeared within 2 minutes

---

## Preventive Measures

### 1. Config Validation Script
Created `scripts/verify_model_config.py` (referenced in skill) to:
- Scan all agent configs for known-bad model IDs
- Optionally query OpenRouter live catalog to verify model existence
- Support `--fix` flag to batch-correct misconfigurations

Run before any scheduled work window:
```bash
python3 /root/.hermes/profiles/gentech/skills/gentech/agent-health-audit/scripts/verify_model_config.py --check
```

### 2. Model ID Allow-List
Suggested future enhancement: maintain an allow-list of approved model IDs per provider in `references/model-catalog-snapshot.md` and validate agent configs against it.

### 3. Health Check Cron
Add a pre-cron gate check that validates model availability before dispatching time-sensitive jobs.

---

## Artifacts Created

- Added this case study to `agent-health-audit` skill references
- Existing scripts enhanced: `verify_model_config.py`, `verify_fleet_health.py`
- Pattern documented: **Model Namespace Misconfiguration Cascade**

---

## Lessons Learned

1. **Last-log-entry > error-count**: A high error count doesn't mean currently blocked; always check the most recent entry
2. **Auxiliary fallback leaves breadcrumbs**: The `Auxiliary auto-detect: using main provider X` INFO line is a strong recovery signal
3. **Global vs profile config divergence**: Global config can be correct while per-agent overrides break everything — always audit both
4. **Model ID namespace matters**: `nousresearch/` vs `arcee-ai/` prefix difference is the difference between 404 and 200; verify against live provider catalog
5. **Zero completions is a red flag**: When no agent completes any task in hours, something is fundamentally broken fleet-wide

---

## Related References

- Skill: `agent-health-audit` — Full diagnostic framework
- Reference: `references/2026-05-04-model-deprecation-fleet-failure.md` — Earlier analysis of model 404 patterns
- Reference: `references/2026-05-04-model-deprecation-cascade-differential-recovery.md` — Differential recovery detection

---

**Status**: RESOLVED — Fleet fully operational after config correction and restart.
