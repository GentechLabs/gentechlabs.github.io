#!/bin/bash
# Hermes Agent Health Check — automated watchdog probe
# Invocation: ./scripts/agent-health-check.sh
# Output: human-readable summary + exit code (0=healthy, 1=degraded, 2=critical)

set -euo pipefail

AGENTS=("yoyo" "dmob" "desmond" "gentech")
CRITICAL_BOOT_THRESHOLD=8
CRITICAL_ERROR_THRESHOLD=1000
DEGRADED_ERROR_THRESHOLD=100

declare -a issues_critical=()
declare -a issues_degraded=()

echo "=== Hermes Agent Health Check ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# 1. Process check
echo "--- Process Status ---"
for agent in "${AGENTS[@]}"; do
  pcount=$(pgrep -f "hermes.*profile $agent" | wc -l)
  if [ "$pcount" -eq 0 ]; then
    echo "[CRITICAL] $agent: NO gateway process running"
    issues_critical+=("$agent process missing")
  elif [ "$pcount" -gt 1 ]; then
    echo "[CRITICAL] $agent: $pcount gateway processes (restart loop suspected)")
    issues_critical+=("$agent restart loop ($pcount procs)")
  else
    echo "[OK]      $agent: gateway process active"
  fi
done
echo ""

# 2. Gateway boot count
echo "--- Gateway Boot Count (last 48h) ---"
for agent in "${AGENTS[@]}"; do
  log="/root/.hermes/profiles/$agent/logs/gateway.log"
  if [ ! -f "$log" ]; then
    echo "[CRITICAL] $agent: gateway.log missing"
    issues_critical+=("$agent log missing")
    continue
  fi
  boots=$(grep -c "Starting Hermes Gateway" "$log" 2>/dev/null || echo 0)
  abnormal=$(grep -c "Exiting with code 1" "$log" 2>/dev/null || echo 0)
  if [ "$boots" -gt "$CRITICAL_BOOT_THRESHOLD" ]; then
    echo "[CRITICAL] $agent: $boots boots (threshold $CRITICAL_BOOT_THRESHOLD), $abnormal abnormal exits")
    issues_critical+=("$agent excessive reboots")
  elif [ "$boots" -gt 5 ]; then
    echo "[DEGRADED] $agent: $boots boots")
    issues_degraded+=("$agent elevated reboots")
  else
    echo "[OK]      $agent: $boots boots")
  fi
done
echo ""

# 3. Credential gap detection
echo "--- Credential Gap Scan ---"

# Anthropic (DMOB)
if grep -qi "No Anthropic credentials found" /root/.hermes/profiles/dmob/logs/agent.log 2>/dev/null; then
  echo "[CRITICAL] DMOB: Anthropic credentials missing"
  issues_critical+=("DMOB Anthropic missing")
else
  echo "[OK]      DMOB: Anthropic credentials present"
fi

# ElevenLabs (Desmond)
des_401=$(grep -ci "elevenlabs.*401\|Invalid API key" /root/.hermes/profiles/desmond/logs/agent.log 2>/dev/null || echo 0)
if [ "$des_401" -gt 50 ]; then
  echo "[CRITICAL] DESMOND: $des_401 ElevenLabs 401 errors — API key invalid/missing"
  issues_critical+=("Desmond ElevenLabs invalid")
else
  echo "[OK]      DESMOND: ElevenLabs errors $des_401 (threshold 50)"
fi

# Provider key missing (Gentech/YoYo)
for agent in gentech yoyo; do
  if grep -qE "Provider '.*' is set in config.yaml but no API key was found" /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null; then
    echo "[CRITICAL] $agent: provider API key missing in config"
    issues_critical+=("$agent provider key missing")
  else
    echo "[OK]      $agent: provider key present"
  fi
done
echo ""

# 4. Error volume classification
echo "--- Error Volume (agent.log) ---"
for agent in "${AGENTS[@]}"; do
  log="/root/.hermes/profiles/$agent/logs/agent.log"
  if [ ! -f "$log" ]; then
    echo "[CRITICAL] $agent: agent.log missing"
    issues_critical+=("$agent agent.log missing")
    continue
  fi
  total=$(wc -l < "$log")
  errs=$(grep -icE "(error|exception|failed)" "$log" 2>/dev/null || echo 0)
  ratio=$(awk "BEGIN {printf \"%.3f\", $errs/$total}")
  if [ "$errs" -gt "$CRITICAL_ERROR_THRESHOLD" ]; then
    echo "[CRITICAL] $agent: $errs errors / $total lines (rate $ratio)"
    issues_critical+=("$agent error flood")
  elif [ "$errs" -gt "$DEGRADED_ERROR_THRESHOLD" ]; then
    echo "[DEGRADED] $agent: $errs errors / $total lines (rate $ratio)")
    issues_degraded+=("$agent elevated errors")
  else
    echo "[OK]      $agent: $errs errors / $total lines (rate $ratio)")
  fi
done
echo ""

# 5. Connection fallback count (auxiliary client)
echo "--- Connection Fallback Count ---"
for agent in "${AGENTS[@]}"; do
  falls=$(grep -c "connection error on auto" /root/.hermes/profiles/$agent/logs/agent.log 2>/dev/null || echo 0)
  if [ "$falls" -gt 1000 ]; then
    echo "[CRITICAL] $agent: $falls connection fallbacks — provider unreachable")
    issues_critical+=("$agent connection storm")
  elif [ "$falls" -gt 100 ]; then
    echo "[DEGRADED] $agent: $falls connection fallbacks")
    issues_degraded+=("$agent connection issues")
  else
    echo "[OK]      $agent: $falls connection fallbacks")
  fi
done
echo ""

# 6. Telegram disconnect count (symptom check)
echo "--- Telegram Disconnect Count ---"
for agent in "${AGENTS[@]}"; do
  disc=$(grep -c "Telegram.*Disconnected" /root/.hermes/profiles/$agent/logs/gateway.log 2>/dev/null || echo 0)
  if [ "$disc" -gt 10 ]; then
    echo "[DEGRADED] $agent: $disc Telegram disconnects")
    issues_degraded+=("$agent Telegram instability")
  else
    echo "[OK]      $agent: $disc Telegram disconnects")
  fi
done
echo ""

# Final verdict
echo "=== SUMMARY ==="
echo "Critical issues: ${#issues_critical[@]}"
echo "Degraded issues: ${#issues_degraded[@]}"
echo ""

if [ ${#issues_critical[@]} -gt 0 ]; then
  echo "STATUS: CRITICAL"
  echo "Critical issues detected:"
  for i in "${issues_critical[@]}"; do echo "  - $i"; done
  exit 2
elif [ ${#issues_degraded[@]} -gt 0 ]; then
  echo "STATUS: DEGRADED"
  echo "Degraded issues detected:"
  for i in "${issues_degraded[@]}"; do echo "  - $i"; done
  exit 1
else
  echo "STATUS: OK"
  exit 0
fi
