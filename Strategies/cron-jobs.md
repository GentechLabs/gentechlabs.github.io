# YoYo Cron Jobs — Active Manifest
> Last updated: 2026-05-02 (DMOB — consolidated duplicate LP jobs into DeFi Milestone)
> Models: All jobs → `kimi-k2.6` via `custom:opencode-go` (pinned, was inheriting broken Nous 401)
> Delivery: Strategies group (-1002916759037)
>
> **Standard:** All cron jobs follow `01-Agency/cron-job-standards.md` (human-readable prompts, no code blocks, no agent roleplay).

---

## 📊 Active Cron Jobs (as of 2026-05-02)

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

### 3. 📊 DeFi Milestone
**Job ID:** `3258c64b`
**Schedule:** `*/10 6-23 * * *` (every 10 min, 6 AM–11 PM UTC)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — consolidated 2026-05-02 (replaced duplicate LP monitoring jobs)
**Script:** `defi-lp-consolidated.py`

**What it does:** Consolidated DeFi Milestone + LP tracker with smart debouncing. Monitors LFJ AVAX/USDC position with:
- **5-minute confirmation window** on range breakouts and low-efficiency alerts (prevents transient spikes)
- **Fee efficiency zones** → dynamic DCA sizing ($50 / $30 / $20 / $10)
- **Shape-aware rebalance suggestions** (curve/spot/bidirectional analysis)
- **Bid-ask spread opportunity detection** for strategic DCA entries
- **Milestone progress tracking** integrated

**Triggers:** Only delivers output when price out of range (confirmed 5min) OR efficiency <50% (confirmed 5min) OR milestone hit. Otherwise silent.

---

### 4. 📊 YoYo — DeFi Milestone (Fee Efficiency Tracker)
**Job ID:** `2563e78bcf72`
**Schedule:** `0 * * * *` (hourly)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — updated 2026-04-28 with conditional alerting

**What it does:** Hourly fee efficiency monitor. **Only delivers output when fee efficiency trends below 30%.** Otherwise silent ("STATUS:OK"). When below threshold, includes rebalance recommendation with liquidity shape and range.

**Updated Apr 28 per Jordan:** Fee efficiency trending < 30% = alert only. Rebalance rec includes shape analysis (bottom-heavy, balanced, top-heavy) and suggested range with reasoning.

---

### 5. 📊 YoYo — Crypto Watchlist
**Job ID:** `915b1df66348`
**Schedule:** `30 4-16/2 * * *` (every 2 hours, 4:30 AM–4:30 PM UTC)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — working

**What it does:** Crypto watchlist update from CoinMarketCap/DexScreener data.

---

### 6. 📊 CMC Watchlist + Market News
**Job ID:** `862ae0c1f85d`
**Schedule:** `every 120m` (every 2 hours)
**Delivery:** Strategies (-1002916759037)
**Status:** ✅ Active — new, awaiting first scheduled run
**Skills:** obsidian

**What it does:** Crypto watchlist check with market news context.

---

### 7. 📊 Gentech — Crypto Watchlist Hourly
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

### 8. 🔍 DMOB — Hackathon & Bug Bounty Scout
**Job ID:** `27a3c4947359`
**Schedule:** `0 10,18 * * *` (2×/day at 10 AM, 6 PM UTC)
**Delivery:** DMOB group (-1003872552815)
**Status:** ✅ Active — new, awaiting first scheduled run

**What it does:** Scans for upcoming hackathons and bug bounty opportunities.

---

### 9. 🔧 Weekly Skills Update Check
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
| `faed4f588aef` | YoYo | Crypto Watchlist + LP Monitor | Duplicate; consolidated into DeFi Milestone (2026-05-02) |
| `cfa8d1c19357` | YoYo | DeFi Milestone + LP Monitor | Duplicate; consolidated into DeFi Milestone (2026-05-02) |
| `b2bb2bae4fc5` | DMOB | LP Range Monitor | Previously consolidated |
| `504ac01d54ed` | YoYo | Daily LP + DeFi (never ran) | Previously consolidated |
| `2563e78bcf72` | YoYo | DeFi Milestone (Fee Efficiency Tracker) | Reinstated Apr 28 — conditional alerting |
| `1f10f10b2a07` | YoYo | CMC Crypto Watchlist (canonical) | ID no longer in scheduler |
| `f930f56d082a` | Gentech | Crypto Watchlist Hourly | Migrated to separate Gentech profile |


---

## 🔮 Pipeline: Next LP Pool Research

**Per Jordan (2026-04-27):**
- LINK → **spot buy only** (too volatile for LP)

**To research:**
- [ ] Check pool depth >$100k, volume >$10k/24h

---

## 🚀 GenTech Current — DeFi Cron Jobs (Active)

| Job ID | Name | Schedule | Status | Delivers To |
|---|---|---|---|---|
| `4cb4f1e92116` | On-Chain LP Position Reader — Live Data | `0 */3 * * *` | ✅ Active | local |
| `2600f8fc0f0e` | AAE DeFi Milestone + LP Monitor (10min) | `*/10 6-23 * * *` | ✅ Active | Strategies (-1002916759037) |

### Reader (`4cb4f1e92116`)
- **Wrapper:** `~/.hermes/scripts/run-reader.py`
- **Canonical script:** `/root/vaults/gentech/scripts/run-reader.sh`
- **Output:** `/root/ProtoJay4789.github.io/DeFi/defi-data.json`
- **Wallet:** `0x7ebff188f2Eba16518C02864589b1403a5d1296a`
- **Shape:** `bid-ask` (default, overridable via `SHAPE` env)

### AAE DeFi Milestone + LP Monitor (`2600f8fc0f0e`)
- **Script:** `/root/vaults/gentech/Strategies/scripts/defi-lp-consolidated.py`
- **Config:** `/root/.hermes/scripts/.lfj-aae-config.json`
- **State:** `/root/.hermes/scripts/.lfj-defi-state.json`
- **Current range:** $6.6518 – $6.9162 (bid-ask)
- **Behavior:** Reads actual on-chain range/shape from `defi-data.json`; fetches live price; debounced alerts (5-min confirmation); silent during quiet hours (11 PM – 6:30 AM ET).
- **Triggers:** Out-of-range confirmed, efficiency <50% confirmed, milestone hit.

*Updated: 2026-06-16*

---

*Canonical LP monitor (10min): YoYo job `3258c64b` (DeFi Milestone with 5min debounce). DeFi Milestone (twice daily, AM/PM): DMob jobs `f709d93b25ab` / `6a85a903e471`.* DeFi Dashboard (3×/day): YoYo job `33b3c40539b2`.*
