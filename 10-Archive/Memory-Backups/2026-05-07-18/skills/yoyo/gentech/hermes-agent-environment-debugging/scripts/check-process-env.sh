#!/bin/bash
# check-process-env.sh — Extract credential-related env vars from a Hermes gateway process
# Usage: check-process-env.sh <agent-name>
# Example: check-process-env.sh yoyo

set -euo pipefail

AGENT="${1:-}"
if [ -z "$AGENT" ]; then
  echo "Usage: $0 <agent-name>" >&2
  echo " Agents: yoyo, dmob, desmond, gentech" >&2
  exit 1
fi

# Find PID
PID=$(pgrep -f "hermes_cli.main.*--profile ${AGENT}.*gateway" | head -1)
if [ -z "$PID" ]; then
  echo "ERROR: No running gateway process found for agent '${AGENT}'" >&2
  exit 1
fi

echo "Agent: ${AGENT}"
echo "PID: ${PID}"
echo ""
echo "=== CREDENTIAL ENVIRONMENT VARIABLES ==="
sudo cat /proc/${PID}/environ 2>/dev/null | tr '\0' '\n' | \
  grep -E 'NOUS|ANTHROPIC|ELEVENLABS|OPENAI|OPENCODE|TELEGRAM' | \
  while IFS= read -r line; do
    key="${line%%=*}"
    val="${line#*=}"
    if [ -z "$val" ]; then
      echo "  ${key}=<EMPTY>"
    else
      echo "  ${key}=${val:0:30}... (len=${#val})"
    fi
  done

echo ""
echo "=== FULL ENVIRONMENT (first 20 lines) ==="
sudo cat /proc/${PID}/environ 2>/dev/null | tr '\0' '\n' | head -20

# Exit 0 if all expected keys are present, 1 otherwise
REQUIRED_KEYS=("NOUS_TOKEN" "ANTHROPIC_API_KEY" "ELEVENLABS_API_KEY")
MISSING=0
for key in "${REQUIRED_KEYS[@]}"; do
  if ! sudo cat /proc/${PID}/environ 2>/dev/null | tr '\0' '\n' | grep -q "^${key}="; then
    echo "MISSING: ${key}" >&2
    MISSING=$((MISSING + 1))
  fi
done

if [ "$MISSING" -gt 0 ]; then
  echo "" >&2
  echo "STATUS: DEGRADED — ${MISSING} credential(s) missing from process environment" >&2
  echo "See skill: hermes-agent-environment-debugging" >&2
  exit 1
else
  echo "" >&2
  echo "STATUS: OK — all required credentials present in process environment"
  exit 0
fi
