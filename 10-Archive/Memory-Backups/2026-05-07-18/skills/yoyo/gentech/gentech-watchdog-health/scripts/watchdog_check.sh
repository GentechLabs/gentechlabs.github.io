#!/bin/bash
# Gentech Watchdog — Quick Health Check
# Runs the full diagnostic suite and emits either STATUS:OK or a Watchdog Alert.
#
# Usage: ./watchdog_check.sh
# Output: STDOUT = human-readable; Exit code: 0=OK, 1=degraded, 2=critical

set -euo pipefail

PROFILES="yoyo dmob desmond gentech"
CRON_DB="/root/.hermes/cron/jobs.db"
JOBS_JSON="/root/.hermes/cron/jobs.json"
ALERT_REASON=""

echo "=== Gentech Watchdog Health Check ===
$(date -Iseconds)
"

# 1. Gateway liveness
echo "--- Gateway Processes ---"
RUNNING=0
for p in $PROFILES; do
    if ps aux | grep -q "hermes_cli.main --profile $p gateway run"; then
        echo "[$p] RUNNING"
        ((RUNNING++))
    else
        echo "[$p] STOPPED"
        ALERT_REASON="${ALERT_REASON} gateway $p down;"
    fi
done

if [ "$RUNNING" -ne 4 ]; then
    echo "⚠️  Not all gateways running"
fi

# 2. Recent Telegram activity
echo -e "\n--- Last Telegram Responses ---"
for p in $PROFILES; do
    LOG="/root/.hermes/profiles/$p/logs/gateway.log"
    if [ -f "$LOG" ]; then
        LAST=$(grep 'Sending response' "$LOG" | tail -1 | awk '{print $1" "$2}')
        if [ -n "$LAST" ]; then
            echo "[$p] $LAST"
        else
            echo "[$p] NO RESPONSES FOUND"
            ALERT_REASON="${ALERT_REASON} $p no responses;"
        fi
    else
        echo "[$p] NO LOG"
    fi
done

# 3. Cron executor health
echo -e "\n--- Cron Executor ---"
if [ ! -f "$CRON_DB" ] || [ ! -s "$CRON_DB" ]; then
    echo "⚠️  cron DB missing or empty: $CRON_DB"
    ALERT_REASON="${ALERT_REASON} cron DB dead;"
else
    echo "✓ cron DB present ($(stat -c%s "$CRON_DB") bytes)"
fi

if [ -f "$JOBS_JSON" ]; then
    OVERDUE=$(jq '[.jobs[] | select(.enabled == true and (.last_run_at | not) and (.next_run_at < (now | todateiso8601)))] | length' "$JOBS_JSON")
    TOTAL=$(jq '[.jobs[] | select(.enabled == true)] | length' "$JOBS_JSON")
    echo "Overdue jobs: $OVERDUE / $TOTAL"
    if [ "$OVERDUE" -gt 0 ]; then
        ALERT_REASON="${ALERT_REASON} $OVERDUE overdue cron jobs;"
    fi
else
    echo "⚠️  jobs.json missing"
    ALERT_REASON="${ALERT_REASON} jobs.json missing;"
fi

# 4. Auth failure velocity (last 100 lines)
echo -e "\n--- Error Velocity (last 100 lines) ---"
for p in $PROFILES; do
    ERRLOG="/root/.hermes/profiles/$p/logs/errors.log"
    if [ -f "$ERRLOG" ]; then
        AUTH_COUNT=$(tail -100 "$ERRLOG" 2>/dev/null | grep -ci 'AuthError\|Refresh session\|revoked\|401' || true)
        CRASH_COUNT=$(tail -100 "$ERRLOG" 2>/dev/null | grep -ci 'exit code 1\|SIGTERM' || true)
        BYTECODE_COUNT=$(tail -100 "$ERRLOG" 2>/dev/null | grep -ci 'marshal data too short' || true)
        echo "[$p] auth_fails=$AUTH_COUNT crashes=$CRASH_COUNT bytecode_err=$BYTECODE_COUNT"
        if [ "$AUTH_COUNT" -ge 10 ]; then
            ALERT_REASON="${ALERT_REASON} $p auth failures($AUTH_COUNT);"
        fi
        if [ "$CRASH_COUNT" -ge 5 ]; then
            ALERT_REASON="${ALERT_REASON} $p crash loop($CRASH_COUNT);"
        fi
        if [ "$BYTECODE_COUNT" -ge 1 ]; then
            ALERT_REASON="${ALERT_REASON} $p bytecode corruption;"
        fi
    fi
done

# 5. Decision
echo -e "\n=== RESULT ==="
if [ -z "$ALERT_REASON" ]; then
    echo "STATUS:OK"
    exit 0
else
    echo "🚨 Watchdog Alert: ${ALERT_REASON//; /, }"
    exit 2
fi
