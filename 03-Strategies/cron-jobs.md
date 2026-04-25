# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-25
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: Strategies group (-1002916759037)

---

## 📊 Crypto Watchlist (DexScreener)
**Job ID:** `faed4f588aef` (YoYo — Unified Watchlist + LP Monitor)
**Schedule:** `15 8,12,16,20 * * *` (4×/day UTC)
**Model:** `kimi-k2.6` | **Skills:** `lp-position-tracker`, `crypto-watchlist-monitor`
**Status:** ✅ Active — sole watchlist cron

**Scope:** Tracks Jordan's holdings + LP position health. Silent unless significant moves or LP out of range.

**Tokens monitored:**
`BTC, ETH, SOL, LINK, AVAX, TAO, XAUt, BEAM`

**Data flow:**
- DexScreener search API → highest-liquidity USD-stable pair per token
- CoinGecko fallback if DexScreener has no coverage
- LP pool data from DexScreener (AVAX/USDC TraderJoe v2.2)

**Alert threshold:** 3% daily move for watchlist | Out-of-range or efficiency < 75% for LP

**Silent rules:**
- All moves < 3% → no message
- Same token already reported today at similar price → no message
- In-range LP + efficiency ≥ 75% → 🤐 Silent
- Script error → ⚠️ alert

**Scripts:**
- Watchlist: `~/.hermes/scripts/dexscreener-watchlist.py`
- LP tracker: `~/.hermes/scripts/lp-unified-monitor.py`
- State: `~/.hermes/scripts/.watchlist-state.json`
- LP state: `~/.hermes/scripts/.lfj-position-tracker.json`

> **Note:** A deprecated DMOB watchlist script (`crypto-watchlist.py`) using CoinMarketCap with a generic 20-token list has been archived. Only YoYo's unified watchlist remains active.

---

## 💹 LP Monitor (Unified with Watchlist)
**Job ID:** `faed4f588aef` (same as above — unified report)
**Schedule:** `15 8,12,16,20 * * *` (4×/day UTC)
**Model:** `kimi-k2.6` | **Skills:** `lp-position-tracker`, `crypto-watchlist-monitor`
**Status:** ✅ Active — merged into unified report since Apr 24

**Scope:** LFJ AVAX/USDC position health + watchlist prices in a single report.

**Report includes:**
1. Watchlist prices + 24h moves for all tracked tokens
2. AVAX price vs LP range (loaded dynamically from tracker JSON)
3. Fee efficiency (%)
4. Pool health (TVL, volume, APR from DexScreener)
5. Position status: in-range / out-of-range / low-efficiency

**Alert Logic:**
- Watchlist token moves ≥ 3% in 24h → 🚨 Alert
- In range + efficiency ≥ 75% → 🤐 Silent
- In range + efficiency < 75% → ⚠️ "Consider rebalancing"
- Out of range → 🚨 URGENT

**Data Sources:**
- Pool: `lp-unified-monitor.py` (Birdeye → DexScreener → on-chain RPC fallback)
- Position: `~/.hermes/scripts/.lfj-position-tracker.json`
- Range updated dynamically from screenshot snapshots or rebalance events
- On-chain fallback uses `getSwapOut()` + `getReserves()` directly from pool contract via Avalanche C-Chain RPC

---

## ⏸️ Overnight Pause/Resume
Handled internally by `lp-unified-monitor.py` quiet-hours logic (11 PM – 6:30 AM EDT).
Watchlist cron runs hourly regardless (but stays silent unless threshold breached).

---

## Screenshot → LP Update Workflow
When Jordan sends LP screenshots:
1. Extract data (price, balance, AVAX/USDC amounts, fees, range)
2. Update `~/.hermes/scripts/.lfj-position-tracker.json` with new snapshot
3. Update `03-Strategies/LFJ-AVAX-USDC-5bps-Analysis.md` with latest data
4. The LP cron reads from the JSON automatically on next run

---

## All Jobs (active across all departments)

| # | Name | Schedule | Delivery |
|---|------|----------|----------|
| 1 | Master Morning Digest | 11:30 AM daily | HQ |
| 2 | Gentech LLC Reminder | 15th of month | HQ |
| 3 | Mess Hall — Agent Check-in | 2:00 PM daily | HQ |
| 4 | End of Shift Wrap-Up | 8 PM Sun–Tue | HQ |
| 5 | Vault Maintenance — Weekly | Sun 10:30 PM | HQ |
| 6 | **Crypto Watchlist (DexScreener)** | Hourly | Strategies |
| 7 | **LP Monitor** | 8:15, 12:15, 16:15, 20:15 UTC | Strategies |
| 8 | Protocol Due Diligence | Thu 6:00 AM | Strategies |
| 9 | Hermes Agent Daily Sync | 6:00 AM daily | Labs |
| 10 | Weekly Opportunity Scanner | Mon/Thu 6 AM | Labs |
| 11 | Kite AI Hackathon Check | 10:00 AM daily | Labs |
| 12 | Security → Content Pipeline | Tue/Fri 7 AM | Creative |
| 13 | Gentech X Content Extractor | 5:00 PM daily | Creative |
| 14 | The Brain — Daily | 4:00 PM daily | Local |
| 15 | Mess Hall — Daily Rotation | 3:00 AM daily | Local |
| 16 | Sunday Skill Update | Sun 10:00 AM | HQ |
| 17 | Vault Manager — Nightly | 11:00 PM daily | HQ |
| 18 | Brain Backup | Every 6h | Origin |
