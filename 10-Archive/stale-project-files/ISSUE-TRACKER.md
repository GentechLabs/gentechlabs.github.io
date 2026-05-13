# Portfolio Issue Tracker

Last updated: 2026-05-12 12:01 UTC

---

## Open Issues

### ISSUE-2026-05-10-001 — GitHub Push Auth Failure ❌ CRITICAL
- **Reported:** 2026-05-10
- **Severity:** Critical
- **Status:** OPEN — UNRESOLVED (3rd day)
- **Description:** `git push` fails with `fatal: Authentication failed`. Remote URL uses username:password auth which GitHub no longer supports. Cannot deploy any updates to GitHub Pages.
- **Impact:** 6 vault commits stuck locally. Live site hasn't updated since May 7.
- **Fix:** Update remote URL with fresh Personal Access Token (PAT) or switch to SSH key auth
- **Owner:** Jordan

### ISSUE-2026-05-10-002 — Root projects.json Vault Paths Stale ⚠️ MEDIUM
- **Reported:** 2026-05-10
- **Severity:** Medium
- **Status:** OPEN — WORSENED
- **Description:** Three `projects.json` files now out of sync: root (7 projects), GitHub Pages (7), `data/` (9), vault inline (10). Vault inline data is most current but not deployed.
- **Fix:** Use `data/projects.json` as canonical source, sync to root and GH Pages
- **Owner:** DMOB or Jordan

### ISSUE-2026-05-10-003 — Footer Date Stale (carried from May 9) ℹ️ LOW
- **Reported:** 2026-05-09 (carried over)
- **Severity:** Low
- **Status:** OPEN — UNRESOLVED (3rd day)
- **Description:** Footer says "Last updated: April 2026" — should be May 2026
- **Fix:** One-line text change in `index.html` line 933
- **Owner:** Jordan

### ISSUE-2026-05-10-004 — Missing .filter-btn CSS ✅ RESOLVED
- **Reported:** 2026-05-10
- **Status:** RESOLVED in vault (CSS added). Not yet deployed to GitHub Pages.

### ISSUE-2026-05-10-005 — agent-escrow Deadline ✅ RESOLVED
- **Reported:** 2026-05-10
- **Status:** RESOLVED — Deadline was May 11. Project marked "completed" in vault data.

### ISSUE-2026-05-12-001 — Vault Diverged from GitHub ⚠️ MEDIUM
- **Reported:** 2026-05-12
- **Severity:** Medium
- **Status:** OPEN
- **Description:** Vault has 6 commits ahead, 3 behind `origin/main`. Branch has diverged. Needs `git pull --rebase` then push (once auth is fixed).
- **Fix:** Pull remote changes, rebase local, then push
- **Owner:** Jordan

### ISSUE-2026-05-12-002 — Incorrect Kite AI Vault Path ⚠️ LOW
- **Reported:** 2026-05-12
- **Severity:** Low
- **Status:** OPEN
- **Description:** `data/projects.json` references `02-Labs/Hackathons/Active/Kite-AI` — this path doesn't exist. Actual path is `02-Labs/Hackathons/Kite-AI`.
- **Fix:** Update vault_path in `data/projects.json`
- **Owner:** DMOB or Jordan

---

## Resolved Issues

### ISSUE-2026-05-10-004 — Missing .filter-btn CSS
- **Resolved:** 2026-05-12 (CSS added in vault index.html)

### ISSUE-2026-05-10-005 — agent-escrow Deadline
- **Resolved:** 2026-05-11 (Deadline passed, project marked completed)

---

## Summary

| Severity | Open | Resolved |
|----------|------|----------|
| Critical | 1 | 0 |
| Medium | 2 | 0 |
| Low | 2 | 2 |
| **Total** | **5** | **2** |

**Top priority:** Fix GitHub push auth (ISSUE-2026-05-10-001). This unblocks everything else.
