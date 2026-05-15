---

# LFJ AVAX/USDC LP Position — Live Tracker

**Pool**: LFJ V2.2 AVAX/USDC 5bps (Avalanche)
**Contract**: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
**Wallet**: `[REDACTED_WALLET]`
**Shape**: Curve
**Entry Date**: 2026-03-31

---
---

## 2026-05-14 Update (20:17 UTC)
**AVAX Price**: $9.9970 (+2.50% 24h)
**USDC Price**: $0.9996 (-0.01% 24h)
**Price Range**: $9.45–$10.00 (Shape: Curve)
**Target**: $9.45–$10.00
**Balances**: 10.43 AVAX (~$104.25) + 92.67 USDC (~$92.63) = **$196.88**
**Wallet**: 0.0983 AVAX (~$0.98) + 0.00 USDC (~$0.00) = **$0.98** | **Combined Total**: **$197.86**
**Fees (24h)**: ~$0.46 (est. from $12.5M vol × 5bps × 0.005% pool share × 1.5x CL boost; oracle not configured)
**IL**: -0.9% ✓ below 2% threshold
**Efficiency**: 6.9% (on-chain share of bin supply — price at 96.5% of range limits Curve effectiveness)
**Action**: ⚠️ Review — price rallied +2.50% to $10.00, pushing active bin to 96.5% of range top. Position balanced 53/47 but near upper boundary. If price breaks above $10.00, position goes out-of-range. Consider widening upper range or monitoring for breakout.

**D5 Milestone Alignment**:
- Scout tier ($5.00/day target) — est. daily fees $0.46 → 9.2% progress
- Price inside strategic target band ✅ ($10.00 within $9.45–$10.00)
- IL -0.9% ✓ below 2% threshold
- Efficiency 6.9% <50% → Micro-DCA boost triggered

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

**Note**: Price rallied +2.50% in 24h (flagged >1.5%). AVAX moved from ~$9.75 → $10.00, pushing active bin from 8363235 → 8363264 (now 96.5% of range). Efficiency dropped from 85.9% → 6.9% — the on-chain reader returns raw bin supply share (ground truth), while previous vault entries used a shape-adjusted formula. Position is earning but competing with significant liquidity in same bins. IL shifted +0.3% → -0.9% (1.2pp swing) as price rose through range. Pool TVL $4.03M, volume $12.5M/24h. Position rebalanced May 13 from $9.95–$10.30.

## 2026-05-13 Update
**AVAX Price**: $9.7541 (-1.09% 24h)
**USDC Price**: $0.9997 (-0.00% 24h)
**Price Range**: $9.45–$10.00 (Shape: Curve)
**Target**: $9.45–$10.00
**Balances**: 8.11 AVAX (~$79.09) + 117.66 USDC (~$117.66) = **$196.75**
**Wallet**: 0.0956 AVAX (~$0.93) + 0.00 USDC (~$0.00) = **$0.93** | **Combined Total**: **$197.68**
**Fees (24h)**: ~$0.77 (est. from $10.6M vol × 5bps × 0.0049% pool share × 3.0x CL boost; oracle not configured)
**IL**: ~0.0% (freshly rebalanced) ✓ below 2% threshold
**Efficiency**: 89.4% ✓ ≥50% — excellent concentration
**Action**: ✅ No rebalance needed — price centered in curve range. Position rebalanced from $9.95–$10.30 (out-of-range) to $9.45–$10.00 (in-range). Efficiency recovered from -10.7% to 89.4%.

**D5 Milestone Alignment**:
- Scout tier ($5.00/day target) — est. daily fees ~$0.77 → 15.5% progress
- Price inside strategic target band ✅ ($9.75 within $9.45–$10.00)
- IL ~0.0% ✓ below 2% threshold
- Efficiency 89.4% ≥50% ✓ — strong fee capture position

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

