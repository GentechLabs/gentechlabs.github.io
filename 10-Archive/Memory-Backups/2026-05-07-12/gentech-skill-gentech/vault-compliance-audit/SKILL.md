---
name: vault-compliance-audit
description: Systematic vault reviews for deadlines, action items, and milestone tracking — periodic compliance and status checks across document types.
triggers:
  - periodic_review
  - deadline_check
  - compliance_audit
  - milestone_tracking
  - "check the vault"
  - "review formation items"
  - monthly_reminder
---

# Vault Compliance Audit

**Purpose:** Conduct systematic reviews of the vault for deadlines, action items, milestones, and compliance items. Encodes the standard approach for periodic check-ups (monthly, quarterly, pre-deadline) across document types.

## When to Use

- Monthly/quarterly review reminders (LLC formation, annual reports, certifications)
- Pre-deadline checks (2-3 months before target dates)
- Compliance status checks (legal, financial, operational)
- Milestone progress audits
- Gap analysis: planned vs actual documentation

## Standard Workflow

### Phase 1: Scope Definition
1. Identify **target folders** — start with primary domain (`01-Agency/`, `02-Labs/`, `03-Projects/`, `04-Entertainment/`)
2. Identify **exclusion patterns** — skip `10-Archive/`, `11-Mess Hall/`, `12-Skills/`, `.git`, `.obsidian`, `memories/`
3. Define **search terms** — combine entity names (LLC, Gentech) with document types (formation, articles, operating agreement) and temporal signals (deadline, due, target, by [date])

### Phase 2: Multi-Stage Discovery
**Stage 1 — Filename/metadata scan** (fast, broad)
```bash
find /root/vaults/gentech/ -type f -name "*.md" | grep -vE "(10-Archive|11-Mess Hall|12-Skills|\.git|\.obsidian)"
```
Look for date-prefixed files (`2026-05-*`, `2026-09-*`) and obvious naming patterns (`*formation*`, `*legal*`, `*compliance*`).

**Stage 2 — Content deep-scan** (targeted, thorough)
Use Python or grep to scan candidate files for keyword combinations:
- Entity terms: `llc`, `LLC`, `articles of organization`, `certificate of formation`, `operating agreement`, `business entity`
- Temporal terms: `target`, `deadline`, `due`, `by `, `before`, `anniversary`, `renewal`
- Action terms: `todo`, `action`, `next`, `step`, `plan`, `complete`, `assign`

**Stage 3 — Timeline calculation**
If a target date exists:
```python
from datetime import datetime, timedelta
target = datetime(2026, 9, 2)
today = datetime.now()
days_until = (target - today).days
setup_window_start = target - timedelta(days=90)  # 3 months before
```
Determine urgency: >90 days (planning), 30-90 days (setup window), <30 days (immediate action).

### Phase 3: Action Item Extraction
Scan found documents for **explicit action language**:
- `- [ ]` unchecked todos
- Lines containing: "TODO:", "ACTION:", "NEXT:", "DEADLINE:", "DUE:"
- Imperative statements: "should begin", "need to", "must", "plan to"
- Assignment markers: `Jordan`, `DMOB`, `YoYo`, `Desmond`

### Phase 4: Gap Analysis
- **Found but incomplete:** docs exist but lack deadlines or next steps
- **Planned but not documented:** goal mentioned in roadmap but no dedicated doc
- **Imminent:** deadline within 30 days or passed
- **Future:** >90 days out, monitor only

### Phase 5: Reporting Format
Deliver a three-part summary:
1. **Status** — phase (planning/active/urgent) and key dates
2. **Key Documents** — list with paths and purpose
3. **Action Items** — what needs attention, by whom, by when
4. **Next Review** — when to re-check (usually 30 days before setup window)

## Pitfalls

- **Over-including archives:** Always exclude `10-Archive/` and `11-Mess Hall/` from active scans — those are historical, not current.
- **Confusing planning with action:** A "goal" on a roadmap is not an action item. Look for explicit sequencing or deadline language.
- **Date format variations:** Dates may be `September 2, 2026`, `9/2/2026`, `2026-09-02`. Normalize to ISO for calculation.
- **Orphaned references:** An LLC mention in a skills reference file (under `skills/` or `10-Archive/`) is not an active item — filter those out.
- **Single-entity bias:** An LLC may span multiple verticals (Labs + Entertainment). Search across `01-Agency/`, `02-Labs/`, `04-Entertainment/` even if asked about one folder.
- **Assuming a fixed vault topology:** Do NOT hardcode a specific set of top-level folders. The vault may include Obsidian system dirs (`.obsidian/`, `.git/`), agent directories (`01-Agents/`, `02-AAE/`), or domain-specific top-level folders (`03-Strategies/`, `04-Entertainment/`). **Robust approach:** discover actual top-level folders at runtime and validate only the *specific* paths requested (e.g. `00-HQ/Travel/`), not an assumed schema. See `references/actual-gentech-vault-structure-2026-05-03.md` for the live topology discovered during the May 3, 2026 audit.

## Verification Checklist

- [ ] Searched all active vault folders, excluded archives
- [ ] Ran both filename and content scans
- [ ] Calculated days until target and setup window
- [ ] Distinguished between goals, plans, and action items
- [ ] Listed all relevant documents with full paths
- [ ] Provided clear "needs attention" items or stated "nothing urgent"
- [ ] Set next review date appropriately

## Support Files

- `references/audit-python-template.md` — Python snippet for content scanning with keyword filters
- `references/timeline-calculator.md` — Date math snippets for determining urgency windows
- `templates/audit-report.md` — Markdown template for delivering findings

---

## Integration Notes

This skill assumes **dynamic** vault topology discovery — do NOT hardcode expected top-level folders. Instead, enumerate actual vault contents at runtime and validate only specific requested paths. See `references/actual-gentech-vault-structure-2026-05-03.md` for a concrete example of the live Gentech vault structure discovered during a May 3, 2026 audit.
