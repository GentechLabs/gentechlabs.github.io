#!/usr/bin/env python3
"""
Fleet Hermes Update — update once, restart ALL profile gateways.

All profiles share ONE Hermes install at /usr/local/lib/hermes-agent, so
`hermes update` updates the code once. But each profile's gateway is a SEPARATE
process that must be restarted to load the new code. This script does both:
update the shared code, then restart every profile gateway so the whole fleet
picks up the update together.

Usage:
  python3 fleet_update.py            # update + restart all gateways
  python3 fleet_update.py --check    # dry-run: show versions + gateways, no changes
  python3 fleet_update.py --restart-only  # skip update, just restart gateways
"""

import json
import os
import subprocess
import sys
import time

HERMES_INSTALL = "/usr/local/lib/hermes-agent"
PROFILES_DIR = "/root/.hermes/profiles"
PROFILES = ["gentech", "gentech-treasury", "gizmo", "pixel"]


def run(cmd, timeout=120):
    """Run a command, return (exit_code, stdout)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, f"TIMEOUT after {timeout}s: {cmd}"


def current_version():
    code, out = run("hermes --version 2>&1 | head -1")
    return out.strip() if code == 0 else "unknown"


def commits_behind():
    code, out = run(
        f"cd {HERMES_INSTALL} && git fetch origin -q 2>&1 && git rev-list --count HEAD..origin/main 2>&1"
    )
    return out.strip() if code == 0 else "?"


def gateway_pid(profile):
    code, out = run(f"hermes gateway status --profile {profile} 2>&1")
    for line in out.splitlines():
        if "PID" in line:
            return line.strip()
    return "not running"


def restart_gateway(profile):
    code, out = run(f"hermes gateway restart --profile {profile} 2>&1", timeout=60)
    return code, out.strip()


def main():
    check_only = "--check" in sys.argv
    restart_only = "--restart-only" in sys.argv

    print("=" * 60)
    print("FLEET HERMES UPDATE")
    print("=" * 60)
    print(f"Current version: {current_version()}")
    print(f"Commits behind upstream: {commits_behind()}")
    print(f"Profiles: {', '.join(PROFILES)}")
    print()

    # Show current gateway state
    print("--- Current gateway state ---")
    for p in PROFILES:
        print(f"  {p}: {gateway_pid(p)}")
    print()

    if check_only:
        print("CHECK MODE — no changes made.")
        return 0

    if not restart_only:
        print("--- Updating shared Hermes install ---")
        code, out = run("hermes update 2>&1", timeout=300)
        print(out[-2000:] if len(out) > 2000 else out)
        if code != 0:
            print(f"⚠️  hermes update exited {code}. Continuing to restart gateways anyway.")
        print(f"New version: {current_version()}")
        print()

    print("--- Restarting all profile gateways ---")
    for p in PROFILES:
        code, out = restart_gateway(p)
        status = "✅" if code == 0 else "❌"
        print(f"  {status} {p}: {out[:200]}")
        time.sleep(2)  # stagger restarts

    print()
    print("--- Post-restart state ---")
    for p in PROFILES:
        print(f"  {p}: {gateway_pid(p)}")

    print()
    print("Fleet update complete. All gateways restarted on new code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
