# Handoff Board Conventions — Table Format & Enforcement

## File Location
`11-Mess Hall/handoff-board.md`

## Table Columns
| Column | Description | Example |
|--------|-------------|---------|
| From | Sender agent or role | `Gentech`, `Jordan`, `Dmob`, `Desmond` |
| To | Recipient agent or role | `DMOB`, `YoYo`, `Desmond`, `Jordan` |
| What | Brief task description | `DeFi Milestone Cron consolidation` |
| Priority | P0/P1/P2 or High/Medium | `P0`, `High` |
| Status | Current handoff state (see below) | `🚀 Pending Ack` |
| Assigned | Date assigned | `May 2` |
| Ack Deadline | UTC deadline for acknowledgment | `May 2 23:59 UTC` |
| Notes | Ref links, context, approvals | `Ref: 03-Strategies/...` |

## Status Values
- `🚀 Pending Ack` — Handoff sent, awaiting recipient acknowledgment (within 5 min)
- `⏳ Pending` — Queued, no immediate deadline (backlog item)
- `🟡 Claimed` — Recipient acknowledged, actively working
- `✅ Completed` — Work done, delivered
- `🔴 ESCALATED` — Unclaimed past deadline, flagged to Jordan
- `❌ Cancelled` — Dropped/withdrawn

## Enforcement Rules (from board header)
```
- ACK deadline: 5 min from assignment
- Escalation: 15+ min no ACK → flagged to Jordan
- Stalled check: 24+ h claimed with no progress → flagged for review
- Monitor: Cron job d31c330959de runs every 15 min, checks board, enforces silently
```

## Escalation Chain
1. **0–5 min:** Handoff in `🚀 Pending Ack` state
2. **5–15 min:** If still unclaimed → Gentech sends nudge privately
3. **15+ min:** → Escalated to Jordan (status becomes `🔴 ESCALATED`)
4. **24+ min claimed no progress:** → Flagged for review (possible reassignment)

## Example Row
```markdown
| Gentech | DMOB | DeFi Milestone Cron: Add 5-min breakout confirmation, efficiency≤30% immediate alert, bid-ask edge strategy | P0 | 🚀 Pending Ack | May 2 | May 2 23:59 UTC | Ref: 03-Strategies/Defi-Monitor/defi-milestone-enhancements-2026-05.md |
```

## Reading the Board (Agent Protocol)
1. Check this board at **session start** before any other work
2. If tagged for you → update status to `🟡 Claimed` immediately
3. Complete work → update to `✅ Completed` with deliverable link
4. If blocked → comment in notes, escalate per rules

## Common Pitfalls
- **Weekend/holiday:** Agents OFFLINE → handoffs remain unacknowledged until next session
- **Deadline timezone:** All deadlines UTC; convert from local
- **Status drift:** Always update board; never assume someone knows you're working
- **Multiple handoffs:** Claim all before starting work; order by Ack Deadline

## Integration with Daily Log
- Escalated handoffs appear in daily log's "## ⚠️ Key Decisions" or "## 🔓 Open Items"
- P0 handoffs trigger RED ALERT in mid-shift executive summaries
- Completion updates should be reflected in next day's daily log

## Related Files
- `11-Mess Hall/agent-coordination-board.md` — agent check-in status
- `09-Green Room/active-handoffs/` — full handoff documents (context, spec, acceptance criteria)
- `08-Daily/YYYY-MM-DD.md` — daily escalation outcomes
