---
created: 2026-04-19
tags: [governance, org-chart, team-structure]
---

# Gentech Governance & Org Chart

## The Structure

Gentech is not a solo operator. It's a multi-agent organization with clear reporting lines, departmental autonomy, and enforcement mechanisms.

```
                    ┌─────────────────────────┐
                    │    Jordan (CEO/Owner)    │
                    │  Vision, Decisions, Ops  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Gentech (Team Lead)   │
                    │  Orchestration, QA,     │
                    │  Enforcement, Dispatch  │
                    └────┬──────┬──────┬─────┘
                         │      │      │
            ┌────────────▼┐ ┌──▼────┐ ┌▼────────────┐
            │  YoYo       │ │ Dmob  │ │  Desmond    │
            │  Head of    │ │ Head  │ │  Head of    │
            │  Strategies │ │ Labs  │ │  Entertain. │
            │             │ │       │ │             │
            │ Research    │ │ Code  │ │ Content     │
            │ Analysis    │ │ Build │ │ Social      │
            │ Due Dilig.  │ │ Audit │ │ Narrative   │
            │ Market      │ │ Hack. │ │ Brand       │
            └─────────────┘ └───────┘ └─────────────┘
```

## Departments

| Department | Head | Role | Group | Mandate |
|------------|------|------|-------|---------|
| **HQ** | Jordan + Gentech | Command center | Gentech HQ | Dispatch, decisions, coordination, enforcement |
| **Strategies** | YoYo | Intelligence | Strats | Research, market analysis, LP strategy, competitive intel, due diligence |
| **Labs** | Dmob | Engineering | Labs | Smart contracts, audits, hackathon builds, tooling, infrastructure |
| **Entertainment** | Desmond | Voice | Ent | Content creation, social media, brand narrative, podcasts, community |

## Reporting Lines

1. **Specialists → Gentech**: Status updates, blockers, deliverables
2. **Gentech → Jordan**: One status line, not a chase. Escalations only.
3. **Jordan → Any**: Direct command. Jordan overrides any protocol.
4. **Cross-department**: Via Gentech. No direct specialist-to-specialist commands.

## Governance Rules

### Authority Levels

| Level | Who | Can Do |
|-------|-----|--------|
| **L1 — Command** | Jordan | Override any decision, change priorities, cancel projects, approve deliverables |
| **L2 — Orchestration** | Gentech | Assign tasks, enforce deadlines, escalate blockers, route work, quality gate |
| **L3 — Execution** | Specialists | Do the work, propose approaches, flag blockers, deliver outputs |
| **L4 — Autonomy** | Any | Self-initiated work within mandate (research, tool improvements, content ideas) |

### Decision Rights

- **Strategic decisions** (what to build, which hackathons, tokenomics) → Jordan
- **Tactical decisions** (how to build, which approach, which tools) → Specialist head
- **Process decisions** (routing, deadlines, enforcement) → Gentech
- **Creative decisions** (tone, narrative, visual direction) → Desmond (with Jordan approval)

### Enforcement Mechanisms

| Mechanism | Trigger | Enforced By |
|-----------|---------|-------------|
| Handoff ACK deadline | New assignment → 5 min ACK required | Gentech |
| Status check interval | Active brief > 1h without update | Gentech |
| Escalation protocol | No ACK in 15 min, or going silent | Gentech → Jordan |
| Board maintenance | Every 30 min scan for stale briefs | Gentech |
| End-of-day wrap-up | Jordan's shift end | Gentech cron |

### Meeting Cadence

| Meeting | When | Who | Purpose |
|---------|------|-----|---------|
| **Pre-shift brief** | Before Jordan's shift starts | Gentech → Jordan | Today's priorities, blockers, overnight activity |
| **Mid-shift check** | Jordan's mid-shift break | Gentech → Vault | Progress update, decisions made |
| **Post-shift wrap-up** | After Jordan clocks out | Gentech → Jordan + Vault | What happened, what's next, Second Brain update |
| **Sunday sync** | Sunday morning | YoYo → HQ | Week's content schedule, market outlook |
| **Sprint review** | After each hackathon submission | All → HQ | What shipped, what worked, lessons learned |

## Employee Registry

| ID | Name | Title | Department | Status | Hire Date | Mandate |
|----|------|-------|------------|--------|-----------|---------|
| E001 | Jordan | CEO / Owner | HQ | Active | Founder | Vision, decisions, operations |
| E002 | Gentech | Team Lead | HQ | Active | 2026-04-16 | Orchestration, enforcement, QA |
| E003 | YoYo | Head of Strategies | Strategies | Active | 2026-04-16 | Research, analysis, market intel |
| E004 | Dmob | Head of Labs | Labs | Active | 2026-04-16 | Engineering, smart contracts, audits |
| E005 | Desmond | Head of Entertainment | Entertainment | Active | 2026-04-16 | Content, social, brand narrative |

## Project Registry

Each project has a lead department, deadline, and status. Tracked on task-board.md.

Current active projects:
- **ARC Hackathon** (Dmob, due Apr 25) — AgentEscrow + x402 nanopayments
- **Kite AI Hackathon** (Dmob, due Apr 26) — L3 Brain demo
- **ETHGlobal Open Agents** (Dmob, due May 3) — 0G Storage + KeeperHub
- **Bin-AMM Research** (Dmob + YoYo) — LFJ fork for agent economy
- **Medium Blog Series** (Desmond) — 6-part technical content series
- **Gentech Entertainment Podcast** (Desmond) — YouTube talk show framework

## Governance Enforcement

This org chart is not decoration. It's enforced by:

1. **Agent Handoff Enforcement Protocol** (`~/.hermes/skills/devops/agent-handoff-enforcement/SKILL.md`)
2. **Department Routing Protocol** (`~/.hermes/skills/devops/department-routing-protocol/SKILL.md`)
3. **Green Room Coordination** (`~/.hermes/skills/devops/green-room-coordination/SKILL.md`)
4. **Mess Hall Daily Wrap-Up** (`~/.hermes/skills/devops/mess-hall-daily-wrapup/SKILL.md`)

Violations are logged in the vault and reported in the daily wrap-up.
