---
name: vault-stale-content-audit
description: "Systematic vault hygiene monitoring: detect stale files, missing daily syncs, orphaned handoffs, and content continuity breaks in structured Obsidian vaults."
tags: [vault-maintenance, hygiene, operational-health, continuity, audit]
trigger: "When performing weekly vault health checks, identifying stale notes (daily syncs, master todos, handoffs), detecting file sequence gaps, or generating executive briefs on content cleanliness."
related_skills:
  - agent-coordination    # for vault sweep protocols (Section 6 in that skill)
  - system-health        # for agent-level health (different scope: human-authored content)
version: 1.0.0
author: Gentech
---

# Vault Stale Content Audit (Umbrella)

Reusable protocol for auditing content staleness, daily sync continuity, and artifact hygiene in structured Obsidian vaults. Encapsulates the two-phase scan (shell + Python), gap detection logic, and executive reporting patterns from the May 3, 2026 vault health review.

> **Pattern origin:** Derived from the `08-Daily/` and `09-Green Room/` audit that identified missing May 1 sync, stale master-todo (Apr 25), orphaned handoff files, and persistent blockers.

---

## Quick-Start Checklist

- [ ] **Phase 1:** Shell discovery — list recent files sorted by mtime
- [ ] **Phase 2:** Python age/gap analysis (use sample script below)
- [ ] **Phase 3:** Apply context rules by file category (daily: 7d, master-todo: 5d, handoffs: 3d)
- [ ] **Phase 4:** Assemble ≤5-item executive report with clear actions
- [ ] **Post-audit:** Write findings to Mess Hall + Green Room handoffs

---

## Phase 1: Shell-Based Discovery (Fast scan)

### 1.1 Daily sync age & cadence

```bash
cd /root/vaults/gentech/
# Last 10 daily files (newest first)
find 08-Daily/ -name "*.md" -type f -exec ls -lt {} + | head -10

# All daily files with dates in filename (for gap analysis)
find 08-Daily/ -type f -name "2026-*.md" | sed 's|08-Daily/||' | sort -r
```

### 1.2 Working Memory & master todo freshness

```bash
ls -lt 00-Working-Memory.md 09-Green\ Room/master-todo.md
```

### 1.3 Handoffs directory scan

```bash
# Unarchived handoffs only (ignore archive/ subdirs)
find 09-Green\ Room/handoffs/ -maxdepth 1 -name "*.md" -type f -exec ls -lt {} \;
COUNT=$(find 09-Green\ Room/handoffs/ -maxdepth 1 -name "*.md" -type f | wc -l)
echo "Unarchived handoffs: $COUNT"
```

### 1.4 Approval folder recency

```bash
find 00-HQ/Approvals/ -name "*.md" -type f -mtime +30  # stale approvals
find 02-Labs/Approvals/ -name "*.md" -type f -mtime +30
```

---

## Phase 2: Python Continuity Analysis

### 2.1 Reference Script

Save as `scripts/audit_vault_health.py` (reusable):

