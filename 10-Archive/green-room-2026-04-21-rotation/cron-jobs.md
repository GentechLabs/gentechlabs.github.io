# ⏰ Cron Jobs — Master Tracker

**Last updated:** 2026-04-20
**Rule:** Update this file whenever a cron job is created, modified, or deleted.

---

## Active Jobs

### 1. CMC Watchlist + LP Report
- **Job ID:** `faed4f588aef`
- **Schedule:** Every 2h (7AM–9PM UTC)
- **Tokens:** BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM
- **LP Check:** AVAX/USDC pool `0x864d4e5Ee7318e97483DB7EB0912E09F161516EA`, range 9.00–9.40
- **Deliver:** Telegram Strategies (-1002916759037)
- **Status:** ✅ Active

### 2. LP Fee Efficiency Monitor
- **Job ID:** `c2c2e40b440e`
- **Schedule:** Every hour at :30
- **Mode:** Silent unless price near range boundary
- **Pool:** AVAX/USDC `0x864d4e5Ee7318e97483DB7EB0912E09F161516EA`, range 9.00–9.40
- **Deliver:** Telegram Strategies (-1002916759037)
- **Status:** ✅ Active

---

*Full reference: `03-Strategies/Cron-Jobs-Reference.md`*