**Note**: Position rebalanced from $9.95–$10.30 (100% AVAX, out-of-range) to $9.45–$10.00 (8.11 AVAX + 117.66 USDC, USDC-heavy 40/60). Active bin 8363242 sits at 55.3% from range bottom — well-centered. Efficiency 89.4% is excellent for fee capture. Pool TVL $4.07M, volume $10.6M/24h.


---

## 2026-05-13 Update
**AVAX Price**: $9.9157 (+0.48% 24h)
**USDC Price**: $0.9997 (+0.01% 24h)
**Price Range**: $9.95–$10.30 (Shape: Curve)
**Target**: $9.95–$10.30
**Balances**: 20.48 AVAX (~$203.07) + 0.00 USDC (~$0.00) = **$203.07**
**Wallet**: 0.0972 AVAX (~$0.96) + 0.00 USDC (~$0.00) = **$0.96** | **Combined Total**: **$204.04**
**Fees (24h)**: ~$0.02 (est. from $9.52M vol × 5bps × 0.0049% pool share × 0.1x CL out-of-range; oracle not configured)
**IL**: ~0.0% (vs. HODL of ~$204) ✓ below 2% threshold
**Efficiency**: -10.7% (100% AVAX — fully out of range below)
**Action**: 🚨 CRITICAL: Rebalance required — price ($9.9157) below range lower bound ($9.95). Position converted to 100% AVAX. Efficiency -10.7%. Active bin (8363260) is 2 bins below position start (8363262).

**D5 Milestone Alignment**:
- Scout tier ($5.00/day target) — est. daily fees ~$0.02 → 0.4% progress
- Price OUTSIDE strategic target band ($9.95–$10.30) — below lower bound
- IL ~0.0% ✓ below 2% threshold
- Efficiency -10.7% <50% → Micro-DCA boost triggered

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

**Note**: Position range appears to have shifted to $9.95–$10.30 (on-chain bins 8363262–8363296) since last vault-logged rebalance on May 12 ($9.75–$10.01). Price at $9.9157 is below the new range lower bound. Position is 100% AVAX with zero USDC — classic out-of-range-below state. Rebalance needed to re-center range around current price.
## 2026-05-12 06:10 AM Rebalance (jordan_screenshot)
**Price Range**: $9.75–$10.01 (Shape: Curve)
**Balances**: 9.771 AVAX (~$96.61) + 106.59 USDC (~$106.57) = **$203.18**
**Fees (24h)**: ~$1.344 (0.07251 AVAX + 0.62683 USDC)
**IL**: ~0.0% (freshly rebalanced) ✓ below 2% threshold
**Range Status**: 🟢 In Range — price ~$9.89, centered in distribution
**Last Rebalance**: 2026-05-12 06:10 AM (jordan_screenshot)
**Action**: No rebalance needed — price centered in new curve range.
**Position Note**: Rebalanced from Bid-Ask ($9.68–$10.00) to Curve ($9.75–$10.01). Jordan analysis: "Bid-ask was great for the fall but most of the day was spent in the middle of bid ask. Low efficiency is a no go." Curve shape better for ranging markets — earns more when price stays centered. Position value stable at $203.18.

**D5 Milestone Alignment**:
- Scout tier ($5.00/day target) — est. daily fees ~$1.34 → 26.8% progress
- Price inside position range ✅
- IL ✓ well below 2% threshold
- Curve shape = optimal for ranging market at $9.89

