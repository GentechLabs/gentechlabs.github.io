---
type: review
date: 2026-06-15
tags: [weekly-review, vault-health, maintenance]
ai-first: true
---

## For future Gentech
Weekly vault health check. Critical issue: `.git-credentials` at vault root.

## Week of June 9–15, 2026

### Security 🔴
- **`.git-credentials` at vault root** — contains GitHub PAT in plaintext. Must move to `~/.git-credentials` or remove and use SSH/GCM.
- No `.env` files at vault root (clean).
- No untracked secrets detected.

### Structure
| Folder | Notes |
|--------|-------|
| Labs | 694 |
| Strategies | 160 |
| Green-Room | 120 |
| Archive | 85 |
| Content | 70 |
| HQ | 52 |
| Mess-Hall | 47 |
| Entertainment | 43 |
| Projects | 42 |
| Skills | 31 |
| Learning | 19 |
| Audits | 15 |
| Daily | 8 |
| Gaming | 5 |
| **Total** | **~1,456** across **41 top-level dirs** |

### Orphan Risk 🔴
- **1,397 files** lack `[[wikilinks]]` — 96% of the vault. Link density is critically low.
- Root cause: many files created without backlink discipline.

### Staleness 🔴
- **1,008 files** not updated in 14+ days (69% of vault).
- Labs and Strategies are the biggest contributors.

### Git Status
- 14 modified, 8 untracked — **needs commit and push**.

### Duplicate Folders ⚠️
- `AAE/` vs `Agent-Arena/` — unclear separation
- `HQ/` vs `00-HQ/` — dual structure
- `Labs/` vs `02-Labs/` vs `10-Labs/` — triple
- `Green-Room/` vs `09-Green Room/`
- `Mess-Hall/` vs `11-Mess Hall/`
- `Gaming/` vs `15-Gaming/`
- `Projects/` vs `03-Projects/`
- `Strategies/` vs `03-Strategies/`
- `profiles/` vs `Profiles/`

### AAE Stack ✅
Green-Room active builds include:
- **ERC-8004** — Gentech Agents (Open Source) framework
- **x402** — Lobby UI micropayment integration
- **Rain Agent Control Layer** — spending guardrails (Tier 1)
- **ERC-8226** — Brickken RAMS integration (Tier 1)
- **Agent Bill Pay MVP** — consumer gateway (Tier 1)
- Dry Powder Vault & Smart Money Rotation — delegated to Labs, specs complete

### Recommendations
1. **Immediate:** Remove `.git-credentials` from vault, commit pending changes
2. **This week:** Consolidate duplicate folders (HQ/00-HQ, Labs/02-Labs, etc.)
3. **Ongoing:** Increase link density — batch-add wikilinks to top 50 most-read files
4. **Archive pass:** Move stale Labs/Strategies content >30d to Archive

### Health Score: 38/100
Security (-15), orphans (-30), staleness (-12), duplicates (-5)
