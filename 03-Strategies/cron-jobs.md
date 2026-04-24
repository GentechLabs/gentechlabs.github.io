# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-24
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: All jobs → Strategies group (-1002916759037)

---

## 📊 Crypto Watchlist
**Job ID:** `675ae691c53e`
**Schedule:** Every 2 hours (7, 9, 11, 13, 15, 17, 19, 21)
**Status:** ✅ Active

- CMC API prices: BTC, ETH, AVAX, SOL, LINK + token-watchlist.md
- Includes LP pool status (consolidated — no separate LP message)
- Macro "why" context (1-2 lines)
- On-chain signal → `keccak256("CMC_WATCHLIST")` to SharedMemory

---

## 💧 LP Watchlist (AVAX/USDC) — Combined with Crypto Watchlist
**Job ID:** `faed4f588aef`
**Schedule:** `15 8,12,16,20 * * *` (4x/day: 8:15, 12:15, 16:15, 20:15 UTC)
**Model:** `kimi-k2.6`
**Status:** ✅ Active (fixed Apr 24 — reduced from 15x/day to avoid 429 rate limits)

| Field | Value |
|-------|-------|
| Pool | LFJ V2.2 (binStep 10) |
| Address | `0x864d4e5Ee7318e97483DB7EB0912E09F161516EA` |
| Range | $9.10 — $9.65 |
| Shape | Curve |
| Position Entry | $31.16 (Mar 31) |
| Tracker Script | `lp-unified-monitor.py` (consolidated watchlist + P&L) |
| Position File | `~/.hermes/scripts/.lfj-position-tracker.json` |

**Report includes:**
1. Crypto watchlist (BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM)
2. LP pool health (volume, liquidity, APR, range status)
3. Position P&L (entry, IL, fees, net, vs HODL)
4. Weekly deep-dive triggers (>5% AVAX move or Sundays)

**Alert Logic:**
- 75-100% efficiency → 🤫 Silent
- <75% efficiency → ⚠️ "Consider rebalancing"
- Out of range → 🚨 URGENT alert

**Consolidation Rule:**
During Crypto Watchlist hours (7,9,11,13,15,17,19,21), LP is SILENT unless URGENT (out of range).

**On-chain signal:** `keccak256("AVAX_LP_MONITOR")` → SharedMemory

---

## ⏸️ Overnight Pause/Resume
Handled internally by `faed4f588aef` quiet-hours logic (11 PM – 6:30 AM EDT). No separate pause/resume jobs needed.

---

## All Jobs (30 active across all departments)

| # | Name | Schedule | Delivery |
|---|------|----------|----------|
| 1 | Master Morning Digest | 11:30 AM daily | HQ |
| 2 | Gentech LLC Reminder | 15th of month | HQ |
| 3 | Mess Hall — Agent Check-in | 2:00 PM daily | HQ |
| 4 | End of Shift Wrap-Up | 4:30 PM Thu-Sat | HQ |
| 5 | Vault Maintenance — Weekly | Sun 10:30 PM | HQ |
| 6 | **YoYo — Crypto Watchlist + LP** | 8:15, 12:15, 16:15, 20:15 UTC | Strategies |
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
| 17 | Brain Backup | Every 6h | Local |