---
## 2026-05-12 DCA Rebalance (jordan_screenshot)
**Price Range**: $9.68–$10.00 (Shape: Bid-Ask)
**Balances**: 9.345 AVAX (~$92.21) + 109.76 USDC (~$109.74) = **$201.94**
**Fees (24h)**: ~$1.88 (carrying from prior period)
**Claimable Rewards**: 0.008 AVAX (~$0.008)
**IL**: ~0.0% (freshly rebalanced) ✓ below 2% threshold
**Range Status**: 🟢 In Range — price ~$9.86, centered in distribution
**Last Rebalance**: 2026-05-12 DCA Rebalance (jordan_screenshot)
**Action**: No rebalance needed — price centered in new bid-ask range.
**Position Note**: DCA rebalance — shifted from Curve ($9.81–$10.06) to Bid-Ask ($9.68–$10.00). Bid-Ask shape concentrates more liquidity near current price for higher fee capture in ranging markets. Range widened slightly on bottom ($0.13 down) and tightened on top ($0.06 down). Position value stable at $201.94.

**D5 Milestone Alignment**:
- Scout tier ($5.00/day target) — est. daily fees ~$1.88 → 37.6% progress
- Price inside position range ✅
- IL ✓ well below 2% threshold
- Bid-Ask shape = maximum fee capture when price stays near $9.86

---
## 2026-05-12 08:36 AM Update (jordan_screenshot)
**Price Range**: $9.81–$10.06 (Shape: Curve)
**Balances**: 9.433 AVAX (~$93.05) + 109.21 USDC (~$109.19) = **$203.14**
**Fees (24h)**: ~$1.88 (0.093 AVAX + 0.952 USDC)
**Claimable Rewards**: 0.08 AVAX (~$0.80)
**IL**: ~0.0% (freshly rebalanced) ✓ below 2% threshold
**Range Status**: 🟢 In Range — price ~$9.96, centered in distribution
**Last Rebalance**: 2026-05-12 08:36 AM (jordan_screenshot)
**Action**: No rebalance needed — price centered in new curve range.
**Position Note**: Rebalanced from $9.25–$10.73 (wide curve) to $9.81–$10.06 (tighter curve). Range narrowed significantly — more concentrated = higher fee capture when in range. Position value up to $203.14 from $180.56 (+12.5%).

**D5 Milestone Alignment**:
- Scout tier ($5.00/day target) — est. daily fees ~$1.88 → 37.6% progress
- Price inside position range ✅
- IL ✓ well below 2% threshold
- Efficiency expected good — price centered in range

---
## 2026-05-11 01:16 PM Update (jordan_screenshot)
**Price Range**: $10.02–$10.30 (Shape: Curve)
**Balances**: 7.982 AVAX (~$81.17) + 99.41 USDC (~$99.39) = **$180.56**
**Fees (24h)**: ~$2.47 (carrying from prior period — new range just established)
**IL**: ~0.0% (freshly rebalanced) ✓ below 2% threshold
**Range Status**: 🟢 In Range — price ~$10.12, centered in distribution
**Last Rebalance**: 2026-05-11 01:16 PM (jordan_screenshot)
**Action**: No rebalance needed — price centered in new curve range.

**Position Note**: Rebalanced from $9.96–$10.26 (8.861 AVAX + 90 USDC) to $10.02–$10.30 (7.982 AVAX + 99.41 USDC). Range shifted up $0.06 on both sides. Slight USDC tilt (55/45) — normal for curve placement. Position value stable at $180.56.

**Market Notes**: AVAX ~$10.12. Price centered in $10.02–$10.30 range. Altcoin rally continuation from May 10.

**D5 Milestone Alignment**:
- Scout tier ($5.00/day target) — est. daily fees ~$2.47 → 49.4% progress
- Price inside position range ✅
- IL ✓ well below 2% threshold
- Efficiency expected good — price centered in range

**Other Pools**: None active

## 2026-05-10 20:15 UTC Update
**Price Range**: $10.28–$10.55 (Shape: curve)
**Balances**: 9.489 AVAX (~$98.96) + 84.02 USDC (~$84.02) = **$182.98**
**Fees (24h)**: $1.19
**IL**: +0.00% (vs. HODL) — freshly rebalanced
**Range Status**: 🟢 In Range (55.3% from bottom, 44.7% from top)
**Last Rebalance**: 2026-05-10 20:06 UTC (jordan_screenshot)
**Action**: No rebalance needed

