# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-04-28 (Desmond — synced with actual cron scheduler)
> Models: YoYo/Gentech/Desmond → `kimi-k2.6` | DMOB → `qwen3-coder-next` | Provider: Ollama Cloud
> Delivery: Strategies group (-1002916759037)
>
> **Standard:** All cron jobs follow `01-Agency/cron-job-standards.md` (human-readable prompts, no code blocks, no agent roleplay).

---

## 📊 Active Cron Jobs (as of 2026-04-28)

### 1. 🏆 YoYo — LP Position Monitor + Alerts
**Job ID:** `8ae8a04f3b71`
**Schedule:** `*/10 6-23 * * *` (every 10 min, 6 AM–11 PM UTC)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — working

**What it does:** Monitors LFJ AVAX/USDC LP position with fee efficiency tracking, range alerts, and micro-DCA triggers.

---

### 2. 📈 YoYo — DeFi Dashboard
**Job ID:** `33b3c40539b2`
**Schedule:** `0 9,15,21 * * *` (3×/day at 9 AM, 3 PM, 9 PM UTC)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — recreated 2026-04-28 (old job `66e224d2a6bd` was dropped from scheduler)

**What it does:** Comprehensive DeFi dashboard combining LP position status, watchlist prices, market context (Fear & Greed, BTC dominance), and actionable insights.

---

### 3. 📊 YoYo — DeFi Milestone (Fee Efficiency Tracker)
**Job ID:** `2563e78bcf72`
**Schedule:** `0 * * * *` (hourly)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — updated 2026-04-28 with conditional alerting

**What it does:** Hourly fee efficiency monitor. **Only delivers output when fee efficiency trends below 30%.** Otherwise silent ("STATUS:OK"). When below threshold, includes rebalance recommendation with liquidity shape and range.

**Updated Apr 28 per Jordan:** Fee efficiency trending < 30% = alert only. Rebalance rec includes shape analysis (bottom-heavy, balanced, top-heavy) and suggested range with reasoning.

---

### 4. 📊 YoYo — Crypto Watchlist
**Job ID:** `915b1df66348`
**Schedule:** `30 4-16/2 * * *` (every 2 hours, 4:30 AM–4:30 PM UTC)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — working

**What it does:** Crypto watchlist update from CoinMarketCap/DexScreener data.

---

### 5. 📊 CMC Watchlist + Market News
**Job ID:** `862ae0c1f85d`
**Schedule:** `every 120m` (every 2 hours)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — new, awaiting first scheduled run
**Skills:** obsidian

**What it does:** Crypto watchlist check with market news context.

---

### 6. 📊 Gentech — Crypto Watchlist Hourly
**Job ID:** `f930f56d082a`
**Schedule:** `0 11-23,0 * * *` (hourly, 7 AM – 9 PM ET)
**Delivery:** HQ (origin)
**Script:** `cmc-watchlist.py`
**Status:** ✅ Active — created 2026-04-28

**What it does:** Hourly crypto watchlist via CMC API. Skips reporting if no coin moved >1.5% since last check. Only pings when there's meaningful movement.

**Coins:** BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM
**Skip threshold:** <1.5% movement = silent one-liner
**Report threshold:** ≥1.5% movement OR any coin >2% in 24h

---

### 7. 🔍 DMOB — Hackathon & Bug Bounty Scout
**Job ID:** `27a3c4947359`
**Schedule:** `0 10,18 * * *` (2×/day at 10 AM, 6 PM UTC)
**Delivery:** DMOB group (-1003872552815)
**Status:** ✅ Active — new, awaiting first scheduled run

**What it does:** Scans for upcoming hackathons and bug bounty opportunities.

---

### 6. 🔧 Weekly Skills Update Check
**Job ID:** `b8ef24caa3d0`
**Schedule:** `30 13 * * 0` (Sunday 1:30 PM UTC)
**Delivery:** HQ (origin)
**Script:** `skills-update-check.py`
**Status:** ✅ Active — new, next run May 3

**What it does:** Checks for Hermes core updates and bundled skill changes. Writes approval list to vault.

---

## ⏸️ Retired / Merged

| Job ID | Profile | Name | Reason |
|--------|---------|------|--------|
| `66e224d2a6bd` | YoYo | DeFi Dashboard (old) | Dropped from scheduler; recreated as `33b3c40539b2` |
| `44f7c2028766` | DMOB | DeFi Milestone + LP Monitor | Consolidated into YoYo |
| `0b2beec3f702` | Desmond | LP Position Monitor + Alerts | Consolidated into YoYo |
| `bce87f59b79e` | YoYo | CMC Watchlist (old) | Replaced with DexScreener-based |
| `faed4f588aef` | YoYo | Daily LP + D5 (old) | Replaced by consolidated tracker |
| `b2bb2bae4fc5` | DMOB | LP Range Monitor | Previously consolidated |
| `504ac01d54ed` | YoYo | Daily LP + D5 (never ran) | Previously consolidated |
|| `2563e78bcf72` | YoYo | DeFi Milestone (Fee Efficiency Tracker) | Reinstated Apr 28 — conditional alerting |
| `1f10f10b2a07` | YoYo | CMC Crypto Watchlist (canonical) | ID no longer in scheduler |

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

*Canonical LP monitor: YoYo job `8ae8a04f3b71` — runs every 10 min. DeFi Dashboard: YoYo job `33b3c40539b2` — runs 3×/day.*
