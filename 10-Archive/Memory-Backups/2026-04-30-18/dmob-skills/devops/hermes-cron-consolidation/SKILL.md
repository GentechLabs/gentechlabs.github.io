---
name: hermes-cron-consolidation
description: "Merge/split Hermes Agent cron jobs: survey, port logic, create unified job, clean up old jobs, sync all vault docs."
version: 1.0.0
author: DMOB
tags: [hermes, cron, consolidation, devops, multi-agent]
---

# Hermes Cron Job Consolidation

Merge two or more Hermes Agent cron jobs into one, porting script logic and keeping all documentation in sync.

## When to Use

- Jordan says "consolidate X into Y" or "merge these cron jobs"
- Two jobs overlap in functionality and should be unified
- Retiring a job and absorbing its rules into another
- Reorganizing cron schedules across agent profiles

## Steps

### 1. Survey Current State

```bash
# List all cron jobs
cronjob(action="list")

# Search vault for docs on both jobs
search_files(path="/root/vaults/gentech", pattern="<job-name-1>|<job-name-2>", target="content")
```

Read the key docs:
- `03-Strategies/LP-Monitor-Rules.md` (or equivalent rules doc)
- `03-Strategies/cron-jobs.md` (job manifest)
- `03-Strategies/current-jobs.json` (machine-readable state)
- Any Green Room handoffs related to the jobs

### 2. Read Both Scripts

Identify what each script does and what logic overlaps vs. is unique:

```bash
read_file(path="<script-a-path>")
read_file(path="<script-b-path>")
```

Create a mental (or actual) diff:
- **Shared logic:** fee efficiency calc, data fetching, alert rules
- **Unique to A:** 2-check confirmation delay, quiet hours
- **Unique to B:** milestone tiers, micro-DCA, AAE signal output

### 3. Patch Target Script

Port missing logic from the retired script into the surviving script:

```bash
patch_file(path="<target-script>", old_string="...", new_string="...")
```

Verify syntax compiles:
```bash
terminal(command="python3 -c \"import py_compile; py_compile.compile('<script>', doraise=True)\"")
```

### 4. Create Consolidated Cron Job

```bash
cronjob(
  action="create",
  name="<Consolidated Name>",
  schedule="<schedule>",
  script="<script-name.py>",
  deliver="telegram:<group-id>",
  prompt="<prompt with all rules>"
)
```

Key decisions:
- **Schedule:** Default to the more frequent job's schedule, or the canonical schedule from the rules doc
- **Script:** Copy to `~/.hermes/scripts/` if not already there
- **Prompt:** Include ALL alert rules from both original jobs

### 5. Remove Old Jobs

```bash
cronjob(action="remove", job_id="<old-job-id>")
```

### 6. Update All Documentation

**Must update all of these (they drift easily):**

1. **Rules doc** (`LP-Monitor-Rules.md` or equivalent):
   - Cron Jobs table → new job ID + schedule
   - Rule 1 (check frequency) → new schedule
   - Consolidation note at bottom

2. **Job manifest** (`cron-jobs.md`):
   - Canonical job entry → new ID, script, schedule
   - Retired/Merged table → add old jobs
   - All Jobs summary table → update schedule
   - Canonical reference at bottom

3. **Machine state** (`current-jobs.json`):
   - Update active jobs with new IDs
   - Add old jobs to `removed` array

4. **Any other files** referencing old job IDs:
   ```bash
   search_files(path="/root/vaults/gentech", pattern="<old-job-id>", target="content")
   ```

### 7. Verify Final State

```bash
cronjob(action="list")
```

Confirm:
- Only the consolidated job exists
- No orphaned jobs
- Schedule matches docs
- Script compiles

## Pitfalls

- **Doc drift is the #1 enemy.** Three files (rules doc, manifest, JSON) can all disagree. Update ALL of them.
- **Old job IDs linger in vault.** Search for them after removal.
- **Script paths differ.** Vault path vs `~/.hermes/scripts/` path — copy the script to the scripts dir for cron execution.
- **Confirmation delays.** When porting alert logic, check if the source script has a 2-check or N-check confirmation pattern. Port it explicitly.
- **Quiet hours.** Both scripts may implement quiet hours differently. Unify to one implementation.

## Example Consolidation

```
Before:
  Job A: LP Range Monitor (every 10 min) — simple range check + fee efficiency
  Job B: DeFi Milestone Tracker (daily) — tiers + compound + micro-DCA

After:
  Job C: DeFi Milestone + LP Monitor (4×/day) — everything combined
  Script: lp-aae-signal-monitor.py (patched to include 2-check confirmation)
```
