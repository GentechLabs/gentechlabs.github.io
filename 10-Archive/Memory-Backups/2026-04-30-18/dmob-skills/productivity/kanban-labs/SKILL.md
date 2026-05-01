---
name: kanban-labs
description: Manage Labs Kanban board via hermes-kanban-sqlite CLI. Create cards, move between columns, run standups, track progress. Primary interface for DMOB project tracking.
version: 1.0.0
category: productivity
metadata:
  hermes:
    tags: [kanban, task-management, project-management, labs]
    capabilities: [terminal]
---

# Kanban Labs — DMOB Project Board

CLI-first Kanban management for Labs department. Uses `hermes-kanban-sqlite` backed by SQLite.

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
