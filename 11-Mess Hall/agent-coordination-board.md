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

### Status Legend
- `PENDING` — Handoff written, waiting for recipient to claim
- `CLAIMED` — Recipient acknowledged, actively working
- `COMPLETED` — Work done, delivered to Jordan
- `ESCALATED` — Unclaimed past deadline, Gentech notified Jordan

### Active Handoffs

| ID | From | To | Task | Priority | Status | Claimed At | Notes |
|----|------|----|------|----------|--------|------------|-------|
|| H001 | Desmond | Dmob | Review dynamic burn rate smart contract feasibility | High | ⏳ PENDING | — | ✅ APPROVED (Jordan voice 2026-05-02) — DMOB go ahead |
|| H002 | Desmond | YoYo | Competitive analysis — dynamic burn rate in AgentFi | High | ✅ COMPLETED | — | ✅ COMPLETED — deliverable in `03-Strategies/TECH-token-dynamic-burn-research.md` |
|| H003 | Jordan | Dmob | Gas Reserve Auto-Rebalance — SC feasibility review | High | ⏳ PENDING | — | ✅ APPROVED (Jordan voice 2026-05-02) — DMOB proceed |
|| H004 | Jordan | YoYo | Gas Reserve Auto-Rebalance — monitoring trigger & strategy | High | ⏳ PENDING | — | Pending YoYo review — depends on DMOB SC approval |

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

## Active Sprint — Week of Apr 21–27

| Task | Owner | Due | Status |
|------|-------|-----|--------|
| ARC Hackathon — AgentEscrow + x402 nanopayments | Dmob | Apr 25 | ❌ **WITHDRAWN** Apr 22 |
| Solana Frontier — Identify tracks, build, execute | Dmob | May 11 | 🟥 **ACTIVE** |
| Kite AI Hackathon — L3 Brain demo + test fixes | Dmob | May 11 | 🟡 Back-burner / stopping-point |
| Colosseum registration | Jordan | Apr 20 | ✅ Done (Apr 21) |
| Google OAuth setup | Jordan | Apr 20 | ⏳ **OVERDUE** |
| Beams SDK research | YoYo | Apr 20 | ⏳ Dmob picking up |
| ETHGlobal sign-up + 0G tokens + KeeperHub key | Jordan | Apr 24 | ⏳ **OVERDUE** |
| Kite AI submission materials | Desmond | May 11 | ⏳ Pending |
| Gas Reserve Auto-Rebalance (SC + strategy) | Dmob / YoYo | Apr 21 | ⏳ **OVERDUE** |

## Escalation Path
1. Agent handles issue in their department
2. If blocked → ping Gentech in HQ
3. If Gentech can't resolve → escalate to Jordan
4. Jordan makes final call

## Dashboard
Live org board: `http://<server-ip>:9119/#/org`
