---
name: vault-daily-rotation
category: note-taking
description: Daily context rotation for the Gentech vault — archive resolved Mess Hall notes, clear stale Green Room handoffs, keep working spaces clean for the next shift.
---

# Vault Daily Context Rotation

## Silent Run Delivery Protocol

This is a scheduled cron job. The delivery mechanism is automated — **do NOT use send_message or attempt manual delivery**.

**Key instructions:**
- Save all outputs directly to the vault
- Final response is automatically delivered to the job's configured destination
- If there is genuinely nothing new to report, respond with exactly `[SILENT]` (nothing else) to suppress delivery
- Never combine `[SILENT]` with content — either report findings normally, or say `[SILENT]` and nothing more

**Execution mindset:** Work fully autonomously, making reasonable decisions where needed. No user interaction expected or allowed.

## Key Directories

| Path | Purpose |
|------|---------|
| `11-Mess Hall/` | Agent session notes, status updates, daily check-ins |
| `09-Green Room/` | Inter-agent handoffs, specs, research notes |
| `13-Green Room/` | Secondary Green Room (keep clean — README only) |
| `01-Agency/HQ-Working/X-Content/Daily Drafts/` | Daily content drafts |
| `10-Archive/` | Archive destination (date-stamped subdirs) |

## Classification Rules

### Resolved (archive)
- Session notes from completed days with no carry-forward items
- Checkpoints/status updates superseded by newer ones
- Completed handoffs where the recipient has finished the work
- Stale handoff-board entries older than 5 days with no progress
- Past-daily content drafts (>1 day old)

### Active (keep in place)
- Living documents (task-board, handoff-board, coordination-board, approvals, vault-cleanup-log)
- Status items with unresolved blockers or waiting-on dependencies
- Active project status docs (deploy in progress, awaiting review, etc.)
- Concept docs that are still gathering feedback
- Drafts scheduled for posting today/tomorrow

### Stale (archive)
- Handoffs from >5 days ago that were never acknowledged or progressed
- Duplicate specs/concepts superseded by newer versions
- "active.md" or "active-handoffs.md" lists that are outdated

## Execution Steps

### 1. Survey the workspace
```bash
# Mess Hall
find "/root/vaults/gentech/11-Mess Hall" -type f -name "*.md" | sort

# Green Room
find "/root/vaults/gentech/09-Green Room" -type f -name "*.md" | sort

# X-Content drafts
find "/root/vaults/gentech/01-Agency/HQ-Working/X-Content/Daily Drafts" -type f 2>/dev/null | sort
```

### 2. Read file contents to assess status
Read the first 200-300 characters of each file. Look for:
- **Resolved markers:** ✅, "COMPLETE", "done", session summary with no open items
- **Active markers:** ⏳, "blocked", "waiting on", "WIP", "IN PROGRESS", future dates
- **Stale markers:** Old dates (>5 days), "PENDING" with no recent activity, superseded by newer file

### 3. Archive resolved/stale files
```bash
# Create date-stamped archive directories
mkdir -p "/root/vaults/gentech/10-Archive/Mess Hall/YYYY-MM-DD/"
mkdir -p "/root/vaults/gentech/10-Archive/green-room-YYYY-MM-DD-rotation/"

# Move files (use Python shutil.move for reliability)
```

### 4. Clean empty directories
```bash
# Remove Daily Drafts dir if empty after archiving
rmdir "/root/vaults/gentech/01-Agency/HQ-Working/X-Content/Daily Drafts" 2>/dev/null
```

### 5. Update logs
- Create rotation log entry in `10-Archive/Mess Hall/YYYY-MM-DD/rotation-log-YYYY-MM-DD.md`
- Append summary to `11-Mess Hall/vault-cleanup-log.md`

### 6. Commit if repo exists
```bash
cd /root/vaults/gentech && git add -A && git commit -m "🔄 Daily rotation $(date +%Y-%m-%d)" 2>/dev/null
```

## Escalation Protocols & Active Flagging

### Handoff ACK Enforcement
The Gentech coordination protocol requires recipients to acknowledge handoffs within strict deadlines:

- **Enforcement deadline:** Typically 13:45 UTC for handoffs submitted the previous day
- **Pre-escalation check:** 3 hours before deadline, run a pre-escalation check on any P0/P1 handoffs still in `🚀 Pending Ack` status
- **Final reminder:** 1 hour before deadline, write final reminder to board; if still pending, prepare escalation notice to Jordan
- **Automatic escalation:** Past enforcement deadline → board updated to `🔴 ESCALATED` and Jordan tagged

**Monitoring cadence:**
- Every session start — scan handoff board for any handoffs tagged to you; ACK immediately
- Every 15 minutes — cron job `d31c330959de` runs and enforces silently

### Flagging Active Discussions

**Task Board** (`11-Mess Hall/task-board.md`):
- Already contains active sprint items with priority markers (P0, P1, P2)
- Check for status updates: 🟥 ACTIVE, 🟡 HIGH, 🟠 BUILDING
- Review "RISKS & BLOCKERS" section for critical items

**Handoff Board** (`11-Mess Hall/handoff-board.md`):
- Primary source for inter-agent task handoffs
- Status conventions: `🚀 Pending Ack`, `🟡 Claimed`, `🟢 Ready for <owner>`, `🔴 Blocked — <reason>`, `🔴 ESCALATED`
- Check for overdue handoffs (older than 5 days with no progress)

**Today's Context** (`11-Mess Hall/2026/W##/2026-MM-DD/today-context.md`):
- Created daily with current sprint countdown, critical issues, and action items
- Should be referenced at session start for situational awareness

### Active Discussion Checklist
Before completing rotation, verify:
- [ ] Handoff board ACK deadlines not missed (escalation triggers checked)
- [ ] Task board active items still accurately reflect priorities
- [ ] Today's context file created with current sprint status and action items
- [ ] Any critical incidents from previous day documented in today's context

## Weekly Organization Pattern

In the Gentech vault, the Mess Hall uses a **weekly folder structure** for session notes:

- `2026/W##/` — Week number (e.g., W19 for May 5-9, 2026)
  - `2026-05-05/` — Daily subfolders with context files
  - `2026-05-06/` — Next day
  - etc.

**Archive strategy:**
- Weekly folders older than the current week can be archived as a whole when they become inactive
- Current week (W##) should be kept until the week is complete
- When archiving a full week, move the entire `W##` directory to `10-Archive/Mess Hall/YYYY-MM/` using the month of the week's start date

**Example:** Archive W16 (April 14-20) to `10-Archive/Mess Hall/2026-04/W16/`

This pattern keeps the vault organized and makes it easy to locate historical context by week.
