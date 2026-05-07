---
title: Mid-Shift Coordination Check — Reference Paths
date: 2026-05-02
source: Gentech (CEO) — mid-shift coordination run
purpose: File locations and pattern checklist for rapid org health assessment
---

## Core Check Paths

| What to Check | Canonical Path | What to Look For |
|---------------|----------------|------------------|
| Latest rotation log | `11-Mess Hall/YYYY/WXX/rotation-log-*.md` (most recent by date) | Active discussions carried forward, flags updated, stale items noted |
| Today's context | `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/today-context.md` | Today's agenda, flags, blocker list |
| Agent coordination board | `11-Mess Hall/agent-coordination-board.md` | All agents should have recent check-in; `OFFLINE` without timestamp = stale |
| Handoff board | `11-Mess Hall/handoff-board.md` | Unclaimed items past ACK deadline (5–15 min) → escalation path; items >24h = stalled |
| Master todo | `09-Green Room/master-todo.md` | Last updated date; missing recent scope changes = needs refresh |
| Active handoffs (current) | `09-Green Room/active-handoffs/` | Recent dated files (last 48h) requiring action |
| Active handoffs (stale) | `10-Archive/green-room-handoffs/` | Older handoffs that may need resolution or DROP decision |
| Vault sweep reports | `11-Mess Hall/vault-sweep-*.md` | Health score trends; pending action items for stakeholder |
| Green Room active files | `09-Green Room/*.md` (non-Archive) | Files modified in last 24–48h indicate active coordination |
| Agent state archives | `10-Archive/Agent-States-April/` or `10-Archive/Memory-Backups/` | Historical reference only; not active |

## Pattern Recognition

### Overload signal
- Single agent appears as `OWNER` on ≥2 P0 tasks in `task-board.md` AND has open handoffs assigned → Capacity exceeded

### Handoff stall pattern
- Status `⏳ Pending` + `Ack Deadline` in past + no `Claimed At` timestamp → Auto-escalation candidate
- Age calculation: `today - assigned_date` > 12h → Route to Jordan for DROP/reschedule

### Coordination degradation
- All agents `OFFLINE` on coordination board + no recent Mess Hall posts → Process breakdown; HQ must nudge all
- Rotation logs showing same stale flags for ≥3 days → Systemic issue requiring Jordan intervention

### Todo staleness
- `master-todo.md` `Last updated` >2 days old during active sprint (P0 items still open) → Assign refresh to responsible agent (usually Desmond or Gentech)

## File Path Conventions

- **Mess Hall daily notes**: `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/{today-context.md,rotation-log-*.md}`
- **W18 = week of Apr 27–May 2, 2026**; ISO week number meets sprint cadence
- **Green Room**: active coordination workspace; `active-handoffs/` holds uncompleted current handoffs
- **Archive**: `10-Archive/` holds historical context; reference only, never edit for current work

## Agent Process Verification (if coordination board unreliable)

```bash
# Check running Hermes agents
ps aux | grep hermes | grep -v grep

# For each agent PID, check elapsed time (should be running if expected online)
ps -p <PID> -o pid,stat,etime,cmd
```

Process names:
- `--profile desmond` → Entertainment
- `--profile dmob` → Labs
- `--profile yoyo` → Strategies
- `--profile gentech` → HQ / CEO

---
*Generated from 2026-05-02 mid-shift coordination check*