**Market Notes**: AVAX at $10.43 (24h +4.39%), inside position range $10.28–$10.55. Pool volume $3.63M/day. Strong altcoin rally: TAO +6.19%, AVAX +4.39%, LINK +3.96%, SOL +3.31%. BTC $81,209 (+0.47%).

**On-Chain Data**: Pool WAVAX/USDC 5bps on LFJ v2.2 (Avalanche). DexScreener price $10.38, 24h change +3.98%.

**D5 Milestone Alignment**:
- Position value ($182.98) → Scout tier ($5.00/day target) — 23.8% progress
- Price inside position range ✅ (55.3% from bottom)
- IL ✓ well below 2% threshold (+0.00%)
- Est. daily fees $1.19 — need 4.2x to hit Scout

**Other Pools**: None active


## 2026-05-10 16:17 UTC Update
**Price Range**: $9.95–$10.30 (Shape: curve)
**Balances**: 0.05531 AVAX (~$0.56) + 0.57731 USDC (~$0.58) = **$1.14**
**Fees (24h)**: ~$0.00 (position reduced — minimal share of pool)
**IL**: +0.00% (vs. HODL) — freshly rebalanced position
**Range Status**: 🟡 Near Boundary (66.6% from bottom, 1.15% from top edge)
**Last Rebalance**: 2026-05-10 15:44 UTC (jordan_screenshot)
**Action**: Monitor — approaching top boundary (AVAX at $10.18, range top $10.30)

**⚠️ Position Note**: Position dramatically reduced from $125.81 (6.758 AVAX + 58.5 USDC at 12:17 UTC) to $1.14 (0.05531 AVAX + 0.57731 USDC). Likely partial withdrawal or rebalance with capital reallocation. Range shifted from $9.78–$10.02 to $9.95–$10.30.

**Market Notes**: AVAX at $10.18 (24h +3.46%), inside position range $9.95–$10.30. Pool volume $3.88M/day, TVL $4.01M. Broad rally: TAO +4.14%, BEAM +3.13%, LINK +2.82%, SOL +1.59%. BTC $81,431 (+1.08%), XAUt $4,717 (+0.37%).

**On-Chain Data**: Pool WAVAX/USDC 5bps on LFJ v2.2 (Avalanche). 1,363 buys / 1,413 sells in 24h — slight sell pressure. TVL $4.01M.

**D5 Milestone Alignment**:
- Position value ($1.14) → Scout tier ($5.00/day target) — ~0% progress
- Price inside position range ✅ but near top boundary — monitor
- IL ✓ well below 2% threshold (+0.00%)
- Est. daily fees ~$0.00 — need significant position increase to approach Scout

**Other Pools**: None active

## 2026-05-10 12:17 UTC Update
**Price Range**: $9.78–$10.02 (Shape: curve)
**Balances**: 6.758 AVAX (~$67.31) + 58.5 USDC (~$58.50) = **$125.81**
**Fees (24h)**: $1.19
**IL**: +0.00% (vs. HODL) — price within narrow concentrated range
**Range Status**: 🟡 Near Boundary (75% from bottom, 0.6% from top edge)
**Last Rebalance**: 2026-05-09 11:06 UTC (jordan_screenshot)
**Action**: Monitor — approaching top boundary (AVAX at $9.96, range top $10.02)

**Market Notes**: AVAX at $9.96 (24h +0.29%), near top of position range $9.78–$10.02. Pool volume $5.0M/day, TVL $4.05M. Quiet across watchlist: BTC $80,809 (+0.62%), SOL $93.41 (-0.17%), LINK $10.45 (-0.13%), TAO $313.31 (+1.17%), XAUt $4,712 (+0.27%), BEAM $0.0021 (-0.61%). No tokens triggered 1.5%+ alerts.

