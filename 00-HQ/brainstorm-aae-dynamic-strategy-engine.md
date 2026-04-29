---
date: 2026-04-29
type: brainstorm
source: Jordan (voice memo)
status: open — team brainstorm
---

# A.A.E. Dynamic Strategy Engine — Brain Layer Concept

## Jordan's Vision (Apr 29, 2026)

> "While everybody is worried about building their own layer of agents that can make payments, we're going to make sure our brain layer is tight to where everybody wants to use it. We want agents that can go from yield farming to staking to just holding. We want a hybrid type system where it's a little bit of everything — what works for the market. The same way we look at who's making better returns, the hodlers, the stakers, or the LPers. That's the same type of system where our bots will let you know like, hey, we're switching strategy, let's do this."

### Jordan's Addition (Apr 29, 2026 — Second Pass)

> "Everybody's strategy is just to make a vault where, of course the AI will trade better than you. But I really want a system where you can learn from the AI, you can train the AI to trade like you, and you can autonomously execute strategies."

### Core Thesis

**Everyone is building payment layers. We're building the brain layer.**

The A.A.E. shouldn't just execute one strategy — it should **dynamically evaluate and switch between all DeFi strategies** based on market conditions. The competitive moat isn't "we can do LP" or "we can stake." It's "our system knows what to do and when to do it."

### Three Pillars

1. **Dynamic Strategy Rotation** — Rotate between LP, staking, hodling, farming based on market regime
2. **Bidirectional Learning** — Users learn from the AI's reasoning; AI learns from user's trading patterns
3. **Autonomous Execution** — Strategies execute on their own with user-set guardrails

---

## What This Means

The A.A.E. brain layer becomes a **strategy-agnostic DeFi orchestrator** that:

1. **Monitors** performance across all major yield sources in real-time
2. **Compares** returns: hodling vs staking vs LPing vs yield farming
3. **Recommends** (or auto-executes) strategy switches based on what's winning
4. **Communicates** to users: "We're switching strategy — here's why"
5. **Learns** from outcomes — which switches worked, which didn't

---

## Strategy Universe

The A.A.E. should track and be capable of deploying capital across:

| Strategy | Risk Profile | Yield Source | Current State in AAE |
|----------|-------------|--------------|---------------------|
| **Hodling** (AVAX/SOL/BTC) | Low–Med | Price appreciation | ✅ D5 DCA + bull exit signals |
| **LP (Concentrated)** | Med–High | Trading fees | ✅ D5 + LP Monitor |
| **LP (Passive/Wide)** | Med | Trading fees (lower) | ❌ Not implemented |
| **Staking (Validator)** | Low | Inflation rewards | ❌ Not implemented |
| **Lending/Borrowing** | Med | Interest | ❌ Not implemented |
| **Yield Farming** | High | Token emissions | ❌ Not implemented |
| **Basis Trading** | High | Funding rate arb | ❌ Not implemented |
| **Stablecoin Yield** | Low | Protocol revenue | ❌ Not implemented |

---

## Architecture: The Brain Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    A.A.E. STRATEGY BRAIN                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Market Oracle │  │ Yield Oracle │  │ Risk Oracle  │      │
│  │ (regime,      │  │ (APY/APR     │  │ (volatility, │      │
│  │  trend, vol)  │  │  across all  │  │  drawdown,   │      │
│  │              │  │  protocols)  │  │  correlation)│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         └──────────────────┼──────────────────┘               │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │  STRATEGY      │                        │
│                    │  EVALUATOR     │                        │
│                    │                │                        │
│                    │  • Rank all    │                        │
│                    │    strategies  │                        │
│                    │    by risk-    │                        │
│                    │    adjusted    │                        │
│                    │    return      │                        │
│                    │  • Apply user  │                        │
│                    │    constraints │                        │
│                    │  • Generate    │                        │
│                    │    switch      │                        │
│                    │    signal      │                        │
│                    └───────┬────────┘                        │
│                            │                                 │
│              ┌─────────────┼─────────────┐                  │
│              │             │             │                   │
│         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐             │
│         │  LP     │  │ Staking │  │ Yield   │             │
│         │  Agent  │  │  Agent  │  │  Agent  │  ...        │
│         └─────────┘  └─────────┘  └─────────┘             │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │           OUTCOME TRACKER / LEARNER               │       │
│  │  • Which switches worked? (measured 24-72h later) │       │
│  │  • Confidence scores per strategy recommendation  │       │
│  │  • User override patterns (what do humans reject?) │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## How the "Strategy Switch" Works

