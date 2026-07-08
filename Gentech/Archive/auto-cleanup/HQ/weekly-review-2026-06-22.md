# Weekly Vault Health Review — 2026-06-22

## Summary
- **Total .md files:** 1,435 (1,335 excluding Archive)
- **Active folders:** 47 top-level directories
- **Uncommitted changes:** 3 (clean)
- **Orphan notes:** 59 (4.1% — good, under 10%)
- **Stale files (>14 days):** 1,002 (70% — needs attention)

## Folder Counts (recursive .md files)
| Folder | Count | Stale (>14d) |
|--------|-------|-------------|
| Labs | 694 | 626 |
| Strategies | 158 | 118 |
| Content | 70 | 58 |
| HQ | 50 | 32 |
| Projects | 42 | 32 |
| Entertainment | 42 | 35 |
| 11-Mess Hall | 33 | — |
| Skills | 22 | 20 |
| Learning | 13 | 19 |
| Audits | 12 | 12 |
| Agent-Arena | 10 | 9 |
| AAE | 6 | — |
| Daily | 8 | — |

## Security
- **🟢 No `.env` at vault root**
- **🟢 No secrets at vault root**
- **🟡 `.git-credentials` at vault root** — contains GitHub token. Consider moving to `.git/config` or removing from vault.
- **🟡 Root artifacts:** `index.html`, `projects.json` present at vault root. Consider moving to appropriate subfolder.
- **🟢 Clean git status** — only 3 modified files, all tracked

## Structure Issues
- **Duplicate folder pairs:** 6 pairs detected (Labs/02-Labs/10-Labs, HQ/00-HQ, Content/06-Content, Projects/03-Projects, Strategies/03-Strategies, Gaming/15-Gaming). Consider consolidating.
- **Stale content:** 70% of active files haven't been updated in 14+ days. Labs folder is the biggest contributor (626 stale files).
- **Orphan notes:** 59 notes with no wikilinks. Low risk but worth linking to daily notes or project notes.

## AAE Stack
- **ERC-8004:** Active in ideas (Agent Registration API) and Agent Kit × Q402 × Injective integration spec
- **x402:** Active in ideas (multiple revenue streams) and integration spec
- **AACP:** Referenced in ideas
- **Fhenix, xGate, Nango, Vibe-Trading:** Not found in current Green Room ideas

## Recommendations
1. **Archive stale Labs content** — 626 stale files in Labs. Move completed/abandoned experiments to Archive.
2. **Consolidate duplicate folders** — Merge numbered-prefix pairs (02-Labs → Labs, etc.)
3. **Clean root artifacts** — Move `index.html` and `projects.json` to appropriate subfolders
4. **Review `.git-credentials`** — Consider if this should be in the vault or if it's a backup
5. **Link orphan notes** — Add wikilinks to 59 orphan notes for better discoverability

## Health Score: 63/100
- Security: 7/10 (minor issues, no critical vulnerabilities)
- Structure: 5/10 (stale content and duplicate folders need attention)
- AAE Stack: 7/10 (active ideas, integration in progress)
