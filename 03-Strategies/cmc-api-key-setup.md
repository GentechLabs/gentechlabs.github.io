---
type: reference
title: "CMC API Key Setup"
created: 2026-04-28
tags: [strategies, crypto, cmc, api, secrets]
---

# 🔑 CMC API Key Setup

## Key Location

**File:** `/root/.hermes/profiles/yoyo/secrets/cmc_api_key.txt`
**Permissions:** 600 (owner read/write only)
**Key:** `[REDACTED_CMC_KEY]`

## Config File

**Path:** `/root/.hermes/scripts/cmc_config.json`
```json
{
  "coinmarketcap_api_key": "[REDACTED_CMC_KEY]",
  "watchlist_id": "67453707ad745f0bbd4ad54f",
  "watchlist_name": "Bullish"
}
```

## Cron Jobs Using This Key

1. **YoYo — Crypto Watchlist** (`faed4f588aef`)
   - Schedule: `0 7-21 * * *` (hourly 7am-9pm)
   - Smart skip: Skips if <0.5% move
   - Alert threshold: 3%+

2. **YoYo — DeFi Milestone** (`2563e78bcf72`)
   - Schedule: `0 11-23,0-3 * * *` (hourly)
   - Uses CMC for AVAX price

## Scripts Using This Key

- `/root/vaults/gentech/03-Strategies/scripts/d5-master-cron.py`
  - Line 25: `CMC_API_KEY="[REDACTED_CMC_KEY]"`
  - Line 87: Headers use `X-CMC_PRO_API_KEY`

## Security Notes

- API key is redacted in cron logs (`[CMC-API-KEY-REDACTED]`)
- Never commit key to git
- Rotate key if compromised
- Store in secrets directory only

## Usage Example

```python
import urllib.request
import json

api_key = "[REDACTED_CMC_KEY]"
url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC&convert=USD"
req = urllib.request.Request(url, headers={
    "X-CMC_PRO_API_KEY": api_key,
    "Accept": "application/json"
})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    btc_price = data["data"]["BTC"]["quote"]["USD"]["price"]
```

---

*Created: April 28, 2026*
