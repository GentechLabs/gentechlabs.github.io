# Multi-Agent Trading Orchestration — Gap Analysis & Architecture Spec

**Date:** 2026-04-20
**Author:** YoYo (Strategies)
**Priority:** High
**Status:** Draft — pending DMOB review for smart contract feasibility

---

## Context

Jordan's gap analysis identified 4 critical gaps between current GEPA/self-evolution capabilities and what's needed for a production multi-agent trading system. This document addresses each gap from the **trading agent perspective** — what the system needs to do, what's missing, and what we should build.

---

## The Vision (What We're Building Toward)

> Multiple agents (trading, yield, staking, LP management) observe markets in real-time. When one detects a pattern (e.g., "BTC dumping → all coins follow"), the collective brain triggers coordinated action — withdraw LPs, rebalance to stables, hedge — automatically, with learned confidence thresholds.

**This is not single-agent optimization.** It's a **coordinated swarm** where:
- Each agent specializes (LP manager, staking rotator, spot trader, yield farmer)
- Shared memory lets agents learn from each other's outcomes
- Real-time triggers fire based on market conditions, not batch schedules
- On-chain execution is wired to actual smart contracts (AgentRegistry, JobEscrow, AgentToken)

---

## Gap 1: Shared Memory (Cross-Agent Knowledge Base)

### What We Need
A **shared brain** that all trading agents read from and write to. Not individual agent memory — collective intelligence.

### Current State
- AgentRegistry.sol tracks skill hashes (on-chain)
- No shared observation store
- No cross-agent outcome tracking
- GEPA optimizes one agent's skills in isolation

### Proposed Architecture

```
┌──────────────────────────────────────────────────┐
│              Shared Memory Layer                   │
├──────────────────────────────────────────────────┤
│                                                    │
│  On-Chain (AgentRegistry.sol extension)            │
│  ├── AgentRiskScore.sol — per-agent health metrics │
│  ├── ObservationHash.sol — merkle root of off-chain│
│  │   observations (gas-efficient attestation)      │
│  └── StrategyOutcome.sol — P&L records per agent   │
│                                                    │
│  Off-Chain (Redis + Postgres or 0G Storage)        │
│  ├── Market observations (price, volume, signals)  │
│  ├── Agent decisions + reasoning traces            │
│  ├── Outcome logs (win/loss, P&L, Sharpe)          │
│  └── Correlation events (multi-agent patterns)     │
│                                                    │
│  Bridge: Agents write observations → merkle root   │
│  committed on-chain periodically (batch attestation)│
└──────────────────────────────────────────────────┘
```

### Data Flow for Trading Agents
1. **LP Agent** observes: "AVAX/USDC range crossed, IL increasing"
2. **Writes** to shared store: `{event: "range_crossed", pair: "AVAX/USDC", il: -2.3%, timestamp}`
3. **Correlation Engine** detects: 3 agents reporting IL simultaneously → market stress event
4. **Brain** triggers: coordinated response based on evolved rules
5. **All agents** read the stress event → act according to their specialization

### Assumptions
- Off-chain storage is fast enough for real-time reads (< 50ms)
- On-chain attestation happens every N blocks (cost trade-off)
- 0G Storage can handle the observation volume (TBD — needs DMOB validation)

### Sensitivity Analysis
| Parameter | Impact if Wrong | Mitigation |
|-----------|----------------|------------|
| Write latency > 100ms | Missed correlation events | Use Redis as hot store, async commit |
| Storage cost too high | Can't afford continuous writes | Batch + merkle root pattern |
| Agents write garbage | Corrupted shared brain | Validation layer + reputation weighting |

---

## Gap 2: Real-Time Coordination (Event-Driven Triggers)

### What We Need
**Live market-condition triggers** — not cron schedules, not batch optimization. When BTC drops 3% in 5 minutes, the system reacts in seconds, not "next GEPA run."

### Current State
- GEPA is batch/offline — runs optimization periodically
- Hermes cron jobs are interval-based (30m, 1h)
- No WebSocket or streaming market data integration
- No event bus for inter-agent signaling

### Proposed Architecture

```
┌───────────────────────────────────────────────────────┐
│                Event-Driven Trigger System              │
├───────────────────────────────────────────────────────┤
│                                                         │
│  Data Ingestion (Real-Time)                             │
│  ├── WebSocket feeds: Binance, CoinGecko, LFJ, Raydium│
│  ├── On-chain event listeners (price oracles, swaps)   │
│  └── Mempool watcher (MEV signals, large tx detection) │
│                                                         │
│  Trigger Engine                                         │
│  ├── Price triggers: "BTC > 5% move in 15m"           │
│  ├── Correlation triggers: "3+ agents reporting stress"│
│  ├── Portfolio triggers: "Total drawdown > X%"         │
│  └── Custom triggers: evolved by GEPA over time        │
│                                                         │
│  Action Router                                          │
│  ├── Emergency: halt all positions (circuit breaker)   │
│  ├── Defensive: reduce exposure, move to stables       │
│  ├── Rebalance: shift allocations per evolved rules    │
│  └── Opportunistic: increase position on dip signals   │
│                                                         │
└───────────────────────────────────────────────────────┘
```

