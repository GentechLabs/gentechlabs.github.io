# Staleness Thresholds by File Category

Reference for `vault-stale-content-audit`. These thresholds define when content is considered stale and the appropriate action severity.

## Core Rules

| Category | Path Pattern | Threshold | Priority | Action |
|----------|--------------|-----------|----------|--------|
| Daily sync | `08-Daily/2026-*.md` | Any missing date in last 7 days | P1 | Investigate gap; create placeholder if intentional |
| Master todo | `09-Green Room/master-todo.md` | >5 days | P0 | Refresh with current active work; archive closed items |
| Working memory | `00-Working-Memory.md` | >7 days | P1 | Review for protocol drift; update if rules changed |
| Handoffs | `09-Green Room/handoffs/*.md` | >3 days | P2 | Archive to `handoffs/ARCHIVE/` or resurrect in Mess Hall |
| Green Room docs | `09-Green Room/*.md` (except master-todo) | >14 days | P2 | Consider archiving if project complete |
| Approvals | `00-HQ/Approvals/*.md` or `02-Labs/Approvals/*.md` | >30 days | P2 | Move to `ARCHIVE/` subfolder; maintain index in README |
| Scratch/experiments | Any `-tmp.md` or `drafts/` (unowned) | >7 days | P3 | Clean up to reduce bloat |

## Exception Handling

- **Intentionally long-lived files:** Specs, reference docs, and approved structures may be old but still active. Cross-check daily-sync TL;DR and current project dashboards before archiving.
- **Weekend/holiday gaps:** Daily sync may legitimately skip Sat/Sun. Use day-of-week check before flagging.
- **Archived content:** Files already under `archive/`, `ARCHIVE/`, or `YYYY/WXX/` dated folders are excluded from staleness flags; they are part of historical record.

## Gap Detection Logic (Python)

```python
def daily_sync_gaps(days_back=14):
    """Return list of missing YYYY-MM-DD dates in 08-Daily/."""
    existing = {f.name[:10] for f in DAILY.glob("2026-*.md")}
    today = datetime.now().date()
    gaps = []
    for i in range(1, days_back):
        d = today - timedelta(days=i)
        # Skip weekend if desired:
        # if d.weekday() >= 5: continue
        if d.strftime("%Y-%m-%d") not in existing:
            gaps.append(d.strftime("%Y-%m-%d"))
    return gaps
```

Call this in Phase 2 audit script. Any result triggers P1 gap alert.

## Archive Movement Protocol

For stale items identified:
1. If in `handoffs/` → move to `handoffs/ARCHIVE/` with suffix `-Resolved-YYYY-MM-DD.md`
2. If in `Approvals/` → move to `Approvals/ARCHIVE/` and append `ARCHIVED: YYYY-MM-DD` to frontmatter
3. For Green Room planning docs >14d → move to `09-Green Room/ARCHIVE/` (create if missing)
4. Commit to git with message: `chore(vault): archive stale {category} files ({file1}, {file2})`

Always preserve original file content; do not delete.

## Example Decision Tree

```
Is file in 08-Daily/?
  YES → missing date in last 7d? → P1 → create placeholder or clarify
  NO → Is it master-todo.md? age >5d? → P0 → refresh
  NO → Is it in handoffs/? age >3d? → P2 → archive
  NO → Apply category-specific thresholds above
```

---

*Thresholds reviewed: 2026-05-03. Adjust quarterly or based on team cadence changes.*
