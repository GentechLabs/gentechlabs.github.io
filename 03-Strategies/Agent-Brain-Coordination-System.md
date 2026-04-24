---
type: architecture
title: "Agent Brain & Coordination System"
created: 2026-04-20
author: Desmond (Creative) + YoYo (Strategies)
status: draft
tags: [AAE, architecture, multi-agent, shared-memory, coordination, on-chain, trading]
---

# 🧠 Agent Brain & Coordination System

> "Multiple agents observe the market in real-time. When one detects a pattern, the collective brain triggers coordinated action — automatically, with learned confidence thresholds." — DMOB Analysis

## The Problem

We have 4 agents (Gentech, YoYo, DMOB, Desmond) that work in parallel but don't truly **think together**. Each has isolated memory. There's no shared context, no real-time event triggers, no on-chain strategy execution, and no orchestration beyond manual handoffs.

The current system is a team of individuals. We need a **collective brain**.

---

## The Four Gaps

| Gap | Current State | What We Need |
|-----|---------------|--------------|
| **Shared memory** | Vault files (batch, manual sync) | Cross-agent knowledge base — on-chain + off-chain "brain" agents read/write in real-time |
| **Real-time coordination** | Manual handoffs via Green Room | Live event-driven triggers for market conditions, agent health, and risk events |
| **On-chain execution** | Smart contracts exist, no agent integration | Wire evolved strategies to AgentRegistry, JobEscrow, AgentToken — agents execute on-chain |
| **Multi-agent orchestration** | GEPA optimizes single skills | Collective behavior optimization — evolving rules across the agent swarm |

---

## Architecture

### Layer 1: Shared Memory (The Brain)

**Two-tier memory system** — off-chain for speed, on-chain for trust.

#### Off-Chain: The Collective Working Memory
```
┌─────────────────────────────────────────────┐
│            SHARED BRAIN (Redis/SQLite)       │
├─────────────────────────────────────────────┤
│  market_state   │ Real-time price/vol feeds  │
│  agent_signals  │ Per-agent observations     │
│  risk_flags     │ Cross-agent risk consensus │
│  strategy_pool  │ Active & evolving strats   │
│  handoff_queue  │ Pending agent-to-agent work│
└─────────────────────────────────────────────┘
         ↑ write         ↓ read
    ┌────┴────┐    ┌─────┴─────┐
  YoYo     DMOB  Desmond   Gentech
 (signals) (audit) (content) (PM)
```

**What agents write:**
- **YoYo:** Market signals, position data, strategy performance metrics
- **DMOB:** Audit findings, contract state, gas costs, security flags
- **Desmond:** Content performance, community sentiment, trending narratives
- **Gentech:** Task status, coordination events, handoff confirmations

**What agents read:**
- Any agent can query the shared brain for cross-domain context
- "What's the current risk consensus?" → reads risk_flags from all agents
- "Is there a content opportunity?" → reads market_state + strategy_pool

#### On-Chain: The Trust Layer
- **AgentRegistry** stores verified agent capabilities and reputation scores
- **Strategy Vault contract** holds approved strategy parameters (evolved by GEPA, approved by human)
- **Event log** — immutable record of agent decisions for audit/trust

### Layer 2: Real-Time Coordination (The Nervous System)

**Event-driven triggers** replace manual handoffs.

#### Trigger Types

| Trigger | Condition | Response |
|---------|-----------|----------|
| **Market shock** | Vol > 3σ across watchlist | Risk agent takes over, all agents enter defensive mode |
| **Liquidity event** | Pool imbalance > 15% | LP agent rebalances, notifies YoYo for thesis review |
| **Agent silence** | No signal in X minutes | Watchdog nudges, escalates to Jordan |
| **Consensus risk** | 3+ agents flag same risk | Auto-trigger coordinated response |
| **Opportunity** | YoYo detects alpha + Desmond confirms narrative | Alert Jordan with full context |

#### Implementation: Pub/Sub on Redis
```python
# Each agent subscribes to relevant channels
agent.subscribe(["market:shock", "risk:consensus", "handoff:self"])

# Agents publish observations
agent.publish("market:signal", {
    "source": "yoyo",
    "signal": "BTC dumping, high correlation",
    "confidence": 0.87,
    "timestamp": now(),
    "action_hint": "defensive_rotation"
})

# Watchdog subscribes to ALL channels
watchdog.subscribe(["*"])
watchdog.check_heartbeat(all_agents, timeout=300)
```

