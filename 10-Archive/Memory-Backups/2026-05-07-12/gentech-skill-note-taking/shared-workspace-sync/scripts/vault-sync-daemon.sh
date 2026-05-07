#!/bin/bash
# Obsidian vault sync daemon with exponential backoff
# Runs obsidian-headless sync in a loop, handling transient failures

set -e

# Configuration
VAULT_NAME="GenTech-Brain"  # Change to your vault name
SYNC_INTERVAL=30           # Seconds between successful syncs
MAX_BACKOFF=300            # Max backoff in seconds (5 min)
LOG_FILE="/var/log/ob-sync.log"

# Ensure log file exists and is writable
touch "$LOG_FILE"

backoff=1

while true; do
    timestamp=$(date -Iseconds)
    echo "[$timestamp] Starting sync..." >> "$LOG_FILE"

    if ob sync --vault "$VAULT_NAME" 2>&1 >> "$LOG_FILE"; then
        echo "[$timestamp] Sync successful" >> "$LOG_FILE"
        backoff=1  # Reset on success
        sleep "$SYNC_INTERVAL"
    else
        echo "[$timestamp] Sync failed, backing off ${backoff}s" >> "$LOG_FILE"
        sleep "$backoff"
        backoff=$(( backoff * 2 ))
        if [ "$backoff" -gt "$MAX_BACKOFF" ]; then
            backoff="$MAX_BACKOFF"
        fi
    fi
done