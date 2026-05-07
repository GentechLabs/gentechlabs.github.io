# Cron Script Path Security Block

**Symptom**

```
Blocked: script path resolves outside the scripts directory (/root/.hermes/profiles/yoyo/scripts): '/root/vaults/gentech/03-Strategies/scripts/d5-lp-consolidated.py'
```

**Root cause**

Hermes `tirith` security gate enforces that cron-executed scripts must reside inside the profile's allowed scripts directory (`~/.hermes/profiles/<profile>/scripts/`) or the global scripts dir (`~/.hermes/scripts/`). Script paths that resolve to the vault (`/root/vaults/...`) are blocked at runtime before execution.

**Why this happens**

- Vault scripts are for development and editing, not for direct cron execution.
- The security model isolates cron execution to the profile's `scripts/` directory to prevent arbitrary file access.
- When a cron job's `script` field points to a vault path, Hermes detects the path resolution and blocks it.

**Diagnosis**

1. Check the cron job definition:
   ```bash
   cat ~/.hermes/profiles/yoyo/cron/jobs.json | grep -A 3 '"D5 Milestone"'
   ```
   Look for the `script` field value.

2. Verify the path is outside allowed directories:
   ```bash
   python3 -c "
   import os
   script = '/root/vaults/gentech/03-Strategies/scripts/d5-lp-consolidated.py'
   allowed = [
       '/root/.hermes/profiles/yoyo/scripts',
       '/root/.hermes/scripts',
   ]
   script_dir = os.path.dirname(os.path.realpath(script))
   print(f'Script dir: {script_dir}')
   print(f'Allowed: {any(script_dir.startswith(a) for a in allowed)}')
   "
   ```

3. Check gateway logs for the exact block message:
   ```bash
   grep -i "blocked.*script path resolves" ~/.hermes/logs/gateway.log
   ```

**Fix**

**Option 1 — Copy to allowed directory (recommended):**
```bash
# Copy to profile's scripts dir
cp /root/vaults/gentech/03-Strategies/scripts/d5-lp-consolidated.py /root/.hermes/profiles/yoyo/scripts/

# Update cron job to point to allowed copy
python3 -c "
import json
with open('/root/.hermes/profiles/yoyo/cron/jobs.json') as f:
    data = json.load(f)
for job in data['jobs']:
    if job['name'] == 'D5 Milestone':
        job['script'] = '/root/.hermes/profiles/yoyo/scripts/d5-lp-consolidated.py'
        print(f\"Updated job {job['id']}\")
with open('/root/.hermes/profiles/yoyo/cron/jobs.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

**Option 2 — Sync with symlink (if dirs are on same filesystem):**
```bash
# Note: Hermes security resolves realpath, so symlinks pointing outside still blocked.
# Only direct files inside allowed dirs work.
```

**Option 3 — Disable security (NOT recommended):**
```bash
hermes config set security.tirith_enabled false
# Requires gateway restart; reduces security posture profile-wide.
```

**Prevention for new cron jobs**

- Always set the `script` field to a path inside `~/.hermes/profiles/<profile>/scripts/`.
- When creating cron jobs via `hermes cron create`, use a relative path within that directory or the absolute allowed path.
- Keep vault scripts as **source-of-truth** only; use a sync/copy step to deploy to the Hermes scripts dir.

**Related: Script path resolution inside the script itself**

The script should use `hermes_path()` for any state/config file access to ensure write permissions:
```python
import os
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")

def hermes_path(filename: str) -> str:
    return os.path.join(HOME_SCRIPTS_DIR, filename)

STATE_FILE = hermes_path(".d5-lp-state.json")  # NOT hardcoded /root/vaults/...
```
See `Script State Locations` in the `hermes-agent` skill for full details.