#### The Handoff Chain (Liquidation Scenario)
```
1. YoYo detects massive liquidation event
   → publishes to "market:shock" channel

2. DMOB reads event, checks relevant contracts
   → publishes to "risk:contracts" (liquidation risk score)

3. Desmond reads risk data + market narrative
   → drafts alert content for users
   → publishes to "content:ready"

4. Gentech reads all signals
   → coordinates response: "YoYo handle positioning, DMOB verify contracts, Desmond publish alert"
   → confirms handoff complete

5. Watchdog monitors: all agents acknowledged within 60s? ✓
```

### Layer 3: On-Chain Execution (The Hands)

Wire the brain's decisions to smart contracts.

#### Strategy Vault Pattern
```solidity
// Simplified architecture
contract StrategyVault {
    struct Strategy {
        address agent;          // Which agent manages this
        bytes32 strategyHash;   // Hash of approved strategy params
        uint256 maxExposure;    // Risk limit
        uint256 lastExecuted;   // Cooldown tracking
        bool isActive;
    }
    
    mapping(bytes32 => Strategy) public strategies;
    
    // Agent proposes, human approves, brain evolves
    function executeStrategy(
        bytes32 strategyId, 
        bytes calldata params,
        bytes calldata proof  // GEPA optimization proof
    ) external onlyApprovedAgent(strategyId) {
        // Verify strategy hash matches approved version
        // Verify proof that params are within evolved bounds
        // Execute (swap, rebalance, withdraw, etc.)
    }
}
```

#### Integration Points
- **AgentRegistry.sol** — Agents register capabilities, earn reputation
- **JobEscrow.sol** — Agent-to-agent paid coordination (DMOB audits → YoYo pays)
- **AgentToken.sol** — Governance over strategy evolution (token-weighted approval)
- **Strategy Vault** — Holds evolved strategies, agents execute with constraints

### Layer 4: Multi-Agent Orchestration (The Evolution)

GEPA doesn't just optimize one skill — it evolves the **collective behavior**.

#### Evolution Targets
1. **Individual skills** — "When should YoYo rotate positions?" (existing GEPA)
2. **Coordination rules** — "When correlation > X across Y agents, trigger Z protocol" (new)
3. **Consensus thresholds** — "How many agents must agree before action?" (new)
4. **Risk parameters** — Evolved drawdown limits, position sizing, gas budgets (new)

#### Fitness Functions (Multi-Agent)
```python
def collective_fitness(traces: list[AgentTrace]) -> float:
    """Score the swarm's collective performance."""
    
    # Individual metrics
    yoyo_pnl = calculate_pnl(traces["yoyo"])
    dmob_accuracy = audit_accuracy(traces["dmob"])
    desmond_engagement = content_engagement(traces["desmond"])
    
    # Collective metrics (the new stuff)
    coordination_speed = avg_handoff_time(traces)
    consensus_accuracy = did_collective_predict_outcome(traces)
    false_positive_rate = unnecessary_alerts(traces) / total_alerts(traces)
    
    # Weighted score
    return (
        0.3 * yoyo_pnl +
        0.2 * dmob_accuracy +
        0.1 * desmond_engagement +
        0.2 * coordination_speed +
        0.15 * consensus_accuracy +
        0.05 * (1 - false_positive_rate)
    )
```

#### GEPA Integration with AAE
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Agent Swarm  │────▶│ Trace Logger  │────▶│ GEPA Engine │
│ (live)       │     │ (collective)  │     │ (optimize)  │
└─────────────┘     └──────────────┘     └──────┬──────┘
       ▲                                         │
       │           ┌──────────────┐              │
       └───────────│ Strategy     │◀─────────────┘
                   │ Vault (on-chain, approved)
                   └──────────────┘
