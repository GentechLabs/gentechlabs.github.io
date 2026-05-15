# Portfolio Issue Tracker

Last updated: 2026-05-15 12:01 UTC

---

## Open Issues

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
- **Status:** OPEN
- **Description:** Three sources with different project counts: inline JS script (13 projects), JSON script element (15), `generate_projects.py` (9). `data/projects.json` (15 projects) is canonical but generator overwrites it with 9 on next run.
- **Fix:** Consolidate to single source. Have `generate_projects.py` be the generator for all outputs.
- **Owner:** Jordan

### ISSUE-2026-05-15-001 — Stale Inline Project Data in First Script Block ⚠️ MEDIUM
- **Reported:** 2026-05-15
- **Severity:** Medium
- **Status:** OPEN
- **Description:** First inline `<script>` block has 13 projects. JSON script element and `data/projects.json` have 15. Missing from inline: `multi-agent-voice`, `personal-finance`. Some descriptions outdated.
- **Fix:** Update inline data to match `data/projects.json` or regenerate via script
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
| Medium | 2 | 3 |
| Low | 1 | 3 |
| **Total** | **3** | **7** |

**Portfolio health: GOOD.** All critical issues resolved. Two medium-priority data consistency items remain open for cleanup.
