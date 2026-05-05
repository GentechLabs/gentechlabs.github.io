# LFJ AVAX/USDC LP Position — Vault

**Pool**: `0x864d4e5ee7318e97483db7eb0912e09f161516ea` (LFJ V2.2, binStep 10, 5 bps)
**Wallet**: `0x7ebff188f2Eba16518C02864589b1403a5d1296a`
**Shape**: Curve
**D5 Tier**: Scout ($3/day target)

> ⚠️ **Pool Address Note**: The address `0x864d3897f3431ad0a5bc16ea987e37816ea95291` requested in the runbook returned **no contract code** on Avalanche C‑Chain. This vault sources data from the active tracked pool `0x864d4e5ee7318e97483db7eb0912e09f161516ea` per `lfj_config.json` and `.lfj-aae-config.json`.

---

## 2026-05-05 Update
**AVAX Price**: $9.4000 (+2.84% 24h) ⚠️ PRICE ALERT
**JOE Price**: $0.0475 (-0.63% 24h)
**LP Position**: 🚨 **EMPTY** — No active LFJ position detected on-chain
**Wallet**: 0.0971 AVAX (~$0.91) + 0.000009 USDC (~$0.00) = **$0.91**
**Fees (24h)**: $0.00 (no active position)
**IL**: N/A (position withdrawn)
**Efficiency**: N/A
**Action**: 🚨 CRITICAL: LP position withdrawn — wallet holds only dust balances. No active LFJ position detected on-chain.

**Pool Data**:
- Pool TVL: $4,010,303
- 24h Volume: $17,546,240
- Total Pool Fees (24h): $8,773

**D5 Milestone Alignment**:
- 🚨 **No active position** — Scout tier suspended until position is re-established.
- AVAX $9.40 is OUTSIDE target band $9.25-$9.59 (above upper bound).
- IL: N/A.
- Efficiency: N/A.

**Other Pools**: No additional LFJ pools detected with active positions for this wallet.

**Recent Transactions** (May 5):
- 12:49 UTC: 8.207 AVAX sent to 0x18556da13313f3532c54711497a8fedac273220e
- 12:47 UTC: Interaction with 0x45a62b090df48243f12a21897e7ed91863e2c86b
- 11:13 UTC: 6.822 AVAX sent to 0x18556da13313f3532c54711497a8fedac273220e

**Telegram Alert**: 🚨 CRITICAL — LP POSITION EMPTY. Sent to -1002916759037 at 16:15 UTC.

---

## 2026-05-04 Update
**AVAX Price**: $9.20 (feed)
**Price Range**: $8.95–$9.36 (Target: $8.95–$9.36)
**Balances**: 11.64 AVAX (~$106.86) + 29.15 USDC (~$29.15) = **$136.01**
**Fees (24h)**: $0.15 (est. from pool volume $8,523,107 × 5 bps × 0.00% share)
**IL**: -41.97% (vs. HODL)
**Efficiency**: 87.8%
**Rewarded Bin**: ✅ Active ($9.18)
**Action**: ⚠️ REVIEW NEEDED — IL exceeded 2% threshold; investigate root cause.

**D5 Milestone Alignment**:
- Position value ($136.01) aligns with **Scout** tier ($3/day target).
- Price $inside strategic band $8.95–$9.36.
- 🔴 IL 41.97% > 2% threshold → Review required. Current ΔIL = 59.62 pp vs. last entry.
- Efficiency 87.8% ≥ 50% (healthy).

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

**Telegram Alert**: 🚨 IL CRITICAL — Sent to -1002916759037 at 16:35 UTC.

---


## 2026-05-03 Update
**AVAX Price**: $9.07 (-0.18% 24h)
**Price Range**: $9.00–$9.45 (Target: $8.95–$9.36)
**Balances**: 11.64 AVAX (~$105.57) + 29.15 USDC (~$29.15) = **$134.72**
**Wallet**: 0.0969 AVAX (~$0.88) | **Combined Total**: **$135.60**
**Fees (24h)**: $0.04 (est. from pool volume ~$2.48M × 5 bps × 3.5% share)
**IL**: -17.65% (vs. HODL)
**Rewarded Bin**: ✅ Active bin 8363171 within position range [8363161–8363210]
**Efficiency**: 31.1%
**Action**: ⚠️ REVIEW NEEDED — IL exceeded 2% threshold; investigate rebalance.

