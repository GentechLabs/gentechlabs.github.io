---
name: cron-job-inspection
description: Diagnose and extract Hermes cron job definitions when CLI shows incomplete metadata but the actual job prompt/task is hidden in vault archives or other storage.
triggers:
  - "hermes cron list shows jobs but hermes cron show returns empty or error"
  - "need to understand what a cron job actually does but the body is missing"
  - "auditing cron job configurations across the vault"
  - "debugging non-running jobs where the implementation is unclear"
category: devops
status: stable
version: 0.1.0
last_updated: 2026-05-03
author: YoYo (Strategies)
---

# cron-job-inspection

Diagnose and extract Hermes cron job definitions when `hermes cron` CLI shows incomplete metadata but the actual job prompt/task is hidden in vault archives or other storage.

## When to Use

USE WHEN:
- `hermes cron list` shows jobs but `hermes cron edit/inspect/show` doesn't reveal the full body
- You need to understand WHAT a cron job actually does (its prompt, task, or skill reference)
- Auditing cron job configurations across the vault
- Debugging non-running jobs where the implementation is missing or unclear

DON'T USE WHEN:
- You only need schedule/frequency info (use `hermes cron list` directly)
- The job body is already visible in your active config files

---

## Quick Start

### Step 1 — Confirm the information gap
```bash
# You see job metadata but can't get the body
hermes cron list          # Shows ID, name, schedule, next_run
hermes cron show <id>    # Returns empty or error
```

### Step 2 — Search archived vault memory backups
```bash
# Hermes cron job database gets snapshotted into daily memory backups
# Search the most recent backup window
rg -i "Gentech LLC Reminder" /root/vaults/gentech/10-Archive/Memory-Backups/
```

Typical hit pattern:
```
10-Archive/Memory-Backups/2026-05-03-11/yoyo-skills-2026-05-02-simultaneous-ticker-failure.md:
  ```json
  {
    "jobs": [
      {
        "id": "682e9597b8d6",
        "name": "Gentech LLC Reminder",
        "schedule": {"kind": "cron", "expr": "0 5 15 * *"},
        "last_run": "never"
      }
    ]
  }
  ```
```

### Step 3 — Search for the prompt/task reference in active vault
```bash
# Once you have the job name, find where the actual task/skill is defined
rg -i "Gentech LLC Reminder" /root/vaults/gentech/01-Agency/ /root/vaults/gentech/00-System/
```

### Step 4 — Reconstruct the full job definition
Combine:
- **Metadata** from `hermes cron list` (ID, schedule, deliver)
- **Task body** from vault search (what prompt/skill it runs)
- **Status** from Mess Hall logs (last run result, errors)

---

## Why This Gap Exists

Hermes cron storage architecture (as of 2026-05):
- Job *registry*: SQLite or JSON in `~/.hermes/state/` (not directly human-readable)
- Job *body*: Stored as opaque blobs; CLI lacks `show --verbose` or `export` subcommands
- Vault integration: Cron job definitions get snapshotted into daily memory-backup archives for brain persistence, but aren't queryable from active vault without searching backups
- Result: Investigating a job's purpose requires forensic vault search, not CLI introspection

---

## Pitfalls

### ❌ Pitfall 1 — Assuming `cron list` is complete
`hermes cron list` shows metadata only. The actual prompt/task may reference a file you can't find because it lives in an old backup archive, not the active vault.

**Fix**: Always search `10-Archive/Memory-Backups/` when the job body is missing.

### ❌ Pitfall 2 — Searching only the active vault
The live cron definition may not be mirrored in any current `.md` file. Hermes snapshots the entire registry to memory backups daily.

**Fix**: Search the **most recent 3 backup directories** under `10-Archive/Memory-Backups/` with date order.

### ❌ Pitfall 3 — Missing the job ID→task mapping
You may find the job ID and name in backups, but the task/prompt might be stored separately in a skill file or agent profile.

**Fix**: After identifying the job name, search vault for that exact name to find the implementation file.

### ❌ Pitfall 4 — Old backup, new job mismatch
If a cron job was created after the latest backup, it won't appear in archive search.

**Fix**: Check `~/.hermes/state/` or `~/.hermes/profiles/*/cron.json` directly for newest jobs not yet snapshotted.

---

## Session Template: Cron Job Investigation

**Automated script**: `scripts/investigate-cron-job.sh`

```bash
# One-liner to search backups + vault for a cron job's body
./investigate-cron-job.sh "Gentech LLC Reminder"
```

Manual equivalent:
```bash
# 1. Get job ID and name
hermes cron list | grep -i "<job-name>"

# 2. Try to show body (expect failure)
hermes cron show <job-id> 2>&1 | tee /tmp/cron-show-error.txt

# 3. Search memory backups (most recent first)
backup_dirs=(/root/vaults/gentech/10-Archive/Memory-Backups/*/)
latest_backup=$(ls -dt ${backup_dirs[@]} | head -1)
rg -i "<job-name>" "$latest_backup"

# 4. If found, extract full JSON blob and task reference
# 5. Search vault for the task/skill name
rg -i "<task-name-or-prompt-excerpt>" /root/vaults/gentech/ --type md
```

---

## Knowledge Base: Hermes Cron Storage Patterns

From reverse-engineering observed in 2026-05 sessions:

| Location | Contains | Format |
|----------|----------|--------|
| `~/.hermes/state/cron.json` (if exists) | Full job registry + bodies | JSON |
| `~/.hermes/profiles/<agent>/cron.json` | Agent-scoped jobs | JSON |
| `10-Archive/Memory-Backups/<date>/` | Daily snapshots of entire cron registry | Embedded in markdown notes |
| Active vault `*-cron-*.md` files | Human-curated job lists (often stale) | Markdown tables |
| `03-Strategies/cron-jobs.md` | Canonical reference (may be outdated) | Markdown |

**Discovery rule**: If `hermes cron show` returns empty, the **memory backup** is the single source of truth for job internals.

---

## Related Skills

- `vault-reorganization` — vault structure and folder placement for LLC tracking
- `handoff-reporting` — documenting cron job investigation findings for HQ
- `hermes-agent-health-monitoring` — diagnosing broader Hermes infrastructure issues

---

## Support Files

Place cron job investigation notes in `references/`:
- `references/cron-job-body-recovery.log` — specific extraction transcript
- `references/hermes-cron-storage-map.md` — storage location diagram
