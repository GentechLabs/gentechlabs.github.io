---
name: vault-context-rotation
description: Rotate daily context in structured vaults — archive old threads, flag active discussions, prepare today's topics, maintain week-based folder hierarchy.
---

# Vault Context Rotation

**Purpose:** Standardize daily context rotation for structured vaults (like Mess Hall) with week-based folders, archival policies, and live board management.

**Scope:** Applies to vaults using the `YYYY/Wxx/YYYY-MM-DD/` folder convention with rotatable daily briefings and permanent live tracking boards.

---

## When to Use

- Daily morning rotation of context folders
- Week transition (Wxx → Wxx+1) archival and indexing
- Vault hygiene sweeps (identifying stale content, orphaned files)
- Preparing today-context.md from yesterday's active discussions
- Flagging overdue items, stalled handoffs, or coordination degradation

**Do NOT use for:** One-off note organization, ad-hoc file moves, or vault restructures — those are manual operations, not rotational.

---

## Core Conventions

### 1. Folder Structure

```
11-Mess Hall/
├── README.md (permanent)
├── handoff-board.md (permanent — live tracking)
├── agent-coordination-board.md (permanent — live tracking)
├── task-board.md (permanent — live tracking)
├── vault-sweep-YYYY-MM-DD.md (permanent — latest sweep only)
└── 2026/
    ├── W16/
    │   ├── 2026-04-16/
    │   └── 2026-04-18/
    ├── W17/
    │   ├── 2026-04-21/
    │   └── ... through Apr 26
    └── W18/  ← current week
        ├── 2026-04-27/  ← background (≥4 days old)
        ├── 2026-04-28/  ← background (≥4 days old)
        ├── 2026-04-29/  ← recent context
        ├── 2026-04-30/  ← still active (2 days old)
        ├── 2026-05-01/  ← yesterday
        └── 2026-05-02/  ← TODAY (freshly created)
```

**Rules:**
- Each day gets its own folder under current week (`Wxx`)
- Only `today-context.md` and optionally `rotation-log-YYYY-MM-DD.md` live in today's folder
- Files older than 3 days are BACKGROUND, verify before referencing
- Weeks >1 behind current are ARCHIVED, use only if explicitly resurrected
- Root-level files: permanent live boards stay forever, never rotate

### 2. Daily Context File (`today-context.md`)

Must include YAML frontmatter:

```yaml
---
date: YYYY-MM-DD
type: today-context
source: Gentech (HQ Coordinator)
status: current
---
```

Required sections:
1. `## 🕒 Active Discussions` — table with Topic, Owner, Status, Priority (use 🔴🟡🟢 emojis)
2. `## 🚩 Flags` — bullet list of blockers, stale items, coordination issues
3. `## 📋 Today's Agenda` — bullet checklist with `[ ]` / `[x]`
4. `## ✅ Yesterday's Highlights` — succinct achievements
5. `## 🏴 Archive Notes` — guidance on what's background vs recent

**Tone:** Warm, calm authority. 2–3 sentence max per thought. Use "We're building" not "They're building".

### 3. Rotation Log (`rotation-log-YYYY-MM-DD.md`)

Documents actions taken during rotation. Include:
- Files/folders created or moved
- Archive decisions (what week got closed)
- Stale items escalated
- Live board status check
- Cross-day context carry summary

Also uses YAML frontmatter with `type: daily-rotation`.

### 4. Week Archive Index (`archive-index-YYYY-MM-DD.md`)

At week boundary (Sunday/Monday), write an index inside the archived week folder:
- Week overview (active sprint, major events)
- Day-by-day table with file counts and key themes
- Archived decisions (reference only)
- Stalled/overdue items carried forward (reference handoff-board)

### 5. Flagging Standards

Use consistent severity language:

| Severity | Indicator | Escalation |
|----------|-----------|------------|
| 🔴 Critical | "OVERDUE since Apr 19", "BLOCKING", "highest risk" | Jordan within 2h |
| 🟡 High | "STALLED", "unclaimed for 7+ days", "needs triage" | Jordan within 12h |
| 🟢 Maintenance | "OPERATIONAL", "background", "no action needed" | None |

