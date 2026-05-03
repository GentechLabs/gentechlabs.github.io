#!/usr/bin/env python3
"""
Gentech Agent Health Check — Quick diagnostic script.
Outputs one-line status per agent: OK | DEGRADED | CRITICAL | STALLED

Usage: python3 agent_health.py
"""

import os
import re
import json
import sqlite3
from datetime import datetime, timezone, timedelta

BASE = '/root/.hermes/profiles'
AGENTS = ['yoyo', 'dmob', 'desmond', 'gentech']

def get_age_seconds(filepath):
    stat = os.stat(filepath)
    return (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds()

def check_agent(agent):
    issues = []
    profile = os.path.join(BASE, agent)

    # 1. Gateway log freshness
    log = os.path.join(profile, 'logs', 'gateway.log')
    if not os.path.exists(log):
        return 'CRITICAL', ['gateway.log missing']

    age = get_age_seconds(log)
    if age > 1800:
        issues.append(f"gateway.log stale ({age/60:.0f}min)")

    # Read last 500 lines
    with open(log) as f:
        lines = f.readlines()[-500:]

    # 2. Recent errors
    errors = [l for l in lines if 'ERROR' in l or 'CRITICAL' in l]
    if errors:
        issues.append(f"{len(errors)} recent errors")

    # 3. Exceptions
    exceptions = [l for l in lines if 'Exception' in l or 'Traceback' in l]
    if exceptions:
        issues.append(f"{len(exceptions)} exceptions")

    # 4. Kanban ticker (DMOB/Desmond only)
    if agent in ('dmob', 'desmond'):
        kanban_logs = [l for l in lines if 'kanban' in l.lower()]
        if not kanban_logs:
            issues.append("kanban ticker inactive")
        else:
            # Check if DB modified recently
            db = os.path.join(profile, 'kanban.db')
            if os.path.exists(db):
                db_age = get_age_seconds(db)
                if db_age > 90000:  # 25h
                    issues.append("kanban.db stale (dispatcher dead?)")
                # Test DB accessibility
                try:
                    conn = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM tasks")
                    tasks = cur.fetchone()[0]
                    if tasks == 0:
                        issues.append("kanban.db empty (no tasks)")
                    conn.close()
                except sqlite3.Error as e:
                    issues.append(f"kanban.db error: {e}")

    # 5. Response latency trend (last 20)
    resp_times = []
    for line in lines:
        if 'response ready:' in line:
            m = re.search(r'time=([\d.]+)s', line)
            if m:
                resp_times.append(float(m.group(1)))
    if resp_times:
        avg = sum(resp_times[-20:]) / min(20, len(resp_times))
        if avg > 120:
            issues.append(f"high latency ({avg:.0f}s avg)")

    # 6. Cron jobs
    cron_file = os.path.join(profile, 'cron', 'jobs.json')
    if os.path.exists(cron_file):
        with open(cron_file) as f:
            jobs = json.load(f)
        paused = [j for j in jobs['jobs'] if j.get('state') == 'paused']
        if paused:
            issues.append(f"{len(paused)} cron jobs paused")
        # Check overdue
        now_utc = datetime.now(timezone.utc)
        overdue = []
        for j in jobs['jobs']:
            nxt = j.get('next_run_at')
            if nxt and j.get('enabled') and not j.get('paused_by_system'):
                try:
                    nxt_dt = datetime.fromisoformat(nxt.rstrip('Z'))
                    if nxt_dt.tzinfo is None:
                        nxt_dt = nxt_dt.replace(tzinfo=timezone.utc)
                    if nxt_dt < now_utc:
                        overdue.append(j.get('name', '?'))
                except:
                    pass
        if overdue:
            issues.append(f"{len(overdue)} jobs overdue")
    else:
        issues.append("no cron jobs file")

    # 7. Telegram errors (Gentech-specific)
    if agent == 'gentech':
        chat_errors = [l for l in lines if 'Chat not found' in l]
        if chat_errors:
            issues.append("Telegram Chat not found")

    # Derive status
    if any('CRITICAL' in str(i) or 'missing' in str(i) for i in issues):
        status = 'CRITICAL'
    elif any('stale' in str(i) or 'inactive' in str(i) for i in issues):
        status = 'STALLED'
    elif len(issues) > 2:
        status = 'CRITICAL'
    elif len(issues) > 0:
        status = 'DEGRADED'
    else:
        status = 'OK'

    return status, issues

def main():
    print("Gentech Agent Health Check —", datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("-" * 60)
    for agent in AGENTS:
        status, issues = check_agent(agent)
        icon = {'OK': '✅', 'DEGRADED': '⚠️', 'CRITICAL': '❌', 'STALLED': '⏸️'}[status]
        print(f"{icon} {agent.upper():8s} {status:10s}", end='')
        if issues:
            print(f" — {'; '.join(issues[:3])}")
        else:
            print()

if __name__ == '__main__':
    main()
