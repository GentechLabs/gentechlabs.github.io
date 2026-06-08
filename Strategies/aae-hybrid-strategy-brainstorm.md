# AAE Hybrid Strategy Engine — Brainstorm

> **Created:** Apr 29, 2026
> **Origin:** Jordan's directive in HQ — "We want a hybrid system, a little bit of everything, not just LP"
> **Status:** Brainstorm / Architecture Draft
> **Purpose:** Evolve the AAE from LP-only monitor into a multi-strategy allocation brain

---

## The Vision

> *"We want agents that can go from yield farming to staking to just holding. A hybrid system where it works for the market. The same way we look at who's making better returns — the hodlers, the stakers, or the LPers — our bots will let you know: hey, we're switching strategy, let's do this."* — Jordan

The AAE becomes the **brain layer** that other agents want to plug into. Instead of being an LP monitor, it becomes a **strategy allocation engine** that:

1. Compares returns across all yield strategies in real-time
2. Dynamically rotates capital to the highest-performing strategy
3. Proactively alerts users: "We're switching from LP to staking — here's why"
4. Adapts to market regime (bull/bear/range/volatile)

---

## Why This Wins

Everyone is building payment agents. We're building the **intelligence layer**:

| What others build | What we build |
|---|---|
| Payment routing | Strategy routing |
| Single-protocol bots | Multi-protocol brain |
| Reactive alerts | Proactive regime detection |
| Manual strategy selection | Dynamic allocation engine |
| "Put money in X" | "Rotate from X to Y because Z" |

The agent that tells you **when to switch** is worth more than the agent that just executes one strategy.

---

## Strategy Universe

### Core Strategies (Phase 1)

| Strategy | Protocol (Avalanche) | Current Yield | Risk | Liquidity |
|---|---|---|---|---|
| **LP (Concentrated)** | LFJ V2.2 | ~15-40% APR (varies) | Medium (IL) | Medium |
| **HODL** | Native wallet | 0% (pure price appreciation) | Market risk | Instant |
| **Staking (Liquid)** | Benqi (sAVAX) | ~6-8% APR | Low | High (sAVAX liquid) |
| **Staking (Native)** | Avalanche Validator | ~8% APR | Low (lock period) | Low (21-day unbond) |
| **Lending** | Benqi / Euler | ~3-12% APR | Low-Medium | High |

### Extended Strategies (Phase 2)

| Strategy | Protocol | Notes |
|---|---|---|
| **Stablecoin Farming** | Curve/Aave stables | Low risk, steady yield |
| **Blue-chip LP** | Uniswap/LFJ ETH/USDC | Diversify beyond AVAX |
| **Options Writing** | Dopex/Chaos | Premium income |
| **Validator Delegation** | Multiple validators | Diversify staking risk |

---

## Market Regime Detection

The brain needs to classify the current market regime to decide strategy allocation.

### Regime Classifiers

```
REGIME = classify(price_action, volume, volatility, momentum)

Regimes:
├── 🟢 BULL TRENDING    — Price up, volume increasing, momentum strong
├── 🔴 BEAR TRENDING    — Price down, volume increasing, momentum weak
├── 🟡 RANGE-BOUND      — Price oscillating, volume normal, no clear trend
├── 🟠 HIGH VOLATILITY  — Price whipsawing, volume spikes, unclear direction
├── 🔵 ACCUMULATION     — Price flat after dump, volume declining, smart money buying
└── ⚪ PRICE DISCOVERY  — New highs/lows, no historical reference
```

### Detection Logic

```python
def classify_regime(price_24h, price_7d, volume_24h, volume_avg, rsi_14, atr_14):
    momentum = (price_7d - price_24h) / price_24h
    vol_ratio = volume_24h / volume_avg
    volatility = atr_14 / price_24h

    if momentum > 0.10 and vol_ratio > 1.3 and rsi_14 > 55:
        return "BULL_TRENDING"
    elif momentum < -0.10 and vol_ratio > 1.3 and rsi_14 < 45:
        return "BEAR_TRENDING"
    elif volatility > 0.08:
        return "HIGH_VOLATILITY"
    elif abs(momentum) < 0.03 and vol_ratio < 0.8:
        return "ACCUMULATION"
    elif abs(momentum) < 0.05:
        return "RANGE_BOUND"
    else:
        return "PRICE_DISCOVERY"
```

---

## Strategy Allocation Matrix

This is the core — which regime gets which allocation.

### Allocation by Regime

