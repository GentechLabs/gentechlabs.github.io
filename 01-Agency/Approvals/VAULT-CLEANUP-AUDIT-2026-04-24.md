# 📝 Vault Cleanup Audit — 2026-04-24
**Status:** Pending Jordan approval  
**Goal:** Consolidate orphans, remove dead folders, align structure with INDEX.md

---

## 📊 Current State

| Folder | Files | Status | Action |
|--------|-------|--------|--------|
| **00-Inbox** | 4 | ✅ Active | Keep |
| **00-Sessions** | 1 | ⚠️ Orphan | → Move to 10-Archive |
| **00-System** | 41 | ✅ Active (agent profiles, SOPs) | **Rename** → 00-System-Config or merge into 12-Skills |
| **01-Agency** | 55 | ✅ Active | Keep |
| **01-GenTech HQ** | 1 | ❌ Duplicate | → Merge into 01-Agency |
| **01-HQ** | 4 | ❌ Duplicate | → Merge into 01-Agency |
| **01-News** | 0 | ❌ Empty | **Delete** |
| **01-Projects** | 6 | ❌ Duplicate | → Merge into 03-Projects |
| **02-Labs** | 885 | ✅ Active | Keep |
| **02-Research** | 1 | ⚠️ Orphan | → Merge into 03-Strategies |
| **03-Projects** | 1451 | ✅ Active | Keep |
| **03-Strategies** | 98 | ✅ Active | Keep |
| **04-Entertainment** | 42 | ✅ Active | Keep |
| **04-Intelligence** | 1 | ⚠️ Orphan | → Merge into 03-Strategies |
| **05-Learning** | 13 | ✅ Active | Keep |
| **06-Content** | 21 | ✅ Active | Keep |
| **06-Security** | 3 | ⚠️ Underused | → Merge into 02-Labs/Security-Analysis |
| **07-Ideas** | 12 | ✅ Active | Keep |
| **07-Projects** | 0 | ❌ Empty (active/completed subdirs) | **Delete** |
| **08-Activity log** | 6 | ✅ Active | Keep |
| **08-Daily** | 4 | ❌ Duplicate | → Merge into 08-Activity log |
| **09-Collaboration** | 44 | ⚠️ Overlap | → Merge into 09-Green Room (rename to 09-Collaboration?) |
| **09-Green Room** | 18 | ✅ Active | Keep |
| **09-Templates** | 5 | ✅ Active | Keep |
| **10-Archive** | 1226 | ✅ Active | Keep |
| **11-Mess Hall** | 38 | ✅ Active | Keep |
| **12-Archive** | 48 | ❌ Duplicate archive | → Merge into 10-Archive |
| **12-Skills** | 27 | ✅ Active | Keep |
| **13-Green Room** | 1 | ❌ Duplicate | → Merge into 09-Green Room |
| **Archive** (root) | 6 | ❌ Duplicate | → Merge into 10-Archive |
| **Audits** (root) | 0 | ❌ Empty | **Delete** |
| **Kanban** (root) | 1 | ✅ New (hermes-kanban) | **Integrate** → 03-Projects/Kanban or 00-Inbox |
| **ProtoBots** (root) | 0 | ⚠️ Empty | **Delete or merge into 02-Labs** |
| **references** (root) | 2 | ⚠️ Orphan | → Merge into 03-Strategies or 02-Labs |
| **research** (root) | 1 | ⚠️ Orphan | → Merge into 03-Strategies |

---

## 📝 Proposed Clean Structure

