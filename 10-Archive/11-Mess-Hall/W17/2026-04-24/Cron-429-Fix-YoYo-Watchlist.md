# YoYo Watchlist Cron Fix — 2026-04-24

**Problem:** YoYo's Crypto Watchlist + LP Monitor (`faed4f588aef`) was hitting 429 rate limits. Schedule was `0 7-21 * * *` (top of every hour, 15x/day) colliding with all other crons.

**Fix applied:**
- Job replaced with hardened version (`e00b46103b08`)
- Model: `glm-5.1` → `kimi-k2.6`
- Schedule: `every 120m` → `15 8,12,16,20 * * *` (4x/day, :15 past the hour)
- 4 runs/day, offset 15 min avoids cron collisions
- Next run: 12:15 PM

**Verification:** Wait for 12:15 run. If clean → close this.
