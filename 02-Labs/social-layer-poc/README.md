# Social Layer POC — GenTech x X API

## Overview
Agent-driven social media pipeline using xurl (official X API CLI).
Leverages the new $0.001/call owned-read pricing for near-free monitoring.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Cron Jobs  │────▶│  xurl CLI    │────▶│  Vault (Obsidian)│
│  (Hermes)   │     │  (X API)     │     │  02-Labs/social  │
└─────────────┘     └──────────────┘     └─────────────────┘
       │                                        │
       ▼                                        ▼
┌─────────────┐                         ┌─────────────────┐
│  Alerts     │                         │  Agent Analysis  │
│  (Telegram) │                         │  (DMOB/YoYo)     │
└─────────────┘                         └─────────────────┘
```

## Modules

### 1. Feed Monitor (`feed-monitor.sh`)
- Pulls home timeline + mentions every 2h
- Deduplicates against last run
- Saves to `02-Labs/social-layer-poc/feed/`
- Cost: ~$0.001 per pull = $0.012/day

### 2. Security Radar (`security-radar.sh`)
- Searches for keywords: "exploit", "vulnerability", "rug pull", "hack"
- Monitors known security researcher accounts
- Alerts to Telegram on matches
- Cost: ~$0.002/day

### 3. Crypto Intel (`crypto-intel.sh`)
- Tracks DeFi protocol announcements
- Monitors hackathon accounts
- Sentiment snapshots for watched tokens
- Cost: ~$0.003/day

## Setup

### Prerequisites
1. X API developer account: https://developer.x.com/en/portal/dashboard
2. App with OAuth 2.0 PKCE (redirect URI: `http://localhost:8080/callback`)
3. Required scopes: tweet.read, users.read, follows.read, bookmark.read, like.read

### Auth (user runs manually — never in agent session)
```bash
xurl auth apps add gentech --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
xurl auth oauth2
xurl whoami  # verify
```

## Cost Analysis
| Module | Calls/day | Cost/day | Cost/month |
|--------|-----------|----------|------------|
| Feed Monitor | 12 | $0.012 | $0.36 |
| Security Radar | 8 | $0.008 | $0.24 |
| Crypto Intel | 10 | $0.010 | $0.30 |
| **Total** | **30** | **$0.03** | **$0.90** |

Old pricing equivalent: **$15.00/day → $0.03/day** (500x savings)
