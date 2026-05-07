#!/bin/bash
# Detect Hermes cron executor deadlock
# Returns 0 if healthy, 1 if deadlocked

set -e

SESSIONS_DIR="/root/.hermes/sessions"
LOG_PATTERN="cron.scheduler: Running job"
RECENT_MINUTES=90

echo "=== Cron Executor Deadlock Check ==="
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M UTC")"
echo ""

# Check 1: Are ANY session directories recent?
recent_sessions=$(find "$SESSIONS_DIR" -type d -mmin "-${RECENT_MINUTES}" 2>/dev/null || true)
session_count=$(echo "$recent_sessions" | grep -c '^' || echo 0)

echo "Recent sessions (last ${RECENT_MINUTES}m): $session_count"

if [ "$session_count" -eq 0 ]; then
    echo "⚠️  NO SESSIONS — cron executor may be deadlocked"
    deadlock_suspected=1
else
    echo "✓ Sessions are being created"
    deadlock_suspected=0
fi

# Check 2: Look for "Running job" entries in last 30m of gateway logs
echo ""
echo "Scanning gateway logs for job execution markers..."
found_execution=0
for agent in yoyo dmob desmond gentech; do
    log="/root/.hermes/profiles/${agent}/logs/gateway.log"
    if [ -f "$log" ]; then
        # Count lines with execution pattern in last 30 minutes
        count=$(grep -c "$LOG_PATTERN" "$log" 2>/dev/null || echo 0)
        if [ "$count" -gt 0 ]; then
            echo "  $agent: $count execution(s) found"
            found_execution=1
        else
            echo "  $agent: no executions in recent log"
        fi
    fi
done

if [ "$found_execution" -eq 0 ]; then
    echo "⚠️  NO JOB EXECUTION LOGS — dispatcher not dispatching"
    deadlock_suspected=1
else
    echo "✓ Job executions detected in gateway logs"
fi

# Check 3: Verify cron ticker is alive (but not sufficient alone)
echo ""
echo "Checking cron ticker thread presence..."
ticker_running=0
for agent in yoyo dmob desmond gentech; do
    log="/root/.hermes/profiles/${agent}/logs/gateway.log"
    if [ -f "$log" ] && grep -q "Cron ticker started" "$log" 2>/dev/null; then
        ticker_running=1
        break
    fi
done

if [ "$ticker_running" -eq 1 ]; then
    echo "✓ Cron ticker thread is started"
else
    echo "✗ Cron ticker NOT started"
    deadlock_suspected=1
fi

# Final verdict
echo ""
echo "=== RESULT ==="
if [ "$deadlock_suspected" -eq 1 ]; then
    echo "🚨 CRON EXECUTOR DEADLOCK DETECTED"
    echo "Recommendations:"
    echo "  1. Stop all hermes-gateway-* services"
    echo "  2. Delete __pycache__: find /usr/local/lib/hermes-agent -name '*.pyc' -delete"
    echo "  3. Restart all gateways simultaneously"
    echo "  4. Re-verify within 5 minutes"
    exit 1
else
    echo "✓ Cron executor appears healthy"
    exit 0
fi
