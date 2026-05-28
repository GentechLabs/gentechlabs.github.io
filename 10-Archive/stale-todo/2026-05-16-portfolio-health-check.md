---
date: 2026-05-16
type: portfolio-health-check
author: Gentech (cron)
---

# Portfolio Health Check — 2026-05-16

## Summary: 🟡 DEGRADED — 3 issues found

| Check | Status | Detail |
|-------|--------|--------|
| `index.html` exists | ✅ PASS | 42.7KB, 1013 lines, valid HTML |
| `data/projects.json` exists | ✅ PASS | Valid JSON, 10 projects |
| JavaScript syntax | ✅ PASS | All 3 `<script>` blocks parse cleanly |
| GitHub Pages live | ✅ PASS | HTTP 200, responding in 70ms |
| Git repo in sync | ✅ PASS | Reset to origin/main, clean state |
| Last commit | ⚠️ NOTICE | 88e83b0 — May 14 (2 days ago) |
| Data consistency | ❌ FAIL | 3 copies of projects.json with different counts |
| Vault path references | ❌ FAIL | 2 of 10 paths broken |
| GitHub Pages freshness | ❌ FAIL | Last-Modified: May 7 (9 days stale) |

---

## Issues

### ISSUE #1: 🔴 DATA DRIFT — Three copies of projects.json, different counts

**Severity:** HIGH | **Since:** May 7 (persistent)

| File | Projects | Generated |
|------|----------|-----------|
| `data/projects.json` (page source) | 10 | 2026-05-11 |
| `projects.json` (root) | 7 | 2026-05-07 |
| `02-Labs/jordan-portfolio/projects.json` | 15 | 2026-05-13 |

The index.html embeds 15 projects from an inline `<script id="project-data">` block, but `data/projects.json` only has 10. The root `projects.json` is stale with 7. There's no single source of truth — three files diverging independently.

**Fix:** Run the sync script to regenerate all copies from one canonical source. Consider making `data/projects.json` the sole source and having index.html fetch it dynamically.

---

### ISSUE #2: 🟡 BROKEN VAULT PATHS — 2 of 10 references invalid

**Severity:** MEDIUM

| Project | vault_path | Status |
|---------|-----------|--------|
| `kite-ai` | `02-Labs/Hackathons/Active/Kite-AI` | ❌ Missing |
| `elevenhacks-9` | `02-Labs/Hackathons/Active/ElevenHacks-9` | ❌ Missing |

The Kite AI path may have moved to `03-Projects/Kite-AI/` in the vault. ElevenHacks-9 may be archived. Both paths should be updated or removed.

**Fix:** Update vault_path in projects.json to correct locations or remove stale references.

---

### ISSUE #3: 🟡 GITHUB PAGES STALE — Last deployed May 7

**Severity:** MEDIUM

The GitHub Pages `Last-Modified` header shows **May 7, 2026** — 9 days ago. While the repo has newer commits (latest: May 14), the Pages build hasn't picked up changes. The index.html served live may not reflect the current project state.

**Root cause:** Commits with `[skip ci]` skip the GitHub Actions workflow but Pages should still rebuild. However, only `data/projects.json` is being updated — `index.html` itself hasn't changed, so the embedded data on the live page remains from the May 7 deployment.

**Fix:** Push a fresh index.html regeneration to trigger a full Pages rebuild. Or investigate Pages deploy status in GitHub repo settings.

---

### ISSUE #4: ⚠️ DEADLINE ALERT — Kite AI due tomorrow

**Severity:** NOTICE

Kite AI hackathon deadline: **May 17, 2026** (1 day remaining). Currently status: `building`.

ElevenHacks-9 deadline: **May 21, 2026** (5 days remaining).

---

## Previous Issue Tracking

| Issue | From | Status |
|-------|------|--------|
| Data sync inline JS vs JSON | May 7 | 🔴 Still open — worsened (3 copies now) |
| Broken vault_path refs | May 7 | 🔴 Still open — 2 of 10 broken |
| Stale GitHub Pages | May 7 | 🔴 Still open — now 9 days stale |
| Git rebase conflict | NEW | ✅ Resolved (aborted stuck rebase) |

## Actions Taken

- ✅ Resolved stuck git rebase on local branch (abort → reset to origin/main)
- ✅ Verified `data/projects.json` is valid JSON (10 projects)
- ✅ Verified all JavaScript syntax passes
- ✅ Confirmed GitHub Pages serves HTTP 200

## Actions Needed

1. **[URGENT]** Regenerate index.html from latest projects.json — resolve the 3-way data drift
2. **[URGENT]** Fix vault_path for kite-ai (likely `03-Projects/Kite-AI/`)
3. Fix vault_path for elevenhacks-9 (verify or remove)
4. Push updated files to trigger fresh GitHub Pages deploy
5. Consider consolidating to single data source (eliminate duplicate copies)
