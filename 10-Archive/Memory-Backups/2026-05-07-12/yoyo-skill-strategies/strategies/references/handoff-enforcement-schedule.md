---
title: Handoff ACK Enforcement Schedule & Monitoring Pattern
updated: 2026-05-03
owner: Gentech (coordination)
applies_to: All agents (DMOB, YoYo, Desmond, Jordan)
---

## Enforcement Rules (2026-04-20 Unified Protocol)

| Rule | Value |
|------|-------|
| ACK deadline | 2 hours from assignment (weekend handoffs relaxed to EOD next day) |
| Reminder | 5–15 min no ACK → reminder written to handoff-board.md |
| Escalation | 15+ min no ACK → flagged to Jordan |
| Stalled check | 24+ h claimed with no progress → flagged for review |
| Enforcement cron | `d31c330959de` runs every 15 min, checks board, enforces silently |

## Pre-Escalation Monitoring Schedule

Each agent should self-monitor using this cadence:

### Every Session Start
1. Read `11-Mess Hall/handoff-board.md`
2. Filter rows where `To` column matches your agent ID
3. For any `🚀 Pending Ack` items:
   - If deadline < 2 hours away → ACK immediately
   - If deadline passed → update to `🔴 Blocked — <reason>` or `🟡 Acknowledged — ETA <date>`

### 3 Hours Before Enforcement Deadline
Scan pending P0/P1 handoffs:
- If still `🚀 Pending Ack` → write reminder comment to board row
- Ping sender in relevant Telegram group (`GenTech HQ`, `GenTech Strategies`, etc.)

### 1 Hour Before Enforcement Deadline
Final check:
- If still unacknowledged → update status to `🔴 ESCALATED`
- Tag `@Jordan` in board update and Telegram
- Copy escalation notice to `11-Mess Hall/escalations/<date>.md`

## Status Field Conventions

| Emoji + Text | Meaning | Action Required |
|-------------|---------|-----------------|
| `🚀 Pending Ack` | Not acknowledged yet | ACK within deadline |
| `🟡 Claimed` | Acknowledged, work in progress | Update with progress notes |
| `🟢 Ready for <owner>` | Completed, awaiting next step | Hand off to recipient |
| `🔴 Blocked — <reason>` | Stuck, needs help | Notify sender + Gentech |
| `🔴 ESCALATED` | Past deadline, Jordan notified | Stop work until Jordan unblocks |
| `✅ Completed` | Fully done | Archive to `10-Archive/green-room-handoffs/` |

## Enforcement Deadlines Calendar (May 2026)

For handoffs submitted on **May 2** (due May 3):
- **ACK deadline**: May 3 13:45 UTC
- **Escalation**: Jordan notified at 13:46 UTC if still `🚀`
- Action: YoYo and DMOB must update `handoff-board.md` by 13:45

For weekend handoffs (submitted Friday–Sunday):
- Extended to **EOD Monday** (23:59 UTC)
- Pre-escalation check Monday 10:00 UTC

## Self-Audit Questions

Before ending any session:
- [ ] Did I read the handoff board today?
- [ ] Are there any handoffs tagged to me that are within 2 hours of deadline?
- [ ] Did I update status fields accurately?
- [ ] Were any completed handoffs moved to archive?

## Related

- `11-Mess Hall/handoff-board.md` — live handoff registry
- `11-Mess Hall/2026/W19/2026-05-03/rotation-log.md` — daily coordination notes
- `strategies/skill.md` → "Handoff ACK Enforcement & Pre-Escalation Monitoring" section
