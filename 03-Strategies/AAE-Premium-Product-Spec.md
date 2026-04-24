# AAE Premium — "Autopilot" Product Spec

**Owner:** YoYo (Strategies)
**Status:** Active — Product Definition Phase
**Date:** Apr 18, 2026
**Companion:** `04-Entertainment/handoffs/aae-premium-autopilot.md` (marketing copy for Desmond)

---

## Product Vision

> "Feed it a token address and bam."

One input. Full intelligence. Autopilot execution.

**The core problem:** Gamma/Arrakis auto pools optimize for TVL, not returns. They rebalance mechanically. They don't see what's happening in the real world. Jordan proved this by outperforming auto pools manually — working with the agent for 12 hours beats passive pools.

**The solution:** An agent that watches everything — sentiment, tokenomics, pool health, macro — and executes LP strategies intelligently.

---

## Feature Layers

### Layer 1: Fee Engine (Default)
- Auto-rebalance LP positions to stay in range and maximize fee capture
- Continuous range optimization based on volatility and volume
- No manual babysitting — the agent handles it

### Layer 2: Community Intelligence Tracker
- Scrape X + Discord for ticker-specific signals
- Weekly community health score (1-100)
- Signals: post velocity, sentiment polarity, dev activity, member growth, FUD spikes
- **Feeds into Autopilot:** "community sentiment dropped 40% → tighten range or exit"

### Layer 3: Tokenomics Radar
- Supply analysis (inflation, emissions, burn mechanics)
- Holder concentration (top 20 wallets, insider %)
- Unlock schedule (cliffs in next 90 days)
- Whale movement tracking (accumulation vs distribution)
- **Pool health exit trigger:** fundamentals deteriorating → agent exits

### Layer 4: Macro Watch
- Truth Social / X policy signals (tariffs, regulations)
- Fed statements / FOMC calendar
- Geopolitical risk (wars, sanctions, Hormuz)
- ETF flow data (institutional direction)
- Liquidation cascade detection

### Layer 5: Swappable Intelligence (Modular Agent Teams)
**Core concept:** Users build their dream team — not "use an agent," but compose one.
- **Brain (the thinker):** Swap underlying models per task — MiMo for research, Claude for coding, GPT-4o for speed, local models for cost efficiency
- **Personality (the voice):** How the agent communicates — aggressive trader, conservative yield farmer, degen sniper, cautious analyst
- **Strategy (the playbook):** Combine layers like a character build — mix and match intelligence + personality + risk profile
- **Composability:** Users share top-performing configurations; leaderboard ranks the best combos
- **Clones are fully editable:** When a user clones a top build from the leaderboard, every single layer remains unlocked and adjustable. No locks, no restrictions. Clone it, then tweak the brain, swap the personality, tighten the enforcement — make it yours.
- **Fork culture:** Users iterate on each other's builds, creating a living meta. "Forked from @user's Sharpe King v2 → swapped brain to MiMo, tightened stops to 3%."

**Why it's a moat:** Anyone can swap models. Not everyone builds the orchestration that makes swapping models *safe and effective*.

### Layer 6: Enforcement Layer (Risk Guardrails)
**Core concept:** What the agent is actually allowed to do — separate from brain and personality.
- **Hard limits (non-bypassable):** Max position size as % of portfolio, stop-loss thresholds, daily loss caps, max leverage
- **Soft preferences (advisory):** Target asset classes, preferred DEXes, minimum yield thresholds — agent can suggest deviations but needs explicit approval
- **User presets:** "Beginner" (tight limits), "Experienced" (moderate), "Pro" (wider but still capped), plus Gentech recommended defaults based on proven strategies
- **Education integration:** Ship our own guidelines derived from our educational content — enforcement as a teaching tool, not just a constraint
- **Leaderboard integration:** Risk-adjusted rankings (Sharpe ratio, consistency, drawdown survival) — not just raw ROI
- **Thesis breakers:** Specific events that trigger mandatory review or auto-exit (unlock cliffs, FOMC surprises, protocol exploits)

**The moat:** The enforcement layer is what makes the swappable intelligence layer *safe to use*. It's the seatbelt that lets people drive fast.

---

## The "One Address" UX Flow

```
User inputs: 0xABC...

Agent runs:
  ├─ Layer 1: Fee Engine → LP position analysis
  ├─ Layer 2: Community sentiment → X/Discord health
  ├─ Layer 3: Tokenomics scan → supply, emissions, vesting, holder concentration
  ├─ Layer 4: Macro context → current risk environment
  ├─ Layer 5: Intelligence config → user's brain + personality + strategy combo
  └─ Layer 6: Enforcement check → risk limits, thesis breakers, guardrails

If user proceeds:
  ├─ Default: autopilot fee-efficient rebalancing
  ├─ Timing: optimize for high-volume windows
  └─ Exit: pool health degrades → auto-exit or user alert
```

