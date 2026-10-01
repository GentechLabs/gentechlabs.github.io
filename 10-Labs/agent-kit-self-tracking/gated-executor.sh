#!/bin/bash
# gated-executor.sh — Trade Mode: scan truth FIRST, then the capital-gated executor.
#
# Fresh-scan audit (Aug 31 2026): the scan writer was orphaned on Aug 29 while
# the executor kept reading its frozen file — Aug-23 basis numbers got replayed
# as "live" for 8 days. Fix order:
#   1. ALWAYS refresh the scan (gta-arb-monitor.py) — scan truth must never age
#      past the gate, even when the treasury is flat.
#   2. THEN run the executor behind the capital gate (gated-run.sh): flat = the
#      executor stays silent (no token spend); scan output goes to a log file,
#      never stdout, so silent-when-flat still holds.
SC="/root/.hermes/profiles/gentech-treasury/scripts"

# 1) Refresh scan truth (quiet: report text to log, errors surfaced on stderr only if scan breaks)
if ! python3 "$SC/gta-arb-monitor.py" > "$SC/.arb-scan-last-report.txt" 2>/dev/null; then
    echo "🔁 ARB SCAN FAILED — executor will skip on stale/no scan data"
    exit 1
fi

# 2) Capital-gated executor (silent when flat — empty stdout contract preserved)
exec bash "$SC/gated-run.sh" gta_executor.py