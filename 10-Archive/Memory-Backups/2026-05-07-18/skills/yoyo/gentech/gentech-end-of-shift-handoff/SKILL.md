---
name: gentech-end-of-shift-handoff
description: Compile Jordan's end-of-shift handoff report from vault data
category: gentech
---

# Gentech End-of-Shift Handoff Reporting

## Overview
Generate comprehensive end-of-shift handoff reports for Jordan, summarizing daily activity across all teams (YoYo Strategies, DMOB Labs, Desmond Creative), tracking pending approvals, active discussions, blockers, and tomorrow's priorities.

**When to use:** Scheduled daily at shift transition (W18→W19, typically ~16:00 UTC Sunday). Also usable for ad-hoc handoff compilations.

**Trigger:** Cron job executing this skill or Jordan request for handoff summary.

## Prerequisites
- Hermes agent with vault access at `/root/vaults/gentech/`
- Read permissions on all vault directories
- Familiarity with Gentech vault structure and file naming conventions

## Workflow

### Phase 1 — Gather Daily Activity
1. Read today's daily log: `08-Daily/YYYY-MM-DD.md`
2. Parse YAML frontmatter (date, type, status, source)
3. Extract sections by team:
   - `## 🧪 Labs (DMOB)`
   - `## 📈 Strategies (YoYo)`
   - `## 🎨 Creative / Entertainment (Desmond)`
   - `## 🏛️ HQ / Coordinator`
4. Pull key accomplishments, decisions, incidents from each section
5. Note any agent check-in status (should be in HQ section)

### Phase 2 — Pending Approvals Scan
1. Read `11-Mess Hall/handoff-board.md` — extract rows with:
   - Status: `🚀 Pending Ack` or `⏳ Pending`
   - Assigned to: `@DMOB`, `@YoYo`, `@Desmond` (any agent)
   - Ack Deadline past current time → flag as ESCALATED
2. Grep vault for "pending approval" and "awaiting Jordan" strings:
   ```bash
   grep -r "pending approval" /root/vaults/gentech/
   grep -r "awaiting Jordan" /root/vaults/gentech/
   ```
3. Check `00-HQ/Approvals/` folder for files with `status: pending` frontmatter
4. Compile list with: task description, assignee, deadline, priority, action required

### Phase 3 — Active Discussions / Debates
1. Scan `09-Green Room/active-handoffs/` for recent handoff files (last 48h)
2. Scan `09-Green Room/` for discussion files with keywords: `debate`, `dispute`, `unresolved`, `?`
3. Check `11-Mess Hall/` for recent coordination files that indicate open questions
4. Summarize each discussion: context, open questions, decision needed, due date

### Phase 4 — Blocked Items
1. Extract from daily log's "## 🔓 Open Items / Blockers" table
2. Cross-reference with `00-HQ/Operations/Infrastructure-Issues.md` for active incidents
3. Categorize:
   - 🔴 P0: Production incidents (OAuth, API downtime, auth failures)
   - 🔴 P0: Bandwidth/ capacity crises
   - 🟡 Secondary: Placeholder addresses, config mismatches, pending reconciliations
   - 🟢 Process: Awaiting approvals, updates pending
4. For each blocker: owner, deadline, impact, resolution path

### Phase 5 — Tomorrow's Deck (W19 Kickoff)
1. Read `09-Green Room/master-todo.md` — extract top-priority items by department
2. Read `11-Mess Hall/task-board.md` — extract `## 🔴 ACTIVE SPRINT` items
3. Read `11-Mess Hall/2026/W19/YYYY-MM-DD-deadline-board.md` (most recent) for deadline countdowns
4. For each team (DMOB, YoYo, Desmond):
   - Top 3 priorities (ordered by priority + deadline proximity)
   - Specific deliverables due tomorrow
   - Any handoffs they must claim
5. Include mandatory session-start checklist from coordination board

### Phase 6 — Compile & Format
1. Structure output with headers: `=`, `##`, `-` bullets
2. Order by urgency: Critical → Pending → Blockers → Tomorrow
3. Use priority markers: 🔴 🔴 🟡 🟢
4. Include table for handoffs (From | To | What | Priority | Status | Ack Deadline)
5. Add dashboard view table at end for quick scan
6. List key files for Jordan review with full paths
7. Mark sections clearly with emojis for visual scanning

## Output Format
Deliver as single markdown text block (no file writes). Use:
- Top-level `=` banners for main sections
- `##` subheaders with team/theme emojis
- Bullet lists with indentation for subtasks
- Tables for handoff board and dashboard view
- Code fences for shell commands or file snippets
- Bold for critical alerts (`**🚨**`)

