# Mess Hall — April 28, 2026

## API Key & Watchlist Update (Gentech)

### CMC API Key
- Jordan provided new CoinMarketCap API key
- Stored in `/root/.hermes/scripts/cmc_config.json`
- Updated all scripts and skills to read from config file (no hardcoded keys)
- Verified working — AVAX price confirmed at $9.17

### New Cron Job: Crypto Watchlist Hourly
- **Job ID:** `f930f56d082a`
- **Schedule:** Hourly, 7 AM – 9 PM ET
- **Script:** `cmc-watchlist.py` (new, at `/root/.hermes/scripts/`)
- **Skip logic:** Silent if <1.5% movement since last check
- **Coins:** BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM

### Files Modified
- `/root/vaults/gentech/03-Strategies/scripts/d5-master-cron.py` — key loading
- `crypto-price-fetch` skill — gentech, yoyo, dmob profiles
- `/root/vaults/gentech/03-Strategies/cron-jobs.md` — manifest updated
- `/root/vaults/gentech/00-HQ/2026-04-28-API-Key-Update.md` — audit log

### Philippines Trip Brainstorm
- Researched flights June–September
- September cheapest ($799 SFO, $869 LAX)
- Peso at record low ₱61/$1 = great for USD holders
- Saved to `00-HQ/Philippines-Trip-Brainstorm.md`

### Market Context
- Oil spike → US markets sell-off ($500B erased pre-market)
- BTC $75,935 (-1.1%), AVAX $9.17 (+0.15%)
- PHP peso record low — good for Philippines trip