```python
#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from pathlib import Path

VAULT = Path("/root/vaults/gentech")
DAILY = VAULT / "08-Daily"
MASTER_TODO = VAULT / "09-Green Room" / "master-todo.md"
WORKING_MEMORY = VAULT / "00-Working-Memory.md"
HANDOFFS = VAULT / "09-Green Room" / "handoffs"

def age_days(path: Path) -> int | None:
    if path.exists():
        return (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).days
    return None

def daily_sync_gaps(days_back: int = 14) -> list[str]:
    """Return list of missing YYYY-MM-DD filenames in daily/."""
    files = [f.name[:10] for f in DAILY.glob("2026-*.md")]
    existing = set(files)
    today = datetime.now().date()
    gaps = []
    for i in range(1, days_back):
        d = today - timedelta(days=i)
        if d.strftime("%Y-%m-%d") not in existing:
            gaps.append(d.strftime("%Y-%m-%d"))
    return gaps

def scan_stale(threshold: int) -> list[tuple[Path, int]]:
    """Return all markdown files older than threshold days."""
    stale = []
    for root, dirs, files in os.walk(VAULT):
        # Skip .git and __pycache__
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.obsidian']]
        for f in files:
            if f.endswith('.md'):
                p = Path(root) / f
                a = age_days(p)
                if a is not None and a > threshold:
                    stale.append((p, a))
    stale.sort(key=lambda x: x[1], reverse=True)
    return stale

# --- Main audit ---
print("=== VAULT HEALTH AUDIT ===\n")

# 1. Daily file recency
daily_files = sorted(DAILY.glob("2026-*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
if daily_files:
    last = daily_files[0]
    print(f"Last daily: {last.name} ({age_days(last)} days ago)")
else:
    print("No daily files found")

# 2. Daily gaps (last 14 days)
gaps = daily_sync_gaps(14)
if gaps:
    print(f"\n⚠️ Missing daily files (last 14d): {gaps}")
else:
    print("\n✓ Daily syncs continuous (last 14d)")

# 3. Master todo age
if MASTER_TODO.exists():
    print(f"\nmaster-todo.md age: {age_days(MASTER_TODO)} days")
    if age_days(MASTER_TODO) > 5:
        print("  ⚠️ STALE — refresh needed")

# 4. Working Memory age
if WORKING_MEMORY.exists():
    print(f"Working Memory age: {age_days(WORKING_MEMORY)} days")

# 5. Unarchived handoffs
handoff_files = list(HANDOFFS.glob("*.md"))
if handoff_files:
    oldest = min(handoff_files, key=lambda p: p.stat().st_mtime)
    print(f"\nOldest handoff: {oldest.name} ({age_days(oldest)} days old)")
    if age_days(oldest) > 3:
        print("  ⚠️ Consider archiving (resolved items likely)")

# 6. Very stale files (>30d)
stale_30 = scan_stale(30)
if stale_30:
    print(f"\nFiles >30d old (top 10):")
    for p, age in stale_30[:10]:
        print(f"  {p.relative_to(VAULT)} — {age}d")
```

**Usage:** `python3 scripts/audit_vault_health.py`

---

## Phase 3: Context-Based Thresholds

Apply these rules to raw age data:

| File / Folder | Threshold | Action | Reason |
|---------------|-----------|--------|--------|
| `08-Daily/{date}.md` missing | Any gap in last 7d = **P1** | Investigate why; may indicate team offline day | Continuity monitoring |
| `master-todo.md` | >5d old = **P0** | Refresh with current scope | Active projects tracked here |
| `00-Working-Memory.md` | >7d = **P1** | Audit protocol drift | Core coordination rules live here |
| `09-Green Room/handoffs/*.md` | >3d = **P2** | Archive or DROP | Should be picked up quickly |
| Green Room docs (>14d) | >14d = **P2** | Review for archival | Planning artifacts age out |
| Approval files (>30d) | >30d = **P2** | Archive to `00-HQ/Approvals/ARCHIVE/` | Completed approvals should be moved |
| Experimental/scratch pads | >7d = **P3** | Clean up | Prevent hoarding |

**Exception:** Approved but intentionally long-lived items (e.g., LFJ features, D5 spec) stay even if old. Cross-check daily-sync status to confirm still-active.

---

## Phase 4: Executive Report Assembly

### Structure (max 5 items, prioritized)

**1. [File] — [P0/P1/P2]**
[Machine-readable date + concise problem statement (1 sentence). Include specific flags from daily-sync TL;DR where available.]
**Action:** [Agent] to [specific action] by [date]

**2. [File] — [P0/P1/P2]**
[Same format]

[Up to 5 items only]

### Tone & Formatting

