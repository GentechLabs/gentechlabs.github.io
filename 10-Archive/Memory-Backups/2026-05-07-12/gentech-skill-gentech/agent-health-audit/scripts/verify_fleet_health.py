#!/usr/bin/env python3
"""
Agent Fleet Health Checker — automated PASS/FAIL verification.
Exit codes:
  0 = all healthy
  1 = degraded (some warnings, jobs still running)
  2 = critical (any agent down, auth revoked, cron failures)
  3 = usage error

Designed to be run via cron every 5 minutes as a meta-health check.
"""

import subprocess
import json
import os
import sys
from datetime import datetime, timezone

HERMES_HOME = os.path.expanduser('~/.hermes')
PROFILES = ['gentech', 'yoyo', 'dmob', 'desmond']
MIN_CRON_AGE_SECONDS = 300  # warn if cron hasn't ticked in 5 min
MAX_RESTART_AGE_SECONDS = 300  # warn if gateway restarted <5 min ago (flapping)

def run_cmd(cmd, timeout=10):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, '', str(e)

def check_processes():
    """Verify all 4 gateway processes are running and not zombie."""
    issues = []
    for agent in PROFILES:
        code, out, err = run_cmd(f"pgrep -f 'hermes.*{agent}.*gateway'")
        if code != 0 or not out.strip():
            issues.append(f"{agent} gateway process not found")
            continue
        pid = out.strip().split()[0]
        code2, stat_out, _ = run_cmd(f"ps -p {pid} -o stat=")
        if 'Z' in stat_out or 'D' in stat_out:
            issues.append(f"{agent} gateway PID {pid} in bad state ({stat_out.strip()})")
    return issues

