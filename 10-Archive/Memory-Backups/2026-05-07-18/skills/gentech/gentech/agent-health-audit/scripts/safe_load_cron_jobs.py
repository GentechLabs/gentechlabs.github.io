#!/usr/bin/env python3
"""
safe_load_cron_jobs.py — Safely parse Hermes cron jobs.json files.

Hermes cron jobs are stored as: {"jobs": [...], "updated_at": "..."}
NOT as a bare JSON array. This helper guards against TypeError
when code mistakenly treats the dict as a list.

Usage:
  python3 safe_load_cron_jobs.py /root/.hermes/profiles/gentech/cron/jobs.json
  python3 safe_load_cron_jobs.py /path/to/jobs.json --count
  python3 safe_load_cron_jobs.py /path/to/jobs.json --validate
"""

import json
import sys
from pathlib import Path


def load_jobs(path: str):
    """Return the jobs list from a Hermes cron jobs.json file."""
    with open(path, 'r') as f:
        data = json.load(f)

    if isinstance(data, dict) and 'jobs' in data:
        return data['jobs']
    elif isinstance(data, list):
        # Legacy format (unlikely but handle gracefully)
        return data
    else:
        raise ValueError(f"Unexpected jobs.json structure: {type(data)} with keys {list(data.keys()) if hasattr(data, 'keys') else 'N/A'}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    path = sys.argv[1]
    try:
        jobs = load_jobs(path)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(4)

    # Handle flags
    if '--count' in sys.argv:
        print(len(jobs))
        sys.exit(0)

    if '--validate' in sys.argv:
        # Check structure of each job
        required = ['name', 'schedule', 'enabled']
        ok = True
        for i, job in enumerate(jobs):
            missing = [k for k in required if k not in job]
            if missing:
                print(f"Job {i} ({job.get('name', 'unnamed')}) missing keys: {missing}")
                ok = False
        if ok:
            print(f"All {len(jobs)} jobs have required fields.")
        sys.exit(0 if ok else 1)

    # Default: print summary
    print(f"Total jobs: {len(jobs)}")
    for i, job in enumerate(jobs[:10]):
        name = job.get('name', 'unnamed')
        enabled = job.get('enabled', '?')
        sched = job.get('schedule', {})
        print(f"  [{i}] {name} — enabled={enabled} — schedule={sched}")
    if len(jobs) > 10:
        print(f"  ... and {len(jobs) - 10} more")


if __name__ == '__main__':
    main()