| Regime | LP % | HODL % | Staking % | Lending % | Rationale |
|---|---|---|---|---|---|
| 🟢 **Bull Trending** | 15% | 60% | 15% | 10% | Ride the wave — HODL dominates, small LP for fees |
| 🔴 **Bear Trending** | 10% | 20% | 50% | 20% | Safety — stake for yield, lend for stability |
| 🟡 **Range-Bound** | 40% | 15% | 30% | 15% | LP thrives in range, stake for base yield |
| 🟠 **High Volatility** | 25% | 30% | 25% | 20% | Diversify — no single strategy wins in chaos |
| 🔵 **Accumulation** | 20% | 40% | 25% | 15% | Stack sAVAX + spot, prepare for next move |
| ⚪ **Price Discovery** | 10% | 70% | 15% | 5% | Full upside capture — don't LP in uncharted territory |

### Dynamic Adjustment Rules

```
IF regime changes:
    1. Calculate target allocation from matrix
    2. Compare to current allocation
    3. IF delta > 20% for any strategy:
        → Alert user: "Regime shift detected. Recommending rotation."
        → Show before/after allocation
        → Wait for confirmation (or auto-execute if auto_mode = true)
    4. Execute rotation in tranches (not all at once)
    5. Log transition for P&L tracking
```

---

## Return Comparison Engine

The brain continuously tracks which strategy is winning.

### Metrics Tracked

```python
strategy_returns = {
    "lp": {
        "fees_24h": float,
        "il_24h": float,           # impermanent loss
        "net_return_24h": float,   # fees - IL
        "apr": float,
        "risk_adjusted_return": float  # return / volatility
    },
    "hodl": {
        "price_change_24h": float,
        "usd_value_change": float,
        "apr_equivalent": float    # annualized price change
    },
    "staking": {
        "rewards_24h": float,
        "apr": float,
        "savax_avax_ratio": float  # sAVAX premium/discount
    },
    "lending": {
        "interest_24h": float,
        "apr": float,
        "utilization_rate": float  # pool utilization
    }
}
```

### Performance Leaderboard

Updated in every signal output:

```
📊 STRATEGY LEADERBOARD — Last 24h
1. 🟢 HODL       +$12.40  (+3.2% APR equiv) ← WINNING
2. 🟡 LP          +$2.15   (+58% APR) 
3. 🔵 Staking     +$0.32   (+7.2% APR)
4. ⚪ Lending     +$0.18   (+4.8% APR)

📈 7-Day Cumulative:
   HODL: +$45.20 | LP: +$14.30 | Staking: +$2.24 | Lending: +$1.26

💡 RECOMMENDATION: Bull market — rotate 60% to HODL
```

---

## Bull Market Exit Integration

The D5 bull exit strategy we just built becomes **one trigger within the hybrid engine**:

```
BULL EXIT TRIGGER (existing):
├── Volume Breakout → exit 75% LP
├── Momentum Surge → exit 75% LP
├── Macro Catalyst → exit 50% LP
└── Trend Confirmation → exit 75% LP

IN HYBRID ENGINE, this becomes:
├── Regime shift: RANGE → BULL_TRENDING
├── LP allocation drops: 40% → 15%
├── HODL allocation rises: 15% → 60%
└── STAKING rises: 30% → 15% (sAVAX for safety)

The exit isn't just "pull out of LP" — it's "rotate into the best strategy for this regime."
```

---

## Proactive Agent Behavior

The brain doesn't just sit there — it **tells you what to do**.

### Alert Types

| Alert | When | Action Required |
|---|---|---|
| **🔄 Regime Shift** | Regime classifier changes | Confirm strategy rotation |
| **📊 Leaderboard Change** | New strategy takes #1 spot | Review allocation |
| **⚠️ Strategy Underperformance** | Any strategy < 50% of benchmark for 7 days | Consider reducing allocation |
| **🐂 Bull Exit** | Existing D5 signals trigger | Rotate LP → HODL |
| **🔻 Bear Entry** | Regime shifts to BEAR_TRENDING | Rotate HODL → Staking + Lending |
| **💰 Compound Optimal** | Fees exceed threshold in current best strategy | Auto-compound |
| **🎯 Rebalance** | Allocation drift > 10% from target | Rebalance to target |

### Message Format

```
🧠 AAE STRATEGY SWITCH — [timestamp]

📊 Regime: RANGE-BOUND → BULL_TRENDING
📈 Confidence: High (RSI 68, Volume 1.8x, 7d momentum +12%)

Current Allocation → Recommended:
  LP:      40% → 15%  (exit 25%)
  HODL:    15% → 60%  (increase 45%)
  Staking: 30% → 15%  (reduce 15%)
  Lending: 15% → 10%  (reduce 5%)

💡 Why: LP underperforms in trending markets (IL > fees). 
   HODL captures full upside. Staking provides base yield.

⚡ Action: Rotate $33.70 from LP to spot AVAX
🎯 Keep $16.85 in bid-ask LP at $10.00 resistance
```

