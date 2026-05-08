# Vault Topology — GenTech Labs (as of 2026-05-04)

**Scope:** Daily second brain sync routing — where files actually live.

## Quick Map (Daily Sync视线)

| What | Where | Notes |
|------|-------|-------|
| Daily summary digest | `11-Mess Hall/daily/YYYY-MM-DD-summary.md` | Auto-curated, 7-day retention |
| Daily context folder | `11-Mess Hall/YYYY/W##/YYYY-MM-DD/` | ISO week layout; contains `today-context.md` |
| Working memory | `00-Working-Memory.md` | Single source of truth for sprint state |
| Active handoffs | `09-Green Room/active-handoffs/` | Dated filenames `YYYY-MM-DD-*.md` |
| All handoffs board | `11-Mess Hall/handoff-board.md` | Master table |
| Coordination board | `11-Mess Hall/agent-coordination-board.md` | Org-wide status, escalation paths |
| Task board | `11-Mess Hall/task-board.md` | Sprint priorities by agent |
| DeFi LP tracker | `09-Green Room/LP Scout — IL Tracker vs HODL & Stake.md` | Primary LP signal (IL, efficiency, fees) |
| D5 milestone | `09-Green Room/D5-Strategy-Engine-Evolution.md` | Milestone ladder + state machine |
| LP snapshots | `09-Green Room/lp-status-*.md` | Timestamped position captures |
| D5 analysis | `09-Green Room/d5-*.md` | Cron bugs, consolidation memos |
| Labs queue | `02-Labs/Labs-Queue.md` | Dmob's active task list |
| Hackathons active | `02-Labs/Hackathons/Active/` | Current hackathon folders |
| Swarms adapter | `02-Labs/Swarms-Solana-Adapter.md` | Build status, gaps |
| Content queue | `06-Content/Queue/CONTENT-QUEUE.md` | Desmond's pending content |
| X drafts | `06-Content/X-Drafts/` | Unpublished social posts |
| Research | `03-Strategies/` | YoYo's competitive intel, research |
| Dev blog | `04-Entertainment/dev-blog/` | Long-form posts |
| Weekly summaries | `08-Logs/2026-W##.md` | Week rollups |
| HQ summaries | `00-HQ/Summaries/` | Jordan-curated summaries |

## Legacy Paths (DO NOT USE)

| Old Path | Status | Replacement |
|----------|--------|-------------|
| `08-Daily/` | ❌ Deprecated → renamed to `08-Logs/` | Use `11-Mess Hall/daily/` |
| `03-Projects/DeFi/` | ❌ Moved to `09-Green Room/` | Use `09-Green Room/(LP Scout\|D5-Strategy-Engine-Evolution).md` |
| `01-Agency/` | ❌ Split into `00-HQ/`, `01-Agents/`, `09-Green Room/` | See INDEX.md |

## Week Folder Convention

Vault uses **ISO week numbers** (W01–W53) under year folders:

```
11-Mess Hall/
├── daily/                          # Global daily summary files (not per-week)
│   ├── 2026-05-02-summary.md
│   ├── 2026-05-03-summary.md
│   └── 2026-05-04-summary.md
└── 2026/
    ├── W16/                        # Apr 16–19, 2026
    │   ├── 2026-04-16/
    │   └── 2026-04-18/
    ├── W17/                        # Apr 20–26, 2026
    │   ├── 2026-04-21/
    │   ├── 2026-04-22/
    │   └── ...
    ├── W18/                        # Apr 27 – May 3, 2026
    │   └── 2026-04-27/
    └── W19/                        # May 4–10, 2026  ← CURRENT
        └── 2026-05-04/            # Today's context + rotation files
```

**Why per-week folders?** Enables clean archiving, week-based rollups, and avoids root-level filename collisions across years.

## Discovery Notes (2026-05-04)

- Assumption: Daily sync skill expected `08-Daily/` root folder → **incorrect** (renamed to `08-Logs/`)
- Assumption: D5/LP trackers in `03-Projects/DeFi/` → **incorrect** (moved to `09-Green Room/` with descriptive prefixed names)
- Pattern: `09-Green Room/` is the active work-in-progress zone for cross-department artifacts that don't fit department folders
- Pattern: `11-Mess Hall/daily/` holds ONE summary file per calendar day; per-week subfolders hold contextual coordination files (`today-context.md`, `rotation-log.md`)
- Active handoffs also appear in `09-Green Room/active-handoffs/` with date-stamped filenames

**Future-proofing:** If vault structure changes again, check `INDEX.md` at vault root for canonical folder map and `11-Mess Hall/README.md` for Mess Hall organization guide.