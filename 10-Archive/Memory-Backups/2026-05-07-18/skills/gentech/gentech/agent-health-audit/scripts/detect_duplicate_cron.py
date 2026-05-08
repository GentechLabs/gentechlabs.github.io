#!/usr/bin/env python3
"""Detect duplicate cron execution patterns in a given agent's session history.

Usage:
  python3 detect_duplicate_cron.py yoyo
  python3 detect_duplicate_cron.py --all

Outputs:
  - List of distinct job ID prefixes found in recent cron sessions
  - Average interval between executions
  - Alert if duplication likely (avg interval < expected_interval * 0.6)
  - Suggested remediation steps

Exit codes:
  0 = no duplication detected
  1 = duplication likely (needs investigation)
  2 = error (missing agent, no sessions, etc.)
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

AGENTS = ["yoyo", "dmob", "desmond", "gentech"]
HERMES_BASE = Path("/root/.hermes/profiles")

def extract_job_prefix(filename: str) -> str | None:
    """Extract the job ID prefix from a cron session filename.
    
    Filenames are like: session_cron_9ecfada01952_20260504_175032.json
    We want the hex segment right after 'session_cron_'.
    """
    m = re.match(r"session_cron_([a-f0-9]+)_", filename)
    if m:
        return m.group(1)
    return None

def analyze_agent(agent: str, expected_interval_min: int | None = None, lookback: int = 30) -> dict:
    """Analyze cron session history for a single agent.
    
    Returns a dict with stats and flags.
    """
    agent_dir = HERMES_BASE / agent / "sessions"
    if not agent_dir.exists():
        return {"error": f"Agent directory not found: {agent_dir}"}
    
    cron_sessions = sorted(
        [s for s in agent_dir.glob("session_cron_*.json")],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:lookback]
    
    if len(cron_sessions) < 2:
        return {"error": f"Insufficient cron sessions ({len(cron_sessions)}) — need 2+"}
    
    # Collect timestamps and prefixes
    records = []
    for sess in cron_sessions:
        try:
            ts = datetime.fromtimestamp(sess.stat().st_mtime, tz=timezone.utc)
            prefix = extract_job_prefix(sess.name)
            records.append({"ts": ts, "prefix": prefix, "file": sess.name})
        except Exception:
            pass
    
    records.reverse()  # chronological order
    
    # Compute intervals
    intervals = []
    for i in range(len(records) - 1):
        delta = (records[i+1]["ts"] - records[i]["ts"]).total_seconds() / 60
        intervals.append(delta)
    
    avg_interval = sum(intervals) / len(intervals)
    prefix_set = set(r["prefix"] for r in records if r["prefix"])
    
    return {
        "agent": agent,
        "sessions_analyzed": len(records),
        "avg_interval_min": round(avg_interval, 2),
        "distinct_prefixes": sorted(prefix_set),
        "prefix_count": len(prefix_set),
        "suspicious": expected_interval_min and (avg_interval < expected_interval_min * 0.6),
        "expected_interval_min": expected_interval_min,
    }

def main():
    parser = argparse.ArgumentParser(description="Detect duplicate cron executions")
    parser.add_argument("agent", nargs="?", help="Agent name (yoyo, dmob, desmond, gentech)")
    parser.add_argument("--all", action="store_true", help="Check all agents")
    parser.add_argument("--expected", type=int, help="Expected interval in minutes (for duplication check)")
    args = parser.parse_args()
    
    agents_to_check = AGENTS if args.all else ([args.agent] if args.agent else [])
    if not agents_to_check:
        print("Error: must specify agent or --all", file=sys.stderr)
        sys.exit(2)
    
    exit_code = 0
    for agent in agents_to_check:
        result = analyze_agent(agent, expected_interval_min=args.expected)
        
        print(f"\n=== {agent.upper()} ===")
        if "error" in result:
            print(f"  ERROR: {result['error']}")
            exit_code = max(exit_code, 2)
            continue
        
        print(f"  Sessions analyzed : {result['sessions_analyzed']}")
        print(f"  Avg interval       : {result['avg_interval_min']} min", end="")
        if result["expected_interval_min"]:
            print(f" (expected ~{result['expected_interval_min']})")
        else:
            print()
        print(f"  Distinct job IDs   : {result['prefix_count']} → {result['distinct_prefixes']}")
        
        if result["suspicious"]:
            print("  🚨 SUSPICIOUS: Average interval is roughly half expected — duplicate cron likely!")
            print("  Recommended: check both system crontab and internal Hermes cron registry")
            exit_code = max(exit_code, 1)
        else:
            print("  ✓ No duplication detected")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
