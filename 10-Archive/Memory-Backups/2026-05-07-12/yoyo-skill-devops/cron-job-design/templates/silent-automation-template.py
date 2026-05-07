#!/usr/bin/env python3
"""
Silent-mode automation script template.

Exit code semantics:
  0 — Success OR expected operational state (needs manual action)
  1 — Unexpected error (triggers cron/alerting)

Always prints JSON status for logging/monitoring.
"""

import json
import sys
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    status = {
        "success": False,
        "needs_manual_action": False,
        "critical": False,
        "message": "",
        "timestamp": now_iso(),
        "details": {}
    }

    try:
        # --- YOUR TASK LOGIC HERE ---
        # Example: check something, perform action
        # If an expected condition occurs (e.g., token needs re-auth):
        #   raise ExpectedCondition("needs_reauth: true — run `hermes model` to re-authenticate")
        # If everything is fine:
        status["success"] = True
        status["message"] = "Task completed successfully"
        # ---------------------------

    except ExpectedCondition as e:
        status["success"] = False
        status["needs_manual_action"] = True
        status["message"] = str(e)
    except Exception as e:
        status["success"] = False
        status["critical"] = True
        status["message"] = f"Unexpected error: {type(e).__name__}: {e}"
        import traceback
        status["traceback"] = traceback.format_exc()[:500]

    print(json.dumps(status, indent=2))

    if status.get("critical"):
        sys.exit(1)
    if not status.get("success") and not status.get("needs_manual_action"):
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