**On-Chain Data**: Pool WAVAX/USDC 5bps on LFJ v2.2 (Avalanche). 1,315 buys / 1,456 sells in 24h — slight sell pressure. TVL $4.05M.

**D5 Milestone Alignment**:
- Position value ($125.81) → Scout tier ($5.00/day target) — 23.8% progress
- Price inside position range ✅ but near top boundary — monitor
- IL ✓ well below 2% threshold (+0.00%)
- Est. daily fees $1.19 — need 4.2x to hit Scout

**Other Pools**: None active

## 2026-05-09 16:15 UTC Update
**Price Range**: $9.78–$10.02 (Shape: curve)
**Balances**: 9.19 AVAX (~$90.52) + 35.87 USDC (~$35.87) = **$126.39**
**Fees (24h)**: $1.19 (tracker) / $2.43 (est. from volume $6.84M × 5bps × 0.039% share)
**IL**: -0.15% (vs. HODL) — price within range
**Range Status**: 🟢 In Range (price at $9.85, 29.2% from bottom)
**Last Rebalance**: 2026-05-08 09:00 UTC (jordan_manual)
**Action**: No rebalance needed — price inside position range. Est. daily fees $2.43 approaching Scout milestone.

**Market Notes**: AVAX at $9.85 (24h +0.89%), inside position range $9.78–$10.02. Pool volume $6.84M/day, TVL $4.04M. Strong altcoin momentum: SOL +3.96%, LINK +2.99%. BTC steady at $80,547 (+0.70%). Gold (XAUt) flat at $4,699.

**On-Chain Data**: Pool WAVAX/USDC 5bps on LFJ v2.2 (Avalanche). Liquidity $4.04M (base: 28,684 WAVAX, quote: $3.75M USDC).

**D5 Milestone Alignment**:
- Position value ($126.39) → Scout tier ($5/day target) — 48.7% progress
- Price inside position range ✅
- IL ✓ well below 2% threshold (-0.15%)
- Est. daily fees $2.43 — need 2x to hit Scout

**Other Pools**: None active

---
## 2026-05-09 20:18 UTC Update
**Price Range**: $9.78–$10.02 (Shape: curve)
**Balances**: 6.758 AVAX (~$67.51) + 58.5 USDC (~$58.50) = **$126.01**
**Fees (24h)**: $1.19
**IL**: -0.2% (vs. HODL)
**Range Status**: 🟢 In Range (price at $9.99, 87.5% from bottom)
**Last Rebalance**: 2026-05-09 11:06 UTC (jordan_screenshot)
**Action**: Monitor — approaching top boundary

**Market Notes**: AVAX at $9.99 (24h +1.07%), inside position range $9.78–$10.02. Pool volume $4.59M/day, TVL $4.04M. BTC $80,815 (+0.78%), SOL $93.32 (+0.99%), LINK $10.42 (+0.8%), TAO $310.84 (-0.57%), XAUt $4,709.01, BEAM $0.002098 (+1.03%).

**On-Chain Data**: Pool WAVAX/USDC 5bps on LFJ v2.2 (Avalanche). Liquidity $4.04M.

**D5 Milestone Alignment**:
- Position value ($126.01) → Scout tier ($5.00/day target) — 23.8% progress
- Price inside position range ✅
- IL ✓ well below 2% threshold (-0.2%)
- Est. daily fees $1.19 — need 4.2x to hit Scout

**Other Pools**: None active


## 2026-05-09 12:47 UTC Update
**Price Range**: $9.78–$10.02 (Shape: curve)
**Balances**: 9.19 AVAX (~$91.16) + 35.87 USDC (~$35.87) = **$127.03**
**Fees (24h)**: $1.19 (tracker) / $2.43 (est. from volume $12.48M × 5bps × 0.039% share)
**IL**: ~0.00% (vs. HODL) — price centered in rebalanced range
**Range Status**: 🟢 In Range (58.3% from bottom)
**Last Rebalance**: 2026-05-08 09:00 UTC (jordan_manual)
**Action**: No rebalance needed — price inside position range. Est. daily fees $2.43 approaching Scout milestone.

