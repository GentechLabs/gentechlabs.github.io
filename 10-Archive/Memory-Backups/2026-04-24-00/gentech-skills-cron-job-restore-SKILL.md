---
name: cron-job-restore
description: Restore cron jobs from an Obsidian vault registry after system rebuild or migration.
tags: [cron, telegram, multi-agent, vault]
---

# Cron Job Restore from Vault Registry

Use when rebuilding or migrating a multi-agent system that has cron job definitions stored in an Obsidian vault.

## Prerequisites
- Vault synced and accessible (e.g., `/root/vaults/gentech/`)
- Vault contains cron registry at `12-Skills/cron-registry.md`
- Vault contains routing rules at `12-Skills/cron-routing.md`

## Steps

### 1. Read the registry and routing docs
```bash
cat /root/vaults/gentech/12-Skills/cron-registry.md
cat /root/vaults/gentech/12-Skills/cron-routing.md
```

### 2. Understand the delivery groups
Each cron job routes to a specific Telegram group based on domain:

| Domain | Group ID |
|--------|----------|
| HQ / system / coordination | `telegram:-1003863540828` |
| Strategies / DeFi / LP / markets | `telegram:-1002916759037` |
| Labs / hackathons / bounties | `telegram:-1003872552815` |
| Entertainment / content / social | `telegram:-1003893562036` |
| Personal (Jordan) | `origin` |
| Internal / silent | `local` |

### 3. Recreate jobs with cronjob tool
- Use `cronjob(action='create')` for each job
- **Job IDs will change** on recreation — note the new IDs
- Preserve schedule, delivery target, and prompt content from registry
- Skip paused/disabled jobs unless user specifically wants them

### 4. Update the vault registry
After recreating all jobs, update `cron-registry.md` with:
- New job IDs
- Updated "Last Synced" timestamp
- Change log entry

### 5. Update the cron routing doc
Update `cron-routing.md` audit table with new job IDs and verification dates.

## Related Skills
- **vault-ecosystem-restore** — Full restore including team protocols, vault restructure, and skills inventory. Use that when restoring more than just cron jobs.

## Schedule format
Use standard cron syntax:
- `*/5 * * * *` — every 5 minutes
- `0 6,10,14,18 * * *` — at 6am, 10am, 2pm, 6pm daily
- `30 4 * * 1-6` — 4:30am Mon-Sat
- `0 5 15 * *` — 5am on 15th of each month

## Consolidating Overlapping Jobs

When the user asks to consolidate cron jobs (e.g., two watchlist trackers overlapping):
1. List all jobs with `cronjob(action='list')` — compare against registry
2. Identify duplicates by name/schedule/purpose overlap
3. Remove extras with `cronjob(action='remove', job_id=...)`
4. Update the surviving job with merged content/prompt
5. Update BOTH vault docs: `12-Skills/cron-registry.md` AND `12-Skills/cron-routing.md`
6. Fix any `||` double-pipe markdown table artifacts after patching

## Pitfalls
- Job IDs are NOT preserved across recreation — vault registry MUST be updated
- `deliver: local` means silent (no Telegram delivery)
- `deliver: origin` goes to the user's direct chat
- Some jobs may reference environment variables or tokens that need reconfiguring
- Check for duplicate jobs before creating (`cronjob list`)
