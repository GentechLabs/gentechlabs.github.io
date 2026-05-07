#!/bin/bash
# Hermes Cron Job Body Investigator
# Usage: ./investigate-cron-job.sh "<job-name-or-id>"
#
# When hermes cron show returns nothing, this script searches vault backups
# and active vault to reconstruct what the cron job actually does.

set -e

JOB_IDENTIFIER="${1:?Provide job name or ID as argument}"

VAULT="/root/vaults/gentech"
BACKUP_GLOB="${VAULT}/10-Archive/Memory-Backups/*/"

echo "=== Investigating cron job: ${JOB_IDENTIFIER} ==="
echo

# Step 1: Try hermes cron list to get metadata
echo "Step 1: Getting metadata from hermes cron list..."
hermes cron list | grep -i "${JOB_IDENTIFIER}" || echo "  Not found in list"

# Step 2: Search memory backups (most recent first)
echo
echo "Step 2: Searching memory backups (most recent first)..."
latest_backup=$(ls -dt ${BACKUP_GLOB} 2>/dev/null | head -1)
if [ -d "$latest_backup" ]; then
    echo "  checking ${latest_backup}..."
    rg -i --no-heading "${JOB_IDENTIFIER}" "$latest_backup" | head -20 || echo "  No match in latest backup"
else
    echo "  No backup directories found at ${BACKUP_GLOB}"
fi

# Step 3: Search active vault
echo
echo "Step 3: Searching active vault..."
rg -i --no-heading "${JOB_IDENTIFIER}" "${VAULT}" --type md | head -20 || echo "  No matches in active vault"

# Step 4: Search Mess Hall logs
echo
echo "Step 4: Searching Mess Hall logs..."
rg -i --no-heading "${JOB_IDENTIFIER}" "${VAULT}/11-Mess Hall" --type md | head -10 || echo "  No Mess Hall references"

echo
echo "=== Investigation complete ==="
echo "If you found the job body, extract:"
echo "  1. Job prompt/task text"
echo "  2. Skill or script being invoked"
echo "  3. Expected deliverables/output"
echo "then update the cron-jobs.md reference file."
