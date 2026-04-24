# Gentech Brand Narrative — "Modular AI Agents"

**Author:** Desmond (Creative)
**Date:** Apr 21, 2026
**Status:** APPROVED — core positioning for all hackathon submissions
**Tagline:** *"Swap the chain, keep the agent."*

---

## The One-Liner

**Gentech builds modular AI agent infrastructure — your chain, your oracle, your rules.**

We don't lock you into one blockchain, one data provider, or one dispute resolver. We build the interfaces. You pick the stack.

---

## Why "Modular" Wins

Every competitor we've analyzed chose lock-in:

| Project | Their Lock-In | Our Approach |
|---------|---------------|--------------|
| **Apolo** | BNB Chain + GenLayer only | Any chain + any oracle via `IResolver` interface |
| **Gamma/Arrakis** | Single chain, black-box strategies | Portable strategies with on-chain provenance |
| **AutoGPT agents** | No payment layer, no escrow | x402-native payments + modular dispute resolution |

**The pitch to judges:** "We built the interface, not the implementation. Plug in your chain. Plug in your oracle. The agent logic stays the same."

---

## Hackathon-Specific Framing

Each submission gets a tailored pitch, same core contracts:

### Arc (Apr 25) — Payments Focus
> "x402 payments + modular dispute resolution — works out of the box, scales with AI."

- Lead with: `DisputeResolver.sol` (ship today) + GenLayer adapter (opt-in)
- Demo: Full escrow lifecycle with human arbiter
- Differentiator: Two-tier architecture vs Apolo's single-oracle lock-in

### Colosseum / Solana (May 11) — Speed Focus
> "400ms finality — the only chain where agent micro-transactions make economic sense."

- Lead with: Solana-native Anchor programs, PDA-based vaults, Jupiter CPI
- Demo: Agent-to-agent payment in under 1 second, sub-cent amounts
- Differentiator: "Ogre Strategy" — 5 modular layers, each a standalone submission

### Kite AI (Apr 26) — AI-Native Focus
> "AI agents that negotiate, arbitrate, and settle — humans set the rules, agents execute."

- Lead with: Agent brain coordination, GEPA-evolved strategies
- Demo: Multi-agent handoff chain (risk → LP → vault → user alert)
- Differentiator: Real multi-agent system (4 agents working together, not one agent in a loop)

### ETHGlobal Open Agents (May 3) — Security Focus
> "Agents that pay for their own audits. Contracts that fund their own security."

- Lead with: AgentRiskScore + security audit marketplace via x402
- Demo: Agent discovers contract → pays x402 for audit scan → reports findings
- Differentiator: x402-native security infrastructure, not bolted on

---

## The Visual Identity

**Concept:** Modular blocks snapping together.

- Each block = a layer (Vault, Agent, Oracle, Chain)
- Blocks are interchangeable — same connectors, different implementations
- Color-coded by function:
  - 🔵 Blue = Payment (x402, USDC, $TECH)
  - 🟢 Green = Agent (Brain, Strategy, Coordination)
  - 🟠 Orange = Dispute (Resolver, Oracle, Arbiter)
  - ⚪ Silver = Chain (Solana, Arc, Base, Avalanche)

---

## The Origin Story (For Judges)

Jordan runs LP positions on Avalanche. Manual rebalancing, 12-hour monitoring shifts, working with AI agents. Returns beat every auto pool on the market.

**The problem:** There was no way to pay agents for their work. No escrow, no quality judgment, no dispute resolution.

**The solution:** AgentEscrow — agents hire agents, money moves trustlessly, AI validates the work.

**The insight:** This isn't a DeFi product. It's **infrastructure for the agent economy.** Every agent that does paid work needs escrow. Every escrow needs dispute resolution. Every dispute resolver can be swapped for a better one.

---

## Key Phrases (Use Everywhere)

- *"Swap the chain, keep the agent."*
- *"Modular AI agents. Your chain, your oracle, your rules."*
- *"Works out of the box today, scales with AI tomorrow."*
- *"We built the interface, not the implementation."*
- *"Agent-native payments. Chain-agnostic by design."*

---

## Competitive Positioning (Apolo Comparison)

**Apolo's flow:**
`Client → x402 → Apolo escrow → GenLayer adjudicates → BNB settles`

**Our flow:**
`Client → x402 → AgentEscrow → [YOUR RESOLVER] → [YOUR CHAIN] settles`

Apolo is a product. We're a **protocol.**

---

## Tags
#brand #narrative #hackathon #positioning #modular #multi-chain
