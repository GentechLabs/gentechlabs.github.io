#!/bin/sh
# fee-ledger.sh — build the fee ledger history, silently. (Jordan, 2026-09-23)
#
# The ledger answers "what is this position actually EARNING?", which LFJ V2.2 makes
# unanswerable on demand: fees are auto-compounded into the bins, so there is no counter to
# read. It can only be measured as GROWTH over time -- so it needs snapshots taken regularly,
# and there is no point in a snapshot that announces itself every 15 minutes.
#
# Prints NOTHING on a normal run (stdout is delivered verbatim by the cron) and only speaks
# when a tenant's position cannot be read at all -- which would silently freeze the history.
set -u
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="/root/vaults/gentech/11-Mess Hall/fee-ledger.log"
mkdir -p "$(dirname "$LOG")"

for TENANT in jordan dadrian; do
    OUT="$(STEWARD_TENANT="$TENANT" timeout 280 python3 "$SCRIPTS_DIR/fee_ledger.py" \
             --tenant "$TENANT" 2>&1)"
    RC=$?
    printf '%s  %s  rc=%s\n%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$TENANT" "$RC" "$OUT" >> "$LOG"
    # speak ONLY on a real failure: a flat book or a missing tenant is normal, not news
    if [ $RC -ne 0 ]; then
        echo "⚠️ fee-ledger: $TENANT snapshot failed (rc=$RC) — history is not accumulating"
        echo "$OUT" | tail -3
    fi
done
exit 0
