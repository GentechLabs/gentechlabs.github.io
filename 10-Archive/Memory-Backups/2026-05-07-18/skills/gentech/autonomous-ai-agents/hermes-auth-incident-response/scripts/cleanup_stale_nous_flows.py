#!/usr/bin/env python3
"""
Cleanup stale Nous OAuth device flow files.

This script removes expired pending device flow state files that may accumulate
if a device authorization flow was initiated but never completed by a human.

Usage:
  cleanup_stale_nous_flows.py [--dry-run] [--max-age-minutes 10]

Without --dry-run, the script permanently deletes stale flow files.
With --dry-run, it only reports what would be deleted.

Files removed:
  - $HERMES_HOME/auth_pending_device_flow.json
  - $HERMES_HOME/scripts/pending_nous_device_flow_latest.json (symlink)

A file is considered stale if it is older than --max-age-minutes (default 10).
Device flow codes expire after ~10 minutes; any pending flow older than that
is definitely expired andsafe to clean up.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

def get_hermes_home() -> Path:
    """Resolve HERMES_HOME to canonical path."""
    hermes_home = os.environ.get("HERMES_HOME")
    if not hermes_home:
        # Fallback to known canonical location for Gentech
        hermes_home = "/root/.hermes/profiles/gentech"
    return Path(hermes_home).resolve()

def is_stale(filepath: Path, max_age_seconds: int) -> bool:
    """Check if file is older than max_age_seconds."""
    if not filepath.exists():
        return False
    age = time.time() - filepath.stat().st_mtime
    return age > max_age_seconds

def format_age(seconds: float) -> str:
    """Pretty-print age in human-readable format."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m"
    else:
        return f"{int(seconds/3600)}h"

def main():
    parser = argparse.ArgumentParser(description="Cleanup stale Nous device flow files")
    parser.add_argument("--dry-run", action="store_true", help="Only report, do not delete")
    parser.add_argument("--max-age-minutes", type=int, default=10,
                        help="Files older than this are considered stale (default: 10)")
    args = parser.parse_args()

    hermes_home = get_hermes_home()
    max_age_seconds = args.max_age_minutes * 60

    targets = [
        hermes_home / "auth_pending_device_flow.json",
        hermes_home / "scripts" / "pending_nous_device_flow_latest.json",
    ]

    print(f" HERMES_HOME: {hermes_home}")
    print(f" Max age: {args.max_age_minutes} minutes")
    print(f" Dry run: {args.dry_run}")
    print()

    any_stale = False
    for target in targets:
        if not target.exists():
            print(f" [SKIP] {target} — not found")
            continue

        if is_stale(target, max_age_seconds):
            any_stale = True
            age_sec = time.time() - target.stat().st_mtime
            print(f" [STALE] {target} (age: {format_age(age_sec)})")
            if not args.dry_run:
                try:
                    target.unlink()
                    print(f" [DELETED] {target}")
                except Exception as e:
                    print(f" [ERROR] Failed to delete {target}: {e}")
        else:
            age_sec = time.time() - target.stat().st_mtime
            print(f" [FRESH] {target} (age: {format_age(age_sec)})")

    print()
    if any_stale and not args.dry_run:
        print(" Cleanup complete — stale flows removed.")
    elif any_stale and args.dry_run:
        print(" Dry-run complete — stale flows WOULD be removed (use without --dry-run to execute).")
    else:
        print(" No stale flows found.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
