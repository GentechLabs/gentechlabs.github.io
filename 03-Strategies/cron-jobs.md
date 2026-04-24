# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-24
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: Strategies group (-1002916759037)

---

## 📊 Unified Crypto Watchlist + LP Monitor
**Job ID:** `faed4f588aef`
**Schedule:** `15 8,12,16,20 * * *` (4×/day UTC)
**Model:** `kimi-k2.6` | **Skill:** `crypto-lp-monitoring`
**Status:** ✅ Active — single source of truth

**Scope:** Market prices + LP position tracking in one report.

**Report includes:**
1. CoinGecko prices (BTC, ETH, SOL, LINK, AVAX, TAO, BEAM, XAUt)
2. 24h/7d changes + macro context
3. LP pool health (price, volume, liquidity, APR, range status)
4. Position P&L (entry, IL, fees earned, net, vs HODL)
5. Milestone progress + compound readiness

**Alert Logic:**
- 75-100% efficiency → 🤫 Silent (1-line LP status included)
- <75% efficiency → ⚠️ "Consider rebalancing"
- Out of range → 🚨 URGENT
- Milestone hit → 🏆 Celebration alert

**Data Sources:**
- Prices: CoinGecko (User-Agent header)
- LP: `lp-unified-monitor.py` (Birdeye → DexScreener fallback)
- Position: `~/.hermes/scripts/.lfj-position-tracker.json`
- Range updated dynamically from screenshot snapshots

**On-chain signals:**
- `keccak256("CMC_WATCHLIST")` → SharedMemory
- `keccak256("AVAX_LP_MONITOR")` → SharedMemory

**Master source:** `03-Strategies/token-watchlist.md`

---

## ⏸️ Overnight Pause/Resume
Handled internally by `lp-unified-monitor.py` quiet-hours logic (11 PM – 6:30 AM EDT).

---

## Screenshot → LP Update Workflow
When Jordan sends LP screenshots:
1. Extract data (price, balance, AVAX/USDC amounts, fees, range)
2. Update `~/.hermes/scripts/.lfj-position-tracker.json` with new snapshot
3. Update `03-Strategies/LFJ-AVAX-USDC-5bps-Analysis.md` with latest data
4. The unified cron job reads from the JSON automatically on next run

---

## All Jobs (active across all departments)

| # | Name | Schedule | Delivery |
|---|------|----------|----------|
| 1 | Master Morning Digest | 11:30 AM daily | HQ |
| 2 | Gentech LLC Reminder | 15th of month | HQ |
| 3 | Mess Hall — Agent Check-in | 2:00 PM daily | HQ |
| 4 | End of Shift Wrap-Up | 4:30 PM Thu–Sat | HQ |
| 5 | Vault Maintenance — Weekly | Sun 10:30 PM | HQ |
| 6 | **YoYo — Unified Watchlist + LP** | 8:15, 12:15, 16:15, 20:15 UTC | Strategies |
| 7 | Protocol Due Diligence | Thu 6:00 AM | Strategies |
| 8 | Hermes Agent Daily Sync | 6:00 AM daily | Labs |
| 9 | Weekly Opportunity Scanner | Mon/Thu 6 AM | Labs |
| 10 | Kite AI Hackathon Check | 10:00 AM daily | Labs |
| 11 | Security → Content Pipeline | Tue/Fri 7 AM | Creative |
| 12 | Gentech X Content Extractor | 5:00 PM daily | Creative |
| 13 | The Brain — Daily | 4:00 PM daily | Local |
| 14 | Mess Hall — Daily Rotation | 3:00 AM daily | Local |
| 15 | Sunday Skill Update | Sun 10:00 AM | HQ |
| 16 | Vault Manager — Nightly | 11:00 PM daily | HQ |
| 17 | Brain Backup | Every 6h | Origin |
