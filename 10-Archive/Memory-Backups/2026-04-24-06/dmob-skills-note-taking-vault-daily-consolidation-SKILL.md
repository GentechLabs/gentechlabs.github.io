---
name: vault-daily-consolidation
description: Consolidate scattered daily notes into a clean Month/Week-01 through Week-04 hierarchy in Obsidian vaults.
triggers:
- "consolidate daily notes"
- "organize activity log"
- "restructure vault folders"
- "monthly weekly folder setup"
---

# Vault Daily Notes Consolidation

When consolidating scattered daily notes into a structured Month/Week hierarchy.

## Approach

1. **Create clean target structure first** — delete any messy/incomplete folders before recreating
2. **Search comprehensively** — daily files often end up in archives (`10-Archive/`), not original locations
3. **Use consistent naming** — `January/Week-01/`, `January/Week-02/`, etc. (not mixed date formats)
4. **Copy, don't move** — preserve originals in archives as backup
5. **Parse dates to determine week** — day 1-7 = Week-01, 8-14 = Week-02, 15-21 = Week-03, 22+ = Week-04

## Common Pitfalls

- **Duplicate folders** — script may create both `2026-04/` and `2026-04-April/`. Clean up ALL existing folder structures before recreating.
- **Files in archives** — daily notes get moved to `10-Archive/Mess Hall/YYYY-MM-DD/` or similar during vault cleanup. Search all archive subfolders.
- **Weekly files** — `2026-W16.md` style files need manual mapping to correct week.
- **README.md not found** — source files may have been renamed during archival (e.g., `Chat — 2026-04-20.md` instead of `2026-04-20.md`).

## Structure Template

```
08-Activity log/
├── January/
│   ├── README.md (month summary table)
│   ├── Week-01/
│   ├── Week-02/
│   ├── Week-03/
│   └── Week-04/
├── February/
│   └── ...
└── README.md (root with month links)
```

Each month README includes a week summary table:

```markdown
# January 2026

| Week | Dates | Notes |
|------|-------|-------|
| Week-01 | 1-7 | |
| Week-02 | 8-14 | |
| Week-03 | 15-21 | |
| Week-04 | 22-28/31 | |
```

## Code Pattern

```python
import os
import shutil
from datetime import datetime

def get_week_in_month(date_str):
    """Return Week-XX for a given date string (YYYY-MM-DD)"""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    day = dt.day
    if day <= 7: return 'Week-01'
    elif day <= 14: return 'Week-02'
    elif day <= 21: return 'Week-03'
    else: return 'Week-04'

def get_month_name(date_str):
    """Return full month name (January, February, etc.)"""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%B')
```

## Steps

1. Clean existing target directory completely
2. Create 12 months × 4 weeks folder structure
3. Write README.md files for each month
4. Search vault comprehensively for daily/weekly files (check archives!)
5. Copy files to correct Month/Week-XX folder based on date
6. Update root README with navigation links
