# Hackathon Strategy — AAE Economy Pivot

**Date:** April 26, 2026  
**Author:** YoYo  
**Trigger:** Jordan's insight — "Everyone sells hammers. We sell the carpenter."

---

## The Problem With Our Previous Strategy

The old "Build Once, Ship Everywhere" plan had us submitting **smart contracts** to every hackathon. AgentEscrow on this chain, x402 on that chain, Marketplace on another.

That made us look like *another DeFi building kit*. We'd compete on gas efficiency, or contract features, or SDK integrations — races we don't need to run.

## The Pivot: Ship the Economy, Not the Contract

| Old Approach | New Approach |
|-------------|--------------|
| "AgentEscrow on Kite AI" | "The agent labor market on Kite AI" |
| "Solidity → Anchor port" | "Solana-native agent economy" |
| "x402 nanopayments" | "Agent-to-agent payment infrastructure" |
| Build a contract | Build the lifecycle: train → REP → deploy → earn |
| Compete on tech specs | Compete on *narrative* — nobody else has this layer |

**The insight:** No other team at any of these hackathons has:

1. **Four production agents** running right now (YoYo, DMOB, Desmond, Gentech) with real chat history
2. **A reputation economy** (AAE) where agents earn REP through simulation before touching real capital
3. **A deployable agent model** (AAS) where trained agents work for fees
4. **A social discovery layer** (AG) with live agent activity feed

These four facts are more compelling than any Solidity optimization.

---

## The Core Narrative — Universal Across All Hackathons

> **"We built the infrastructure for AI agents to earn, learn, and get hired — on-chain."**

One story, four chapters, each hackathon gets a different chain deployment:

```
AAE (Training) → REP (Reputation) → AAS (Deployment) → AG (Discovery)
    ↑                                               ↓
    └──────────── $TECH flows back to rewards ──────┘
```

Every hackathon submission opens with this lifecycle. Then you show the *piece* that lives on their chain.

---

## Updated Submission Strategy Per Hackathon

### 🟠 Kite AI — May 11 ($10K)
**Track:** Agentic Commerce  
**New pitch:** "The agent labor market landing on Kite AI for settlement"

- Show an agent (our Hermes bot) **learning in AAE**, earning REP, then **deploying via AAS** to perform a paid task
- Settlement happens on Kite AI (x402 + USDC)
- Demo: "Watch YoYo's agent get hired, execute, and earn $TECH"
- **Why Kite AI wins:** Kite's chain becomes the *settlement layer* for the agent economy. Not just another chain running escrow — the chain where labor gets paid.

Kite's own narrative is "agentic economy" — we're giving them the literal definition of that phrase.

### 🟢 Solana Frontier — May 11 ($230K+)
**Track:** Agents + Tokenization  
**New pitch:** "Solana-native agent economy — high-speed, low-cost labor market"

- Same AAE lifecycle, but **native Solana programs** (Anchor) instead of EVM
- Focus on **speed** as the differentiator: Solana agents can execute more tasks per block, higher frequency trading, faster REP accumulation
- Tokenization angle: agent REP as a Solana SPL token, tradeable on secondary (this opens the financialization debate but it's Frontier — they want bold ideas)
- **Why Solana wins:** Solana becomes the *high-throughput execution chain* for agent labor. Low fees mean micro-transactions for agent tasks are viable.

### 🔵 ARC Hackathon — TBD
**New pitch:** "The escrow foundation of the agent economy — dispute resolution for AI labor"

- DisputeResolver becomes the **enforcement layer** of the economy
- Show: agent does work, client disputes, AI validators resolve it on-chain
- **Why ARC wins:** ARC becomes the *trust layer* — where agent contracts go when things go wrong

### 🔴 ElevenHacks #6 — ~May 7 ($10K + credits)
**New pitch:** "Voice interface for the agent labor market — hire agents by speaking"

- Same economy, but **voice-first**: "Hey agent, swap this" → agent executes → voice confirmation
- The game angle: the Trading Arena becomes a *recruitment ground* — users play, learn agent skills, then graduate to AAS
- **Why ElevenLabs wins:** Their voice tech becomes the *human interface* to the agent economy. Every agent has a voice. Every transaction is confirmed audibly.

---

## What Actually Changes in Our Deliverables

| Item | Old | New |
|------|-----|-----|
| **README** | Contract docs | Agent economy whitepaper, link to lifecycle |
| **Demo video** | "Here's a swap" | "Watch an agent earn REP, get hired, execute, get paid" |
| **Architecture diagram** | Contract hierarchy | AAE → AAS → AG flow |
| **Live demo** | Transaction in explorer | Real Hermes agent executing a task |
| **Unique sell** | "We used x402" | "We have 4 production agents with REP scores" |

**Our contracts barely change.** The narrative does all the heavy lifting.

---

## The Unfair Advantage — Concrete Proof

When the judges ask "show me it works," every other team points at a testnet contract.

We point at our **Telegram group** — four real agents, with real chat history, executing real tasks, earning real REP. We've been running since April 2026.

No competitor at any of these hackathons has that. Not one.

---

## Action Items

| Who | What | By |
|-----|------|-----|
| **YoYo** | Write revised README templates for Kite AI + Solana Frontier | Apr 27 |
| **Desmond** | Update demo video scripts to show the full lifecycle (not just the contract) | Apr 28 |
| **DMOB** | Contracts stay the same — just add REP-related events/metadata for the demo narrative | May 5 |
| **Jordan** | Final narrative review + record demos showing the agent economy pitch | May 9 |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Judges think it's too ambitious (multiple layers) | 🟡 | Demo focuses on ONE agent lifecycle (5 min loop) |
| Other team copies the narrative | 🟢 | They can't copy our 4 running agents — that's years of operations compressed into weeks |
| Judges want code over story | 🟡 | Contracts are still solid. Lead with code, close with the economy vision. |
| Can't show live Hermes agent in demo | 🟡 | Record screen capture of Telegram group + agent responses. Time-stamp the REP earning. |
