# Late-Shift Wrap-Up Coordination Checklist

**Trigger:** End-of-day (after 12:00 UTC) or third break coordination during hackathon sprint weeks.

**Goal:** Ensure continuity between early/late shifts, surface stale handoffs, verify agent check-ins, and flag carry-over items for next day.

## Sequence

1. **Scan early shift activity**
   - `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/today-context.md` — read for agenda + flags
   - `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/rotation-log-*.md` — see what was archived/rotated
   - Any `00-HQ/Operations/YYYY-MM-DD-*.md` created today — check for deliverables

2. **Verify agent presence**
   - `agent-coordination-board.md` — check all agents ONLINE/OFFLINE + timestamp
   - If all OFFLINE with no timestamps → run process check: `ps aux | grep hermes`
   - If processes running but board shows OFFLINE → **must correct immediately**
   - Post in HQ if any agent unresponsive >2h during sprint crunch

3. **Handoff board health check**
   - `handoff-board.md` — filter for Status = ⏳ PENDING or 🟡 IN PROGRESS
   - Identify aging items:
     - Unclaimed >24h → escalate to Jordan
     - Approved but not claimed within 2h → nudge
   - Cross-reference with `09-Green Room/active-handoffs/` for recent activity

4. **Master todo freshness**
   - Read `09-Green Room/master-todo.md`
   - If `last_updated` field or last mod >2 days during sprint → assign refresh
   - If stale, note owner in wrap-up summary

5. **Sprint priority audit**
   - Confirm primary sprint items visible on task-board.md
   - Update any status changes that occurred today but not reflected

6. **File system loose ends**
   - Check Mess Hall root for stray `.md` files → archive if today's discussion
   - Confirm no incomplete notes in `09-Green Room/` without due dates

7. **Carry-over list**
   - Create bullet list of items NOT completed today due to time/blockers
   - Assign owners + due dates for tomorrow
   - Add to tomorrow's `today-context.md` agenda during early shift

8. **Status post to Mess Hall**
   - File: `11-Mess Hall/2026/WXX/YYYY-MM-DD/late-shift-wrap-up.md` (or third-break-summary)
   - Include: completed items, blockers, carry-over, urgent flags, agent check-in status
   - Forward-looking hook: "This is just the beginning..."

## File References

| Pattern | Path | Purpose |
|---------|------|---------|
| Early shift context | `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/today-context.md` | Agenda + flags from early shift |
| Rotation log | `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/rotation-log-*.md` | Archive actions, week context |
| Coordination board | `11-Mess Hall/agent-coordination-board.md` | Agent presence + sprint task table |
| Handoff board | `11-Mess Hall/handoff-board.md` | Inter-agent task handoff tracking |
| Master todo | `09-Green Room/master-todo.md` | Cross-department todos |
| Active handoffs | `09-Green Room/active-handoffs/` | Unclaimed/recent handoffs |
| Ops deliverables | `00-HQ/Operations/` | Analysis or delivery artifacts |
| Wrap-up post | `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/` | Today's wrap-up log |

## Decision Triggers

| Observation | Action |
|-------------|--------|
| All agents OFFLINE, processes running | Immediate correction required; post in HQ |
| Handoffs aging >24h unclaimed | Escalate to Jordan with DROP recommendation |
| DMOB owns >2 P0 items | Flag overload; recommend Jordan triage |
| Master todo stale >2 days | Assign refresh; escalate if not done by EOD tomorrow |
| Weekend (Sat/Sun) + sprint due ≤5d | Assume weekend sprints; confirm availability if unclear |