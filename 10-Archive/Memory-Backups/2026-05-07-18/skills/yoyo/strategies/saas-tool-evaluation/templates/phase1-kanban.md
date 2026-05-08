# Phase 1 Kanban Template — SaaS Tool Integration

**Purpose:** Structured project board for Phase 1 implementation of any new SaaS tool integration.

**Usage:** Copy to `03-Strategies/<tool>/phase1-kanban.md` and customize.

---

## Board Structure

### Columns
```
BACKLOG → IN PROGRESS → REVIEW → DONE → DEPLOYED
```

### Card Anatomy
Each card includes:
- **ID:** Tool-specific code (e.g., CMP-01)
- **Assignee:** Owner
- **Est.:** Hours
- **Dependencies:** Card IDs that must finish first
- **Priority:** P0/P1/P2
- **Tasks:** Checklist of actionable items
- **Definition of Done:** Explicit criteria
- **Links:** Vault paths, external URLs

---

## Template Start

```
# <TOOL> Phase 1 — Implementation Kanban

**Target completion:** YYYY-WW (Month DD, YYYY)
**Budget:** $X/mo (<tier name>)
**Owner:** <Agent/Person>
**Total dev time:** ~X hours

---

## 🏁 Goal

<One sentence describing the Phase 1 objective>

Success criteria:
- ✅ <Criterion 1>
- ✅ <Criterion 2>
- ✅ <Criterion 3>

---

## 📊 Progress Dashboard

| Metric | Current | Target |
|--------|---------|--------|
| Tools integrated | 0/X | X/X |
| Hours spent | 0/X | X |
| Monthly quota used | 0% | <Y% |
| Overage cost risk | $0 | <$Z/mo |

---

## 📋 Columns

```
BACKLOG     →  IN PROGRESS   →  REVIEW   →  DONE   →  DEPLOYED
(not started)  (active work)  (QA/test)  (complete) (in production)
```

---

## 🗂️ BOARD

### 🔵 BACKLOG — Ready to Start

#### Card 1 — Tool Name
- **ID:** TLM-01
- **Assignee:** Agent
- **Est.:** X hrs
- **Dependencies:** None

**Tasks:**
- [ ] Task description
- [ ] Another task

**Definition of Done:**
- [x] Done condition 1
- [x] Done condition 2

**Links:**
- Vault: `path/to/file`
- Dashboard: https://example.com

*(Repeat cards 2–N...)*

---

### 🟡 IN PROGRESS — Active Work

*(Move cards here when started)*

---

### 🟢 REVIEW — QA/Testing

---

### ✅ DONE — Completed

---

### 🚀 DEPLOYED — In Production

---

## 📈 Burndown Chart

```
Week 1:  ████████░░░░░░░░░░░░  X/X hrs (%)
Week 2:  ░░░░░░░░░░░░░░░░░░░░  0/X hrs (0%)
Week 3:  ░░░░░░░░░░░░░░░░░░░░  Buffer/overflow
Target completion: Month DD, YYYY
```

---

## 💰 Budget Tracker

| Date | Expense | Category | Notes |
|------|---------|----------|-------|
| YYYY-MM-DD | $X | Tool Name | Monthly subscription |
| YYYY-MM-DD | $Y | Overage | Phase 1 usage < X calls |
| **Total (Phase 1)** | **$Z** | — | — |

---

## 📝 Meeting Notes

**YYYY-MM-DD — Kickoff:**
- Attendees: Jordan, YoYo, DMOB, Storm
- Decisions: Approved budget, assigned cards
- Action items:
  - [ ] Owner: Task
  - [ ] Owner: Task

---

## 🔗 Related Documents

- Business case: `03-Strategies/analysis/YYYY-MM-DD-<tool>-cost-benefit.md`
- Implementation logs: `03-Strategies/<tool>/logs/`
- Skills: `skills/<tool>/`
- Credentials: `03-Strategies/credentials/`

---

**Last updated:** YYYY-MM-DD
**Next review:** YYYY-MM-DD
```

---

## Field Descriptions

| Field | Meaning | Example |
|-------|---------|---------|
| **ID** | Unique card ID (TLM = Tool Evaluation; CMP = Composio; etc.) | `CMP-01` |
| **Assignee** | Who owns this | `DMOB`, `YoYo`, `Storm` |
| **Est.** | Estimated hours | `2 hrs`, `4 hrs` |
| **Dependencies** | Card IDs that must finish first | `CMP-02, CMP-05` |
| **Priority** | P0=critical, P1=important, P2=nice-to-have | `P0` |
| **Definition of Done** | Explicit pass/fail criteria | `[x]` checkboxes |
| **Links** | Vault paths + external URLs | `03-Strategies/credentials/` |

---

## Best Practices

1. **Keep cards atomic** — one deliverable per card
2. **Estimate realistically** — pad 20% for unknowns
3. **Dependencies explicit** — prevents blocking
4. **DOD before acceptance** — no "done-ish"
5. **Burndown chart updated weekly** — track velocity
6. **Blocked cards moved to 🔴 column** — escalates visibility

---

## Color Legend

- 🔵 **Backlog** — Ready, not started
- 🟡 **In Progress** — Active work
- 🟢 **Review** — QA/testing/peer review
- ✅ **Done** — Complete, awaiting deployment
- 🚀 **Deployed** — In production
- 🔴 **Blocked** — Stuck, needs decision/input

---

## Adaptations

**For larger Phase 2/3:**
- Add `Epic` parent cards grouping related tasks
- Add `Testing` sub-column within Review
- Add `Blocked reason` field on red cards

**For solo execution (one agent):**
- Remove assignee column
- Add `Status` field (Not Started / Active / Review / Done)
- Simplify burndown to weekly checkboxes

---

**Template version:** 1.0
**First used:** Composio Phase 1 Kanban (2026-05-03)
**Maintained by:** YoYo (Strategies)
