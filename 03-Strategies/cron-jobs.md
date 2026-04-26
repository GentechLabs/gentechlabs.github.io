# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-26
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: Strategies group (-1002916759037)
>
> **Standard:** All cron jobs follow `01-Agency/cron-job-standards.md` (human-readable prompts, no code blocks, no agent roleplay).

---

## 📊 Strategies Cron Jobs

### D5 Unified Master Cron (CMC + LP Milestones)
**Job ID:** `7180d8a26738`
**Schedule:** `15 8,12,16,20 * * *` (4×/day: 8:15, 12:15, 16:15, 20:15 ET)
**Script:** `scripts/d5-master-cron.py`
**Status:** ✅ Active — sole Strategies cron

**Scope:** Consolidated report. One script covers everything Jordan needs:
- CMC watchlist for 7 tokens (BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM)
- D5 Milestone LP report (AVAX/USDC on LFJ/TraderJoe)
- Shape-aware DCA sizing ($50→$30→$20→$10)
- Tier progression ladder with progress bars
- Compound threshold tracking

**Silent rules:** 🤐 Only speaks if:
- Any CMC token moves ≥3% in 24h
- LP out of range OR efficiency <50%
- Monday DCA day
- Compound threshold crossed ($50)
- Script error

**State files:**
- Watchlist: `~/.hermes/scripts/.cmc-watchlist-state.json`
- D5 LP: `~/.hermes/scripts/.lfj-aae-state.json`

---

## ⏸️ Retired Cron Jobs

| Job ID | Name | Reason |
|--------|------|--------|
| `bce87f59b79e` | YoYo — CMC Crypto Watchlist | **Retired** — merged into unified D5 Master Cron (`7180d8a26738`) |
| `faed4f588aef` | YoYo — Daily LP + D5 Milestone | **Retired** — merged into unified D5 Master Cron (`7180d8a26738`) |

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

