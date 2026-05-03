# Sprint Plan Section Structure — GenTech Convention

**Applies to:** `02-Labs/`, project folders, any active sprint plan

Use this structure when creating or updating sprint plans during execution.

---

## Frontmatter

```yaml
---
date: YYYY-MM-DD
type: sprint-plan
source: [who initiated / directive origin]
status: ACTIVE | COMPLETE | CANCELLED
---
```

---

## Document Body Structure

```
# Sprint Plan — [Name]

## Approved Scope ([Date])

**Two-sentence rule:** State the focused scope, what's in, what's out.

| Hackathon | Deadline | Submission | Lead |

---

## [Hackathon/Project Name] ([Deadline]) — [Subtitle]

**Submission:** [one-line description]
**One-liner:** "[tagline if useful]"
**Prize:** [amount + sidetracks]

### Current Status
- ✅ [completed items]
- 🔄 [in-progress items]
- 📋 [planned/not started]

### Sprint Tasks ([Start] – [End])

#### [Role] — [Category]
- [ ] Task description
- [ ] Task description

---

### Coordination (or Communication)

### Daily Sync (Async)
- Each lead posts status to [channel] by EOD
- Blockers flagged immediately in Green Room

### Checkpoints
| Date | Milestone | Owner |

### Communication
- **Labs** — daily status, technical decisions
- **Green Room** — blockers, coordination
- **HQ** — Jordan updates, approval requests
- **Mess Hall** — end-of-day summaries

---

## 📅 [Date] Coordination Update

**Context:** [why this update exists]

| Department | Agent | Priority Tasks Assigned ([Date range]) |
|------------|-------|--------------------------------|

**Dependencies:** [what's blocking whom + timing]

**Additionally flagged:** [registrations, deadlines, risks]

---

*Created by: [name]*  
*Approved by: Jordan*  
*Date: YYYY-MM-DD*
```

---

## Rules

1. **Never duplicate task lists across files** — sprint plan is source of truth
2. **Use dated coordination update sections** to preserve history without fragmenting
3. **Keep table columns consistent** — Department | Agent | Tasks | Owner
4. **Dependencies must specify owner + eta** — "DMOB has until May 5" not "waiting on DMOB"
5. **Flag external deadlines** (hackathon registration, audit windows) separately from internal milestones
6. **Vault path references** always full absolute path: `/root/vaults/gentech/...`

---

## File Naming

- Active sprint: `sprint-[focus]-[dates].md` or `[project-name]-sprint-plan.md`
- Location: `02-Labs/` or project-specific folder
- Handoffs: `09-Green Room/active-handoffs/YYYY-MM-DD-brief.md` (link to plan, don't duplicate)
