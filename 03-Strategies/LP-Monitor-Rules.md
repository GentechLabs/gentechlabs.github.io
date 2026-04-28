# LP + Milestone Tracker Rules — AVAX/USDC (AAE v2)

> Established: 2026-04-18
> Updated: 2026-04-28 — Position confirmed: $135.24, range $9.00–$9.30 (bid-ask), fees 0.47%
> Status: Active
> Pool: LFJ V2.2 AVAX/USDC (binStep 10, pool 0x864d4e5ee7318e97483db7eb0912e09f161516ea)

## Current Position

- **Range:** $9.00 — $9.30 (rebalanced Apr 27, bid-ask)
- **Position:** ~$135.24 (3.446 AVAX @ $31.87 + 103.38 USDC @ $103.37)
- **Shape:** Bid-Ask
- **Strategy:** Bear market accumulation — farm the bottom, compound rewards
- **Crash Scenario (Dadrian):** If AVAX drops to $8.30-9.00, DCA strategy will work itself out through Impermanent Loss (IL). Continuous DCA at lower prices builds cheaper positions—IL math naturally offsets price decay over time.
- **Optimal Entry Range:** During crash, consider 70 USDC / 30 AVAX bid-ask weighting (Curve-style concentrated liquidity).
- **Current Tool:** Bid-Ask shape — range widened for stability

---

## AAE Signal Output (New in v2)

The monitor now outputs **structured JSON signals** for AAE squad treasury + progression ingestion:

```json
{
  "status": "SILENT | OK | ALERT | CRITICAL",
  "signal": {
    "timestamp": "ISO8601",
    "signal_type": "POSITION",
    "severity": "SILENT",
    "pool_address": "0x...",
    "chain": "avalanche",
    "token0_symbol": "AVAX",
    "token1_symbol": "USDC",
    "price": 9.4566,
    "price_change_24h": -2.5,
    "range_low": 9.00,
    "range_high": 9.30,
    "in_range": true,
    "fee_efficiency": 87.5,
    "shape": "curve",
    "position_value_usd": 83.92,
    "token0_split_pct": 39.5,
    "token1_split_pct": 60.5,
    "fees_24h": 0.33,
    "fees_since_deposit": 12.45,
    "claimable_rewards_usd": 1.13,
    "apr": 5138.0,
    "current_tier": 1,
    "current_tier_label": "Scout",
    "next_tier": 2,
    "next_tier_label": "Raider",
    "progress_to_next_pct": 6.6,
    "days_in_range": 14.3,
    "compound_ready": false,
    "dca_ready": false,
    "suggested_action": "HOLD: Position healthy. Continue earning.",
    "data_source": "dexscreener",
    "squad_id": null
  },
  "human_report": "...markdown for Telegram...",
  "config_hash": 1234567890
}
```

### Signal Severity Levels

| Level | Condition | Action |
|-------|-----------|--------|
| **SILENT** | In range + efficiency ≥ 50% + no compound/DCA/milestone | Log only, no Telegram |
| **OK** | Compound ready OR DCA day OR milestone hit | Telegram notification |
| **ALERT** | Out of range OR efficiency < 50% | Telegram alert + suggest rebalance |
| **CRITICAL** | Efficiency < 30% or price crash | Immediate alert + urgent rebalance |

---

## Monitoring Rules (Jordan's Exact Spec)

### Rule 1 — Check Frequency
⏰ LP Monitor runs **frequently** via consolidated cron job `2563e78bcf72` (currently every 10 min — may adjust to 4×/day per preference).

### Rule 2 — In Range + High Efficiency → SILENT
🤫 Price in range AND fee efficiency **50–100%** → **no alert, stay silent** (compact log only)

### Rule 3 — In Range + Low Efficiency → ALERT
⚠️ Price in range BUT fee efficiency **< 50%** → alert: *"fee efficiency dropping — consider rebalancing"*

### Rule 4 — Out of Range → ALERT
⚠️ Price out of range → **immediate alert** (v2: no 5-min delay, structured signal handles confirmation)

### Rule 5 — Overnight Pause
🌙 **Pause at 11 PM**, resume at **6:30 AM** (EDT/EST)

### Rule 6 — Recovery Alert
🔔 When price returns to range after being out → alert with "recovered"

---

## Squad Progression Tiers (Updated Apr 25)

| Tier | Rank | Daily Fee Target | Visual | Unlocks |
|------|------|-----------------|--------|---------|
| 1 | **Scout** | $5/day | Bronze badge | Entry strategies (CURVE) |
| 2 | **Raider** | $20/day | Silver badge | SPOT + BIDIRECTIONAL shapes |
| 3 | **Warlord** | $55/day | Gold badge | Multi-pool positions |
| 4 | **Sovereign** | $200/day | Platinum badge | Custom strategy creation |

### Progress Calculation
```
progress_pct = ((current_daily_fees - current_tier_target) / (next_tier_target - current_tier_target)) * 100
```

### Rule P1 — Tier Promotion
🏆 When estimated daily fees cross a tier threshold → ALERT with promotion + new unlocks

