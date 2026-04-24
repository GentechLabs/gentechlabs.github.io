# ETHGlobal Open Agents — Hackathon Scope

## Overview
- **Event**: Open Agents by ETHGlobal
- **Prize Pool**: $50,000+ (partners: $15K + $5K + $5K + $5K visible)
- **Hackathon Dates**: April 24 – May 6, 2026
- **Submission Deadline**: May 3, 2026 at 4:00 PM UTC
- **Live Judging**: May 4, 2026
- **Finale**: May 6, 2026
- **Format**: Async, remote, global
- **Entry**: Solo or teams (max 5), 0.005 ETH stake per person
- **Apply**: https://ethglobal.com/events/openagents

## What You Submit
1. Project page on ETHGlobal (name, description, tech)
2. GitHub repo (CRITICAL — judges check this)
3. Demo video (REQUIRED — 2-3 min, tight)
4. Live deployment URL (testnet or mainnet)
5. Partner prize applications (max 3, explain integration)
6. AI usage disclosure (can't be 100% AI-generated)

## Sponsor Tracks (Research Complete)

### 0G (Zero Gravity) — $15,000 🎯 PRIMARY TARGET
**What it is**: Decentralized AI operating system — Storage, Compute, Chain, INFT
- **Storage**: Files chunked in Merkle trees, TypeScript SDK (@0glabs/0g-ts-sdk)
- **Compute**: GPU marketplace for AI inference (DeepSeek, Qwen, Whisper), TEE-verified
- **Chain**: Fast EVM L1 (chain ID 16661 mainnet, 16602 testnet)
- **INFT (ERC-7857)**: New NFT standard for AI agents with encrypted metadata

**Integration path**: 
- Agent skills → JSON → 0G Storage → root hash → on-chain registry
- Use INFT for agent ownership/transfer
- Use Compute for agent inference

**Key repos**:
- 0gfoundation/0g-agent-skills (14 ready-made skills)
- 0gfoundation/agenticID-examples (3 ERC-7857 examples)
- 0gfoundation/0g-memory (persistent agent memory)

**Docs**: https://docs.0g.ai | **Faucet**: https://faucet.0g.ai

### KeeperHub — $5,000 🎯 SECONDARY TARGET
**What it is**: Web3 workflow automation with FIRST-CLASS AI agent support via MCP
- MCP Server: `claude mcp add --transport http keeperhub https://app.keeperhub.com/mcp`
- Direct Execution API: contract calls, transfers, conditional execution
- **Killer feature**: `check-and-execute` — read state → evaluate → execute in one call
- Para MPC wallets (no private key exposure)
- Supported chains: Ethereum, Sepolia, Base, Arbitrum, Optimism

**Integration path**: Agent keeper system — agents autonomously monitor and execute on-chain tasks

### Uniswap Foundation — $5,000
**What it is**: DEX protocol
- Likely wants: Agents interacting with Uniswap (trading, LP, governance)
- Oversubscribed with trading bots — need unique angle

### Gensyn — $5,000
**What it is**: Decentralized compute network for ML
- Likely wants: Agents using Gensyn for inference/training
- Adds complexity — lower priority unless time permits

## What Judges Want (Patterns from Past Winners)
1. **Working on-chain demo** — live URL, not "coming soon"
2. **Deep sponsor integration** — go deep on 1-2 sponsors, not shallow on all
3. **Clear problem → solution** — articulate value prop in 10 seconds
4. **Polished 2-3 min video** — async round IS your first impression
5. **Genuine blockchain usage** — logic that couldn't work off-chain
6. **Clean GitHub** — README, deployed addresses, architecture diagram
7. **Novelty > perfection** — rough working prototype beats polished clone

## AAE Layer Mapping

This project targets **Layers 2, 3, 4, 5** of the AAE architecture:
- **Layer 2: Agent Risk Intel** → AgentKeeper.sol (condition-based execution)
- **Layer 3: Brain** → 0G Storage integration (agent skills/memory)
- **Layer 4: Social/Reputation** → Leaderboard built from registry data
- **Layer 5: Cross-Agent Coordination** → TaskManager.sol (task lifecycle)

See: `AAE-Layers-Overview.md` for master architecture

## Architecture: On-Chain Agent Economy

```
┌─────────────────────────────────────────────────┐
│                 AgentRegistry.sol                 │
│  registerAgent() / updateSkills() / getAgent()   │
│  skillHash → 0G Storage root hash                │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│                 TaskManager.sol                   │
│  postTask() / claimTask() / completeTask()       │
│  payment escrow + dispute resolution             │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│               AgentKeeper.sol (KeeperHub)         │
│  registerCondition() / execute()                 │
│  agents autonomously trigger on-chain actions    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│            0G Storage (off-chain)                 │
│  Agent skills, configs, knowledge stored here    │
│  Root hashes referenced on-chain                 │
└─────────────────────────────────────────────────┘
```

## Revised Timeline (17 Days — Deadline May 3)

### Phase 1: Setup (Apr 17-19)
- [x] Register for ETHGlobal Open Agents (Jordan handles) ✅ Apr 17
- [ ] Get 0G testnet tokens from faucet
- [ ] Get KeeperHub API key
- [x] Set up Foundry project on 0G testnet ✅ Apr 17
- [ ] Clone 0g-agent-skills + agenticID-examples repos
- [x] Define contract interfaces ✅ Apr 17
- [x] Core contracts written + 44 tests passing ✅ Apr 17
- [x] Pushed to GitHub: github.com/ProtoJay4789/ethglobal-open-agents ✅ Apr 17

### Phase 2: Core Contracts (Apr 20-25)
- [x] AgentRegistry.sol — register agents with 0G skill hashes ✅ Apr 17
- [x] TaskManager.sol — task lifecycle with escrow ✅ Apr 17
- [x] AgentKeeper.sol — condition-based agent execution ✅ Apr 17
- [x] Integration tests in Foundry (44/44 passing) ✅ Apr 17

### Phase 3: Integration (Apr 26-28)
- [ ] 0G Storage integration — upload/download agent skills
- [ ] KeeperHub integration — agent execution triggers
- [ ] Agent execution flow — end-to-end demo
- [ ] Basic frontend or CLI demo

### Phase 4: Polish + Submit (Apr 29 – May 3)
- [ ] Security audit pass on all contracts
- [ ] Deploy to 0G testnet (or mainnet if stable)
- [ ] Record 2-3 min demo video
- [ ] Write README with architecture + deployed addresses
- [ ] Submit on ETHGlobal before May 3 4 PM UTC
- [ ] Prepare for live judging on May 4

## Competitive Advantage
- Already building AAE (agent economy concepts)
- Smart contract security expertise (Dmob)
- Agent coordination system (just built huddle/green room)
- Knowledge of agent skills/lifecycle management
- 0G + KeeperHub combination is unique — most will do Uniswap trading bots

## Risks
- 0G testnet stability (unknown)
- KeeperHub API limits (60 req/min)
- Solo vs team (speed vs coverage)
- Demo video quality (need to practice)

## Decision Points
1. **Primary track**: 0G ($15K) — largest prize, best fit
2. **Secondary**: KeeperHub ($5K) — natural agent integration
3. **Skip**: Uniswap (oversubscribed), Gensyn (complexity)
4. **Solo or team**: Recommend solo for speed, bring someone for frontend if needed
5. **Brand new repo**: Yes — must start from scratch per rules
