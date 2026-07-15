#!/bin/bash
# NotebookLM Sources — Git Sync
# Adds and commits any new/changed prepared sources
# Run after manually processing sources in NotebookLM

cd "$(dirname "$0")/.."
VAULT_DIR=$(pwd)
OUTPUT_DIR="$VAULT_DIR/11-Mess Hall/notebooklm-sources"

echo "=== NotebookLM Sources Sync ==="
echo "Vault: $VAULT_DIR"

# Check for changes
CHANGED=$(git status --short "$OUTPUT_DIR" 2>/dev/null | grep -c .)
if [ "$CHANGED" -eq 0 ]; then
  echo "No changes to sync."
  exit 0
fi

echo "Changes detected:"
git status --short "$OUTPUT_DIR"

git add "$OUTPUT_DIR"
git commit -m "notebooklm-sources: update prepared sources $(date +%Y-%m-%d)" --quiet
git push 2>&1 | tail -3

echo "Done."
