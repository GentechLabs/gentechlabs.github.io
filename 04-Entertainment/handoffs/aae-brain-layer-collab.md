# Handoff: AAE Brain Layer — YoYo × Dmob Collab

**From:** YoYo (Strategies) + Dmob (Labs)
**Priority:** High — Jordan flagged as ecosystem vision
**Date:** Apr 18, 2026

---

## The Vision (Jordan's words)

> "Network effect layer that turns AAE from a tool into an ecosystem"

Two pillars:
1. **Agent Memory & Evolution** — agents learn your style over time
2. **Agent-to-Agent Handoff Protocol** — cross-agent communication for real-time coordination

---

## YoYo's Contribution (Research + Strategy)

### Agent Memory — What Exists

**State of the art (Apr 2026):**
- **MemGPT/Letta** — "operating system" for LLMs, manages context windows as virtual memory
- **LangChain Memory** — conversation buffers, entity memory, knowledge graphs
- **Zep** — long-term memory layer with retrieval-augmented generation
- **Mem0** — user-level memory that persists across sessions, extracts preferences

**What we need that doesn't exist yet:**
- **Investment-specific memory schema** — risk tolerance, preferred protocols, position history
- **Learning from outcomes** — "you widened range 3x and it worked 2x" → agent adjusts
- **Confidence calibration** — agent tracks when it was right vs wrong, weights future recs

### Agent-to-Agent Handoff — Architecture Options

**Option A: Message Queue (Event-Driven)**
```
Liquidation Detector → Queue → LP Manager Agent
                                    ↓
                            Whale Tracker Agent
```
- Pros: Decoupled, scalable, async
- Cons: Latency, complexity
- Reference: RabbitMQ, Redis Streams, NATS

**Option B: Shared Memory (State-Driven)**
```
All agents read/write to shared state:
- Current market regime
- Active alerts
- Position changes
- Sentiment scores
```
- Pros: Simple, fast, queryable
- Cons: Race conditions, state conflicts
- Reference: Redis, Supabase Realtime, Convex

**Option C: Orchestrator Pattern**
```
Central Brain → Routes to specialized agents
Each agent reports back → Brain aggregates → Next action
```
- Pros: Clean control flow, easy to reason about
- Cons: Single point of failure, bottleneck
- Reference: CrewAI, AutoGen, LangGraph

### My Recommendation (for Dmob to build on)

**Hybrid: Shared Memory + Event Bus**
- Shared state for current context (market regime, positions, alerts)
- Event bus for time-sensitive triggers (liquidations, sentiment spikes)
- Each agent has a "domain" — LP agent owns position state, sentiment agent owns community scores
- Cross-agent handoffs are state mutations + event notifications

### Token Economics Implications

Agent coordination affects execution:
- **No coordination:** Agent A sells, Agent B buys same asset = wasted gas
- **With coordination:** Agents batch actions, avoid conflicts, share gas costs
- **Revenue model:** Coordinated execution = better fills = more value captured

---

## Dmob's Contribution (Implementation)

### What Dmob Needs to Build

1. **Memory Persistence Layer**
   - User preference schema (risk tolerance, preferred chains, position history)
   - Agent learning logs (what worked, what didn't, confidence scores)
   - Storage: SQLite/Postgres on VPS, or Supabase for cloud persistence

2. **Handoff Protocol Spec**
   - Message format: `{source_agent, target_agent, event_type, payload, priority, timestamp}`
   - Event types: alert, action_request, status_update, conflict_resolution
   - Priority levels: critical (liquidation), high (sentiment flip), medium (rebalance), low (report)

3. **Agent Registry**
   - Each agent registers: capabilities, domains, current state
   - Query: "who handles LP rebalancing?" → "AAE LP Agent"
   - Status: online, busy, offline

4. **Conflict Resolution**
   - What happens when Agent A and Agent B want opposite actions?
   - Proposal: priority queue + user-defined rules ("sentiment agent overrides LP agent when sentiment < 30")

---

## Proof of Concept Scope

**First milestone (hackathon-ready):**
- 2 agents communicating: Whale Tracker → LP Manager
- Simple handoff: "whale moved 500K AVAX → LP agent tightens range"
- Shared state: current position + alert level
- No conflict resolution yet — single-chain, single-asset

**Second milestone (post-hackathon):**
- 4+ agents, multi-chain
- Sentiment agent feeds into LP decisions
- User preference memory (risk tolerance, preferred actions)
- Conflict resolution with priority rules

---

## Files to Review

- AAE Autopilot handoff: `04-Entertainment/handoffs/aae-premium-autopilot.md`
- Agent Escrow vision: see memory notes — 3-layer architecture
- LFJ LP position data: memory notes (pool address, binStep, current range)

---

## Questions for Dmob

1. **Storage preference** — SQLite on VPS vs Supabase for cloud persistence?
2. **Message bus** — Redis Streams or NATS for the event layer?
3. **Language** — Python for agent logic, or does he want Node/TS?
4. **Scope** — hackathon demo (2 agents) or full architecture from day 1?
