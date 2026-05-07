---
name: kanban-workflows
description: Manage Kanban workflows — Labs board, agent team conventions, standups, and cross-project tracking.
version: 1.0.0
category: productivity
metadata:
  hermes:
    tags: [kanban, task-management, project-management, workflow, multi-agent]
    capabilities: [terminal]
---

# Kanban Workflows

Manage Kanban workflows for Labs, agent teams, and cross-project tracking. Covers:
- Labs Kanban board (DMOB project tracking)
- Agent team conventions (Obsidian vault workflows)
- Standups and handoffs
- Cross-project tracking and drift detection

---

## 1. Kanban Labs — DMOB Project Board

CLI-first Kanban management for Labs department. Uses `hermes-kanban-sqlite` backed by SQLite.

### Setup

- **DB**: `/root/vaults/gentech/02-Labs/kanban/kanban.db`
- **CLI**: `hermes-kanban-sqlite` (installed via `pip install -e .` from `/root/vaults/gentech/03-Projects/hermes-kanban`)
- **Board**: "Labs" (id=1) — Backlog, To Do, In Progress, Review, Done, Blocked

### Commands

All commands use `--db-path /root/vaults/gentech/02-Labs/kanban/kanban.db`.

#### Add a card
```bash
hermes-kanban-sqlite add "Card title" --db-path "$DB" --column "To Do" --tag tag1 --tag tag2
```

#### List cards
```bash
hermes-kanban-sqlite list --db-path "$DB"
hermes-kanban-sqlite list --db-path "$DB" --column "In Progress"
```

#### Move a card
```bash
hermes-kanban-sqlite move <card_id> "In Progress" --db-path "$DB"
```

#### Card info
```bash
hermes-kanban-sqlite info <card_id> --db-path "$DB"
```

#### Add comment
```bash
hermes-kanban-sqlite comment <card_id> "Comment text" --author DMOB --db-path "$DB"
```

#### Create dependency
```bash
hermes-kanban-sqlite dependency <blocker_id> <blocked_id> --db-path "$DB"
```

#### Archive card
```bash
hermes-kanban-sqlite archive <card_id> --yes --db-path "$DB"
```

#### Sync to Obsidian vault
```bash
hermes-kanban-sqlite sync --db-path "$DB" --vault-dir /root/vaults/gentech/02-Labs/kanban/vault
```

### Workflow

1. **When starting work**: Move card to "In Progress", add comment with plan
2. **When blocked**: Move to "Blocked", add dependency or comment with reason
3. **When done**: Move to "Done", add comment with summary
4. **Daily**: List "In Progress" to see what's active
5. **Weekly**: Sync to vault for Obsidian visual board

### Tags Convention

- `security` — audit, vulnerability research, exploit analysis
- `defi` — DeFi protocol work, LP positions, token analysis
- `solidity` — smart contract development, gas optimization
- `solana` — Solana ecosystem, Colosseum, hackathons
- `backend` — server-side, APIs, databases
- `devops` — infrastructure, CI/CD, deployment
- `hackathon` — competition prep and execution
- `research` — investigation, analysis, documentation

### References
- [Kanban CLI cheatsheet](references/kanban-cli-cheatsheet.md)

---

## 2. Agent Team Workflow

Multi-agent team conventions in a shared Obsidian vault: communication channels, approval workflows, stopping point protocols, and folder organization.

### Communication Channels

| Purpose | Folder | When to Use |
|---------|--------|-------------|
| Active work coordination | `09-Green Room/` | During task execution, handoffs, debates between agents |
| Social / non-work chat | `11-Mess Hall/` | Outside of tasks, general discussion, idle chatter |
| Human approval requests | `00-HQ/Approvals/` | When agents need Jordan/operator sign-off |
| Task status & todo lists | `00-HQ/` or root-level board | Living documents tracking what's next |

### Approval Workflow

When agents need human sign-off on a decision, use a structured approval request.

#### Template Structure

