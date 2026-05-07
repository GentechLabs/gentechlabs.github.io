---
name: hermes-maintenance-scripts
description: Deploy and maintain profile-specific maintenance scripts (OAuth refresh, health checks) across Hermes Agent profiles using the vault as single source of truth.
version: 0.1.0
author: Gentech Labs
license: MIT
metadata:
  hermes:
    tags: [hermes, maintenance, deployment, scripts, cron, oauth]
    related_skills: [hermes-agent, vault-script-execution]
---

# Hermes Maintenance Scripts

**Purpose:**  
Ensure critical maintenance scripts (OAuth token refresh, health checks, periodic tasks) are consistently deployed, executable, and functional across all Hermes profiles. This skill codifies the vault→runtime deployment pattern and avoids drift between environments.

**Scope:**  
- Profile-specific scripts stored in `~/.hermes/profiles/<profile>/scripts/`
- Vault as canonical source: `/root/vaults/gentech/00-System/agent-profiles/<profile>/scripts/`
- Global scripts directory: `/root/.hermes/scripts/` (different semantics — not for profile cron jobs)
- Cron jobs reference scripts by filename only, resolved relative to the profile's scripts directory

## When to Use

Use this skill when:
- Setting up a new Hermes profile that requires automated maintenance tasks
- Debugging a failing cron job that invokes a script
- Reconciling script drift between vault and runtime across multiple profiles
- Adding a new periodic maintenance task (token refresh, health check, LP monitor, etc.)

## Pattern: Vault-Centric Script Deployment

**Golden Rule:**  
The vault's `/root/vaults/gentech/00-System/agent-profiles/<profile>/scripts/` directory is the **single source of truth**. Runtime copies in `~/.hermes/profiles/<profile>/scripts/` are ephemeral and must be refreshed from the vault when they diverge or go missing.

### 1. Author in Vault First

Write and test your script in the vault path:

```bash
cd /root/vaults/gentech/00-System/agent-profiles/gentech/scripts/
# Edit refresh_nous_oauth.py or create new script
```

**Requirements for all maintenance scripts:**
- Shebang: `#!/usr/bin/env python3`
- Emit JSON to stdout on success/failure for log parsing
- Exit code `0` on success, non-zero on error
- Respect `HERMES_HOME` environment variable to locate the profile's data
- Use Hermes internal modules when available (e.g., `from hermes_cli.auth import resolve_nous_access_token`) — **do not reimplement OAuth flows**
- Make executable: `chmod 755 <script>.py`

### 2. Deploy to Runtime

Copy (or symlink) from vault to each profile's scripts directory:

```bash
# For gentech profile
cp /root/vaults/gentech/00-System/agent-profiles/gentech/scripts/refresh_nous_oauth.py \
   /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
chmod 755 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py

# Repeat for yoyo, dmob, desmond as needed
```

⚠️ **Warning:** Profile scripts are regular files, not symlinks. If a deployment tool (e.g. `install.sh`) exists, verify it uses the vault version and does **not** overwrite with the global script variant.

### 3. Verify Under Profile Context

```bash
HERMES_HOME=/root/.hermes/profiles/gentech \
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
```

Expected output (JSON):
```json
{
  "success": true,
  "message": "Tokens are fresh",
  "remaining_seconds": 563,
  ...
}
```

### 4. Sync Vault → All Profiles (Automation)

Use the bundled sync helper (see `scripts/sync_maintenance_scripts.py`) to propagate vault changes to all profiles:

```bash
# Dry-run first to see differences
python3 /root/.hermes/profiles/gentech/skills/autonomous-ai-agents/hermes-maintenance-scripts/scripts/sync_maintenance_scripts.py --dry-run

# Apply sync
python3 /root/.hermes/profiles/gentech/skills/autonomous-ai-agents/hermes-maintenance-scripts/scripts/sync_maintenance_scripts.py
```

The sync helper:
- Compares MD5 hashes of each `.py` file between vault and runtime
- Copies only changed files
- Sets `chmod 755` on deployed scripts
- Supports `--profile <name>` to limit scope

## Case Study: Nous OAuth Token Refresh

This is the canonical example — deploy `refresh_nous_oauth.py` to every profile that uses Nous Portal OAuth.

**Script behavior:**
- Calls `resolve_nous_access_token(force_refresh=False)` from `hermes_cli.auth`
- Refreshes proactively when `expires_at - now < ACCESS_TOKEN_REFRESH_SKEW_SECONDS` (300s)
- Writes updated tokens to `~/.hermes/profiles/<profile>/auth.json`
- Returns JSON status with `success`, `message`, `remaining_seconds`, `tokens.*` fields

**Cron integration:**
```json
// ~/.hermes/profiles/gentech/cron/jobs.json
{
  "jobs": [
    {
      "id": "...",
      "name": "Nous OAuth Proactive Refresh",
      "schedule": {"kind": "interval", "minutes": 10},
      "prompt": "...",
      "script": "refresh_nous_oauth.py"
    }
  ]
}
```

**Critical:** The cron environment sets `HERMES_HOME` to the profile directory. If you test manually, you **must** set it explicitly or the script will read the wrong `auth.json`.

See `references/refresh_nous_oauth_canonical.py` for the full working implementation.

## Architecture: Three Script Realms