- **No introductory paragraph** — start with first item
- **Bold the file path** (GitHub-flavored markdown)
- **Action ownership** explicit (Gentech / DMOB / YoYo / Desmond)
- **Deadlines** from daily-sync TL;DR or reasonable defaults (EOD today, EOW)
- **Cite context** where helpful: "*as flagged in May 2 sync*" or "*persistent since Apr 30*"

### Example Output (derived from May 3 session)

```
**1. `09-Green Room/master-todo.md` — P0**
Stale master baseline from 2026-04-25 (8 days); active projects (Solana Frontier, Kite AI, D5) have resolved items not yet cleaned up. May 2 daily sync explicitly flagged this item.
**Action:** Desmond to refresh by EOD May 3; archive closed tasks; align P0/P1 with current frontier work.

**2. `09-Green Room/handoffs/unified-defi-lp-describe-request.md` — P2**
Orphaned handoff from 2026-04-25 (8 days); D5 consolidation likely resolved this. Still sitting in handoffs/ with no disposition.
**Action:** DMOB to archive to `handoffs/archive/` or confirm still-active by EOD May 3.

**3. `08-Daily/2026-05-01.md` — P1** (GAP)
Missing daily sync file for May 1; continuity break between Apr 30 and May 2 despite critical work (H001–H004 closures, D5 consolidation).
**Action:** Daily cron to investigate why May 1 entry not created; add placeholder with "no-team-activity" tag if confirmed correct.

**4. `00-Working-Memory.md` — P1**
Last updated 2026-04-26 (6 days old); contains active protocol rules but aging. Needs periodic review.
**Action:** Cross-check May 5 weekend; schedule refresh for May 6 if no substantive changes.

**5. Vault-wide — P2**
Storage bloat (152 GB) flagged daily since Apr 30; cleanup deferred until post-May 11/17. No tracking on master-todo.
**Action:** Add explicit `Storage cleanup (May 18)` P2 item to master-todo; track in DMOB's dev environment prep.
```

---

## Post-Audit Actions

1. **Publish to Mess Hall:** `11-Mess Hall/vault-health-audit/{date}.md` with full findings
2. **Create Green Room handoffs** for each P0/P1 item (tag responsible agent)
3. **Update master-todo** (if you are Gentech) to reflect deferred items from the audit itself
4. **Schedule next audit:** Re-run weekly on Monday at 03:00 UTC via cron or agent reminder

---

## Integration with Existing Skills

- **`agent-coordination` Section 6 (Vault Sweep Protocol):** This skill provides the *technical implementation* that the coordination skill references. When a "vault sweep" is scheduled, load this skill and execute its procedure.
- **`system-health` skill:** Use `system-health` for *agent process health*; use `vault-stale-content-audit` for *human-authored content health*. Related but separate domains.

---

## Pitfalls & Edge Cases

| Situation | Mis-step | Correct approach |
|-----------|----------|------------------|
| Weekends show no daily files | Flag as gap => false positive | Check day-of-week; skip automatic flag for Sat/Sun unless daily explicitly required |
| Old file is intentionally long-lived | Archive based on age alone | Cross-reference with daily-sync status; if mentioned in TL;DR, it's still active |
| Handoffs directory explodes | Count files; archive in bulk | Archive all >7d handoffs to `handoffs/ARCHIVE/` with single commit |
| Audit runs on May 3, finds May 1 gap | Assume someone forgot | Check Mess Hall for May 1 discussion; may already be covered via alternative channel |

---

## References

- `references/gentech-vault-conventions.md` — Obsidian folder structure, file naming, handoff lifecycle rules
- `references/staleness-thresholds.md` — Age-based thresholds by file type with reasoning
- `references/executive-report-template.md` — Final report formatting patterns and examples
- `references/may-3-2026-audit-case.md` — Full reproduction of this session's discovery, including gaps analysis and resolution recommendations

---

## Templates

See `templates/vault-audit-report.md` for markdown report starter.
