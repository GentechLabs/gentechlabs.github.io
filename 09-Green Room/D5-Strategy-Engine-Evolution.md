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

## Completed
- [x] **YoYo** — Model ROI potential of each enhancement, rank by alpha-per-complexity
- [x] **YoYo** — Implement hybrid DCA strategy in LP monitor (v2.1)
- [x] **Gentech** — Consolidation (Apr 26): Merged D5 milestone tracking into hourly unified cron (`faed4f588aef`). Paused standalone daily D5 cron (`76d0ee972be9`). D5 block now appears in every hourly report with tier progression, efficiency, and action recommendations.
- [x] **DMOB** — Wallet Monitor (Apr 28): Created `wallet-monitor.py` script tracking AVAX, WAVAX, USDC balances on Avalanche C-Chain. State file tracks deltas between checks. Cron job `81c989cc5886` runs every 3h (local delivery). Feeds D5 with DCA readiness + portfolio value context.

## Action Items
- [ ] **DMOB** — Scope on-chain data requirements: fee growth oracles, liquidity shape APIs, bid-ask depth feeds, execution complexity for automated rebalancing.
- [ ] **Gentech** — Once YoYo + DMOB report, consolidate into a phased roadmap for Jordan.
- [ ] **DMOB** — Build "Go Spot" indicator script (regime detection: AVAX hold, BTC trend, macro pivot, volume, higher lows). See `03-Strategies/hybrid-lp-spot-strategy.md` for full spec.
- [ ] **YoYo** — Integrate regime signals into hourly LP monitor. When 3+ signals fire → recommend "EXIT LP → SPOT".
- [ ] **Gentech** — Finalize indicator thresholds after backtesting on historical AVAX data.

## Context
Current unified cron (`YoYo — AAE DeFi Milestone + LP Monitor`) already pulls:
- TVL, APY, IL vs HODL for AVAX/USDC pool (0x864d...16EA)
Current unified cron (`YoYo — AAE DeFi Milestone + LP Monitor`) now runs `lp-aae-signal-monitor.py` directly:
- Hourly (7AM–9PM EDT), silent unless alert
- Position value, splits, price, range, efficiency, APR
- Revenue: 24H fees, cumulative, claimable, days in range
- Progression: Scout→Raider→Warlord→Sovereign tier tracking
- Action: HOLD / WATCH / COMPOUND / DCA / REBALANCE
- **NEW (Apr 26):** Bid-ask-aware micro-DCA sizing ($10–$20) based on efficiency thresholds

This is the single source of truth.

---

## Live LP Snapshot (Apr 26, 2026)

| Metric | Value | Status |
|--------|-------|--------|
| Pool | LFJ V2.2 AVAX/USDC | ✅ Active |
| Efficiency | ≥50% | ✅ In-range |
| D5 Progress | $0 / $50 | ⏳ Pending |
| DCA Trigger | None | ⏳ Wait for efficiency drop |
| Pool fees (24h) | — | 🟡 Awaiting next cron |

> _“This could literally run, and it's easy to look at.”_ — Jordan, Apr 26 — consolidated LP + D5 status in one view.
