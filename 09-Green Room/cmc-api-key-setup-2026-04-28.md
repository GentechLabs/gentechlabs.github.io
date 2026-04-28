# CMC API Key Setup — April 28, 2026

## Overview
Jordan provided new CoinMarketCap API key for crypto watchlist monitoring.

## Key Storage Locations
1. `/root/vaults/gentech/00-HQ/config/cmc-api-key.env` — Primary vault storage
2. `/root/.hermes/scripts/cmc_config.json` — Script config
3. `~/.hermes/.env` — Environment file
4. `~/.bashrc` — Exported as environment variable

## Updated Files
- `03-Strategies/scripts/d5-master-cron.py` — Updated API key (was truncated)
- `03-Strategies/scripts/d5-master-cron.py.bak-2026-04-27` — Updated backup
- `~/.hermes/scripts/cmc-watchlist.py` — New hourly monitor script

## Cron Jobs
| Job | Schedule | Script | State File |
|-----|----------|--------|------------|
| YoYo — Crypto Watchlist (862ae0c1f85d) | `0 7-21 * * *` | cmc-watchlist.py | .cmc-watchlist-hourly-state.json |
| D5 Master Cron | Multiple/day | d5-master-cron.py | .cmc-watchlist-state.json |

## Behavior
- Hourly from 7 AM to 9 PM
- Skips if all tokens moved < 1.5% since last check
- Fallback to CoinGecko if CMC fails

## Watchlist
BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM, COQ, ARENA, PROPS, LAND, XAG
