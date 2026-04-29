# 🧠 AAE Hybrid Strategy Brain — Brainstorm

> **Date**: 2026-04-29
> **Context**: Jordan wants AAE to have an adaptive brain layer that dynamically switches between yield strategies based on market conditions — not locked into one approach.

---

## The Vision

While everyone else is building "agents that can make payments," we're building **agents that know where to put the money**.

The AAE Brain Layer evaluates yield strategies in real-time and re-allocates capital based on what's actually performing. Not one strategy — **all strategies**, intelligently rotated.

## The Three Modes (Current Market)

| Strategy | When It Wins | AAE Signal |
|----------|-------------|------------|
| **HODL** | Bull momentum, breakout conditions | Volume spike, RSI >60, above range |
| **Staking** | Sideways/choppy, low volatility | Range-bound, no clear trend |
| **LP (Liquidity Provision)** | High volume, range-bound | Tight spread, high pair volume |
| **Yield Farming** | Any market (passive income) | Always-on baseline allocation |

## The Hybrid Allocation Model

Instead of all-or-nothing, AAE runs a **weighted portfolio** that shifts:

```
BASELINE (always active):
├── 30% — Yield Farming (passive, compounding)
├── 20% — Staking (stable yield, low risk)
└── 50% — Active bucket (LP / HODL / rotate)

ACTIVE BUCKET (dynamic):
├── LP when: volume high, range-bound
├── HODL when: breakout / momentum surge
├── Rotate when: signals shift
└── Defensive when: macro uncertainty
```

## Decision Tree — The Brain Logic

```
MARKET STATE DETECTED
│
├─ HIGH VOLATILITY + BREAKOUT
│   └─ → Shift 50% to HODL, exit LP
│   └─ → Keep farming + staking baseline
│
├─ HIGH VOLUME + RANGE-BOUND
│   └─ → Increase LP allocation to 40%
│   └─ → Reduce HODL exposure
│
├─ LOW VOLATILITY + SIDEWAYS
│   └─ → Max staking allocation (30%)
│   └─ → LP with tight ranges
│
├─ MACRO UNCERTAINTY (bear signals)
│   └─ → Max staking + farming (60%)
│   └─ → Exit LP positions
│   └─ → Minimal HODL (10%)
│
└─ UNKNOWN / NO SIGNAL
    └─ → Default to baseline allocations
    └─ → Wait for clear signal
```

## The "Switch Strategy" Prompt

AAE agents proactively notify the user:

> *"Market regime shift detected. RSI crossing 70 with volume surge — transitioning 40% from LP to HODL position. Yield farming continues at 30% baseline. Approve?"*

Or in passive mode:

> *"AAE re-allocated: LP ↓30%, HODL ↑20%, Staking ↑10%. Net yield impact: +2.3% projected APR."*

## The Learning Layer — Train the AI to Trade Like You

This is the real moat. Not just autonomous execution — **user-trained intelligence**.

### How It Works
1. **Observe** — AAE watches your trading decisions over time (what you buy, sell, hold, and why)
2. **Learn** — Pattern recognition: your risk tolerance, preferred strategies, market conditions you thrive in
3. **Mimic** — AAE starts making decisions *like you*, with your style baked in
4. **Execute** — Autonomously runs your strategies when you're not watching
5. **Improve** — Compares its decisions to yours, learns from mistakes

### The Feedback Loop
```
USER ACTION → AAE OBSERVES → PATTERN CAPTURED
     ↑                                    ↓
     ← CORRECTION ← AAE PROPOSES ←
```

- User corrects AAE: "No, exit now" → AAE learns the signal
- User approves AAE: "Yes, good call" → AAE reinforces the pattern
- Over time: AAE = personalized trading agent that thinks like you

### The Three Modes of Learning
| Mode | Description |
|------|------------|
| **Shadow Mode** | AAE observes, suggests, but doesn't execute. User confirms every move. |
| **Supervised Mode** | AAE executes with approval. User can override anytime. |
| **Autonomous Mode** | AAE runs independently. Only notifies on major shifts. |

### Why This Matters
> *"Everyone's building AI that trades better than you. We're building AI that trades **like** you — and learns to be even better."*

The user doesn't lose control. They **train** the system. Their edge becomes the AI's edge.

---

## Competitive Advantage

| Competitor Approach | AAE Approach |
|--------------------|--------------|
| Single strategy agents | Multi-strategy portfolio |
| Manual prompt required | Proactive regime detection |
| One-dimensional yield | Hybrid compounding |
| Reactive only | Predictive + reactive |
| "Pay for my service" | "My service makes you money" |

## Key Differentiator

> **"Everyone is building the payment layer. We're building the brain layer."**

The AAE doesn't just execute — it **decides**. It watches the market, compares strategy performance, and rotates capital. The user can override, but the default is smart.

## Implementation Phases

### Phase 1 — The Brain (Now → Hackathon)
- [ ] Market regime classifier (volatility, trend, volume)
- [ ] Strategy performance tracker (LP APR vs staking vs HODL)
- [ ] Basic rotation logic (if/then rules)
- [ ] User notification on strategy shifts

### Phase 2 — The Hybrid (Post-Hackathon)
- [ ] Weighted allocation engine
- [ ] Dynamic rebalancing based on signals
- [ ] Multi-chain support (AVAX, SOL, ETH)
- [ ] Historical backtesting of rotation decisions

### Phase 3 — The Intelligence (Long-term)
- [ ] ML-based regime prediction
- [ ] Correlation analysis across strategies
- [ ] Portfolio optimization (Sharpe ratio, max drawdown)
- [ ] Cross-agent coordination (multiple AAEs sharing signals)

---

## Next Steps

1. **Design the regime classifier** — What signals define each market state?
2. **Build the strategy comparison engine** — Track APR across all active strategies
3. **Prototype the rotation logic** — Start with simple rules, evolve to adaptive
4. **Integrate with existing LP monitor rules** — Extend D5 with hybrid allocation
5. **Hackathon angle** — "The only agent that knows WHERE to put your money"

---

*This is the moat. While they build payment rails, we build the brain that tells the money where to go.*
