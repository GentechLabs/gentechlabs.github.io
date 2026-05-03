#!/bin/bash
# verify-credentials-loaded.sh — Wrapper to run check-process-env.sh on all agents and aggregate status
# Usage: verify-credentials-loaded.sh
# Returns: 0 if all agents OK, 1 if any degraded

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_SCRIPT="${SCRIPT_DIR}/check-process-env.sh"

AGENTS=(yoyo dmob desmond gentech)
OVERALL_STATUS=0

echo "=== Hermes Agent Credential Verification ==="
echo "Checking ${#AGENTS[@]} agents..."
echo ""

for agent in "${AGENTS[@]}"; do
  echo "--- ${agent} ---"
  if "${CHECK_SCRIPT}" "${agent}"; then
    echo "  ✓ PASS"
  else
    echo "  ✗ FAIL — see hermes-agent-environment-debugging skill"
    OVERALL_STATUS=1
  fi
  echo ""
done

if [ "$OVERALL_STATUS" -eq 0 ]; then
  echo "All agents have credentials loaded."
  exit 0
else
  echo "One or more agents are missing credentials in process environment." >&2
  echo "Remediation: Populate ~/.hermes/.env with missing keys and restart gateways." >&2
  exit 1
fi