## Key File Locations
- Daily logs: `08-Daily/YYYY-MM-DD.md`
- Handoff board: `11-Mess Hall/handoff-board.md`
- Coordination board: `11-Mess Hall/agent-coordination-board.md`
- Pending approvals: `00-HQ/Approvals/`
- Infrastructure issues: `00-HQ/Operations/Infrastructure-Issues.md`
- Master todo: `09-Green Room/master-todo.md`
- Task board: `11-Mess Hall/task-board.md`
- Deadline board: `11-Mess Hall/2026/W19/YYYY-MM-DD-deadline-board.md`
- Green Room handoffs: `09-Green Room/active-handoffs/`

## Grep Patterns for Discovery
- Pending handoffs: `grep -r "🚀 Pending Ack" 11-Mess Hall/handoff-board.md`
- Checkbox items: `grep -r "\[ \]" 00-Working/ 11-Mess Hall/`
- Pending approval: `grep -r "pending approval" /root/vaults/gentech/`
- Awaiting Jordan: `grep -r "awaiting Jordan" /root/vaults/gentech/`
- Overdue items: `grep -r "overdue" 08-Daily/ 11-Mess Hall/`
- Incident status: `grep -r "INCIDENT\|ACTIVE" 00-HQ/Operations/`

## Handoff Board Table Format
```markdown
| From | To | What | Priority | Status | Assigned | Ack Deadline | Notes |
```
Statuses:
- `🚀 Pending Ack` — sent, awaiting acknowledgment
- `⏳ Pending` — queued, no deadline
- `🟡 Claimed` — recipient acknowledged
- `✅ Completed` — done
- `🔴 ESCALATED` — past deadline, flagged to Jordan

Enforcement rules (from board):
- ACK within 5 min of assignment
- Escalation at 15 min no ACK
- Stalled check: 24h claimed with no progress → flag for review

## Daily Log YAML Frontmatter
```yaml
---
date: YYYY-MM-DD
type: daily-sync
status: complete
source: gentech-cron
---
```
Body sections: `# Daily Second Brain Sync — YYYY-MM-DD (Day)`, `## TL;DR`, `## 🏛️ HQ`, `## 🧪 Labs`, `## 📈 Strategies`, `## 🎨 Creative`, `## ⚠️ Key Decisions`, `## 🔓 Open Items / Blockers`, `## 📊 Week WXX Activity Summary`, `## 📎 End Of Day Summary`.

## Escalation & Enforcement
- Cron job `d31c330959de` (Handoff Enforcement Monitor) runs every 15 min
- Deadlines hard-coded; no extensions without Jordan approval
- Unacknowledged → Gentech nudge → Jordan escalation (12h max)

## Pitfalls
⚠️ **All agents OFFLINE on weekends** — Sunday May 3 had zero check-ins; expect no activity, but still process Monday morning handoffs  
⚠️ **Handoff ack deadlines strict** — May 2 handoffs escalated by May 3 13:45 UTC; never assume agents claimed  
⚠️ **State file fragmentation** — multiple HERMES profiles cause divergent script outputs; always cross-reference with `lp-position-reader.py` for ground truth  
⚠️ **OAuth incidents block all data collection** — check `Infrastructure-Issues.md` first if scripts failing  
⚠️ **Two sources of truth** — milestone ladder hardcoded in `d5-master-cron.py` vs config file; reconcile immediately

## Verification
Before delivering handoff report, verify:
- [ ] Today's daily log exists and is non-empty
- [ ] Handoff board parsed correctly (≥1 pending items)
- [ ] Infrastructure issues file checked for active incidents
- [ ] Agent coordination board shows check-in status
- [ ] All P0 items listed under "Critical Reminders"
- [ ] Tomorrow's deck extracted from task-board and master-todo

## References
- Handoff board conventions: `references/handoff-board-conventions.md`
- Vault structure map: `references/vault-locations.md`
- Daily log schema: `references/daily-log-structure.md`
- Escalation protocol: `references/escalation-rules.md`
- Grep patterns cheat sheet: `references/grep-patterns.md`

## Notes
This skill supersedes ad-hoc handoff compilation; use for all formal shift transitions. Output format strictly follows Jordan's preference: skimmable, emoji-priority markers, tables for at-a-glance dashboards.

**Overlap note:** Partially overlaps with `gentech-coordination-audit` (which focuses on board audit only). This skill is broader — full cross-team synthesis, not just coordination metrics.