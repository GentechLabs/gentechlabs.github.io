# AAE Tracker Pivot Log — 2026-04-25

**Pivot triggered by:** Jordan (HQ)

## Changes

| Before | After |
|--------|-------|
| Simulated / paper trading included | ❌ Removed entirely |
| NL trigger locked to X/Twitter API | ✅ Any relevant market news source |
| No monetization | ✅ Subscription model (Free vs Pro, $15-20/mo) |
| No gamification | ✅ REP/XP, streaks, leaderboards, achievements |
| Multi-agent per user (potential) | ✅ **1 agent per user** (generalist) |

## Architecture Decision: 1 Agent Per User

- Each user gets ONE personalized generalist agent
- Agent handles: DCA, fee tracking, rewards, news sentiment, LP rebalancing, gamification, subscription gating
- No specialist swarm per user — simplifies orchestration, agent is the user's financial companion

## Active Routes

| Agent | Group | Task | Status |
|-------|-------|------|--------|
| DMOB | Labs | Re-scope for single-agent architecture + subscription gating + sentiment pipeline | Pending |
| Desmond | Creative | Gamification copy (achievements, tiers, leaderboards, onboarding) | Pending |
| YoYo | Strategies | Subscription pricing model for $TECH/USDC dual pricing | On hold until DMOB reports |

## Spec Location
`01-Agency/AAE-DCA-Fee-Tracker-Spec.md`
