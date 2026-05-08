# Escalation Protocol — Handoff Enforcement & Agent Coordination

## Handoff Enforcement Rules
**Source:** `11-Mess Hall/handoff-board.md` header (canonical)

```
## Enforcement Rules (Unified — 2026-04-20)
- ACK deadline: 5 min from assignment
- Escalation: 15+ min no ACK → flagged to Jordan
- Stalled check: 24+ h claimed with no progress → flagged for review
- Monitor: Cron job d31c330959de runs every 15 min, checks board, enforces silently
- Board updates: Specialist must update status on delivery
```

## Timeline Visualization
```
t=0      Handoff written, tagged
         ↓
t+0-5m   🚀 Pending Ack (recipient MUST claim)
         ↓
t+5m     Still unclaimed? → Gentech private nudge
         ↓
t+15m    Still unclaimed? → 🔴 ESCALATED to Jordan
         ↓
t+24h    Claimed but no progress update? → Flagged for review
```

## Status Transition Diagram
```
[Sent] --(recipient reads)--> 🚀 Pending Ack
  ↓  (timeout 5min)
[ESCALATE] --(Gentech nudge)--> 🔴 ESCALATED
  ↓  (Jordan assigns)
[Reassigned] --(new recipient)--> 🚀 Pending Ack

🚀 Pending Ack --(recipient clicks claim)--> 🟡 Claimed
  ↓  (work in progress)
  ↓  (progress update required every 8h ideally)
[Stalled] --(24h no update)--> ⚠️ Review Flag
  ↓
✅ Completed --(deliverable ready)--> ✅ Completed
```

## Severity Levels
- **P0:** Business-critical; blocking multiple workstreams; requires immediate (within 1h) response
  - Examples: OAuth incident, Solana Frontier deadline at risk, D5 consolidation blocker
- **P1:** High priority; due within 24h; escalate if blocked
  - Examples: Kite AI scoping, milestone ladder reconcile, state file fix
- **P2:** Normal priority; scheduled work; no immediate escalation
  - Examples: AAE Signal Spec optimization, background research

## Agent Check-In Protocol
**Source:** `11-Mess Hall/agent-coordination-board.md`

Every agent **MUST** at session start:
1. Read `11-Mess Hall/agent-coordination-board.md`
2. Check `handoff-board.md` for tags
3. Update your row in "Agent Session Check-In" table
4. Acknowledge any pending handoffs within 2h

**Failure to check-in:** Marked OFFLINE; coordination visibility lost; HQ may assume agent down.

## Escalation Contact Matrix
| Escalation Level | Notify | Action |
|-----------------|--------|--------|
| 5min no ACK | Gentech (COO) | Private nudge to recipient |
| 15min no ACK | Jordan (CEO) | Escalation message in HQ |
| 24h stalled | Jordan + Gentech | Review + reassignment decision |
| P0 incident | Jordan + All agents | Immediate broadcast (all-hands) |

## Incident Severity Definitions
- **🔴 P0 INCIDENT (ACTIVE)** — Production systems down; data pipelines blocked; revenue-impacting; requires immediate human intervention
  - Example: OAuth token revoked blocking all data collection
  - Response: All agents drop, owner prioritizes fix, status updates every 30min
- **🟡 P1 BLOCKER** — Workstream blocked; cannot proceed without external resolution; due within 24h
  - Example: Placeholder address in production script
- **🟢 P2 PROCESS** — Awaiting approval, queue items, no deadline pressure

## Communication Channels by Urgency
| Urgency | Channel | Format |
|---------|---------|--------|
| P0 incident | HQ group + all-agent ping | `/all STATUS: OAuth incident — DMOB assigned` |
| P1 blocker | HQ group + tagged owner | `@DMOB H2026-05-02-01 needs claim` |
| P2 pending | Handoff board only | Board status update sufficient |
| Jordan escalation | HQ group + direct message | Clear subject, action required, deadline |

## Common Failure Modes
- **Weekend blackout:** Agents OFFLINE Saturday-Sunday; handoffs accumulate; Monday morning flood
- **Time zone confusion:** All deadlines UTC; convert local to UTC before claiming
- **Silent failure:** Cron job `d31c330959de` enforces but doesn't notify; agents must self-check board
- **Single point of failure:** DMOB bandwidth crisis (4 P0/P1 tracks) → all critical paths at risk
- **OAuth dependency:** External provider downtime → entire data layer offline; fallback providers mandatory

## Post-Incident Checklist
After resolving a P0 incident:
- [ ] Update `Infrastructure-Issues.md` with resolution timestamp
- [ ] Add post-mortem root cause section
- [ ] Verify fallback providers in `config.yaml` to prevent recurrence
- [ ] Update daily log with incident summary
- [ ] Notify Jordan of closure

## References
- Handoff board table format: `references/handoff-board-conventions.md`
- Vault structure: `references/vault-locations.md`
- Daily log schema: `references/daily-log-structure.md`
