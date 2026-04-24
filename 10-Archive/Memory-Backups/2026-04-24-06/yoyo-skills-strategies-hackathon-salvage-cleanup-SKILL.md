---
name: hackathon-salvage-cleanup
description: Systematic audit and cleanup when a hackathon is cancelled or pivoted — salvage reusable assets, update priorities, archive the rest
---

# Hackathon Salvage & Cleanup

When a hackathon is cancelled or the team pivots away, use this process to audit assets, salvage what's reusable, and cleanly update the vault.

## When to Use
- Hackathon application withdrawn
- Team decides to skip a hackathon deadline
- Pivoting from one hackathon to another
- Project scope changed mid-sprint

## Steps

### 1. Search All References
Search the vault for all mentions of the hackathon:
```
search_files: pattern = "{hackathon_name}" target = "content"
```
Check: INDEX.md, master-todo.md, daily logs, Green Room drafts, strategy docs, content drafts, GitHub repos.

### 2. Audit Built Assets
Create a salvage table:

| Asset | Status | Reusable? | Destination |
|-------|--------|-----------|-------------|
| Smart contracts | N/N tests | Yes/No | Target project |
| Content (pitch, video) | Draft/Final | Yes — rebrand | Next hackathon |
| Architecture docs | | Yes | Protocol-wide |
| Security findings | | Always yes | Apply before deploy |
| Chain-specific config | | No | Archive |
| Deploy scripts | | No/Adapt | Archive or adapt |

### 3. Extract Key Learnings
Document what was learned that transfers:
- Technical traps (e.g., 6-decimal USDC on Arc vs 18)
- Security vulnerabilities found
- Architecture patterns validated
- Process improvements discovered

### 4. Update Priority Docs
- **INDEX.md**: Remove hackathon from Active Hackathons table
- **master-todo.md**: Remove hackathon section, update priorities for remaining hackathons
- **Daily log**: Note the cancellation and reason

### 5. Log to Mess Hall
Create a summary file: `11-Mess Hall/{hackathon}-withdrawn.md`
Include:
- Status and date
- Salvaged assets table
- Key learnings retained
- What was archived

### 6. Archive Hackathon-Specific Files
Move to `10-Archive/`:
- Hackathon-specific deploy scripts
- Testnet configs
- Submission materials (README, demo recordings)

### 7. Update Sprint Flow
If other hackathons depend on this one, update the sprint sequence. Shift resources to next priority.

## Template — Mess Hall Log
```markdown
# {Hackathon} — Withdrawn ({date})

## Status: CANCELLED
Reason: {why}

## Salvaged Assets
| Asset | Destination |
|-------|-------------|
| {item} | {where it goes} |

## Key Learnings Retained
1. {lesson}
2. {lesson}

## Archived
- {items}

---
**Last updated:** {date}
**Updated by:** {agent}
```

## Pitfalls
- Don't delete — archive. Code and content may be useful later.
- Security findings always transfer — even if the chain doesn't.
- Content scripts just need rebranding (swap chain name), not rewrite.
- Check GitHub repos for branch-specific code that can be cherry-picked.

## Files to Update
- `/root/vaults/gentech/INDEX.md` — hackathon table
- `/root/vaults/gentech/09-Green Room/master-todo.md` — priority tasks
- `/root/vaults/gentech/11-Mess Hall/` — withdrawal log
- `/root/vaults/gentech/10-Archive/` — archived files
