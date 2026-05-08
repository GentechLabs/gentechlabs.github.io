# 00-Working Directory Convention

**Purpose:** Jordan's active attention queue — items pending his review, approval, decision, or input.

**Location:** `/root/vaults/gentech/00-Working/`

**Scope:** Only items that require **direct Jordan action** live here. Not agent work-in-progress, not ideas, not backlogs.

---

## What Belongs in 00-Working

| Item Type | Example | When to use |
|-----------|---------|-------------|
| **Pending approvals** | `DEFI-MILESTONE-CONSOLIDATION-APPROVAL.md` | Jordan's YES/NO needed before execution |
| **Awaiting Jordan review** | Content drafts, spec documents | Jordan must read and sign off |
| **Jordan decision required** | `ALMANAK-INTEGRATION-GO-NO-GO.md` | Cross-team decision only Jordan can make |
| **Jordan input requested** | Specific questions needing Jordan's answer | Not something agents can decide autonomously |

**File naming:** `YYYY-MM-DD-short-description.md` with frontmatter:
```yaml
---
type: pending-approval|pending-review|decision-required|input-requested
priority: P0|P1|P2|P3
owner: @Jordan
due: YYYY-MM-DD (optional)
status: pending|in-review|approved|rejected
---
```

---

## What Does NOT Belong Here

- ❌ Agent in-progress work (belongs in department folders: `03-Strategies/`, `02-Labs/`, `04-Entertainment/`)
- ❌ Backlog ideas (belongs in `07-Ideas/`)
- ❌ Daily coordination notes (belongs in `11-Mess Hall/daily/`)
- ❌ Meeting agendas (belongs in `00-HQ/Operations/`)
- ❌ Generic reference material (belongs in `06-Content/Shared-References/`)

---

## Lifecycle

1. **Create:** Agent creates file in `00-Working/` with clear status and due date
2. **Consume:** Jordan reads, acts (approve/reject/decide), updates status in file frontmatter
3. **Archive:** Gentech moves resolved items to `10-Archive/00-Working-completed/` during daily sweep
4. **Sweep rule:** Files >7 days old in `00-Working/` automatically flagged as stale; move to `10-Archive/00-Working-stale/` with note

---

## Routing Notes

- **Gentech monitors** `00-Working/` during daily sync and mid-shift check
- `00-Working/` items are **Jordan's personal queue** — agents should not touch without explicit request
- When Jordan approves something in `00-Working/`, he typically moves it to department `Approvals/` folder or marks complete in place; Gentech archives
- **Never** use `00-Working/` for work that should be in `00-HQ/Approvals/` — that folder is for tracking approvals already submitted; `00-Working/` is the *inbound* queue

---

## Current Status (May 3, 2026)

**Observed:** `00-Working/` directory is **empty** despite 56 pending approvals elsewhere in vault and multiple handoffs awaiting Jordan ACK.

**Gap identified:** Pipeline disconnect — agents are placing items directly in `00-HQ/Approvals/` or `09-Green Room/` but not staging them in Jordan's personal queue `00-Working/`.

**Action required (Gentech):**
- Review all `00-HQ/Approvals/` items pending Jordan review → copy key ones to `00-Working/` with clear status
- Reinforce with team: New items requiring Jordan's YES/NO should be filed in `00-Working/` first, then moved to `Approvals/` after Jordan consumes

---

**Related:** `agent-coordination` skill — handoff protocols, approval workflows
