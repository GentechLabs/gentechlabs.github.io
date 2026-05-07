#!/usr/bin/env python3
"""
Template: Maintenance Cron Script with Silent Expected Failures

This is a canonical starting point for cron scripts that perform
proactive maintenance (token refresh, health checks, cleanup, etc.).

Key principle:
  - Exit 0 for expected manual-action states (token revoked, service down, quota exceeded)
  - Exit 1 only for unexpected errors (crashes, misconfigurations)
  - Always output structured JSON so humans can see what happened

Usage: Copy this template and adapt the `run_maintenance()` logic.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def build_status(success: bool, *, needs_manual_action: bool = False,
                  action_type: str | None = None, message: str = "",
                  **extra_fields) -> dict:
    """Build a standardized status dict for cron consumption."""
    status = {
        "success": success,
        "needs_manual_action": needs_manual_action,
        "action_type": action_type,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).name,
    }
    status.update(extra_fields)
    return status


def run_maintenance() -> dict:
    """
    Your maintenance logic goes here. Return a status dict.

    Example return values:

    All good, nothing to do:
        {"success": True, "needs_manual_action": False, "message": "No action needed"}

    Expected manual intervention needed:
        {"success": False, "needs_manual_action": True, "action_type": "reauth",
         "message": "OAuth token revoked; run `hermes model` to re-authenticate."}

    Unexpected error:
        {"success": False, "needs_manual_action": False, "action_type": "bug",
         "message": "Invalid configuration: missing API key"}
    """
    # --- YOUR CODE HERE ---
    # Replace this stub with actual work
    status = build_status(
        success=True,
        needs_manual_action=False,
        message="Maintenance completed successfully"
    )
    return status


def main():
    status = run_maintenance()

    # Print JSON for cron job logs and downstream consumption
    print(json.dumps(status, indent=2))

    # Exit code decision:
    #  0 — Script executed (even if manual action is needed; that's an expected state)
    #  1 — Unexpected error (script crashed, misconfigured, etc.)
    if status.get("needs_manual_action"):
        return 0  # Silence automated alerts; human will read output
    return 0 if status["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
