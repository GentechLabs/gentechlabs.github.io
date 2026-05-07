# Vault Stale Content Audit Report

Use this template when writing the executive summary (Phase 4 output). Max 5 items, prioritized by impact.

```
## Vault Stale Content Scan — [DATE]

**1. `[FILE PATH]` — [PRIORITY]**
[One-sentence problem statement referencing date of staleness or gap. Link to prior daily-sync TL;DR if applicable: "*as flagged in May 2 sync*"]
**Action:** [Agent] to [specific verb] by [deadline]

**2. `[FILE PATH]` — [PRIORITY]**
[Same format]

**3. `[FILE PATH]` — [PRIORITY]**
[Same format]

**4. `[BLOCKER DESCRIPTION]` — [PRIORITY]**
[For non-file systemic issues, use descriptive title instead of file path]

**5. [OPTIONAL P2 ITEM]**
[Only include if all above are P0/P1; skip otherwise]
```

## Format Rules

- **Bold file paths** using `backticks`
- Actions start with verb in **bold**: `**Action:** Gentech to …`
- Priority markers: **P0** (blocker/core), **P1** (continuity), **P2** (hygiene), **P3** (cleanup)
- Date format: `YYYY-MM-DD`
- Keep each item to ≤3 lines total

## Example (real)

```
## Vault Stale Content Scan — May 3, 2026

**1. `09-Green Room/master-todo.md` — STALE (P0)**
Dated 2026-04-25 (8 days old). Active projects (Solana Frontier, Kite AI, D5 consolidation) have resolved items not yet cleaned up; May 2 daily sync explicitly flagged.
**Action:** Desmond to refresh + archive old items by EOD May 3

**2. `09-Green Room/handoffs/unified-defi-lp-describe-request.md` — STALE (P2)**
Last modified 2026-04-25 (8 days old). Likely resolved in D5 consolidation shipped May 2; still in handoffs/ with no cleanup.
**Action:** DMOB to archive to `handoffs/archive/` by EOD May 3

**3. `08-Daily/2026-05-01.md` — MISSING (P1)**
No daily sync for May 1; gap exists between Apr 30 and May 2 despite work on May 2 (H001–H004 resolutions).
**Action:** Daily cron modified to auto-create empty `skipped` placeholder for continuity tracking
```

## Header Requirements

- Start directly with `## Vault…` — no intro paragraph
- Report title includes scan date
- No conclusion/summary paragraph at end (max 5 items stands alone)

### When You Have <5 Items

If only 2–3 items are significant, stop there. Do not pad. The user sees all context in Mess Hall full trace; executive wants distillation.

### When You Have >5 Items

Prioritize ruthlessly. Merge related items under one heading if they share same owner/action. Drop P2/P3 items if not urgent.
