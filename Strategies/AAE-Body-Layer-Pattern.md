# LP Monitor → AAE Body Pattern

**Date:** 2026-04-21
**Source:** LP Unified Monitor (AVAX/USDC on LFJ)
**Status:** Reference Pattern for AAE

## The Pattern (What We Built)

The LP Unified Monitor is a prototype of what AAE's "body" layer should do for every user's DeFi position.

### Core Data Layers
1. **Position Awareness** — "Here's what you put in, here's where it sits"
2. **Yield Tracking** — "Here's what you're making per day" (no mental math)
3. **Milestone Progression** — "X days from your next goal" (turns passive farming into a game)
4. **Smart Alerts** — Silent when fine, loud when action needed

### The Retention Loop
Maps to The Trade Off vision: *lose → analyze → learn → improve → stay*

Applied to money management:
- **Lose** → See position drop below range, fee efficiency drops
- **Analyze** → Agent explains why, shows IL vs fees earned
- **Learn** → Simulated "what if" scenarios (compound at $75/wk vs $50/wk)
- **Improve** → Auto-rebalance suggestions, DCA optimization
- **Stay** → Milestone gamification keeps them engaged

## Monetization Angle

**Hook:** Free monitor — users see position, milestones, projected earnings
**Upsell:** Premium simulated learning
- "What if you compound at $75/week instead of $50?"
- "What if you LP'd a tighter range?"
- Agent auto-rebalance when out of range
- Multi-position dashboard

## Implementation
- Script: `scripts/lp-unified-monitor.py`
- Cron: `00ef264dbdab` (every 10 min)
- Can be abstracted to any LP/DeFi position
- State persistence via JSON
- Multi-source data (Birdeye + DexScreener fallback)

## For AAE Integration
This pattern generalizes to ANY yield-bearing position:
- LP positions (any DEX, any chain)
- Staking rewards
- Lending protocol interest
- Auto-compound vaults

Each user gets their own "body" layer with personalized milestones and alert preferences.

## Tags
#project:aae #pattern:monitor #layer:body #agent:all
