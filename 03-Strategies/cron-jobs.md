# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-27
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: Strategies group (-1002916759037)
>
> **Standard:** All cron jobs follow `01-Agency/cron-job-standards.md` (human-readable prompts, no code blocks, no agent roleplay).

---

## 📊 Strategies Cron Jobs (Consolidated)

### 🏆 DeFi Milestone + LP Tracker (Consolidated)
**Job ID:** `0b2beec3f702`
**Name:** YoYo — DeFi Milestone + LP Tracker (Consolidated)
**Schedule:** `25 8,12,16,20 * * *` (4×/day at 8:25, 12:25, 4:25, 8:25 ET)
**Script:** Inline prompt (consolidated — all rules in cron prompt)
**Status:** ✅ Active — canonical LP + milestone monitor

**Consolidated from (Apr 27):**
| Former Job | Function |
### 🏆 DeFi Milestone + LP Monitor (Canonical — Consolidated)
**Job ID:** `2563e78bcf72`
**Name:** YoYo — DeFi Milestone + LP Monitor
**Schedule:** `25 8,12,16,20 * * *` (4×/day at :25 past, ET)
**Script:** `lp-aae-signal-monitor.py` (AAE Signal Monitor v2)
**Status:** ✅ Active — canonical LP + milestone monitor

**Consolidated from:**
| Former Job | ID | Reason Removed |
|------------|-----|----------------|
| LP Fee Efficiency Monitor | `c2c2e40b440e` | Merged into this job (was every 10 min) |
| DeFi Milestone Tracker | `2563e78bcf72` | Updated to include LP fee rules |

**What it does:**
1. Fetches live pool data (Birdeye x402 → DexScreener → on-chain RPC fallback)
2. Calculates fee efficiency + position status (in/out of range) with shape awareness
3. Tracks D5 Milestone progression (Scout $5/day → Raider $20 → Warlord $55 → Sovereign $200)
4. Micro-DCA triggers based on efficiency thresholds
5. Compound threshold tracking ($50)
6. TVL trend monitoring (7-day)

**LP Fee Monitoring Rules (Jordan's Spec):**
- **SILENT:** In range + efficiency ≥ 50% + no action → no Telegram alert
- **OK:** Compound ready / DCA day / milestone hit → Telegram notification
- **ALERT:** Out of range OR efficiency < 50% → alert + suggest rebalance
- **CRITICAL:** Efficiency < 30% or price crash → immediate alert
- **Quiet hours:** 11 PM – 6:30 AM ET → no alerts
- **Recovery alert:** Price returns to range after being out

**Micro-DCA Triggers:**
| Efficiency | Flag | Bonus DCA | Action |
|-----------|------|-----------|--------|
| 60–50% | 🟡 Yellow | $0 | Watch only |
| 50–40% | 🟠 Orange | $10 | Micro-DCA + monitor |
| 40–30% | 🔴 Red | $20 | Consider rebalance |
| <30% | 🔴 Critical | $20 + rebalance | Shift range immediately |

**State files:**
- Config: `~/.hermes/scripts/.lfj-aae-config.json`
- State: `~/.hermes/scripts/.lfj-aae-state.json`

---

### 📈 CMC Crypto Watchlist
**Job ID:** `1f10f10b2a07`
**Name:** YoYo — CMC Crypto Watchlist
**Schedule:** `15 8,12,16,20 * * *` (4×/day)
**Script:** `~/.hermes/scripts/dexscreener-watchlist.py` (DexScreener-based, no CMC key needed)
**Status:** ✅ Active

**Watchlist (7 tokens):** BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM
**Silent:** Only reports if any token moves ≥3% in 24h

---

## ⏸️ Retired / Merged

| Job ID | Name | Reason |
|--------|------|--------|
| `bce87f59b79e` | CMC Watchlist (old) | Replaced by `862ae0c1f85d` with DexScreener |
| `faed4f588aef` | Daily LP + D5 (old) | Replaced by `0b2beec3f702` consolidated tracker |
| `0b2beec3f702` (old) | LP Position Monitor (every 10 min) | Consolidated into DeFi Milestone + LP Tracker |

---

## 🔮 Pipeline: Next LP Pool Research

**Per Jordan (2026-04-27):**
- LINK → **spot buy only** (too volatile for LP)
- Next pool research targets: **LAND / LSRWA** (tokenized real estate / RWA)

**To research:**
- [ ] Identify LAND or LSRWA pool on supported DEX (LFJ, Uniswap V3)
- [ ] Check pool depth >$100k, volume >$10k/24h
- [ ] Verify V2/V3 CL support (bidirectional/spot shapes available)
- [ ] Evaluate cross-chain viability (Avalanche vs Arbitrum/Solana)
- [ ] Port `lp-default-tracker.py` logic to new pool slot

---

## All Jobs (active across all departments)

| # | Name | Schedule | Delivery |
|---|------|----------|----------|
| 1 | Omni-Summary Master Brief | 11:30 AM daily | HQ |
| 2 | Gentech LLC Reminder | 15th of month | HQ |
| 3 | Mess Hall — Agent Check-in | 2:00 PM daily | HQ |
| 4 | End of Shift Wrap-Up | 8 PM Sun–Tue | HQ |
| 5 | Vault Maintenance — Weekly | Sun 10:30 PM | HQ |
| 6 | **DeFi Milestone LP Tracker** | 10:00 AM daily | Strategies |
| 7 | **CMC Crypto Watchlist** | 4×/day | Strategies |
| 8 | Protocol Due Diligence | Thu 6:00 AM | Strategies |
| 9 | x402 Ecosystem Monitor | Every 14 days | Strategies |
| 10 | LayerZero DVN Monitor | 9:00 AM daily | Strategies |
| 11 | Hermes Agent Daily Sync | 6:00 AM daily | Labs |
| 12 | Weekly Opportunity Scanner | Mon/Thu 6 AM | Labs |
| 13 | Kite AI Hackathon Check | 10:00 AM daily | Labs |
| 14 | Security → Content Pipeline | Tue/Fri 7 AM | Creative |
| 15 | Gentech X Content Extractor | 5:00 PM daily | Creative |
| 16 | The Brain — Daily | 4:00 PM daily | Local |
| 17 | Mess Hall — Daily Rotation | 3:00 AM daily | Local |
| 18 | Sunday Skill Update | Sun 4:00 PM | HQ |
| 19 | Vault Manager — Nightly | 11:00 PM daily | HQ |
| 20 | AAE Dashboard Data Refresh | Every 15 min | Local |

---

*Canonical LP tracker: `lp-default-tracker.py` — always run this for LP status.*