```
00-Inbox/               → Triage, incoming
00-System/              → Agent profiles, SOPs, cron configs (RENAME from 00-System)
01-Agency/              → LLC, ops, finances, HQ working (MERGE 01-HQ + 01-GenTech HQ here)
02-Labs/                → Dev, code, hackathons, audits (MERGE 06-Security here)
03-Strategies/          → DeFi, market, research (MERGE 02-Research + 04-Intelligence here)
03-Projects/            → All active projects (MERGE 01-Projects + 07-Projects here)
04-Entertainment/       → Content, social, branding
05-Learning/            → Courses, notes
06-Content/             → Desmond domain — KEEP ( podcasts, specs, drafts)
07-Ideas/               → Brain dumps, travel
08-Activity log/        → Daily/weekly/monthly (MERGE 08-Daily here)
09-Green Room/          → Agent collaboration (MERGE 09-Collaboration + 13-Green Room here)
09-Templates/           → Note templates
10-Archive/             → All archived stuff (MERGE 12-Archive + Archive + 00-Sessions here)
11-Mess Hall/           → Brainstorming, off-topic
12-Skills/              → Agent protocols, coordination rules
Kanban/                 → hermes-kanban boards — integrate into 03-Projects or keep root
assets/                 → Branding, images, voices
```

---

## ⚠️ Structural Fixes Needed

1. **INDEX.md mismatch:** Says Desmond writes to `04-Entertainment` only, but `06-Content` is also Desmond's domain with 21 active files. Update INDEX to include both.

2. **06-Security underused:** Only 3 files. D-Mob's security work is scattered across `02-Labs/Security-Analysis`, `02-Labs/security-audit`, and `06-Security`. Consolidate.

3. **12-Archive is a mess:** 48 files of old session dumps. Merge into `10-Archive/2025-2026-Sessions`.

---

## 📋 Files to Move (Details)

### Merge 01-HQ + 01-GenTech HQ → 01-Agency
- `01-GenTech HQ/Brain-Map.md` → `01-Agency/Brain-Map.md`
- `01-HQ/brain-backup.md` → `01-Agency/archive/brain-backup.md`
- `01-HQ/llc/` → `01-Agency/llc/`
- `01-HQ/operations/` → `01-Agency/operations/`

### Merge 01-Projects → 03-Projects
- `01-Projects/AAE/` → `03-Projects/AAE/` (check for dupes first)
- `01-Projects/Birdeye-Token-Radar/` → `03-Projects/Birdeye-Token-Radar/`

### Merge 08-Daily → 08-Activity log
- `08-Daily/Monthly-Summaries/` → `08-Activity log/Monthly-Summaries/`

### Merge 09-Collaboration → 09-Green Room
- `09-Collaboration/Inbox.md` → `09-Green Room/Inbox.md` (or keep at root?)
- `09-Collaboration/active-tasks/` → `09-Green Room/active-tasks/`
- `09-Collaboration/drafts/` → `09-Green Room/drafts/`

### Merge orphans → 03-Strategies
- `02-Research/LayerZero-Risk-Analysis.md` → `03-Strategies/research/`
- `04-Intelligence/layerzero-dvn-warning-2026-04-20.md` → `03-Strategies/intelligence/`
- `research/genlayer-ecosystem/` → `03-Strategies/research/`
- `references/` → `03-Strategies/references/`

### Merge 06-Security → 02-Labs
- `06-Security/Audit-Findings/` → `02-Labs/Audit-Findings/`
- `06-Security/Vuln-Patterns/` → `02-Labs/Vuln-Patterns/`

### Delete Empty Folders
- `01-News/` (empty)
- `07-Projects/` (empty subdirs)
- `Audits/` (empty)
- `ProtoBots/` (empty at root, but has files in 02-Labs/ProtoBots)

---

## ✅ Approval Checklist for Jordan

- [ ] **Approve structure** — Does the proposed folder layout look right?
- [ ] **06-Content** — Confirm Desmond owns both `04-Entertainment` + `06-Content`
- [ ] **06-Security** — Confirm merging into `02-Labs` is okay
- [ ] **09-Collaboration** — Should we merge into Green Room or keep separate?
- [ ] **Kanban folder** — Where should hermes-kanban boards live? `03-Projects/Kanban/` or root `Kanban/`?
- [ ] **Go/no-go** — Ready to execute cleanup?

---

*Generated by Desmond — 2026-04-24*
