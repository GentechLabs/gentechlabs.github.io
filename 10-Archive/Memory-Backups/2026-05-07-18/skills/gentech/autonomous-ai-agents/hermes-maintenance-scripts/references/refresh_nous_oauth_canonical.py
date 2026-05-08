#!/usr/bin/env python3
"""
Canonical Nous OAuth refresh script for Hermes profiles.

This script must be deployed to ~/.hermes/profiles/<profile>/scripts/
and invoked by cron with HERMES_HOME set to the profile directory.

It uses Hermes' internal resolve_nous_access_token() which:
- Reads the profile's auth.json
- Refreshes if within ACCESS_TOKEN_REFRESH_SKEW_SECONDS (300s) of expiry
- Writes updated tokens back to auth.json
- Mints a fresh agent key if needed

Output: JSON to stdout with fields:
  success (bool), message (str), remaining_seconds (int),
  tokens (access_token_preview, refresh_token_present, expires_at, agent_key_expires_at),
  needs_reauth (bool), critical (bool), hermes_home (str)

Exit code: 0 if tokens are/were fresh, 1 if re-auth required.
"""

import json
import os
import sys

# Hermes internal modules live in /usr/local/lib/hermes-agent
sys.path.insert(0, '/usr/local/lib/hermes-agent')

from hermes_cli.auth import resolve_nous_access_token, get_hermes_home


def main():
    # Use explicit HERMES_HOME from environment (cron sets this per-profile)
    hermes_home = os.environ.get('HERMES_HOME')
    if not hermes_home:
        print(json.dumps({
            "success": False,
            "message": "HERMES_HOME not set — cannot locate profile",
            "critical": True
        }), file=sys.stdout)
        sys.exit(1)

    try:
        result = resolve_nous_access_token(force_refresh=False)
        # result is a dict; convert to JSON-serializable structure
        output = {
            "success": result.get("success", True),
            "message": result.get("message", "Tokens are fresh"),
            "remaining_seconds": result.get("remaining_seconds", 0),
            "tokens": {
                "access_token_preview": (result.get("access_token") or "")[:20] + "...",
                "refresh_token_present": bool(result.get("refresh_token")),
                "expires_at": result.get("expires_at_iso"),
                "agent_key_expires_at": result.get("agent_key_expires_at_iso"),
            },
            "needs_reauth": result.get("needs_reauth", False),
            "critical": result.get("critical", False),
            "hermes_home": hermes_home,
        }
        print(json.dumps(output, indent=2))
        if result.get("needs_reauth"):
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "message": f"Refresh failed: {e}",
            "critical": True,
            "hermes_home": hermes_home
        }), file=sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
