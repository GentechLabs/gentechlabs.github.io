#!/bin/bash
# Vault Health Check — Gentech Maintenance
# Scans vault structure for anomalies, size outliers, and contamination
# Usage: ./vault-health-check.sh

VAULT_ROOT="/root/vaults/gentech"
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "=== Gentech Vault Health Check ==="
echo "Timestamp: $(date -Iseconds)"
echo ""

# 1. Total vault size
total_size=$(du -sh "$VAULT_ROOT" | cut -f1)
echo -e "Total vault usage: ${GREEN}$total_size${NC}"

# 2. Per-folder breakdown (sorted)
echo ""
echo "--- Folder Breakdown ---"
du -sh "$VAULT_ROOT"/* 2>/dev/null | sort -rh | while read size path; do
  folder=$(basename "$path")
  # Remove trailing slash from size if present
  size_num=$(echo "$size" | sed 's/G//;s/M//;s/K//')
  unit=$(echo "$size" | grep -o '[GMK]$' || echo '')

  # Threshold checks (rough heuristics)
  if [[ "$unit" == "G" ]] && (( $(echo "$size_num > 10" | bc -l) )); then
    status="${YELLOW}[LARGE]${NC}"
  elif [[ "$folder" == "10-Archive" ]]; then
    status="${GREEN}[ARCHIVE]${NC}"
  else
    status="${GREEN}[OK]${NC}"
  fi

  printf "%-20s %10s %s\n" "$folder" "$size" "$status"
done

# 3. Contamination check — look for non-vault bloat patterns
echo ""
echo "--- Contamination Scan ---"
contamination=0

# Check for node_modules within vault
if find "$VAULT_ROOT" -name 'node_modules' -type d 2>/dev/null | grep -q .; then
  echo -e "${RED}[FAIL]${NC} node_modules found inside vault!"
  find "$VAULT_ROOT" -name 'node_modules' -type d 2>/dev/null | head -5
  contamination=1
else
  echo -e "${GREEN}[PASS]${NC} No node_modules in vault"
fi

# Check for target/ dirs within vault
if find "$VAULT_ROOT" -name 'target' -type d 2>/dev/null | grep -q .; then
  echo -e "${RED}[FAIL]${NC} Rust target/ dirs found inside vault!"
  find "$VAULT_ROOT" -name 'target' -type d 2>/dev/null | head -5
  contamination=1
else
  echo -e "${GREEN}[PASS]${NC} No Rust target/ in vault"
fi

# Check for large media files that might not belong (images, videos)
large_media=$(find "$VAULT_ROOT" \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.mp4' -o -iname '*.mov' \) -size +10M 2>/dev/null | wc -l)
if [[ "$large_media" -gt 0 ]]; then
  echo -e "${YELLOW}[WARN]${NC} $large_media media files >10MB found. Consider if these belong in 06-Content or should be archived."
  contamination=1
else
  echo -e "${GREEN}[PASS]${NC} No oversized media files (>10MB)"
fi

# 4. Summary
echo ""
echo "--- Summary ---"
if [[ "$contamination" -eq 0 ]]; then
  echo -e "Status: ${GREEN}HEALTHY${NC} — Vault structure clean. No build artifacts detected."
  exit 0
else
  echo -e "Status: ${RED}NEEDS ATTENTION${NC} — Vault contains bloat or misplaced files."
  echo "Run: find $VAULT_ROOT -name 'node_modules' -o -name 'target' | xargs rm -rf (after review)"
  exit 1
fi
