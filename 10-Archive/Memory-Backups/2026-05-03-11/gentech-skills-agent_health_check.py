#!/usr/bin/env python3
"""
Agent Health Check Script — run from host to verify all agent gateways.
Returns exit code 0 if all healthy, 1 if any issues detected.
Prints concise status table.
"""

import subprocess
import json
import os
import sys
from datetime import datetime, timedelta

AGENTS = ['yoyo', 'dmob', 'desmond', 'gentech']
HERMES_ROOT = '/root/.hermes/profiles'

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def check_processes():
    """Check if gateway processes are running."""
    result = run('ps aux')
    found = {}
    for agent in AGENTS:
        found[agent] = [l for l in result.stdout.split('\n') 
                       if agent in l.lower() and 'gateway' in l.lower()]
    return found

def check_systemd():
    """Check systemd --user service status."""
    status = {}
    for agent in AGENTS:
        r = run(f'systemctl --user status hermes-gateway-{agent}.service')
        status[agent] = r.stdout.strip().split('\n')[0] if r.returncode == 0 else 'inactive/unknown'
    return status

def check_gateway_state(agent):
    """Read gateway_state.json and extract key fields."""
    path = f'{HERMES_ROOT}/{agent}/gateway_state.json'
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            s = json.load(f)
        return {
            'gateway_state': s.get('gateway_state'),
            'pid': s.get('pid'),
            'telegram_state': s.get('platforms', {}).get('telegram', {}).get('state'),
            'updated_at': s.get('updated_at')
        }
    except Exception:
        return None

def check_cron_lock_age(agent):
    """Return age of .tick.lock or None."""
    path = f'{HERMES_ROOT}/{agent}/cron/.tick.lock'
    if not os.path.exists(path):
        return None
    age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(path))
    return age

def check_recent_errors(agent):
    """Scan agent.log and gateway.log for error keywords."""
    errors = []
    for logname in ['agent.log', 'gateway.log']:
        path = f'{HERMES_ROOT}/{agent}/logs/{logname}'
        if os.path.exists(path):
            try:
                with open(path) as f:
                    lines = f.readlines()[-100:]
                for line in lines:
                    if 'error' in line.lower():
                        errors.append(line.strip())
            except:
                pass
    return errors[-3:] if errors else []

def main():
    print("\n=== AGENT HEALTH CHECK ===\n")
    proc_map = check_processes()
    systemd_map = check_systemd()
    
    issues = []
    
    for agent in AGENTS:
        procs = proc_map[agent]
        systemd_line = systemd_map[agent]
        state = check_gateway_state(agent)
        lock_age = check_cron_lock_age(agent)
        errors = check_recent_errors(agent)
        
        # Determine status
        gateway_running = len(procs) > 0
        systemd_active = 'active' in systemd_line.lower()
        
        print(f"{agent.upper():8s} | ", end='')
        if gateway_running and systemd_active:
            print(f"✓ ONLINE  | ", end='')
        elif gateway_running and not systemd_active:
            print(f"⚠ PROC OK | ", end='')
        elif not gateway_running and systemd_active:
            print(f"✗ SYSTEMD | ", end='')
        else:
            print(f"✗ OFFLINE | ", end='')
            issues.append(f'{agent}: gateway down')
        
        # Telegram state if available
        if state:
            tg = state.get('telegram_state', '?')
            print(f"Telegram: {tg:8s} | ", end='')
        else:
            print(f"Telegram: ?      | ", end='')
        
        # Cron lock age
        if lock_age:
            if lock_age < timedelta(seconds=90):
                print(f"cron: fresh")
            else:
                print(f"cron: STALE ({lock_age})")
                issues.append(f'{agent}: stale cron lock')
        else:
            print(f"cron: n/a")
        
        # Show last error if any
        if errors:
            print(f"         Last error: {errors[-1][:80]}")
        else:
            print()
    
    print("\n=== ISSUES DETECTED ===")
    if issues:
        for issue in issues:
            print(f"  ✗ {issue}")
        print("\nRecovery: see agent-coordination skill section 'Agent Health Check & Recovery Protocol'")
        sys.exit(1)
    else:
        print("  ✓ All agents healthy")
        sys.exit(0)

if __name__ == '__main__':
    main()
