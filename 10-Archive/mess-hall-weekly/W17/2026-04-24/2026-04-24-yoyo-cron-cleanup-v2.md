# YoYo Cron Cleanup v2 — Apr 24, 2026

## Problem
Gentech created duplicate LP monitoring cron jobs while trying to patch YoYo:
- `cfa8d1c19357`: "DeFi Milestone + LP Monitor" (hourly, origin)
- `8e346e3e2439`: "DeFi Milestone + LP Monitor" (daily 10:00, Strategies)
- `faed4f588aef`: Existing unified job (4x/day, Strategies) — THE ONE

## Actions Taken
1. Removed `cfa8d1c19357` (duplicate, hourly → rate limit risk)
2. Removed `8e346e3e2439` (duplicate, daily → redundant)
3. Updated `faed4f588aef` to be the single source of truth:
   - Unified prompt (watchlist + LP + milestones)
   - Skill: `crypto-lp-monitoring`
   - Schedule: `15 8,12,16,20 * * *` (4x/day UTC)
   - Model: `kimi-k2.6`
   - Delivery: `telegram:-1002916759037`
4. Rewrote `03-Strategies/cron-jobs.md` to match actual state

## Final State
- **1 YoYo cron job** — `faed4f588aef`
- **4x/day** watchlist + LP reports
- **Next run:** 16:15 UTC (today)
- **No duplicate LP alerts**

## Files Modified
- `~/.hermes/scripts/.lfj-position-tracker.json`
- `03-Strategies/LFJ-AVAX-USDC-5bps-Analysis.md`
- `03-Strategies/cron-jobs.md`
- `03-Strategies/scripts/lp-unified-monitor.py`
