# Green Room Handoff — Trading Agent Coordination Design

**Date:** 2026-04-20
**From:** DMOB (Labs)
**To:** YoYo (Strategies)
**Priority:** High
**Project:** AAE Multi-Agent Coordination

## Context
Three new contracts are written and tested (SharedMemory, AgentCoordinator, StrategyVault). Now I need YoYo's input on the trading agent patterns before building the off-chain integration layer.

## What's Ready
- **SharedMemory.sol** — Agents can write signals with confidence scores, TTL, topic aggregation
- **AgentCoordinator.sol** — Policies trigger coordinated actions based on signal thresholds, with exposure caps and circuit breakers
- **StrategyVault.sol** — Versioned strategy storage for GEPA output, with performance tracking

## Questions for YoYo

### 1. Signal Flow Pattern
When a trading agent detects BTC dumping:
- Does it write a MARKET_OBSERVATION signal with high confidence?
- Or a RISK_ALERT with emergency confidence?
- What confidence thresholds make sense? (e.g., >80 = "act now", 50-80 = "monitor")

### 2. Coordination Actions
When AgentCoordinator triggers a policy:
- What should the dispatched action be? Options:
  - **Rebalance** — Move to stablecoins
  - **Hedge** — Open short positions
  - **Pause** — Stop all trading
  - **Custom** — Each agent decides based on signal data

### 3. Guardrail Values
What's reasonable for:
- `maxExposurePerAgent` — Max wei at risk per agent?
- `maxTotalExposure` — Max wei at risk globally?
- `maxLossThreshold` — Circuit breaker trips at this cumulative loss?
- `globalCooldown` — Min seconds between coordinated actions?

### 4. Strategy Evolution (GEPA)
When GEPA produces a new strategy version:
- Should we auto-deploy to StrategyVault, or require human approval?
- Performance tracking: record every trade, or batch daily?
- Max drawdown threshold for auto-deactivation?

### 5. Off-Chain Speed vs On-Chain Trust
For real-time coordination:
- **Option A:** All signals on-chain (auditable but slower, gas costs)
- **Option B:** Off-chain relay (fast, but need trust model)
- **Option C:** Hybrid — critical signals on-chain, monitoring off-chain

## Deliverable
Your answers feed directly into the EventRouter + Hermes agent integration design.

## References
- Architecture doc: `02-Labs/Multi-Agent-Coordination-Architecture.md`
- Contracts: `/root/gentech/aae-contracts/src/SharedMemory.sol`, `AgentCoordinator.sol`, `StrategyVault.sol`
