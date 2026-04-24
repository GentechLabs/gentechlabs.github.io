---
name: Consolidated Crypto Watchlist
category: smart-contract
description: Combined token price watchlist (CoinMarketCap) + LP pool monitoring (DexScreener) in a single cron report. Replaces separate alerts with one consolidated view.
related_skills: [lp-position-monitor]
---

# Consolidated Crypto Watchlist

Single cron job that combines **CMC token prices** with **LP pool position data** into one report. User prefers consolidated views over separate LP alerts.

## Why Consolidate

User explicitly requested merging LP monitoring into the token watchlist instead of separate alerts:
> "You could just show me the watchlist with the pool instead of showing me the LP"

Separate LP monitors (every 10min) + token watchlists create alert fatigue. One clean report every 2h is preferred.

## Architecture

```
┌──────────────────┐     ┌─────────────────────┐     ┌───────────┐
│ Cron (2h, 7A-9P) │────▶│ Python Script        │────▶│ Telegram  │
│ ~/.hermes/       │     │ CMC API + DexScreener│     │ Report    │
│ scripts/         │     │ + State File         │     │           │
└──────────────────┘     └─────────────────────┘     └───────────┘
```

### API Key Management
To prevent API failures and improve security:
- Prioritize reading the API key from the environment (`os.environ.get(\"CMC_API_KEY\")`).
- Provide a hardcoded fallback key only for emergency redundancy.

## Workflow for Updating Watchlist
1. **Identify Assets**: Extract the symbols/slugs from the user's CoinMarketCap public watchlist URL.
2. **Update Script**: Modify the `WATCHLIST_TOKENS` array in `~/.hermes/scripts/crypto-watchlist.py`.
3. **Test Execution**: Run `python3 ~/.hermes/scripts/crypto-watchlist.py` manually to verify API connectivity and formatting.
4. **Verify Cron**: Ensure the `cronjob` ID associated with the script is active and delivering to the correct Telegram group.

### DexScreener API (pool data)
- **Endpoint:** `https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}`
- **Auth:** None (public)
- **Returns:** price, volume, liquidity, priceChange, txns

## Report Format

```
📊 Crypto Watchlist — 01:04 PM EDT

Token Prices (CMC):
  🔴 AVAX: $9.1797 (-0.48% 24h)
  🔴 USDC: $0.999658 (-0.01% 24h)
  🔴 ETH: $2,303.37 (-0.28% 24h)
  🔴 CRV: $0.227639 (-0.10% 24h)

LP Pool — AVAX/USDC (TraderJoe v2.2):
  Status: ✅ IN RANGE
  AVAX Price: $9.1956
  Your Range: $9.00 – $9.40
  Fee Efficiency: 97.8%

  Pool Stats (24h):
  - Volume: $6,510,940
  - Liquidity: $3,798,585
  - Price Δ: -0.2%
  - Txns: 2,589 buys / 3,224 sells
```

## Script Structure

```python
#!/usr/bin/env python3
"""
Consolidated Crypto Watchlist + LP Pool Monitor
- CoinMarketCap API for EVM token prices
- DexScreener for LP pool data
"""

import json, os, sys, urllib.request
from datetime import datetime, timezone, timedelta

# Config
CMC_API_KEY = "<from memory>"
CMC_QUOTES_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
WATCHLIST_TOKENS = ["AVAX", "USDC", "ETH", "CRV"]
POOL_ADDRESS = "0x..."
CHAIN = "avalanche"
RANGE_LOW = 9.00
RANGE_HIGH = 9.40
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.watchlist-state.json")
```

### Key Functions
1. `fetch_cmc_prices(symbols)` — CMC quotes endpoint with API key header
2. `fetch_pool_data()` — DexScreener public endpoint
3. `calc_fee_efficiency(price)` — Curve shape position math (from LP skill)
4. `is_quiet_hours()` — EDT quiet hours check (11PM-7AM)
5. `format_price(price)` — Adaptive decimals (>$100: 2dp, >$1: 4dp, <$1: 6dp)
6. State tracking for out-of-range confirmation delays

## Cron Deployment

```python
cronjob(
    action='create',
    name='Crypto Watchlist + AVAX/USDC LP',
    schedule='0 7,9,11,13,15,17,19,21 * * *',  # every 2h, 7AM-9PM
    script='crypto-watchlist.py',
    deliver='telegram:CHAT_ID',
    prompt='Read script output and deliver as-is (already markdown formatted)...'
)
```

### Consolidation Pattern
When creating a consolidated watchlist:
1. **Pause old separate monitors** — `cronjob(action='pause', job_id=...)`
2. **Create new consolidated job** — single script with both data sources
3. **Update vault registry** — `02-Labs/cron-jobs-registry.md` + `03-Strategies/Cron-Jobs-Reference.md`
4. **Update memory** — cron job ID, schedule, token list

## Important Notes
- **No separate LP alerts** — user explicitly doesn't want them
- **Quiet hours** built into script (not cron-level pause)
- **State file** tracks out-of-range status across runs for confirmation logic
- **Stdlib only** — `urllib.request`, no pip dependencies
- **Script location:** MUST be in `~/.hermes/scripts/` (filename only in cron)

## Vault References
- Job Registry: `02-Labs/cron-jobs-registry.md`
- Cron Reference: `03-Strategies/Cron-Jobs-Reference.md`
- Script: `~/.hermes/scripts/crypto-watchlist.py`
