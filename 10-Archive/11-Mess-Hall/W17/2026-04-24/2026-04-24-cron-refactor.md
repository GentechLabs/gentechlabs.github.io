# Cron Refactor — 2026-04-24

**Status:** ✅ Locked & Live

## What Changed

### Crypto Watchlist (`faed4f588aef`)
- **Was:** Combined watchlist + LP, 4× daily
- **Now:** Standalone watchlist, **every hour** 7 AM – 9 PM ET (15 runs/day)
- **Silent if:** All tokens <3% moves + no news
- **Scope:** BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM only

### D5 Milestone + LP Monitor (`268ac3d50ce9`)
- **Was:** Combined with watchlist, 4× daily
- **Now:** Unified D5 + LP, **every hour** 6:30 AM – 8:30 PM ET (15 runs/day, :30 offset)
- **Capital addition detection:** $50–$100 increase in position tracker → triggers full milestone report
- **Rebalance threshold:** <50% fee efficiency (was <75%)
- **DCA:** Only mentioned on Mondays — never reports "no DCA"
- **Silent if:** No capital added + efficiency 50–100% + not Monday + no milestone crossed

## Files Updated
- `03-Strategies/cron-jobs.md` — full manifest rewrite
- `03-Strategies/LP-Monitor-Rules.md` — rules + thresholds + schedule
- `03-Strategies/scripts/lp-unified-monitor.py` — efficiency threshold 75%→50%
- Synced to `~/.hermes/scripts/lp-unified-monitor.py`

## Next
- Jordan testing DCA — next LP run will detect capital addition and fire milestone report
