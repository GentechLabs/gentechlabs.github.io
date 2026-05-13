# AAE DCA + Fee + Rewards Tracker — Product Spec

**Date:** 2026-04-25
**Status:** Queued for build — **PIVOTED Apr 25**

---

## Pivot Summary

- ❌ **Removed:** Simulated/paper trading
- ❌ **Removed:** Multi-agent per user
- ✅ **Added:** Gamification layer
- ✅ **Added:** Subscription model (unlocks all features, funds bot maintenance)
- ✅ **Changed:** NL trigger source is now **any relevant market news** (not just X/Twitter)
- ✅ **New constraint:** **1 agent per user** (generalist agent, not specialist swarm)

---

## Architecture: One Agent Per User

Each user has **one personalized agent** that handles:

| Capability | Description |
|-----------|-------------|
| **DCA Execution** | Static schedules + custom NL strategies |
| **Fee Tracking** | 5 default presets + custom fee configs |
| **Rewards Monitoring** | Real-time APR + one-click claims |
| **News Sentiment** | Pulls market news, scores sentiment, triggers decisions |
| **LP Rebalancing** | Position adjustments based on strategy (not trading) |
| **Gamification** | Tracks XP/REP, streaks, achievements, tier progress |
| **Subscription** | Enforces Free vs Pro tier gating |

**Agent persona:** Generalist financial assistant, not a swarm of specialists.

---

## Feature Set: 3 Core Components

### 1. DCA Schedule (AgentPaymentFlow)
- **Default options:** Weekly, Monthly, Yearly (static intervals)
- **Custom strategy builder:** Users write/prompt their own DCA strategy
- **Example strategy:** "Invest on days when Trump tweets negative" → generalizes to any news sentiment trigger
- **Funding source:** Amazon Flex income ($50–100/week)
- **Target:** $31.16 position → $55/day by Sep 2027
- **News sources:** Configurable (X API, RSS feeds, news APIs, on-chain events)
- **Agent decision:** Parses sentiment (good/bad) → buy/skip/hold

### 2. Rewards Tracking (Incentives Engine)
- **Metric:** 5,137% APR, claimable AVAX
- **Feature:** Real-time rewards accrual display
- **Action:** One-click claim integration

### 3. Fee Tracking
- **Default settings:** 5 preset fee-earning configurations
- **Custom:** User-defined fee capture strategies
- **Integration:** Tie into overall P&L dashboard

---

## Gamification Layer

| Element | Description |
|---------|-------------|
| **XP / REP** | Earn REP for consistent DCA, hitting milestones, creating winning strategies |
| **Leaderboards** | Top-performing custom strategies (anonymized or opted-in) |
| **Streaks** | Consecutive weeks of DCA execution |
| **Achievements** | First claim, 30-day streak, custom strategy profit, etc. |
| **Tiers** | Free tier = static DCA only. Subscription = custom strategies + full news feed + gamification |
| **Tier Progression** | Scout → Architect (or Desmond's names when ready) |

---

## Subscription Model

| Tier | Price | Unlocks |
|------|-------|---------|
| **Free** | $0 | Static weekly/monthly/yearly DCA + basic fee tracker |
| **Pro** | $15–20/mo ($TECH or USDC) | Custom NL strategies, full news sentiment engine, gamification, leaderboards, advanced fee presets, LP rebalancing |

- Subscription revenue → bot maintenance + development fund
- Dual pricing: USDC full price, $TECH 20–30% discount

---

## News → Decision Pipeline

```
News Feed (X API / RSS / Web / On-chain)
    → Sentiment Analysis (good / bad / neutral)
    → Trigger Engine (matches user's NL strategy)
    → Agent Decision (rebalance LP / skip / hold)
    → On-chain Execution
```

---

## Next Steps
- [ ] DMOB: Scaffold single-agent architecture (not multi-agent)
- [ ] DMOB: Build subscription gating contract
- [ ] DMOB: Build sentiment + trigger parser (NL → conditions)
- [ ] DMOB: Fee tracking module + 5 default presets
- [ ] YoYo: Model ROI projections for default strategies + subscription pricing
- [ ] Desmond: Gamification UX copy + achievement names + tier progression names