---

## Architecture

### Current (LP-Only)
```
DexScreener → lp-aae-signal-monitor.py → JSON Signal → Cron → Telegram
```

### Proposed (Hybrid Engine)
```
┌──────────────────────────────────────────────────────────┐
│                  AAE STRATEGY BRAIN                       │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Market     │  │   Strategy   │  │  Allocation   │  │
│  │   Regime     │  │   Returns    │  │  Engine       │  │
│  │   Classifier │  │   Tracker    │  │               │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                │                   │           │
│         ▼                ▼                   ▼           │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Signal Aggregator                    │    │
│  │  (regime + returns + allocation = recommendation)│    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────────────────┴──────────────────────────┐    │
│  │              Execution Router                     │    │
│  │  (LP commands, staking txs, swap routes)         │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────────────────┴──────────────────────────┐    │
│  │              P&L Tracker                          │    │
│  │  (per-strategy returns, cumulative, risk-adjusted)│   │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
      ┌──────────┐ ┌──────────┐ ┌──────────┐
      │ Telegram │ │  Web     │ │  API     │
      │ Alerts   │ │Dashboard │ │  (other  │
      │          │ │          │ │ agents)  │
      └──────────┘ └──────────┘ └──────────┘
```

### Data Sources

| Module | Data Source | Frequency |
|---|---|---|
| Price/Volume | DexScreener, Birdeye x402 | Every 10 min |
| LP Position | On-chain (balanceOf bins) | Every 10 min |
| Staking APR | Benqi API, Validator API | Daily |
| Lending APR | Benqi/Euler API | Daily |
| RSI/Momentum | Computed from price history | Every 10 min |
| Gas Costs | Avalanche RPC | Per transaction |

---

## Implementation Phases

### Phase 1: Return Comparison Engine (Week 1)
- [ ] Add HODL tracking to existing AAE script (track spot value vs entry)
- [ ] Add staking APR fetch (Benqi sAVAX rate)
- [ ] Add lending APR fetch (Benqi supply rate)
- [ ] Output strategy leaderboard in signal JSON
- [ ] Update cron to include leaderboard in Telegram output

### Phase 2: Regime Classifier (Week 2)
- [ ] Implement regime detection logic (price action, volume, RSI, ATR)
- [ ] Build regime history tracking (store last N regimes in state file)
- [ ] Map regimes to allocation targets
- [ ] Add regime + allocation to signal output

### Phase 3: Allocation Engine (Week 3)
- [ ] Calculate current vs target allocation
- [ ] Generate rotation recommendations
- [ ] Add proactive alerts (regime shift, leaderboard change)
- [ ] Build rotation execution prompts (manual confirmation first)

### Phase 4: Auto-Execution (Week 4)
- [ ] Build swap routing (LP exit → AVAX/USDC split → stake/lend)
- [ ] Add auto-compound per strategy
- [ ] Risk limits (max 20% rotation per day, max 60% in any single strategy)
- [ ] Full P&L tracking across all strategies

---

## Risk Management

### Hard Limits
- **Max single-strategy allocation:** 70% (always diversify)
- **Min per strategy:** 5% (keep positions alive for re-entry)
- **Max daily rotation:** 20% of total portfolio (prevent overtrading)
- **Cooldown between regime shifts:** 4 hours (prevent whipsaw)
- **Gas budget:** Max 2% of rotation value in gas costs

### Safety Rails
- **Manual confirmation required** for all rotations (Phase 3)
- **Auto-mode opt-in** only after 30 days of manual confirmation history
- **Emergency exit:** If any strategy loses >15% in 24h, alert + reduce to minimum
- **Circuit breaker:** If gas > 5% of position value, pause all rotations

---

## Open Questions

1. **Which chains?** Start Avalanche only? Or plan for Base/Solana from day 1?
2. **Validator staking vs liquid staking?** sAVAX is liquid but lower yield. Native staking locks capital.
3. **Options strategies?** Too complex for v1? Or worth including for advanced users?
4. **Multi-asset support?** Start AVAX/USDC only? When do we add ETH/BTC pools?
5. **Auto-execution trust level?** Jordan-only? Or configurable per user?
6. **API for other agents?** REST endpoint for payment agents to query brain state?

---

*Brainstorm session: Apr 29, 2026 — Jordan directive, DMOB architecture*
