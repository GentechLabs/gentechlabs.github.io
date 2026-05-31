# 🗜️ Vault Condensing Plan

**Generated:** 2026-05-30
**Total files:** 2,735 markdown files | 192MB repo
**Goal:** Condense from ~2,735 to ~800-900 files (70% reduction)

---

## 📊 Executive Summary

| Action | Files | Impact |
|--------|-------|--------|
| 🗑️ DELETE (safe, no review needed) | ~1,834 | 67% of vault |
| 🔀 MERGE (deduplicate across folders) | ~50 | Consolidate scattered content |
| 🔍 REVIEW (decide keep/delete) | ~150 | Mostly stale hackathon files |
| ✅ KEEP (active & current) | ~700 | Core vault |

---

## 🗑️ TIER 1: DELETE (1,834 files — safe to mass-delete)

### 10-Archive/ — DELETE ALL (1,627 files, 18MB)
The entire folder is archival trash from April-May 2026. **All deletable.**

| Subfolder | Files | Why deletable |
|-----------|-------|---------------|
| Memory-Backups/ | 832 | Hermes skill snapshots from April 24 — raw backup data |
| vault-cleanup-2026-05-18/ | 203 | Already cleaned from vault on May 18 |
| 11-Mess-Hall/ | 187 | Duplicates live 11-Mess Hall/archive |
| green-room-stale/ | 166 | Old Green Room content, superseded |
| multi-agent-era/ | 74 | Old multi-agent org structure, abandoned |
| _meta/ | 53 | Metadata from old archive operations (includes Python code, not vault content) |
| stale-project-files/ | 27 | Old project drafts and health checks |
| Empty-Files/ | 19 | Files that were "emptied" during cleanup |
| Agent-States-April/ | 16 | Old agent state snapshots |
| 08-Daily-Old/ | 14 | Old daily summaries |
| Watchdog-Checks-April/ | 6 | Old watchdog results |
| Cron-Changes-April/ | 5 | Old cron config changes |
| Content-Drafts-April/ | 4 | Old content drafts |
| 08-Logs-Old/ | 4 | Old logs |
| ETHGlobal-Dropped/ | 4 | Dropped hackathon |
| ElevenHacks-Dropped/ | 2 | Dropped hackathon |
| orphaned/ | 3 | Orphaned files |
| stale-tracking/ | 2 | Old tracking files |
| Kanban/ | 2 | Old kanban state |
| stale-todo/ | 1 | Stale todo |
| 00-Sessions/ | 1 | Old session file |
| Salvaged-Assets/ | 0 | Empty |
| Top-level .md | 5 | Old plans and reports |

### 12-Archive/ — DELETE ALL (41 files)
All from April-May 2026, superseded by current vault structure.

| Subfolder | Files | Content |
|-----------|-------|---------|
| 2026-05/Ops-May08/ | 10 | Old operational scripts |
| Usage/ | 6 | Old usage reports |
| vault-audits/ | 5 | Old vault audits |
| 08-Logs-W17/ | 5 | Old weekly logs |
| Approvals/ | 4 | Old approval records |
| Daily-Digest/ | 3 | Old daily digests |
| 08-Daily/ | 3 | Old daily files |
| sweep-summaries/ | 2 | Old sweep summaries |
| inbox-cleanup/ | 2 | Old inbox cleanup |
| Inbox/ | 1 | Old approval queue |

### 11-Mess Hall/archive/ — DELETE (166 files)
All from April 16 – May 19, 2026. Already archived. The valuable deliberation content has been captured in top-level files (task-board.md, considerations.md).

| Subfolder | Files | Content |
|-----------|-------|---------|
| W16-W21 weekly folders | ~140 | Daily summaries, rotation logs, context files |
| Standalone files | ~26 | Coordination boards, handoff boards, summaries |

**⚠️ PRESERVE BEFORE DELETING:** The daily summaries (2026-05-04 through 2026-05-10) contain detailed agent coordination decisions. These have been summarized in the vault-audits and top-level files.

---

## 🔀 TIER 2: MERGE & DEDUPLICATE (~50 files)

