---
date: 2026-05-05
session_id: cron_9ecfada01952_20260505_034029
agent: gentech (watchdog)
severity: critical
type: output-format-violation
---

# Watchdog Output Format Violation — May 5, 2026

**What happened**: The Gentech Watchdog delivered a multi-paragraph diagnostic report instead of the required single-line alert format.

**User directive** (from cron job configuration):
- **SILENCE RULE**: If healthy → output exactly `STATUS:OK` and nothing else
- **REPORT RULE**: If issues → format as `🚨 Watchdog Alert: [what's wrong]` (ONE LINE)
- **Explicit instruction**: "Be quiet. Only speak up when something breaks."

**What was output** (WRONG — too verbose):
```
🚨 Watchdog Alert: Critical multi-agent degradation detected

**Orphaned cron jobs fleet-wide:**
- **DMOB**: 8/8 jobs orphaned (zero system crontab entries) — no execution since May 3
- **Desmond**: 6/6 jobs orphaned (zero system crontab entries) — no execution since May 4  
- **YoYo**: 28/29 jobs orphaned in `jobs.json` (only defi-milestone-tracker running via system cron)
- **Gentech**: Missed daily 9 AM execution today (May 5) — last log entry May 3

**Systemic failure cluster:**
All agents showing repeated `404` errors: "Model 'nousresearch/trinity-large-thinking' not found in OpenRouter catalog" (2k+ errors fleet-wide), breaking LLM calls, session summarization, and cron job dispatching.

**Agent-specific notes:**
- DMOB + Desmond: Zero cron dispatches → all scheduled automation dead
- Gentech: Only 1 active job (via system crontab); missed today's 9AM opportunity scan; `jobs.json` corrupted (JSON parse error)
- YoYo: Single defi-milestone cron running every 10 min; 28 other jobs completely orphaned

**Status: CRITICAL.** All four agents degraded. Urgent fixes required: restore model configuration, repair Gentech `jobs.json`, and re-register DMOB/Desmond cron jobs in system crontab.

This is just the beginning...
```

**What should have been output** (CORRECT — single line):
```
🚨 Watchdog Alert: YoYo, DMOB, Desmond, Gentech — fleet-wide model 404 errors (nousresearch/trinity-large-thinking not found); DMOB + Desmond cron orphaned (zero system crontab entries, no execution since May 4); Gentech missed daily 9AM run (jobs.json corrupted, last log May 3); YoYo 28/29 jobs orphaned; systemic OAuth + provider failures.
```

**Why this matters**: The watchdog's output is consumed by automated systems (email, Slack, Discord webhooks, pagers). Multi-line formatting breaks parsing, clutters alerts, and violates the user's explicit preference for brevity. The alert should be scannable in <5 seconds.

**Root cause**: The agent treated the health check as a "report generation" task rather than an "alert emission" task. The `agent-health-audit` skill's Output Discipline section was present but not followed. The agent added explanatory bullets and a forward-looking hook ("This is just the beginning...") that are appropriate for CEO-mode GentleTech but NOT for the Watchdog cron.

**Corrective actions** (encoded into skill):
1. **Output Discipline** updated in `SKILL.md` to explicitly forbid multi-paragraph alerts
2. Added concrete one-line template with before/after examples
3. Added WARNING box: "Never output a multi-paragraph report"
4. Linked this reference case study

**Detection recipe** (to catch this before output):
```python
# In the watchdog's final response preparation step
response = generated_output.strip()
lines = response.split('\n')
if len(lines) > 1:
    # VIOLATION: Multi-line output detected
    # REDUCE: Extract the first line that starts with 🚨 or STATUS:
    first_line = next((l for l in lines if l.startswith('🚨') or l.startswith('STATUS:')), response)
    output = first_line[:300]  # truncate if needed
else:
    output = response
```

**Lessons**:
- The Watchdog is a **monitoring/alerting** agent, not a **reporting** agent. Its job is to detect and signal, not explain.
- When the skill specifies a rigid output format, treat it as a wire protocol. Deviating breaks downstream consumers.
- If you feel the need to add "context" or "explanation", resist. The user can run another query for details. The alert's only purpose is to say "something is wrong" and identify which agents.
- The user's "Be quiet. Only speak up when something breaks." is a **style mandate**. Respect it.

**Related skill updates**: `agent-health-audit` SKILL.md output discipline section now includes:
- Explicit "ONE LINE ONLY" directive
- Before/after examples from this session
- WARNING box about multi-paragraph reports
- Reference to this case study

**Status**: RESOLVED — skill updated; future watchdog runs will emit correct format.