**Market Notes**: AVAX at $9.92 (24h +3.41%), inside position range $9.78–$10.02. Pool volume $12.48M/day, TVL $4.04M. Strong risk-on across altcoins: SOL +5.27%, LINK +4.80%, BEAM +2.83%. BTC steady at $80,333 (+0.13%). Gold (XAUt) flat at $4,700.

**On-Chain Data**: Pool WAVAX/USDC 5bps on LFJ v2.2 (Avalanche). 2,378 buys / 2,511 sells in 24h — balanced flow. Liquidity $4.04M (base: 28,684 WAVAX, quote: $3.75M USDC).

**D5 Milestone Alignment**:
- Position value ($127.03) → Scout tier ($5/day target) — 48.7% progress
- Price inside position range ✅
- IL ✓ well below 2% threshold (~0.00%)
- Est. daily fees $2.43 — need 2x to hit Scout

**Other Pools**: None active

---


## 2026-05-09 12:15 Update
**Price Range**: $9.78–$10.02 (Target: $8.95–$9.36)
**Balances**: 9.19 AVAX (~$91.26) + 35.87 USDC (~$35.87) = **$127.13**
**Fees (24h)**: $2.55 (est. from volume $12.96M × 5 bps × 0.039% effective share)
**IL**: 0.00% (vs. HODL) — price centered in rebalanced range
**Efficiency**: 75.0% (price at 62.5% of position range)
**Action**: No rebalance needed — price inside position range. Position rebalanced to $9.78–$10.02 (manual rebalance detected).

**Market Notes**: AVAX at $9.93 (24h +3.64%), above strategic target $8.95–$9.36 but within position range $9.78–$10.02. Pool volume $12.96M/day (3.2x TVL). B/S ratio 0.956 — balanced. JOE at $0.0493 (+2.64%). BTC $80,302 (+0.03%), ETH $2,314 (+0.95%).

**On-Chain Data**: Rebalance detected — range shifted from $9.45–$9.74 to $9.78–$10.02. Composition changed: AVAX 5.93→9.19, USDC 78.54→35.87.

**D5 Milestone Alignment**:
- Position value ($127.13) aligns with **Scout** tier ($5/day target) — 51.0% progress
- Price is outside target band $8.95–$9.36 (above) but inside position range ✅
- IL ✓ well below 2% threshold (0.00%)
- Efficiency ✓ at 75.0% — good concentration

**Other Pools**: None active

---

## 2026-05-07 Update
**Price Range**: $9.45–$9.74 (Target: $8.95–$9.36)
**Balances**: 5.93 AVAX (~$57.05) + 78.54 USDC (~$78.54) = **$135.59**
**Fees (24h)**: $1.17 (est. from volume $31.6M × 5 bps × 0.0074% share)
**IL**: 0.00% (vs. HODL) — price nearly unchanged from entry reference
**Efficiency**: 89.7% (price centered in position range, bin position 0.55)
**Action**: No rebalance needed — price inside position range. Consider adding liquidity to increase share % and fee capture.

**Market Notes**: AVAX at $9.62 (24h -1.06%), still above strategic target $8.95–$9.36 but within position range $9.45–$9.74. Pool volume strong at $31.6M/day (7.8x TVL). B/S ratio 0.839 — sell pressure moderate. JOE at $0.0482 (-1.31%).

**D5 Milestone Alignment**:
- Position value ($135.59) aligns with **Scout** tier ($5/day target) — 23.4% progress
- Price is outside target band $8.95–$9.36 (above) but inside position range ✅
- IL ✓ well below 2% threshold (0.00%)
- Efficiency ✓ at 89.7% — excellent concentration

**Other Pools**: None active

---

