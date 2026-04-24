---
name: hackathon-withdrawal
description: Clean up vault when a hackathon or project is cancelled — scan references, salvage reusable assets, update boards, mark docs withdrawn.
category: project-management
---

# Hackathon Withdrawal / Project Cancellation Protocol

When a hackathon or project is cancelled, use this to clean up the vault efficiently and preserve reusable assets.

## Trigger
Jordan says: "We're dropping [hackathon/project]", "Skip [X]", "Cancel [Y]", or "Withdraw from [Z]"

## Steps

### 1. Scan the Vault
Search all `.md` files for references to the cancelled item. Expect many results — filter for actionable items (task entries, deadlines, chain-specific references).

```python
keywords = ['arc', 'arc-hackathon']  # adjust per project
# Walk vault, collect files with matches
# Group by file, note which keywords hit
```

### 2. Read Core Files
Read the main project/hackathon docs to understand:
- What was built (tech assets)
- What was planned (content, submissions)
- What was project-specific vs reusable

### 3. Create Salvage Log
Write to `11-Mess Hall/[project]-salvage-log.md`:

Sections:
- **Reusable Tech Assets** — contracts, code, patterns, test suites
- **Reusable Content/Process** — README structures, demo workflows, submission templates
- **Scrubbed** — project-specific items removed
- **Action Items** — what each agent needs to do
- **Lesson for Future** — timing, chain alignment, effort-to-prize ratio

### 4. Update Task Board (`11-Mess Hall/task-board.md`)
- Mark project tasks as `[X]` (discarded) with status `❌ CANCELLED` or `WITHDRAWN`
- Update Sprint Flow section to remove cancelled item
- Add note linking to salvage log

### 5. Update Project Files
- Mark hackathon docs as `WITHDRAWN` or `CANCELLED`
- Add `See: salvage-log.md` reference
- Keep original info but clearly mark as archived

### 6. Notify Team
Post brief status in Mess Hall or HQ:
- What was cancelled
- What was salvaged
- What's the new priority

## Rules
- **Don't delete history** — mark as withdrawn, don't remove files
- **Salvage aggressively** — contracts, patterns, and workflows are almost always reusable
- **Log the lesson** — timing, chain alignment, effort ratio for future selection
- **Update sprint flow** — team needs clear picture of what's next

## Example Output
```
📄 11-Mess Hall/arc-salvage-log.md
📄 11-Mess Hall/task-board.md (updated)
📄 02-Labs/Hackathons/01-ARC-Hackathon-*.md (3 files, marked withdrawn)
```
