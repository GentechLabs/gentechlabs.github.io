---
name: vault-reorganization
category: note-taking
description: Reorganize the Obsidian vault at /root/vaults/gentech - merge duplicates, create clean numbered structure
---

# Vault Reorganization Workflow

## When to Use
When the Obsidian vault at `/root/vaults/gentech` needs restructuring due to duplicates, unclear naming, or organizational drift.

## Current Status (2026-05-07)
Major consolidation completed:
- `03-Projects` fully merged into `02-Labs` (all 11 subdirs moved, directory removed)
- DeFi Milestone docs renamed from "D5" to "DeFi Milestone" (scripts kept as-is for cron compatibility)
- Portfolio synced: vault canonical source → GitHub Pages deployed

## Current Structure (as of 2026-05-07)
```
vault/
├── 00-HQ/                       ← Jordan's command center, approvals, config
├── 00-Inbox/                    ← Drop zone
├── 00-System/                   ← Agent voice assignments, system config
├── 01-Agents/                   ← Agent profiles and config
├── 02-Labs/                     ← ALL projects consolidated here (was 03-Projects)
│   ├── AAE/
│   ├── BirdeyeBIP/
│   ├── DeFi/
│   ├── Hackathons/
│   ├── jordan-portfolio/
│   ├── tech-payment-router/
│   └── ... (11 subdirs total)
├── 03-Strategies/               ← DeFi monitoring, LP scripts, market analysis
│   ├── Defi-Monitor/
│   └── scripts/
├── 04-Entertainment/            ← Content, social media
├── 06-Content/                  ← Architecture docs, content drafts
├── 08-Daily/                    ← Daily logs
├── 09-Green Room/               ← Active handoffs, work threads
├── 10-Archive/                  ← Historical, memory backups
├── 11-Mess Hall/                ← Team banter, status updates
└── 12-Skills/                   ← Skill tracker
```

**Key change**: `03-Projects` no longer exists. All project work lives in `02-Labs/`.

## Vault Philosophy
- The vault is the "shared brain" for all agents (Hermes and others)
- Use before/during/after tasks to maintain context across sessions
- Agents should think creatively with it — like a ping pong table
- Helps agents maintain context since LLMs have memory limits
- Hermes already creates skills based on what it does

## Execution Steps
1. `cd /root/vaults/gentech`
2. Create new folder structure with `mkdir -p`
3. Move files from old to new locations
4. Merge all 3 Green Room folders into `09-Collab/green-room/`
5. Merge `08-Activity log/` into `01-Brain/daily/`
6. Remove empty old directories
7. Run `npx obsidian-headless sync` after completion

## Key Conventions
- Vault synced via Obsidian Sync (user has paid subscription)
- Use `npx obsidian-headless sync` to push changes
- All agents access via the vault path, not directly
