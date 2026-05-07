#!/bin/bash
# Daily log cleanup — part of vault-maintenance-audit
# Deletes .md files in 08-Daily/ older than 7 days (direct children only)

set -euo pipefail

VAULT="/root/vaults/gentech"
DAILY_DIR="$VAULT/08-Daily"
RETENTION_DAYS=7
DRY_RUN="${DRY_RUN:-true}"  # set DRY_RUN=false to actually delete

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Enumerate protected subdirs (never touch)
PROTECTED=("Daily-Summaries" "2026-Weekly" "Monthly-Summaries" "Reviews" "agent-states" "content-drafts" "cron-changes")

# Check if we're in the right place
if [[ ! -d "$DAILY_DIR" ]]; then
  log "ERROR: $DAILY_DIR not found"
  exit 1
fi

cd "$DAILY_DIR"

# Find candidate files: direct children .md, mtime > RETENTION_DAYS
candidates=$(find . -maxdepth 1 -type f -name "*.md" -mtime +${RETENTION_DAYS})

if [[ -z "$candidates" ]]; then
  log "No daily logs older than ${RETENTION_DAYS} days. Clean."
  exit 0
fi

log "Found $(echo "$candidates" | wc -l) file(s) older than ${RETENTION_DAYS} days:"
echo "$candidates" | while read -r f; do
  age_days=$(( ( $(date +%s) - $(stat -c %Y "$f") ) / 86400 ))
  log "  [$(printf '%3d' "$age_days")d] $(basename "$f")"
done

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY RUN — no files deleted. Set DRY_RUN=false to execute."
  exit 0
fi

# Actual deletion
deleted=0
echo "$candidates" | while read -r f; do
  if rm -f "$f"; then
    log "  DELETED: $(basename "$f")"
    ((deleted++))
  else
    log "  FAILED: $(basename "$f")"
  fi
done

log "Cleanup complete. Deleted: $deleted file(s)"
exit 0
