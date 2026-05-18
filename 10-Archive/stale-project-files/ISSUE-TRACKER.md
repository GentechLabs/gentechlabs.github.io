# Portfolio Issue Tracker

Last updated: 2026-05-18 12:01 UTC

---

## Open Issues

### ISSUE-2026-05-18-001 — Local Repo Diverged from Remote (3 Commits Behind) ⚠️ MEDIUM
- **Reported:** 2026-05-18
- **Severity:** Medium
- **Status:** OPEN
- **Description:** Local HEAD (`3fb9023`) is 3 commits behind remote HEAD (`1579b0c`). Remote has 3 automated "chore: update projects data [skip ci]" commits. Local has unmerged changes. `git status` reports "up to date" due to stale origin ref. Requires `git pull` to reconcile.
- **Impact:** Local edits may conflict with remote updates. GitHub Pages serves the remote version which may not match local `index.html`.
- **Fix:** `git pull origin main` to merge remote data updates into local working copy.
- **Owner:** Jordan

### ISSUE-2026-05-10-001 — GitHub Push Auth via GITHUB_TOKEN ⚠️ LOW
- **Reported:** 2026-05-10
- **Severity:** Low (downgraded from Critical)
- **Status:** WORKAROUND ACTIVE
- **Description:** `GITHUB_TOKEN` env var contains invalid token that overrides valid `gh` CLI credentials. Workaround: `unset GITHUB_TOKEN && git push`.
- **Fix:** Remove stale `GITHUB_TOKEN` from cron environment or update with valid PAT
- **Owner:** Jordan

### ISSUE-2026-05-10-002 — Multiple Project Data Sources Out of Sync ⚠️ MEDIUM
- **Reported:** 2026-05-10
- **Severity:** Medium
- **Status:** OPEN (still relevant — counts have shifted)
- **Description:** Three sources with different project counts: inline JS `const projects` array (13 projects), JSON `<script id="project-data">` element (15 projects), `data/projects.json` (10 projects), root `projects.json` (7 projects, stale since May 7). No single source of truth.
- **Fix:** Consolidate to single source. Have `generate_projects.py` be the generator for all outputs.
- **Owner:** Jordan

### ISSUE-2026-05-15-001 — Stale Inline Project Data in First Script Block ⚠️ MEDIUM
- **Reported:** 2026-05-15
- **Severity:** Medium
- **Status:** OPEN (merged into ISSUE-2026-05-10-002)
- **Description:** First inline `<script>` block has 13 projects. JSON script element has 15. `data/projects.json` has 10. Different projects, different descriptions across sources. Root `projects.json` (7 projects) is the most stale.
- **Fix:** Same as ISSUE-2026-05-10-002 — single generator for all outputs.
- **Owner:** Jordan

---

## Resolved Issues

### ISSUE-2026-05-10-003 — Footer Date Stale
- **Resolved:** 2026-05-15 (Footer now says "Last updated: May 2026")

### ISSUE-2026-05-10-004 — Missing .filter-btn CSS
- **Resolved:** 2026-05-12 (CSS added and deployed)

### ISSUE-2026-05-10-005 — agent-escrow Deadline
- **Resolved:** 2026-05-11 (Deadline passed, project marked completed)

### ISSUE-2026-05-12-001 — Vault Diverged from GitHub
- **Resolved:** 2026-05-15 (Rebased and pushed)

### ISSUE-2026-05-12-002 — Incorrect Kite AI Vault Path
- **Resolved:** 2026-05-13 (Updated to `02-Labs/Hackathons/Kite-AI/`)

### ISSUE-2026-05-15-JS-SYNTAX — JavaScript Syntax Error (Extra Closing Bracket)
- **Reported:** 2026-05-15
- **Resolved:** 2026-05-15 (Same day)
- **Description:** First inline `<script>` block had `}]];` instead of `}];` on line 410, causing `Unexpected token ']'` runtime error in browsers.
- **Fix:** Removed extra `]`. Commit `f38cae7` deployed to GitHub Pages.

---

## Summary

| Severity | Open | Resolved |
|----------|------|----------|
| Critical | 0 | 1 |
| Medium | 3 | 3 |
| Low | 1 | 3 |
| **Total** | **4** | **7** |

**Portfolio health: GOOD (with caveats).** All critical issues resolved. Three medium-priority items open: two data consistency items (carry-over) and one local/remote divergence.