### HACKATHON-ROSTER-2026.md (2 copies)
- `02-Labs/Hackathons/HACKATHON-ROSTER-2026.md`
- `03-Projects/HACKATHON-ROSTER-2026.md`
- **→ Keep in 02-Labs/Hackathons, delete from 03-Projects**

### agent-coordination-board.md (2 copies)
- `11-Mess Hall/archive/agent-coordination-board.md`
- `10-Archive/11-Mess-Hall/agent-coordination-board.md`
- **→ Both deletable (already archived)**

### handoff-board.md (3 copies)
- `11-Mess Hall/archive/handoff-board.md`
- `10-Archive/11-Mess-Hall/handoff-board.md`
- `10-Archive/_meta/from-12-Archive/handoff-board-landscape-analysis.md`
- **→ All deletable (archived content)**

### Vanito.md (2 copies)
- `01-Agents/Vanito.md`
- `15-Gaming/Vanito/character-sheet.md` (different file)
- **→ Keep both (different purposes: agent config vs gaming character)**

### Defi Milestone files (13+ scattered)
- `02-Labs/defi-milestones.md` — working doc
- `00-HQ/defi-milestones-gamification-spec.md` — gamification layer
- `03-Strategies/Defi-Monitor/defi-milestone-enhancements-2026-05.md` — enhancements
- `06-Content/Architecture/defi-milestone-tracker-architecture.md` — architecture
- Multiple copies in 10-Archive and 11-Mess Hall/archive (all deletable)
- **→ Keep 02-Labs + 00-HQ versions, delete archive copies**

### AAE files (30+ scattered across 8+ folders)
- `02-Labs/AAE/` (8 files) — technical specs
- `03-Strategies/AAE-*` (7 files) — product strategy
- `02-Agent-Arena/` (10 files) — architecture
- `02-Labs/AAE-Merged/` (2 files) — merged docs
- `02-Labs/AAE-Reference/` (1 file) — reference
- **→ Keep 02-Agent-Arena as primary, consolidate 02-Labs/AAE + 03-Strategies/AAE specs there**

### Kite AI files (16+ scattered)
- `02-Labs/Hackathons/Kite-AI/` — main folder
- `03-Strategies/KiteAI*` (2 files)
- `05-Learning/Kite-AI-Hackathon-2026.md`
- `04-Entertainment/Kite-AI-CMC-Social-Drafts.md`
- Multiple in 06-Content
- **→ Consolidate to 02-Labs/Hackathons/Kite-AI, delete scattered copies**

---

## 🔍 TIER 3: REVIEW & DECIDE (~150 files)

### 02-Labs/ — REVIEW (310 files)
Many subfolders contain stale content from completed hackathons.

| Subfolder | Files | Recommendation |
|-----------|-------|----------------|
| Hackathons/Active/ | 25 | **REVIEW** — some completed (ARC Apr, Kite AI Apr, Solana Frontier May 11) |
| Hackathons/ root | 38 | **DELETE** completed hackathons, keep active ones |
| Contest-Scans/ | 26 | **REVIEW** — most recent May 29, some may be active |
| Security-Analysis/ | 10 | **KEEP** — useful reference |
| research/ | 8 | **REVIEW** — check if still relevant |
| AAE/ | 8 | **MERGE** into 02-Agent-Arena |
| DeFi/ | 7 | **REVIEW** — check overlap with 03-Strategies/Defi |
| From-Entertainment/ | 5 | **DELETE** — duplicates in 04-Entertainment |
| SDK-Comparisons/ | 4 | **KEEP** — useful reference |
| Design-Assets/ | 4 | **REVIEW** — check if still needed |
| security-audit/ | 3 | **KEEP** — audit reference |
| genlayer-recon/ | 3 | **REVIEW** — check if still relevant |
| Bug-Bounties/ | 3 | **KEEP** — active bounty tracking |
| R&D/ | 0 | **DELETE** empty folder |
| hermes-kanban/ | 0 | **DELETE** empty folder |
| Top-level .md | 136 | **REVIEW** — many stale grant applications, old sprint plans |

