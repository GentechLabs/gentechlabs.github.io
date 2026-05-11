# Agent Coordination Board

## MANDATORY — Read at session start before any other action

This is the Gentech org coordination board. Every agent MUST check this file at the start of each session.

## Org Structure

```
                    [CEO] Jordan — Vision, final decisions, HQ
                              |
                    [COO] Gentech — PM, coordination, enforcement
                   ┌──────────┼──────────┐
            [CTO] Dmob    [CRO] YoYo    [CMO] Desmond
            Labs          Strategies    Entertainment
```

## Department Rules

- **HQ (Jordan, Gentech):** Dispatch, decisions, coordination, ops
- **Labs (Dmob):** Smart contracts, Foundry, security, deployment, hackathons
- **Strategies (YoYo):** Research, DeFi analysis, competitive landscape, market data
- **Entertainment (Desmond):** Content, X posts, Medium, social media, submissions

## Load Balancing Protocol

DMOB is single point of failure for all code work. To prevent overload:
- **Max 2 P1 tasks** assigned to DMOB at any time
- **YoYo picks up** SDK research, API integration, and non-contract code tasks
- **Desmond handles** all submission packaging, README, demo materials
- **Gentech triages** incoming work before assigning — no direct DMOB drops from Jordan
- If DMOB has 3+ active tasks → Gentech redistributes or defers lowest priority

## 📍 Context Update — 2026-05-10

**Last updated:** 2026-05-10 by Gentech (brain audit sync)

### Sprint Status (Week of May 10–13)
- **Dashboard Scoping** — DMOB architecture sketch, target **Tuesday May 13** (P0)
- **Agent Coordination Cleanup** — Tighten handoff enforcement (P0)
- **Bankr Integration** — Passive income play, research + scoping (P1)
- **Kite AI** — PRIMARY focus, deadline **May 17** (P0)
- **Swarms ACM** — Secondary, deadline **May 27** (P1)
- **Bags FM** — Pipeline, deadline **Jun 1** (P2)
- **Solana Frontier** — WITHDRAWN (May 10). Assets preserved for cross-chain reuse.

### Handoff Status
- All prior handoffs resolved or dropped (May 10)
- 0 active handoffs — board clean

### Agent Check-In Required
All agents currently OFFLINE in coordination board. Session start MUST include:
1. Read this file
2. Check `handoff-board.md` for tags
3. Update your row in "Agent Session Check-In" table
4. Acknowledge any pending handoffs within 2h

### Blockers
1. Dashboard scoping (DMOB) → target Tuesday May 13
2. Bankr research (YoYo) → need integration assessment
3. Kite AI submission materials (Desmond) → deadline May 17
4. Kite AI contract adaptation (DMOB) → deadline May 17

---

### Status Legend
- `PENDING` — Handoff written, waiting for recipient to claim
- `CLAIMED` — Recipient acknowledged, actively working
- `COMPLETED` — Work done, delivered to Jordan
- `ESCALATED` — Unclaimed past deadline, Gentech notified Jordan

### Active Handoffs

| ID | From | To | Task | Priority | Status | Notes |
|----|------|----|------|----------|--------|-------|
| — | — | — | No active handoffs | — | — | Board clean as of May 10 |

### Protocol
1. **Sender** writes handoff here + tags recipient in Mess Hall or Green Room
2. **Recipient** MUST update status to CLAIMED within 2 hours of being tagged
3. **Recipient** completes work → updates to COMPLETED + delivers result
4. **Unclaimed >4h** → Gentech nudges recipient
5. **Unclaimed >12h** → Gentech escalates to Jordan

## Agent Session Check-In

Each agent updates their row when they start a session:

| Agent | Last Check-In | Current Task | Status | Notes |
|-------|--------------|--------------|--------|-------|
| Dmob | — | — | OFFLINE | — |
| YoYo | — | — | OFFLINE | — |
| Desmond | — | — | OFFLINE | — |
| Gentech | — | — | OFFLINE | — |

### Active Sprint — Week of May 10–13

|| Task | Owner | Due | Status ||
||------|-------|-----|--------||
|| Dashboard scoping — architecture sketch | Dmob | May 13 | 🟥 **PRIMARY** ||
|| Agent coordination cleanup — handoff enforcement | Gentech | May 13 | 🟥 **PRIMARY** ||
|| Bankr integration research | YoYo | TBD | 🟡 **P1** ||
|| Kite AI Hackathon — contract adaptation + submission | Dmob | May 17 | 🟡 **P1** ||
|| Kite AI submission materials — README, demo | Desmond | May 17 | 🟡 **P1** ||
|| Kite AI — L3 Brain integration research | YoYo | May 17 | 🟡 **P1** ||
|| Swarms ACM Hackathon — scoping + build | Dmob | May 27 | 🟡 **P1** ||
| Solana Frontier | Dmob | May 11 | ❌ **WITHDRAWN** (May 10) |
| Google OAuth setup | Jordan | Apr 20 | ⏳ Pending |

## Escalation Path
1. Agent handles issue in their department
2. If blocked → ping Gentech in HQ
3. If Gentech can't resolve → escalate to Jordan
4. Jordan makes final call

## Dashboard
Live org board: `http://<server-ip>:9119/#/org`
