#!/usr/bin/env python3
"""
Quick diagnostic for D5 Milestone cron job health.
Checks: gateway status, job active, credentials, state freshness, last run result.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

def sh(cmd):
    """Run shell command, return output or empty string."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() + "\n" + result.stderr.strip()
    except Exception as e:
        return str(e)

def main():
    print("═" * 60)
    print("  D5 Milestone Cron Diagnostic")
    print("═" * 60)

    # 1. Gateway status
    print("\n[1] Gateway status:")
    gateway_out = sh("hermes status")
    if "Gateway is running" in gateway_out:
        print("  ✅ Gateway running")
        # Extract PIDs
        for line in gateway_out.splitlines():
            if "PID:" in line:
                print(f"     {line.strip()}")
    else:
        print("  ❌ Gateway NOT running or not detected")
        print(gateway_out[:200])

    # 2. Job list
    print("\n[2] Cron job list:")
    cron_list = sh("hermes cron list")
    if "Defi Milestone" in cron_list:
        print("  ✅ 'Defi Milestone' job found")
        # Extract job ID and status
        for line in cron_list.splitlines():
            if "Defi Milestone" in line or ("active" in line and "3fc1a11a88d7" in line):
                print(f"     {line.strip()}")
    else:
        print("  ❌ 'Defi Milestone' job NOT found in list")

    # 3. Anthropic credentials
    print("\n[3] Anthropic credentials:")
    anth_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_TOKEN")
    if anth_key:
        print("  ✅ ANTHROPIC_API_KEY set (masked)")
    else:
        print("  ⚠️  ANTHROPIC_API_KEY not set in environment")

    # 4. State file freshness
    print("\n[4] State file freshness:")
    state_path = os.path.expanduser("~/.hermes/scripts/.lfj-aae-state.json")
    if os.path.exists(state_path):
        mtime = os.path.getmtime(state_path)
        age = (datetime.now().timestamp() - mtime) / 3600
        last_check = "unknown"
        try:
            with open(state_path) as f:
                state = json.load(f)
                last_check = state.get("last_check", "N/A")
        except Exception:
            pass
        print(f"  State file: {state_path}")
        print(f"  Last modified: {age:.1f}h ago")
        print(f"  Last check field: {last_check}")
    else:
        print("  ❌ State file not found")

    # 5. Script presence
    print("\n[5] Required scripts:")
    scripts = [
        "d5-master-cron.py",
        "d5-milestone-summary.py",
        "lp-position-reader.py",
    ]
    scripts_dir = os.path.expanduser("~/.hermes/profiles/dmob/home/.hermes/profiles/gentech/scripts/")
    # Also check vault location
    vault_dir = "/root/vaults/gentech/03-Strategies/scripts/"
    for script in scripts:
        vault_path = os.path.join(vault_dir, script)
        hermes_path = os.path.join(scripts_dir, script)
        if os.path.exists(vault_path):
            print(f"  ✅ {script} (vault: {vault_path})")
        elif os.path.exists(hermes_path):
            print(f"  ✅ {script} (hermes: {hermes_path})")
        else:
            print(f"  ❌ {script} NOT FOUND")

    print("\n" + "═" * 60)
    print("  Diagnostic complete")
    print("═" * 60)

if __name__ == "__main__":
    main()
