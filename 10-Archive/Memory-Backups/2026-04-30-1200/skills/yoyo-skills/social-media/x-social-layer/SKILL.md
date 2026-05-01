---
name: x-social-layer
description: Agent-driven X/Twitter social media operations using xurl CLI. Daily briefings, keyword monitoring, engagement tracking.
version: 1.0.0
author: GenTech
---

# X Social Layer

Agent-driven social media monitoring and engagement via `xurl` CLI.

## Prerequisites
- `xurl` installed and authenticated (`xurl auth status` confirms)
- X API app registered with OAuth 2.0

## Scripts

### Morning Briefing (`morning-briefing.py`)
Pulls timeline (20 posts), bookmarks (10), mentions (10). Outputs JSON for agent summarization.

### Feed Monitor (`feed-monitor.py`)
Searches keywords, tracks seen post IDs in `~/.hermes/data/x-seen-posts.json` to avoid duplicates. Silent when no new matches.

## Cron Jobs

| Job | ID | Schedule |
|-----|-----|----------|
| x-morning-briefing | `2cb3aea47618` | Daily 7:00 AM UTC |
| x-feed-monitor | `355cb2d587d1` | Every 2h |

## Keywords (edit in feed-monitor.py)
x402, GenLayer, ARC hackathon, AI agents, multi-agent, Hermes agent, Solana hackathon, Base chain, HTTP 402

## Cost
~$0.50/month for full monitoring (owned reads at $0.001/call)

## Location
Scripts: `/root/vaults/gentech/03-Strategies/social-layer/`
Strategy: `/root/vaults/gentech/03-Strategies/social-layer/SOCIAL-LAYER.md`
