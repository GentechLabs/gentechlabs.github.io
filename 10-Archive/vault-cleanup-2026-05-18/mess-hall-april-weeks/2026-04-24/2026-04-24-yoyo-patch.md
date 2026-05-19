# YoYo Cron Patch — 2026-04-24

## Problem
Two YoYo jobs were running duplicative hourly reports to Strategies:
- `faed4f588aef`: Crypto Watchlist only
- `268ac3d50ce9`: D5 Milestone + LP Monitor only

## Fix
1. **Updated `faed4f588aef`** → Unified Crypto Watchlist + LP Monitor
   - Name: "YoYo — Unified Crypto Watchlist + LP Monitor"
   - Schedule: `15 8,12,16,20 * * *` (4× daily, avoids rate limits)
   - Prompt: merged both watchlist + LP/P&L + compound tracker into one report
   - Skill: `lp-position-tracker`
   - Model: `kimi-k2.6`
   - Delivery: Strategies group

2. **Removed `268ac3d50ce9`** → duplicate, fully merged into unified job

3. **Vault docs reconciled:**
   - `LP-Monitor-Rules.md` — cron table updated to reflect single active job
   - `cron-jobs.md` — already aligned

## Result
One clean YoYo job. Next run: **16:15 UTC** (12:15 PM EDT).
