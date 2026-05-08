# Vault Path Reference — Handoff Reporting

Quick lookup for which vault folders contain what during shift handoff scanning.

## Root
`/root/vaults/gentech/`

## Key Folders

| Folder | Purpose | scan? |
|--------|---------|-------|
| `08-Daily/` | Daily operator logs by date (YYYY-MM-DD.md) | ✅ Always |
| `11-Mess Hall/` | Team discussions, decisions, context (year/W##/) | ✅ Always |
| `09-Green Room/` | Cross-team handoffs, debates, open questions | ✅ Always |
| `00-HQ/Approvals/` | Explicit Jordan approval requests | ✅ Always |
| `03-Strategies/` | YoYo's strategy work, configs, scripts | 🔍 For recent changes |
| `03-Projects/` | DMOB Labs + Desmond Creative project work | 🔍 For recent changes |
| `10-Archive/` | Historical items (do NOT treat as active) | ❌ Skip unless investigating |
| `00-Working/` | Temporary scratch space | ⚠️ Check for pending items |
| `02-Labs/` | Bug bounties, contest scans | 🔍 If deadline-driven |
| `06-Content/` | Published content drafts (X threads, articles) | ⚠️ Only if content pending review |

## Active vs Archive Pattern
- **Active items**: Live in `active-handoffs/` subdirectory (Green Room) or top-level folders
- **Archived items**: Moved to `10-Archive/` or `10-Archive/green-room-handoffs/` — treat as resolved

## Date/Time Conventions
- Week folders: `2026/W18/` (ISO week, Monday start)
- Daily logs: `08-Daily/2026-05-02.md`
- Eastern time (UTC-4) assumed for shift boundaries

## Frontmatter Keys to Extracts
```yaml
date: YYYY-MM-DD
type: today-context | discussion-thread | handoff
status: current | pending | approved | blocked
author: Agent name
```
These help filter and sort items quickly.

---
*Used by `handoff-reporting` skill*