# D5 Strategy Engine — Evolution Brief
**Date:** 2026-04-24  
**Source:** Jordan (voice feedback on unified LP + D5 cron)  
**Status:** Open — awaiting YoYo strategy model + DMOB tech scoping

---

## Jordan's Vision
Upgrade the D5 from a static threshold-DCA into a **dynamic strategy engine** that integrates real-time LP telemetry:

1. **Fee-Earning-Based DCA** — Trigger capital adds based on cumulative fee growth / yield acceleration, not just time+threshold.
2. **Liquidity Shape Integration** — Read the pool's liquidity distribution (bid-ask width, depth) to shape DCA timing and sizing.
3. **Bid-Ask-Aware Entries** — Load the "cheap" side first when spread is wide; essentially programmatic range-order market making.
4. **Curve-Style Concentrated Liquidity** — Granular range-order strategies for advanced capital efficiency.
5. **Dynamic Thresholds** — Adjust the $50 (or future) threshold based on market regime / volatility.

## Jordan's Decision (Apr 25, 2026)

**DCA Strategy: Hybrid Base + Micro-DCA**

- **Base DCA:** $50/week every Monday (unchanged — discipline-first)
- **Micro-DCA:** $10–$20 bonus DCA triggered by fee efficiency drops:
  - 40–50% efficiency → $10 bonus DCA + monitor for rebalance
  - <40% efficiency → $20 bonus DCA + strongly consider rebalancing

**Rationale:** Weekly base builds position size predictably. Micro-DCA capitalizes on temporary range edge positioning without overcommitting to stale ranges. Never DCA without considering a rebalance first.

## Action Items
- [x] **YoYo** — Model ROI potential of each enhancement, rank by alpha-per-complexity. What's the lowest-hanging fruit?
- [x] **YoYo** — Implement hybrid DCA strategy in LP monitor (v2.1)
- [ ] **DMOB** — Scope on-chain data requirements: fee growth oracles, liquidity shape APIs (e.g., Gamma, Beefy, or direct subgraph queries), bid-ask depth feeds, execution complexity for automated rebalancing.
- [ ] **Gentech** — Once YoYo + DMOB report, consolidate into a phased roadmap for Jordan.

## Context
Current unified cron (`YoYo — AAE DeFi Milestone + LP Monitor`) already pulls:
- TVL, APY, IL vs HODL for AVAX/USDC pool (0x864d...16EA)
- D5 capital-add threshold ($50) and DCA window (Monday)
- **NEW:** Micro-DCA triggers at 40%/50% efficiency thresholds

This is the foundation. The next layer is **strategy intelligence** — fee-growth-based DCA, liquidity shape integration, and dynamic thresholds.
