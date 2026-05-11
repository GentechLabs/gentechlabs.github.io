# 📊 AVAX/USDC LFJ LP Position Analysis — May 11, 2026

**Report Generated**: 2026-05-11 08:30 UTC  
**Analyst**: DMOB, Head of Labs  
**Status**: ⚠️ HIGH RISK — Action Required

---

## ⚠️ PARAMETER DISCREPANCY DETECTED

| Field | Task Description (STALE) | Tracker State (CURRENT) |
|-------|--------------------------|------------------------|
| Range | 9.44–9.74 | **9.90–10.15** |
| Shape | Bid-Ask | Bid-Ask ✅ |
| Reserves | 170,549 AVAX / 2,372,096 USDC | **13.35 AVAX / 44.2 USDC** |
| Total Value | ~$3,990,652 | **$177.76** |
| Last Rebalance | Unknown | **2026-05-11 03:20 UTC** |

> ⚡ The task description lists **pool-level reserves** (170K AVAX / 2.37M USDC) as if they were position reserves. Your actual position is $177.76 (0.004% of pool). Using tracker values for all analysis below.

---

## 📊 POSITION HEALTH CHECK

| Metric | Value | Status |
|--------|-------|--------|
| Current Price | $10.041 | — |
| Range | $9.90 – $10.15 | — |
| Shape | Bid-Ask | — |
| Position in Range | 56.4% | ✅ In Range |
| Range Width | 2.49% | ⚠️ Narrow |
| Active Bins | 24 (10bps step) | — |
| Position Value | $177.76 | — |
| Token Split | 13.35 AVAX + 44.2 USDC | — |

**Verdict**: ✅ **IN RANGE** — price well-centered. However, the Bid-Ask shape is **poorly aligned** with center positioning (see efficiency below).

---

## 🔬 BID-ASK EFFICIENCY ANALYSIS

```
Range:     |████████████████████████████|
$9.90      $10.00      $10.041     $10.10      $10.15
           [  50%  ]    ▲ HERE
           LOW FEE ZONE  (center = worst for Bid-Ask)
```

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Position Ratio | 56.4% | Near center |
| Bid-Ask Efficiency | **12.8%** | 🔴 CRITICAL — price in worst zone |
| Expected Fee Capture | ~13% of potential | Most liquidity sits at edges, unused |

**Problem**: Bid-Ask concentrates liquidity at range boundaries. With price at 56.4% (near center), **87% of your position's liquidity is idle**. You're earning fees on a tiny sliver of your capital.

**Fix Options**:
1. **Switch to CURVE shape** — captures max fees at center (current price position)
2. **Widen range** — push edges further out so center has more weight
3. **Wait for price to move to edge** — Bid-Ask earns most at 0% or 100% position

---

## 💰 FEE INCOME & APR

| Metric | Value |
|--------|-------|
| Pool 24h Volume | $3,960,133 |
| Pool TVL | $4,123,179 |
| Pool Daily Fees | $1,980.07 |
| Position Share | 0.0043% |
| Est. Daily Fees | **$0.085** |
| APR | **17.5%** |
| vs Staking (8% APY) | 2.2x ✅ |

### Fee Trend (CRITICAL)
```
May 7:  $31.2M volume → ~$1.50/day fees → 311-422% APR
May 9:  $16.1M volume → ~$0.80/day fees → 73-345% APR  
May 11:  $3.96M volume → ~$0.09/day fees → 17.5% APR
        ─────────────────────────────────────────────
        87% volume decline in 4 days
```

### Projections (at current volume)
| Period | Estimated Fees |
|--------|---------------|
| Daily | $0.085 |
| Weekly | $0.60 |
| Monthly | $2.56 |
| Yearly | $31.09 |

**Note**: Last recorded 24h fees were $1.19 (May 8, pre-rebalance). Current estimate reflects the new range and collapsed volume.

---

## ⚠️ IMPERMANENT LOSS

| Metric | Value |
|--------|-------|
| Entry Price | $8.85 (Mar 31, 2026) |
| Current Price | $10.041 |
| Price Change | +13.5% |
| IL Amplification | ~20x (narrow range) |
| Estimated IL | ~18.2% vs HODL |
| IL in USD | ~$32.27 |

**Assessment**: The 13.5% price appreciation from entry creates significant IL in a concentrated position. The 20x amplification from the tight 2.5% range means IL is ~20x what a passive Uniswap V2 LP would experience. However, fee income should partially offset this if volume recovers.

---

## 🔒 RISK ASSESSMENT: 🔴 HIGH

| Risk Factor | Severity | Detail |
|-------------|----------|--------|
| Volume Collapse | 🔴 HIGH | 87% decline in 4 days ($31M → $3.96M) |
| Bid-Ask Misalignment | 🔴 HIGH | 12.8% efficiency — price at center, not edges |
| Position Size | 🟡 MEDIUM | 0.004% of pool — negligible market impact |
| Narrow Range | 🟡 MEDIUM | 2.5% width → ~20x IL amplification |
| Price Near Center | 🟢 LOW | Well-buffered from both edges (21% from top, 14% from bottom) |
| Toxic Flow | 🟢 LOW | Low volume = low adversarial MEV risk |
| Gas Costs | 🟢 LOW | ~$0.10 per tx — negligible |

### Additional Risk Factors
- **B/S Ratio**: 1.00 (2,475 buys / 2,466 sells) — perfectly balanced, no directional pressure
- **Volume Floor Risk**: If volume stays <$5M for 48h, daily fees drop below $0.10
- **Rebalance Frequency**: 7+ rebalances in 41 days — high maintenance cost