| Realm | Path | Purpose | Used By |
|-------|------|---------|---------|
| **Vault (canonical)** | `/root/vaults/gentech/00-System/agent-profiles/<profile>/scripts/` | Version-controlled source, audit trail, team collaboration | Human editors, sync tools |
| **Runtime (profile)** | `/root/.hermes/profiles/<profile>/scripts/` | Actual execution by cron jobs, gateway, manual runs | Hermes cron, `hermes cron run` |
| **Global** | `/root/.hermes/scripts/` | Shared utilities, NOT profile-specific cron scripts | Potentially other Hermes subsystems |

**Do NOT** use the global script directory for profile cron jobs unless the job explicitly references it with an absolute path. Most profile cron jobs use relative script names, which resolve to the profile's own `scripts/` directory.

## Common Pitfalls

### Script Drift
**Symptom:** Script works in one profile but fails in another with `Script not found` or import errors.  
**Cause:** Runtime copy out of sync with vault.  
**Fix:** Run the sync helper from this skill; consider adding a pre-cron validation step.

### Missing Executable Bit
**Symptom:** `Permission denied` when cron runs the script.  
**Fix:** `chmod 755 /root/.hermes/profiles/<profile>/scripts/<script>.py`

### Wrong HERMES_HOME
**Symptom:** Script reads wrong `auth.json` or config, tokens never refresh.  
**Fix:** Always test with `HERMES_HOME` set to the target profile. Cron should inherit this from the profile's environment; verify with `hermes cron list` and check the gateway's environment.

### Global Script Confusion
**Symptom:** Deployed script differs from vault version despite copying.  
**Cause:** An `install.sh` or other deployment tool copied the global `/root/.hermes/scripts/refresh_nous_oauth.py` (4411 bytes) instead of the vault version (3640 bytes).  
**Fix:** Audit `/root/.hermes/scripts/` — if it contains a divergent variant, either update it to match the vault or remove it to prevent accidental overwrites. The global script may serve a different purpose.

### Auth JSON Path Resolution Under Profile-Isolated HOME
**Symptom:** Script crashes with `FileNotFoundError: /root/.hermes/profiles/gentech/home/.hermes/auth.json` when run from cron. The file exists at `/root/.hermes/auth.json` but the script looks in the profile-isolated home directory.  
**Cause:** Using `os.path.join(HOME, '.hermes', 'auth.json')` where `HOME` expands to the profile's isolated home (e.g., `/root/.hermes/profiles/gentech/home`). This path does not exist because the Hermes global `auth.json` lives at `/root/.hermes/auth.json`, not under the profile's home. The bug commonly affects scripts that import from `hermes_cli.auth` and need to access the *global* token pool.  
**Fix:** Replace the HOME-based path with an absolute reference:
```python
# BEFORE (broken)
AUTH_PATH = os.path.join(HOME, '.hermes', 'auth.json')

# AFTER (correct)
AUTH_PATH = '/root/.hermes/auth.json'
```
**Verification:** After fixing, run the script manually first (`python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py`) and then let cron execute it on schedule. The cron job must succeed without FileNotFoundError.

**Detection:** Check the script's `AUTH_PATH` definition; if it uses `os.path.expanduser('~')` or `HOME` to construct the auth path, it is vulnerable to this bug.

### Stale Cron Data
**Symptom:** Cron job shows `next_run_at` in the past and never fires.  
**Fix:** Restart the gateway with `hermes gateway restart --profile <profile>` or use the timestamp repair script in the `hermes-agent` skill's troubleshooting section.

## Audit Checklist

Run monthly across all profiles:

```bash
for profile in gentech yoyo dmob desmond; do
  echo "=== $profile ==="
  # 1. List runtime scripts
  ls -l /root/.hermes/profiles/$profile/scripts/*.py 2>/dev/null
  # 2. Compare hashes with vault
  for s in /root/.hermes/profiles/$profile/scripts/*.py; do
    [ -f "$s" ] || continue
    fname=$(basename "$s")
    vault="/root/vaults/gentech/00-System/agent-profiles/$profile/scripts/$fname"
    if [ -f "$vault" ]; then
      r=$(md5sum "$s" | cut -d' ' -f1)
      v=$(md5sum "$vault" | cut -d' ' -f1)
      if [ "$r" != "$v" ]; then
        echo "  DRIFT: $fname"
      fi
    fi
  done
done
```

## Integration with Other Skills

- **`hermes-agent`**: Use this skill for the OAuth-specific refresh logic and cron troubleshooting
- **`vault-script-execution`**: For running vault scripts directly without deployment
- **`agent-health-audit`**: Health checks should use the same deployment pattern

## Future Extensions

- Auto-sync hook: Watch vault script directory and auto-deploy on change (requires inotify or polling)
- Pre-cron validation: Gateway runs a quick check before each scheduled run
- Cross-profile version matrix: Track which profile runs which script version for compliance

---

*This skill captures the deployment architecture discovered during the Gentech OAuth refresh script incident (2026-05-03). The vault→runtime pattern is now the standard for all periodic maintenance automation.*

**Support Files:**
- `references/refresh_nous_oauth_canonical.py` — Proven, working implementation of the Nous OAuth refresh script
- `scripts/sync_maintenance_scripts.py` — CLI tool to propagate vault script changes to all profiles
