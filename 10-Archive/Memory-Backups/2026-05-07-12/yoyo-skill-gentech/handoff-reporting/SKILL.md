---
name: handoff-reporting
description: Generate end-of-shift handoff reports by scanning vault state across departments. Aggregates accomplishments, pending approvals, active discussions, blocked items, and next steps from Mess Hall, Green Room, Approvals, and Daily logs.
triggers:
  - end-of-shift reporting
  - shift handoff generation
  - mid-shift coordination update
  - vault status aggregation
  - operational summary compilation
  - daily standup preparation
  - Jordan handoff preparation
  - urgent item flagging
  - deadline monitoring
  - system health check
steps:
  - Scan 08-Daily/ for today's and yesterday's activity logs
  - Scan 11-Mess Hall/ for recent team notes, discussions, and decisions
  - Scan 09-Green Room/ for active handoffs and open questions
  - Scan 00-HQ/Approvals/ for pending approval items requiring Jordan's sign-off
  - Search vault-wide for keywords like pending approval, awaiting Jordan, checkbox items, TODO, blocked, waiting
  - Check department folders (03-Strategies/, 03-Projects/) for recent file modifications
  - Parse frontmatter from markdown files to extract status, dates, owners
  - Compile structured report with sections — Accomplishments, Pending Approvals, Active Discussions, Blocked Items, Next Steps
  - Lead with most critical or high-priority items first
  - Keep format skimmable with headers, bullets, tables where appropriate
output_format:
  - Header — Date, shift type, delivery method
  - Section — Key accomplishments by team (YoYo Strategies, DMOB Labs, Desmond Creative)
  - Section — Pending approvals as table (Item, Type, Deadline, Owner, File Ref)
  - Section — Active discussions or debates requiring Jordan's call
  - Section — Blocked items (Blocker, Impact, Resolution Path)
  - Section — Tomorrow's priorities (2-3 per team)
  - Critical reminders or context box
pitfalls:
  - Don't omit sections even if empty (use "None")
  - Don't combine [SILENT] with content — if nothing to report, say [SILENT] only
  - Verify file paths exist before reading to avoid errors
  - Use Eastern time (UTC-4) when interpreting dates for shift boundaries
  - Distinguish between archived items (10-Archive) and active items (Green Room active-handoffs/)
  - Always state assumptions before conclusions in the report
  - Separate facts from projections clearly
references:
  - vault-path-reference.md
  - handoff-report-template.md
  - vault-scan-commands.sh
---

# Handoff Reporting — Operational Shift Summaries from Vault State

## Purpose
Transform vault state (markdown files across Mess Hall, Green Room, Approvals, Daily logs) into structured end-of-shift handoff reports for Jordan. This skill systematizes the pattern of aggregating team activity, pending items, and blockers into a concise, skimmable format.

## When to Use
- Scheduled cron job at shift end (early or late shift)
- Before Jordan's return from absence
- Daily standup or coordination call preparation
- Any situation requiring a "state of the union" snapshot across teams

## Prerequisites
- Read access to entire vault at `/root/vaults/gentech/`
- Familiarity with vault folder structure and naming conventions
- Ability to run terminal commands (`find`, `grep`, `cat`, `ls`)
- Markdown frontmatter parsing capability (YAML between `---` lines)

## Scan Sequence

### 1. Daily Logs (08-Daily/)
```bash
find /root/vaults/gentech/08-Daily/ -type f -name '*.md' | sort
```
Look for today's entry (if exists) and yesterday's entry for context. These provide raw activity logs.

### 2. Mess Hall (11-Mess Hall/)
```bash
find /root/vaults/gentech/11-Mess\\ Hall/$(date +%Y)/W$(date +%V)/ -type f -name '*.md' | sort
```
Recent team notes, discussions, decisions. Key files:
- `today-context.md` — coordinator's daily briefing
- `handoff-board.md` — **inter-agent handoff status with enforcement windows**
- `agent-coordination-board.md` — org structure, active sprint, escalation path
- Topic-specific discussion files (e.g., `almanak-aae-integration-question.md`)
- Any file containing "pending jordan" or "awaiting decision"

### 3. Green Room (09-Green Room/)
```bash
find /root/vaults/gentech/09-Green\\ Room/active-handoffs/ -type f -name '*.md'
find /root/vaults/gentech/09-Green\\ Room/ -maxdepth 1 -type f -name '*.md' | sort
```
Active handoffs show what teams are waiting on. Green Room open questions need Jordan's input.

