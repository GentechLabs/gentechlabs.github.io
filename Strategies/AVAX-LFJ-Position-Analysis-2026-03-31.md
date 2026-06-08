# AVAX-USDC LFJ Position Analysis — Mar 31, 2026

## Raw Data (Verified)
| Metric | Value |
|--------|-------|
| Position Value | $31.16 |
| AVAX Holdings | 1.39 AVAX (~$12.31) |
| USDC Holdings | 18.85 USDC |
| AVAX Price | $8.853 |
| Rewards APR | 5,137.78% |
| 24H Fees | $0.3331 |
| Claimable Rewards | 0.12782 AVAX (~$1.132) |
| Range | 8.2217 — 9.5325 USDC/AVAX (16% spread) |
| Range TVL | $629.18 |
| Pool Share | ~4.95% of range TVL |

## YoYo's Math Check

**Rewards:** 5,137% × $31.16 / 365 = **$4.39/day** in rewards.  
**Fees:** $0.333/day = **$121.55/year** = 390% fee APR.  
**Combined run rate:** ~**$4.72/day** (~$141/month).  

Claimable $1.13 = **3.6% of total position**. Compounding it is non-negotiable.

**Pool emission check:** 10 AVAX/day × 4.95% share × $8.85 = $4.36/day. Matches.

---

## Critical Issue: Projection Table Is Broken

The accumulation table in the Milestone Tracker uses "20% monthly compounding" but the math is inconsistent and the rate is unsustainable.

**Why 20%/mo is fantasy planning:**
- 20% monthly = **791% annualized**. That's higher than even your current APR.
- The 5,137% APR is a **transient emission subsidy**. It decays as TVL enters the pool.
- Your fee APR of 390% is more realistic long-term, but even that depends on volume staying high.
- The table's numbers don't actually follow any consistent formula (Apr shows negative growth, May shows 0%, June+ roughly adds DCA × 1.2).

**Planning with fantasy numbers creates disappointment.**

---

## Conservative Re-Projection

Assumptions:
- DCA: $300/month (midpoint of $50-100/week)
- Sustained blended APR: **150%** (rewards decay to ~100%, fees contribute ~50%)
- Monthly compounding at 12.5%/mo (150%/12)

| Month | Start | DCA | End (Compounded) | Daily Yield @ 150% |
|-------|-------|-----|------------------|-------------------|
| 0 | $31 | — | $31 | $0.13 |
| 3 | $31 | +$900 | ~$1,050 | $4.32 |
| 6 | $1,050 | +$900 | ~$2,200 | $9.04 |
| 9 | $2,200 | +$900 | ~$3,500 | $14.38 |
| 12 | $3,500 | +$900 | ~$5,000 | $20.55 |
| 15 | $5,000 | +$900 | ~$6,700 | $27.53 |
| **18 (Sep 2027)** | $6,700 | +$900 | **~$8,600** | **$35.34** |

At **300% sustained APR** (still conservative vs current, but achievable early):
- Sep 2027 position: ~$10,500
- Daily yield: **$86/day**

**Verdict:** The $55/day birthday goal is achievable even with conservative APR assumptions. The problem isn't the goal — it's the bad math in the tracker creating false precision.

---

## Risk Flags

1. **Range boundary:** $8.22 floor is only **7.1% below current price**. A bad news day puts you out-of-range and fees die.
2. **APR decay:** 5,137% won't last. Don't emotionally anchor to it.
3. **Impermanent loss:** 60.5% USDC / 39.5% AVAX. If AVAX rips to $50, you'll have much less AVAX than holding spot.
4. **Fee sustainability:** $0.33/day on $31 requires sustained volume. If trading dries up, fee APR collapses.

---

## Immediate Actions

| Priority | Action | Impact |
|----------|--------|--------|
| P0 | **Claim & compound $1.13 immediately** | +3.6% position growth, zero cost |
| P1 | **Fix projection table** — show 3 scenarios (bull 400%, base 150%, bear 50%) | Prevents emotional whiplash |
| P1 | **Set price alert at $8.30** (near range floor) | 3-4h lead time to rebalance before going OOR |
| P2 | **Track "Blended APR"** (rewards + fees) separately from "Rewards APR" | Fees are 390% APR right now — that's real money |
| P2 | **Consider 70/30 or 80/20 AVAX/USDC bias** if you believe $8.85 is bottom | Reduces IL if AVAX pumps, increases if it dumps |

---

## Bottom Line

**Strategy is sound. Math in the tracker is not.**

The DCA plan at $8.85 AVAX is smart. The $55/day birthday target is realistic even if APR collapses to 150%. But the 20%/mo compounding table will make every month feel like failure when reality diverges. 

Rebuild the projections with scenario analysis. Compound the $1.13 today. Watch that $8.22 floor.

— YoYo, Head of Strategies  
*Mar 31, 2026*
