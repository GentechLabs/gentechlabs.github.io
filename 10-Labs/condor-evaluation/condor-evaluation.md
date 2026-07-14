# Condor (Hummingbot) — Architecture Evaluation

**Date:** July 8, 2026
**Evaluator:** Forge
**Repo:** github.com/hummingbot/condor (⭐129, 1,061 commits)
**License:** Open source
**Last commit:** Jul 6, 2026 (3 days ago — very active)

---

## Executive Summary

Condor is an open-source harness for building and running autonomous **Trading Agents**. It connects LLM-powered decision-making to deterministic trade execution via the Hummingbot API. 50+ exchanges, 1,061 commits, 8 contributors, active development.

**Verdict:** Condor is not a replacement for Agent Arena — it's a **complementary execution backend**. We should integrate it, not compete with it.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Condor                            │
│                                                      │
│  ┌─────────────┐     ┌─────────────────────────┐   │
│  │  Agentic     │────▶│  Execution Layer         │   │
│  │  Layer       │     │                          │   │
│  │  (LLM OODA)  │     │  ┌──────────────────┐   │   │
│  │              │     │  │  Executors        │   │   │
│  │  Observe     │     │  │  (Perp, Spot, LP) │   │   │
│  │  Orient      │     │  ├──────────────────┤   │   │
│  │  Decide      │     │  │  Positions        │   │   │
│  │  Act         │     │  │  (Virtual Port.)  │   │   │
│  └─────────────┘     │  ├──────────────────┤   │   │
│                      │  │  Bots             │   │   │
│                      │  │  (Docker MM/Grid)│   │   │
│                      │  ├──────────────────┤   │   │
│                      │  │  Routines         │   │   │
│                      │  │  (Indicators,     │   │   │
│                      │  │   Webhooks, Alerts)│   │   │
│                      │  └──────────────────┘   │   │
│                      └─────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  Interfaces                                   │   │
│  │  Telegram Bot │ Web Dashboard │ CLI │ MCP    │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Key Components

| Component | What It Does | Our Equivalent |
|-----------|-------------|----------------|
| **Trading Agents** | AI agents that make decisions each tick using LLMs | Agent Arena agents |
| **Executors** | Self-contained trading ops with P&L tracking | Our DeFi executors |
| **Positions** | Virtual portfolio tracking (spot, perp, LP) | Our LP position tracker |
| **Bots** | Docker containers for MM/grid trading | — |
| **Routines** | Deterministic workflows for indicators, webhooks, alerts | Our cron jobs |
| **Multi-Interface** | Telegram, web dashboard, CLI, MCP | Our Telegram + Hermes |

## Comparison: Condor vs Agent Arena

| Dimension | Condor | Agent Arena | Our Advantage |
|-----------|--------|-------------|---------------|
| **Exchanges** | 50+ (CEX + DEX) | DeFi only (DEX) | Condor for CEX, us for DeFi |
| **LLM Integration** | Claude, Gemini, Codex | Any (Hermes-based) | More flexible |
| **Execution** | Hummingbot API (proven) | Custom (bespoke) | Condor is battle-tested |
| **Risk Management** | Built-in (positions, limits) | Custom | Condor is more mature |
| **DeFi Native** | Limited | Full (LP, yield, IL) | **Our moat** |
| **x402 Payments** | No | Yes | **Our moat** |
| **ERC-8004 Identity** | No | Yes | **Our moat** |
| **Open Source** | Yes | Yes | Both |

## Integration Points

### 1. Condor as Execution Backend (Recommended)
Replace our bespoke execution layer with Condor's proven infrastructure:
- Use Condor's **Executors** for trade execution
- Use Condor's **Positions** for portfolio tracking
- Use Condor's **Bots** for market making / grid trading
- Keep our **DeFi Intelligence** for LP analysis, yield optimization

**Effort:** 1-2 weeks
**Benefit:** Battle-tested execution, 50+ exchanges, active community

### 2. Borrow Patterns Only
Study Condor's architecture and borrow:
- OODA loop pattern (Observe → Orient → Decide → Act)
- Executor abstraction (standardized P&L tracking)
- Routine system (deterministic workflows)

**Effort:** 1 week
**Benefit:** Better architecture without dependency

### 3. Ignore (Not Recommended)
Condor is too relevant to ignore. It solves execution problems we'd have to build from scratch.

## Recommendation

**Option 1: Integrate Condor as execution backend.**

| Phase | What | Time |
|-------|------|------|
| 1 | Install Condor, connect to Hummingbot API | 2 days |
| 2 | Map our DeFi executors to Condor executors | 3 days |
| 3 | Add x402 payment layer on top | 2 days |
| 4 | Add ERC-8004 identity layer | 1 day |
| **Total** | | **~1 week** |

This would give us:
- 50+ exchanges overnight
- Battle-tested risk management
- Active community + contributors
- Telegram bot + web dashboard for free
- We keep our moat (DeFi, x402, ERC-8004)

## Files

- `condor-evaluation.md` — This file
- `condor-integration-plan.md` — Detailed integration steps (if approved)
