---
date: YYYY-MM-DD
type: vault-audit
status: draft
author: Gentech
---

# Vault Health Audit — {DATE}

## Scope & Methodology

**Vault root:** `/root/vaults/gentech/`  
**Audit window:** Last 14 days  
**Sections scanned:** `00-HQ/`, `01-Agency/`, `02-Labs/`, `03-Projects/`, `03-Strategies/`, `08-Daily/`, `09-Green Room/`, `11-Mess Hall/`

Use skill **`vault-stale-content-audit`** for scan logic.

## Raw Findings

[Optional: include full shell output, Python dump, or significant excerpts here. Not required for executive report.]

## Stage 1: File Inventory

| Folder | Files Scanned | Oldest | Newest | Comment |
|--------|--------------|--------|--------|---------|
| 08-Daily/ | | | | |
| 09-Green Room/ | | | | |
| 00-Working-Memory.md | 1 | | | |
| 09-Green Room/handoffs/ | | | | |
| 00-HQ/Approvals/ | | | | |
| 02-Labs/Approvals/ | | | | |

## Stage 2: Gap Analysis

**Daily sync gaps (last 14d):**
- [List each missing YYYY-MM-DD]
- Weekend? Yes/No
- Reason (if known):

**Other stale items (>threshold):**
- [File path], [age] days — [reason for flag]

## Stage 3: Context Classification

Merge gaps + staleness into executive items

## Stage 4: Executive Report (≤5 items)

Paste final report here for copy/paste to user/HQ.

## Action Items

[Ownership handoff table for follow-up work not in executive report.]

## Next Audit

Scheduled: `cron` expression or EOD [NEXT_DATE]
