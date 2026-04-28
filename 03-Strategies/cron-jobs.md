# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-27 (consolidated LP + DeFi into single YoYo job)
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: Strategies group (-1002916759037)
>
> **Standard:** All cron jobs follow `01-Agency/cron-job-standards.md` (human-readable prompts, no code blocks, no agent roleplay).

---

## 📊 Strategies Cron Jobs (Consolidated)

### 🏆 DeFi Milestone + LP Monitor (Canonical)
**Job ID:** `2563e78bcf72`
**Name:** YoYo — DeFi Milestone + LP Monitor (Consolidated)
**Profile:** YoYo
**Schedule:** `25 8,12,16,20 * * *` (4×/day at 8:25, 12:25, 4:25, 8:25 ET)
**Script:** None (prompt-driven, uses DexScreener API)
**Status:** ✅ Active — sole LP + milestone cron

**Consolidated from (Apr 27):**
| Former Job | Profile | ID | Reason Removed |
|------------|---------|-----|----------------|
| DeFi Milestone + LP Monitor | DMOB | `44f7c2028766` | Merged into YoYo canonical |
| LP Position Monitor + Alerts | Desmond | `0b2beec3f702` | Merged into YoYo canonical |
| LP Fee Efficiency Monitor | YoYo | (old) | Replaced with consolidated |
| LP Range Monitor | DMOB | `b2bb2bae4fc5` | Previously merged |

**What it does:**
1. Fetches live pool data (DexScreener primary → DeFiLlama → CoinGecko fallback)
2. Calculates fee efficiency + position status (in/out of range) with Curve formula
3. LP monitoring rules (Jordan's exact spec: silent thresholds, recovery alerts, quiet hours)
4. Tracks D5 Milestone / Squad Progression (Scout $5/day → Raider $20 → Warlord $55 → Sovereign $200)
5. Micro-DCA triggers with bid-ask weighting (crash protection)
6. Compound threshold tracking ($50)
7. Market scenario detection (Bullish/Bearish/Ranging) with shape recommendations
8. DeFi milestone check from vault

**LP Fee Monitoring Rules (Jordan's Spec):**
- **SILENT:** In range + efficiency ≥ 50% + no action → no Telegram alert
- **OK:** Compound ready / DCA day / milestone hit → Telegram notification
- **ALERT:** Out of range OR efficiency < 50% → alert + suggest rebalance
- **CRITICAL:** Efficiency < 30% or price crash → immediate alert
- **Quiet hours:** 11 PM – 6:30 AM ET → no alerts
- **Recovery alert:** Price returns to range after being out
- **Silent rules:** Only alert if eff < 60%, Monday DCA, AVAX ±5% from entry, or OOR/recovery

**Micro-DCA Triggers:**
| Efficiency | Flag | Bonus DCA | USDC/AVAX Weight | Action |
|-----------|------|-----------|-----------------|--------|
| 60–50% | 🟡 Yellow | $0 | 50/50 | Watch only |
| 50–40% | 🟠 Orange | $10 | 70/30 | Micro-DCA + monitor |
| 40–30% | 🔴 Red | $20 | 80/20 | Consider rebalance |
| <30% | ⚫ Critical | $20 + rebalance | 90/10 | Shift range immediately |

**Position:** Range $9.10–$9.40 (rebalanced Apr 27), Curve shape, ~$83.37

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

| Job ID | Profile | Name | Reason |
|--------|---------|------|--------|
| `44f7c2028766` | DMOB | DeFi Milestone + LP Monitor | Consolidated into YoYo `2563e78bcf72` |
| `0b2beec3f702` | Desmond | LP Position Monitor + Alerts | Consolidated into YoYo `2563e78bcf72` |
| `bce87f59b79e` | YoYo | CMC Watchlist (old) | Replaced by `1f10f10b2a07` with DexScreener |
| `faed4f588aef` | YoYo | Daily LP + D5 (old) | Replaced by consolidated tracker |
| `b2bb2bae4fc5` | DMOB | LP Range Monitor (every 10 min) | Previously consolidated |
| `504ac01d54ed` | YoYo | Daily LP + D5 (never ran) | Previously consolidated |

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
| 6 | **DeFi Milestone + LP Monitor** | 4×/day (8:25, 12:25, 16:25, 20:25 ET) | Strategies |
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

*Canonical LP + DeFi tracker: YoYo job `2563e78bcf72` — single source of truth for LP monitoring + milestones. Consolidated Apr 27 from YoYo/DMOB/Desmond duplicates.*
