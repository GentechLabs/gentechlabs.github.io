# Portfolio Issue Tracker

## Active Issues

### #007 — 🔴 GitHub Pages Stale (May 7)
- **Severity**: CRITICAL
- **Date**: 2026-05-20
- **Status**: OPEN
- **Description**: Live page `Last-Modified` header shows May 7, 2026 — 13 days stale. 5 remote commits unpushed locally. Pages not rebuilding despite commits to `main` branch.
- **Action**: Pull remote, investigate Pages deployment, push if needed.

### #006 — 🔴 Data Drift: projects.json vs index.html
- **Severity**: HIGH
- **Date**: 2026-05-20
- **Status**: OPEN (recurring)
- **Description**: `data/projects.json` has 11 projects, `index.html` project-data block has 15. 2 projects only in JSON (elevenhacks-9, swarms-defi-signal-agent), 6 only in HTML (agora-agents, google-cloud-rapid-agent, google-startups, multi-agent-voice, personal-finance, somnia). 2 status mismatches (kite-ai, lfj-avax-usdc).
- **Action**: Run `generate.py` from canonical source to sync both files. Designate single source of truth.

### #005 — ⚠️ Dead Code: Hardcoded Projects Array
- **Severity**: LOW
- **Date**: 2026-05-20
- **Status**: OPEN
- **Description**: Inline `projects` array at line 398 (14 items, ~8KB) is dead code — page renders from `project-data` block instead. Wastes bandwidth and creates confusion.
- **Action**: Remove the hardcoded array.

### #004 — ⚠️ Local Repo Behind Remote
- **Severity**: MEDIUM
- **Date**: 2026-05-20
- **Status**: OPEN
- **Description**: Local HEAD (8444afa) is 5 commits behind origin/main. 1 modified file (hackathon-tracker.md) uncommitted.
- **Action**: `git pull --rebase origin main`, commit changes, verify.

## Resolved

### #003 — Data drift (3-way) — 2026-05-16
- **Status**: RESOLVED (partial — drifted again)
- **Notes**: Reduced from 3 copies to 2, but drift persists between projects.json and inline data.

### #002 — Missing CSS for filter-btn — 2026-05-14
- **Status**: RESOLVED

### #001 — Broken external link — 2026-05-07
- **Status**: RESOLVED
