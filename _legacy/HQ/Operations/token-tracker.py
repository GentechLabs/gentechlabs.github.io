#!/usr/bin/env python3
"""
Token Usage Tracker for Gentech Multi-Agent System
Tracks token consumption per agent to measure Option 1 routing efficiency.

Usage:
  python3 token-tracker.py log --agent gentech --tokens 1500 --task "routed to DMOB"
  python3 token-tracker.py report --days 7
  python3 token-tracker.py baseline
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "/root/vaults/gentech"))
TRACKER_DIR = VAULT_PATH / "00-HQ" / "Usage"
LOG_FILE = TRACKER_DIR / "token-usage-log.jsonl"
BASELINE_FILE = TRACKER_DIR / "token-baseline.json"


def log_usage(agent: str, tokens: int, task: str = "", group: str = "hq"):
    """Log a token usage entry."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "tokens": tokens,
        "task": task,
        "group": group,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Logged: {agent} used {tokens} tokens for '{task}'")


def report(days: int = 7):
    """Generate a usage report for the last N days."""
    if not LOG_FILE.exists():
        print("No usage data found. Run 'log' commands first.")
        return

    cutoff = datetime.utcnow() - timedelta(days=days)
    entries = []
    with open(LOG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts >= cutoff:
                entries.append(entry)

    if not entries:
        print(f"No usage data in the last {days} days.")
        return

    # Aggregate by agent
    agent_totals = {}
    agent_counts = {}
    for e in entries:
        agent = e["agent"]
        agent_totals[agent] = agent_totals.get(agent, 0) + e["tokens"]
        agent_counts[agent] = agent_counts.get(agent, 0) + 1

    total_tokens = sum(agent_totals.values())

    print(f"\n{'='*60}")
    print(f"  Token Usage Report — Last {days} Days")
    print(f"  Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")

    print(f"{'Agent':<15} {'Tokens':<12} {'% of Total':<12} {'Activations':<12}")
    print(f"{'-'*15} {'-'*12} {'-'*12} {'-'*12}")

    for agent in sorted(agent_totals, key=agent_totals.get, reverse=True):
        tokens = agent_totals[agent]
        pct = (tokens / total_tokens * 100) if total_tokens > 0 else 0
        count = agent_counts[agent]
        print(f"{agent:<15} {tokens:<12,} {pct:<11.1f}% {count:<12}")

    print(f"{'-'*15} {'-'*12} {'-'*12} {'-'*12}")
    print(f"{'TOTAL':<15} {total_tokens:<12,} {'100.0':<11}% {sum(agent_counts.values()):<12}")

    # Check baseline comparison
    if BASELINE_FILE.exists():
        with open(BASELINE_FILE) as f:
            baseline = json.load(f)
        baseline_daily = baseline.get("daily_avg_tokens", 0)
        current_daily = total_tokens / days if days > 0 else 0
        if baseline_daily > 0:
            reduction = (1 - current_daily / baseline_daily) * 100
            print(f"\n📊 Baseline Comparison:")
            print(f"   Baseline daily avg: {baseline_daily:,.0f} tokens")
            print(f"   Current daily avg:  {current_daily:,.0f} tokens")
            print(f"   Reduction:          {reduction:.1f}%")
            if reduction > 0:
                print(f"   ✅ Token savings detected!")
            else:
                print(f"   ⚠️  Usage increased — review routing efficiency")


def set_baseline():
    """Set current usage as the baseline for comparison."""
    if not LOG_FILE.exists():
        print("No usage data found. Run 'log' commands first.")
        return

    entries = []
    with open(LOG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))

    if not entries:
        print("No entries to baseline.")
        return

    # Calculate daily average from available data
    timestamps = [datetime.fromisoformat(e["timestamp"]) for e in entries]
    date_range = (max(timestamps) - min(timestamps)).days + 1
    total_tokens = sum(e["tokens"] for e in entries)
    daily_avg = total_tokens / max(date_range, 1)

    baseline = {
        "date": datetime.utcnow().isoformat(),
        "total_tokens": total_tokens,
        "days_of_data": date_range,
        "daily_avg_tokens": daily_avg,
        "entry_count": len(entries),
    }

    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=2)

    print(f"Baseline set:")
    print(f"  Total tokens: {total_tokens:,}")
    print(f"  Days of data: {date_range}")
    print(f"  Daily average: {daily_avg:,.0f} tokens")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "log" and len(sys.argv) >= 4:
        agent = sys.argv[2]
        tokens = int(sys.argv[3])
        task = sys.argv[4] if len(sys.argv) > 4 else ""
        group = sys.argv[5] if len(sys.argv) > 5 else "hq"
        log_usage(agent, tokens, task, group)

    elif cmd == "report":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        report(days)

    elif cmd == "baseline":
        set_baseline()

    else:
        print(__doc__)
        sys.exit(1)
