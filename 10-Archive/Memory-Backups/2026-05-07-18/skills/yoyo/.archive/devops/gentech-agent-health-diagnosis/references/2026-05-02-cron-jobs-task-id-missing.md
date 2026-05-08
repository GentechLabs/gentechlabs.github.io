# Cron jobs.json `task_id` Field Missing — Structural Corruption Pattern

**Detected:** 2026-05-02  
**Agents affected:** yoyo, gentech, dmob, desmond (all profiles)  
**Severity:** Medium — execution continues but kanban linkage broken

---

## What We Found

All four Hermes agent profiles have cron job definitions where **every single job entry lacks the `task_id` field entirely**.

```json
{
  "jobs": [
    {
      "id": "3044d70c58bc",
      "name": "DMOB Brain Backup",
      "schedule": "0 */6 * * *",
      "prompt": "Backup DMOB brain..."
      // ← NO task_id field present
    }
  ]
}
```

Inspection method:
```bash
grep -r 'task_id' /root/.hermes/profiles/*/cron/jobs.json
# Returns 0 matches across all agents
```

`hermes cron list` shows jobs with `task_id: MISSING` placeholder in the table output. Direct JSON inspection confirms the key is absent, not just null.

---

## Impact

- **Job execution:** Still works — scheduler only requires `id`, `schedule`, `prompt`, `deliver`
- **Kanban integration:** Broken — `task_id` normally maps to a kanban task for tracking job runs and aggregating history
- **Database state:** `kanban.db.task_runs` may have `task_id = NULL` for cron-triggered runs, creating orphaned records
- **Audit trail:** Unable to trace a cron execution back to a visible kanban card; debugging harder

---

## Root Cause Hypotheses

| # | Hypothesis | Evidence | Likelihood |
|---|-----------|----------|------------|
| 1 | **Legacy migration gap** — Jobs created before `task_id` field was introduced; migration script failed to backfill | All 744 jobs across 4 agents affected; uniform pattern suggests systemic origin | High |
| 2 | **Direct `jobs.json` editing** — Manual edits bypassed `hermes cron add/edit` CLI which auto-sets `task_id` | Field is missing entirely, not just empty; suggests never set | Medium |
| 3 | **Save-path bug** — `save_jobs()` in `cron/jobs.py` drops `task_id` during dict→JSON serialization | Code inspection shows `task_id` referenced elsewhere but not preserved on write | Low (needs code review) |
| 4 | **Split-config sync failure** — `config.yaml` has empty `cron_jobs: []`; separate sync process meant to populate `task_id` from kanban never ran | The empty `config.yaml` vs populated `jobs.json` mismatch indicates two sources of truth; sync may be broken | Medium |

---

## Immediate Remediation

**Option A — Auto-populate `task_id = id` (safe, quick, preserves uniqueness):**

```bash
python3 << 'PYEOF'
import json, os
for agent in ['gentech','yoyo','dmob','desmond']:
    path = f"/root/.hermes/profiles/{agent}/cron/jobs.json"
    with open(path) as f:
        data = json.load(f)
    jobs = data['jobs']
    fixed = 0
    for job in jobs:
        if 'task_id' not in job:
            job['task_id'] = job['id']  # identity-preserving assignment
            fixed += 1
    if fixed:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"{agent}: fixed {fixed} jobs (added task_id=id)")
    else:
        print(f"{agent}: all task_id already present")
PYEOF
```

**Option B — Use `hermes cron edit` per job (slower, preserves any hidden fields):**

```bash
# For each job, open editor to re-save (forces task_id generation)
hermes cron edit <job-id>
# Save and exit; CLI ensures task_id is set
```

**Option C — Regenerate from kanban (if kanban tasks exist):**

```bash
# Link each cron job to an existing kanban task
hermes cron link --from-kanban
# (hypothetical; verify CLI supports this)
```

**Recommended:** **Option A** — run with gateways **stopped** to avoid race conditions. Idempotent and reversible.

---

## Verification

After remediation:

```bash
# Verify every job has task_id
for agent in gentech yoyo dmob desmond; do
  python3 -c "
import json
data = json.load(open('/root/.hermes/profiles/$agent/cron/jobs.json'))
assert all('task_id' in j for j in data['jobs']), 'MISSING'
print(f'{agent}: ✓ all {len(data[\"jobs\"])} jobs have task_id')
  "
done

# Verify kanban linkage (task_runs should now have proper task_id)
sqlite3 /root/.hermes/profiles/dmob/kanban.db "
SELECT task_id, COUNT(*) FROM task_runs GROUP BY task_id ORDER BY COUNT(*) DESC LIMIT 5;
"
```

---

## Prevention

1. **Never edit `jobs.json` directly** — always use `hermes cron add/edit` CLI, which ensures required fields
2. **Add a pre-commit hook or CI check** to validate `jobs.json` schema before committing:
   ```bash
   python3 -c "
import json, sys
data = json.load(open('cron/jobs.json'))
for j in data['jobs']:
    assert 'task_id' in j, f\"Job {j['id']} missing task_id\"
   "
   ```
3. **Run validation on agent startup** — gateway should log WARNING if any cron job lacks `task_id`
4. **Audit weekly** — run health-check script that scans all profiles for missing `task_id` and alerts

---

## Related Patterns

- **Phase 14** in `gentech-agent-health-diagnosis` — cron subsystem silent execution gap often coincides with this corruption
- **jobs.json vs config.yaml split** — empty `cron_jobs: []` in `config.yaml` may indicate the config system is in a transitional state; investigate migration status