### 1. Continuous Evaluation (Every Hour/Daily)

The brain queries yield data across all protocols and strategies:

```
Strategy Returns (Last 24h, Risk-Adjusted):
  1. LP AVAX/USDC (Ranger)    → 14.2% APR, Sharpe 1.8
  2. Staking AVAX (Validator)  → 8.1% APR, Sharpe 2.4
  3. Hodl AVAX                 → +2.3% (price move)
  4. Yield Farm (Pangolin)     → 18.5% APR, Sharpe 0.9
  5. Stablecoin Lending        → 4.2% APR, Sharpe 3.1

Recommendation: HOLD current LP position
Reasoning: Risk-adjusted return still beats alternatives.
           Monitor: if AVAX breaks $10 → switch to hodl.
```

### 2. Switch Signal (When Market Changes)

```
⚠️ STRATEGY SWITCH RECOMMENDATION

Current: LP AVAX/USDC (earning 14.2% APR)
Trigger: AVAX broke $10.50 with volume spike (>2x avg)
Recommendation: EXIT LP → HODL (spot AVAX)

Why: Bull regime confirmed. LP upside is capped at fee income.
     Spot captures unlimited upside. Risk-adjusted, hodl now
     beats LP by 3.1x on expected return.

Confidence: 87% (4/5 signals fired)
User action: Confirm or override in 60 seconds
Auto-execute: [OFF by default — ON after user sets preference]
```

### 3. User Communication

The bot proactively tells the user:
- **"We're switching strategy — here's why"**
- **"Market conditions changed — here's what we're doing about it"**
- **"You're leaving money on the table — let's rebalance"**

Not just notifications — **actionable intelligence with context.**

---

## Key Differentiators

### What Others Are Building
- Payment agents (Venmo for crypto)
- Single-strategy bots (just LP, just DCA)
- Chatbot wrappers (GPT + wallet = "agent")

### What We're Building
- **Brain layer** that evaluates ALL strategies simultaneously
- **Dynamic switching** based on real market conditions
- **Bidirectional learning** — AI teaches you, you teach the AI
- **Autonomous execution** with user-set guardrails
- **Outcome tracking** — learns what works, what doesn't
- **User-facing intelligence** — "here's what to do and why"

---

## Pillar 2: Bidirectional Learning

This is what separates A.A.E. from every other "AI trades for you" vault.

### Learning FROM the AI (User Education)
- The bot explains WHY it's recommending a switch in plain language
- Users see the reasoning chain: market signal → strategy evaluation → recommendation
- Historical dashboard: "Here's what we did last month, here's how it performed"
- Pattern recognition: "When AVAX does X, LP tends to outperform staking by Y%"
- Educational nudges: "You might not have noticed this — BTC just broke a key level"

### Training the AI to Trade Like You (User Patterns)
- **Trade journaling** — User's manual trades get logged and analyzed
- **Style fingerprinting** — AI builds a profile: "User tends to be conservative, prefers stablecoin yield over high-vol LP"
- **Override learning** — When user rejects a recommendation, the AI asks why and learns
- **Consensus building** — "User has overrode 3 recommendations this month — adjusting risk model"
- **Copy-trading DNA** — If user has good trades, AI learns the pattern and replicates