### 4. Approvals (00-HQ/Approvals/)
```bash
find /root/vaults/gentech/00-HQ/Approvals/ -type f -name '*.md' | sort
```
Any file here is awaiting Jordan's explicit sign-off. Filter for this week's files.

### 5. Agent Coordination Board (11-Mess Hall/agent-coordination-board.md)
**ALWAYS READ THIS FIRST.** It contains:
- Org structure and department rules
- Handoff protocol enforcement rules (ACK deadlines, escalation thresholds)
- Active sprint table with due dates and status
- Escalation path

Check agent check-in rows to see who's online/offline today.

### 6. Active Hackathon Status (01-Agency/active-hackathons.md)
```bash
cat /root/vaults/gentech/01-Agency/active-hackathons.md
```
Current hackathon focus, deadlines, prize pools, and our play for each. Use for T-minus countdowns.

### 7. Project & Strategy Recent Changes (03-Projects/, 03-Strategies/)
```bash
# Last 24 hours
find /root/vaults/gentech/03-Projects/ -type f \( -name '*.md' -o -name '*.py' \) -mtime -1 2>/dev/null
find /root/vaults/gentech/03-Strategies/ -type f \( -name '*.md' -o -name '*.py' \) -mtime -1 2>/dev/null
```
Recent work activity. Key files:
- `03-Strategies/full-strategy-revenue-pipeline.md` — hackathon pipeline, revenue projections
- `03-Projects/defi-milestones.md` or `D5-Milestone-Tracker.md` — LP position progress
- `03-Strategies/Hackathon-Grants-Tracker.md` — opportunity radar, upcoming events
- `02-Labs/Hackathons/Active/` — technical build progress (Solana Frontier, Kite AI)
- `09-Green Room/genlayer-testnet-status.md` — testnet status for GenLayer builder program

### 8. Keyword Searches
```bash
# Pending items, checkboxes, TODOs
grep -r -i "pending approval|awaiting jordan|\[ \]|todo|to do" /root/vaults/gentech --include='*.md' | head -50
# Blocked items
grep -r -i "blocked|waiting on|blocking" /root/vaults/gentech --include='*.md' | head -30
# Urgent flags
grep -r -i "🔴|urgency|critical|asap" /root/vaults/gentech --include='*.md' | head -20
# Deadline proximity
grep -r -i "t-minus|deadline|due:" /root/vaults/gentech --include='*.md' | head -30
```
These catch checkbox items, explicit blockers, urgent flags, and deadline proximity throughout the vault.

### 6. Recent File Modifications
```bash
# Last 2 hours
find /root/vaults/gentech -type f \( -name '*.md' -o -name '*.py' \) -mmin -120 2>/dev/null
# Today's new files (by date)
find /root/vaults/gentech -type f -newermt "$(date +%Y-%m-%d)" 2>/dev/null
```
Shows what work actually happened today or recently.

## Content Assembly

**For MID-SHIFT reports** (partial shift check-in):
Lead with **🔴 URGENT ITEMS FLAGGED** — items requiring immediate attention within the next 2-4 hours. Use T-minus countdowns (T-8, T-14). Include:
- Active sprint items with approaching deadlines
- P0 handoffs with enforcement windows
- Systemic blockers (auth expired, disk full, jobs dead)
- Items where owner is offline/unresponsive

**🟡 HIGH PRIORITY — THIS SHIFT** — important but not immediately critical. Items to monitor or complete before shift end.

**🟢 WATCH / BACK-BURNER** — ongoing monitoring, deferred items, opportunistic tracking.

**📋 SHIFT ACTIONS RECOMMENDED** — prioritized action list by agent (YoYo, DMOB, Desmond, Gentech). One-line directives.

**For END-OF-SHIFT reports**: Lead with **✅ ACCOMPLISHMENTS** — what each team completed today. Use recent file modifications and daily logs as evidence.

**For EXECUTIVE summaries** (Jordan-level):
- TL;DR table (Item | Urgency | Owner | Action)
- Context bullets for each urgent item (why critical, impact if missed)
- Decision requests (if any)
- Quick wins list (≤1 hr tasks)
- Shift summary metrics