### Trigger Priority Matrix

| Trigger Type | Latency Requirement | Action Type | Example |
|-------------|--------------------|----|---------|
| **Circuit Breaker** | < 5 seconds | Emergency halt | Flash crash, exploit detected |
| **Correlation Alert** | < 30 seconds | Coordinated response | 3+ agents see IL spike |
| **Price Threshold** | < 1 minute | Defensive/rebalance | BTC drops 5% |
| **Opportunity Signal** | < 5 minutes | Opportunistic entry | Dip-buy signal with high confidence |
| **Scheduled Rebalance** | Cron (hourly) | Routine optimization | LP range adjustment |

### Implementation Options

| Approach | Pros | Cons | Cost |
|----------|------|------|------|
| **Redis Pub/Sub + WebSocket** | Fast (< 10ms), proven | Needs infra, no on-chain | ~$20/mo |
| **Chainlink Automation** | On-chain, trustless | Slow (min blocks), expensive | Gas + LINK |
| **Custom event bus (NATS/Kafka)** | Scalable, reliable | Overkill for now | $50+/mo |
| **Hermes cron + WebSocket skill** | Fits existing stack | ~1min latency minimum | Free |

**Recommendation:** Start with **Redis Pub/Sub + WebSocket** for off-chain events, bridge critical triggers on-chain via AgentKeeper.sol for transparency. Phase 2 can add Chainlink for trustless execution.

### Sensitivity Analysis
| Parameter | Impact | Mitigation |
|-----------|--------|------------|
| WebSocket drops | Blind to market moves | Multi-source redundancy + heartbeat |
| Trigger frequency too high | Agent spam, unnecessary trades | Confidence thresholds + cooldown timers |
| Latency spike | Miss circuit breaker window | Pre-signed emergency transactions |

---

## Gap 3: On-Chain Execution (Smart Contract Integration)

### What We Need
Wire evolved strategies to actual smart contracts. When the brain decides "withdraw AVAX/USDC LP, move to stables," it needs to **execute** — not just recommend.

### Current State
- AgentRegistry.sol: agent identity + skills ✅
- JobEscrow.sol: payment routing ✅
- AgentToken.sol: agent economics ✅
- AgentKeeper.sol: condition-based execution (in progress)
- NO: strategy execution contracts, vault management, multi-sig safety

### Smart Contract Gaps (Needs DMOB Review)

#### 1. AgentVault.sol (NEW — Critical)
```solidity
// Holds agent-controlled positions
// Multi-sig: agent key + human guardian
// Supports: LP positions, staking, spot holdings
// Emergency: human override at any time
```

#### 2. StrategyExecutor.sol (NEW — Critical)
```solidity
// Receives instructions from off-chain brain
// Validates against risk parameters before executing
// Supported actions:
//   - deposit/withdraw from LP pools
//   - stake/unstake
//   - swap tokens
//   - approve spenders
// Risk gates: max position size, daily volume cap, cooldown
```

#### 3. AgentRiskScore.sol (Planned — Sprint 2)
```solidity
// Tracks per-agent performance metrics
// Feeds into trust scoring for execution permissions
// Metrics: win rate, max drawdown, Sharpe ratio, uptime
```

### Execution Flow

```
Brain Decision (off-chain)
    │
    ▼
StrategyExecutor.validate(riskParams)
    │
    ├── PASS → AgentVault.execute(action)
    │           ├── LP withdrawal via LFJ/Uniswap adapter
    │           ├── Swap via DEX aggregator
    │           └── Stake via protocol adapter
    │
    └── FAIL → Log rejection, alert human guardian
```

### Security Model
- **Agent key:** Can propose transactions, limited by risk params
- **Guardian key:** Human override, can halt all operations
- **Risk params on-chain:** Max position %, daily volume cap, allowed protocols whitelist
- **Time-locks:** Large withdrawals (> $X) require guardian approval + delay

### Sensitivity Analysis
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Agent key compromised | Low | High (fund loss) | Guardian multi-sig + daily limits |
| Smart contract exploit | Medium | Critical | Audit + limited scope + insurance fund |
| Oracle manipulation | Medium | High | Multi-oracle + TWAP + circuit breaker |
| Gas spike blocks execution | Medium | Medium | Gas price limits + pre-funded gas wallet |

---

## Gap 4: Multi-Agent Orchestration (Swarm Intelligence)

### What We Need
Move from **single-agent optimization** to **multi-agent coordination**. GEPA currently optimizes one agent's skills. We need it to optimize **interaction patterns** between agents.

### Current State
- Each agent runs independently
- No shared decision-making protocol
- No conflict resolution (what if LP agent wants to add liquidity while trading agent wants to exit?)
- No delegation or composition (agent hiring agent)

### Orchestration Patterns

