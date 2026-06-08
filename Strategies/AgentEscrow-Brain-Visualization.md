# AgentEscrow — Brain Visualization & Simulated Training
**Created:** 2026-04-18
**Status:** Ideation

---

## The Concept

The agent's "brain" (its research, decisions, and reasoning) is not hidden — it's the product. Users see WHY the agent recommends, not just WHAT. Combined with simulated training (backtesting on historical data), users build trust before committing real capital.

---

## Brain Visualization

Show the user the agent's thinking process in real-time.

### Layer 1: Research
```
📊 Research Layer
├─ Checked: LFJ, Yield Yak, Benqi
├─ Compared: 12 pools, 3 protocols
└─ Selected: AVAX/USDC V2.2 (binStep 10)
```

### Layer 2: Decision
```
🧠 Decision Layer
├─ Current price: $9.80
├─ Recommended range: 9.66 - 9.95
├─ Projected fees: ~$12/day
└─ Risk score: Medium (volatility flag)
```

### Layer 3: Simulation
```
🎮 Simulation Layer
├─ Backtest 30 days: +$340 (vs $280 hold)
├─ Backtest 90 days: +$890 (vs $720 hold)
└─ Worst drawdown: -$45 (4.5%)
```

### Layer 4: Recommendation
```
✅ Recommendation: Deploy with 9.66-9.95 range
```

---

## Simulated Training (Backtesting)

Before committing real money, the agent "practices" on historical data.

### Features
1. **Historical backtest** — "If you did this 30/60/90 days ago, here's what happens"
2. **Side-by-side comparison** — Your strategy vs. auto-pool vs. holding
3. **Stress testing** — "What if AVAX drops 20%?" "What if volume spikes 3x?"
4. **Agent self-adjustment** — Learns from simulation, refines recommendation

### Data Sources
- On-chain historical prices (CoinGecko, DeFiLlama)
- Historical LP volume/fees (DexScreener, LFJ API)
- Volatility metrics (ATR, standard deviation)
- Correlation data (AVAX vs BTC, AVAX vs ETH)

### Visualization
- Line chart: strategy PnL vs. hold vs. auto-pool
- Drawdown chart: worst-case scenarios
- Fee accumulation over time
- Range efficiency heat map

---

## Our Vault → User Brain

Mapping our internal Obsidian system to user-facing features:

| Our Vault | User-Facing | What It Shows |
|-----------|-------------|---------------|
| Green Room | Research notes | What the agent considered |
| Mess Hall | Decision log | Why the agent chose this |
| Agent States | Market understanding | Agent's current read on market |
| Handoff Board | Reasoning chain | Step-by-step logic |
| Wiki | Knowledge base | Agent's learned patterns |
| Cron Jobs | Automation rules | User's custom triggers |

---

## Why This Wins

1. **Trust** — Users see the brain, not a black box
2. **Confidence** — Simulated training before real money
3. **Education** — Users learn DeFi by watching the agent think
4. **Retention** — Brain visualization is addictive (like watching your portfolio)
5. **Differentiation** — Nobody else shows their agent's thinking

---

## Tags
#AgentEscrow #brain #visualization #simulation #backtesting #UX