### Rule P2 — Progress Updates
📊 Every OK/ALERT includes current rank, next rank, and % progress

---

## Compound Tracker Rules

### Rule C1 — Compound Ready
🔄 When cumulative fees hit **$50 threshold** → ALERT: "Compound ready — reinvest + DCA"

### Rule C2 — DCA Day Reminder
💰 **Monday** → Alert: "$50 DCA ready to deploy"

### Rule C2b — Efficiency-Triggered Micro-DCA (NEW)
📉 When fee efficiency drops, deploy **bonus DCA** in $10–$20 increments:

| Efficiency | Trigger | Bonus DCA | Action |
|-----------|---------|-----------|--------|
| **60–50%** | Yellow flag | $0 | Watch only — still earning, no panic |
| **50–40%** | Orange flag | **$10** | Price near edge, deploy micro-DCA + monitor for rebalance |
| **40–30%** | Red flag | **$20** | Strongly consider rebalancing range + DCA into fresh range |
| **<30%** | Critical | **$20 + rebalance** | Shift range immediately, deploy DCA into new position |

**Principle:** Never DCA into a stale range without at least *considering* a rebalance. Bonus DCA is for fresh, efficient positions only.

### Rule C3 — Compound Report
📊 Every alert includes:
- Est. daily fees (from pool volume × position share)
- Cumulative fees earned
- Days in range
- Current tier + progress %
- DCA countdown
- Compound threshold progress

---

## Fee Efficiency Formula

### Curve Shape (Default)
```
position = (price - RANGE_LOW) / (RANGE_HIGH - RANGE_LOW)
fee_efficiency = (1 - abs(position - 0.5) * 2) * 100
```
- **Center (50%)** → 100% efficiency
- **Edge (0% or 100%)** → 0% efficiency

### Spot Shape
- **In range** → 100% efficiency (uniform)
- **Out of range** → 0% efficiency

### Bidirectional Shape
- **Edges** → 100% efficiency (highest at extremes)
- **Center** → 0% efficiency

---

## Data Sources

| Priority | Source | Notes |
|----------|--------|-------|
| 1 | **Birdeye x402** | Premium data, requires API key |
| 2 | **DexScreener** | Free, no key, reliable |
| 3 | **On-chain RPC** | Fallback, no volume data |

---

## Fee Estimation Formula

```
daily_fees = pool_volume_24h × (fee_tier_bps / 10000) × (position_usd / pool_liquidity)
apr = (daily_fees × 365 / position_usd) × 100
```

---

## Cron Jobs

| Job | ID | Schedule | Status | Script |
|-----|----|----------|--------|--------|
|| **LP Range Monitor v3** | `03b4cc0310ba` | `*/10 * * * *` | ✅ Active | `lp-range-monitor-v3.py` |
|| **YoYo — DeFi Milestone (Fee Efficiency Tracker)** | `2563e78bcf72` | `0 * * * *` | ✅ Active | Prompt-driven (DexScreener) |

> **Updated Apr 28 per Jordan:** Hourly fee efficiency monitor with conditional alerting.
> **Only delivers output when fee efficiency trends below 30%.** Otherwise silent (STATUS:OK).
> When below threshold, includes rebalance recommendation with liquidity shape and range.
> History tracked in `/root/.hermes/profiles/yoyo/defi-lp-history.json`.
> **Consolidated (Apr 27):** Merged LP Range Monitor into DeFi Milestone tracker.
> Preserved 2-check out-of-range confirmation, quiet hours, and all fee efficiency rules.

---

## Compound Strategy (Jordan's Vision)

**"Bear market accumulation play — farm the bottom, compound rewards"**

- LP generates fees in the $9.00-$9.30 range
- Compound weekly: reinvest accumulated fees + $50-100 DCA
- Target: $5/day (Scout) → $20/day (Raider) by July → $55/day (Warlord) by Sep 2027
- Each compound increases position → more fees → faster tier progression

### Crash / Out-of-Range Decision Matrix (Dadrian Logic)

> *"How am I doing vs stakers/hodlers? Should I hold?"*

| Scenario | Position Value | Loss from Current | Mechanics | Decision Logic |
|----------|---------------|-------------------|-----------|----------------|
|| **In Range (9.00–9.30)** | ~$135.24 | — | Earning fees | ✅ **HOLD** — keep LP, compound fees |
| **Below Range ($8.80)** | ~$78.63 | -$5.29 | 100% AVAX | ❓ **HOLD vs DCA?** — if AVAX fundamentals intact, **add USDC** |
| **Crash ($8.30)** | ~$74.17 | -$9.75 | 100% AVAX | ⚠️ **DCA or EXIT?** — if deep dump, **70 USDC / 30 AVAX** weighted re-entry |
|| **Staking comparison** | — | — | 13.5% APR vs LP APR | ✅ **LP wins** — fees dominate staking unless extreme volatility |

**Key insight:** Once below range, **you're just holding AVAX**. No IL — just price depreciation. Same as if you'd never LP'd.

