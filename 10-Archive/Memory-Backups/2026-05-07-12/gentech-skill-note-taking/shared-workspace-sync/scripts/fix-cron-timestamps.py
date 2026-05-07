#!/usr/bin/env python3
"""
Recalculate stale cron next_run_at timestamps across all Hermes profiles.

When a gateway restarts after downtime, cron jobs can get stuck with
next_run_at in the past. The scheduler silently skips them.
This script resets all past-due timestamps to the next valid time.

Usage:
  python3 fix-cron-timestamps.py [--profiles gentech yoyo dmob desmond]
  python3 fix-cron-timestamps.py --all-profiles
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from croniter import croniter

PROFILES = ['gentech', 'yoyo', 'dmob', 'desmond']
# Path may be in hermes-brain or in the profile directory
POSSIBLE_PATHS = [
    '/root/repos/hermes-brain/profiles/{profile}/cron/jobs.json',
    '/root/.hermes/profiles/{profile}/cron/jobs.json',
]

def find_jobs_file(profile):
    for pattern in POSSIBLE_PATHS:
        path = pattern.format(profile=profile)
        if os.path.exists(path):
            return path
    return None

def fix_timestamps(profiles, dry_run=False):
    now = datetime.now(timezone.utc)
    total_jobs = 0
    fixed_jobs = 0

    for profile in profiles:
        path = find_jobs_file(profile)
        if not path:
            print(f"⚠️  {profile}: no cron jobs file found")
            continue

        with open(path) as f:
            data = json.load(f)

        modified = False
        for job in data.get('jobs', []):
            total_jobs += 1
            next_run = job.get('next_run_at')
            if not next_run:
                continue

            try:
                next_dt = datetime.fromisoformat(next_run)
            except Exception:
                print(f"⚠️  {profile}: invalid date format in job '{job.get('name', '?')}'")
                continue

            if next_dt < now:
                # Job is past due — recalculate
                schedule = job.get('schedule', {})
                kind = schedule.get('kind', '')
                expr = schedule.get('expr', '')
                minutes = schedule.get('minutes', 60)

                if kind == 'interval':
                    # Interval job: add minutes to now
                    new_next = now + timedelta(minutes=minutes)
                elif expr:
                    # Cron expression
                    try:
                        new_next = croniter(expr, now).get_next(datetime)
                    except Exception as e:
                        print(f"⚠️  {profile}: bad cron expr '{expr}' in job '{job.get('name', '?')}': {e}")
                        continue
                else:
                    print(f"⚠️  {profile}: unknown schedule kind for job '{job.get('name', '?')}'")
                    continue

                job['next_run_at'] = new_next.isoformat()
                modified = True
                fixed_jobs += 1
                print(f"✅ {profile}: fixed '{job.get('name', '?')}' → {new_next.isoformat()}")

        if modified and not dry_run:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"   Updated {path}")
        elif dry_run and modified:
            print(f"   [DRY RUN] Would update {path}")

    print(f"\nSummary: {total_jobs} jobs scanned, {fixed_jobs} fixed")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fix stale Hermes cron timestamps")
    parser.add_argument('--profiles', nargs='+', default=PROFILES, help='Profiles to fix')
    parser.add_argument('--all-profiles', action='store_true', help='Scan all profiles from hermes-brain')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without writing')
    args = parser.parse_args()

    if args.all_profiles:
        # Discover all profile dirs
        base = '/root/repos/hermes-brain/profiles'
        if os.path.exists(base):
            profiles = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
        else:
            print("hermes-brain repo not found, using default profiles")
            profiles = PROFILES
    else:
        profiles = args.profiles

    fix_timestamps(profiles, dry_run=args.dry_run)