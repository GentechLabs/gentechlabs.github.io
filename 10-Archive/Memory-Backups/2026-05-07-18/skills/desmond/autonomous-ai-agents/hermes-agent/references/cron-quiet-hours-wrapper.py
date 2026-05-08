#!/usr/bin/env python3
"""
Quiet-Hours Wrapper for Maintenance Cron Jobs

Wraps a maintenance script and suppresses its stdout during configured
quiet hours (local time). The wrapped script still runs; only output
is silenced. Exit code is preserved so cron health checks work.

Usage:
  1. Copy this file to ~/.hermes/scripts/quiet_wrapper.py (or any name)
  2. Set QUIET_START/QUIET_END/QUIET_END_MINUTE to your local quiet hours
  3. Set TIMEZONE to your IANA timezone (e.g., "America/New_York")
  4. Set ORIGINAL_SCRIPT to the filename of the real maintenance script
  5. Make wrapper executable (chmod +x)
  6. Update cron job: hermes cron edit <ID> --script quiet_wrapper.py

Note: Keep ORIGINAL_SCRIPT in the same directory as this wrapper
(~/.hermes/scripts/ or profile-specific scripts/).
"""

import os
import sys
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

# --- Configuration ---
# Local quiet hours (24h clock)
QUIET_START_HOUR = 23   # 11 PM
QUIET_END_HOUR   = 6    # 6 AM
QUIET_END_MINUTE = 30   # 6:30 AM

# Your timezone for quiet-hour conversion (IANA database name)
# EST/EDT: "America/New_York"
# Other examples: "America/Los_Angeles", "Europe/London", "Asia/Tokyo"
TIMEZONE = "America/New_York"

# The actual maintenance script filename (must exist in same scripts/ dir)
ORIGINAL_SCRIPT = "refresh_nous_oauth.py"
# ---------------------

def in_quiet_hours(now: datetime) -> bool:
    """Check if 'now' (aware datetime in local tz) falls within quiet hours."""
    hour = now.hour
    minute = now.minute
    start = QUIET_START_HOUR
    end = QUIET_END_HOUR
    end_min = QUIET_END_MINUTE

    if start > end:
        # Window crosses midnight (e.g., 23:00–06:30)
        if hour >= start or (hour < end or (hour == end and minute < end_min)):
            return True
    else:
        # Window within same day (unusual but supported)
        if hour >= start and (hour < end or (hour == end and minute < end_min)):
            return True
    return False


def main():
    hermes_home = os.environ.get("HERMES_HOME", "")
    if not hermes_home:
        # Default to root gentech profile if not set (adjust if needed)
        hermes_home = "/root/.hermes/profiles/gentech"

    script_path = os.path.join(hermes_home, "scripts", ORIGINAL_SCRIPT)
    if not os.path.exists(script_path):
        print(f"ERROR: Wrapped script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env["HERMES_HOME"] = hermes_home

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )

    # Determine quiet status using local timezone
    try:
        local_tz = ZoneInfo(TIMEZONE)
        now_local = datetime.now(local_tz)
        quiet = in_quiet_hours(now_local)
    except Exception as e:
        # If zoneinfo fails, fall back to simple UTC offset approx
        print(f"WARNING: ZoneInfo error: {e}", file=sys.stderr)
        quiet = False  # Better to leak output than stay silent on error

    if not quiet:
        # Outside quiet hours: passthrough stdout exactly as received
        print(result.stdout, end='')

    # Exit with original code (0 = ok, 1 = needs reauth, etc.)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
