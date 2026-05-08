#!/usr/bin/env python3
"""
Gentech Agent Fleet Health Check — Cron Watchdog Edition

Rapid diagnostic for the 4 Gentech Hermes agents. Checks cron subsystem integrity,
gateway liveness, auth health, and Telegram connectivity.

Usage: python3 agent_health.py

Exit codes: 0 = all OK, 1 = degraded/critical issues detected

Output format per agent: STATUS | DETAIL
Example: yoyo OK | cron_enabled: true, last_dispatch: 2m ago, errors: 0
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

AGENTS = ['yoyo', 'dmob', 'desmond', 'gentech']
BASE = Path('/root/.hermes/profiles')


def run(cmd, timeout=3):
    """Run shell command, return output or empty string."""
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip()
    except Exception:
        return ''


def read_last_lines(path, n=100):
    """Read last n lines of a file safely."""
    try:
        with open(path) as f:
            return f.readlines()[-n:]
    except Exception:
        return []


def agent_status(agent):
    """Compute health status for one agent. Returns (status_code, detail_string)."""
    profile = BASE / agent
    log_gw = profile / 'logs' / 'gateway.log'
    log_err = profile / 'logs' / 'errors.log'
    config = profile / 'config.yaml'

    detail_parts = []

    # ── 1. Process liveness ────────────────────────────────────────────────────
    ps_out = run(f"ps aux | grep 'hermes.*gateway run --profile {agent}' | grep -v grep")
    if not ps_out:
        return 'CRITICAL', 'Process not running'

    # ── 2. Cron executor health ───────────────────────────────────────────────
    # A. Check cron_enabled flag
    cron_enabled = False
    if config.exists():
        cfg_text = config.read_text()
        cron_enabled = 'cron_enabled' in cfg_text and 'true' in cfg_text.lower().split('cron_enabled')[1].split('\n')[0]

    # B. Check for cron ticker activity (last 10 minutes)
    gw_lines = read_last_lines(log_gw, 200)
    recent_timestamp = None
    ticker_lines = [l for l in gw_lines if 'Cron ticker started' in l or 'Cron ticker stopped' in l]
    if ticker_lines:
        # Parse timestamp from last tick line
        m = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', ticker_lines[-1])
        if m:
            recent_timestamp = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')

    # C. Check for actual job dispatches in last 30 minutes
    dispatch_lines = [l for l in gw_lines if re.search(r'dispatching cron job|job started|cron\.scheduler:', l, re.I)]
    recent_dispatches = []
    for l in dispatch_lines:
        m = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', l)
        if m:
            ts = datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
            if ts > datetime.now() - timedelta(minutes=30):
                recent_dispatches.append(ts)

    # D. Cron health classification
    now = datetime.now()
    cron_age_min = (now - recent_timestamp).total_seconds() / 60 if recent_timestamp else 999

    if not cron_enabled:
        cron_status = 'DISABLED'
        detail_parts.append('cron_enabled: false')
    elif cron_age_min > 30 and not recent_dispatches:
        cron_status = 'DEAD'
        detail_parts.append(f'cron ticker stale ({cron_age_min:.0f}min), 0 recent dispatches')
    elif recent_timestamp and not recent_dispatches:
        cron_status = 'STUCK'
        detail_parts.append(f'ticker running but 0 dispatches in 30min')
    elif recent_dispatches:
        last_dispatch_age = (now - recent_dispatches[-1]).total_seconds() / 60
        cron_status = 'OK'
        detail_parts.append(f'last dispatch: {last_dispatch_age:.0f}min ago')
    else:
        cron_status = 'UNKNOWN'
        detail_parts.append('cron state unclear')

    # ── 3. Recent error rate ───────────────────────────────────────────────────
    err_lines = read_last_lines(log_err, 100)
    error_count = sum(1 for l in err_lines if 'ERROR' in l or 'CRITICAL' in l or 'Traceback' in l)

    if error_count > 20:
        detail_parts.append(f'errors: {error_count} (HIGH)')
    elif error_count > 0:
        detail_parts.append(f'errors: {error_count}')
    else:
        detail_parts.append('errors: 0')

    # ── 4. Gateway log recency ─────────────────────────────────────────────────
    gw_stat = log_gw.stat()
    gw_age_min = (now - datetime.fromtimestamp(gw_stat.st_mtime)).total_seconds() / 60
    if gw_age_min > 10:
        detail_parts.append(f'gateway.log stale ({gw_age_min:.0f}min)')
    elif gw_age_min < 0:
        detail_parts.append('gateway.log future timestamp')

    # ── 5. Specific failure pattern detection ──────────────────────────────────
    # A. TTS failures (fleet-wide indicator)
    tts_401 = sum(1 for l in err_lines if 'elevenlabs' in l.lower() and '401' in l)
    if tts_401 > 5:
        detail_parts.append(f'ELEVENLABS_401: {tts_401}')

    # B. Nous Portal auth revocation
    if any('Refresh session has been revoked' in l for l in err_lines):
        detail_parts.append('NOUS_AUTH_REVOKED')

    # C. Telegram "Chat not found" (transient vs permanent check)
    gw_recent = read_last_lines(log_gw, 200)
    chat_errors = [l for l in gw_recent if 'Chat not found' in l or 'telegram.error.BadRequest' in l]
    if chat_errors:
        # Check if successful sends occurred after the errors
        sends_after_errors = [l for l ingw_recent if 'Sending response' in l]
        if sends_after_errors:
            # Compare timestamps
            last_err_ts_str = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', chat_errors[-1])
            last_send_ts_str = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', sends_after_errors[-1])
            if last_err_ts_str and last_send_ts_str:
                err_ts = datetime.strptime(last_err_ts_str.group(1), '%Y-%m-%d %H:%M:%S')
                send_ts = datetime.strptime(last_send_ts_str.group(1), '%Y-%m-%d %H:%M:%S')
                if send_ts > err_ts:
                    detail_parts.append('TELEGRAM_CHAT_ERROR: recovering')
                else:
                    detail_parts.append('TELEGRAM_CHAT_ERROR: active')
            else:
                detail_parts.append('TELEGRAM_CHAT_ERROR: active')
        else:
            detail_parts.append('TELEGRAM_CHAT_ERROR: active (no sends)')
    # D. Cron job failures (look in errors.log for cron.scheduler entries)
    cron_failures = [l for l in err_lines if 'cron.scheduler' in l and 'failed' in l.lower()]
    if cron_failures:
        detail_parts.append(f'cron_job_failures: {len(cron_failures)}')

    # ── 6. Final status determination ─────────────────────────────────────────
    # Priority issues that force DEGRADED or CRITICAL
    if cron_status == 'DEAD' or 'CRITICAL' in detail_parts[0] if detail_parts else False:
        return 'CRITICAL', '; '.join(detail_parts)
    elif cron_status in ('DEAD', 'STUCK') or error_count > 50 or 'TELEGRAM_CHAT_ERROR: active' in '; '.join(detail_parts):
        return 'DEGRADED', '; '.join(detail_parts)
    else:
        return 'OK', '; '.join(detail_parts)


def main():
    print("=" * 70)
    print("Gentech Agent Fleet Health Check — Watchdog")
    print(f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    overall = []
    for agent in AGENTS:
        status, detail = agent_status(agent)
        overall.append(status)
        icon = {'OK': '✓', 'DEGRADED': '⚠️ ', 'CRITICAL': '🔴'}.get(status, '?')
        print(f"{icon} {agent.upper():10s} {status:10s} {detail}")

    print("\n" + "=" * 70)
    if all(s == 'OK' for s in overall):
        print("STATUS: OK — All agents healthy")
        return 0
    elif any(s == 'CRITICAL' for s in overall):
        print("STATUS: CRITICAL — Immediate attention required")
        return 1
    else:
        print("STATUS: DEGRADED — Non-critical issues detected")
        return 1


if __name__ == '__main__':
    sys.exit(main())
