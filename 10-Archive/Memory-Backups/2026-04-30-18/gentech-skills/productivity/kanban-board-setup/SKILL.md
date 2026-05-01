---
name: kanban-board-setup
description: Set up and manage Kanban boards for projects using hermes-kanban-sqlite CLI. Create boards, add cards, sync to Obsidian vault.
version: 1.0.0
category: productivity
metadata:
  hermes:
    tags: [kanban, project-management, obsidian]
---

# Kanban Board Setup

## When to Use
- Starting a new project that needs task tracking
- Breaking down a goal into trackable cards
- Syncing project state to Obsidian vault for visual boards

## Prerequisites
- `hermes-kanban-sqlite` CLI installed globally
- Obsidian vault at `/root/vaults/gentech/`

## Setup Steps

### 1. Initialize a board
```bash
hermes-kanban-sqlite init <project-name> --db-path /root/vaults/gentech/03-Projects/<folder>/<project-name>-kanban.db
```

### 2. Add cards
```bash
hermes-kanban-sqlite add "Card title" \
  --board <project-name> \
  --column "Backlog" \
  --tag "tag1,tag2" \
  --due "2026-05-15" \
  --db-path <db-path>
```

Columns: Backlog, To Do, In Progress, Review, Done, Blocked

### 3. Move cards
```bash
hermes-kanban-sqlite move <card_id> "<target_column>" --db-path <db-path>
```

### 4. List board
```bash
hermes-kanban-sqlite list --board <project-name> --db-path <db-path>
```

### 5. Sync to Obsidian vault
```bash
hermes-kanban-sqlite sync \
  --db-path <db-path> \
  --vault-dir /root/vaults/gentech/Kanban \
  --force
```

This creates a `Kanban/<project-name>.md` file compatible with obsidian-kanban plugin.

### 6. Dry run sync (preview changes)
```bash
hermes-kanban-sqlite sync --db-path <db-path> --vault-dir /root/vaults/gentech/Kanban --dry-run
```

## Kanban Orchestrator Skill
For AI-driven board management (standups, auto-move, queries), the `kanban-orchestrator.md` skill is installed at `~/.hermes/skills/productivity/kanban-orchestrator.md`.

It supports:
- REST API calls to Obsidian plugin (port 27124) when Obsidian is running
- Markdown fallback when plugin is offline (read/write files directly)

## Board File Format
Synced boards are stored as Obsidian Kanban markdown with `kanban-plugin: board` frontmatter. Compatible with the `obsidian-kanban` community plugin for visual rendering.

## Pitfalls
- DB path must be consistent across all commands for the same project
- `--force` flag on sync overwrites conflicts automatically
- The Obsidian plugin REST API requires Obsidian desktop running — CLI works headless
- `demo` command has a known bug (unbound variable) — skip it
