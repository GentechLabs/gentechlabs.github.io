# OpenTrader × Agent Arena — Integration Analysis

**Date:** 2026-05-22
**Repo:** [Open-Trader/opentrader](https://github.com/Open-Trader/opentrader) — 12K+ lines TypeScript, pnpm monorepo, MIT license

---

## TL;DR

OpenTrader is a production-quality open-source trading bot framework. Its paper trading mode, generator-based strategy runner, and backtesting engine are directly usable as Agent Arena's simulation backbone. We fork the core packages and build Arena's multi-agent orchestration, scoring, and competitive layers on top. The current HTML demo gets replaced with a real backend.

---

## What We Get Out of the Box

### 🎯 Paper Trading Mode
`PaperExchange` extends the real exchange class but overrides all order methods with simulated fills. Uses live bid/ask data from real exchanges but executes against simulated balances stored in Prisma. Limit orders fill when price crosses, market orders fill at current bid/ask. This is exactly what Agent Arena's simulation layer needs — no custody risk, real market dynamics.

### 🎯 Strategy Runner (Generator-Based)
Strategies are JavaScript generator functions that `yield` effects (buy, sell, get indicators). A central `StrategyRunner` intercepts effects, executes them, and feeds results back into the generator. This means Agent Arena agents could be written as OpenTrader strategies — same contract, same lifecycle, same effect types.

### 🎯 Backtesting Engine
Full candle-by-candle simulation with `MarketSimulator` and `MemoryExchange`. Processes historical data, fills orders against candle closes, generates profit reports. Ready to go for agent performance scoring and leaderboard computation.

### 🎯 18 Effect Types
`BUY`, `SELL`, `USE_SMART_TRADE`, `USE_DCA`, `USE_INDICATOR` (RSI/SMA/EMA), `USE_MARKET`, `USE_CANDLE`, `ALL` (parallel execution). Rich enough to power complex agent strategies without custom extensions.

### 🎯 Custom Strategy Loading
Drop `.mjs` files in a directory, they get auto-loaded. Agent Arena could register agent strategies the same way — each agent ships as a strategy module.

### 🎯 100+ Exchange Support (via CCXT)
Real market data for simulation, or live trading for post-Arena deployment. The exchange abstraction means agents trained in Arena can graduate to real markets with minimal code changes.

---

## What Needs Building

### ⚡ Multi-Agent Orchestration
OpenTrader is single-bot per instance. Arena needs N agents running simultaneously with isolated state. Extend the `Platform` class to manage multiple concurrent strategy runners, each with their own balance, position, and trade history.

### ⚡ Agent Scoring & Leaderboard
No built-in performance ranking. Add a scoring layer on top of trade logs: Sharpe ratio, max drawdown, total return, win rate, risk-adjusted metrics. Real-time leaderboard updates as agents trade.

### ⚡ Competitive Mechanics
No PvP features (market manipulation, agent-vs-agent dynamics, information asymmetry). Build these as custom effects or extend the strategy runner with Arena-specific effect types.

### ⚡ Arena Dashboard (Web UI)
OpenTrader has a React SPA but it's designed for single-bot management. Arena needs a competition dashboard: live agent performance, trade feed, leaderboard, bracket/tournament view.

### ⚡ Echo Brain Integration
OpenTrader has no concept of cross-session memory or agent reflection. The Echo Brain architecture (agent remembers trades, reflects across weeks) sits on top as a separate layer that reads trade logs and feeds insights back into strategy decisions.

---

## Integration Architecture

```
Agent Arena (new layer)
├── Competition Manager (new)
│   ├── Tournament brackets
│   ├── Agent registration
│   └── Scoring engine
├── Arena Dashboard (new React SPA)
│
├── Core Engine (forked from OpenTrader)
│   ├── bot-processor/    → strategy execution
│   ├── exchanges/        → paper + live exchange
│   ├── backtesting/      → historical simulation
│   └── types/            → shared type system
│
└── Extensions (new)
    ├── multi-agent orchestrator
    ├── competitive effects (PvP)
    ├── Echo Brain (cross-session memory)
    └── scoring/leaderboard service
```

---

## Migration Impact

- **Current HTML demo** → replaced with OpenTrader-backed simulation
- **Repo structure** → fork core packages, build Arena layers in same monorepo or new repo importing them
- **Demo timeline** → slightly extended (need to integrate, not just build UI), but the result is production-quality
- **Hackathon readiness** → stronger. Real simulation engine > HTML mockup for judges

---

## Recommendation

**Fork and integrate.** The simulation and strategy execution infrastructure is production-quality — we don't rebuild that, we extend it. The 12K lines of battle-tested TypeScript saves us weeks of work on the parts that are hardest to get right (exchange abstraction, order matching, backtesting). We focus our energy on what makes Agent Arena unique: multi-agent competition, scoring, Echo Brain, and the arena experience.

**Next step:** Clone, set up dev environment, verify paper trading mode works end-to-end with a test strategy. Then start building the multi-agent orchestrator.
