# Portfolio Issue Tracker

Last updated: 2026-05-10 12:00 UTC

---

## Open Issues

### ISSUE-2026-05-10-001 — GitHub Push Auth Failure ❌ CRITICAL
- **Reported:** 2026-05-10
- **Severity:** Critical
- **Status:** OPEN
- **Description:** `git push` fails with `fatal: Authentication failed`. Remote URL uses username:password auth which GitHub no longer supports. Cannot deploy any updates to GitHub Pages.
- **Fix:** Update remote URL with fresh Personal Access Token (PAT) or switch to SSH key auth
- **Owner:** Jordan

### ISSUE-2026-05-10-002 — Root projects.json Vault Paths Stale ⚠️ MEDIUM
- **Reported:** 2026-05-10
- **Severity:** Medium
- **Status:** OPEN
- **Description:** Root `projects.json` uses old `02-Labs/` paths for 6 of 7 projects. HTML embedded data and `data/projects.json` already use corrected `03-Projects/` paths.
- **Fix:** Update root `projects.json` to match embedded data paths
- **Owner:** DMOB or Jordan

### ISSUE-2026-05-10-003 — Footer Date Stale (carried from May 9) ℹ️ LOW
- **Reported:** 2026-05-09 (carried over)
- **Severity:** Low
- **Status:** OPEN
- **Description:** Footer says "Last updated: April 2026" — should be May 2026
- **Fix:** One-line text change in `index.html` line 933
- **Owner:** Jordan

### ISSUE-2026-05-10-004 — Missing .filter-btn CSS ℹ️ LOW
- **Reported:** 2026-05-10
- **Severity:** Low
- **Status:** OPEN
- **Description:** 5 filter buttons in HTML use `.filter-btn` class but no CSS is defined. Buttons render unstyled.
- **Fix:** Add `.filter-btn` CSS rules (padding, border, border-radius, background, hover)
- **Owner:** DMOB or Jordan

### ISSUE-2026-05-10-005 — agent-escrow Deadline Tomorrow ℹ️ INFO
- **Reported:** 2026-05-10
- **Severity:** Info
- **Status:** WATCHING
- **Description:** AgentEscrow project deadline is 2026-05-11 (Solana Frontier hackathon). Confirm submission readiness.
- **Owner:** Jordan / YoYo

---

## Resolved Issues

_(none yet)_
