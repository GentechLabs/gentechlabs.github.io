# LFJ AVAX/USDC LP Position Analysis — 2026-05-10

**Report Date:** 2026-05-10 21:00 UTC
**Analyst:** DMOB (Labs)
**Status:** CRITICAL — OUT OF RANGE

---

## Position Status: OUT OF RANGE

| Metric | Value |
|--------|-------|
| Current AVAX Price | $10.091 |
| Active Range | $10.28 — $10.55 |
| Position Status | **BELOW RANGE** |
| Price Gap to Range | -$0.189 (-1.87%) |
| Range Width | 2.59% (CURVE shape) |
| Position Config Value | $162.87 |
| Token Split (at rebalance) | 9.489 AVAX + 84.02 USDC |
| Effective Position State | ~100% AVAX (all USDC converted) |
| Fee Earnings | **$0.00/day** |

**⚠️ CRITICAL: Position is earning zero fees. Price must rise +1.87% to $10.28 to re-enter range.**

---

## Pool Health Metrics

| Metric | Value | Trend |
|--------|-------|-------|
| Pool TVL | $4,064,396 | Stable (+0.9% vs May 7) |
| 24h Volume | $4,127,439 | **DOWN 86.8%** (was $31.2M) |
| Volume/TVL Ratio | 1.02x | Collapsed (was 7.7x) |
| Pool Daily Fees (5bps) | $2,063.72 | Down ~87% |
| Buys/Sells | 1,901 / 1,929 | B/S: 0.985 (balanced) |
| Pool Dominance | Low — deep liquidity |

**Volume Collapse:** The 87% volume decline from May 7 ($31.2M) to May 10 ($4.1M) is the most significant market change. This dramatically reduces fee income potential even when in range.

---

## Fee Income Analysis

### Current State (OUT OF RANGE)
- **Daily Fees:** $0.00
- **Weekly Projection:** $0.00
- **Monthly Projection:** $0.00

### Hypothetical (If Price Were In Range)
| Metric | Value |
|--------|-------|
| Position Share of Pool | 0.0040% |
| Est. Daily Fees | $0.083 |
| Est. APR | 18.5% |
| Est. Weekly | $0.58 |
| Est. Monthly | $2.48 |
| Est. Annual | $30.21 |

### Historical Fee Progression
| Date | APR | Volume/TVL | Status |
|------|-----|------------|--------|
| May 7 | 311-422% | 7.7x | In Range |
| May 9 | 15.1% | 1.1x | In Range |
| May 10 | 0% (18.5% potential) | 1.02x | **OUT OF RANGE** |

**Key Insight:** The position's fee-earning potential has declined ~95% in 3 days due to both volume collapse and being out of range.

---

## Impermanent Loss Assessment

### IL Analysis
| Metric | Value |
|--------|-------|
| Range Width | 2.59% |
| IL Amplification | ~39x vs full-range LP |
| Position State | 100% AVAX (below range) |
| Initial Value (at rebalance) | ~$182.90 |
| Current AVAX-only Value | ~$95.75 |
| **IL Impact** | **-$87.14 (-47.6%)** |

### IL Risk Factors
- **Single-Asset Exposure:** Below range = 100% AVAX. Maximum risk realized.
- **Narrow Range Amplification:** 2.59% width = 39x IL amplification vs passive LP
- **Price Volatility:** AVAX traded $9.11-$10.42 in tracking period (14.4% swing)
- **Rebalance Frequency:** Range adjusted 3x in 2 weeks — each adjustment crystallizes IL

### IL Comparison
| Scenario | IL Impact |
|----------|-----------|
| Full-range LP | ~2.3% |
| This position (2.59% range) | ~47.6% |
| Amplification factor | 20.7x worse than passive |

---

## Risk Assessment: HIGH

### Risk Factors

| Factor | Level | Details |
|--------|-------|---------|
| **Out of Range** | CRITICAL | Earning $0, position idle |
| **IL Exposure** | HIGH | 47.6% loss, 100% AVAX |
| **Volume Collapse** | HIGH | 87% decline in 3 days |
| **Range Miss** | HIGH | Range set too high at rebalance |
| **Capital Efficiency** | HIGH | $162.87 earning $0 |
| **Toxic Flow** | LOW | Position negligible vs pool |
| **Smart Contract** | LOW | LFJ v2.2 battle-tested |
| **Gas Costs** | MEDIUM | Rebalance cost vs position size |

### Security Considerations
- Token approvals to pool contract should be reviewed
- Wallet: `[REDACTED_WALLET]`
- Pool: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- Consider revoking unused approvals quarterly

---

## Milestone Progress

| Tier | Daily Target | Current | Progress | Required Capital |
|------|-------------|---------|----------|-----------------|
| Scout | $5.00/day | $0.00 | 0.0% | $9,847 |
| Raider | $20.00/day | $0.00 | 0.0% | $39,389 |
| Warlord | $50.00/day | $0.00 | 0.0% | $98,473 |
| Sovereign | $100.00/day | $0.00 | 0.0% | $196,945 |

**Milestone Gap:** Position is at 0% across all tiers while out of range. Even if in range, the 18.5% APR means Scout tier requires ~$9,847 in capital — a 60x increase from current position.

---

## DCA Analysis

| Parameter | Value |
|-----------|-------|
| DCA Enabled | Yes |
| Base Amount | $50/week |
| Mode | Hybrid |
| Last DCA Date | None recorded |
| Total Fees Earned (all time) | $0.027 |
| Total Days in Range | 0.23 days (~5.6 hours) |

