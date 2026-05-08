#!/bin/bash
# Disk Audit Pipeline — Gentech System Maintenance
# Outputs: JSON report to stdout
# Usage: ./disk-audit.sh > audit-$(date +%Y-%m-%d).json

set -euo pipefail

# Output as JSON lines
echo "{"
echo "  \"timestamp\": \"$(date -Iseconds)\","
echo "  \"hostname\": \"$(hostname)\","
echo "  \"disk_usage\": $(df -h / | tail -1 | awk '{print \",\"}'),"

# Top-level directories
echo "  \"top_directories\": ["
du -sh /root/* 2>/dev/null | sort -rh | awk -v OFS=',' '
{
  gsub(/"/, "\\\"", $2)
  printf "    {\"path\": \"%s\", \"size\": \"%s\"}", $2, $1
  if (NR < NR_MAX) printf ",\n"
}
' NR_MAX=$(du -sh /root/* 2>/dev/null | wc -l)
echo "  ],"

# Bloat patterns — each as an array element
echo "  \"bloat_patterns\": {"

# Rust targets
echo "    \"rust_targets\": ["
find /root -name 'target' -type d 2>/dev/null | while read -r dir; do
  size=$(du -sh "$dir" 2>/dev/null | cut -f1)
  echo "      {\"path\": \"$dir\", \"size\": \"$size\"},"
done | sed '$ s/,$//'
echo " ],"

# NPM cache
echo "    \"npm_cache\": $(du -sh ~/.npm 2>/dev/null | awk '{print $1}'),"

# UV cache
echo "    \"uv_cache\": $(du -sh ~/.cache/uv 2>/dev/null | awk '{print $1}'),"

# Docker
if command -v docker &>/dev/null; then
  echo "    \"docker\": $(docker system df 2>/dev/null | tail -n +2 | jq -R -s -c 'split("\n")[:-1] | map(select(length>0)) | map(split("\\t")) | map({type: .[0], total: .[1], active: .[2], size: .[3], reclaimable: .[4]})' 2>/dev/null || echo 'null'),"
else
  echo "    \"docker\": null,"
fi

# Hermes logs
echo "    \"hermes_logs\": {"
for profile in /root/.hermes/profiles/*/logs; do
  [ -d "$profile" ] || continue
  name=$(basename $(dirname "$profile"))
  size=$(du -sh "$profile" 2>/dev/null | awk '{print $1}')
  echo "      \"$name\": \"$size\""
  [ "$(ls -1 "$profile" 2>/dev/null | tail -n +2)" ] && echo ","
done
echo "    },"

# Vault breakdown
echo "    \"vaults\": {"
du -sh /root/vaults/gentech/* 2>/dev/null | sort -rh | while read size path; do
  name=$(basename "$path")
  echo "      \"$name\": \"$size\""
  [ "$(du -sh /root/vaults/gentech/* 2>/dev/null | tail -n +2)" ] && echo ","
done
echo "    }"

echo "  }"
echo "}"
