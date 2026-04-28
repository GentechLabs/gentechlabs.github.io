# 🔐 API Key Updates — 2026-04-28

## CoinMarketCap API Key
- **Key:** Stored in `/root/.hermes/scripts/cmc_config.json`
- **Updated by:** Jordan, April 28, 2026
- **Status:** ✅ Active and verified

### Files Updated
1. `/root/.hermes/scripts/cmc_config.json` — primary config (JSON)
2. `d5-master-cron.py` — now reads from cmc_config.json (no hardcoded key)
3. `crypto-price-fetch` skill — updated in gentech, yoyo, dmob profiles
4. `cmc-watchlist.py` — new hourly watchlist script (reads from cmc_config.json)

### Key Rotation Notes
- All scripts read from `/root/.hermes/scripts/cmc_config.json` as primary source
- Fallback: `CMC_API_KEY` env var
- When rotating: update cmc_config.json only — all scripts pick it up automatically

---

## Related Files
- Cron manifest: `03-Strategies/cron-jobs.md`
- Watchlist config: `03-Strategies/cron-watchlist-config.md`
- Watchlist script: `/root/.hermes/scripts/cmc-watchlist.py`
