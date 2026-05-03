#!/bin/bash
# system-cleanup/scripts/find-recursive-traps.sh
# Detects nested dot-directory copies (bloat traps) in a given path
# Usage: ./find-recursive-traps.sh /path/to/scan
# Returns: lines matching "TRAP: <path> (<size>) — nested count: N"

set -euo pipefail

TARGET="${1:-/root/vaults/gentech/10-Archive}"

# Patterns that indicate backup traps
# .hermes = agent backups
# .git = version control (should never be nested)
# node_modules = npm dependencies (often copied inadvertently)
PATTERNS="\.hermes|\.git|node_modules"

echo "Scanning $TARGET for recursive backup traps..."
echo "Pattern: $PATTERNS"
echo ""

FOUND=0

while IFS= read -r -d '' dir; do
  # Determine pattern type for nested count
  if [[ "$dir" == *".hermes"* ]]; then
    PAT=".hermes"
  elif [[ "$dir" == *".git"* ]]; then
    PAT=".git"
  else
    PAT="node_modules"
  fi

  # Count nested occurrences of same pattern inside this directory
  nested_count=$(find "$dir" -type d -name "$PAT" 2>/dev/null | wc -l)

  if [ "$nested_count" -gt 1 ]; then
    size=$(du -sh "$dir" 2>/dev/null | cut -f1)
    depth=$(echo "$dir" | tr -cd '/' | wc -c)
    echo "⚠️  TRAP DETECTED: $dir"
    echo "   Size: $size | Nested count: $nested_count | Path depth: $depth"
    echo ""
    FOUND=$((FOUND + 1))
  fi
done < <(find "$TARGET" -type d \( -name '.hermes' -o -name '.git' -o -name 'node_modules' \) 2>/dev/null -print0)

if [ "$FOUND" -eq 0 ]; then
  echo "✓ No recursive traps found in $TARGET"
else
  echo "Found $FOUND trap(s). Review before deletion."
  echo "Recommendation: Verify no external references exist (grep -r 'path' /root/workspace) then delete entire trap tree."
fi

exit $FOUND
