---
name: brain-backup
description: Back up agent memory, skills, and vault structure to a private GitHub repo for disaster recovery.
category: devops
tags: [backup, github, memory, git, cron, disaster-recovery]
---

# Brain Backup

Version-controlled backup of agent memory, skills, and vault to a private GitHub repo. Acts as a "second brain" — if the server dies, git history is the recovery point.

## When to Use

- Setting up a new agent or recovering from server loss
- After significant memory updates (new API keys, config changes, user profile changes)
- Periodically via cron for hands-free backups
- Whenever "Update the Brain" is requested by the user (Integrates Vault updates with GitHub persistence)

## Prerequisites

- GitHub CLI (`gh`) authenticated with repo access
- Private repo in org (e.g. `Gentech-Labs/hermes-brain-backup`)
- Agent profile directory exists at `~/.hermes/profiles/<agent>/`

## Steps

### 1. Clone or Initialize the Repo

```bash
gh repo clone Gentech-Labs/hermes-brain-backup ~/hermes-brain-backup
# Verify actual path — ~ may expand to agent profile home, not /root/
cd ~/hermes-brain-backup && pwd
```

### 2. Directory Structure

```
hermes-brain-backup/
├── agents/<name>/
│   ├── memory.md        # Memory snapshot (user profile, config, tokens ref)
│   ├── SOUL.md          # Agent soul/personality
│   └── config.yaml      # Agent config
├── vault/               # Vault skeleton (no media files)
├── skills/
│   └── INDEX.md         # Skills index with restore instructions
├── cron/                # Cron job configs
├── scripts/
│   └── backup-brain.py  # Automation script
└── README.md
```

### 3. Create Memory Snapshot

Export the agent's memory blocks to `agents/<name>/memory.md`. Include:
- User profile (GitHub, preferences, setup details)
- Server environment (OS, tool paths, installed binaries)
- API keys (reference only — NEVER include actual keys)
- Telegram bot tokens (reference only — mask values)
- Vault location and sync method

### 4. Create Backup Script

`scripts/backup-brain.py` should:
- Update timestamp in memory.md
- Regenerate skills index
- Run `git add -A && git commit && git push`
- Log actions to `backup.log`

### 5. Configure .gitignore

**ALWAYS exclude:**
- `.env`, `*.key`, `*.pem`, `auth.json`
- Media files (`*.mp3`, `*.mp4`, `*.wav`, `*.ogg`)
- Cache dirs (`.cache/`, `__pycache__/`, `node_modules/`)
- Large binary files

**Do NOT use negation patterns** (`!vault/**`, `!skills/**`) — they break in unexpected ways. Instead, simply don't add ignore rules for directories you want tracked. If you must use negation, use the catch-all-then-unignore pattern:
```
*
!vault/
!agents/
!skills/
!cron/
!scripts/
```

### 6. Set Up Cron Job

```bash
# Daily backup at 6 AM UTC
cronjob action=create
  name: brain-backup
  schedule: "0 6 * * *"
  prompt: "Run backup script at ~/hermes-brain-backup/scripts/backup-brain.py. Report what was backed up."
```

## Security Rules

- **NEVER** commit actual API keys, tokens, or passwords
- Reference them by name only (e.g. "CoinMarketCap key provided Apr 20 2026")
- Keep the repo PRIVATE
- Use `.gitignore` to enforce exclusions

## Restore Procedure

1. Clone the repo
2. Read `agents/<name>/memory.md` for agent context
3. Use `skill_view()` to inspect skills from index
4. Recreate cron jobs from `cron/` configs
5. Re-apply API keys from the user (they're not stored)

## Memory Consolidation (when near limit)

When memory is at 90%+ capacity (2200 char limit):
1. Merge related entries (user profile + server config → one entry)
2. Remove redundant entries (e.g., duplicate "server is Linux" lines)
3. Compress to declarative facts only — no instructions or procedures
4. Check: `memory(action='read')` shows usage percentage
5. Use `replace` to merge, then `remove` to delete duplicates
6. Add new entry only after freeing space

## Cron Job Management

- **Always check for duplicates first**: `cronjob(action='list')` before creating
- If two agents need the same backup, one cron job with multi-target delivery is better than duplicates
- Remove stale jobs: `cronjob(action='remove', job_id=<id>)`

## Pitfalls

- **Nested `.git` directories in vault**: If the vault contains Foundry/Hardhat projects (e.g. `tech-payment-router/`), their `lib/` directories (forge-std, openzeppelin-contracts) may have their own `.git` dirs. When rsync copies these to `vault/`, `git add -A` fails with `does not have a commit checked out`. Fix: run `find /root/hermes-brain-backup/vault -name '.git' -type d -exec rm -rf {} +` before `git add -A`. Consider adding `--exclude='lib/'` to rsync if you don't need dependency source code in backups.
- Memory tool data isn't stored as filesystem files — you must snapshot it manually or via script
- Skills live in the Hermes system, not as files — the index is a reference, not a restorable backup
- Vault media (images, audio) should be excluded to keep the repo small
- **Telegram delivery in cron**: When running as a cron job, `TELEGRAM_BOT_TOKEN_*` env vars are not accessible from Python sandbox (`execute_code`). For cron jobs configured with `deliver`, the final response is auto-delivered — just put the report as your last output. Don't try to send manually via curl/urllib.
- Always verify `.gitignore` before first commit — a leaked API key in git history is a security incident
- **Tilde expansion mismatch**: In the Hermes sandbox, `~` expands to the agent's profile home (`/root/.hermes/profiles/<agent>/home/`), NOT `/root/`. So `gh repo clone ... ~/hermes-brain-backup` clones to `/root/.hermes/profiles/dmob/home/hermes-brain-backup/`. But `write_file` tool writes relative to `/root/`. If using `write_file` to create files, copy them to the correct clone path with `cp` before committing. Verify with `cd ~/hermes-brain-backup && pwd` after cloning.
- **`.gitignore` negation patterns are broken**: Do NOT use `!vault/**`, `!skills/**` etc. to "include" directories — negation patterns only override *previous explicit ignore rules*, they don't force-include. Without a catch-all `*` ignore, negation patterns actually cause git to ignore those files. Solution: simply don't add patterns that exclude your backup directories. If you need to use negation, add a catch-all `*` first: `*` then `!vault/`, `!agents/`, etc.