## 2026-05-07 20:15 Update
**Price Range**: $9.45–$9.74 (Target: $8.95–$9.36)
**Balances**: 5.93 AVAX (~$56.34) + 78.54 USDC (~$78.54) = **$134.88**
**Fees (24h)**: $1.41 (est. from volume $38.1M × 5 bps × 0.0074% share)
**IL**: ~0.1% (vs. HODL) — minimal, price within position range
**Efficiency**: 89.7% (price centered in position range)
**Action**: No rebalance needed — price inside position range. Volume up 20% from last check, boosting fee capture.

**Market Notes**: AVAX at $9.50 (24h -1.41%), still above strategic target $8.95–$9.36 but within position range $9.45–$9.74. Pool volume strong at $38.1M/day (9.5x TVL). B/S ratio balanced (105 buys vs 100 sells 1h). JOE at $0.0484 (+0.53%). BTC $80,149 (-1.83%), ETH $2,295 (-2.43%).

**D5 Milestone Alignment**:
- Position value ($134.88) aligns with **Scout** tier ($5/day target) — 28.2% progress
- Price is outside target band $8.95–$9.36 (above) but inside position range ✅
- IL ✓ well below 2% threshold (~0.1%)
- Efficiency ✓ at 89.7% — excellent concentration

**Other Pools**: None active

---

# LFJ AVAX/USDC LP Position — Live Tracker