**DCA Effectiveness:** Currently injecting capital into an idle position. Each $100 DCA adds ~$0.004/day in potential fees (at current volume). DCA should be paused or redirected until position is back in range.

---

## Benchmark Comparison

| Strategy | Daily Return | Annual Return | vs LP |
|----------|-------------|---------------|-------|
| **AVAX Staking (8% APY)** | $0.036 | $13.03 | Better while OOR |
| **LP Position (current)** | $0.00 | $0.00 | **0x** |
| **LP Position (if in range)** | $0.083 | $30.21 | 2.3x staking |

**Conclusion:** Staking would outperform LP by an infinite margin while position is out of range. LP only wins if price returns to range AND volume recovers.

---

## Historical Comparison

| Date | Price | Range | Status | Volume | APR |
|------|-------|-------|--------|--------|-----|
| Apr 27 | $9.26 | $9.02-$9.32 | Rebalanced | - | - |
| May 4 | $9.20 | $9.33-$9.52 | OUT OF RANGE | $6.69M | 0% |
| May 7 | $9.65 | $9.45-$9.74 | In Range | $31.2M | 311-422% |
| May 9 | $9.96 | $9.78-$10.02 | In Range | $4.46M | 15.1% |
| **May 10** | **$10.09** | **$10.28-$10.55** | **OUT OF RANGE** | **$4.13M** | **0%** |

**Pattern:** The position has been out of range for significant portions of its life. Total days in range: only 0.23 days out of 13+ days tracked. This suggests the range-setting strategy is too aggressive.

---

## Actionable Recommendations

### IMMEDIATE ACTIONS (Next 24 Hours)

1. **DO NOT REBALANCE YET** — Wait for price to approach $10.25+ before rebalancing. Rebalancing at $10.09 into a $10.28-$10.55 range would immediately put position back out of range.

2. **MONITOR PRICE CLOSELY** — If AVAX rises above $10.20, consider rebalancing to $10.15-$10.45 (wider range to capture more price movement).

3. **PAUSE DCA** — Do not inject more capital while position is out of range. Each DCA dollar is earning $0.

### SHORT-TERM (This Week)

4. **REBALANCE STRATEGY** — When rebalancing:
   - Use wider range: 4-5% width instead of 2.59%
   - Set range centered on current price ±2%
   - Consider $10.00-$10.50 (5% width) to survive volatility
   
5. **VOLUME MONITORING** — The 87% volume collapse is concerning. Monitor if this is temporary or structural. If volume stays at $4M/day, APR potential drops to ~18% even when in range.

6. **GAS OPTIMIZATION** — Rebalance only when:
   - Price is within 0.5% of range edge, OR
   - Fees earned > $2 (to justify gas cost), OR
   - Weekly DCA day (combine with rebalance)

### MEDIUM-TERM (This Month)

7. **RANGE WIDTH ADJUSTMENT** — The 2.59% range is too narrow for AVAX's volatility:
   - Current: 2.59% width → 39x IL amplification
   - Recommended: 5-8% width → 12-20x IL amplification
   - Trade-off: Lower peak APR, but more time in range

8. **SHAPE EVALUATION** — CURVE shape is appropriate for current conditions. Bid-Ask would be better if price stabilizes in a tight range.

9. **CONFIG SYNC** — Ensure all monitoring scripts (`d5-master-cron.py`, `lp-position-reader.py`) use the latest range from `.lfj-aae-config.json` ($10.28-$10.55).

### LONG-TERM (Strategic)

10. **CAPITAL ACCUMULATION** — At 18.5% APR (if in range), reaching Scout tier ($5/day) requires $9,847. At $75/week DCA:
    - Time to Scout: ~127 weeks (2.4 years)
    - This assumes volume stays at $4M/day
    - If volume recovers to $31M, Scout requires ~$1,260 (16 weeks)

11. **RISK MANAGEMENT** — Consider a hybrid approach:
    - 70% in wider-range LP (5-8% width)
    - 30% in AVAX staking (8% APY, guaranteed)
    - This provides floor returns while capturing upside

12. **TAX CONSIDERATIONS** — Each rebalance is a taxable event. Document all rebalance timestamps and prices for tax reporting.

---

## Summary

| Category | Status | Action |
|----------|--------|--------|
| Position Health | CRITICAL | Out of range, earning $0 |
| Fee Income | $0.00/day | Wait for price recovery |
| IL Exposure | HIGH (-47.6%) | Widen range on next rebalance |
| Milestone Progress | 0% | Capital-constrained |
| DCA | Pause | Redirect to staking until OOR |
| Risk Level | HIGH | Active management required |

**Bottom Line:** The position was rebalanced too aggressively upward ($10.28-$10.55) and price dropped below range. The 87% volume collapse compounds the problem. The position has earned only $0.027 in total fees over its lifetime. A wider range strategy (5-8%) would have kept the position in range through the recent volatility. For now, wait for price to recover to $10.20+ before taking action, and pause DCA injections.

---

## Data Sources

- DexScreener API (live): $10.091, $4.13M volume, $4.06M TVL
- AAE Config: range $10.28-$10.55, CURVE shape, updated May 10
- AAE State: last check May 10 20:06 UTC, $162.87 position
- Previous analyses: May 7 (311-422% APR), May 9 (15.1% APR)
- Historical price data: $9.11-$10.42 range over tracking period
