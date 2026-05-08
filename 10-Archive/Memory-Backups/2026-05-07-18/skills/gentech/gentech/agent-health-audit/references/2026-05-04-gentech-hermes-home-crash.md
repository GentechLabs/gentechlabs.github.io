# Gentech HERMES_HOME Environment Crash — May 4, 2026 22:05

## Symptom
Gentech agent session `session_20260504_220501_8d25ec.json` contains a full Python traceback ending with:

```
KeyError: b'HERMES_HOME'
...
OSError: [Errno 5] Input/output error
```

The agent gateway process crashes shortly after startup (10-second session duration).

## Root Cause
The Hermes gateway attempted to read environment variables from the process environment but the `HERMES_HOME` key was missing. This is typically caused by:
- The agent was launched without properly setting the HERMES_HOME environment variable
- The systemd service ExecStart or manual command omitted `--env` or the environment file
- The gateway's configuration expected HERMES_HOME to be present but it wasn't exported

## Detection
From other agent sessions, the same timeframe shows multiple `NameError` and `RuntimeError` entries, suggesting a systemic environment misconfiguration affecting Gentech specifically.

Traceback signature:
- Appears within first 10–15 seconds of session start
- `File "/usr/local/lib/hermes-agent/hermes_cli/profiles.py", line 760, in get_active_profile_name` → calls `get_hermes_home()`
- `File "/usr/local/lib/hermes-agent/hermes_constants.py", line 30, in get_hermes_home` → `os.environ.get("HERMES_HOME", "")`
- KeyError indicates `os.environ[b'HERMES_HOME']` access pattern (using bytes key)

## Impact
- Gentech gateway crashes immediately; no cron jobs execute
- No Telegram connectivity established
- Silent failure until watchdog review of session transcripts

## Recovery
1. Verify HERMES_HOME is set correctly for the Gentech profile:
   ```bash
   cat /root/.hermes/profiles/gentech/.env 2>/dev/null | grep HERMES_HOME
   ```
   Should be absent — HERMES_HOME is not typically in .env; it's set by the launcher.

2. Check the actual gateway launch command:
   - If using systemd: `systemctl --user status hermes-gateway-gentech.service` → inspect `ExecStart` line
   - If manual: review the start script or crontab entry

3. Ensure HERMES_HOME points to the profile directory:
   ```bash
   export HERMES_HOME=/root/.hermes/profiles/gentech
   ```
   This should be set before invoking `python -m hermes_cli.main gateway run`.

4. Restart the gateway with proper environment:
   ```bash
   HERMES_HOME=/root/.hermes/profiles/gentech /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile gentech gateway run --replace
   ```

5. Validate: Check new session file appears within 60 seconds and no traceback present.

## Prevention
- All gateway launch mechanisms (systemd units, crontab entries, manual scripts) must export HERMES_HOME before execution
- Add a pre-start validation script to check for required env vars:
  ```bash
  [ -z "$HERMES_HOME" ] && echo "ERROR: HERMES_HOME not set" && exit 1
  ```
- The `agent-health-audit` skill now includes HERMES_HOME missing as a flagged condition during process environment validation (see "Process environment vs .env file validation" section).

## Related Patterns
- Process environment validation: The skill's existing pattern "Process environment vs .env file validation" covers checking the running process environment; this case extends it to include HERMES_HOME specifically.
- Gateway.pid file format: Use the PID file to get the actual running command and environment; if HERMES_HOME is missing from the process environ, the gateway cannot resolve its profile path and crashes.