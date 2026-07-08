# Fee Tracker — Game Model Spec v2

> Status: Draft — Jordan pivot approval
> Date: 2026-04-25
> Scope: Gamified fee tracker + agent-driven market intelligence
> Key Change: Removed simulated trading. Added subscription gating + agent news monitoring.

---

## Philosophy

**"More winners than losers"**

The Fee Tracker is a **progression game disguised as a DeFi tool**. Users don't "trade" — they deploy capital, unlock tiers, and watch their agent make decisions based on real market intelligence. The goal is learning + disciplined accumulation, not casino speculation.

---

## Game Loop

```
1. SUBSCRIBE → One agent assigned per user
2. DEPLOY → Lock capital in LP position
3. EARN → Fees accrue in real-time
4. MONITOR → Agent watches news, scores sentiment
5. DECIDE → Agent suggests DCA action (buy/hold/skip)
6. ACT → User approves or overrides
7. PROGRESS → Hit fee targets → unlock ranks, shapes, multi-pool
8. COMPOUND → Reinvest → larger position → faster progression
```

**Constraint: 1 agent per user.** Your agent is yours alone — it learns your preferences, tracks your positions, and makes recommendations tailored to your setup. No shared agents, no agent marketplaces (for now).

---

## Tier System (Game Ranks)

| Tier | Rank | Daily Fee Target | Unlock | Visual Badge |
|------|------|-----------------|--------|--------------|
| 1 | **Scout** | $5/day | Basic LP, CURVE shape | 🦔 Bronze |
| 2 | **Raider** | $20/day | SPOT + BIDIRECTIONAL shapes | 🥈 Silver |
| 3 | **Warlord** | $55/day | Multi-pool positions | 🥇 Gold |
| 4 | **Sovereign** | $200/day | Custom agent strategies | 💎 Platinum |
| 5 | **Oracle** | $500/day | AI news prediction + auto-execution | 🌟 Legendary |

**Progression formula:**
```
progress_pct = ((current_daily_fees - current_tier_target) / (next_tier_target - current_tier_target)) * 100
```

**Tier-ups trigger:**
- Badge animation
- New shape/strategy unlocked
- Agent announcement in Telegram
- Optional: small $TECH reward (if tokenomics allows)

---

## Free vs Subscription

### Free Tier
| Feature | Limit |
|---------|-------|
| Positions | 1 active LP |
| Fee presets | 2 (Micro $100, Starter $500) |
| Static DCA | Weekly only |
| Agent news monitoring | ❌ Disabled |
| Custom strategies | ❌ Disabled |
| Alerts | Basic (out of range only) |

### Subscription Tier ($X/month — TBD)

**What you're paying for: your dedicated agent.**

One agent per subscriber. It runs 24/7 monitoring markets, scoring news, and waiting to advise you. No shared instances, no multi-tenancy.

| Feature | Access |
|---------|--------|
| Positions | Unlimited |
| Fee presets | All 5 (+ custom) |
| Static DCA | Weekly, Monthly, Yearly |
| **Dedicated agent** | ✅ Your personal market intelligence agent |
| **Custom strategies** | ✅ Write your own triggers |
| Alerts | All strategies + tier pushes + compound ready |
| Priority support | Direct agent tuning |

**Subscription value prop:** "Hire your own DeFi agent — it never sleeps, never misses news, never panics."

**Subscription value prop:** "Unlock the full agent + keep the bots running"

---

## Agent News Monitoring (Subscription Feature)

### What the Agent Does
1. **Scans** — Monitors news sources every 15 minutes during market hours
2. **Scores** — Assigns sentiment (-1.0 to +1.0) to each story
3. **Correlates** — Maps sentiment to user's held assets (AVAX, BTC, etc.)
4. **Decides** — Generates DCA recommendation:
   - **BUY** — Negative sentiment + price dip = accumulation opportunity
   - **HOLD** — Neutral / conflicting signals
   - **SKIP** — High volatility / uncertain — wait for clarity
5. **Notifies** — Sends structured alert to user with reasoning

### News Sources (v1)
| Priority | Source | Type | Free/Sub |
|----------|--------|------|----------|
| 1 | CoinDesk / TheBlock RSS | Crypto news | Free |
| 2 | X/Twitter (key accounts) | Sentiment | Subscription |
| 3 | On-chain signals | Whale moves, exchange flows | Subscription |
| 4 | Macro calendar | Fed decisions, earnings | Subscription |

**Note on X/Twitter:** v1 uses RSS/blog sources. X API integration is Phase 2 (cost/complexity). When ready, the agent can monitor specific accounts (e.g., @realDonaldTrump) for market-moving posts.

### Agent Decision Example

