# Today's Context Template

The `today-context.md` file is created daily in the current week's folder (e.g., `2026/W19/2026-05-05/today-context.md`). It serves as the primary situational awareness document for each day.

## Purpose
- Provide a quick overview of current sprint status
- Highlight critical issues and escalation triggers
- List action items for the day/week
- Document decisions and rationale
- Serve as a handoff document between shifts

## Standard Sections

### 📅 Date & Sprint Info
- Date, week number, sprint theme
- Countdown timers for upcoming deadlines

### 🔴 Critical Issues & Escalations
- Most urgent items requiring immediate attention
- Clear escalation triggers with deadlines
- P0/P1 priorities

### 🟡 High Priority Items
- Important but not critical items
- Overdue deliverables
- Medium-risk items

### 🟢 Active Projects Snapshot
- Current status of major initiatives by department
- Key metrics and progress indicators
- Responsible agents

### 📊 System Health
- Infrastructure metrics (disk space, agent status)
- System alerts or warnings
- Health check results

### 🎯 Today's Action Items
- Immediate tasks (due today)
- This week's priorities
- Follow-up items from previous days

### 🔗 Important Links
- Cross-references to related vault documents
- Task board, handoff board, active sprint docs
- Monitoring dashboards

### 🚨 Escalation Triggers
- Specific times and conditions that require escalation
- Clear ownership and deadlines

## Writing Guidelines

1. **Be concise but comprehensive** — Include essential details but avoid unnecessary verbosity
2. **Use clear formatting** — Markdown headers, bullet points, and emoji indicators improve readability
3. **Update in real-time** — As conditions change, update the document to reflect current status
4. **Document decisions** — Include rationale for key decisions in the "Notes" or "Rationale" sections
5. **Flag risks clearly** — Use 🔴 for critical, 🟡 for high, 🟠 for medium, 🟢 for low priority items
6. **Include timestamps** — For critical events or changes, include UTC timestamps

## When to Create
- Created fresh each day during the daily context rotation
- If the day is missed, create it as soon as possible with retrospective information
- Never leave a day blank — even a minimal context is better than none

## When to Archive
- The file remains in the daily folder permanently
- It becomes part of the historical record and may be referenced later
- No need to move or delete — it will be archived with the weekly folder when that week is complete

## Example Structure
```markdown
# 2026-05-05 — Mess Hall Context

## 📅 Date & Sprint Info
- **Date:** May 5, 2026 (Tuesday)
- **Week:** W19
- **Sprint Theme:** Hackathon Homestretch
- **Countdown:** 
  - Solana Frontier: **6 days** (due May 11)
  - Kite AI: **12 days** (due May 17)

## 🔴 Critical Issues & Escalations
### 1. Overdue Handoffs — P0 Escalation Required
**Status:** 4 handoffs overdue since Apr 19-21, blocking multiple workstreams.

| ID | From → To | Task | Priority | Due | Status |
|----|-----------|------|----------|-----|--------|
| H001 | Gentech → Dmob | Dynamic Burn Rate SC Review | P0 | Apr 19 | ⏳ Pending |
...

## 🚨 Escalation Triggers
- **13:45 UTC:** Handoffs still unclaimed → notify Jordan
- **14:00 UTC:** No Solana Frontier status → reassign critical tasks
- **23:59 UTC:** Kite AI scoping not delivered → transfer to Gentech
```

## Vault Location
`11-Mess Hall/2026/W##/YYYY-MM-DD/today-context.md`

## Maintenance
- Created during daily context rotation
- Updated throughout the day as conditions change
- Archived with the weekly folder when the week is complete