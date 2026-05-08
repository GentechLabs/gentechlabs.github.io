#!/usr/bin/env bash
# Gentech Enterprise Agent Health Check — Automated Watchdog
# Part of: gentech-enterprise-agent-monitoring skill
# Usage: /path/to/gentech/scripts/agent-health-check.sh
# Output: Machine-parseable pipe-separated table to stdout

set -euo pipefail

AGENTS=("desmond" "dmob" "gentech" "yoyo")
CRON_DIR="/tmp"
NOW=$(date +%s)
STALE_THRESHOLD_HOURS=24
CRITICAL_STALE_HOURS=72

# Header
echo "AGENT|CRON_STALE|GATEWAY_UP|AUTH_OK|LAST_ERROR|HOURS_AGO|MEM_MB|CPU_PCT"

for agent in "${AGENTS[@]}"; do
  CRON_FILE="${CRON_DIR}/${agent}_cron.txt"
  
  # Defaults
  CRON_STALE="UNKNOWN"
  GATEWAY_UP="UNKNOWN"
  AUTH_OK="UNKNOWN"
  LAST_ERROR=""
  HOURS_AGO=""
  MEM_MB=""
  CPU_PCT=""
  
  # --- Check cron file existence ---
  if [[ ! -f "$CRON_FILE" ]]; then
    CRON_STALE="MISSING"
    HOURS_AGO=">168"
  else
    FILE_MTIME=$(stat -c %Y "$CRON_FILE" 2>/dev/null || echo 0)
    
    # Extract last run line (last occurrence)
    LAST_RUN_LINE=$(grep -i "Last run:" "$CRON_FILE" 2>/dev/null | tail -1 || true)
    
    if [[ -n "$LAST_RUN_LINE" ]]; then
      # Parse timestamp: "Last run:  2026-04-30T09:00:31.681521+00:00  ok"
      TS_STR=$(echo "$LAST_RUN_LINE" | sed -n 's/.*Last run:[[:space:]]*//p' | awk '{print $1}')
      
      if [[ -n "$TS_STR" ]]; then
        # Convert ISO8601 to epoch (strip fractional seconds, handle +00:00)
        TS_CLEAN=$(echo "$TS_STR" | sed -E 's/\.[0-9]+//;s/\+00:00$//')
        LAST_EPOCH=$(date -d "$TS_CLEAN" +%s 2>/dev/null || echo 0)
        
        if [[ $LAST_EPOCH -gt 0 ]]; then
          DIFF_SEC=$(( NOW - LAST_EPOCH ))
          HOURS_AGO=$(awk "BEGIN {printf \"%.1f\", $DIFF_SEC/3600}")
          
          if (( $(echo "$HOURS_AGO > $CRITICAL_STALE_HOURS" | bc -l) )); then
            CRON_STALE="CRITICAL"
          elif (( $(echo "$HOURS_AGO > $STALE_THRESHOLD_HOURS" | bc -l) )); then
            CRON_STALE="STALE"
          else
            CRON_STALE="OK"
          fi
          
          # Check for error suffix
          if echo "$LAST_RUN_LINE" | grep -qi "error:"; then
            AUTH_OK="FAILED"
            LAST_ERROR=$(echo "$LAST_RUN_LINE" | sed -n 's/.*error:[[:space:]]*//p' | head -c 80)
          else
            AUTH_OK="OK"
          fi
        else
          CRON_STALE="PARSE_ERROR"
          HOURS_AGO="?"
        fi
      else
        CRON_STALE="NO_TS"
        HOURS_AGO="?"
      fi
    else
      CRON_STALE="NO_LAST_RUN"
      HOURS_AGO="?"
    fi
    
    # Check file freshness (mtime should be recent if cron is active)
    FILE_AGE_HOURS=$(( (NOW - FILE_MTIME) / 3600 ))
    if [[ $FILE_AGE_HOURS -gt 48 ]] && [[ "$CRON_STALE" == "OK" ]]; then
      # Cron says OK but file hasn't updated in 48h — suspect lock/stale output
      CRON_STALE="LOCKED"
    fi
  fi
  
  # --- Check gateway process ---
  GATEWAY_PATTERN="hermes_cli.main.*--profile ${agent}.*gateway"
  if pgrep -f "$GATEWAY_PATTERN" >/dev/null 2>&1; then
    GATEWAY_UP="RUNNING"
    # Get RSS memory and CPU%
    PID=$(pgrep -f "$GATEWAY_PATTERN" | head -1)
    if [[ -n "$PID" ]]; then
      # Read /proc/${PID}/status for memory
      if [[ -f "/proc/${PID}/status" ]]; then
        RSS_KB=$(grep "^VmRSS:" "/proc/${PID}/status" | awk '{print $2}')
        MEM_MB=$(( RSS_KB / 1024 ))
      fi
      # Get CPU% from ps
      CPU_LINE=$(ps -p "$PID" -o %cpu,cmd --no-headers 2>/dev/null || true)
      CPU_PCT=$(echo "$CPU_LINE" | awk '{print $1}')
    fi
  else
    GATEWAY_UP="DOWN"
  fi
  
  # --- Check error log accumulation ---
  ERR_LOG="${CRON_DIR}/dr_errors.txt"
  if [[ -f "$ERR_LOG" ]]; then
    ERR_SIZE=$(stat -c %s "$ERR_LOG" 2>/dev/null || echo 0)
    if [[ $ERR_SIZE -gt 150000 ]]; then
      # Large error log — flag as anomaly but don't override primary status
      if [[ -z "$LAST_ERROR" ]]; then
        LAST_ERROR="Large error log (${ERR_SIZE}B)"
      fi
    fi
  fi
  
  # --- Output ---
  echo "${agent}|${CRON_STALE}|${GATEWAY_UP}|${AUTH_OK}|${LAST_ERROR}|${HOURS_AGO}|${MEM_MB}|${CPU_PCT}"
done