### How This Works Technically
```
┌──────────────────────────────────────────────────┐
│           LEARNING FEEDBACK LOOP                 │
│                                                   │
│  AI recommends: "Exit LP → HODL"                 │
│       │                                           │
│       ▼                                           │
│  User: [Approve] or [Reject + Reason]            │
│       │                                           │
│       ▼                                           │
│  Outcome tracked (48-72h later):                  │
│    • If approve → result logged (win/loss)        │
│    • If reject → user's alternative logged        │
│       │                                           │
│       ▼                                           │
│  AI updates:                                      │
│    • Confidence score for this signal type        │
│    • User's risk preference model                 │
│    • Strategy ranking weights                     │
│                                                   │
│  Over time: AI learns "this user is conservative, │
│  doesn't like vol LP, prefers staking. Also,      │
│  when they override, they're right 60% of time."  │
└──────────────────────────────────────────────────┘
```

---

## Pillar 3: Autonomous Execution

### The Moat
> While everyone else's agent is executing one strategy, ours is already three moves ahead — telling you when to switch before you even knew you should.

---

## Existing AAE Assets That Feed Into This

| Asset | What It Provides | Status |
|-------|-----------------|--------|
| D5 Strategy Engine | LP ↔ Spot switching logic | ✅ Built |
| LP Monitor | Real-time fee/range efficiency | ✅ Running hourly |
| Bull Market Exit Strategy | When to exit LP, go spot | ✅ Documented |
| Hybrid LP + Spot Strategy | Regime detection, Go Spot signals | ✅ Draft |
| Multi-Agent Trading Orchestration | Shared brain, cross-agent memory | 📝 Spec written |
| Wallet Monitor | Portfolio balance tracking | ✅ Running 3h |
| Almanak Integration | DeFi strategy framework | 🔄 Research phase |
| Agent Escrow (Solana) | On-chain agent coordination | 🔨 Building |

---

## Open Questions for Team

### For YoYo (Strategies)
1. What's the best risk-adjusted ranking methodology? Sharpe vs Sortino vs simple APR?
2. How do we model correlation between strategies? (LP + staking on same asset = concentrated risk)
3. What's the minimum viable yield oracle we can build? (DeFiLlama API? Direct protocol queries?)
4. How do we account for gas costs in strategy switching?

### For DMOB (Labs)
1. Can we build a unified yield scanner that pulls APY/APR from Ranger, Pangolin, Benqi, etc.?
2. What's the execution complexity for multi-protocol capital movement?
3. Can we reuse the LP Monitor infrastructure for cross-strategy monitoring?
4. Smart contract feasibility: one contract per strategy or unified vault?

### For Jordan
1. Priority ranking: which strategies should we support first beyond LP?
2. Auto-execute on switch signals, or always require user confirmation?
3. User risk profiles: conservative vs aggressive vs degen — different defaults?
4. Integration with Agent Escrow: does strategy switching become a job on the escrow system?

---

## Phased Roadmap

### Phase 1: Monitor Only (Weeks 1–2)
- Build yield oracle that tracks APY/APR across protocols
- Display "strategy leaderboard" in daily reports
- No capital movement — just intelligence

### Phase 2: Recommend (Weeks 3–4)
- Add switch signals to bot output
- "We recommend switching from X to Y" with reasoning
- User confirms via button/prompt

### Phase 3: Auto-Switch (Month 2)
- User sets risk profile and auto-execute preferences
- Bot moves capital based on strategy rankings
- Circuit breakers prevent bad switches (slippage, gas, etc.)

### Phase 4: Learn (Month 3+)
- Track outcome of each switch (was it profitable 48h later?)
- Build confidence scores per strategy recommendation
- Personalize recommendations based on user's portfolio and history

---

## Bottom Line

This is the **brain layer** that makes A.A.E. the system everyone wants to use. Not because it can do one thing well — because it knows what to do, when to do it, and why. The payment agents are commodity. The execution layer is commodity. **The brain layer is the moat.**

Let's brainstorm this in depth and figure out the architecture.

---

*Created by: Desmond (Creative)*
*Status: Open — awaiting team input*
*Location: 00-HQ/brainstorm-aae-dynamic-strategy-engine.md*
