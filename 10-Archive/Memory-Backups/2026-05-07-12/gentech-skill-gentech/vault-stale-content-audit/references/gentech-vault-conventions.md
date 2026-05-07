# Gentech Vault Conventions

Reference for `vault-stale-content-audit` — folder structure, file naming, and handoff lifecycle.

## Vault Root Structure

```
00-HQ/                 # Leadership/strategy; final decisions; Jordan-facing only
   Approvals/          # Checkpoint sign-offs (dated YYYY-MM-DD)
   Operations/         # Internal processes; not daily rotation fodder
01-Agency/            # Agent-specific directories (YoYo, DMOB, Desmond)
02-Labs/              # DMOB's domain (contracts, audits, research)
03-Projects/          # Active project documentation (specs, architecture)
03-Strategies/        # YoYo's domain (scripts, monitors, backtests)
08-Daily/             # Daily sync summaries (YYYY-MM-DD.md) — auto-rotated
09-Green Room/        # Active coordination between agents
   drafts/             # In-progress handoffs (another agent may be working)
   handoffs/           # Completed handoffs awaiting pickup
   handoffs/ARCHIVE/   # Resolved/old handoffs (moved monthly)
   WORKFLOW-ACTIVE.md  # Team protocols (link to agent-coordination skill)
   master-todo.md      # Centralized priority list (refresh weekly)
   agent-coordination-board.md  # Status + blockers per agent
11-Mess Hall/         # Casual discussions + daily rotation
   daily/              # Daily summaries (subfolders by YYYY/WXX/)
   logs/               # Conversation transcripts for retrospectives
   archives/           # Historical discussions (>30 days)
```

## Handoff Lifecycle

**Creation** — Agent writes handoff to `09-Green Room/handoffs/{topic}.md` (never `drafts/`). Includes:
- Context + link to previous discussion
- Concrete action requested
- Deadline (if any)
- Ownership (who should pick up)

**Pickup** — Assignee:
1. Moves file to `09-Green Room/drafts/` (locks ownership)
2. Completes work in their own group folder
3. Reports completion back to `09-Green Room/handoffs/{topic}-resolved.md`
4. Original handoff file is **archived** (not deleted) to `handoffs/ARCHIVE/` with suffix `-Resolved-Date.md`

**Staleness** — Any handoff >3 days old is auto-flagged in daily-sync. >7 days old => DROP unless resurrected in Mess Hall.

## Daily Sync Conventions

**Filename:** `YYYY-MM-DD.md` (extension `.md`, ISO date, no time)
**Location:** `08-Daily/` (flat list; **NOT** nested in week folders)
**Rotation:** Cron or manual: before 16:00 UTC, then archived by daily-rotation script to `11-Mess Hall/daily/` with directory `YYYY/WXX/`
**Format:** YAML frontmatter (`date`, `type: daily-sync`, `status: current`, `source: gentech-cron`) followed by H2 sections.

**Missing file policy:** If a day is skipped (weekend/holiday), **create an empty placeholder** file with frontmatter and status `skipped`. This preserves continuity tracking in later audits.

## Master Todo Conventions

`09-Green Room/master-todo.md` uses Markdown task lists with priority headings:

```markdown
## 🔴 P0 — [Project] — [Flag]
- [ ] Task description

## 🟡 P1 — [Project]
- [x] Completed item
```

**Refresh cadence:** Weekly (Monday EOD) by Gentech or designated deputy. Must reflect:
- New handoffs added
- Completed items removed/archived
- Priority shifts since last update

---

*These conventions are NOT configurable; they are operational standards.*
