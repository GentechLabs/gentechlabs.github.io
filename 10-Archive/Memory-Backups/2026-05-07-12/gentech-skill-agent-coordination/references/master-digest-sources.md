# Master Digest Intelligence Sources — Quick Reference

## Query Order (Run in sequence)

### 1. Session Search
```bash
session_search(limit=5, query="HQ OR Strategies OR Labs OR Creative OR YoYo OR DMOB OR Desmond recent activity")
```
Purpose: Get high-level summaries of recent activity across all groups.

### 2. Mess Hall Daily Files
- `/root/vaults/gentech/11-Mess Hall/daily/YYYY-MM-DD-morning-handoff.md`
- `/root/vaults/gentech/11-Mess Hall/YYYY/WXX/YYYY-MM-DD/today-context.md`
- `/root/vaults/gentech/11-Mess Hall/YYYY/WXX/YYYY-MM-DD/rotation-log-YYYY-MM-DD.md`

### 3. Green Room Activity
- `/root/vaults/gentech/09-Green Room/active-handoffs/` — list all files, read each
- `/root/vaults/gentech/09-Green Room/*YYYY-MM-DD*.md` — last 24h activity

### 4. Coordination & Task Boards
- `/root/vaults/gentech/11-Mess Hall/task-board.md`
- `/root/vaults/gentech/09-Green Room/agent-coordination-board.md`
- `/root/vaults/gentech/11-Mess Hall/handoff-board.md` (if exists)

### 5. Sprint Plans
- `/root/vaults/gentech/02-Labs/sprint-plan-*.md`
- `/root/vaults/gentech/02-Labs/Hackathons/Active/*.md`

### 6. Master Todo
- `/root/vaults/gentech/09-Green Room/master-todo.md` — check `last_updated` date

### 7. Active Workspace Scan
- `/root/workspace/` — check for recent Solana/Kite activity
- `/root/vaults/gentech/02-Labs/Hackathons/Active/` — count active tracks

## File Age Detection Pattern

For staleness checks:
```bash
find /root/vaults/gentech/09-Green Room -name "*.md" -mtime -1  # last 24h
find /root/vaults/gentech/11-Mess Hall -name "*.md" -newermt "YYYY-MM-DD"
```

Read `## 📋 Today's Agenda` and `## ✅ Yesterday's Highlights` sections for immediate context.

## Handoff Age Calculation

Extract date from filename: `YYYY-MM-DD-description.md`
```python
from datetime import datetime, timezone
handoff_date = datetime.strptime(filename[:10], "%Y-%m-%d")
age_days = (datetime.now(timezone.utc).date() - handoff_date.date()).days
```
- Age ≥13 days: CRITICAL (Apr 19–21 items on May 2)
- Age 5–12 days: URgent
- Age 1–4 days: Pending (normal)

## Critical File Locations Map

| Intel Type | Primary Source | Secondary Source |
|------------|----------------|------------------|
| Daily agenda | `today-context.md` → `## 📋 Today's Agenda` | `morning-handoff.md` |
| Completed items | `today-context.md` → `## ✅ Yesterday's Highlights` | rotation log |
| Flags | `today-context.md` → `## 🚩 Flags` | Green Room handoffs |
| Sprint scope | `sprint-plan-*.md` | hackathon readme files |
| Agent status | `agent-coordination-board.md` → `Agent Session Check-In` table | Mess Hall check-ins |
| Handoff health | `active-handoffs/` directory + handoff-board.md | Green Room last 24h posts |