**D5 Milestone Alignment**:
- Position value ($134.72) aligns with **Scout** tier ($5/day target).
- Price is inside the strategic target band ($8.95–$9.36).
- 🔴 IL 17.65% > 2% threshold → **Review required**.
- Efficiency 31.1% < 50% → Micro-DCA boost remains active.

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

**Telegram Alert**: ⚠️ IL EXCEEDED 2% — Sent to -1002916759037 at 11:43 UTC.

## 2026-05-02 Update
**AVAX Price**: $9.1600 (-0.19% 24h)
**Price Range**: $9.00–$9.37 (Target: $8.95–$9.36)
**Balances**: 11.64 AVAX (~$106.62) + 29.15 USDC (~$29.15) = **$135.77**
**Wallet**: 0.0969 AVAX (~$0.89) | **Combined Total**: **$136.66**
**Fees (24h)**: unavailable — fee oracle not configured; volume APIs unreachable
**IL**: +0.6% (vs. previous day)
**Rewarded Bin**: ✅ Active bin 8363179 within position range [8363161–8363210]
**Efficiency**: ~38%
**Action**: No rebalance needed — price within target range, IL below 2% threshold. Efficiency <50% → Micro-DCA condition persists.

**D5 Milestone Alignment**:
- Position value ~$135.77 aligns with **Scout** tier ($3–$5/day target).
- Price $9.16 within strategic band $8.95–$9.36.
- IL +0.6% ✓ under 2% review trigger.
- Efficiency 38% <50% → Micro‑DCA boost active.

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

## 2026-05-01 Update
**AVAX Price**: $9.1111
**Price Range**: $8.95–$9.36 (Target: $8.95–$9.36)
**Balances**: 6.21 AVAX (~$56.58) + 78.0 USDC (~$78.01) = **$134.59**
**Wallet**: 0.0969 AVAX (~$0.88) | **Combined Total**: **$135.47**
**Fees (24h)**: ~$0.0319 (est. from pool volume $1.84M × 5 bps × 0.0348 share)
**IL**: 0.0% (vs. HODL)
**Rewarded Bin**: ✅ Active bin within position range
**Efficiency**: ~74%
**Action**: Rebalance suggested: JOE +8.29%

**D5 Milestone Alignment**:
- Position value ($134.59) aligns with **Scout** tier ($3/day target).
- Price is inside the strategic target band ($8.95–$9.36) and the config range ($8.95–$9.36).
- IL is well below the 2% review threshold.
- Micro‑DCA trigger: Efficiency ≥50% → no bonus DCA required.

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

## 2026-04-30 Update
**AVAX Price**: $9.17
**Price Range**: $8.96–$9.37 (Target: $8.95–$9.36)
**Balances**: 6.21 AVAX (~$56.94) + 78.00 USDC (~$78.00) = **$134.94**
**Wallet**: 0.0969 AVAX (~$0.89) | **Combined Total**: **$135.83**
**Fees (24h)**: unavailable — on‑chain fee oracle not yet configured (DexScreener 24h pool volume: $4.64M)
**IL**: ~0.0% (vs. HODL)
**Rewarded Bin**: ✅ Active bin 8363180 within position range (46 bins total)
**Efficiency**: 74.7%
**Action**: No rebalance needed.

**D5 Milestone Alignment**:
- Position value ($134.94) and range health align with **Scout** tier.
- Price is inside the strategic target band ($8.95–$9.36) and the config range ($9.00–$9.45).
- IL is well below the 2% review threshold.
- Micro‑DCA trigger: Efficiency ≥50% → no bonus DCA required.

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

*Next check: 4× daily (08:15 / 12:15 / 16:15 / 20:15 UTC). Updates are appended only when material changes occur (IL ≥0.5% or price exits range).*
---