**Key stale items in 02-Labs top-level:**
- Grant applications (Solana Foundation, Chainlink BUILD, Arbitrum Foundation) — DRAFT, may be abandoned
- Old sprint plans (sprint-plan-solana-frontier-kite-ai.md) — completed
- Old status files (status.md) — check if current

### 03-Strategies/ — LIGHT REVIEW (157 files)
Most files are from May 2026 (current). Only 7 AAE files need consolidation.

### 09-Green Room/ — LIGHT REVIEW (114 files)
Active folder with designs, research, and runbooks. Check `completed/` subfolder for archival.

### 04-Entertainment/ — LIGHT REVIEW (44 files)
Active content. Check `handoffs/` and `drafts/` for staleness.

---

## ✅ TIER 4: KEEP AS-IS (~700 files)

### Active Operational Files
| Folder | Files | Status |
|--------|-------|--------|
| 00-HQ/ | 40 | ✅ Keep — central command |
| 00-System/ | 8 | ✅ Keep — workflows and SOPs |
| 01-Agents/ | 6 | ✅ Keep — agent configs |
| 03-Projects/ | 36 | ✅ Keep — active projects |
| 06-Content/ | 69 | ✅ Keep — content pipeline |
| 06-Audits/ | 14 | ✅ Keep — audit reports |
| 09-Templates/ | 5 | ✅ Keep — templates |
| 12-Skills/ | 31 | ✅ Keep — agent skills |
| 15-Gaming/ | 4 | ✅ Keep — gaming content |
| 08-Logs/ | 1 | ✅ Keep — monthly summary |
| 08-Daily-Digest/ | 2 | ✅ Keep — daily digests |
| 08-Projects/ | 1 | ✅ Keep — multichain status |
| 02-Agent-Arena/ | 10 | ✅ Keep — AAE architecture |
| Kanban/ | 2 | ✅ Keep — current kanban |

### 11-Mess Hall/ — KEEP (15 files)
| File | Status |
|------|--------|
| README.md | ✅ Keep — explains Mess Hall purpose |
| task-board.md | ✅ Keep — current sprint board (W22) |
| considerations.md | ✅ Keep — active decision items |
| nightly-sweep-*.md (3 files) | ✅ Keep — recent sweep reports |
| daily/*.md (2 files) | ✅ Keep — weekly review + skills update |
| vault-audits/*.md (5 files) | ✅ Keep — maintenance records |

---

## 📈 Projected Results

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Total .md files | 2,735 | ~850 | **69%** |
| Total size | 192MB | ~40MB | **79%** |
| 10-Archive | 1,627 | 0 | **100%** |
| 12-Archive | 41 | 0 | **100%** |
| 11-Mess Hall/archive | 166 | 0 | **100%** |
| 02-Labs | 310 | ~180 | **42%** |

---

## 🚀 Recommended Execution Order

1. **Delete 10-Archive/** — immediate 67% reduction, no review needed
2. **Delete 12-Archive/** — clean up 41 stale files
3. **Delete 11-Mess Hall/archive/** — clean up 166 archived files
4. **Merge AAE files** — consolidate from 30+ to ~15
5. **Merge Kite AI files** — consolidate from 16+ to ~8
6. **Delete 02-Labs empty folders** (R&D, hermes-kanban)
7. **Review 02-Labs/Hackathons** — delete completed hackathons
8. **Review 02-Labs top-level** — delete stale grant applications and old sprint plans

---

## ⚠️ Important Notes

1. **The 10-Archive/Memory-Backups (832 files)** are raw Hermes skill snapshots from April 24. These are NOT vault content — they're automated backups. Safe to delete.

2. **The Mess Hall archive contains daily summaries** with detailed agent coordination decisions. The key decisions have been captured in:
   - `11-Mess Hall/task-board.md` (current sprint priorities)
   - `11-Mess Hall/considerations.md` (active decisions)
   - `00-HQ/STATUS-BOARD.md` (org status)

3. **The `_meta` folder in 10-Archive** contains Python code and non-markdown files (Birdeye-Token-Radar project). These are not vault content.

4. **Git history preserves everything** — even after deletion, all content is recoverable from git history if needed.
