---
name: multi-agent-team-workflows
description: Establish and maintain coordination protocols for multi-agent teams — communication channels, approval workflows, stopping-point behavior, and vault organization conventions.
tags: [governance, coordination, vault, team]
---

# Multi-Agent Team Workflows

Set up and maintain coordination protocols for multi-agent teams working in shared Obsidian vaults.

## When to Use

- Onboarding new agents to a team
- Establishing or revising coordination protocols
- Setting up approval workflows for stakeholder sign-off
- Organizing shared vault folders (Mess Hall, Green Room, HQ)
- Defining stopping-point and idle-time behavior
- **Running a periodic vault sweep** to audit stale items, pending approvals, duplicate folders, and agent coordination gaps

## Communication Channels

| Channel | Purpose | When |
|---------|---------|------|
| **Green Room** | Real-time coordination, active work discussions | During work sessions |
| **Mess Hall** | Async check-ins, extended discussions, casual chat | Outside work cadence |
| **HQ** | Final decisions, approvals, stakeholder updates | When ready to surface |

**Rule:** Agents discuss internally first, then present unified output to stakeholder.

## Approval Workflow

1. Agent team reaches a decision requiring stakeholder sign-off
2. Create note in `00-HQ/Approvals/` using checkbox format
3. Naming: `YYYY-MM-DD-topic.md`
4. Stakeholder checks off approved items

### Approval Template

```markdown
# Approval: [Topic]

**Submitted by:** [Agent/Department]
**Date:** YYYY-MM-DD
**Priority:** [Low/Medium/High/Urgent]

## Summary
[1-2 sentence overview]

## What We Need
- [ ] Approval to proceed with [action]
- [ ] Budget allocation: $[amount]
- [ ] Timeline confirmation: [dates]

## Recommendation
[Agent team's recommended course of action]
```

### Status Codes

- `[ ]` = Pending
- `[x]` = Approved
- `[-]` = Rejected (include feedback)
- `[~]` = Needs revision

## Stopping-Point Protocol

When work reaches a natural stopping point:

1. **Ask stakeholder** what's next, or grab the next to-do
2. **If stakeholder is away 10–20 min:**
   - Audit recent work (code, content, decisions)
   - Review the vault brain / working memory
   - Have extended discussions in Mess Hall
   - Prep next logical steps for when stakeholder returns

## Vault Organization

### Mess Hall Structure

```
11-Mess Hall/
├── README.md
├── task-board.md
├── agent-coordination-board.md
├── handoff-board.md
├── daily/                    # Auto-generated summaries
├── archive/                  # Old conversations
└── YYYY/                     # Conversations by ISO week
    ├── WXX/
    │   ├── YYYY-MM-DD/
    │   └── YYYY-MM-DD/
    └── WXX/
```

**Naming:** `YYYY/WXX/YYYY-MM-DD/` — ISO week numbers for easy lookup.

### Cleanup Rules

- Remove empty week/month folders periodically
- Auto-purge daily summaries older than 7 days
- Archive old conversations to `archive/`

---

## Daily Mess Hall Rotation (vs Periodic Vault Sweep)

The **Vault Sweep Protocol** below is a deep, periodic audit (weekly/bi-weekly). But the Mess Hall also needs a **fast daily rotation** to keep conversation context fresh for the team. Do this every morning as the first task.

### What to Rotate (execution order)

1. **Archive yesterday's loose files**
   - Scan Mess Hall root for non-permanent `.md` files (everything except `README.md`, `task-board.md`, `agent-coordination-board.md`, `handoff-board.md`)
   - Create today's folder: `YYYY/WXX/YYYY-MM-DD/` using ISO week numbering
   - Move each loose file into the correct date folder underneath
   - Also use `find` with `-newer <last_rotation_file>` to catch files that were dropped into root since the last run

2. **Harvest cross-vault context**
   - Check `08-Daily/YYYY-MM-DD.md` or nearby daily summaries for yesterday's team highlights
   - Check `09-Green Room/` for active handoffs and requests due today
   - Peek at `task-board.md`, `agent-coordination-board.md`, and `handoff-board.md` in the root to surface stale check-ins, overdue handoffs, and overloaded agents

3. **Identify active discussions to flag**
   - Read the last 2–3 days of files in the current week folder
   - Extract: topic, owner, status, priority, and "why still active"
   - Sort into:
     - **Active** (>0 movement in last 48h, deadline >0 days out)
     - **Stalled** (>24h no movement, or handoff unclaimed past SLA)
     - **Due today** — requires action before the next rotation
   - Flag anything that is CRITICAL (deadline <10 days), STALLED, or awaiting a stakeholder decision

4. **Prepare today's context**
   - Write `today-context.md` in today's date folder with:
     - Active discussions table (topic, owner, status, priority)
     - Flags (blockers, stale items, overloaded agents, stale master-todos)
     - Today's agenda (checklist items with owners and priorities)
     - Yesterday's archive summary (files moved + key highlights harvested from daily notes)

