# AAE LP Dashboard — Product Concept

*Source: Jordan voice note, Apr 21 2026*

## Core Insight
The LP tracker isn't just a personal tool — it's a core AAE product feature. Users want to know:
1. What they're putting in
2. What they're making daily (especially yield farming)
3. Progress toward milestones/goals
4. What to do next

## What Exists vs. What We're Building

| Existing Tools | AAE Dashboard |
|----------------|---------------|
| DeBank: shows *what you have* | Shows *how you're doing vs. goals* |
| Zapper: portfolio view | Projection + action prompts |
| Manual tracking | Agent-coach with recommendations |

## Tier Structure (Draft)

### Free Tier — The Hook
- Manual LP position + milestone tracker
- Paste wallet → get dashboard
- Conservative projections (realistic APR ranges)

### Pro Tier ($X/mo)
- Auto-monitoring via cron (like YoYo's LP watcher)
- Rebalancing alerts
- DCA impact modeling
- Multi-pool tracking
- Market condition adaptation (bull/bear/chop modes)

### Autopilot (Pay-to-Launch)
- One-time fee for custom agent deployment
- Agent actively manages LP position
- Auto-rebalance, range adjustment, exit triggers
- Full "set and forget" experience

## Connection to Simulated Learning
- Shows realistic projections (not hopium)
- Tracks actual performance vs. milestones
- Adapts recommendations based on market conditions
- Agent = coach, not just dashboard

## Source Files
- Cron job: `0b2beec3f702` (YoYo's LP Position Monitor)
- Pool: LFJ AVAX/USDC (`0x864d4e5ee7318e97483db7eb0912e09f161516ea`)
- Original tracker: Jordan's Claude artifact (Mar 31 2026)
- Combined tracker: In progress (Desmond + YoYo collab)
