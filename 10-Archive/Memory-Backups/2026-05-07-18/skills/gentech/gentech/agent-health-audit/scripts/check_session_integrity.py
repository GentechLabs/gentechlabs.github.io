#!/usr/bin/env python3
"""
Session completeness auditor for Hermes agents.

Checks recent session files for structural integrity (presence of required fields).
Intended for cron execution (e.g., every 5 minutes) as part of fleet health monitoring.

Exit codes:
  0 — All agents healthy (≥80% completion rate, no agents at 0%)
  1 — Degraded (one or more agents with 50–79% completion)
  2 — Critical (any agent with <50% completion, or all agents at 0%)
  3 — No session files found for one or more agents (misconfiguration)

Usage:
  python3 check_session_integrity.py [--hours 2] [--min-sessions 5]

Dependencies:
  Python 3.7+, standard library only.
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

AGENTS = ["yoyo", "dmob", "desmond", "gentech"]
BASE_DIR = Path("/root/.hermes/profiles")

# Required top-level keys for a complete session record
# NOTE: Schema evolved — older sessions used {'status', 'created_at'}.
# Current sessions (May 2026+) use {'session_start', 'last_updated', 'messages'}.
# Update REQUIRED_KEYS when schema changes again. Run schema probe to verify:
#   python3 -c "import json,glob,os; f=sorted(glob.glob('/root/.hermes/profiles/gentech/sessions/*.json'),key=os.path.getmtime,reverse=True); print(list(json.load(open(f[0])).keys())[:15])"
REQUIRED_KEYS = {"session_start", "last_updated", "messages"}


def check_agent(agent: str, hours: int, min_sessions: int) -> dict:
    """Return completeness stats for one agent."""
    session_dir = BASE_DIR / agent / "sessions"
    if not session_dir.exists():
        return {"error": "NO_SESSION_DIR"}

    cutoff = datetime.now().timestamp() - (hours * 3600)
    complete = 0
    incomplete = 0
    errors = 0
    total_recent = 0

    pattern = str(session_dir / "*.json")
    for fpath in glob.glob(pattern):
        try:
            if os.path.getmtime(fpath) < cutoff:
                continue
            total_recent += 1
            with open(fpath, "r") as fh:
                data = json.load(fh)
            if REQUIRED_KEYS.issubset(data.keys()):
                complete += 1
            else:
                incomplete += 1
        except (json.JSONDecodeError, OSError):
            errors += 1

    if total_recent == 0:
        return {"error": "NO_RECENT_SESSIONS"}

    rate = (complete / total_recent) * 100 if total_recent else 0
    return {
        "total": total_recent,
        "complete": complete,
        "incomplete": incomplete,
        "errors": errors,
        "rate": rate,
    }


def evaluate_fleet(results: dict) -> tuple[int, list[str]]:
    """Determine fleet health and produce human-readable issues list."""
    issues = []
    critical = degraded = 0

    for agent, r in results.items():
        if "error" in r:
            issues.append(f"{agent.upper()}: {r['error']}")
            critical += 1
            continue

        if r["rate"] == 0:
            critical += 1
            issues.append(f"{agent.upper()}: 0% completion ({r['incomplete']}/{r['total']} incomplete)")
        elif r["rate"] < 50:
            critical += 1
            issues.append(f"{agent.upper()}: {r['rate']:.0f}% completion (critical)")
        elif r["rate"] < 80:
            degraded += 1
            issues.append(f"{agent.upper()}: {r['rate']:.0f}% completion (degraded)")

    if critical > 0:
        return 2, issues  # critical
    elif degraded > 0:
        return 1, issues  # degraded
    else:
        return 0, []  # OK


def main():
    parser = argparse.ArgumentParser(description="Audit Hermes agent session integrity")
    parser.add_argument("--hours", type=int, default=2, help="Time window in hours (default: 2)")
    parser.add_argument("--min-sessions", type=int, default=5, help="Minimum expected sessions in window (warning only)")
    args = parser.parse_args()

    results = {}
    for agent in AGENTS:
        results[agent] = check_agent(agent, args.hours, args.min_sessions)

    # Print per-agent summary
    for agent, r in results.items():
        if "error" in r:
            print(f"{agent.upper()}: {r['error']}")
        else:
            print(
                f"{agent.upper()}: {r['complete']}/{r['total']} complete, "
                f"{r['incomplete']} incomplete, {r['errors']} errors — {r['rate']:.0f}%"
            )

    exit_code, issues = evaluate_fleet(results)

    if exit_code != 0:
        print("\n🚨 Watchdog Alert:")
        for iss in issues:
            print(f"  - {iss}")
        print(
            "\nRemediation: Verify model configuration, rotate credentials if needed, "
            "restart gateways, and investigate session storage path."
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