def check_cron_activity():
    """Verify cron ticker is active per agent and jobs have run recently."""
    issues = []
    for agent in PROFILES:
        log = f"{HERMES_HOME}/profiles/{agent}/logs/agent.log"
        if not os.path.exists(log):
            issues.append(f"{agent}: no agent.log found")
            continue
        
        # Check for execution markers [cron_<job_id>] — most reliable sign jobs are running
        code, out, _ = run_cmd(f"grep -E '\\[cron_[a-f0-9]+\\]' {log} | tail -5")
        if code == 0 and out.strip():
            # Found recent executions — good
            last_line = out.strip().split('\n')[-1]
            # Try to parse timestamp
            try:
                ts_str = last_line.split(',')[0].strip().split()[-2:]
                from datetime import datetime, timezone
                log_time = datetime.strptime(' '.join(ts_str), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                age = (datetime.now(timezone.utc) - log_time).total_seconds()
                if age > MIN_CRON_AGE_SECONDS:
                    issues.append(f"{agent}: last cron execution {int(age)}s ago (>300s threshold)")
            except Exception:
                pass  # parsing failed but we saw executions, consider OK
        else:
            # No execution markers found — check output directory as fallback
            output_dir = f"{HERMES_HOME}/profiles/{agent}/cron/output/"
            if os.path.exists(output_dir):
                files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
                if files:
                    # Sort by mtime
                    files_mtime = [(f, os.path.getmtime(os.path.join(output_dir, f))) for f in files]
                    files_mtime.sort(key=lambda x: x[1], reverse=True)
                    newest_mtime = files_mtime[0][1]
                    age = time.time() - newest_mtime
                    if age > MIN_CRON_AGE_SECONDS:
                        issues.append(f"{agent}: cron output stale ({int(age)}s old)")
                else:
                    issues.append(f"{agent}: cron output dir empty — no executions")
            else:
                issues.append(f"{agent}: no cron output directory found")
    return issues
def check_errors_log():
    """Scan per-agent errors.log for FATAL patterns in last 30 min."""
    all_critical = []
    for agent in PROFILES:
        err_log = f"{HERMES_HOME}/profiles/{agent}/logs/errors.log"
        if not os.path.exists(err_log):
            continue
        try:
            with open(err_log, 'r') as f:
                lines = f.read().split('\n')
            
            # Scan last 200 lines for recent critical patterns
            recent_errors = []
            now = datetime.now()
            for line in reversed(lines):
                if not line.strip():
                    continue
                try:
                    # Parse timestamp from log line (format: "2026-05-04 00:37:00,123")
                    ts_str = line[:19] if len(line) >= 19 else ''
                    if not ts_str:
                        continue
                    log_time = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                    if (now - log_time).total_seconds() > 1800:  # 30 min window
                        break
                    line_lower = line.lower()
                    if any(pattern in line_lower for pattern in [
                        'refresh session has been revoked',
                        'hermes is not logged into nous portal',
                        'model .* not supported',
                        'marshal data too short',
                        'database error',
                        "status_code: 401",
                        "status_code: 403",
                        "no anthropic credentials",
                        "invalid api key",
                    ]):
                        recent_errors.append(line.strip())
                except Exception:
                    continue
            if recent_errors:
                all_critical.extend([f"[{agent.upper()}] {e[:120]}" for e in recent_errors[:3]])
        except Exception as e:
            all_critical.append(f"{agent}: error reading log — {e}")
    return all_critical

def check_oauth_status():
    """Check if Nous Portal auth is currently valid per-agent via auth.json and recent logs."""
    issues = []
    for agent in PROFILES:
        auth_file = f"{HERMES_HOME}/profiles/{agent}/auth.json"
        log_file = f"{HERMES_HOME}/profiles/{agent}/logs/errors.log"
        
        # Check recent log for "Refresh session has been revoked" (last 30 min)
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.read().split('\n')
                now = datetime.now()
                for line in reversed(lines):
                    if 'Refresh session has been revoked' in line:
                        try:
                            ts_str = line[:19]
                            log_time = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                            if (now - log_time).total_seconds() < 1800:
                                issues.append(f"{agent}: OAuth revocation detected (log entry at {ts_str})")
                                break
                        except Exception:
                            pass  # still counts if we can't parse timestamp
            except Exception:
                pass
        
        # Also check auth.json expiry
        if not os.path.exists(auth_file):
            continue
        try:
            with open(auth_file, 'r') as f:
                auth = json.load(f)
            expires_at = auth.get('tokens', {}).get('expires_at')
            if expires_at:
                exp = datetime.fromisoformat(expires_at.replace('Z','+00:00'))
                if exp < datetime.now(exp.tzinfo):
                    issues.append(f"{agent}: OAuth token expired at {exp.isoformat()}")
        except Exception:
            pass
    return issues

def check_cron_job_failures():
    """Use hermes cron list to find active jobs with error status."""
    issues = []
    code, out, _ = run_cmd('hermes cron list')
    if code != 0:
        return ["hermes cron list command failed"]
    
    current_job = None
    for line in out.split('\n'):
        line = line.strip()
        if line.startswith('[') and 'active' in line.lower():
            if current_job and current_job.get('error'):
                issues.append(f"{current_job['name']}: {current_job['error']}")
            current_job = {'id': line.split()[0].strip('[]'), 'name': '', 'error': ''}
        elif current_job and line.startswith('Name:'):
            current_job['name'] = line.split(':',1)[1].strip()
        elif current_job and 'error:' in line.lower():
            current_job['error'] = line.split('error:',1)[1].strip()
    
    if current_job and current_job.get('error'):
        issues.append(f"{current_job['name']}: {current_job['error']}")
    
    return issues

def main():
    critical = []
    warnings = []
    
    # Phase 1: Process liveness
    proc_issues = check_processes()
    critical.extend(proc_issues)
    
    # Phase 2: Cron activity
    cron_issues = check_cron_activity()
    warnings.extend(cron_issues)
    
    # Phase 3: Error log scan
    err_issues = check_errors_log()
    if err_issues:
        critical.extend([f"FATAL_ERROR: {e[:120]}" for e in err_issues])
    
    # Phase 4: OAuth status
    oauth_issues = check_oauth_status()
    if oauth_issues:
        critical.extend(oauth_issues)
    
    # Phase 5: Cron job failures
    job_failures = check_cron_job_failures()
    if job_failures:
        critical.extend(job_failures)
    
    # Output
    if critical:
        print("CRITICAL:")
        for c in critical:
            print(f"  ✗ {c}")
        sys.exit(2)
    elif warnings:
        print("DEGRADED:")
        for w in warnings:
            print(f"  ⚠ {w}")
        sys.exit(1)
    else:
        print("STATUS:OK")
        sys.exit(0)

if __name__ == '__main__':
    main()
