# Cron Database Corruption Patterns

## Signature

All cron jobs in `jobs.json` have empty `profile` and `script` fields, and `last_run` is `null`:

```bash
python3 -c "import json; d=json.load(open('/root/.hermes/cron/jobs.json')); jobs=d['jobs']; print('Total:', len(jobs)); print('Missing profile:', sum(1 for j in jobs if not j.get('profile'))); print('Missing script:', sum(1 for j in jobs if not j.get('script'))); print('Never run:', sum(1 for j in jobs if not j.get('last_run')))"
```

Output:
```
Total: 4
Missing profile: 4
Missing script: 4
Never run: 4
```

## Root Causes

- **Interrupted cron create**: Job creation via `hermes cron create` interrupted by gateway crash or disk pressure.
- **Database migration failure**: Incomplete migration from old cron format to new schema.
- **Manual JSON edit error**: Accidental field deletion during manual `jobs.json` editing.
- **Filesystem corruption**: Disk pressure or I/O errors causing truncated writes (see concurrent `Errno 28` errors in agent logs).

## Detection

Cross-check across multiple dimensions:

```bash
# 1. Field completeness check (above)
# 2. Gateway log: cron ticker started but zero executor runs
grep "Cron ticker started" /root/.hermes/profiles/*/logs/gateway.log
grep -c "executing job" /root/.hermes/profiles/*/logs/agent.log  # should be >0 if healthy

# 3. Agent log: no "Job completed" messages
grep "Job run completed" /root/.hermes/profiles/*/logs/agent.log | wc -l  # expect 0 if corrupt

# 4. hermes cron list shows None status
hermes cron list --verbose | grep "status=None"
```

## Remediation

**Option A — Recreate individual jobs (preserves IDs if known):**

```bash
# For each job, recover parameters from old records or memory, then:
hermes cron create --name "Job Name" --schedule "0 6 * * *" --script "/path/to/script.py" --profile yoyo
```

**Option B — Bulk rebuild from backup (if available):**

```bash
# Restore known-good jobs.json from /root/.hermes/cron/backups/ or vault
cp /root/vaults/gentech/backups/cron-jobs-20260501.json /root/.hermes/cron/jobs.json
systemctl restart hermes-gateway  # or restart each agent gateway
```

**Option C — Emergency reset (nuclear):**

```bash
# WARNING: deletes all cron jobs
rm /root/.hermes/cron/jobs.json
hermes cron create --name "Watchdog" --schedule "*/60 * * * *" --script "/root/scripts/watchdog.py" --profile yoyo
# Recreate remaining jobs manually
```

## Prevention

- **Enable cron backups**: `hermes cron backup --daily` (if available) or set up manual snapshot before bulk edits.
- **Validate after create**: Immediately after `hermes cron create`, run `hermes cron list --verbose` and verify `profile` and `script` fields populated.
- **Disk space monitoring**: Ensure root partition stays below 75% to prevent I/O errors during writes.
- **Atomic updates**: Edit `jobs.json` only via `hermes cron edit <id>` CLI, never direct file edit.

## Related Errors

- `cron.scheduler: Job 'xxxx' failed: <exception>` — generic failure; underlying cause may be database corruption.
- `cron executor deadlock` — ticker runs but no jobs dispatch; symptom of corrupt DB where executor loop aborts early.
- Gateway log: `Cron ticker started` followed by nothing in `agent.log` → executor never initialized due to DB validation error at startup.