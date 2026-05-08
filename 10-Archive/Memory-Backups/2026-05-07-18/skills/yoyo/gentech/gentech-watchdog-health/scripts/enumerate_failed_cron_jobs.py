#!/usr/bin/env python3
"""
enumerate_failed_cron_jobs.py — Rapid diagnostic for systemic cron failures across Gentech agent fleet.

Scans agent.log files for all profiles and counts:
  - Failed cron job occurrences (Job 'X' failed)
  - 401 authentication errors (indicator of OAuth cascade)
  - Nous Portal auth revocation ("Refresh session has been revoked")
  - "Hermes is not logged into Nous Portal" errors

Output:
  A sorted table of failed job names with counts, plus per-agent auth failure tallies.

Usage:
  python3 enumerate_failed_cron_jobs.py [--log-dir /path/to/logs]

If --log-dir is omitted, defaults to /root/.hermes/profiles.
"""

import argparse
import os
import re
from collections import Counter

DEFAULT_PROFILES = ['yoyo', 'dmob', 'desmond', 'gentech']
DEFAULT_BASE = '/root/.hermes/profiles'

# Patterns that indicate systemic auth failure across the fleet
AUTH_FAILURE_PATTERNS = [
    re.compile(r'Refresh session has been revoked', re.IGNORECASE),
    re.compile(r'Hermes is not logged into Nous Portal', re.IGNORECASE),
    re.compile(r'Error code: 401', re.IGNORECASE),  # ElevenLabs/OpenAI 401s
]

def main():
    parser = argparse.ArgumentParser(description='Aggregate cron failure metrics across Gentech agents')
    parser.add_argument('--log-dir', default=DEFAULT_BASE, help='Base directory containing agent profile logs')
    args = parser.parse_args()

    base = args.log_dir
    failed_job_counter = Counter()
    agent_401_counter = Counter()
    agent_auth_failure_counter = Counter()
    agent_total_errors = Counter()

    for profile in DEFAULT_PROFILES:
        log_path = os.path.join(base, profile, 'logs', 'agent.log')
        if not os.path.isfile(log_path):
            print(f"WARNING: No agent.log for {profile} at {log_path}")
            continue
        try:
            with open(log_path, 'r', errors='replace') as f:
                content = f.read()
            lines = content.split('\n')
            # Count Job 'X' failed
            for line in lines:
                m = re.search(r"Job '([^']+)' failed", line)
                if m:
                    job = m.group(1)
                    failed_job_counter[job] += 1
                if re.search(r'401', line):
                    agent_401_counter[profile] += 1
                if any(p.search(line) for p in AUTH_FAILURE_PATTERNS):
                    agent_auth_failure_counter[profile] += 1
                if re.search(r'ERROR', line, re.IGNORECASE):
                    agent_total_errors[profile] += 1
        except Exception as e:
            print(f"ERROR reading {log_path}: {e}")

    print("\n=== Failed Cron Jobs (all agents combined) ===")
    if failed_job_counter:
        for job, count in failed_job_counter.most_common(20):
            print(f"  {job}: {count} failures")
    else:
        print("  No failed job entries found.")

    print("\n=== Auth Failure Counts per Agent ===")
    for agent in DEFAULT_PROFILES:
        count401 = agent_401_counter.get(agent, 0)
        count_auth = agent_auth_failure_counter.get(agent, 0)
        total = agent_total_errors.get(agent, 0)
        print(f"  {agent.upper()}: {count401} HTTP-401s, {count_auth} total auth failures ({total} total ERRORs)")

    # Heuristic: alert if systemic
    total_failures = sum(failed_job_counter.values())
    agents_with_401 = sum(1 for c in agent_401_counter.values() if c > 0)
    agents_with_auth_fail = sum(1 for c in agent_auth_failure_counter.values() if c > 0)

    print("\n=== Summary ===")
    print(f"Total failed job entries: {total_failures}")
    print(f"Agents with >0 HTTP-401 errors: {agents_with_401}/{len(DEFAULT_PROFILES)}")
    print(f"Agents with >0 auth failures (any type): {agents_with_auth_fail}/{len(DEFAULT_PROFILES)}")

    if agents_with_auth_fail >= 3:
        print("🚨 Systemic auth cascade likely: ≥3 agents showing auth failures (OAuth revoked/blocked).")
    if any(c > 100 for c in agent_auth_failure_counter.values()):
        print("🚨 High auth failure velocity detected in at least one agent — token likely revoked.")
    if agents_with_401 >= 2:
        print("ℹ️  Multiple agents showing 401 errors — check ElevenLabs/OpenAI key validity fleet-wide.")

if __name__ == '__main__':
    main()
