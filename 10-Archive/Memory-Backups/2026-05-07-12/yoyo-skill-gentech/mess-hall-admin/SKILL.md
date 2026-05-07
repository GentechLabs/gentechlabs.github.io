---
name: mess-hall-admin
description: Daily administrative operations for Gentech's Mess Hall coordination hub
domain: gentech
tags:
  - coordination
  - handoff
  - daily-ops
  - context-rotation
  - admin
status: active
version: 1.0.0
created: 2026-05-03
maintainer: YoYo (Strategies)
---

# 🏛️ Mess Hall Administration

Daily context rotation and coordination hygiene for the Gentech Mess Hall (`11-Mess Hall/`).

## Purpose

Maintain continuity of conversation context across agent sessions by:
- Archiving stale threads
- Flagging active discussions with deadlines
- Preparing daily topic briefs
- Enforcing handoff protocol compliance

This is a **silent-run** cron task (no messages). All output is file-based.

---

## Trigger & Schedule

| | |
|---|---|
| **Trigger** | Scheduled cron job (Gentech dispatch) |
| **Frequency** | Daily at 11:00 UTC |
| **Agent** | YoYo (Strategies) — primary duty |
| **Fallback** | Gentech (if YoYo unavailable) |

---

## Scope

### Files Managed

| Path | Purpose |
|------|---------|
| `11-Mess Hall/daily/` | Active daily handoff files (7-day retention) |
| `11-Mess Hall/archive/` | Monthly archive (e.g., `archive/2026-04/`) |
| `11-Mess Hall/handoff-board.md` | Active handoff tracking table |
| `11-Mess Hall/agent-coordination-board.md` | Org-wide coordination status |
| `08-Daily/` | Second brain daily summaries |

---

## Procedure

### 1. Scan Recent Activity

List files modified in the last 24 hours across `11-Mess Hall/`:
```bash
find /root/vaults/gentech/11-Mess-Hall/ -type f -mtime -1
```

Identify:
- New daily summaries (yesterday's wrap-ups)
- Handoff updates needing flagging
- Agent coordination check-ins

### 2. Archive Stale Content

**Retention policy:**
- `daily/` files older than 7 days → move to `archive/YYYY-MM/`
- Keep `README.md` in `daily/` untouched

**Archive structure:** `archive/2026-04/` (year-month)

### 3. Create Today's Morning Handoff

**File:** `11-Mess Hall/daily/YYYY-MM-DD-morning-handoff.md`

Use template `templates/morning-handoff.md` (see references).

Required sections:
- Archive actions (just completed)
- Active discussions — pending ACK handoffs with deadlines
- Sprint status (current week focus)
- Completed activity (previous day summary)
- Today's topics (numbered list)
- Active blockers (table with action)
- Metrics snapshot (LP positions, handoff count, etc.)
- Alerts summary (immediate vs ongoing)
- Handoff checklist (per agent)
- Previous day reference (table of files)
- Forward outlook

**Frontmatter:**
```yaml
---
date: YYYY-MM-DD
type: context-rotation
agent: YoYo (Strategies)
shift: morning-rotation
status: complete
---
```

### 4. Update Handoff Board

Add enforcement reminder section above the handoff table if any handoffs from the previous day remain unacknowledged.

**ACK deadline enforcement:**
- Submission + 2 hours → ACK due
- 2–4 hours unclaimed → Gentech nudge
- 4–12 hours unclaimed → escalated to Jordan
- >12 hours claimed with no progress → stalled flag

Format (insert before `---` separator):
```markdown
## ⚠️ Today's Enforcement Window (May 3)

**ACK Deadline:** 13:45 UTC for handoffs submitted May 2
**Handoffs pending acknowledgment:**
| ID | From | To | Task | Submitted | Deadline |
|----|------|----|------|-----------|----------|
| H2026-05-02-01 | Gentech | DMOB | ... | May 2 12:45 | May 2 23:59 UTC |

**Action:** DMOB and YoYo must update status to `🟡 CLAIMED` before deadline or escalation is triggered.
```

### 5. Update Agent Coordination Board

Insert context update block immediately after **Department Rules** section.

```markdown
## 📍 Context Update — 2026-05-03 Morning Rotation

**Rotation completed:** 11:00 UTC by YoYo (Strategies)

### Sprint Status (Week of May 2–11)
- **Solana Frontier** — Day 3/12, deadline **May 11** (P0)
- **Kite AI** — Secondary priority, deadline **May 17** (P1)

### Handoff Compliance Alert
- **2 handoffs** submitted May 2 remain unacknowledged (H2026-05-02-01, H2026-05-02-02)
- **ACK deadline:** 13:45 UTC today
- **Escalation:** Unclaimed → Gentech nudge → Jordan (per enforcement rules)

### Agent Check-In Required
All agents currently OFFLINE in coordination board. Session start MUST include:
1. Read this file
2. Check `handoff-board.md` for tags
3. Update your row in "Agent Session Check-In" table
4. Acknowledge any pending handoffs within 2h

### Blockers
1. D5 config thresholds (YoYo) → blocks DMOB integration
2. Hermes-brain sync verification (Gentech) → blocks cron install

---
```

### 6. Daily Second Brain Sync

At ~16:00 UTC, generate daily summary to `08-Daily/YYYY-MM-DD.md` capturing all agent activity, decisions, and file movements.

---

## Pitfalls

| # | Pitfall | Mitigation |
|---|---------|------------|
| 1 | **Silent-run violation** — sending Telegram messages | This is a file-only task. Do NOT call `send_message` or any notification tool |
| 2 | **Archive over-pruning** — deleting files <7 days old | Check `daily/` file dates; only archive if `mtime < now - 7 days` |
| 3 | **Handoff deadline mis-match** — using wrong timezone | All deadlines are UTC. Local time conversions are agent responsibility |
| 4 | **Broken frontmatter** — malformed YAML | Use exact keys: `date`, `type`, `agent`, `shift`, `status` |
| 5 | **Obsidian sync failure** — `ob sync` not available | Do NOT rely on `ob` command. Vault writes are persistent without sync |
| 6 | **Duplicate daily file** — re-creating today's file | Check existence before writing; append if already exists |

---

## Verification

After completion, validate:
```bash
# 1. Morning handoff exists and has content
test -s /root/vaults/gentech/11-Mess\ Hall/daily/$(date +%Y-%m-%d)-morning-handoff.md

# 2. Archive updated (if applicable)
ls -lt /root/vaults/gentech/11-Mess\ Hall/archive/*/

# 3. Handoff board contains enforcement reminder
grep -q "Today's Enforcement Window" /root/vaults/gentech/11-Mess\ Hall/handoff-board.md

# 4. Coordination board updated with context block
grep -q "Context Update — $(date +%Y-%m-%d)" /root/vaults/gentech/11-Mess\ Hall/agent-coordination-board.md
```

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `gentech/gentech-coordination-audit` | Audit coordination board hygiene and handoff health |
| `vault/vault-staleness-audit` | Audit vault for stale/outdated content |
| `vault/vault-sweep` | Weekly vault cleanup (deeper than daily rotation) |
| `strategies/strategies` | YoYo's primary domain (DeFi research, LP monitoring) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-03 | Initial skill capture (derived from May 3 rotation session) |
