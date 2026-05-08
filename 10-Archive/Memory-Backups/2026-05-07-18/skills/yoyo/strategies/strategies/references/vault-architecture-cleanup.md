# Vault Architecture & Duplicate Cleanup

## Canonical Architecture (2026-05-03)

```
Primary:     /root/vaults/gentech/          ← Single source of truth (Obsidian)
Backup:      GitHub mirror (Gentech-Labs/hermes-brain-backup) ← Auto-pushed every 6h
Stale copy:  /root/repos/hermes-brain/vault/  ← REDUNDANT — DELETE
```

## Discovery (May 3 Session)

**Duplicate identified**: `/root/repos/hermes-brain/vault/` contains only `02-Labs/`, `03-Projects/`, `03-Strategies/` — a partial subset that:
- Gets overwritten on Hermes agent updates (it's part of upstream repo)
- Is not synced to GitHub backup
- Causes confusion when agents accidentally read/write here

**Evidence**:
```bash
$ diff -rq /root/repos/hermes-brain/vault /root/vaults/gentech
Only in /root/vaults/gentech: .obsidian, 00-HQ, 01-Agency, 02-AAE, ... (gentech-specific dirs)
Only in /root/repos/hermes-brain/vault: (nothing — it's strictly smaller)
```

## Consolidation Actions

1. **DELETE stale copy**:
   ```bash
   rm -rf /root/repos/hermes-brain/vault/
   ```
   
2. **Audit for stray references**:
   ```bash
   rg "/root/repos/hermes-brain/vault" /root/vaults/gentech ~/.hermes 2>/dev/null
   ```
   Fix any hardcoded paths found.

3. **Lock down canonical path** in all agent configs:
   - `00-System/Brain-SOP.md` — rules out other locations
   - `00-HQ/GenTech-Shared-Brain-Status-2026-05-03.md` — documents the two-system sync

## Rules for All Agents

- **READ/WRITE ONLY**: `/root/vaults/gentech/`
- **BACKUP TRIGGER**: After significant work, run `git -C /root/vaults/gentech push origin main`
- **OBSIDIAN HEADLESS (`ob`)**: Not needed for local vault; only for remote vault sync (different machine)
- **PROFILE STATE**: Hermes profile state lives in `~/.hermes/profiles/<agent>/`, NOT in the hermes-brain repo's `vault/`

## Verification

```bash
# Confirm no cron jobs reference the old path
rg "/root/repos/hermes-brain/vault" ~/.hermes/profiles/*/cron/jobs.json

# Confirm GitHub remote is correct
git -C /root/vaults/gentech remote -v
# Expected: origin git@github.com:Gentech-Labs/hermes-brain-backup.git
```

## Related

- See `00-System/Brain-SOP.md` for the three pillars (atomic notes, structured metadata, knowledge web)
- See `00-System/SOP-Brain-Sync-Workflow.md` for the daily sync procedure
