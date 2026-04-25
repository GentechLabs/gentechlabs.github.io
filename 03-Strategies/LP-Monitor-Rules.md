# LP + Milestone Tracker Rules — AVAX/USDC (AAE v2)

> Established: 2026-04-18
> Updated: 2026-04-25 — AAE Signal Monitor v2, new milestone tiers, structured output
> Status: Active
> Pool: LFJ V2.2 AVAX/USDC (binStep 10, pool 0x864d4e5ee7318e97483db7eb0912e09f161516ea)

## Current Position

- **Range:** $9.33 — $9.52 (rebalanced Apr 24)
- **Position:** ~$83.37 (3.33 AVAX + $51.91 USDC)
- **Shape:** Curve
- **Strategy:** Bear market accumulation — farm the bottom, compound rewards
- **Crash Scenario (Dadrian):** If AVAX drops to $8.30-9.00, DCA strategy will work itself out through Impermanent Loss (IL). Continuous DCA at lower prices builds cheaper positions—IL math naturally offsets price decay over time.
- **Optimal Entry Range:** During crash, consider 70 USDC / 30 AVAX bid-ask weighting (Curve-style concentrated liquidity).
- **Current Tool:** Using Curve shape while moving slowly (low volatility)

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
    "range_low": 9.33,
    "range_high": 9.52,
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
⏰ LP Monitor runs **every 4 hours** (8:25 AM, 12:25 PM, 4:25 PM, 8:25 PM ET) via cron job `2ca757ee055c`.

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
| **YoYo — LP + DeFi Milestone Tracker** | `2ca757ee055c` | `25 8,12,16,20 * * *` | ✅ Active | `lp-aae-signal-monitor.py` |

---

## Compound Strategy (Jordan's Vision)

**"Bear market accumulation play — farm the bottom, compound rewards"**

- LP generates fees in the $9.33-$9.52 range
- Compound weekly: reinvest accumulated fees + $50-100 DCA
- Target: $5/day (Scout) → $20/day (Raider) by July → $55/day (Warlord) by Sep 2027
- Each compound increases position → more fees → faster tier progression

### Crash / Out-of-Range DCA Strategy

**Worst-case scenario:** AVAX drops below $9.33 (out of range)

| AVAX Price | Position Value | Loss from Current | Mechanics |
|------------|---------------|-------------------|-----------|
| $9.00 | ~$80.42 | -$2.95 | Out of range → 100% AVAX |
| $8.80 | ~$78.63 | -$4.74 | Out of range → 100% AVAX |
| $8.50 | ~$75.95 | -$7.42 | Out of range → 100% AVAX |
| $8.30 | ~$74.17 | -$9.20 | Out of range → 100% AVAX |

**Key insight:** Once below range, **you're just holding AVAX**. No IL — just price depreciation. Same as if you'd never LP'd.

**DCA Re-entry Play:**
- Add $50 USDC at ~$8.50 → buy ~5.88 AVAX
- Total AVAX: ~14.82
- Set new range: $8.30–$9.00 (or $8.30–$9.10)
- Recovery to $9.00: position ≈ **$133**
- Earning fees the entire way up

**Shape selection by regime:**
- **Slow grind / chop (now):** Use **Curve** — captures small moves both directions
- **Crash / panic dump:** Go **70% USDC / 30% AVAX** (skewed / bid-ask) — you're buying the dip, not market-making
- **Fast recovery:** Use **Curve** again to capture volatility both ways
- **Trending up hard:** Use **Spot** (100% AVAX) or exit LP and stake

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
