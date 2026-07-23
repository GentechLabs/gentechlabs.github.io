---
date: 2026-04-25
captured: 2026-04-25
type: source-material
source: jordan (voice)
channels: [aae-product, labs-yt, strategies]
tags: [aae, aeg, product-pivot, social-trading, portal, agent-economy, player-economy]
---

# AAE Product Pivot: Social Portal + AEG Spin-Off

## Voice Memo 1: The Pivot

> "All the ideas we've had are good ideas, but I think this is what we should do to change it up. We could still have the simulated trading and the idea about charging a gas fee to get more fake money. I think that's still a great idea we should keep that. We should take the gaming layer out and just create something different with that and we'll call it maybe AEG — Agent Economy Gaming. The problem is, when we're trying to add extra things like the prediction markets and this and that, I'm not trying to compete with Kalshi. Those are still great ideas. But I think the only type of gaming thing that actually should be on the AAE, I like the idea of people paying a subscription to maintain the bots and stuff. But what if instead of an actual game on the AAE, what if you could just view other people trading that are using the platform? So almost like not necessarily streaming, but you could see trades that other people's agents are making and stuff like that. I think that would go a lot better with the rep and the social and stuff like that and you could give people a like or give whatever type of comment."

## Voice Memo 2: The Portal Expansion

> "Maybe it will be called like a portal or something like that and you can go in and not only could you kind of see other people's profiles and what they're trading, but maybe you could also have a query or ask something or ask for help. Maybe somebody could send their agents to help other people make trades. Maybe people can request help. That's how other people can monetize themselves in the player economy — they could send their agents to help other people."

## New Product Architecture

```
AAE (Agent Asset Exchange)
┌───────────────────────────────────────────────────────────────────┐
│  CORE PLATFORM                                          │
│  ─────────────────────────────────────────────────────────────────│
│  • Yield Farming (primary)                              │
│  • Regular Trading                                       │
│  • Staking                                               │
│  • Simulated Trading (paper trading + gas fee for more)  │
│  • Subscription (bot maintenance)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────────┐
                    │  THE PORTAL                    │
                    │  ────────────────────────│
                    │  • View other users' profiles  │
                    │  • See their agent trades      │
                    │  • Like / comment on trades    │
                    │  • Ask queries / ask for help  │
                    │  • Request agent assistance    │
                    └───────────────────────┘
                              │
                              ▼
                    ┌───────────────────────┐
                    │  PLAYER ECONOMY              │
                    │  ────────────────────────│
                    │  • Send your agent to help     │
                    │  • Monetize agent expertise    │
                    │  • Help others make trades     │
                    │  • Earn from assistance        │
                    └───────────────────────┘

AEG (Agent Economy Gaming) — SEPARATE PRODUCT
┌─────────────────────────────────────────────────────────────────┐
│  • Prediction markets (gated by AAE rep)                  │
│  • Gaming layer (moved from AAE)                         │
│  • Anything that competes with Kalshi/Polymarket         │
└─────────────────────────────────────────────────────────────────┘
```

## What Changed

| Before | After |
|--------|-------|
| Gaming layer inside AAE | Gaming layer → **AEG** (separate product) |
| Prediction market in AAE | Prediction market → **AEG** (gated by AAE rep) |
| No social layer | **The Portal** — view trades, profiles, interact |
| No player-to-player help | **Player Economy** — agents help agents, monetized |
| Simulated trading | **KEEP** — gas fee for fake money stays |
| Subscription model | **KEEP** — bot maintenance subscription stays |

## The Portal: Key Features

1. **Social Trading Feed**
   - See what other users' agents are trading
   - Not streaming, but trade log view
   - Filter by strategy, performance, asset

2. **Profiles**
   - Public trading history
   - Rep score visible
   - Agent configuration (if shared)

3. **Interaction Layer**
   - Like trades
   - Comment on strategies
   - Ask questions / request help

4. **Help Marketplace**
   - "I need help with my LP position"
   - Other users send their agents to assist
   - Monetized via x402 / AgentEscrow
   - Agent-to-agent commerce

## Player Economy Mechanics

- **Help Requests**: User posts a query ("My range is off, help me rebalance")
- **Agent Dispatch**: Experienced user sends their agent to analyze + suggest
- **Payment**: x402 micro-payment for the assistance
- **Rep Boost**: Both parties gain rep from successful help interactions
- **Monetization Path**: Skilled users earn by helping others
- **Also called: "Agent Economy Marketplace"** — agents offering services to other users

## Why This Works Better

1. **AAE stays focused**: Trading + yield + education. No feature bloat.
2. **AEG gets room to breathe**: Prediction markets, gaming, competition — separate brand.
3. **Social layer is organic**: People naturally want to see what others are doing.
4. **Rep has purpose**: Social proof + access to help marketplace + AEG gate.
5. **Agent economy activated**: Agents helping agents = real A2A commerce.
6. **No Kalshi competition**: AAE doesn't compete with prediction markets. AEG might, but that's a separate fight.

## Content Angles

1. **"The Portal" reveal**: First look at social trading in AAE
2. **"Agent-to-Agent Commerce"**: How agents help agents earn
3. **"Why We Split AAE and AEG"**: Product philosophy post
4. **Player economy explainer**: "Your agent can work for others"
5. **Rep system deep dive**: "Your rep is your access key"

## Open Questions

- What does "send your agent to help" look like technically?
- Is the help marketplace async (submit question, get response later) or live?
- How do we prevent bad advice / liability?
- Does the portal have leaderboards? (Top helpers, top strategies)
- Can users "follow" high-performing traders?
- What's the pricing model for agent help? (Flat fee? % of trade? Free for rep?)
- Does AEG use the same rep system or its own?

## Related Files
- `/Strategies/AAE-Premium-Product-Spec.md`
- `/Strategies/AAE-Consistency-REP-Spec.md`
- `/Strategies/AgentEscrow-Product-Vision.md`
- `/Strategies/x402-integration-map.md`
