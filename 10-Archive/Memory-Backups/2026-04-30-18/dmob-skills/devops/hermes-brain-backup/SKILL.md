---
name: hermes-brain-backup
description: Set up private GitHub backup of the Hermes agent brain — vault, agent profiles, memory, skills, and cron configs.
---

# Hermes Brain Backup

Backs up the entire agent "brain" to a private GitHub repo as a second brain. Protects against vault corruption, server loss, or accidental deletion.

## What Gets Backed Up
- **Vault** — Obsidian vault (shared brain for all agents)
- **Agent Profiles** — SOUL.md, config.yaml, memory.md per agent
- **Skills** — Custom skills from the skills directory
- **Cron Registry** — Job definitions from vault

## Key Paths
- **Gentech (main agent):** SOUL.md and config.yaml live directly in `~/.hermes/`
- **Sub-agents (YoYo, DMOB, Desmond):** Live in `~/.hermes/profiles/{agent}/`
- **Vault:** `/root/vaults/gentech/`
- **Skills:** `~/.hermes/skills/`

## Setup Steps

1. **Create private repo** via `gh repo create <org>/hermes-brain-backup --private`
2. **Create directory structure:** `vault/`, `agents/{gentech,yoyo,dmob,desmond}/`, `cron/`, `skills/`, `scripts/`
3. **Initialize git** with token-authenticated remote URL
4. **Create .gitignore** — exclude .env, auth.json, *.key, *.pem, cache dirs, audio files
5. **Write backup.sh** — rsync vault, copy agent SOUL.md/config/memory, sync skills, git commit+push
6. **Write restore.sh** — reverse: pull repo, rsync back to vault, copy agent files back
7. **Schedule cron** — every 6 hours run backup.sh
8. **Run initial backup** to populate the repo

## Pitfalls
- **Agent profile paths:** Sub-agents live in `~/.hermes/profiles/{name}/`, NOT `~/.hermes/{name}/`
- **Git auth:** HTTPS push may fail. Two options:
  - Token in remote URL: `https://user:token@github.com/org/repo.git`
  - Credential helper (preferred): `git config credential.helper '!gh auth git-credential'` — uses `gh auth login` token, no hardcoded secrets in remote URL
- **memory.md:** Not all agents have one — DMOB does, others may not. Handle missing files gracefully.
- **Vault .obsidian:** Exclude workspace files (change constantly) but keep plugin configs
- **config.yaml may contain bot tokens:** Consider stripping secrets before committing or adding to .gitignore

## Disaster Recovery
When restoring: pull repo, rsync vault back, copy agent profiles back, restart agents with `hermes gateway restart`.
