# LP Monitor — Range Update (Apr 19)
**Date:** April 19, 2026 ~3:40 AM UTC
**Job ID:** `400f99be0cad` (recreated — old job removed during consolidation)
**Changed by:** Jordan

## What Changed
- **Shape:** Curve (was Bid-Ask)
- **Range:** $9.19 – $9.40
- **Schedule:** Every 10 min
- **Deliver:** Strategies group

## Alert Logic
- Curve: alert if price at outer edges ($9.19–$9.23 or $9.36–$9.40) = low fee efficiency
- Bid-Ask: alert if price in middle zone = low fee efficiency
- Breakout (confirmed 5 min) + back-in-range alerts
- Default: silent, CMC watchlist owns regular updates
