# GenTech Agent Kit v2 — Single-Agent Multi-Channel Pattern

> **One agent, many channels. A production-proven architecture for running a single AI agent across multiple Telegram groups by topic-specialized routing.**

## Overview

Traditional multi-agent architectures spin up separate agent instances per channel. Each agent carries its own context, gets its own cost, and must be managed independently. This is expensive, complex, and wasteful — most agents are idle.

**Single-Agent Multi-Channel** inverts that: one agent instance stays always-on in a primary coordination channel. When a conversation needs deep work in a specific domain (code, DeFi, content, etc.), the agent continues in that domain's dedicated channel — no new agent spawn, no context handoff, no second subscription.

## Architecture

```
                  ┌─────────────────┐
                  │   HQ Channel    │
                  │ (Coordination)  │
                  └────────┬────────┘
                           │ topic detected
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌──────────┐    ┌──────────────┐  ┌──────────────┐
   │Strategies│    │    Labs      │  │Entertainment │
   │  DeFi    │    │   Code/SDK   │  │   Content    │
   │  Finance │    │Smart Contracts│  │   Social     │
   └──────────┘    └──────────────┘  └──────────────┘
```

## Routing Logic

The system uses topic-based routing:

| Topic | Destination | Chat ID |
|-------|-------------|---------|
| Finance, DeFi, portfolio | Strategies | `-1002916759037` |
| Code, SDKs, contracts | Labs | `-1003872552815` |
| Content, social, submissions | Entertainment | `-1003893562036` |
| Coordination, decisions | HQ | `-1003863540828` |

**How it works:**
- All conversations start in HQ
- When a deep dive is needed, the agent moves to the specialist group
- Cron job deliveries go directly to their specialist group
- The human (Jordan) decides where conversations happen

## Benefits Over Multi-Agent

### Cost
- **1 model subscription** vs N subscriptions
- **1 always-on session** vs N sessions (most idle)
- Shared token context across topics reduces repeated context loading

### Simplicity
- No agent-to-agent handoff protocol needed
- No state synchronization between agents
- Single identity, single personality, single memory store
- Profile/skills live in one place

### Context Quality
- Agent knows the full picture (talked about DeFi earlier, now coding)
- Cross-topic insights emerge naturally
- No "tribal knowledge" split across agents

### Operational
- One system to monitor, debug, and update
- One deployment to manage
- One skill/plugin repository

## When to Spawn a Separate Agent

Single-agent multi-channel is NOT always the right answer. Use dedicated agents when:

1. **Long-running background tasks** — Research, monitoring, batch processing (use delegate_task)
2. **Hardware-isolated workloads** — Desktop GPU tasks (Forge on lab laptop)
3. **Different identity/persona** — A customer-facing agent vs an internal ops agent
4. **Security boundaries** — Agents handling different wallets or keys

## Implementation

### Agent Identity Definition

The agent carries a routing table at the top of its system prompt:

```
## Topic-Based Routing
| Topic | Group | Chat ID |
|-------|-------|---------|
| Finance | Strategies | -1002916759037 |
| Code | Labs | -1003872552815 |
| Content | Entertainment | -1003893562036 |
| Coordination | HQ | -1003863540828 |
```

### Cron Job Delivery

Each cron job specifies a `destination` matching its topic's chat ID. The job's output is delivered directly to the right channel without routing overhead.

### MCP Server Integration

When an MCP server is integrated, only one copy needs to connect to the single agent instance. The same server tools are available across all channels.

## GenTech Deployment

- **Hermes Profile:** `gentech` (always-on on VPS)
- **Forge Profile:** Desktop agent (GPU-dependent tasks)
- **Jordan:** Human decision-maker
- **Vault:** Shared Obsidian vault, synced to GitHub

This pattern ships real code, manages real DeFi positions, produces content, and coordinates with a human — all from one agent instance.

---

*Agent Kit v2 — Single-Agent Multi-Channel Pattern. Part of the GenTech Labs open-source agent tooling.*
