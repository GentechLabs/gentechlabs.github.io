#!/bin/bash
# reentry-watch.sh — the paired RE-ENTRY signal: BLACK health + price rainbow vs the farm.
#
# WHY (Jordan, Sep 15 2026): "the black health watch, that's to see when we should
# re-enter. You could probably add that to the DeFi rainbow — pair it up with the
# farm that we're in, and that way we can see how much more fees we could earn by
# buying at a cheaper price."
#
# Two rainbows, two questions, ONE briefing:
#   black_health.py  -> is the venue still worth re-entering? (emissions runway, TVL vs volume)
#   reentry_yield.py -> what does re-entering at each dip level actually get us?
# Silence doctrine: black_health is quiet unless something changed; the rainbow always
# prints its plan (it is a decision input, not an alert).
set -uo pipefail
D="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
echo "════════ RE-ENTRY WATCH ════════"
echo
echo "── VENUE HEALTH (should we re-enter at all?) ──"
python3 "$D/black_health.py" 2>&1
echo
echo "── ENTRY PLAN (what each dip level buys) ──"
python3 "$D/reentry_yield.py" 2>&1
