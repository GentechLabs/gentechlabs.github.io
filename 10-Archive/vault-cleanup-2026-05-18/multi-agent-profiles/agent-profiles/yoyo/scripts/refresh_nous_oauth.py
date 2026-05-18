#!/usr/bin/env python3
"""
Proactive Nous OAuth Refresh Script

Refreshes Nous Portal OAuth tokens before they expire.
This script is run by cron to keep the Nous integration alive.

It checks the current token expiry and refreshes if within the skew window
(2 minutes before expiry) or if the token is already expired.

Exit codes:
  0 - Success (tokens are valid, refreshed if needed)
  1 - Error (needs manual re-authentication via `hermes model`)

Output: JSON status report for cron job consumption.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add Hermes to path
sys.path.insert(0, '/usr/local/lib/hermes-agent')

def get_hermes_home() -> Path:
    """Get HERMES_HOME respecting profile-specific locations."""
    val = os.environ.get("HERMES_HOME", "").strip()
    if val:
        return Path(val)
    # Fallback uses ~/.hermes but cron should always set HERMES_HOME
    return Path.home() / ".hermes"

def main():
    hermes_home = get_hermes_home()
    auth_file = hermes_home / "auth.json"
    
    status = {
        "success": False,
        "message": "",
        "tokens": {},
        "needs_reauth": False,
        "critical": False,
        "hermes_home": str(hermes_home),
    }

    try:
        # Import here to avoid unnecessary imports on failure
        from hermes_cli.auth import resolve_nous_access_token, AuthError

        # Resolve and refresh if necessary
        access_token = resolve_nous_access_token()

        # Read back the updated state
        if not auth_file.exists():
            raise Exception(f"Auth file not found: {auth_file}")

        with open(auth_file) as f:
            auth_data = json.load(f)

        nous_state = auth_data.get('providers', {}).get('nous', {})
        if not nous_state:
            raise Exception("Nous provider state missing after refresh")

        # Calculate remaining TTL
        expires_at = nous_state.get("expires_at")
        remaining_seconds = None
        if expires_at and isinstance(expires_at, str):
            try:
                exp = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                remaining_seconds = max(0, int((exp - now).total_seconds()))
            except Exception as e:
                status["message"] = f"Could not parse expiry: {e}"

        status["success"] = True
        status["message"] = "Tokens are fresh"
        status["tokens"] = {
            "access_token_preview": (
                nous_state.get("access_token", "")[:20] + "..."
                if nous_state.get("access_token") else None
            ),
            "refresh_token_present": bool(nous_state.get("refresh_token")),
            "expires_at": expires_at,
            "agent_key_expires_at": nous_state.get("agent_key_expires_at"),
        }
        status["remaining_seconds"] = remaining_seconds
        status["needs_reauth"] = False

    except AuthError as e:
        status["success"] = False
        status["message"] = str(e)
        status["needs_reauth"] = e.relogin_required
        if e.relogin_required:
            status["message"] += " Run `hermes model` to re-authenticate."
    except Exception as e:
        status["success"] = False
        status["message"] = f"Unexpected error: {type(e).__name__}: {e}"
        status["critical"] = True
        import traceback
        status["traceback"] = traceback.format_exc()[:500]

    # Output JSON for cron job consumption
    print(json.dumps(status, indent=2))

    # Exit code logic:
    #  0 — Success OR needs_reauth (expected operational state; silent)
    #  1 — Unexpected error (actual script failure; alert)
    # This keeps the cron job "silent" when tokens just need manual re-authentication.
    if status.get("critical"):
        return 1
    if not status.get("success") and not status.get("needs_reauth"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