**Pool**: LFJ V2.2 AVAX/USDC 5bps (Avalanche)
**Contract**: `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
**Wallet**: `[REDACTED_WALLET]`
**Shape**: Curve
**Entry Date**: 2026-03-31

---


## 2026-05-07 Update
**Price Range**: $9.45–$9.74 (Target: $8.95–$9.36)
**Balances**: 5.93 AVAX (~$57.37) + 78.54 USDC (~$78.54) = **$135.91**
**Fees (24h)**: $1.15 (est. from volume $31.2M × 5 bps × 0.01% share)
**IL**: N/A — DCA-adjusted position; LP value $135.91 vs approx invested $134.94
**Efficiency**: 0.01% avg share across 32 bins (low — position is small fraction of pool)
**Action**: No rebalance needed — price inside position range. Consider adding liquidity to increase share % and fee capture.

**Market Notes**: AVAX at $9.6660 (24h +0.75%), above strategic target $8.95–$9.36. Position range $9.45–$9.74 is well-calibrated for current price. Pool volume strong at $31.2M/day (7.7x TVL). B/S ratio 0.881 — slight sell pressure but improving.

**On-Chain Data**: Active bin 8363232, 32 bins with user shares (8363210–8363241). Avg share 0.0074% across position.

---
## 2026-05-13 Update
**Price Range**: $9.95–$10.30 (Target: $8.95–$9.36)
**Balances**: 21.02 AVAX (~$203.05) + 0.00 USDC (~$0.00) = **$203.37**
**Fees (24h)**: $0.26 (est. from $10.2M vol × 5bps × 0.005% share × 1.0x CL; out of range)
**IL**: ~+2.7% (approximate — position recently rebalanced)
**Efficiency**: -156.3% — OUT OF RANGE, zero fee capture
**Action**: 🚨 OUT OF RANGE — price $9.66 below range $9.95–$10.30. Position is 100% AVAX. Rebalance suggested: re-center range around current price.

**Market Notes**: AVAX at $9.6612 (-0.73%), below position range $9.95–$10.30. Pool volume $10.2M/day (2.5x TVL). Position fully converted to AVAX as price dropped through range.

**D5 Milestone Alignment**:
- Tier Scout ($5/day target) — $0.26/day estimated → below target
- Price OUTSIDE strategic band $9.95–$10.30 (below)
- IL ~+2.7% — above 2% threshold ⚠️
- Efficiency -156.3% < 50% → Micro-DCA boost triggered

**Other Pools**: None active

---

## 2026-05-15 Update (16:16 UTC)
**AVAX Price**: $9.5000 (-5.63% 24h)
**USDC Price**: $0.9998
**Price Range**: $9.65–$9.95 (Shape: Curve)
**Target**: $8.95–$9.36
**Balances**: 20.59 AVAX (~$195.58) + 0.00 USDC (~$0.00) = **$195.66**
**Wallet**: 0.1141 AVAX (~$1.08) + 0.0000 USDC (~$0.00) = **$1.08** | **Combined Total**: **$196.74**
**Fees (24h)**: $0.00 (out of range — no active fee capture; if in range: ~$1.50/day from $20.6M vol × 5bps × 0.0049% pool share × 3x CL boost; oracle not configured)
**IL**: +1.9% ✓ below 2% threshold
**Efficiency**: -97.4% — 🚨 OUT OF RANGE, zero fee capture
**Action**: 🚨 OUT OF RANGE — price $9.50 below range $9.65–$9.95. Position 100% AVAX. Rebalance suggested: re-center range around current price or wait for recovery.

**Market Notes**: AVAX at $9.5000 (-5.63% 24h), dropped below position range. Pool volume $20.6M/day (5.1x TVL). Position fully converted to AVAX as price fell through range floor. Price dropped ~$0.27 from last entry at $9.77.

**D5 Milestone Alignment**:
- Tier Scout ($5.00/day target) — est. daily fees $0.50 → below target
- Price OUTSIDE strategic target band $8.95–$9.36 AND outside position range
- IL +1.9% ✓ below 2% threshold
- Efficiency -97.4% <50% → Micro-DCA boost triggered

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

**Note**: Price dropped $5.63% in 24h, fell below range floor $9.65. Position shifted from 73/27 AVAX/USDC split (at 12:18 UTC) to 100/0. Efficiency collapsed from 69.4% to -97.4%. Pool TVL $4.05M, volume $20.6M/24h.


## 2026-05-15 Update (20:16 UTC)

**AVAX Price**: $9.5151 (-4.80% 24h)
**USDC Price**: $0.9998 (+0.02% 24h)
**Price Range**: $9.30–$9.60 (Shape: Bidirectional)
**Target**: $8.95–$9.36
**Balances**: 7.74 AVAX (~$73.62) + 116.70 USDC (~$116.65) = **$190.29**
**Wallet**: 0.1141 AVAX (~$1.09) + 0.0000 USDC (~$0.00) = **$1.09** | **Combined Total**: **$191.38**
**Fees (24h)**: $0.83/day (est. from $23.7M vol × 5bps × 0.0047% pool share × 1.5x CL; oracle not configured)
**IL**: +0.0% ✓ below 2% threshold
**Efficiency**: 51.4% ≥50% ✓
**Action**: ✅ Position in range, IL stable, efficiency recovered above 50%. No rebalance needed. Micro-DCA boost no longer triggered.

**D5 Milestone Alignment**:
- Tier Scout ($5.00/day target) — est. daily fees $0.83/day → below target
- Price inside strategic target band $8.95–$9.36 (position range $9.30–$9.60, price at 71.7% of range)
- IL +0.0% ✓ below 2% threshold
- Efficiency 51.4% ≥50% ✓

**📐 Shape Analysis**: Price stagnant (0.2% range) — switching to CURVE could boost fee efficiency. Current bidirectional shape earns best during swings, but price is consolidating.

**🎯 Scout ($5.00/day): [==○○○○○○○○○○○○○○○○○] 16.6% — $0.83/day**

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

**Note**: Range rebalanced from $9.65–$9.95 (16:16 UTC) to $9.30–$9.60. Position re-centered: was 100% AVAX at $195.66, now 38.7/61.3 AVAX/USDC split at $191.38. Efficiency recovered from -97.4% to 51.4%. Pool TVL $4.11M, volume $23.7M/24h. AVAX down 4.80% in 24h.

