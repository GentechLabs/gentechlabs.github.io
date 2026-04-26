# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-26
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: Strategies group (-1002916759037)
>
> **Standard:** All cron jobs follow `01-Agency/cron-job-standards.md` (human-readable prompts, no code blocks, no agent roleplay).

---

## 📊 Consolidated Crypto Watchlist (CMC + LP Monitor)
**Job ID:** `bce87f59b79e` (YoYo — CMC Watchlist + LP Monitor)
**Schedule:** `15 8,12,16,20 * * *` (4×/day: 8:15, 12:15, 16:15, 20:15 ET)
**Model:** `kimi-k2.6` | **Script:** `cmc-watchlist.py`
**Status:** ✅ Active — sole watchlist cron (consolidated Apr 26)

**Scope:** Tracks Jordan's holdings + LP position health. Silent unless significant moves or LP out of range.

**Tokens monitored:**
- BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM (CMC prices)
- LFJ AVAX/USDC TraderJoe v2.2 (DexScreener + state tracking)

**Data flow:**
1. CMC API → quotes for 7 tokens + 1-day state tracking
2. DexScreener API → LFJ pool price, liquidity, volume
3. State file `.lfj-aae-state.json` → cumulative fees

** LP position monitoring:**
- Price vs range (9.33–9.52)
- Fee efficiency calculation (curve shape)
- In-range/Out-of-range status
- Cumulative fees tracking

**Alert threshold:** 3% daily move for watchlist | Out-of-range or efficiency < 75% for LP

**Silent rules:**
- All moves < 3% → no message
- Same token already reported today at similar price → no message
- In-range LP + efficiency ≥ 75% → 🤐 Silent
- Script error → ⚠️ alert

**State files:**
- Watchlist: `~/.hermes/scripts/.cmc-watchlist-state.json`
- LP position: `~/.hermes/scripts/.lfj-aae-state.json`
- LP tracker: `~/.hermes/scripts/.lfj-position-tracker.json`

---

## ⏸️ Disabled Cron Jobs
| Job ID | Name | Reason |
|--------|------|--------|
| `faed4f588aef` | AAE DeFi Milestone + LP Monitor | **Consolidated with `bce87f59b79e`** — daily milestone tracking merged into 4×/day consolidated report |

| Job | ID | Schedule | Status |
|-----|-----|----------|--------|
| 6 | **Consolidated Watchlist (CMC + LP)** | 4×/day | ✅ Active |
| 7 | **AAE Milestone + LP (disabled)** | — | ⏸️ Paused |

---

## All Jobs (active across all departments)

| # | Name | Schedule | Delivery |
|---|------|----------|----------|
| 1 | Master Morning Digest | 11:30 AM daily | HQ |
| 2 | Gentech LLC Reminder | 15th of month | HQ |
| 3 | Mess Hall — Agent Check-in | 2:00 PM daily | HQ |
| 4 | End of Shift Wrap-Up | 8 PM Sun–Tue | HQ |
| 5 | Vault Maintenance — Weekly | Sun 10:30 PM | HQ |
| 6 | **Consolidated Crypto Watchlist** | 4×/day | Strategies |
| 7 | **D5 Milestone Summary (Daily)** | 8:00 AM daily | Strategies |
| 8 | Protocol Due Diligence | Thu 6:00 AM | Strategies |
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

---

