---
name: daily-second-brain-sync
title: Daily Second Brain Sync
description: Review vault activity and create/update daily log, weekly overview, activity log, and monthly summary files.
category: note-taking
---

# Daily Second Brain Sync

Cron job that reviews all vault activity for today and consolidates into structured daily files.

## When to Use
- Scheduled cron job (runs daily, typically evening)
- Need to summarize what happened across all teams/departments
- Updating the Gentech Obsidian vault's daily/weekly/monthly tracking

## File Structure

```
08-Daily/
├── YYYY-MM-DD.md              # Full daily log (DETAILED)
├── YYYY-WNN.md                # Weekly overview (BRIEF Second Brain + links)
├── 2026-Weekly/
│   └── YYYY-WNN.md            # Full weekly activity log (DETAILED per-agent)
├── Monthly-Summaries/
│   └── YYYY-MM.md             # Monthly + weekly summaries
├── content-drafts/            # Content drafts (check for recent)
└── ...

08-Activity log/
└── 2026-Weekly/
    └── YYYY-WNN.md            # Parallel activity log (also append here)

11-Mess Hall/
├── daily-checkpoint-YYYY-MM-DD.md  # Checkpoint if exists
├── Chat — YYYY-MM-DD.md            # Chat log
├── apr-NN-*.md                      # Agent-specific updates
└── task-board.md                    # Current task assignments

09-Collaboration/active-tasks/
├── active-YYYY-MM-DD.md        # Today's active session
└── master-todo.md              # Master task list

10-Archive/Agent-States-*/      # Agent state snapshots
09-Green Room/                  # Handoffs and coordination
```

## Step-by-Step Process

### 1. Determine Today's Date
```bash
date +%Y-%m-%d
```

### 2. Discover Modified Files
Run Python to find all files modified today:
```python
import os
from datetime import datetime
today = datetime.now().strftime("%Y-%m-%d")
vault = "/root/vaults/gentech"
for root, dirs, files in os.walk(vault):
    for f in files:
        path = os.path.join(root, f)
        try:
            if datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d") == today:
                print(path)
        except: pass
```

### 3. Read Key Sources (in order of priority)
1. `11-Mess Hall/daily-checkpoint-YYYY-MM-DD.md` — if exists, this is the primary summary
2. `11-Mess Hall/Chat — YYYY-MM-DD.md` — conversation/activity log
3. `11-Mess Hall/apr-NN-*.md` — agent-specific updates from Dmob, YoYo, Desmond
4. `11-Mess Hall/task-board.md` — current task assignments and status
5. `09-Collaboration/active-tasks/active-YYYY-MM-DD.md` — today's active session
6. `10-Archive/Agent-States-*/yoyo-YYYY-MM-DD-state-late.md` — YoYo state snapshot
7. `09-Green Room/master-todo.md` — pending handoffs
8. `00-Inbox/HACKATHON-TODO.md` — hackathon command center
9. `08-Daily/2026-Weekly/YYYY-WNN.md` — previous days in current week
10. `08-Daily/Monthly-Summaries/YYYY-MM.md` — monthly running summary

### 4. Create Daily Log (`08-Daily/YYYY-MM-DD.md`)
Template structure:
```markdown
# Daily Log — [Day], [Month] [Date], [YYYY]

## 📊 Overview
[One-paragraph summary of the day]

## 🧠 Team Activity Summary
### ⚙️ Dmob (Labs)
[Build activity, commits, contract work]
### 📊 YoYo (Strategies)
[Research, analysis, competitive intel]
### ✍️ Desmond (Entertainment)
[Content, org systems, architecture]
### 🧠 Gentech (HQ)
[Coordination, ops, cron, vault]

## ✅ Completed Today
[Table: Task | Owner | Status]

## 🔄 In Progress
[Table: Task | Owner | Status]

## ⚠️ Blockers
[Numbered list]

## 🔑 Key Decisions & Discoveries
[Bullet list]

## 📋 Tomorrow's Queue
### Critical
### This Week

## 📈 Metrics
[Agent uptime, files modified, tests passing, active hackathons, days to deadline]
```

### 5. Create/Update Weekly Overview (`08-Daily/YYYY-WNN.md`)
Brief "Second Brain" section with today's one-paragraph summary. If file exists, append. If new week, create fresh.

### 6. Update Activity Log (`08-Activity log/2026-Weekly/YYYY-WNN.md`)
Append detailed per-agent breakdown (same format as existing entries in the file). Use `patch` to add after the last `#daily` tag.

**IMPORTANT:** Use `patch` not `write_file` to append — don't overwrite existing content. Read the file first to get exact text for the old_string match.

### 7. Update Monthly Summary (`08-Daily/Monthly-Summaries/YYYY-MM.md`)
Add W[N+1] Day [N] highlights section. Keep it brief — key wins, discoveries, blockers.

## Pitfalls

1. **Two W[NN] files exist** — `08-Daily/2026-WNN.md` (brief overview) vs `08-Activity log/2026-Weekly/YYYY-WNN.md` (detailed log). Don't confuse them.

2. **Patch failures** — `patch` requires exact string matching including whitespace. Always `read_file` the target section first before attempting `patch`. If patch fails, re-read and retry with exact content. **Weekly overview fallback:** For `08-Daily/YYYY-WNN.md` (typically <20 lines, no concurrent edits), `write_file` with full content is a safe fallback — reconstruct the file from the prior content plus today's paragraph. Reserve strict `patch` for `08-Activity log/` files which can be long and have entries from other agents.

3. **Week boundaries** — Sunday is start of Jordan's work week (Sun-Wed day shift, Thu-Sat late shift). Apr 20 = Monday = Week 17.

4. **Multiple agent state files** — Check `10-Archive/Agent-States-April/` for the latest YoYo state snapshots (may be `*-state-late.md` or `*-state.md`).

5. **Memory tool unavailable in cron** — Save all findings directly to vault files, not to the memory tool.

6. **Don't use send_message** — Cron jobs auto-deliver. The final response IS the delivery. Just produce the summary.

## Verification
After syncing, confirm:
- [ ] `08-Daily/YYYY-MM-DD.md` exists and has all 4 team sections
- [ ] `08-Daily/YYYY-WNN.md` has today's summary appended
- [ ] Activity log has today's detailed entry
- [ ] Monthly summary has W[N+1] highlights
- [ ] No files were accidentally overwritten (use `patch` for appends)
