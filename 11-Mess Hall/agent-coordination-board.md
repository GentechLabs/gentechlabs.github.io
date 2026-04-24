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

## Handoff Protocol — ENFORCED

### Status Legend
- `PENDING` — Handoff written, waiting for recipient to claim
- `CLAIMED` — Recipient acknowledged, actively working
- `COMPLETED` — Work done, delivered to Jordan
- `ESCALATED` — Unclaimed past deadline, Gentech notified Jordan

### Active Handoffs

| ID | From | To | Task | Priority | Status | Claimed At | Notes |
|----|------|----|------|----------|--------|------------|-------|
| H001 | Desmond | Dmob | Review dynamic burn rate smart contract feasibility | High | PENDING | — | OVERDUE since Apr 19 |
| H002 | Desmond | YoYo | Competitive analysis — dynamic burn rate in AgentFi | High | PENDING | — | OVERDUE since Apr 19 |

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

## Active Sprint — Week of Apr 20

| Task | Owner | Due | Status |
|------|-------|-----|--------|
| ARC Hackathon — AgentEscrow + x402 nanopayments | Dmob | Apr 25 | In Progress |
| Kite AI Hackathon — L3 Brain demo + test fixes | Dmob | Apr 26 | Pending |
| Colosseum registration | Jordan | Apr 20 | Pending |
| Google OAuth setup | Jordan | Apr 20 | Pending |
| Beams SDK research | YoYo | Apr 20 | Pending |
| ARC submission materials | Desmond | Apr 25 | Pending |
| Kite AI submission materials | Desmond | Apr 26 | Pending |

## Escalation Path
1. Agent handles issue in their department
2. If blocked → ping Gentech in HQ
3. If Gentech can't resolve → escalate to Jordan
4. Jordan makes final call

## Dashboard
Live org board: `http://<server-ip>:9119/#/org`
