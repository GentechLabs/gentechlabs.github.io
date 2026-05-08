# 2026-05-05: Missing Skill Registry Cron Skipping (DMOB & Desmond)

**Watchdog**: Gentech (May 5, 2026 03:43 UTC)

## Symptom

DMOB and Desmond cron jobs are failing with immediate `skill not found` errors, causing jobs to be skipped:

```
WARNING cron.scheduler: Cron job 'YoYo — Crypto Watchlist + LP Monitor (Hardened)': skill not found, skipping — Skill 'cmc-watchlist-scraper' not found.
WARNING cron.scheduler: Cron job 'Desmond — Crypto Monitor': skill not found, skipping — Skill 'crypto-monitoring-cron' not found.
```

Jobs remain enabled but `last_run_at` stays null; no execution occurs.

## Affected Jobs & Agents

| Agent | Job Name | Missing Skill | Status |
|-------|----------|---------------|--------|
| DMOB  | YoYo — Crypto Watchlist + LP Monitor (Hardened) | `cmc-watchlist-scraper` | Skipped |
| Desmond| Desmond — Crypto Monitor | `crypto-monitoring-cron` | Skipped |

## Root Cause

The skill modules referenced by these cron jobs are **not present** in the agents' skill directories:

```bash
ls /root/.hermes/profiles/dmob/skills/ | grep cmc-watchlist
# (no output)

ls /root/.hermes/profiles/desmond/skills/ | grep crypto-monitoring
# (no output)
```

Likely scenarios:
- Skills were never cloned/synced into these profiles' `skills/` directories
- Skills were removed during a cleanup or git operation
- Skills are defined in the Obsidian vault at `05-Agency/` but symlinks into the agent profiles are broken or missing

## Verification

1. Check each agent's skill registry:
   ```bash
   ls /root/.hermes/profiles/<agent>/skills/
   ```

2. Search logs for all missing-skill warnings (last 6 hours):
   ```bash
   grep -h "Skill.*not found" /root/.hermes/profiles/{dmob,desmond}/logs/errors.log | sort -u
   ```

3. Cross-check job definition in `jobs.json`:
   ```bash
   grep -A5 "Crypto Watchlist" /root/.hermes/cron/jobs.json | head -10
   # Look for "skill" or "script" field; verify path exists
   ```

## Recovery

**Option A — Restore from vault (preferred)**:
1. Locate skill in Obsidian vault: `vault/05-Agency/<skill-name>/`
2. Symlink into agent profile:
   ```bash
   ln -s /root/vaults/gentech/05-Agency/cmc-watchlist-scraper \
          /root/.hermes/profiles/dmob/skills/cmc-watchlist-scraper
   ln -s /root/vaults/gentech/05-Agency/crypto-monitoring-cron \
          /root/.hermes/profiles/desmond/skills/crypto-monitoring-cron
   ```
3. Ensure each skill directory contains `SKILL.md` and `__init__.py` (can be empty file).
4. Restart affected gateways:
   ```bash
   hermes gateway stop --profile dmob
   hermes gateway stop --profile desmond
   hermes gateway run --profile dmob --replace
   hermes gateway run --profile desmond --replace
   ```
5. Re-enable jobs if auto-paused: `hermes cron enable <job_id>`
6. Verify next scheduled run appears in `hermes cron list --profile <agent>`

**Option B — Clone from external repo**:
If skills are maintained in a separate git repo:
```bash
cd /root/.hermes/profiles/dmob/skills/
git clone <repo_url> cmc-watchlist-scraper
cd /root/.hermes/profiles/desmond/skills/
git clone <repo_url> crypto-monitoring-cron
# Then restart gateways
```

**Option C — Remove and recreate jobs without skill dependency** (last resort):
If the skill is deprecated and no longer needed:
1. Disable the job: `hermes cron disable <job_id>`
2. Remove from jobs.json or via `hermes cron delete <job_id>`
3. Alert user that functionality is unavailable

## Prevention

- **Vault as source of truth**: All agent skills should be symlinked from Obsidian vault (`05-Agency/`). Run vault sync before agent startup.
- **Skill presence audit**: Add a pre-cron-run check that verifies every job's `skill` field resolves to an importable module; if missing, log and skip with alert.
- **Git submodules**: If skills live in external repos, add them as git submodules to prevent accidental deletion.
- **Registry integrity script**: Periodically run:
  ```bash
  for agent in yoyo dmob desmond gentech; do
    for job in $(cat /root/.hermes/cron/jobs.json | jq -r '.jobs[] | select(.profile=="'$agent'") | .skill // empty'); do
      if [ ! -d "/root/.hermes/profiles/$agent/skills/$job" ]; then
        echo "MISSING: $agent -> $job"
      fi
    done
  done
  ```

## Related

- `agent-health-audit` pattern: **Missing Skill Registry Cron Skipping**
- Vault: `05-Agency/` skill repository
- Script idea: `scripts/verify_skill_registry_integrity.py` — cross-check all cron job skill references against actual filesystem presence
