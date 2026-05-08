# Gentech Brain Backup Architecture — Session 2026-05-03

## Architecture

```
/root/vaults/gentech/              ← Primary working vault (Obsidian)
    ↓ every 6h via backup.sh (rsync)
/root/hermes-brain-backup/         ← Local sync mirror
    ├─ vault/         ← rsync'd copy of Obsidian (excludes large dirs)
    ├─ agents/        ← SOUL.md + config.yaml + memories per agent
    ├─ skills/        ← custom skill bundles
    └─ cron/          ← job registry JSON
    ↓ SSH push (Node.js v22 credential helper)
GitHub: git@github.com:Gentech-Labs/hermes-brain-backup.git
```

**Key properties:**
- Single source of truth: `/root/vaults/gentech/`
- Backup is a *mirror*, not a working copy — all edits happen in the primary vault
- Push uses SSH (no HTTPS credential expiry issues)
- Daily health check logs to `/root/hermes-brain-backup/backup.log`

## What We Cleaned (May 2–3, 2026)

| Item | Status | Action |
|------|--------|--------|
| `ProtoJay4789/gentech-vault` remote | ⚠️ Stale mirror, never updated | `rm -rf /root/gentech/gentech-vault` |
| `/root/vault` (partial copy) | ⚠️ Legacy path, referenced in old SOULs | Update SOULs → `/root/vaults/gentech` |
| Lock files (`*.lock`) | 🔴 Accumulated 50K+ | Purged via vault sweep |
| Archive bloat | 🔴 10-Archive/ grew to 10GB | Consolidated to latest timestamp snapshots only |
| OAuth tokens (Nous) | 🔴 Simultaneously expired | Refresh script added; manual re-auth still needed |

## Decision: No Headless Sync

The vault already has a reliable git-based backup chain. Adding `obsidian-headless-sync` would create a third sync layer with no additional reliability. Stick with:

1. **Write** via `vault-atomic-operations/vault_writer.py` (file-locked)
2. **Mirror** via `backup.sh` rsync → `/root/hermes-brain-backup/vault/`
3. **Push** via SSH to GitHub

## Verification Commands

```bash
# Check backup health
tail -20 /root/hermes-brain-backup/backup.log

# Verify vault size < 200MB (active notes only)
du -sh /root/vaults/gentech

# Ensure excluded dirs not present
find /root/vaults/gentech -maxdepth 2 -type d -name "10-Archive" -o -name "Memory-Backups"

# Confirm remote connectivity (GitHub)
git -C /root/hermes-brain-backup remote -v
```

## Cleanup Script Reference

See `vault-atomic-operations/scripts/detect_stale_vault_clones.sh` for automated detection of duplicate/obsolete vault clones across the system.