```
🤖 AGENT ALERT — DCA Decision

Asset: AVAX
Price: $9.42 (-3.2% 24h)

News Scan:
• 🔴 "SEC delays AVAX ETF decision" — CoinDesk (sentiment: -0.6)
• 🔴 "Avalanche Foundation announces $100M gaming fund" — TheBlock (sentiment: +0.4)
• 🟡 "BTC correlation: AVAX tracking broader market down" — On-chain (sentiment: -0.2)

Net Sentiment: -0.15 (slightly bearish)

📊 Agent Recommendation: BUY
Reason: Short-term regulatory FUD vs. long-term ecosystem growth. 
Price dip (-3.2%) within DCA range. Discipline suggests accumulate.

Action: Deploy $50 USDC → AVAX
[Approve] [Skip This Round] [Adjust Amount]
```

### User Override
- User can set **auto-approve** threshold (e.g., "auto-execute if sentiment < -0.3")
- Default: **always ask** (notification + one-tap approve)
- Override history logged for agent learning

---

## 5 Fee Earning Presets (Subscription)

Presets are **scenario planners** — "what if I had X capital in this pool?"

| Preset | Position | Pool | Example Daily | Tier |
|--------|----------|------|---------------|------|
| Micro | $100 | LFJ 5bps | ~$0.08/day | — |
| Starter | $500 | LFJ 5bps | ~$0.42/day | Scout |
| Growth | $2,500 | LFJ 20bps | ~$2.14/day | Scout → Raider |
| Pro | $10,000 | Multi-pool | ~$10/day | Raider → Warlord |
| Sovereign | $50,000 | Custom | ~$55/day | Warlord → Sovereign |

**Free users see:** Micro + Starter only (grayed out: "Subscribe to unlock projections")
**Subscribers see:** All 5 + custom position size input

---

## 3 Default Strategies (Queue)

All users get **Fee Floor Guardian** (basic). Subscribers get all 3.

| # | Strategy | Free | Sub | Trigger |
|---|----------|------|-----|---------|
| 1 | **Fee Floor Guardian** | ✅ | ✅ | Daily fees < minimum |
| 2 | **Tier Push Alert** | ❌ | ✅ | 80% to next tier |
| 3 | **Auto-Compound** | ❌ | ✅ | Cumulative fees ≥ $50 |

---

## DCA Modes

### 1. Static Schedule (Free — Weekly only)
- Every Monday, fixed amount ($50 default)
- No intelligence — purely disciplined accumulation

### 2. Agent-Assisted (Subscription)
- Agent monitors news + sentiment
- Suggests optimal DCA timing
- User approves each action

### 3. Custom Rules (Subscription)
- User writes simple rules:
  - "Double DCA if AVAX drops 5%"
  - "Skip if gas > 50 gwei"
  - "Increase amount if sentiment < -0.5"
- Rules validated before execution
- Phase 2: Natural language rule builder

---

## Reward Mechanics (REP System)

Users earn **REP** (reputation) for disciplined behavior:

| Action | REP Reward |
|--------|-----------|
| Complete DCA on schedule | +10 REP |
| Approve agent recommendation | +5 REP |
| Compound fees | +15 REP |
| Tier promotion | +50 REP |
| Maintain position 30 days without panic exit | +25 REP |
| Skip DCA due to agent warning (saved loss) | +20 REP |

**REP unlocks:**
- Leaderboard ranking (opt-in)
- Custom agent personalities
- Early access to new strategies
- NOT convertible to $TECH (avoid ponzinomics)

---

## UI Flow (MVP)

### Dashboard
```
┌─────────────────🏆 FEE TRACKER ─────────────────┐
│                                           │
│  🦔 SCOUT ───────────────── 43% │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│  $0.42/day → $5/day (Raider)            │
│                                           │
│  💰 Position: $500 LFJ AVAX/USDC         │
│  📈 Daily Fees: $0.42  |  APR: 31.2%      │
│  ⏰ Next DCA: Monday ($50) — Auto          │
│                                           │
│  [🔍 AGENT MONITORING — 3 alerts today]  │
│  • AVAX: SEC ETF delay (-0.6) → BUY rec  │
│  • BTC: ETF inflows positive (+0.4)      │
│                                           │
│  [View Agent Feed] [Approve DCA]          │
└─────────────────────────────────────────┘
```

### Agent Feed
```
┌────────🤖 AGENT MARKET INTELLIGENCE ─────────┐
│                                             │
│  Today — 2:34 PM                            │
│  🔴 AVAX: SEC delays ETF (-0.6)            │
│     → Price dipped 3.2% → BUY signal      │
│     [Approve $50 DCA] [Skip] [Why?]        │
│                                             │
│  Today — 11:15 AM                          │
│  🟡 BTC: Neutral macro — HOLD              │
│     No action recommended                   │
│                                             │
│  Yesterday — 4:20 PM                       │
│  🟢 LINK: Partnership news (+0.7)         │
│     → Not in your LP — info only           │
│                                             │
└─────────────────────────────────────────┘
```