**Common flag patterns:**
- **Handoff storms:** "4+ handoffs unclaimed for N days" → explicit table with ID, From→To, Task, Age, Recommended Action (DROP/ESCALATION/REASSIGN)
- **Coordination degraded:** "All agents OFFLINE", "no check-ins since DATE" → require session check-in
- **Workload overload:** "Agent overloaded with 4+ P1s" → recommend triage conversation
- **Stale documents:** "Master todo stale (last updated DATE)" → specify owner to refresh

---

## Step-by-Step Rotation Protocol

1. **Inventory current state**
   ```bash
   ls /root/vaults/gentech/11-Mess\ Hall/2026/W18/
   # identify latest date folder, note loose files at root
   ```

2. **Read yesterday's today-context.md** (if exists) to carry forward active discussions and flags

3. **Check live boards** at root (`handoff-board.md`, `agent-coordination-board.md`, `task-board.md`) — DO NOT rotate these

4. **Create today's folder** `2026/W18/YYYY-MM-DD/` if not exists

5. **Write `today-context.md`**
   - Update Active Discussions from yesterday's context + any overnight changes
   - Refresh Flags based on handoff board ages, agent check-in status, workload signals
   - Set Today's Agenda with explicit owners and deadlines
   - Summarize Yesterday's Highlights from rotation-log or status files
   - Add Archive Notes guidance (what's background vs recent)

6. **Write `rotation-log-YYYY-MM-DD.md`**
   - List all actions taken (files created, folders archived, escalations made)
   - Capture any decisions or observations
   - Include table of week progression with file counts and status markers

7. **Week boundary check** (if today is Sunday/Monday and new Wxx folder needs to be created)
   - Write `archive-index-YYYY-MM-DD.md` in the week being closed
   - Summarize week's themes, decisions, carried-forward items

8. **Silent run compliance**
   - No `send_message` or external delivery
   - All output written to vault only
   - Final output is the report itself, not a delivery action

9. **Final verification**
   - Check YAML frontmatter on all new files
   - Confirm no loose non-permanent files left at root
   - Validate that all rotated content is inside dated folders
   - Ensure live boards remain untouched at root

---

## Pitfalls

- **Rotating live boards** — handoff-board.md, agent-coordination-board.md, task-board.md are permanent root-level fixtures. Never move or rename them.
- **Missing YAML frontmatter** — all rotation files must start with `---` frontmatter block including `date`, `type`, `source`, `status`. Obsidian and downstream tools rely on this.
- **Ambiguous file age thresholds** — stick to these rules: ≥4 days = BACKGROUND (verify before acting), ≥7 days = STALE (flag), ≥14 days = ARCHIVE (unless resurrected). Be explicit about day counts in flags.
- **Assuming agents checked in** — always read `agent-coordination-board.md` to verify last check-in timestamps before claiming "all agents online". If blank, flag as degraded.
- **Silent run violation** — never use send_message, external post, or delivery tools. The final response text IS the delivery mechanism for this skill's output.
- **Carrying forward dead threads** — if a discussion is flagging as STALLED for >10 days with no owner movement, explicitly recommend DROP or escalation rather than letting it linger.

---

## Verification

After rotation:
```bash
# Confirm today's files exist and are well-formed
ls /root/vaults/gentech/11-Mess\ Hall/2026/W18/$(date +%Y-%m-%d)/
head -1 /root/vaults/gentech/11-Mess\ Hall/2026/W18/$(date +%Y-%m-%d)/today-context.md
# should output: ---

# Check no loose non-permanent files at root (except the 4 live boards)
find /root/vaults/gentech/11-Mess\ Hall/ -maxdepth 1 -type f ! -name 'README.md' ! -name 'handoff-board.md' ! -name 'agent-coordination-board.md' ! -name 'task-board.md' ! -name 'vault-sweep-*.md'
# should return empty
```

---

## Related Skills

- `obsidian` — for reading/writing vault markdown files
- `kanban-board-setup` — if rotating task board structures
- `dogfood` — for vault QA and hygiene validation

---

## Reference Examples

- `references/session-example-may-2-2026.md` — Concrete output patterns, flag tables, and folder structure from a live May 2, 2026 rotation run.

---

**Last updated:** 2026-05-02 (initial capture from Gentech HQ rotation run)