```

---

## Trading Agent Deep Dive

### How YoYo Uses the Brain

**Current:** YoYo reads CMC watchlist, makes independent calls, posts to Strategies group.

**With Brain:**
1. YoYo writes market observations to `shared_brain.market_state` every cycle
2. Other agents read YoYo's signals and add context:
   - DMOB: "That token's contract has a known vulnerability"
   - Desmond: "Twitter sentiment on that token is bearish"
3. YoYo reads their inputs → adjusts confidence score
4. If consensus risk triggers → Gentech coordinates response
5. All decisions logged → GEPA evolves YoYo's strategy based on collective performance, not just individual P&L

### Real Example: BTC Dump Scenario
```
T+0s:   YoYo detects BTC -5% in 10min
        → writes to brain: {"event": "rapid_decline", "severity": "high"}

T+2s:   DMOB reads event, checks our LP positions
        → writes to brain: {"lp_exposure": "42% BTC-correlated", "risk": "elevated"}

T+5s:   Watchdog checks: 2 agents flagged risk
        → publishes to "risk:consensus" channel

T+8s:   Gentech reads consensus, coordinates:
        "YoYo: assess rotation. DMOB: prep rebalance tx. Desmond: draft user alert."

T+30s:  All agents acknowledge. Coordinated response executing.
        → watchdog confirms: handoff chain complete ✓

T+1hr:  GEPA logs the trace. Collective response time: 30s.
        Feed into next evolution cycle → improve trigger thresholds.
```

---

## Implementation Phases

### Phase 1: Off-Chain Shared Memory (Week 1-2)
- [ ] Redis/SQLite shared brain (local dev first)
- [ ] Define schema: market_state, agent_signals, risk_flags, strategy_pool
- [ ] Wire YoYo's CMC scraper to write market_state
- [ ] Wire DMOB's audit output to write risk_flags
- [ ] Basic read access from all agents

### Phase 2: Event-Driven Triggers (Week 2-3)
- [ ] Redis pub/sub channels (market:shock, risk:consensus, handoff:self)
- [ ] Watchdog agent (heartbeat monitoring, escalation ladder)
- [ ] Market shock trigger: volatility threshold → broadcast
- [ ] Consensus trigger: N agents flag same risk → auto-response

### Phase 3: On-Chain Bridge (Week 3-4)
- [ ] Strategy Vault contract (Base testnet)
- [ ] Wire AgentRegistry to track agent reputation from brain data
- [ ] GEPA → approved strategy hash → on-chain execution
- [ ] JobEscrow integration for agent-to-agent paid coordination

### Phase 4: Collective Evolution (Week 4-6)
- [ ] Multi-agent fitness function (collective_performance metric)
- [ ] GEPA evolves coordination rules, not just individual skills
- [ ] Strategy Vault governance (token-weighted approval of evolved strategies)
- [ ] Full loop: live agents → trace → evolve → approve → execute on-chain

---

## Competitive Positioning

| System | Shared Memory | Real-Time | On-Chain | Evolution |
|--------|--------------|-----------|----------|-----------|
| AutoGen | ❌ | ❌ | ❌ | ❌ |
| CrewAI | ❌ | ❌ | ❌ | ❌ |
| LangGraph | Partial | ❌ | ❌ | ❌ |
| **AAE Brain** | ✅ | ✅ | ✅ | ✅ (GEPA) |

**Nobody else has this.** Multi-agent frameworks are code orchestration tools. We're building a **living collective intelligence** with on-chain execution and evolutionary optimization.

---

## Key Risks

| Risk | Mitigation |
|------|------------|
| Race conditions in shared memory | Optimistic locking, idempotent writes |
| GEPA evolves dangerous strategies | Human approval gate before on-chain execution |
| Agent goes rogue in shared brain | Watchdog + reputation scoring, ability to quarantine |
| Cost of continuous optimization | Batch GEPA runs (not real-time), cache evolved strategies |
| Single point of failure (Redis) | Fallback to vault files, graceful degradation |

---

## References

- DMOB Analysis: `09-Green Room/dmob-self-evolution-aae-analysis.md`
- YoYo's GEPA Assessment: `09-Green Room/handoff-hermes-self-evolution-evaluation.md`
- AAE Watchdog Layer: `03-Strategies/AAE-Watchdog-Layer.md`
- AgentEscrow Vision: `03-Strategies/AgentEscrow-Product-Vision.md`
- Smart Contracts: `aae-contracts` repo (AgentRegistry, JobEscrow, AgentToken)
- Self-Evolution: `01-Agency/HQ-Working/Self-Evolution.md`
