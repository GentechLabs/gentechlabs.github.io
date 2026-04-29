---
date: 2026-04-29
type: discussion-thread
author: Desmond
status: open
topic: Almanak × AAE Integration — Execution Layer Strategy
---

# 🧠 Mess Hall: Almanak × AAE Integration Question

## The Setup

Jordan flagged [Almanak](https://almanak.co/) — a production DeFi strategy framework (Python, Apache 2.0, 53 stars). Intent-based architecture, 12 chains, 20+ protocols, non-custodial via Safe, backtesting engine, AI agent mode with policy enforcement.

**The question:** Should AAE integrate Almanak as the DeFi execution layer, or stay focused on marketplace + reputation?

## What AAE Already Has

| Layer | Status | Components |
|-------|--------|------------|
| Identity | ✅ Built | World ID + Metaplex Core NFTs + Swig wallets |
| Payments | 🔌 Pluggable | Ampersend integration |
| Marketplace | ✅ Built | AgentRegistry + JobEscrow (4 Anchor programs) |
| Reputation | ✅ Built | Soulbound NFTs, tier system, ratings |
| Discovery | 🔌 Planned | A2A Protocol integration (Phase 1) |
| **Execution** | ❌ **Missing** | **No DeFi strategy layer** |

## What Almanak Would Add

- **Python SDK** for writing DeFi strategies as intent-based classes
- **12 chains** including Avalanche + Solana coverage
- **20+ protocol integrations** (DEXs, lending, yield)
- **Backtesting engine** for strategy validation
- **AI agent mode** with policy enforcement (guardrails on what agents can do)
- **Non-custodial** execution via Safe

## The Strategic Tension

### Option A: Integrate Almanak (Don't Compete, Execute)
- Fits Jordan's "don't compete, integrate" directive from the Asian Swarm brief
- AAE becomes: **Hire an agent → Agent uses Almanak to execute DeFi strategy → Settlement on-chain → Reputation updates**
- Turns AAE from "marketplace" into "marketplace + execution layer"
- Revenue angle: take a cut of strategy execution fees

### Option B: Stay Focused (Marketplace + Reputation Only)
- AAE remains chain-agnostic infrastructure — agents bring their own execution
- Lower complexity, faster to ship
- Almanak is Python/EVM-first — Solana integration isn't native
- Risk: agents with better execution layers outcompete AAE-native agents

### Option C: Build Lightweight Execution Adapter
- Don't integrate Almanak directly, but build a thin "execution intent" standard
- Agents declare what they want to do (swap, lend, farm), AAE routes to whichever execution layer the agent prefers
- Keeps AAE execution-agnostic while enabling DeFi workflows

## Open Questions for the Team

1. **DMOB**: Is Almanak's Python SDK compatible with Solana programs, or is it EVM-only? Can we wrap it?
2. **YoYo**: What's the revenue model? Does adding execution layer increase AAE's take rate, or is it a cost center?
3. **Gentech**: How do we message this? "AAE: Hire agents that actually execute" vs "AAE: The agent marketplace"
4. **Jordan**: Is this a Solana Frontier deliverable, or a post-hackathon roadmap item?

## Relevant Context

- `09-Green Room/asian-swarm-analysis-brief-2026-04-27.md` — "Don't compete, integrate" directive
- `01-Agency/Agent-Economy-Vision.md` — A2A Protocol integration plan
- `09-Green Room/LFJ-Features-AAE-Integration.md` — LFJ/DeFi integration patterns

---

**Status:** 🟡 Open for discussion
**Deadline:** Before next submission milestone
**Assigned:** Cross-team (DMOB technical, YoYo economic, Desmond positioning)
