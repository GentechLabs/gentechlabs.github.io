#!/bin/bash
# agentic-treasury-report.sh — cron wrapper for the AGENTIC TREASURY REPORT.
#
# Jordan (Sep 16 2026): "how the other day we made a yield farm report, we should
# also add trading to that. We can call it the agentic treasury report."
#
# ONE report, THREE layers of the treasury:
#   YIELD    — cross-rail venue comparison, capital-to-goal, rank/milestone ladder
#   TRADING  — rail basis (arb), buy-list value bands, accumulation/DCA state
#   RESEARCH — the measured price-sensitivity relationship
set -uo pipefail
D="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
exec python3 "$D/agentic-treasury-report.py"