---

## Smart Timing — When to Rebalance

**Key insight:** Asia overnight markets don't move much. Most volume = US + EU hours.

| Period | Strategy |
|---|---|
| US/EU market hours | Active rebalancing, tighter ranges, capture fees |
| Friday evening | Pre-weekend check → tighten or reduce exposure |
| Saturday | Chill mode, wider ranges, lower activity |
| Sunday | ⚠️ Defensive — wider range, reduce exposure |
| Sunday night | If sentiment spikes → pre-emptive adjustment before Monday |
| Asia overnight | Sit tight, low volatility, safe to hold |

**The Sunday Pattern (Jordan's observation):**
- Low liquidity, thin order books → moves amplify
- News gets priced in hard (geopolitical, Trump posts)
- Monday gap risk → asymmetric downside
- Pre-emptive positioning Sunday evening = edge

---

## Pool Health — Exit Triggers

Agent exits when:
- Tokenomics deteriorating (inflation spikes, emissions changes)
- Holder concentration spiking (one wallet accumulating)
- Community sentiment cratering (FUD, dev silence)
- Unlock cliff approaching (scheduled dump)
- Macro event risk (tariffs, geopolitical escalation)
- Volume drying up (pool becoming illiquid)

---

## Competitive Moat

| Feature | Gamma | Arrakis | AAE Premium |
|---|---|---|---|
| Auto-rebalance | ✅ | ✅ | ✅ |
| Fee optimization | Basic | Basic | Advanced |
| Sentiment signals | ❌ | ❌ | ✅ |
| Tokenomics analysis | ❌ | ❌ | ✅ |
| Macro awareness | ❌ | ❌ | ✅ |
| Timing optimization | ❌ | ❌ | ✅ |
| Pool health exits | ❌ | ❌ | ✅ |
| One-address onboarding | ❌ | ❌ | ✅ |
| Swappable intelligence | ❌ | ❌ | ✅ |
| Risk enforcement layer | ❌ | ❌ | ✅ |
| Community leaderboards | ❌ | ❌ | ✅ |

**The pitch:** "They see price. We see *why* price might move. And we make sure you survive to trade tomorrow."

---

## Origin Story

Jordan built this to solve his own problem:

> "I work too much to keep up with everything."

The journey:
1. Saw OpenClaw wrappers being built, watched what others made
2. Tried a wrapper, gave it something simple
3. "It was history after that"
4. Full autonomous agent stack — sentiment, tokenomics, pool health, market timing

**Validation:**
> "Of course I'll be subscribing to my own service."

He's not selling a product he doesn't use. Features came from real problems, not brainstorming.

---

## Data Sources

| Signal | Source | Cost |
|---|---|---|
| X sentiment | `xitter` skill + NLP | Free (existing) |
| Discord activity | Bot in server or public scrape | Free/Medium |
| Holder concentration | Snowtrace/Etherscan API | Free |
| Tokenomics | CoinGecko/Messari API | Free tier |
| Unlock schedules | TokenUnlocks.app | Free tier |
| Whale movements | Arkham/Nansen or direct RPC | Paid |
| Macro signals | Truth Social scraper + news API | Free/Medium |
| Pool health | On-chain RPC queries | Free |
| ETF flows | CoinShares reports | Free |

---

## Pricing Tier Spec (for Desmond to flesh out)

### Free Tier
- Basic auto-rebalance (mechanical, like Gamma)
- Pool health monitoring (limited)
- Weekly summary
- 1 brain model, 1 personality preset
- Basic enforcement (hard limits only)

### Premium Tier ($X/month)
- Full 6-layer intelligence stack
- Community sentiment tracking
- Tokenomics radar with alerts
- Macro watch with timing optimization
- One-address full scan
- Smart rebalancing (timing-aware)
- Auto-exit on pool health degradation
- Swappable brains + personalities + strategy combos
- Full enforcement layer with soft preferences
- Leaderboard access + config sharing

### Pro Tier (future)
- Custom enforcement rules
- Whale movement tracking (Arkham/Nansen)
- Multi-pool portfolio management
- API access for custom integrations

---

## References

- LFJ AVAX/USDC V2.2 pool, binStep 10bps, range 9.66-9.95
- BullTheory frameworks (M2, ISM, inflation correlation)
- OpenClaw wrapper origin → full agent evolution
