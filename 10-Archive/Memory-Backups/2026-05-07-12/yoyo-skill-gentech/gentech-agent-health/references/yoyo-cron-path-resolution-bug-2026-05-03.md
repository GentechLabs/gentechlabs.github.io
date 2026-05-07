# YoYo Cron Path Resolution Bug — May 3, 2026

## Symptom

YoYo's `defi-milestone-tracker.py` cron job repeatedly fails with:

```
ERROR: AAE config missing: [Errno 2] No such file or directory: '/root/home/.hermes/scripts/.lfj-aae-config.json'
```

The job runs every 10 minutes (cron job ID `3258c64b`), but never succeeds. Gateway log shows no agent-level errors — the failure is isolated to the cron script's stderr.

## Root Cause

The script contains faulty path resolution logic:

```python
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")
```

When `HERMES_HOME` is unset (cron environment), `os.path.expanduser("~")` returns `/root/home`, not `/root`. The script then constructs `/root/home/.hermes/scripts/...` which doesn't exist.

**Actual config location:** `/root/.hermes/scripts/.lfj-aae-config.json`

## Fix Applied

Hardcoded correct path in the script:

```python
HOME_SCRIPTS_DIR = "/root/.hermes/scripts"
```

Changed line in `/root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py`.

## Validation

After fix, cron job should:
1. Find AAE config at `/root/.hermes/scripts/.lfj-aae-config.json`
2. Execute without config-missing errors
3. Exit with code 0 (normal), 1 (efficiency <30%), or 2 (out of range) per script logic

Check cron log:
```bash
tail -20 /root/.hermes/profiles/yoyo/cron.log
```

Expected: No more "AAE config missing" errors. Reports appear in Telegram Strategies group every 10 minutes during trading hours, subject to quiet-hour suppression and debounce logic.

## Pattern to Watch For

Cron scripts that:
- Use `os.path.expanduser("~")` for config paths
- Depend on environment variables that may be unset in cron context
- Construct paths like `~/.hermes/scripts/` or `$HOME/.hermes/scripts/`

**Correction:** Use either:
1. Absolute paths (`/root/.hermes/scripts/`)
2. Or derive from known Hermes profile location: `/root/.hermes/profiles/<agent>/../scripts/`

## Detection Script

```python
import os, glob

hermes_profiles = '/root/.hermes/profiles'
for agent in ['yoyo', 'dmob', 'desmond', 'gentech']:
    scripts_dir = f'{hermes_profiles}/{agent}/scripts'
    if os.path.isdir(scripts_dir):
        for script in glob.glob(f'{scripts_dir}/*.py'):
            with open(script) as f:
                content = f.read()
            if 'expanduser' in content and '.hermes' in content:
                print(f"⚠️  {agent}/{os.path.basename(script)}: uses expanduser — verify path resolution in cron context")
```
