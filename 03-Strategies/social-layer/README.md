# Social Layer POC — Gentech x X API

## Status: ⏳ Awaiting Auth Setup

### What This Is
Proof of concept for agent-driven social media intelligence and engagement via `xurl` (official X API CLI).

## Architecture

```
┌─────────────────────────────────────────────────┐
│              SOCIAL LAYER                       │
├────────────────┬────────────────┬───────────────┤
│   LISTEN       │   ANALYZE      │   ENGAGE      │
│                │                │               │
│ • Timeline     │ • Trend score  │ • Like        │
│ • Mentions     │ • Sentiment    │ • Reply       │
│ • Search       │ • Influencer   │ • Quote       │
│ • Bookmarks    │   mapping      │ • Follow      │
│ • Lists        │ • Signal       │ • Repost      │
│                │   extraction   │               │
└────────────────┴────────────────┴───────────────┘
```

## Cost Model (Post-Price Drop)
| Action | Before | Now | Daily (est.) |
|--------|--------|-----|-------------|
| Timeline pull (100 posts) | $0.50 | $0.001 | $0.003 |
| Search 5 queries | $2.50 | $0.005 | $0.015 |
| Mentions check (50) | $0.25 | $0.001 | $0.003 |
| **Full daily monitoring** | **$3.25** | **$0.019** | **~$0.60/mo** |

## Setup Steps
1. Jordan: Create X Developer app at https://developer.x.com
2. Jordan: Set redirect URI to `http://localhost:8080/callback`
3. Jordan: Run `xurl auth apps add gentech --client-id ID --client-secret SECRET`
4. Jordan: Run `xurl auth oauth2` (opens browser for OAuth)
5. YoYo: Verify with `xurl whoami`
6. YoYo: Activate cron jobs

## Cron Jobs (Ready to Activate)
- `social-briefing` — Daily morning timeline + mention digest
- `social-monitor` — Hourly search for crypto/hackathon signals
- `social-engagement` — Engagement scoring and recommendations
