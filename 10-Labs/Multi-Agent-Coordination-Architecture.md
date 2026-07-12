# Multi-Agent Coordination Architecture

**Created:** 2026-04-20
**Author:** DMOB (Labs)
**Status:** Active Development
**Collaborators:** YoYo (trading agent design)

## Problem Statement

The current AAE architecture has 5 implemented layers (Foundation: AgentRegistry, JobEscrow, Marketplace, AgentToken) but lacks:

1. **Shared Memory** — No cross-agent knowledge base. Agents operate in isolation.
2. **Real-Time Coordination** — GEPA is batch/offline. No live event-driven triggers.
3. **On-Chain Execution** — No bridge between evolved strategies and smart contracts.
4. **Multi-Agent Orchestration** — Current system optimizes single agents, not coordinated behavior.

## Design Principles

- **Security first** — every external call is a potential exploit
- **Checks-effects-interactions** — no exceptions
- **OpenZeppelin base contracts** always
- **Pull-over-push** for payments
- **On-chain state for trust/audit, off-chain relay for speed**

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    Off-Chain Layer (Hermes Agents)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ Trading  │  │  Yield   │  │ Staking  │  │  GEPA Engine │    │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  (evolution) │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘    │
│       │              │              │               │            │
│  ┌────▼──────────────▼──────────────▼───────────────▼───────┐   │
│  │              EventRouter (off-chain relay)                │   │
│  │         Watches on-chain events, dispatches to agents     │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────┼──────────────────────────────────────┘
                            │ ABI calls
┌───────────────────────────┼──────────────────────────────────────┐
│                    On-Chain Layer (Base / Avalanche)             │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │              AgentCoordinator.sol                         │   │
│  │    Multi-agent task dispatch, confidence thresholds,      │   │
│  │    circuit breakers, exposure caps                        │   │
│  ├───────────────────────────────────────────────────────────┤   │
│  │              SharedMemory.sol                             │   │
│  │    Cross-agent signals, market observations, strategy     │   │
│  │    state — write by registered agents, read by all        │   │
│  ├───────────────────────────────────────────────────────────┤   │
│  │              StrategyVault.sol                            │   │
│  │    Evolved strategy parameters (GEPA output), versioned,  │   │
│  │    with performance tracking and rollback capability      │   │
│  ├───────────────────────────────────────────────────────────┤   │
│  │              AgentRegistry.sol ✅ (existing)               │   │
│  │              JobEscrow.sol ✅ (existing)                   │   │
│  └───────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Contract Specifications

### 1. SharedMemory.sol

**Purpose:** Cross-agent knowledge base. Agents write observations, signals, and strategy state that other agents can read.

**Key Design:**
- Registered agents only can write
- Signal types: MARKET_OBSERVATION, RISK_ALERT, STRATEGY_UPDATE, COORDINATION_REQUEST
- TTL (time-to-live) for signals — auto-expire stale data
- Confidence scores (0-100) for each signal
- Aggregation functions — e.g., "what's the average BTC risk score across all agents?"

**Storage Model:**
```solidity
struct Signal {
    address sender;          // Agent who wrote this
    SignalType signalType;   // MARKET_OBSERVATION | RISK_ALERT | etc.
    bytes32 topic;           // keccak256("BTC_DUMPIG") — machine-readable
    string data;             // JSON payload (IPFS URI for large data)
    uint8 confidence;        // 0-100
    uint256 timestamp;
    uint256 expiresAt;       // TTL
}
```

**Security:**
- Only registered agents (checked via AgentRegistry) can write
- Rate limiting: max N signals per agent per block
- No reentrancy (view-heavy, no external calls in write path)

---

### 2. AgentCoordinator.sol

**Purpose:** Multi-agent orchestration — dispatch coordinated actions based on signals, enforce guardrails.

**Key Design:**
- **Policies:** Define coordination rules (e.g., "if 3+ agents signal RISK_ALERT with confidence > 80, trigger REBALANCE")
- **Circuit Breakers:** Pause all coordinated actions if loss threshold exceeded
- **Exposure Caps:** Per-agent and global max exposure limits
- **Cooldowns:** Minimum time between coordinated actions

**Policy Model:**
```solidity
struct Policy {
    bytes32 id;                    // keccak256 of policy name
    address creator;
    SignalType triggerType;        // What signal triggers this
    bytes32 triggerTopic;          // Which topic to watch
    uint8 minConfidence;           // Minimum avg confidence to trigger
    uint8 minSignalCount;          // Minimum number of agent signals
    address[] targetAgents;        // Agents to dispatch to
    bytes actionData;              // ABI-encoded action to execute
    uint256 cooldown;              // Min seconds between triggers
    uint256 lastTriggered;
    bool isActive;
}
```