```markdown
# Approval: [Topic]

**Submitted by:** [Agent/Department]
**Date:** YYYY-MM-DD
**Priority:** [Low/Medium/High/Urgent]

## Summary
[1-2 sentence overview]

## Details
[Full context, rationale, data]

## What We Need
- [ ] Approval to proceed with [action]
- [ ] Budget allocation: $[amount]
- [ ] Timeline confirmation: [dates]

## Alternatives Considered
1. [Option A] — pros/cons
2. [Option B] — pros/cons

## Recommendation
[Agent team's recommended course of action]

## Decision
- [ ] Approved
- [ ] Approved with modifications: _______________
- [ ] Rejected — Feedback: _______________
```

#### Flow

1. Agents debate in Green Room
2. Create approval note using template
3. Human reviews and checks boxes
4. Agents proceed based on decision

### Stopping Point Protocol

When an agent hits a stopping point (task complete, blocked, waiting):

1. **First**: Ask Jordan/human what to do next, OR check the to-do list for next task
2. **If no reply in 10-20 minutes**: Self-direct
   - Go back to the vault and audit current work
   - Review code quality
   - Start extended discussions in Mess Hall
   - Look for optimization opportunities
3. **Don't sit idle.** Use downtime productively.

### Vault Organization

#### Time-Based Folders

```
11-Mess Hall/
├── 2026/
│   ├── W17/
│   │   ├── 2026-04-21/
│   │   ├── 2026-04-22/
│   │   └── ...
│   └── W18/
│       └── 2026-04-27/
├── archive/
│   └── 2026-04/
└── task-board.md
```

#### Folder Purpose Mapping

| Folder | Purpose | Contents |
|--------|---------|----------|
| `00-HQ/` | Human-facing commands & approvals | Approval requests, top-level plans |
| `02-Labs/` (or dept folder) | Agent's own work domain | Code, specs, audit reports |
| `09-Green Room/` | Inter-agent work coordination | Debates, handoffs, technical discussions |
| `11-Mess Hall/` | Social & status updates | Daily logs, general chat, status boards |

### References
- [Agent team workflow template](templates/agent-team-workflow-template.md)
- [Vault organization guide](references/vault-organization.md)


## Setup

- **DB**: `/root/vaults/gentech/02-Labs/kanban/kanban.db`
- **CLI**: `hermes-kanban-sqlite` (installed via `pip install -e .` from `/root/vaults/gentech/03-Projects/hermes-kanban`)
- **Board**: "Labs" (id=1) — Backlog, To Do, In Progress, Review, Done, Blocked

## Commands

All commands use `--db-path /root/vaults/gentech/02-Labs/kanban/kanban.db`.

### Add a card
```bash
hermes-kanban-sqlite add "Card title" --db-path "$DB" --column "To Do" --tag tag1 --tag tag2
```

### List cards
```bash
hermes-kanban-sqlite list --db-path "$DB"
hermes-kanban-sqlite list --db-path "$DB" --column "In Progress"
```

### Move a card
```bash
hermes-kanban-sqlite move <card_id> "In Progress" --db-path "$DB"
```

### Card info
```bash
hermes-kanban-sqlite info <card_id> --db-path "$DB"
```

### Add comment
```bash
hermes-kanban-sqlite comment <card_id> "Comment text" --author DMOB --db-path "$DB"
```

### Create dependency
```bash
hermes-kanban-sqlite dependency <blocker_id> <blocked_id> --db-path "$DB"
```

### Archive card
```bash
hermes-kanban-sqlite archive <card_id> --yes --db-path "$DB"
```

### Sync to Obsidian vault
```bash
hermes-kanban-sqlite sync --db-path "$DB" --vault-dir /root/vaults/gentech/02-Labs/kanban/vault
```

## Workflow

1. **When starting work**: Move card to "In Progress", add comment with plan
2. **When blocked**: Move to "Blocked", add dependency or comment with reason
3. **When done**: Move to "Done", add comment with summary
4. **Daily**: List "In Progress" to see what's active
5. **Weekly**: Sync to vault for Obsidian visual board

## Tags Convention

- `security` — audit, vulnerability research, exploit analysis
- `defi` — DeFi protocol work, LP positions, token analysis
- `solidity` — smart contract development, gas optimization
- `solana` — Solana ecosystem, Colosseum, hackathons
- `backend` — server-side, APIs, databases
- `devops` — infrastructure, CI/CD, deployment
- `hackathon` — competition prep and execution
- `research` — investigation, analysis, documentation
