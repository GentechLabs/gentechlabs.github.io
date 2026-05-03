#!/usr/bin/env python3
"""Agent Fleet Health Verification Script — exit codes: 0=OK, 1=degraded, 2=critical

Quick, deterministic health probe suitable for cron execution every 5 minutes.
Checks gateway processes, recent error rates, and TTS credential validity.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

AGENTS = ['yoyo', 'dmob', 'desmond', 'gentech']
ERROR_LOG_DIR = '/root/.hermes/profiles/{}/logs/errors.log'
STATUS_FILE = '/tmp/.watchdog_last_status.json'

def run(cmd, timeout=5):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, '', str(e)

def check_processes():
    """Return dict of agent -> (running, pid)"""
    result = {}
    for agent in AGENTS:
        code, out, _ = run(f'pgrep -f "hermes.*{agent}.*gateway"')
        pids = [p for p in out.strip().split('\n') if p]
        if pids:
            # Verify each PID is still live
            living = []
            for pid in pids:
                code2, _, _ = run(f'ps -p {pid} -o pid=')
                if code2 == 0 and _.strip():
                    living.append(int(pid))
            result[agent] = (bool(living), living[0] if living else None)
        else:
            result[agent] = (False, None)
    return result

def check_recent_errors(agent, minutes=5):
    """Count error lines in last N minutes."""
    log = ERROR_LOG_DIR.format(agent)
    if not os.path.exists(log):
        return -1  # missing = critical
    
    # Get current time in log's timezone (UTC)
    now = datetime.now(timezone.utc)
    cutoff = now.timestamp() - minutes * 60
    
    count = 0
    try:
        with open(log, 'r') as f:
            # Seek from end and work backwards to avoid reading entire file
            f.seek(0, os.SEEK_END)
            block_size = 4096
            buffer = ''
            while f.tell() > 0 and count == 0:
                to_read = min(block_size, f.tell())
                f.seek(f.tell() - to_read)
                buffer = f.read(to_read) + buffer
                # Count lines with timestamps within window
                for line in buffer.split('\n'):
                    if line.startswith('2026-05-02'):
                        try:
                            ts_str = line[:19]
                            ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()
                            if ts >= cutoff:
                                count += 1
                        except ValueError:
                            continue
                # Trim to last 10k chars to keep memory bounded
                if len(buffer) > 10000:
                    buffer = buffer[-10000:]
    except Exception as e:
        return -1
    return count

def check_elevenlabs_key():
    """Quick validation: return True if key format looks valid and endpoint responds."""
    key = os.environ.get('ELEVENLABS_API_KEY') or os.popen('grep ELEVENLABS_API_KEY /root/.hermes/profiles/gentech/.env 2>/dev/null | cut -d= -f2').read().strip()
    if not key or len(key) < 30:
        return False
    code, out, _ = run(f'curl -s -H "xi-api-key: {key}" https://api.elevenlabs.io/v1/user', timeout=10)
    if code != 0:
        return False
    return 'invalid_api_key' not in out and 'missing_permissions' not in out

def main():
    alerts = []
    score = 0  # 0=ok, 1=degraded, 2=critical

    # 1. Process liveness
    procs = check_processes()
    for agent, (up, pid) in procs.items():
        if not up:
            alerts.append(f"[CRITICAL] {agent} gateway process not running (PID={pid})")
            score = max(score, 2)

    # 2. Recent error rate (>10 errors in 5 min = degraded; >50 = critical)
    for agent in AGENTS:
        err_count = check_recent_errors(agent, minutes=5)
        if err_count == -1:
            alerts.append(f"[CRITICAL] {agent} error log missing or unreadable")
            score = max(score, 2)
        elif err_count > 50:
            alerts.append(f"[CRITICAL] {agent} {err_count} errors in last 5 min")
            score = max(score, 2)
        elif err_count > 10:
            alerts.append(f"[DEGRADED] {agent} {err_count} errors in last 5 min")
            score = max(score, 1)

    # 3. TTS credential check (sample one agent's key)
    if not check_elevenlabs_key():
        alerts.append("[CRITICAL] ElevenLabs API key invalid or uncontactable; TTS broken fleet-wide")
        score = max(score, 2)

    # 4. Cron execution check (verify watchdog itself ran recently)
    # Look for last successful Watchdog run in Hermes session index
    # This is a simplified check; in production read cron history
    code, out, _ = run('hermes cron list | grep -A 1 "Gentech Watchdog"')
    if code == 0 and 'ok' not in out:
        alerts.append("[DEGRADED] Watchdog cron last run not marked 'ok'")
        score = max(score, 1)

    # Output
    print(f"Health check complete — score={score}")
    for a in alerts:
        print(a)
    
    # Persist last status for trend tracking
    with open(STATUS_FILE, 'w') as f:
        json.dump({'timestamp': datetime.now(timezone.utc).isoformat(), 'score': score, 'alerts': alerts}, f)
    
    return 0 if score == 0 else (1 if score == 1 else 2)

if __name__ == '__main__':
    sys.exit(main())
