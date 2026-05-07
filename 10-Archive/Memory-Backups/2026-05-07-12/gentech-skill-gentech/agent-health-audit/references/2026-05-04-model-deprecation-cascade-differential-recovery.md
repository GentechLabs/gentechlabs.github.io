# Model Deprecation Cascade with Differential Recovery — 2026-05-04 (Evening)

**Watchdog run**: May 4, 2026 21:05–21:10 UTC  \n**Agents affected**: YoYo, DMOB, Gentech (still failing); Desmond (recovered)  \n**Severity**: Critical — fleet partially functional  \n**Duration**: ~6.5 hours from initial failure to partial recovery  \n**Status**: PARTIAL RECOVERY (Desmond only, as of 21:10)

---

## What Happened (Updated Timeline)

Building on the earlier May 4 14:40 model-deprecation incident, this follow-up check revealed a **bifurcated recovery state** across the fleet:

- **14:40 UTC** — Initial failure: All agents began throwing `Model 'nousresearch/trinity-large-thinking' not found (404)` errors (2529 total log entries)
- **14:40–20:15** — YoYo, DMOB, Gentech remained in continuous failure state; cron jobs aborting every 5–60 min depending on schedule
- **20:15:17** — **Desmond auto-recovered**: Log shows successful switch to auxiliary provider:  
  `INFO agent.auxiliary_client: Auxiliary auto-detect: using main provider nous (stepfun/step-3.5-flash)`  
  Subsequent cron jobs expected to resume normal operation
- **21:05–21:10** — Watchdog re-check: YoYo, DMOB, Gentech still failing; last log entries are 404 errors; Desmond showing recovered state

**Key discovery**: Auto-recovery is **not simultaneous** across agents. Desmond's gateway autonomously failed over to an alternative provider (stepfun/step-3.5-flash) while the other three agents remained stuck on the deprecated model ID, repeatedly attempting and failing every scheduled interval.

---

## Root Cause (Confirmed)

Same root cause as earlier incident: **incorrect model ID prefix** in agent config.yaml files.

- **Wrong**: `nousresearch/trinity-large-thinking`
- **Correct**: `arcee-ai/trinity-large-thinking`

Why the differential recovery? Investigation suggests:

1. **Desmond had an alternative provider configured** (`stepfun/step-3.5-flash`) with valid credentials, and the auxiliary auto-detection logic successfully fell back when the primary (nous/trinity) failed
2. **YoYo/DMOB/Gentech** either:
   - Had no fallback provider configured, OR
   - Had fallback providers present but with missing/invalid credentials, OR
   - Their auxiliary auto-detection did not trigger within the 6.5-hour window (timing-dependent behavior)

The auto-detection appears to be **opportunistic** rather than immediate — it may only engage when a request is processed and the primary provider fails, which depends on cron schedule timing and gateway uptime.

---

## New Detection Patterns Identified

### 1. Stuck Timestamp Signature in Per-Agent Logs

When an agent repeatedly fails on a fixed schedule, its agent.log shows **clusters of entries sharing identical timestamps** (to the second), indicating rapid-fire sequential failures within the same clock second.

**Evidence** (from log analysis):

| Agent      | Stuck timestamps detected (count ≥ 8)                      |
|------------|------------------------------------------------------------|
| YoYo       | `2026-05-04 20:45:27` (8), `20:50:28` (16), `20:55:29` (9), `21:00:30` (10), `21:00:31` (8), `21:05:32` (8) |
| DMOB       | `16:37:07` (7), `16:37:08` (7), `17:00:12` (8), `18:00:14` (8), `19:00:16` (8), `20:00:18` (8), `21:00:20` (9) |
| Desmond    | `14:41:07` (10), `16:37:08` (8), `16:37:09` (7), `18:00:14` (17) |

These clusters appear at or near the scheduled cron times (e.g., :00, :05, :15 minutes) and reflect multiple error log entries written within the same second — a strong indicator of **repeating, non-recovering failure loops**.

Gentech showed no stuck-timestamp clusters in the last 100 lines, suggesting either fewer recent cron attempts or a different failure mode (possibly fewer scheduled jobs in its profile).

**Diagnostic use**: When checking agent health, if you see multiple log lines sharing the exact same timestamp (especially 5+ entries in one second), treat this as evidence the agent is stuck in a rapid retry loop and is not healthy even if the gateway process appears running.

### 2. Differential Recovery Detection

After identifying a fleet-wide failure pattern, **do not assume uniform recovery**. Check each agent individually for signs of having auto-recovered:

```bash
# Per agent, inspect the last log entry
tail -1 /root/.hermes/profiles/<agent>/logs/agent.log
```

**Auto-recovered indicators**:
- Recent log shows `Auxiliary auto-detect: using main provider nous (stepfun/step-3.5-flash)` or similar fallback provider message
- No recent 404 model errors in the last 10–20 lines
- Cron job execution markers (e.g., `[cron_<id>]`) appear with success status

**Still-stuck indicators**:
- Last log entry is a 404 model error or Traceback
- No successful cron runs since the failure onset
- Log timestamps show stuck-cluster pattern

**Why this matters**: Recovery actions should be targeted. If an agent auto-recovered, no manual intervention is needed for that agent. If stuck, proceed with manual config correction.

### 3. Session-Based Agent Silence Confirmation

Complementary to log analysis, verify agent functional death via session traces:

```bash
latest=$(ls -t /root/.hermes/profiles/<agent>/sessions/session_*.json 2>/dev/null | head -1)
if [ -f "$latest" ]; then
  python3 -c "
import json
with open('$latest') as f:
    d = json.load(f)
roles = [m.get('role') for m in d.get('messages', [])]
print('SILENT' if 'assistant' not in roles else 'RESPONDING')
"
fi
```

Applied to YoYo and DMOB during this check: sessions contained **only `user` role messages** (cron job payloads) with **zero `assistant` responses**, confirming these agents are functionally dead despite running processes.

Desmond's latest session (post-20:15) would be expected to show normal assistant responses if cron jobs resumed.

---

## Updated Recovery Sequence (Model Deprecation Scenario)

When facing fleet-wide 404 model errors:

1. **Initial assessment**: Check last log entry per agent to identify who (if anyone) auto-recovered
2. **For still-stuck agents**:
   a. Verify current model ID: `grep 'default:' /root/.hermes/profiles/<agent>/config.yaml`  
   b. Check OpenRouter catalog to confirm correct ID:  
      `curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models \| jq -r '.data[] | select(.id | contains("trinity")) | .id'`  
      Expected: `arcee-ai/trinity-large-thinking`
   c. **Manual fix required**: Edit config.yaml to replace `nousresearch/` with `arcee-ai/` OR run `hermes model` interactively per agent
   d. Restart agent gateway
3. **For auto-recovered agents**: No action needed; monitor to ensure recovery persists
4. **Validation**: After fixes, re-run the full health audit; expect all agents to show recent successful cron markers and no 404 errors

**Important**: Auto-recovery depend on having a working fallback provider already configured. Do not rely on it as a strategy — manually correct the root misconfiguration across all profiles.

---

## Diagnostic Commands Reference (New Additions)

```bash
# Check for stuck-timestamp clusters in an agent's recent log (last 100 lines)
tail -100 /root/.hermes/profiles/<agent>/logs/agent.log | awk '{print $1" "$2}' | sort | uniq -c | sort -nr | head -20

# One-liner to report per-agent last-log status and model error presence
for a in yoyo dmob desmond gentech; do
  last=$(tail -1 /root/.hermes/profiles/$a/logs/agent.log 2>/dev/null)
  has404=$(echo "$last" | grep -c '404' || echo 0)
  hasRecovered=$(echo "$last" | grep -c 'Auxiliary auto-detect.*stepfun' || echo 0)
  echo "$a: last_entry=$(echo "$last" | cut -c1-19) has_404=$has404 recovered=$hasRecovered"
done

# Session silence check per agent (requires jq)
for a in yoyo dmob desmond gentech; do
  latest=$(ls -t /root/.hermes/profiles/$a/sessions/session_*.json 2>/dev/null | head -1)
  if [ -f "$latest" ]; then
    has_asst=$(jq -e '.messages[] | select(.role=="assistant")' "$latest" >/dev/null 2>&1 && echo yes || echo no)
    echo "$a: $(basename $latest) assistant=$has_asst"
  else
    echo "$a: NO SESSION FILES"
  fi
done
```

---

## Key Takeaway

Model deprecation cascades can produce **heterogeneous outcomes** across a fleet. Always audit each agent individually; never assume "all recovered" or "all still broken" based on a single sample. Combine log analysis (last entry, stuck timestamps) with session trace inspection (role-based silence) for conclusive status determination.

---

**Related skill patterns**:  
- Pattern: Model Provider Deprecation Cascade (core detection/recovery)  
- Pattern: Alive But Degraded  
- Pattern: Agent Silence Detection via Session Analysis  

**Previous reference in this skill**: `2026-05-04-model-deprecation-fleet-failure.md` (earlier May 4 incident, same root cause, earlier time window)