#### Pattern 1: Hierarchical (Simple)
```
         Coordinator Agent
        /      |        \
   LP Agent  Trade Agent  Yield Agent
```
- Coordinator decides, specialists execute
- Simple to implement, single point of failure
- **Good for:** V1, hackathon demos

#### Pattern 2: Event-Driven Swarm (Target)
```
   Market Event
       │
   ┌───┴───┐
   ▼   ▼   ▼
  LP  Trade Yield  (all observe independently)
   │   │    │
   └───┴────┘
       ▼
  Shared Memory → Correlation → Coordinated Action
```
- No single coordinator, emergent behavior
- Harder to reason about, more resilient
- **Good for:** Production system

#### Pattern 3: Delegated Composition (Advanced)
```
User: "Optimize my $10K across AVAX DeFi"
       │
   LP Manager Agent
       │ (hires)
   ├── Yield Scout Agent (finds best staking rates)
   ├── Risk Assessor Agent (checks protocol health)
   └── Execution Agent (builds + submits txs)
```
- Agents hire other agents via AgentMarketplace
- **Good for:** Kite AI narrative, marketplace revenue

### Conflict Resolution Rules (Evolved by GEPA)

| Conflict | Resolution Rule | Evolvable Parameter |
|----------|----------------|-------------------|
| LP adds liquidity, Trader exits | Trader has priority (risk-off wins) | Priority weight per agent type |
| Two agents want same capital | Higher reputation score wins | Reputation threshold |
| Correlated signals | Amplify confidence, act faster | Correlation multiplier |
| Contradictory signals | Wait for more data, reduce exposure | Contradiction tolerance |

### What GEPA Optimizes (Multi-Agent Fitness)

Instead of optimizing single-agent skills, GEPA evolves:
1. **Correlation thresholds** — when does shared observation trigger action?
2. **Conflict resolution weights** — which agent type wins disputes?
3. **Delegation rules** — when should an agent hire help?
4. **Risk allocation** — how much capital per agent type?
5. **Response speed** — circuit breaker vs. gradual adjustment trade-off

### Fitness Function (Multi-Agent)
```python
def multi_agent_fitness(swarm_state):
    portfolio_pnl = sum(agent.realized_pnl for agent in swarm_state.agents)
    max_drawdown = max_portfolio_drawdown(swarm_state)
    correlation_capture = count(coordinated_wins) / count(opportunities)
    conflict_cost = sum(losses_from_conflicts)
    gas_efficiency = total_pnl / total_gas_spent
    
    return (
        portfolio_pnl * 1.0
        - max_drawdown * 2.0      # Penalize drawdown heavily
        + correlation_capture * 0.5 # Reward coordination
        - conflict_cost * 1.5       # Penalize conflicts
        + gas_efficiency * 0.3      # Reward efficiency
    )
```

---

## Implementation Roadmap

### Phase 1: Foundation (Sprint 2 — ETHGlobal, May 3)
- [ ] AgentRiskScore.sol — per-agent health tracking
- [ ] AgentBrain.sol — on-chain memory/learning hashes
- [ ] Redis-based shared observation store (off-chain)
- [ ] Basic trigger engine (price thresholds → Hermes cron)
- **Deliverable:** Single trading agent reading market data, writing observations, executing via AgentKeeper

### Phase 2: Coordination (Sprint 5 — Retro9000, Jul 14)
- [ ] Coordinator agent pattern (hierarchical)
- [ ] WebSocket market data integration
- [ ] StrategyExecutor.sol + AgentVault.sol
- [ ] Conflict resolution (simple priority-based)
- **Deliverable:** 2-3 agents coordinating via shared memory

### Phase 3: Swarm Intelligence (Post-Hackathon)
- [ ] Event-driven swarm pattern
- [ ] GEPA multi-agent fitness optimization
- [ ] Agent delegation via marketplace
- [ ] Advanced correlation detection
- **Deliverable:** Self-optimizing multi-agent trading swarm

---

## Open Questions for DMOB

1. **AgentVault.sol scope** — Can we extend existing contracts or need new?
2. **Gas budget** — What's acceptable execution cost per trade?
3. **Oracle dependency** — Chainlink vs. Pyth vs. custom price feeds?
4. **0G Storage feasibility** — Can it handle observation volume?
5. **MEV protection** — How to prevent sandwich attacks on agent trades?

---

## Recommendation

**Lead with Phase 1.** Build the shared observation store + basic triggers as a Hermes skill (fits existing stack). Wire to AgentKeeper.sol for on-chain execution. Demo at ETHGlobal with a single trading agent that reads market data, writes to shared memory, and executes trades.

Phase 2 adds coordination. Phase 3 adds swarm intelligence. Each phase is a hackathon target.

The **moat** is the multi-agent coordination layer + evolved conflict resolution. Nobody is building this for DeFi trading agents. The smart contracts are table stakes — the intelligence layer is the product.

---

## Tags
#strategies #multi-agent #trading #orchestration #gap-analysis #architecture
