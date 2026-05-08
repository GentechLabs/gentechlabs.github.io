# Green Room Handoff File Structure — GenTech Convention

**Location:** `09-Green Room/active-handoffs/`
**Naming:** `YYYY-MM-DD-brief-description.md`
**Lifecycle:** Delete or archive after task completed or handed off >48h

---

## Minimal Handoff Template

```markdown
# 📡 Handoff — [Topic] ([Date])
**From:** [Agent/Role]
**To:** [Agent/Role] · [Other Agent if needed]
**Date:** YYYY-MM-DD
**Channel:** [source → target]
**Context:** [one sentence why this handoff exists]

---

## What Was Decided

[Bullet list of decisions made, max 5 items]

---

## Tasks Assigned (Brief)

### [Recipient] ([Department])
- [ ] Task (with deadline if known)
- [ ] Task

### [Other Recipient] ([Department])
- [ ] Task

---

## Dependencies & Timeline

| Milestone | Target | Owner |
|-----------|--------|-------|

---

## Open Questions

1. [Question needing answer]
2. [Risk or uncertainty]

---

**Status:** [In Progress | Blocked | Complete — next step]
```

---

## Principles

1. **Link, don't duplicate** — Reference sprint plan files, strategy docs, message threads
2. **Keep it minimal** — 15 lines max. Details live in source files
3. **Flag dependencies explicitly** — "Blocked until DMOB deploys Reputation program (May 5)"
4. **Assign single owner per task** — avoid shared ownership ambiguity
5. **Timebox questions** — "EOD May 3" not "soon"

---

## Anti-Patterns

- ❌ Repeating full sprint task tables — just link to sprint plan
- ❌ Vague dependencies — "waiting on DMOB" → "waiting on DMOB devnet deploy (eta May 5)"
- ❌ Multiple owners for single task — split into subtasks with clear assignees
- ❌ Leaving handoff files in Green Room root — always `active-handoffs/` subfolder
- ❌ Forgetting to delete after resolution — archive or remove within 24h of completion

---

## Example Handoff Flow

**Step 1:** CEO routes tasks via Telegram → creates handoff file linking to message
**Step 2:** Assignee claims by responding in Telegram + updating Green Room handoff status
**Step 3:** On completion, assignee marks handoff as complete + deletes file
**Step 4:** Daily vault sweep clears any stale handoffs (>24h unclaimed)