**ALWAYS include supporting sections:**
- **System Health Check** — cron job status, agent auth, disk space, hermes-brain sync, bytecode health
- **Files Touched Today** — list of recently modified files in Strategies/Projects (proves activity)
- **Handoff Board Status** — current unclaimed/overdue handoffs with ACK deadlines
- **Deadline Board** — gantt visualization + table of upcoming hackathons with days-left counts

## Formatting Rules

**Mandatory structure (choose template based on report type):**

| Report Type | Primary Sections | Separate Files |
|-------------|-----------------|----------------|
| End-of-shift | Accomplishments, Pending Approvals, Active Discussions, Blocked Items, Tomorrow's Priorities, Critical Reminders | None |
| Mid-shift | Urgent Items, High Priority This Shift, Watch/Back-Burner, Shift Actions, System Health, Files Touched Today | Full detailed report + executive summary (both) |
| Executive summary | TL;DR table, Urgent context, Decisions Required, Quick Wins, Shift Summary | Standalone for Jordan |

**Mid-shift output files** (save all to same W## folder):
1. `mid-shift-coordination-report.md` — full detailed report (all sections)
2. `mid-shift-executive-summary.md` — TL;DR for leadership
3. `deadline-board.md` — gantt + deadline table
4. `mid-shift-checkpoint.md` — daily log entry

**Timing & delivery:**
- Include date, shift type (early/late/mid), delivery method in header frontmatter
- Use headers (`#`, `##`, `###`) and bullets for skimmability
- Lead with most critical or high-priority item first
- Use emoji status markers consistently: 🔴 CRITICAL, 🟡 HIGH, 🟢 WATCH, ⚠️ FLAG, ✅ DONE, ⏳ PENDING
- Tables for structured data (handoffs, deadlines, blockers)
- If a section is empty, write "None" — don't omit
- Always include date and shift timing in header
- Never combine `[SILENT]` with content — either full report or `[SILENT]` only

**Deadline board:** Include mermaid gantt visualization + countdown table with "Days Left" column. Tag stale files (older than current week).

**Handoff board:** Always extract enforcement window and ACK deadlines. Flag items approaching cutoff (within 2h).

## Data Freshness & Assumptions
Assumes Eastern time (UTC-4) for shift boundaries. Use vault date folders as ground truth. When uncertain, state assumption explicitly: "Assuming today is May 3 based on vault folder structure..."

## Vault Path Reference
| Path | Purpose |
|------|---------|
| `08-Daily/` | Daily operator logs by date (YYYY-MM-DD.md) |
| `11-Mess Hall/` | Team discussions, decisions, context (year/W##/ folders) |
| `09-Green Room/` | Cross-team handoffs, debates, open questions |
| `00-HQ/Approvals/` | Explicit Jordan approval requests |
| `03-Strategies/` | YoYo's strategy work and configs |
| `03-Projects/` | DMOB Labs and Desmond Creative project work |
| `10-Archive/` | Historical items (ignore for active status) |
| `00-Working/` | Temporary scratch space (check for pending items) |

## Example Output Structure
```markdown
# 📊 End-of-Shift Handoff — 2026-05-03
**Shift:** Early (03:00 UTC) | **Delivery:** Silent vault-only run

## ✅ TODAY'S KEY ACCOMPLISHMENTS
- **DMOB Labs**: Fixed LP monitor script, synced across agent profiles; D5 milestone cron scaffolded
- **YoYo Strategies**: LFJ position log updated (efficiency 31.1%, IL spike flagged)
- **Desmond Creative**: Bug bounty scan automated; content thread draft ready

## ⏳ PENDING APPROVALS
| Item | Deadline | Owner | File |
|------|----------|-------|------|
| D5 Milestone Consolidation | EOD May 3 | DMOB+YoYo | `00-HQ/Approvals/2026-05-02-d5-milestone-tracker-consolidation.md` |

## 🔄 ACTIVE DISCUSSIONS / DEBATES
- **Almanak × AAE Integration** — cross-team, OPEN, PENDING DECISION

## 🚩 BLOCKED / STUCK ITEMS
- **YoYo Strategy Params Not Delivered** → blocks DMOB D5 milestone enhancements

## 🎯 WHAT'S ON DECK FOR TOMORROW
- **DMOB**: Solana Frontier devnet deploy, D5 cron enhancements merge
- **YoYo**: Strategy params doc + config thresholds
- **Desmond**: Master todo refresh, content thread for Jordan review

## ⚠️ CRITICAL REMINDERS
- Solana Frontier: May 11 (9 days)
- Kite AI: May 17 (15 days)
```