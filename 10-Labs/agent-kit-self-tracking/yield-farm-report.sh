#!/bin/bash
# yield-farm-report.sh — cron wrapper for the cross-rail YIELD FARM REPORT.
#
# Jordan (Sep 15 2026): "we can compare the different pools — the SOL/USDC pool
# versus the AVAX pool we've been in, or the TAO pool we thought about, or the
# LINK pool. This is almost like a yield farm — it really is like a yield farm
# report. We can make it its own thing."
set -uo pipefail
D="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
exec python3 "$D/yield-farm-report.py"