5. **Note permanent root references**
   - These stay in root forever: `README.md`, `task-board.md`, `agent-coordination-board.md`, `handoff-board.md`
   - Everything else rotates out daily

### Rotation Log Template

Write a brief `rotation-log-YYYY-MM-DD.md` in the same date folder:

```markdown
---
date: YYYY-MM-DD
type: daily-rotation
source: [Agent Name]
status: complete
---

# Mess Hall Rotation Log — YYYY-MM-DD

## Actions Taken
1. Root-level loose file cleanup — list files moved and destinations
2. Date folder file counts — table: date | files | notes
3. Active discussions flagged — what and why
4. Archive notes — old threads buried and why

## 📋 Today's Agenda
- [ ] Item | Owner | Priority

## ⚠️ Flags for Stakeholder
- Overloaded agents, stale handoffs, decisions needed

## Permanent Root References (retained)
- README.md, task-board.md, agent-coordination-board.md, handoff-board.md
```

### Difference: Rotation vs Sweep

| | Daily Rotation | Vault Sweep |
|---|---|---|
| **Frequency** | Every morning | Weekly/bi-weekly |
| **Scope** | Mess Hall only + today-context prep | Full vault (all folders) |
| **Depth** | Fast — file movement + flagging | Deep — audit stale items, duplicates, empty folders, approvals queue |
| **Output** | `today-context.md` + `rotation-log.md` | `vault-sweep-YYYY-MM-DD.md` with health score |
| **Goal** | Fresh context for the day's shift | Long-term vault hygiene and stakeholder visibility |

---

## Vault Sweep Protocol

Run this periodically (e.g., nightly cron) to keep the vault healthy. **Never delete anything** — archive only.

### 5-Step Sweep

#### Step 1: Vault Health Scan
Check each of these and note findings:

| Check | Where | Threshold | Action |
|-------|-------|-----------|--------|
| Inbox aging | `00-Inbox/` | >7 days | Process or archive |
| Temp aging | `08-Temp/` or temp-like folders | >24 hours | Archive to `12-Archive/` |
| Stale handoffs | `09-Green Room/` | >5 days | Archive if superseded by newer decisions |
| Pending items | `11-Mess Hall/` | any | Flag in report |
| Duplicate folders/files | anywhere | — | Merge, keep newest, archive the rest |
| Empty folders | anywhere | — | Remove after confirming empty |
| Orphaned files | root level | outside standard folders | Flag for review |

#### Step 2: Agent Status Check
- Read latest files in `11-Mess Hall/` (last 3 days)
- Search for keywords: `pending`, `blocked`, `stuck`, `waiting on`, `handoff`, `TODO:*Jordan`
- Flag any agent waiting on another agent >24h with no ACK

#### Step 3: Pending Approvals for Stakeholder
Search across ALL vault folders for:
- Files containing `TODO:*Jordan` or `needs approval` or `pending review`
- `00-HQ/Approvals/` items not checked off
- `00-Inbox/` items older than target SLA
- Hackathon submissions not yet reviewed
- Contract/strategy changes awaiting sign-off

#### Step 4: Safe Cleanup Actions
- Move old items from `00-Inbox/` → `12-Archive/` or appropriate folder
- Move stale temp files → `12-Archive/`
- Merge duplicate folders (prefer hyphenated names, archive space-named duplicates)
- Remove truly empty folders (confirm first)

#### Step 5: Write Sweep Report
Write report to `11-Mess Hall/vault-sweep-YYYY-MM-DD.md` with:

1. **What was cleaned** — list files moved/archived with reasons
2. **Pending items needing stakeholder** — list with file paths and what action is needed
3. **Agent coordination issues found** — stale handoffs, agents waiting, overloaded agents
4. **Vault health score** — 1-10 with category breakdowns

### Report Header Template

```markdown
---
date: YYYY-MM-DD
type: vault-sweep
sweeper: [Agent Name]
status: complete
score: [1-10]
---

# Vault Sweep Report — YYYY-MM-DD
```

## Pitfalls

- **Don't skip internal discussion** — stakeholder wants one unified answer, not multiple agent voices.
- **Don't post directly to HQ** without Green Room/Mess Hall coordination first.
- **Don't leave stale empty folders** — clean up during vault maintenance.
- **Checkbox format matters** — stakeholder expects scannable checklists, not prose.
- **Avoid duplicate messages** — if multiple agents have relevant input, consolidate into a single response with clear sections (e.g., 'GenTech Strategies:', '02-Labs:'). Use the Green Room to coordinate before presenting to the stakeholder.
- **Update protocols dynamically** — if the stakeholder flags duplicate messages or requests adjustments (e.g., 'remember this'), update memory or skill protocols immediately to reflect the new behavior.

## Verification

After setup, confirm:
- [ ] Green Room and Mess Hall folders exist with READMEs
- [ ] HQ/Approvals/ folder exists with template
- [ ] All agents know which channel to use when
- [ ] Stopping-point behavior is documented
