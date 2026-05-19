---
date: 2026-04-27
source: Desmond audit
type: consolidation-audit
status: pending-decision
---

# Vault + GitHub + Skills Consolidation Audit

## Vault Structure Diagnosis

### Current Top-Level Folders
```
00-HQ, 00-Inbox, 00-Sessions, 00-System
01-Agency, 01-Agents
02-AAE, 02-Audits, 02-Labs
03-Projects, 03-Strategies
04-Entertainment
05-Learning, 05-Product  ← duplicate #5!
06-Content, 06-Security
07-Ideas, 08-Logs
09-Green Room, 09-Templates
10-Archive, 11-Mess Hall, 12-Skills
```

### Critical Issues
| # | Problem | Evidence | Owner |
|---|---------|----------|-------|
| 1 | Lab/Project sprawl | `02-Labs/` has Hackathons, social-layer-poc, AAE-Merged; `03-Projects/` has AAE, AgentFi, Kite | DMOB / YoYo |
| 2 | Triple `social-layer-poc` | Exists in `02-Labs/`, `03-Strategies/`, `04-Entertainment/` | Desmond |
| 3 | AAE scattered | `02-AAE/`, `02-Labs/AAE-Merged/`, `03-Projects/AAE/`, `04-Entertainment/AAE-reference/` | DMOB |
| 4 | Duplicate numbering | `05-Learning` + `05-Product` | HQ / Gentech |
| 5 | Content/Ent boundary bleed | `04-Entertainment/dev-blog/` vs `06-Content/drafts/` | Desmond |
| 6 | Loose `memories` file | In root, should be in `00-System/agent-profiles/` | HQ / Gentech |
| 7 | Archive bloat | `10-Archive/` has 15+ subdirs, some may be recoverable | All agents |

### Skills Audit
- **Desmond installed**: 33 skills
- **Missing from bundle** (12): `arxiv`, `hackathon-bounty-scanner`, `birdeye-token-radar`, `cmc-watchlist-scraper`, `competitive-intelligence-recon`, `extract-interactive-docs`, `protocol-comparison-analysis`, `blogwatcher`, `hackathon-submission`, `lp-position-tracker`, `crypto-monitoring-cron`, `crypto-apy-tracking`
- **No optional-skills dir** found on this machine
- **Path refs to update**: Skills referencing `02-Labs/`, `03-Projects/`, `06-Content/` will break post-consolidation

### GitHub Repos (Gentech-Labs)
- `hermes-brain` | `gentech-vault` | `hermes-brain-backup` | `gentech-agency` | `hermes-workspace` | `hermes-control-interface`
- Naming is clean, no action needed unless vault reorg needs repo renames

## Proposed Consolidation Plan

### Phase 1: Fix Numbering + Merge Duplicates
- Rename `05-Product` → `07-Product` (shifts Ideas → 08, Logs → 09, etc.)
- OR merge `05-Learning` + `05-Product` into single `05-Product-Learning`

### Phase 2: Merge Labs + Projects + Audits Into `01-Gentech Labs/`
```
01-Gentech Labs/
  ├─ 🧪 Active Builds/           ← merged from 02-Labs (non-archive) + 03-Projects
  ├─ 🏗️ Hackathon Submissions/   ← merged from 02-Labs/Hackathons
  ├─ 🔍 Audit Practice/          ← merged from 02-Audits
  ├─ 📊 AAE/                     ← single canonical AAE folder (merge all 4 locations)
  ├─ 🧰 Boilerplates/            ← from 03-Strategies/AAE-LP-Dashboard-Boilerplate
  └─ 📦 Archive/
```

### Phase 3: Entertainment + Content Merge
```
02-Entertainment & Content/
  ├─ 🎬 Scripts/
  ├─ 📝 Drafts/
  ├─ 📱 X-Drafts/
  ├─ 🎙️ Podcast/
  ├─ 🎨 Visual Assets/
  ├─ 📊 Analytics/
  └─ 🚀 Launches/
```

### Phase 4: Skills Sync
- Install missing 12 skills to Desmond
- Check for optional-skills (blockchain/Base/Solana) — may need re-clone from fork
- Update all skill path references post-consolidation

### Phase 5: Archive Cleanup
- `10-Archive/` subdirs: classify as recoverable vs permanently dead
- Create `10-Archive/YYYY-MM-DD/` dating convention for future

## Agent Delegation
| Task | Best Agent | Reason |
|------|-----------|--------|
| Vault folder moves + git commit | Gentech (HQ) | Orchestrator, owns structure |
| AAE folder merge + smart contract refs | DMOB | Domain expertise |
| Entertainment/Content merge | Desmond | That's me |
| Skills install + path updates | Gentech + DMOB | DMOB for crypto skills, Gentech for orchestration |
| Archive triage | All agents in Mess Hall | Collaborative decision |
| GitHub repo rename? | Jordan (owner) | Needs human approval |

## Next Action
**Jordan approval needed** on:
1. `01-Gentech Labs` as the consolidated name
2. Whether to merge Entertainment + Content or keep separate
3. Whether GitHub repo names need to match vault names
4. Whether to install missing skills immediately or wait until after consolidation
