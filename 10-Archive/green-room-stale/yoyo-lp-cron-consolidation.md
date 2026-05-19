# LP Cron Consolidation — Handoff to YoYo

**From:** Jordan (via Desmond relay)
**For:** YoYo
**Date:** 2026-04-21

## Action Items

1. **Delete** cron job `c2c2e40b440e` (LP Fee Efficiency Monitor) — redundant
2. **Update** cron job `e030307a1a47` (watchlist cron):
   - Schedule change: `0 7,9,11,13,15,17,19,21 * * *` → `0 7-21 * * *` (hourly 7AM-9PM EDT)
3. **No code changes needed** — the `crypto-watchlist.py` script already has full LP monitoring baked in

## Why
The LP Fee Efficiency Monitor was running separately but the watchlist script already covers LP data. Combining into one cron simplifies the schedule and reduces noise.