**Guardrails:**
```solidity
struct Guardrails {
    uint256 maxExposurePerAgent;   // Max wei at risk per agent
    uint256 maxTotalExposure;      // Max wei at risk globally
    uint256 maxLossThreshold;      // Circuit breaker trips at this loss
    uint256 cooldownPeriod;        // Global cooldown between actions
    uint256 lastActionTimestamp;
    bool isPaused;                 // Emergency pause
}
```

**Execution Flow:**
1. AgentCoordinator.evaluate() — checks SharedMemory for signals matching a policy
2. If thresholds met → dispatches action via JobEscrow.createJob() to target agents
3. Guardrails checked before every dispatch
4. Events emitted for off-chain monitoring

---

### 3. StrategyVault.sol

**Purpose:** Store evolved strategy parameters (GEPA output). Versioned, with performance tracking and rollback.

**Key Design:**
- Strategies are versioned — each evolution produces a new version
- Performance metrics tracked on-chain (PnL, Sharpe, win rate)
- Rollback to previous version if performance degrades
- Strategy parameters hashed for verification (full params off-chain on IPFS/0G)

**Strategy Model:**
```solidity
struct Strategy {
    uint256 id;
    address owner;                 // Agent or human who owns this
    string name;                   // "BTC-Momentum-v3"
    bytes32 paramsHash;            // keccak256 of full params (IPFS URI)
    uint256 version;
    uint256 parentVersion;         // For lineage tracking
    int256 cumulativePnl;          // Signed — can be negative
    uint256 tradesExecuted;
    uint256 winCount;
    uint256 deployedAt;
    bool isActive;
}
```

**Performance Tracking:**
- Called by JobEscrow or AgentCoordinator after each trade
- Updates cumulative PnL, trade count, win rate
- Emits StrategyPerformance event for off-chain analysis

**Rollback Mechanism:**
- Owner can mark a version as "superseded" and activate a previous version
- Emergency rollback by owner if max drawdown exceeded

---

## Off-Chain Components (Hermes Integration)

### EventRouter (Cron/Watcher)

**Responsibilities:**
- Watch on-chain events (SignalWritten, PolicyTriggered, StrategyUpdated)
- Dispatch to appropriate Hermes agents via Telegram/webhook
- Aggregate off-chain data (DexScreener prices, CMC feeds) and write to SharedMemory

**Implementation:**
- Cron job: `event-router` — polls every 30s for new events
- Script: `~/.hermes/scripts/event-router.py` — reads contract events, dispatches to agents

### GEPA Integration (Future)

**Flow:**
1. Trading agent runs strategy, logs results to SharedMemory
2. GEPA reads performance data from StrategyVault
3. GEPA evolves strategy parameters (off-chain, ~$2-10/run)
4. New strategy version deployed to StrategyVault with paramsHash
5. AgentCoordinator can reference new strategy in policies

---

## Integration with Existing Contracts

### AgentRegistry.sol (existing)
- SharedMemory checks `isRegistered[msg.sender]` before allowing writes
- AgentCoordinator validates target agents are registered

### JobEscrow.sol (existing)
- AgentCoordinator creates jobs via JobEscrow for dispatched actions
- Reputation updates flow through existing path

### AgentToken.sol / AgentTokenFactory.sol (existing)
- Future: Strategy performance could influence token economics
- Not in scope for initial coordination layer

---

## Deployment Plan

### Phase 1: SharedMemory (Week 1)
- [ ] Write SharedMemory.sol with signal CRUD
- [ ] Write tests (Foundry)
- [ ] Deploy to Base Sepolia

### Phase 2: AgentCoordinator (Week 2)
- [ ] Write AgentCoordinator.sol with policies + guardrails
- [ ] Integration tests with AgentRegistry + JobEscrow
- [ ] Deploy to Base Sepolia

### Phase 3: StrategyVault (Week 3)
- [ ] Write StrategyVault.sol with versioning + rollback
- [ ] Performance tracking integration
- [ ] Deploy to Base Sepolia

### Phase 4: Off-Chain Integration (Week 4)
- [ ] EventRouter cron job
- [ ] Hermes agent integration
- [ ] GEPA pipeline connection

---

## Security Considerations

1. **Access Control** — Only registered agents can write to SharedMemory
2. **Rate Limiting** — Prevent signal spam (max N per block)
3. **Circuit Breakers** — Emergency pause on AgentCoordinator
4. **Reentrancy** — All state changes before external calls
5. **Oracle Manipulation** — Confidence scores aggregated, no single-agent trust
6. **Strategy Validation** — paramsHash verification before activation

---

## Tags
#AAE #architecture #multi-agent #coordination #smart-contracts #labs
