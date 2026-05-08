---
name: vault-daily-rotation
category: note-taking
description: Daily context rotation for the Gentech vault — archive resolved Mess Hall notes, clear stale Green Room handoffs, keep working spaces clean for the next shift.
---

# Vault Daily Context Rotation

## When to Use
When running the daily cron job to clean up the vault at `/root/vaults/gentech`. Archives yesterday's resolved content and clears stale handoffs so the next shift starts with a clean workspace.

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

## Pitfalls
- **Don't archive living docs:** task-board.md, handoff-board.md, agent-coordination-board.md, approvals.md, vault-cleanup-log.md, README.md — these are always kept
- **Check for carry-forward items:** A status note may be from yesterday but contain unresolved blockers — those stay
- **Don't archive active handoffs:** If a handoff file shows "IN PROGRESS" or "Waiting on X" and the work is ongoing, keep it
- **Green Room has duplicates:** `09-Green Room/` is the active one, `13-Green Room/` should stay clean (README only). Archive from 09, not 13.
- **X-Content drafts directory:** May be empty after archiving — remove it to avoid clutter, it gets recreated when needed
- **Misdated files:** Watch for wrong-year filenames (e.g., 2025 instead of 2026) — archive them as stale

## Archive Naming Convention
- Mess Hall: `10-Archive/Mess Hall/YYYY-MM-DD/` (date of the archived content)
- Green Room: `10-Archive/green-room-YYYY-MM-DD-rotation/` (date of rotation run)
- Content drafts: Reuse existing `10-Archive/Content-Drafts-April/` or create monthly
