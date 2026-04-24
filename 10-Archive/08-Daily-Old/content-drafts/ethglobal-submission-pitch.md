# ETHGlobal Open Agents — Submission Pitch

**Status:** DRAFT — ready for Jordan review
**Hackathon:** ETHGlobal Open Agents | Deadline: May 3, 4 PM UTC
**Format:** ETHGlobal project page content + partner track applications

---

## Project Name
**AgentChain** — On-Chain Agent Economy

## Tagline
*"Agents that discover, decide, coordinate, and settle — without a human in the loop."*

## Project Description (for ETHGlobal page)

### The Problem
AI agents are exploding in capability — but they operate in silos. A trading agent can't hire a research agent. A coding agent can't verify another agent's work. There's no trust layer for agent-to-agent commerce.

### Our Solution
AgentChain is a four-layer on-chain economy that enables autonomous agent coordination:

1. **Agent Registry** — Agents register with verifiable skills stored on 0G decentralized storage. Merkle root hashes on-chain prove capabilities without centralized trust.

2. **Task Manager** — Agents post tasks, claim work from others, and settle payments through smart contract escrow. Disputes resolved on-chain.

3. **Agent Keeper** — Powered by KeeperHub's MCP integration, agents autonomously monitor conditions and execute on-chain actions. The `check-and-execute` model eliminates polling waste.

4. **Risk Intel** — Every agent builds an on-chain reputation through completion rates, dispute history, and skill endorsements. Reputation is portable and verifiable.

### Why It Matters
The future isn't one super-agent — it's a marketplace of specialized agents that coordinate. AgentChain provides the infrastructure for that coordination: discovery, trust, payment, and reputation — all on-chain.

## Technical Architecture

| Component | Contract/Integration | Purpose |
|-----------|---------------------|---------|
| AgentRegistry | `AgentRegistry.sol` + 0G Storage | Register agents, store skills as Merkle hashes |
| TaskManager | `TaskManager.sol` | Post/claim tasks, escrow payments, resolve disputes |
| AgentKeeper | `AgentKeeper.sol` + KeeperHub MCP | Autonomous condition monitoring and execution |
| Risk Intel | On-chain reputation scoring | Track agent performance, build portable reputation |

## Sponsor Integrations

### 🎯 0G (Zero Gravity) — Primary Track ($15K)
**What we integrated:**
- **0G Storage** — Agent skills, configs, and knowledge stored as Merkle-tree chunks. Root hashes referenced on-chain in `AgentRegistry.sol`, enabling verifiable capability proofs without centralized APIs.
- **0G Chain** — Contracts deployed on 0G testnet (Chain ID: 16602), leveraging fast EVM finality for agent task lifecycle.
- **INFT (ERC-7857)** — Exploring agent identity tokens with encrypted metadata for private skill endorsements.

**Why it matters:** 0G gives agents decentralized, verifiable storage for their skills and memory. No single point of failure, no API dependency — just cryptographic proof of capability.

### 🎯 KeeperHub — Secondary Track ($5K)
**What we integrated:**
- **MCP Server** — Agents connect via KeeperHub's MCP: `claude mcp add --transport http keeperhub https://app.keeperhub.com/mcp`
- **Check-and-Execute** — Agents autonomously read on-chain state, evaluate conditions, and execute transactions in a single call. No polling loops, no wasted gas.
- **Para MPC Wallets** — Agents execute without exposing private keys, using KeeperHub's MPC wallet infrastructure.

**Why it matters:** KeeperHub turns passive agents into autonomous actors. Instead of "check every 5 minutes," agents fire precisely when conditions are met — efficient, reliable, truly autonomous.

## Demo
- **Live deployment:** 0G testnet (addresses in repo)
- **Demo video:** [2-min walkthrough — see repo]
- **GitHub:** github.com/ProtoJay4789/ethglobal-open-agents

## Team
**Gentech** — Building the Autonomous Agent Economy (AAE). Composable AI agent infrastructure — agents you can stack, customize, and trust.

---

#hackathon #ethglobal #pitch #submission #0g #keeperhub
