---
name: vault-reorganization
category: note-taking
description: Reorganize the Obsidian vault at /root/vaults/gentech - merge duplicates, create clean numbered structure
---

# Vault Reorganization Workflow

## When to Use
When the Obsidian vault at `/root/vaults/gentech` needs restructuring due to duplicates, unclear naming, or organizational drift.

## Current Status (2026-04-21)
User approved reorganization. 446 files, major issues found:
- 3 duplicate "Green Room" folders (`09-Green Room/`, `13-Green Room/`, `green-room/`)
- 2 duplicate "08" folders (`08-Activity log/`, `08-Daily/`)
- 2 each of `01-Agency/` vs `01-GenTech HQ/`, `02-AAE/` vs `02-Labs/`, `04-Entertainment/` vs `04-Projects/`, `05-Learning/` vs `05-Reviews/`

## Target Structure
```
vault/
├── 00-Inbox/                    ← Drop zone
├── 01-Brain/                    ← Agent memory & daily ops
│   ├── agent-states/            ← Current agent states
│   ├── daily/                   ← Daily logs, morning checklists (merge 08-Activity log here)
│   ├── weekly/                  ← Weekly rollups
│   └── cron-changes/            ← Cron job change logs
├── 02-Projects/                 ← Active work
│   ├── AAE/
│   ├── Kite/
│   ├── AgentFi/
│   └── genlayer-recon/
├── 03-Strategy/                 ← Planning, tokenomics, vision
├── 04-Research/                 ← Recon, security, SDK comparisons
│   ├── security/
│   ├── bug-bounties/
│   └── sdk-comparisons/
├── 05-Content/                  ← Posts, scripts, YouTube
│   ├── drafts/
│   ├── scripts/
│   └── youtube/
├── 06-Learning/                 ← Courses, updraft, avalanche
├── 07-Wiki/                     ← Concepts, entities, references
├── 08-Templates/                ← Note templates
├── 09-Collab/                   ← Agent communication
│   ├── handoffs/
│   ├── chats/
│   ├── approvals/
│   └── green-room/              ← Merge all 3 Green Room folders here
├── 10-Archive/                  ← Old/completed stuff
├── assets/                      ← Branding, voices
└── skills/                      ← Agent skills & protocols
```

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
