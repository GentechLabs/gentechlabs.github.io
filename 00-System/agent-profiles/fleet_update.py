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
    # Use the systemd unit when it exists (reliable, no duplicate spawn).
    code, out = run(f"systemctl --user restart hermes-gateway-{profile}.service 2>&1", timeout=60)
    if code != 0 or "Failed" in out or "not" in out:
        # fall back to the CLI restart
        code, out = run(f"hermes gateway restart --profile {profile} 2>&1", timeout=60)
    return code, out.strip()


def current_profile():
    """Determine which profile's gateway is running THIS script, by walking the
    parent-process chain up to the hermes gateway process. Returns the profile
    name, or None if we can't tell (e.g. run from a plain shell)."""
    import os
    pid = os.getppid()
    for _ in range(12):
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmd = f.read().decode(errors="ignore").replace("\x00", " ").strip()
            if "gateway run" in cmd:
                for p in PROFILES:
                    if f"--profile {p}" in cmd or f"profile {p}" in cmd or f"/{p}" in cmd:
                        return p
                # systemd unit name also encodes the profile
                if "hermes-gateway" in cmd:
                    for p in PROFILES:
                        if p in cmd:
                            return p
                return None
        except FileNotFoundError:
            return None
        # walk up
        try:
            with open(f"/proc/{pid}/stat") as f:
                parts = f.read().split()
                pid = int(parts[3])
        except (FileNotFoundError, ValueError, IndexError):
            return None
    return None


def restart_current_detached(profile):
    """Restart the CURRENT profile's gateway in a detached session so it survives
    the script being killed by its own gateway restart. Runs ~3s after exit."""
    import subprocess
    script = (
        "sleep 3 && "
        f"systemctl --user restart hermes-gateway-{profile}.service"
    )
    subprocess.Popen(["bash", "-c", script], start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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

    # Detect which profile is running this script (so we don't kill ourselves).
    runner = current_profile()
    if runner:
        print(f"Running inside gateway for profile: {runner}")
    else:
        print("Not running inside a gateway (standalone shell) — restarting all.")
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
    # Restart every profile EXCEPT the one running this script first.
    others = [p for p in PROFILES if p != runner]
    for p in others:
        code, out = restart_gateway(p)
        status = "✅" if code == 0 else "❌"
        print(f"  {status} {p}: {out[:200]}")
        time.sleep(2)  # stagger restarts

    # Restart the current profile LAST, detached, so the script survives.
    if runner:
        print(f"  ⏳ {runner} (current): queued for detached restart after script exits")
        restart_current_detached(runner)

    print()
    print("--- Post-restart state (other profiles) ---")
    for p in others:
        print(f"  {p}: {gateway_pid(p)}")
    if runner:
        print(f"  {runner}: restarting now in a detached session — will be back on new code shortly")

    print()
    print("Fleet update complete. All gateways restarting on new code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
