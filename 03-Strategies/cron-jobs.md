# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-25
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: Strategies group (-1002916759037)

---

## 📊 Crypto Watchlist (DexScreener)
**Job ID:** `bce87f59b79e`
**Schedule:** `0 * * * *` (hourly)
**Model:** `kimi-k2.6` | **Skill:** none (script-driven)
**Status:** ✅ Active

**Scope:** Silent price monitoring using DexScreener pool data. Only alerts on significant moves.

**Logic:**
- Fetches BTC, ETH, SOL, LINK, AVAX, TAO, BEAM, XAUt from DexScreener search API
- Picks highest-liquidity USD-stable pair for each token
- Falls back to CoinGecko if DexScreener has no coverage
- Compares 24h change against 3% threshold
- Tracks last-reported prices to avoid spam on sustained moves

**Silent rules:**
- All moves < 3% → no message
- Same token already reported today at similar price → no message
- Script error → ⚠️ alert

**Script:** `~/.hermes/scripts/dexscreener-watchlist.py`
**State:** `~/.hermes/scripts/.watchlist-state.json`

---

## 💹 LP Monitor
**Job ID:** `faed4f588aef`
**Schedule:** `15 8,12,16,20 * * *` (4×/day UTC)
**Model:** `kimi-k2.6` | **Skill:** `crypto-lp-monitoring`
**Status:** ✅ Active — LP-only since Apr 24 split

**Scope:** LFJ AVAX/USDC position health only. No watchlist prices.

**Report includes:**
1. AVAX price vs range (loaded dynamically from tracker JSON)
2. Fee efficiency (%)
3. Pool health (TVL, volume, APR from DexScreener)
4. Position status: in-range / out-of-range / low-efficiency

**Alert Logic:**
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
