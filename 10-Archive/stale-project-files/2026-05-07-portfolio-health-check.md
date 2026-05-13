# Portfolio Health Check — 2026-05-07

**Reporter:** Gentech Cron (Daily Health Check)
**Date:** 2026-05-07 06:00 UTC
**Severity:** ⚠️ MEDIUM — 3 issues found, none breaking but data integrity is compromised

---

## ✅ Passing Checks

| Check | Status |
|-------|--------|
| `index.html` exists | ✅ 35KB, 938 lines |
| `projects.json` exists | ✅ 5KB, valid JSON |
| JSON syntax valid | ✅ No parse errors |
| HTML structure valid | ✅ DOCTYPE, charset, viewport, balanced tags |
| Script tags balanced | ✅ 3 open / 3 close |
| DIV tags balanced | ✅ 35 open / 35 close |
| No broken external links | ✅ Only 3 external refs (GitHub, LinkedIn, mailto) — all valid |
| GitHub remote configured | ✅ ProtoJay4789.github.io |
| Last commit on portfolio | ✅ 2026-05-07 00:44 UTC |

---

## 🚨 Issues Found

### ISSUE #1: Data Sync — Inline JS vs projects.json (HIGH)

The index.html contains **two separate copies** of project data that are out of sync with each other AND with projects.json:

**Inline JS (line 397):** 7 projects (used by filter UI)
**Embedded JSON (line 519):** 7 projects (used by roadmap columns)
**projects.json:** 10 projects

**Missing from HTML (exist only in projects.json):**
- `personal-finance` (Personal Finance Agent)
- `multi-agent-voice` (Multi-Agent Voice Integration)
- `solana-frontier` (Solana Frontier)

**Status/title/description mismatches:**
| Project | HTML Value | projects.json Value |
|---------|-----------|-------------------|
| agent-escrow status | `building` (deadline May 11) | `live` (no deadline) |
| kite-ai status | `building` | `research` |
| kite-ai title | "Kite AI Governance" | "Kite AI Brain Layer" |
| kite-ai description | Agent economy lifecycle... | Yield oracle integration... |
| lfj-avax-usdc description | Cross-chain rebalancing... | DeFi milestone tracking... |

**Root cause:** projects.json was updated on May 7 with the latest status, but the inline JS / embedded JSON in index.html was not regenerated. The HTML is serving stale data.

**Fix:** Regenerate index.html from projects.json as the single source of truth.

---

### ISSUE #2: Stale vault_path References (MEDIUM)

After the `03-Projects → 02-Labs` consolidation (commit c11d4c67, May 7 00:44 UTC), **9 of 10** vault_path references in both index.html and projects.json are broken:

| Project | Stale Path | Correct Path |
|---------|-----------|-------------|
| agent-escrow | `03-Projects/AAE/...` | `02-Labs/AAE/` |
| lfj-avax-usdc | `03-Projects/DeFi/...` | `02-Labs/DeFi/LFJ-AVAX-USDC.md` |
| multi-agent-voice | `03-Projects/Multi-Agent-Voice/` | ❌ NOT FOUND — missing from vault |
| solana-frontier | `02-Labs/Hackathons/Solana-Frontier/` | `02-Labs/Hackathons/Active/Colosseum-Frontier/` |
| personal-finance | `03-Projects/Personal-Finance/` | ❌ NOT FOUND — missing from vault |
| lets-fg | `03-Projects/Travel-Agent/` | ❌ NOT FOUND — missing from vault |
| hermes-kanban | `03-Projects/hermes-kanban/` | `02-Labs/hermes-kanban/` |
| birdeye-bip | `03-Projects/BirdeyeBIP/` | `02-Labs/BirdeyeBIP/` |
| tech-payment-router | `03-Projects/tech-burn-test/` | `02-Labs/tech-burn-test/` |

**Note:** 3 projects have no vault directory at all (multi-agent-voice, personal-finance, lets-fg). These may have been dropped during consolidation or never existed.

---

### ISSUE #3: Footer Date Staleness (LOW)

Footer text on line 933 reads:
> "Last updated: April 2026"

Portfolio was last meaningfully updated May 7, 2026. Footer should read "May 2026".

---

## 📋 Duplicate / Orphan Files

Three portfolio variants exist in `06-Content/`:
- `portfolio-canonical.html` — synced same commit as main, likely redundant
- `portfolio-updated-May4.html` — older version (May 4), stale
- `portfolio-current.html` — yet another variant

These should be consolidated or removed. `02-Labs/jordan-portfolio/index.html` should be the single canonical source.

---

## 🔧 Recommended Actions

1. **[DMOB]** Regenerate index.html from projects.json — make JSON the single source of truth, remove duplicate inline JS data
2. **[DMOB]** Update all vault_path references to post-consolidation paths
3. **[DMOB]** Add 3 missing projects or remove them from projects.json
4. **[Desmond]** Update footer date to "May 2026"
5. **[Desmond]** Clean up orphan portfolio files in `06-Content/`
6. **[Jordan]** Commit and push to GitHub Pages after fixes

---

*Filed by Gentech Cron Job — Daily Portfolio Health Check*
