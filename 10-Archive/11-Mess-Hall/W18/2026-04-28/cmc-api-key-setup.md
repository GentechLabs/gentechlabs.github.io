---
type: mess-hall
created: 2026-04-28T16:35:00-04:00
author: YoYo
tags: [strategies, crypto, cmc, api, cron]
---

# 📊 CMC API Key Setup & Cron Update

**Status:** ✅ Complete
**Time:** 4:35 PM EDT

## What Changed

### 1. CMC API Key Saved
- **Location:** `/root/.hermes/profiles/yoyo/secrets/cmc_api_key.txt`
- **Config:** `/root/.hermes/scripts/cmc_config.json`
- **Permissions:** 600 (secure)

### 2. Cron Job Updated
- **Job:** YoYo — Crypto Watchlist (`faed4f588aef`)
- **Old Schedule:** 10am, 12pm, 2pm, 4pm, 6pm, 8pm, 10pm
- **New Schedule:** Every hour from 7 AM to 9 PM (`0 7-21 * * *`)
- **Smart Skip:** Skips if all tokens moved < 0.5%
- **Alert Threshold:** 3%+ move

### 3. Documentation Updated
- `/root/vaults/gentech/03-Strategies/cron-watchlist-config.md` — Watchlist config with API details
- `/root/vaults/gentech/03-Strategies/cmc-api-key-setup.md` — Full API key reference
- `/root/.hermes/skills/finance/crypto-price-fetch/SKILL.md` — Skill updated with key management

## Files Modified
- ✅ `d5-master-cron.py` — API key verified working
- ✅ `cmc_config.json` — Config file has correct key
- ✅ `cmc-watchlist-config.md` — Updated with new schedule
- ✅ `cmc-api-key-setup.md` — New reference doc

## For Other Agents
- **DMOB:** Use `cmc_config.json` for CMC API access
- **Desmond:** Key stored in secrets directory, not in chat
- **Gentech:** All cron jobs using CMC key are updated

## Security
- API key redacted in cron logs
- Never commit to git
- Rotate if compromised

---

*YoYo — Strategies Department*
