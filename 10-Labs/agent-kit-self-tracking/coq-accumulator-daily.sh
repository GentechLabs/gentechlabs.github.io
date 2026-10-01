#!/bin/bash
# COQ accumulator — dip-aware buy & hold (Jordan's design, Sep 12 2026).
#
# "you'll make the purchase at the right time... catch the pullbacks"
# Runs DAILY, holds a $5/week budget, buys when COQ is down >=3% in 24h,
# with a Sunday fallback so a budget is never silently skipped.
#
# Funding: idle WAVAX + native AVAX above the gas reserve.
# NEVER touches farm position #3479882.
# Silence doctrine: emits nothing unless it bought or something changed.
cd /root/.hermes/profiles/gentech-treasury/scripts || exit 0
python3 coq_accumulator.py --execute --quiet --source lp 2>&1
