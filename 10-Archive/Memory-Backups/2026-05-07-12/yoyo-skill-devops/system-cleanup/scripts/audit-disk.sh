#!/bin/bash
# system-cleanup/scripts/audit-disk.sh
# Quick disk audit — outputs JSON for parsing by Hermes agents
# Usage: ./audit-disk.sh

# Colors for readability (optional)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get values
ROOT_USED=$(df -h / | awk 'NR==2{print $5}' | tr -d '%')
ROOT_SIZE=$(df -h / | awk 'NR==2{print $2}')
VAULT_SIZE=$(du -sh /root/vaults/gentech 2>/dev/null | cut -f1)
CACHE_SIZE=$(du -sh /root/.cache 2>/dev/null | cut -f1)
HERMES_SIZE=$(du -sh /root/.hermes 2>/dev/null | cut -f1)
TMP_SIZE=$(du -sh /tmp 2>/dev/null | cut -f1)

# Count nested .hermes traps in vault backups
NESTED_COUNT=$(find /root/vaults/gentech/10-Archive -type d -name '.hermes' 2>/dev/null | wc -l)

# Docker summary (if available)
if command -v docker &> /dev/null; then
  DOCKER_TOTAL=$(docker system df 2>/dev/null | grep -E '^Images' | awk '{print $3}')
  DOCKER_RECLAIM=$(docker system df 2>/dev/null | grep -E '^TYPE' -A1 | tail -1 | awk '{print $4}')
else
  DOCKER_TOTAL="N/A"
  DOCKER_RECLAIM="N/A (docker not installed)"
fi

# Risk assessment
if [ "$ROOT_USED" -gt 80 ]; then
  RISK_LEVEL="HIGH"
  RISK_COLOR=$RED
elif [ "$ROOT_USED" -gt 65 ]; then
  RISK_LEVEL="MEDIUM"
  RISK_COLOR=$YELLOW
else
  RISK_LEVEL="HEALTHY"
  RISK_COLOR=$GREEN
fi

# Output JSON (machine-readable)
cat <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "disk_usage_percent": $ROOT_USED,
  "disk_usage_gb": "${ROOT_SIZE//[!0-9.]/}",
  "risk_level": "$RISK_LEVEL",
  "vault_size": "$VAULT_SIZE",
  "cache_size": "$CACHE_SIZE",
  "hermes_size": "$HERMES_SIZE",
  "tmp_size": "$TMP_SIZE",
  "nested_hermes_traps": $NESTED_COUNT,
  "docker_total": "$DOCKER_TOTAL",
  "docker_reclaimable": "$DOCKER_RECLAIM"
}
EOF

# Human-readable summary
echo ""
echo -e "${RISK_COLOR}=== Disk Health: $RISK_LEVEL (${ROOT_USED}% used)${NC}"
echo "Vault:        $VAULT_SIZE"
echo "Cache:        $CACHE_SIZE"
echo "Hermes:       $HERMES_SIZE"
echo "/tmp:         $TMP_SIZE"
echo "Nested traps: $NESTED_COUNT"
echo "Docker total: $DOCKER_TOTAL  (reclaimable: $DOCKER_RECLAIM)"

exit 0
