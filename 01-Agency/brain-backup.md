# 🧠 Brain Backup System

Private GitHub repo backing up the entire Hermes agent brain.

## Repo
https://github.com/Gentech-Labs/hermes-brain-backup (private)

## What's Backed Up
- 📚 Obsidian vault (160+ files)
- 🤖 Agent SOUL.md, config.yaml, memory.md (all 4 agents)
- 🛠️ Custom skills
- ⏰ Cron job registry

## Schedule
Auto-syncs every 6 hours via cron job.

## Manual Backup
```bash
cd /root/hermes-brain-backup
./scripts/backup.sh
```

## Disaster Recovery
```bash
cd /root/hermes-brain-backup
git pull origin master
./scripts/restore.sh
```

## Key Paths
- Backup dir: `/root/hermes-brain-backup/`
- Vault: `/root/vaults/gentech/`
- Agent profiles: `~/.hermes/profiles/{agent}/`

Created: 2026-04-20
