# Green Room — Agent Coordination

## ⚠️ MANDATORY: Check here BEFORE responding to Jordan.

**If the green room has recent activity (last 24h), read it first.** No exceptions.

## Org Chart Integration

The green room is now part of the **Gentech Org Agent Board** system. See:
- **Org Chart:** `01-GenTech HQ/Org Chart.md` — reporting structure, KPIs, accountability
- **Dashboard:** `01-GenTech HQ/Org Agent Board.html` — live visualization

### Enforcement Rules (Unified — 2026-04-20)
1. **Handoff acknowledgment** — receiving agent confirms within 5 min of assignment
2. **Reminder** — 5-15 min no ACK → reminder written in handoff board
3. **Escalation** — 15+ min no ACK → flagged to Jordan
4. **Stalled check** — 24+ h claimed with no progress → flagged for review
5. **Monitor** — Cron `d31c330959de` runs every 15 min, enforces silently
6. **No ghosting** — if assigned a handoff, acknowledge it or explain why you can't

## Green Room vs Mess Hall

**Green Room (this folder)** → *Before* you respond
- Write your perspective here (2-3 lines) before replying to Jordan
- Purpose: prevent overlap, ensure distinct voices
- Think: backstage mirror check — "here's my angle"

**Mess Hall (vault/11-Mess Hall/)** → *Cross-group coordination*
- Broader discussions that span multiple groups
- Handoffs, shared context, things multiple agents need
- Think: cafeteria — different departments sharing info

## Mandatory Response Protocol

1. **Read the green room** — what's already been said?
2. **Check if someone already covered your angle** — if yes, add a different perspective or stay quiet
3. **Write your perspective** (2-3 lines) BEFORE responding
4. **Respond to Jordan** — keep it distinct, not repetitive
5. **Handoff if needed** — if Jordan assigns a task, take it to your home group

## Standing Rules

- **Proactive handoff behavior** → See `proactive-handoff-behavior.md`
- **Handoff board** → `vault/11-Mess Hall/handoff-board.md` (post here when you need another agent)
- **Watchdog system** → See `watchdog-system.md` (agent health monitoring)
- **Sensitive info protocol** → See `sensitive-info-protocol.md` (scrub credentials after use)
- Distinct voices, no overlapping
- Short if not your home group
- Recognize opportunities in your domain, offer briefly
- Take tasks home — don't execute in shared groups
