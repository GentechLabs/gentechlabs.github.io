---
name: cmc-watchlist-hourly
description: "Hourly crypto watchlist monitor via CoinMarketCap API. Skips output if prices haven't moved significantly. Runs 7 AM - 9 PM."
version: 1.1.0
author: Desmond (Gentech Creative)
tags: [cmc, crypto, watchlist, monitoring, api]
---

# CMC Watchlist — Hourly Monitor

## Purpose
Automated hourly price monitoring of Jordan's "Bullish" crypto portfolio. Uses CMC API with CoinGecko fallback. Skips delivery if no meaningful price movement.

## Configuration
- **API Key Location:** `/root/vaults/gentech/00-HQ/config/cmc-api-key.env`
- **Config File:** `/root/.hermes/scripts/cmc_config.json`
- **State File:** `/root/.hermes/scripts/.cmc-watchlist-hourly-state.json`
- **Movement Threshold:** 1.5% (skips if all tokens moved less)

## Watchlist (Jordan's "Bullish" Portfolio)
| Symbol | CMC ID | Category |
|--------|--------|----------|
| BTC | 1 | Blue Chip |
| SOL | 5426 | Blue Chip |
| LINK | 1975 | Blue Chip |
| AVAX | 5805 | Avalanche Ecosystem |
| TAO | 22974 | AI/DePIN |
| XAUt | 5176 | Commodities |
| BEAM | 28298 | Avalanche Ecosystem |

## Cron Job
- **Job ID:** 862ae0c1f85d
- **Schedule:** `0 7-21 * * *` (every hour, 7 AM - 9 PM)
- **Script:** `cmc-watchlist.py`
- **Delivery:** Telegram (-1002916759037)

## Output Format
- Human-readable with Daily (24h), Weekly (7d), Monthly (30d) performance
- Emoji trends: 🟢 up, 🔴 down, ⚪ flat
- `[SILENT]` if no token moved >= 1.5% since last check

## Fallback Chain
1. CoinMarketCap API (primary)
2. CoinGecko (free, no key required)

## Related
- `d5-master-cron.py` — Combined watchlist + LP monitor (separate state file)
- `defi-lp-monitor` — LP position monitoring skill
