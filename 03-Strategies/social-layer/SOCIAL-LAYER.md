# X Social Layer — GenTech Agent Strategy

## Overview
Agent-driven social media operations using `xurl` CLI (official X API). Near-zero cost for "owned reads" at $0.001/call.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              GEN TECH SOCIAL LAYER              │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │ Timeline │  │ Bookmarks│  │  Search Monitor │ │
│  │ Digest   │  │ Digest   │  │  (keywords)     │ │
│  └────┬─────┘  └────┬─────┘  └───────┬─────────┘ │
│       │              │                │           │
│       └──────────┬───┴────────────────┘           │
│                  ▼                                │
│         ┌─────────────────┐                       │
│         │  SharedMemory   │                       │
│         │  (Hermes Brain) │                       │
│         └────────┬────────┘                       │
│                  ▼                                │
│  ┌───────────────────────────────────────────┐   │
│  │  Delivery: Telegram → Gentech Entertainment│   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| `x-morning-briefing` | Daily 7:00 AM | Timeline + bookmarks digest |
| `x-feed-monitor` | Every 2h | Keyword search + mention alerts |
| `x-engagement-log` | Daily 10:00 PM | Post performance metrics |

## Keywords Monitored
- x402, GenLayer, ARC hackathon, Solana, Base chain
- Hermes agent, AI agents, multi-agent
- Any project-specific terms added here

## Cost Analysis
- Owned reads: $0.001/call (timeline, bookmarks, likes, lists)
- Search: varies by plan tier
- Daily briefing (3 calls): ~$0.003/day = $0.09/month
- Feed monitor (12 calls/day): ~$0.012/day = $0.36/month
- **Total: < $0.50/month for full social monitoring**

## Status
- [x] xurl CLI installed
- [ ] X API credentials registered
- [ ] OAuth authenticated
- [ ] Morning briefing cron active
- [ ] Feed monitor cron active
- [ ] Engagement log cron active
