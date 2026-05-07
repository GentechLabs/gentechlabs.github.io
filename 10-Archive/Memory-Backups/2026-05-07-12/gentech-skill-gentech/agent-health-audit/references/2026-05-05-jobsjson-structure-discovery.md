# 2026-05-05 — jobs.json Structure Discovery: Dict-with-Jobs-Key vs Direct Array

**Skill context**: `agent-health-audit` — Phase 3 cron verification, job registry parsing

## What happened

During a fleet health audit (May 5, 2026), the diagnostic script that iterates over `jobs.json` content failed with:

```
TypeError: unhashable type: 'slice'
```

The code was:
```python
jobs = json.load(open(jobs.json))
for i, job in enumerate(jobs[:5]):  # <-- assumes jobs is a list
    ...
```

## Root cause

Hermes cron `jobs.json` files are **not** a raw JSON array. They have this structure:

```json
{
  "jobs": [
    { "name": "Gentech Watchdog", "schedule": {...}, ... },
    ...
  ],
  "updated_at": "2026-05-05T03:45:59.256388Z"
}
```

Attempting to slice a dict (`jobs[:5]`) raises `TypeError: unhashable type: 'slice'`.

## Impact

Any diagnostic code that directly indexes `jobs` as a list will crash:
- `len(jobs)` → returns key count (2), not job count
- `jobs[0]` → KeyError (dict has no numeric keys)
- `for job in jobs` → iterates dict keys (`'jobs'`, `'updated_at'`), not job objects

This broke the May 5 watchdog run mid-output and required manual recovery via direct file inspection.

## Correct access pattern

```python
import json

with open('/root/.hermes/profiles/<agent>/cron/jobs.json') as f:
    data = json.load(f)

if isinstance(data, dict) and 'jobs' in data:
    jobs = data['jobs']
    total = len(jobs)
else:
    jobs = []
    total = 0

for i, job in enumerate(jobs[:5]):
    print(f"Job {i}: {job.get('name')}")
```

**One-liner** (when structure is known correct):
```python
jobs = json.load(open(path)).get('jobs', [])
```

## Affected locations

This structure appears in **every agent's cron directory**:
- `/root/.hermes/profiles/gentech/cron/jobs.json`
- `/root/.hermes/profiles/yoyo/cron/jobs.json`
- `/root/.hermes/profiles/dmob/cron/jobs.json`
- `/root/.hermes/profiles/desmond/cron/jobs.json`

All use the same dict-with-`jobs`-key format.

## Related skill code needing update

Any skill or script that reads cron job definitions must guard with:
```python
data = json.load(...)
jobs = data['jobs'] if isinstance(data, dict) else data  # legacy fallback
```

Scripts identified with this anti-pattern:
- `scripts/detect_duplicate_cron.py` (in this skill directory) — needs same guard
- Quick one-liners in health-check transcripts that assume direct list

## Validation

Check a file's actual type before indexing:
```bash
python3 -c "
import json
d = json.load(open('/root/.hermes/profiles/gentech/cron/jobs.json'))
print(type(d), d.keys() if isinstance(d, dict) else 'list')
"
# Expected output: <class 'dict'> dict_keys(['jobs', 'updated_at'])
```

## Prevention

Add a helper function to the agent-health-audit scripts:
```python
def load_cron_jobs(path):
    with open(path) as f:
        obj = json.load(f)
    return obj.get('jobs', []) if isinstance(obj, dict) else obj
```

Use this instead of raw `json.load()` everywhere.
