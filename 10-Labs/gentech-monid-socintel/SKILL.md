# Monid Social Intel — AAE Narrative Rotation Monitor

> Track how the AAE narrative is trending across platforms.
> Know when to push content, when to pivot, and what's working.

## What

Monid (Moment + Onid = Moment ID) is a lightweight social intelligence tool for monitoring the AAE (Agentic Artificial Economy) narrative across X, Reddit, Farcaster, and Lens. It tracks sentiment, mention velocity, and engagement to tell you when to publish, what angle to take, and which platforms are hot.

## Monitoring Framework

### Core Metrics

| Metric | What It Measures | Action Signal |
|--------|-----------------|---------------|
| **Mention Velocity** | Mentions/day of AAE keywords | ↑ spike = publish now |
| **Sentiment Ratio** | Positive:Negative mentions | < 2:1 = needs defense |
| **Narrative Drift** | What topics co-occur with AAE | New co-occurence = trend |
| **Platform Share** | % of conversation per platform | Shift = post there |
| **Influencer Lift** | Mentions by accounts with 1K+ followers | ↑ = amplification opportunity |
| **Cross-Pollination** | Same idea appearing on 2+ platforms | = narrative is sticky |

### Keywords to Track

```
Primary:   AAE, Agentic Artificial Economy, agent economy
Secondary: x402, Q402, agent payments, agent commerce, agent DeFi
Context:   CLARITY Act, ERC-8004, pay-per-call, AI agent payments
Brand:     GenTech, GenTech Labs, Gentech Agency
Competition: t54, BNB Agent SDK, ai16z, Virtuals
```

## Quick Start

### 1. Run a narrative scan

```bash
python scripts/monitor.py --scan
```

Sample output:
```
┌─ AAE Narrative Scan ──────────────────────────────────┐
  Period:    2026-07-22 → 2026-07-24
  Mentions:  47 total
  Platforms: X (24), Farcaster (12), Reddit (8), Lens (3)
  Sentiment: 3.2:1 positive
  Velocity:  +23% vs last period
  Top topic: x402 compliance (+12 mentions)
  Signal:    🔴 Publish window — x402 narrative gaining
```

### 2. Get a narrative report

```bash
python scripts/monitor.py --report weekly
```

### 3. Watch mode (continuous)

```bash
python scripts/monitor.py --watch --interval 3600
```

## Narrative Rotation Strategy

### When to Publish

| Signal | Action | Timing |
|--------|--------|--------|
| Mention velocity up 50%+ | Publish technical content | Within 4 hours |
| New co-occurence detected | Write the "X + AAE" post | Same day |
| Sentiment dips below 2:1 | Publish defense/milestone post | Within 8 hours |
| Platform share shifts | Post on the rising platform | Within 2 hours |

### Content Types by Signal

| Signal | Content Type | Example |
|--------|-------------|---------|
| Positive sentiment spike | Technical deep-dive | "How x402 enables agent commerce" |
| Negative sentiment | Milestone/defense | "GenTech's CLARITY Act compliance layer" |
| New trend detection | Hot take / first post | "AAE meets X — what this means" |
| Slow period (velocity low) | Educational series | "AAE explained in 3 posts" |

### Rotation Cadence

```
Monday:    Technical (specs, architecture, code)
Tuesday:   Ecosystem (partnerships, integrations)
Wednesday: Market (pricing, adoption, metrics)
Thursday:  Vision (long-term, philosophy, predictions)
Friday:    Community (builds, wins, memes, culture)
```

## Integration

### Manual Run (no API keys needed)

The script runs in demo mode with sample data to demonstrate the framework.

### Production (requires API keys)

| Source | Key Needed | Config |
|--------|-----------|--------|
| X (Twitter) API | Bearer token | `X_BEARER_TOKEN` |
| Reddit API | Client ID + Secret | `REDDIT_CLIENT_ID` |
| Farcaster | Hub URL | `FARCASTER_HUB` |
| Lens API | Public (no key) | Lens API endpoint |

## Files

```
10-Labs/gentech-monid-socintel/
├── SKILL.md              # This file
└── scripts/
    └── monitor.py        # Narrative scan & report
```
