# Gentech Agents — Open Source Multi-Agent Stack

**Date:** 2026-06-02
**Status:** Green Room — scoping
**Source:** Jordan's vision + AgentRQ cold email

---

## TL;DR

Open source our multi-agent orchestration system as "Gentech Agents" — a framework for building agent teams with specialized roles, human-in-the-loop, and x402 payments.

---

## What We're Building

A multi-agent system where:
- **Hermes** is the orchestrator (brain)
- **Specialized agents** handle code, strategy, content
- **Humans** can be hired via EarnFi + x402
- **ERC-8004** identity for agent discovery
- **Game UI** wraps it all in a multiplayer experience

---

## Agent Roles (Our Current Setup)

| Agent | Role | Tools | Group |
|-------|------|-------|-------|
| **Gentech HQ** | Orchestrator, coordination, decisions | Everything | HQ |
| **DMOB/Labs** | Code, builds, technical dev | Terminal, file, browser | Labs |
| **YoYo/Strategies** | Finance, DeFi, portfolio | Web, terminal | Strategies |
| **Desmond/Entertainment** | Content, social, marketing | Web, terminal | Entertainment |

---

## Open Source Components

### Core (MVP)
1. **Agent Registry** — ERC-8004 based identity for agents
2. **Role System** — Specialized agents with defined toolsets
3. **Communication Layer** — Inter-agent messaging (MCP-based)
4. **Human-in-the-Loop** — EarnFi + x402 integration
5. **Game UI** — Multiplayer lobby for hiring agents/humans

### Extensions (v2)
1. **Payment Layer** — x402 micropayments via AgentLayer
2. **Reputation System** — On-chain agent performance tracking
3. **Marketplace** — Agents discover and hire each other
4. **Templates** — Pre-built agent teams for common tasks

---

## GitHub Structure

```
ProtoJay4789/gentech-agents
├── README.md
├── LICENSE (MIT)
├── package.json
├── src/
│   ├── registry/          # ERC-8004 agent identity
│   ├── orchestrator/      # Hermes-based coordination
│   ├── agents/
│   │   ├── base.ts        # Base agent class
│   │   ├── coder.ts       # Code agent (DMOB)
│   │   ├── strategist.ts  # Strategy agent (YoYo)
│   │   └── content.ts     # Content agent (Desmond)
│   ├── communication/     # Inter-agent messaging
│   ├── human-loop/        # EarnFi + x402 integration
│   └── ui/                # Game lobby UI
├── templates/
│   ├── hackathon-team/    # Pre-built hackathon agents
│   ├── content-crew/      # Content creation team
│   └── trading-desk/      # DeFi trading agents
├── examples/
│   ├── basic-orchestration/
│   ├── human-hiring/
│   └── multi-agent-task/
└── docs/
    ├── getting-started.md
    ├── agent-roles.md
    ├── human-loop.md
    └── contributing.md
```

---

## Differentiation vs AgentRQ

| Feature | Gentech Agents | AgentRQ |
|---------|------------|---------|
| Orchestrator | Hermes (open source) | Claude Code |
| Agent identity | ERC-8004 (on-chain) | Off-chain |
| Payments | x402 USDC (Solana) | N/A |
| Human hiring | EarnFi integration | Task board |
| Game UI | Multiplayer lobby | Dashboard |
| Chain | Multi-chain (Solana, Base, BNB) | None |
| License | MIT | Open source |

---

## Build Phases

### Phase 1: Core (1 week)
- [ ] Clean up agent code for public release
- [ ] Document agent roles and toolsets
- [ ] Create basic orchestration example
- [ ] Write README + getting started guide
- [ ] Push to GitHub as public repo

### Phase 2: Human Loop (1 week)
- [ ] Integrate EarnFi Agent Client SDK
- [ ] Build "Find Teammates" lobby UI
- [ ] Add x402 payment flow
- [ ] Document human hiring workflow

### Phase 3: Marketplace (1 week)
- [ ] Agent discovery via ERC-8004
- [ ] Agent reputation tracking
- [ ] Template system for pre-built teams
- [ ] Contributing guide

### Phase 4: Polish (1 week)
- [ ] Examples and tutorials
- [ ] CI/CD setup
- [ ] NPM package publishing
- [ ] Announcement content

---

## Why This Matters

1. **Infrastructure play** — We're not just building products, we're building the framework others use
2. **Agent economy validation** — Open sourcing proves our thesis that agents + humans = economy
3. **Community building** — Contributors become users become partners
4. **Grant magnet** — Open source + agent economy = perfect for Ethereum Foundation, Solana Foundation, etc.
5. **Brand authority** — "Gentech Agents" becomes synonymous with multi-agent orchestration

---

## The Moat: Open Source Framework + Premium Agents

**Strategy:** Open source the base layer, but our agents are the full experience.

| Component | Open Source | AAE Premium |
|-----------|-------------|-------------|
| Agent framework | ✅ Free | ✅ Free |
| Basic orchestration | ✅ Free | ✅ Free |
| MCP integration | ✅ Free | ✅ Free |
| ERC-8004 identity | ✅ Free | ✅ Free |
| x402 payments | ❌ Requires our stack | ✅ Built-in |
| EarnFi human hiring | ❌ Requires our stack | ✅ Built-in |
| Reputation system | ❌ Requires our stack | ✅ Built-in |
| Game UI (lobby) | ❌ Requires our stack | ✅ Built-in |
| Pre-built agents | ❌ BYOA (bring your own) | ✅ 4 optimized agents |

**The pitch:**
"Bring your own agent? Great — the framework is free. But you'll be missing x402 payments, human hiring, reputation tracking, and the multiplayer lobby. Our agents have all of that built in."

**Revenue model:**
1. **Agent Pass** ($15/mo) — Full access to our agents + premium features
2. **Pay-per-hire** — x402 fees on human hiring via EarnFi
3. **Marketplace** — Third-party agents built on our framework
4. **Enterprise** — Custom agent teams for businesses

**The flywheel:**
1. Open source framework → developers build on it
2. They need payments + human hiring → they use our stack
3. They list agents on our marketplace → we take a cut
4. More agents → more users → more revenue → more features

---

## Open Questions

1. What's the minimum viable open source release?
2. Do we need to refactor Hermes integration for public use?
3. Should we publish as NPM package or keep it GitHub-only?
4. What's the documentation standard? (JSDoc? TypeDoc? Markdown?)
5. Do we need a landing page / website for the project?
6. How do we enforce the "missing features" without being hostile to open source?

---

## Related

→ See [[09-Green Room/lobby-ui-product-vision.md]] (Lobby UI design)
→ See [[03-Projects/AAE/]] (Agent Arena infrastructure)
→ See [[03-Projects/Integrations/earnfi-agent-client/assessment.md]] (EarnFi SDK)
