# HERMES_HOME Path Quirk — 2026-05-03

## Observation

On this host, `HERMES_HOME` environment variable was set to:

```
/root/.hermes/profiles/gentech
```

However, when inspected from within the Python process launched by cron, the resolved working directory showed a **nested duplication**:

```
/root/.hermes/profiles/gentech/home/.hermes/profiles/gentech
```

This caused initial script path construction to fail with "No such file or directory" when concatenating `HERMES_HOME/scripts/refresh_nous_oauth.py` directly.

## Root Cause

The Hermes cron runner appears to `cd` into a nested `home/.hermes/profiles/<profile>` subdirectory before executing scripts, possibly to isolate profile state. The `HERMES_HOME` env var remains the top-level profile dir, but the actual script lives in the nested copy.

## Fix Pattern

Always resolve the **canonical** script directory:

```bash
# Bash
HERMES_HOME_CANONICAL=$(realpath "${HERMES_HOME:-~/.hermes/profiles/gentech}")
SCRIPT_DIR="$HERMES_HOME_CANONICAL/scripts"
```

Or hardcode the known canonical path when operating in Gentech's vault context:

```python
canonical = "/root/.hermes/profiles/gentech"  # vault-configured ground truth
scripts_dir = os.path.join(canonical, "scripts")
```

Never trust that `$HERMES_HOME` + relative path = script location without validation.

## Affected Scripts

Any maintenance script that constructs paths from `HERMES_HOME` without resolution:
- Path-discovery logic in `refresh_nous_oauth.py` (uses `HERMES_HOME` from env)
- Ad-hoc diagnostic commands run from cron sandbox
- Future health-check scripts

## Quick Test

```bash
# Should resolve to same canonical path
echo "HERMES_HOME env: $HERMES_HOME"
echo "Realpath: $(realpath "$HERMES_HOME")"
echo "Script exists: $(test -f "$(realpath "$HERMES_HOME")/scripts/refresh_nous_oauth.py" && echo yes || echo no)"
```

If you see duplication in the realpath output, use the realpath result for all file operations.
