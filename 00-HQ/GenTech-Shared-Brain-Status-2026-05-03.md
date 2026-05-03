# 🧠 GenTech Shared Brain — GitHub Mirror Status

**Date:** 2026-05-03  
**Status:** ✅ Green (fixed)  
**brains:** 1. Obsidian Vault 2. GitHub Mirror (Gentech-Labs/hermes-brain-backup)

---

## Executive Summary

Gentech's shared brain is a **two-system sync**:
- **Primary:** Obsidian vault at `/root/vaults/gentech/`
- **Backup:** Git mirror on GitHub `Gentech-Labs/hermes-brain-backup`

No `obsidian-headless-sync` needed — existing backup system is the canonical mirror.

---

## Repo Inventory

| Repo | Org | State | Purpose |
|------|-----|-------|---------|
| `Gentech-Labs/hermes-brain-backup` | Gentech-Labs | ✅ Active, syncing | Primary brain backup (full vault + agents + skills) |
| `ProtoJay4789/gentech-vault` | JS personal | ⚠️ Empty/unused | Deprecated — safe to delete |

**Synced content** (as of May 3):
- `vault/` — 26,226 files, full Obsidian vault structure
- `agents/` — SOUL.md + config.yaml for all 4 agents (gentech, desmond, yoyo, dmob)
- `skills/` — 13,910 skill tree entries
- `cron/` — job registry snapshots

---

## Incident: Failed Pushes (May 2–3)

**What broke:**
- Backup script successfully committed locally but failed at `git push`
- Error: `fatal: could not read Username for 'https://github.com': No such device or address`
- Root cause: Git credential store lost/ lacked credentials; HTTPS auth with PAT expired/failed

**Fix applied:**
- Pre-approve credentials via `git credential approve` before push
- Ensured HOME=/root and credentials at `/root/.git-credentials`
- Verified push working May 3 18:48 UTC

**Next run:** Scheduled 6-hourly; next expected ~00:00 UTC May 4

---

## Operational Specs

### Backup Script
**Location:** `/root/hermes-brain-backup/scripts/backup.sh`

**Pipeline:**
1. `rsync` vault → backup dir (excludes .obsidian temp files)
2. Copy agent SOUL/config/memory from `~/.hermes/`
3. Copy custom skills from `~/.hermes/skills/`
4. `git add -A && git commit` (if changes)
5. `git push origin main`

**Schedule:** Every 6 hours via cron (crontab on root)

**Log:** `/root/hermes-brain-backup/backup.log`

**Manual run:**
```bash
/root/hermes-brain-backup/scripts/backup.sh
```

### Restore Procedure
```bash
cd /root/hermes-brain-backup
git pull origin master   # or specific commit
./scripts/restore.sh
```

---

## Verification

```bash
# Check last commit on GitHub
gh api repos/Gentech-Labs/hermes-brain-backup/commits --jq '.[0].commit.committer.date'

# Check local backup health
tail -30 /root/hermes-brain-backup/backup.log

# Test fetch
git -C /root/hermes-brain-backup fetch --dry-run
```

---

## Recommendations

1. **Archive & delete** `ProtoJay4789/gentech-vault` (empty, unused)
2. **Pin backup cron** in Green Room master-todo if not already
3. **Add health check** to daily Mess Hall summary: "Brain last synced: {date}"
4. **Consider SSH deploy key** (currently PAT-based HTTPS)
5. **Document credential recovery** in `00-HQ/` (we just fixed it)

---

## Quick Reference

| Item | Value |
|------|-------|
| Vault source | `/root/vaults/gentech/` |
| Backup dir | `/root/hermes-brain-backup/` |
| GitHub repo | `https://github.com/Gentech-Labs/hermes-brain-backup` |
| Auth | PAT in vault `.env` → git credential store |
| Cron frequency | 6 hours |
| Last success | May 1 06:00 UTC (before auth degraded) |
| Now fixed | May 3 18:48 UTC ✅ |

---

*Created by Desmond, Creative — brain audit & auth repair completed*