---

## Technical Architecture

### Components
```
┌────────────────────────────────────────┐
│  PER-USER AGENT INSTANCE (1 per subscriber) │
│  • Isolated state (prefs, positions, history)   │
│  • Dedicated news scanning loop                  │
│  • Personal sentiment thresholds                 │
│  ↓                                              │
│  NEWS AGGREGATOR (per-agent)                   │
│  • RSS polling (CoinDesk, TheBlock)           │
│  • X scraping (Phase 2)                       │
│  • On-chain alerts (whale moves)              │
│  ↓                                              │
│  SENTIMENT ENGINE (per-agent)                  │
│  • Per-article score (-1.0 to +1.0)           │
│  • Asset tag extraction (AVAX, BTC, etc.)     │
│  • Time-decay weighting (newer = heavier)     │
│  ↓                                              │
│  DECISION ENGINE (per-agent)                   │
│  • User position + preferences                │
│  • Rule evaluation (custom strategies)        │
│  • Generate BUY/HOLD/SKIP + reasoning         │
│  ↓                                              │
│  NOTIFICATION ROUTER                           │
│  • Telegram bot (primary)                     │
│  • In-app notification (batched)              │
│  • Email digest (daily summary)               │
└────────────────────────────────────────┘
```

**Architecture implication:** Each subscriber gets their own agent process/container. No shared memory between users. Scale = N agents for N subscribers.

### Cron Jobs Needed
| Job | Frequency | Subscription | Description |
|-----|-----------|--------------|-------------|
| News scan | Every 15 min (market hours) | Sub only | Poll RSS, score sentiment |
| DCA scheduler | Daily (configurable) | All | Check if today is DCA day |
| LP monitor | Every 4 hours | All | Position health, fee accrual |
| Tier check | Hourly | All | Check for tier promotions |
| Daily digest | 8 PM ET | Sub only | Summarize agent decisions |

---

## Phase Plan

### Phase 1 — MVP (Free + Basic Sub)
- [ ] 2 free presets (Micro, Starter)
- [ ] Weekly static DCA
- [ ] Basic LP monitoring (existing)
- [ ] Tier system + REP
- [ ] 1 strategy: Fee Floor Guardian

### Phase 2 — Agent Intelligence (Sub unlock)
- [ ] RSS news aggregation
- [ ] Sentiment scoring
- [ ] Agent BUY/HOLD/SKIP recommendations
- [ ] 5 full presets
- [ ] 3 strategy queue
- [ ] Monthly/yearly DCA

### Phase 3 — Advanced (Sub)
- [ ] X/Twitter integration
- [ ] On-chain signals
- [ ] Custom strategy builder
- [ ] Auto-execution (user pre-approved)
- [ ] Multi-pool positions

---

## Business Model

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free** | $0 | Try the game, one position, basic monitoring. No agent. |
| **Agent** | ~$15–30/month | **Your own dedicated agent.** Unlimited positions, full intelligence, all strategies. |

**Why charge per agent?**
- Each user gets a **dedicated agent instance** — not shared, not pooled
- Agent runs continuous news monitoring, sentiment scoring, and decision logic
- Compute + API costs are per-agent
- Higher price = higher perceived value ("I have my own agent")

**Revenue use (transparency):**
- 40% — API costs (data feeds, RPC)
- 30% — Agent infrastructure (dedicated compute per user)
- 20% — Development
- 10% — Treasury/insurance

### Why Not Multi-Agent Per User?

**For v1: hard limit at 1 agent per user.**

- Simplifies architecture (no agent orchestration layer needed)
- Clear value prop: "your agent" not "your fleet"
- Prevents complexity creep (users managing 5 agents with conflicting signals)
- Future: "Agent upgrades" instead of "more agents" (faster scanning, more sources, auto-execution)

---

## Open Questions

1. **Subscription price point?** $15? $30? Annual discount?
2. **REP → anything?** Or purely cosmetic/leaderboard? (I recommend cosmetic only)
3. **Agent wrong → who pays?** If agent says BUY and price drops — is there any protection?
4. **Free tier limits:** Should free users see agent recommendations grayed out ("Upgrade to unlock agent") to drive conversion?
5. **$TECH token role:** Does subscription payment accept $TECH at a discount? Stake $TECH for free tier upgrades?

---

## Tags
#project:aae #spec:fee-tracker-v2 #model:game #model:subscription #layer:agent-intelligence #status:draft
