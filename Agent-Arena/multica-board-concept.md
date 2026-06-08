# Multica Board — AAE Prototype Dashboard

**Date:** May 26, 2026
**Status:** 🟡 Concept + Prototype
**Purpose:** Multi-agent dashboard for development + token acquisition agent

---

## What Is It

A visual control panel for managing multiple AI agents across chains. Think of it as:
- **Development tool:** Test agent orchestration before going live
- **Token acquisition agent:** Buy specific tokens at target prices (DCA/limit)
- **AAE prototype:** The four-agent stack you can actually interact with

## Why It Matters

1. **Brings multi-agent strategy back** — we've been building agents in isolation. This unifies them.
2. **Development environment** — test agent communication, handoffs, governance in a safe sandbox
3. **Token acquisition** — a practical agent that buys tokens at certain prices (immediate value)
4. **AAE showcase** — when hackathon judges see this, they see the vision

## The Four Agents (from AAE spec)

```
┌─────────────────────────────────────────────────────────┐
│  📊 ANALYST ("The Eyes")                                │
│  Market regime detection, on-chain flow tracking        │
│  Feeds signals → Strategy Brain                         │
├─────────────────────────────────────────────────────────┤
│  🧠 STRATEGY BRAIN ("The Brain")                        │
│  Allocation decisions, risk management                  │
│  Receives signals → Approved orders to Validator        │
├─────────────────────────────────────────────────────────┤
│  ✅ VALIDATOR ("The Safety Net")                        │
│  Reviews every decision BEFORE execution                │
│  Risk checks, position sizing → Validated orders        │
├─────────────────────────────────────────────────────────┤
│  ⚡ EXECUTOR ("The Hands")                              │
│  Pure on-chain execution, NO decision-making            │
│  Swaps, LP management, staking → Results back           │
└─────────────────────────────────────────────────────────┘
```

## Token Acquisition Agent (New)

A focused agent for buying tokens at target prices:

| Feature | Description |
|---------|-------------|
| **DCA Mode** | Buy $X of token Y every N hours |
| **Limit Orders** | Buy when price hits target |
| **Multi-chain** | Solana, Base, Avalanche |
| **Governance** | AGT policy wraps every trade |
| **Budget Cap** | Max spend per day/week/month |

### Use Cases
- Accumulate AVAX at $25 for LP positions
- DCA into SOL for Agent Arena starting capital
- Buy the dip on tokens we're building with (SOMNIA, etc.)

## Dashboard Features

### Development Mode
- Agent status (idle, thinking, executing, error)
- Communication flow visualization (who's talking to whom)
- Policy check results (allowed/denied + reason)
- Audit log viewer

### Production Mode
- Portfolio overview across chains
- Token balances + positions
- Agent performance metrics
- Governance alerts

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML/CSS/JS (static, GitHub Pages) |
| Agent Runtime | Hermes Agent (Python) |
| Governance | Microsoft AGT (policy engine) |
| Blockchain | Solana (RPC), Base (Alchemy), Avalanche (RPC) |
| Storage | SQLite (agent state), JSON (config) |

## Integration Points

1. **AGT Governance** — every agent action wrapped with `govern()`
2. **Hermes Agent** — agents run as Hermes profiles or subagents
3. **x402 Payments** — micropayments for agent services
4. **Agent Arena** — this IS the AAE prototype

## Roadmap

### Phase 1: Static Dashboard (This Week)
- HTML dashboard showing four agents + status
- Simulated communication flow
- Portfolio overview

### Phase 2: Live Agent Connection (Next Week)
- Connect to real Hermes agents
- Live portfolio data from on-chain
- Governance audit log viewer

### Phase 3: Token Acquisition Agent (June)
- DCA mode: buy tokens on schedule
- Limit orders: buy at target prices
- Multi-chain support

### Phase 4: AAE Integration (July)
- Full four-agent stack
- Market regime simulation
- Reputation system

---

*The Multica Board is AAE made visible. Build the dashboard, build the agents, build the game.*
