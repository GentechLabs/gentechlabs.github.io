# Mess Hall Admin — Session Notes

## Obsidian Sync Quirk

**Date discovered:** 2026-05-03  
**Issue:** Running `ob sync` directly fails (`command not found`) though `obsidian` skill exists.

**Root cause:** The Obsidian CLI binary is not in PATH; instead, Obsidian operations are performed through the Hermes skill system (`note-taking/obsidian`).

**Workaround:** Do not rely on `ob sync` in scripts. Vault writes are immediately persistent in the filesystem. Sync to Obsidian graph is handled by background processes (not blocking).

**Implication for this skill:** Skip explicit sync step; just verify file writes succeed.

---

## Handoff Enforcement Rules (Canonical)

From `handoff-board.md` (as of 2026-05-03):

| Phase | Action | Timeline |
|-------|--------|----------|
| Phase 1 | Sender writes handoff + tags recipient | t=0 |
| Phase 2 | Recipient MUST acknowledge | within 2h |
| Phase 3 | Recipient completes work | — |
| Escalation 1 | Unclaimed after 4h | Gentech nudges |
| Escalation 2 | Unclaimed after 12h | Jordan notified |

**ACK deadline in practice:** For a handoff submitted at 12:45 UTC, ACK is due by 14:45 UTC (2-hour window). Escalation check runs at 16:45 UTC (4h after submission).

---

## Archive Retention Policy

From `daily/README.md`:
- **Keep:** 7 days
- **Auto-purge:** Files older than 7 days deleted during Sunday vault maintenance

**Implementation:** Archive files older than 7 days to `archive/YYYY-MM/` subfolders.

---

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Morning handoff | `YYYY-MM-DD-morning-handoff.md` | `2026-05-03-morning-handoff.md` |
| Sync complete | `YYYY-MM-DD-sync-complete.md` | `2026-05-02-sync-complete.md` |
| Wrap-up | `YYYY-MM-DD-wrapup.md` or `Third-Break-Wrapup-YYYY-MM-DD.md` | `2026-05-02-d5-milestone-consolidation-complete.md` |
| Vault sweep | `vault-sweep-YYYY-MM-DD.md` | `vault-sweep-2026-04-30.md` |

All dates in filenames are UTC calendar date.

---

## Coordination Board Structure

`agent-coordination-board.md` contains:
1. Org structure diagram
2. Department rules
3. Context update block (inserted by this skill)
4. Handoff protocol legend
5. Active handoffs table (H001, H002, ...)
6. Protocol description
7. Agent session check-in table
8. Active sprint table
9. Escalation path
10. Dashboard link

When updating, insert context block **before** the "Handoff Protocol" section to keep it visible at top.

---

## Handoff Board Format

Table columns (markdown):

| From | To | What | Priority | Status | Assigned | Ack Deadline | Notes |
|------|----|------|----------|--------|----------|--------------|-------|

**Status values:**
- `🚀 Pending Ack` — newly submitted, awaiting acknowledgment
- `🟡 Claimed` — acknowledgment received, work in progress
- `✅ Completed` — work delivered
- `⏳ Pending` — in backlog, no deadline pressure
- `🔴 Escalated` — unclaimed past escalation threshold

**Priority indicators:**
- `P0` — critical, sprint-blocking
- `P1` — high, deadline-driven
- `P2` — medium, important but not urgent

---

## Silent Run Policy

This cron job runs without user presence. **Do NOT:**
- Send Telegram messages
- Call notification hooks
- Generate audible alerts
- Write to stdout/stderr unless error

All communication is through file writes to the vault. Users read the files on their own schedule.
