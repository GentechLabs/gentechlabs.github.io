# GenTech Academy — Product Vision

> **Status:** Draft v1.0 — Greenlit by Jordan (Jul 10, 2026)
> **Owner:** Gentech
> **Pillars:** Agent Development + Crypto/DeFi
> **Source Trigger:** freeCodeCamp AI Agents course → four build ideas → Academy wrapper
> **Tags:** #notebooklm

---

## Core Vision

GenTech Academy teaches people to **build, deploy, and manage AI agents** using the infrastructure we already ship — Agent Kit, x402 payments, ERC-8004 identity, guardrails, and multi-agent patterns.

Crypto/DeFi is one track, not the whole thing. The Academy is a multi-pillar platform.

---

## The Two Tracks

### Track 1: Agent Development

| Tier | Modules | Theme |
|------|---------|-------|
| Scout | 1–3 | Agent fundamentals: LLMs, loops, tools |
| Raider | 4–6 | Building with Agent Kit: MCP, payments, identity |
| Warlord | 7–8 | Production agents: guardrails, HITL, multi-agent |
| Sovereign | 9–10 | Mastery: monetization, marketplace, agent economies |

**Module Draft:**

1. **What Is an AI Agent?** — Agent loops (observe → think → act), tools vs prompts, why agents matter
2. **Structured Outputs & Tool Contracts** — Why schemas matter, MCP protocol, **Output Enforcer** plugin
3. **Agent Identity & Reputation** — ERC-8004 registration, on-chain feedback, portable identity
4. **Payment Rails for Agents** — x402 per-call payments, Q402 gasless USDC, recurring billing, escrow
5. **Building with Agent Kit** — Install, tools, plugins, deployment in 10 minutes
6. **Safe Agent Design** — **Guardrail Plugin**: schema validation, rate limits, content filtering, reputation logging
7. **Agent Personality** — **Personality Framework**: profiles, tone, autonomy levels, ERC-8004 metadata
8. **Human-in-the-Loop** — **HITL Layer**: approval gates, escalation chains, Telegram inline buttons
9. **Multi-Agent Systems** — Handoff protocols, state sharing, loop termination (Gentech ↔ Forge patterns)
10. **Agent Monetization & Marketplaces** — Listing on OKX/Circle/HIVE, revenue tokens, agent-as-RWA

### Track 2: Crypto & DeFi

| Tier | Modules | Theme |
|------|---------|-------|
| Scout | 1–3 | Foundations: wallets, tokens, DEXs |
| Raider | 4–6 | Liquidity provision: shapes, ranges, IL |
| Warlord | 7–8 | Portfolio management, automation |
| Sovereign | 9–10 | Mastery: risk systems, agent integration |

**Module Draft (adapted from PGE-Academy):**

1. What Is Liquidity Provision?
2. Range Shapes — Curve, Spot, Bidirectional
3. Impermanent Loss — The Math That Matters
4. Reading DexScreener — Pool Selection
5. Multi-Shape Strategies
6. Gas Optimization — Timing Your Transactions
7. Portfolio LP — Multi-Pool Management
8. Custom Range Design
9. Risk Management & Position Sizing
10. Building a System — Automation & Compounding

---

## Delivery Formats

| Format | Tool | Use Case |
|--------|------|----------|
| **Audio Overview** | NotebookLM → vault note | Passive learning, commute-friendly |
| **Short Video** | NotebookLM → vault note | Social distribution, hooks |
| **Interactive Module** | Web (static HTML + JS) | Hands-on learning, sandbox simulators |
| **Live Session** | Telegram group | Q&A, cohort-based learning |
| **Build Exercise** | Agent Kit + VPS | Ship a real agent as graduation |

## Content Pipeline

```
Vault note (tagged #notebooklm)
      ↓
notebooklm-prep.py
      ↓
NotebookLM (Audio / Video / Briefing)
      ↓
Distribute to Telegram:
  - Labs → technical modules
  - Strategies → DeFi/crypto modules
  - Entertainment → practitioner stories
  - HQ → Academy announcements
```

## REP & Credentials

- Each module awards REP on completion
- Track completion = on-chain credential (ERC-8004 attestation)
- Sovereign tier graduates get:
  - Agent Kit pro license
  - Listing on GenTech agent marketplace
  - Contributor status in GenTech DAO

## Why This Works

| Angle | Advantage |
|-------|-----------|
| **Dogfooding** | We teach using our own tools — every lesson is a showcase |
| **Content engine** | Our vault already has the source material. NotebookLM turns it into content in clicks |
| **Distribution** | 4 Telegram groups are built-in channels |
| **Network effects** | Graduates deploy agents → more Agent Kit usage → more x402 volume |
| **Differentiation** | No one teaches "agent development as a curriculum." Everyone sells tooling. We sell the skill. |

---

## Next Steps

1. ✅ Greenlit by Jordan
2. Draft Academy master spec (this document)
3. Port PGE-Academy modules into new structure
4. Build Output Enforcer plugin (the quick win, half day)
5. Build Guardrail Plugin (differentiator, 2-3 days)
6. Record first Agent Track module as NotebookLM audio
7. Publish to Telegram channels
