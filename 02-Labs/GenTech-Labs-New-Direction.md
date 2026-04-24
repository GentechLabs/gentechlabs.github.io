# Gentech Labs — New Direction & Project Overview
**Date:** 2026-04-18
**From:** Jordan via YoYo
**Audience:** Dmob, Ali, Daedran (Labs team)

---

## The Learning Plan

**Primary path (80%): EVM/Solidity**
- Smart contract development (Solidity, Foundry)
- Security auditing (Cyfrin Updraft, bug bounties)
- This is the income bridge — bug bounties on EVM pay NOW

**Secondary path (20%): Solana/Rust (read-only)**
- Learn enough to READ Solana smart contracts
- Not writing from scratch — reviewing, understanding, testing
- Rust basics + Anchor framework overview
- Why: Solana audit demand is growing fast, few auditors, less competition

**The goal:** Be a cross-chain auditor (EVM + Solana). Extremely rare, 2x market value.

---

## The Grand Project: AgentEscrow (working title: "GenTech Strategies")

**What it is:** AI-managed DeFi vaults where autonomous agents handle LP management, risk alerts, and strategy execution — with a social arena for competing and showcasing agent performance.

**The edge:**
> "Auto pools are great but I have better returns working 12 hours with you guys."

Pure auto pools (Gamma, Arrakis) optimize for TVL, not user returns. AgentEscrow brings **judgment + automation + social proof.**

### Three Layers

**Layer 1: Vault (The Money)**
- Smart contracts holding LP positions
- Rule engine: auto-rebalance, dip-buying, exit triggers
- Fee-efficiency focused by default
- Custom rules for advanced users

**Layer 2: Agents (The Brains)**
- Persistent memory across sessions
- Agent-to-agent handoffs on risk events
- Multi-agent coordination (watchdog, green room protocols)
- Strategy evaluation and research

**Layer 3: Arena (The Social)**
- Spin up agents, deploy strategies, compete on-chain
- Public dashboards — others view agent performance
- Leaderboard by returns, risk-adjusted, fee capture
- Skills marketplace — agents charge for premium strategies
- "Gentech Strategies" = the pro league

### Chain Strategy

| Chain | Role | Timeline |
|-------|------|----------|
| **Solana** | Primary — build, break, learn | Now → May 11 (Frontier Hackathon) |
| **Avalanche** | Chain #2 — expand with proven product | July 14 (grant window) |
| **AVAX Subnet** | Endgame — AgentEscrow L1 | Late 2026+ |
| **Arbitrum** | Was primary → now chain #3 | Whenever |

### Hackathon Pipeline

1. **Kite AI (Apr 26)** — Prove concept on Arbitrum/Solidity
2. **Solana Frontier (May 11)** — Port to Solana (Rust/Anchor), agents track, $230K+ prizes
3. **Dev3pack (May 8-10)** — Solana + AI, co-hosted by ElevenLabs

### Existing Code

We have repos on GitHub (ProtoJay4789):
- `agent-escrow` — Core Solidity contract (Foundry)
- `arc-hackathon` — Escrow + x402 nanopayments
- `kite-agent-commerce` — Kite AI agent commerce
- `avalanche-agent-economy` — AVAX multi-agent system

**Solana needs a Rust/Anchor rewrite.** The EVM Solidity stays for Kite AI. Solana version builds fresh.

---

## Division of Labor

| Who | Role |
|-----|------|
| **Jordan** | Product vision, Solidity, security auditing, hackathon pitches |
| **Dmob** | Smart contracts (Solidity + Rust/Anchor), code review |
| **Ali** | TBD — development support |
| **Daedran** | TBD — development support |
| **YoYo** | Research, strategy, competitive analysis |
| **Desmond** | Content, social media, marketing |

---

## What We Need From Labs

1. **Solidity side:** Keep building agent-escrow for Kite AI (Apr 26 deadline)
2. **Solana side:** Start scoping Rust/Anchor architecture for Solana Frontier
3. **Learning:** Everyone should understand the basics of Solana programs (accounts, PDAs, SPL tokens) — not just Jordan

---

## Project Naming

Working title: **AgentEscrow**
Brand name under consideration: **GenTech Strategies** or **GenTech Strategy**

Open to suggestions from the team.

---

#AgentEscrow #GenTechStrategies #Labs #direction