**DCA Re-entry Play:**
- Add $50 USDC at ~$8.50 → buy ~5.88 AVAX
- Total AVAX: ~14.82
- Set new range: $8.30–$9.00 (or $8.30–$9.10)
- Recovery to $9.00: position ≈ **$133**
- Earning fees the entire way up

### Shape Selection by Regime

| Condition | Recommended Shape | Rationale |
|-----------|-------------------|-----------|
| **Slow grind / chop (now)** | **Curve** | Captures small moves both directions, smooth efficiency curve |
| **Crash / panic dump** | **70 USDC / 30 AVAX (skewed)** | Buying the dip, not market-making; avoids center loss |
| **Bidirectional (wide range)** | **Spot + Curved Ends** | High upside at extremes, low cost in middle |
| **Trending up hard** | **Spot (100% AVAX) or EXIT** | No need to market make — just hold asset |

---

## Bid-Ask DCA Weighting (Crash Protection)

When price is **out of range** and **fee efficiency < 30%**, deploy DCA with **weighted asset allocation** to minimize IL:

| Efficiency | DCA Type | USDC Weight | AVAX Weight | Rationale |
|-----------|----------|-------------|-------------|-----------|
| **60–50%** | Normal DCA | 50% | 50% | Standard rebalancing |
| **50–40%** | Weighted DCA | **70%** | **30%** | Price near lower edge, bias to USDC |
| **40–30%** | Recovery DCA | **80%** | **20%** | Strong bias to USDC, expecting re-entry |
| **<30%** | Aggressive Recovery | **90%** | **10%** | Deep dump — buy AVAX dip, minimize IL risk |

**Principle:** Never DCA into a stale range without at least *considering* a rebalance. Bonus DCA is for fresh, efficient positions only.

## Fee Efficiency vs Staking Performance

| APY | staking (GEN/AVAX) | LP (LFJ V2.2) | LP Advantage |
|-----|--------------------|---------------|--------------|
| **Base** | 13.5% APR | LP APR | **LP advantage** |
| **Daily Fees (S1)** | $0.22 | $0.47 | **+$0.25** |
| **Risk** | Low (no impermanent loss) | Medium (IL only if out-of-range) | LP wins on risk-adjusted return |
| **Volatility Hedge** | None | In-range fees offset price decay | LP outperforms in sideways/crash |

**Bottom line:** LP fees are **2x higher** than staking. The only scenario where staking wins is during **extreme volatility** (>20% daily moves where IL > fees earned).

---

### Compound Checklist
1. ✅ LP in range, earning fees
2. ⬜ Accumulate $50+ in fees
3. ⬜ It's Monday (DCA day)
4. ⬜ Withdraw fees → swap to AVAX+USDC → re-deposit to LP
5. ⬜ Add $50-100 fresh capital (DCA)
6. ⬜ Log compound event in state file

---

## Related Files

- **Script (v2):** `/root/vaults/gentech/03-Strategies/scripts/lp-aae-signal-monitor.py`
- **Script (legacy):** `/root/vaults/gentech/03-Strategies/scripts/lp-unified-monitor.py`
- **Config:** `~/.hermes/scripts/.lfj-aae-config.json`
- **State:** `~/.hermes/scripts/.lfj-aae-state.json`
- **Analysis:** `/root/vaults/gentech/03-Strategies/LFJ-AVAX-USDC-5bps-Analysis.md`
- **Crypto Watchlist (standalone):** `/root/vaults/gentech/03-Strategies/token-watchlist.md`
- **AAE Signal Spec:** `/root/vaults/gentech/03-Strategies/AAE-Signal-Spec.md`

---

## ✅ Optimization Milestone — Apr 25 2026

Jordan approved the optimized cron output format:
> *"You guys did a great job optimizing the cron job. It looks fantastic. This is not only something that our users are gonna love, but our community."*

**What changed:**
- Clean emoji taxonomy (💧 WARNING header, 📊 DexScreener attribution)
- Compact P&L block (Est. Daily Fees, Cumulative Fees, LP Value vs HODL)
- Inline pool context (Vol 24h, TVL)
- Squad-aware tier progression (Scout → Raider → Warlord → Sovereign)

## ✅ D5 Milestone Summary Consolidated — Apr 26 2026

Jordan's directive: Consolidate the daily LP summary into the D5 milestone format.

**What changed:**
- daily-lp-summary.py → replaced by d5-milestone-summary.py
- Daily 8 AM cron now produces structured D5 Milestone Report:
  - Full tier ladder display (Scout→Raider→Warlord→Sovereign) with progress bars
  - Micro-DCA triggers with efficiency-based bonus amounts ($10/$20)
  - Compound threshold tracking ($50 target)
  - Action items ranked by severity
  - Revenue summary (daily fees, implied APR, cumulative fees)
  - Monday DCA reminder
- Frontend Impact Principle applies — feeds the DeFi Milestone Tracker data layer

**Frontend Impact Principle logged:
> *"As we add more layers, we're always going to consider how this is going to affect our front end, our DeFi milestone tracker."*

All future LP layer additions must pass a frontend compatibility check before deployment.
