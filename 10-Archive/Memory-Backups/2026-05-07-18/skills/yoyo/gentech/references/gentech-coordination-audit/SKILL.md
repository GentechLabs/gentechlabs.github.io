---
name: gentech-coordination-audit
domain: devops
tags:
- gentech
- coordination
- team-health
- audit
status: active
version: 0.1.0
description: Systematic coordination board audit and team health check for Gentech org. Validates agent check-in compliance, handoff staleness, and sprint health before breaks or coordination windows.
---

## Purpose

Ensure org coordination hygiene before breaks, handoffs, or sprint transitions. Detect:
- Stale agent check-ins (coordination board not updated)
- Overdue handoffs requiring escalation
- Workload imbalance across agents
- Master todo staleness
- Blocked critical path items

## When to Run

- **Pre-break coordination** (daily standup cadence)
- **Agent session start** (mandatory check-in validation)
- **Sprint transition points** (week boundaries, deadline proximity)
- **After system downtime** (gateway restarts, server maintenance)

## Execution Pattern

### Phase 1 — Agent Presence Verification
Check all agent gateway processes are running:
```bash
ps aux | grep hermes | grep -E '(desmond|dmob|gentech|yoyo).*gateway'
```
Expected: 4 gateway processes (one per agent profile).

### Phase 2 — Coordination Board Audit
Read `11-Mess Hall/agent-coordination-board.md`:
- Verify all agents have updated **Last Check-In** within protocol timeframe
- Verify **Status** column reflects ONLINE/OFFLINE accurately
- Check for stale timestamps (>24h without update)

**If any agent OFFLINE:** Tag in Mess Hall + Gentech escalation.

### Phase 3 — Handoff Escalation Check
Scan `09-Green Room/handoffs` and `active-handoffs/` for items:
- Age > 12h unclaimed → escalate to Jordan
- Age > 24h claimed with no progress → flag for review
- Cross-reference with `handoff-board.md` for priority

**Deadline enforcement:** Cron `d31c330959de` runs every 15 min; manual check should precede break to avoid auto-escalation surprises while offline.

### Phase 4 — Sprint Health Assessment
Read `11-Mess Hall/today-context.md` for:
- Active discussions with 🔴 CRITICAL priority
- Due dates within 48h requiring immediate action
- Weekend/holiday work cadence clarification

Verify master todo (`09-Green Room/master-todo.md`) includes all recent scope changes. If stale (>3 days), flag for refresh.

### Phase 5 — Resource Load Balancing
Identify agents with >2 concurrent critical (P1) items. Flag overload to Gentech for triage.

## Output Format

Post findings to `11-Mess Hall/<date>/pre-break-coordination-check.md` with sections:
1. Agent Status Summary (table)
2. Urgent Flags (P0/P1/P2 priority)
3. Handoff Escalation List (IDs, age, recommended action)
4. Sprint Blockers (critical path items)
5. Recommendations (who needs to do what before break)

Use the Standard Flag Legend:
- 🔴 P0 — System health/coordination degraded
- 🟡 P1 — Blocked handoffs or overdue items
- 🟢 P2 — Process gaps, non-urgent
- ✅ Clear — Items verified healthy

## Escalation Path

1. Agent-level issue → agent handles directly
2. Coordination failure (no check-in after 2 reminders) → escalate to Gentech
3. Handoff staleness (>12h unclaimed) → escalate to Jordan
4. Systemic overload (multiple P1s on single agent) → Gentech triages workload

## Common Pitfalls

- **Assuming process running = agent available:** Gateway process may be alive but agent not actively checking coordination board. Always verify Last Check-In timestamp.
- **Missing weekend cadence:** Saturdays/Sundays require explicit "weekend sprint" or "Mon catch-up" confirmation before proceeding.
- **Handoff board vs active-handoffs mismatch:** Always cross-check both; stale entries can linger in `active-handoffs/` even after completion.
- **Silent cron escalation:** The enforcement cron runs autonomously. Run this BEFORE the cron fires to avoid surprise escalations while offline.

## Related Skills

- `gentech-agent-health-diagnosis` — individual agent gateway troubleshooting
- `gentech-agent-reactivation` — recovery procedures for offline agents
- `kanban-orchestrator` — sprint task decomposition and tracking
