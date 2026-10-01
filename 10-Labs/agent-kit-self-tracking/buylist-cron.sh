#!/bin/bash
# buylist-cron.sh — cron wrapper for the Steward Buy List / Watch List.
#
# WHY A WRAPPER (Jordan, Sep 16 2026): "I wanted it to run from 7 a.m. to 9 p.m."
#
# Two things have to agree for that window to actually hold:
#   1. The CRON SCHEDULE, which is fixed UTC. 7am-9pm ET spans 11:00-01:00 UTC in
#      summer (EDT) but 12:00-02:00 UTC in winter (EST). A single UTC cron cannot
#      track DST, so the job is scheduled over the UNION (11:00-02:00 UTC) and the
#      quiet-hours guard trims the seasonal extra hour on each end.
#   2. The QUIET-HOURS GUARD inside steward-buylist.py, which defaults to
#      22:00-08:00 ET. That default BLOCKS a 7am run — which is exactly how the
#      old 11:00 UTC slot became a dead slot that could never fire. This wrapper
#      narrows the window to 22:00-07:00 ET so 7am is live and 9pm is still the
#      last run of the day.
#
# RESULT: 15 genuine runs/day, 7:00am-9:00pm ET, year-round.
#   summer (EDT): 11:00 UTC = 07:00 ET  ...  01:00 UTC = 21:00 ET  (02:00 UTC == 22:00 ET, guarded)
#   winter (EST): 12:00 UTC = 07:00 ET  ...  02:00 UTC = 21:00 ET  (11:00 UTC == 06:00 ET, guarded)
set -uo pipefail
D="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
export QUIET_START=22
export QUIET_END=7
exec python3 "$D/steward-buylist.py"