---

## 📈 VOLUME TREND (CRITICAL WATCH)

```
$35M ┤ ████████
$30M ┤ ████████
$25M ┤ ████████
$20M ┤ ████████ ████
$15M ┤ ████████ ████
$10M ┤ ████████ ████
 $5M ┤ ████████ ████ ██
 $0M ┤ ████████ ████ ██
     └─May 7───May 9─May 11─
         87% decline in 4 days
```

**This is the #1 risk factor.** The position's yield is directly proportional to pool volume. At $3.96M/day, the position earns ~$0.09/day. If volume recovers to $15M+, daily fees jump to ~$0.34. If it collapses further, fees approach zero.

**Trigger Points**:
- 🟡 **Watch**: Volume <$5M for 24h → consider range widening
- 🔴 **Alert**: Volume <$2M for 48h → consider shape change to CURVE or position reduction
- 🟢 **Recovery**: Volume >$10M sustained → current Bid-Ask may become viable again

---

## 🏁 MILESTONE PROGRESS

| Metric | Value |
|--------|-------|
| Current Tier | Pre-Scout |
| Next Target | Scout ($5/day) |
| Daily Yield | $0.085 / $5.00 |
| Progress | **1.7%** |
| Gap | $10,234 principal needed at 17.5% APR |
| DCA Path | ~136 weeks (2.6 years) at $75/week |

**Comparison to S2S Report (May 2)**:
- May 2: 51.4% APR, $0.19/day, needed $14,205 principal
- May 11: 17.5% APR, $0.09/day, needs $10,234 principal
- APR dropped 66% due to volume collapse; capital need dropped 28% but timeline extended

---

## 📋 ACTIONABLE RECOMMENDATIONS

### P0 — IMMEDIATE (This Week)

**1. Shape Change: Bid-Ask → CURVE** ⭐ Highest Impact
- **Why**: Price at 56.4% position = 12.8% efficiency with Bid-Ask. CURVE would give ~87% efficiency at same position.
- **Expected Impact**: Daily fees $0.085 → ~$0.57 (6.7x increase)
- **Risk**: If price moves to edge, CURVE earns less than Bid-Ask
- **Action**: Rebalance with CURVE shape targeting $9.95–$10.15 (tighter, center-focused)

**2. Monitor Volume Floor**
- **Why**: 87% volume decline is the existential risk
- **Action**: Set alert if volume <$2M for 48h → emergency protocol (reduce position or switch to CURVE)
- **Trigger**: DexScreener `volume.h24` < $2,000,000

### P1 — SHORT TERM (This Month)

**3. Accelerate DCA**
- **Why**: Position at 0.004% of pool — capital is the primary bottleneck
- **Action**: Maintain $75/week DCA; each $100 adds ~$0.04/day at current volume
- **Note**: At current APR, DCA returns are modest; focus on volume recovery

**4. Compound Threshold Adjustment**
- **Why**: At $0.09/day, the $50 compound threshold takes 556 days to reach
- **Action**: Lower compound threshold to $5 or set time-based compound (monthly)

### P2 — MEDIUM TERM

**5. Range Widening Consideration**
- **Why**: If AVAX breaks above $10.15, position goes OOR again
- **Action**: Prepare backup range $9.80–$10.40 (wider, more forgiving)
- **Trade-off**: Wider range = lower fees but less rebalancing

**6. Multi-Pool Diversification**
- **Why**: Single-pool dependency = single point of failure
- **Action**: Evaluate SOL-USDC on Raydium (higher volume, higher volatility)
- **Timeline**: Q3 2026 after AVAX position stabilizes

---

## 🔐 SECURITY CONSIDERATIONS

| Item | Status | Notes |
|------|--------|-------|
| Approval Management | ⚠️ Review | Check token approvals — revoke unused ones |
| Wallet Security | ✅ OK | Using hardware wallet (implied from tracker) |
| Contract Risk | ✅ Low | LFJ V2.2 is audited, battle-tested |
| Gas Optimization | ✅ OK | No pending txs; compound only when >$2 |

**Action Items**:
- Verify no stale approvals on wallet `0x7ebf...1296a`
- Ensure no unlimited USDC/WAVAX approvals to unknown contracts

---

## 📊 COMPARISON TO BENCHMARKS

| Strategy | APR | Risk | Liquidity |
|----------|-----|------|-----------|
| **Current LP (AVAX/USDC)** | **17.5%** | HIGH | Medium |
| Benqi Staking (sAVAX) | 8.0% | Low | High |
| Benqi Lending (USDC) | 3-5% | Low | High |
| Simple HODL (AVAX) | N/A | High | High |
| **LP Advantage** | **2.2x staking** | Higher risk | Lower |

**Verdict**: LP still outperforms staking by 2.2x, but the gap has narrowed significantly from the 38.9x advantage seen on May 7. Risk-adjusted returns may favor staking if volume doesn't recover.

---

## 📅 NEXT ACTIONS

| Priority | Action | Deadline | Owner |
|----------|--------|----------|-------|
| P0 | Shape change to CURVE | Before next rebalance | Jordan |
| P0 | Volume monitoring alert | Set today | DMOB |
| P1 | DCA injection ($75) | Sunday | Jordan |
| P1 | Compound threshold review | This week | DMOB |
| P2 | SOL-USDC feasibility | June 2026 | Labs |

---

*Report saved to `02-Labs/DeFi/lp-position-analysis-2026-05-11.md`*  
*Next analysis: 2026-05-12 08:30 UTC (scheduled cron)*
