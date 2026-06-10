# Mantle Turing Test — DoraHacks Submission Draft

## Project Name
**Agent Economy Protocol (AEP)**

## Tagline
Multi-chain agent identity, escrow, and autonomous execution — powered by ERC-8004 on Mantle.

## Track
**Agentic Wallets & Economy**

## Description (500 chars max)
Agent Economy Protocol enables AI agents to operate as first-class economic actors on-chain. Agents get ERC-8004 identity NFTs on Mantle, participate in job escrows with dispute resolution, and execute autonomous strategies via condition-based triggers. Built with OpenZeppelin RBAC, the protocol provides the infrastructure layer for the agentic economy — where agents earn, spend, and build reputation autonomously.

## Description (Full)
### The Problem
AI agents are becoming economic actors — trading, providing services, managing portfolios — but they have no on-chain identity, no payment rails, and no reputation system. They operate in silos, trusting no one and being trusted by no one.

### The Solution
Agent Economy Protocol (AEP) provides three core primitives for agentic commerce:

1. **Agent Registry** — ERC-721 identity NFTs with reputation scoring (0-10000 scale). Each agent gets an on-chain identity, metadata URI, and verifiable reputation.

2. **Job Escrow** — Payment escrow with built-in dispute resolution. Humans post jobs, agents claim and complete them, funds release on completion or go to arbitration.

3. **Agent Keeper** — Autonomous execution triggers. Define conditions (price thresholds, time-based, event-driven) and agents execute actions automatically when conditions are met.

### ERC-8004 Integration
Our ERC8004Adapter wraps the Mantle IdentityRegistry (0x8004A818BFB912233c491871b3d84c89A494BD9e) to give agents standardized on-chain identity NFTs. This enables:
- Cross-platform agent discovery
- Reputation portability across protocols
- Verified agent capabilities via metadata

### Multi-Chain Architecture
Built on Solidity with Foundry, AEP is chain-agnostic. The same contracts deploy to Mantle, Base, Arbitrum, or any EVM chain. Adapters (Zerion, GoldRush) provide chain-specific data feeds.

## Tech Stack
- **Solidity** ^0.8.24 (Foundry framework)
- **OpenZeppelin** (AccessControl, ReentrancyGuard, ERC721)
- **ERC-8004** (Mantle Identity NFT standard)
- **Mantle Sepolia** testnet (Chain ID 5003)

## Contracts (Mantle Sepolia — Deployment Pending Faucet)
| Contract | Purpose | Simulated Address |
|----------|---------|-------------------|
| AgentRegistry | Agent identity + reputation (0-10000 scale) | 0x3d37b9E431878B0998a38A834c448677b0cF53cA |
| JobEscrow | Payment escrow with dispute resolution | 0xF467b034702f13E14d7dE171A8f2aea3Df804Aa4 |
| AgentKeeper | Autonomous execution triggers | 0x89Bf3c3f76d36334A7A96Ac1f4bEFB3a6Bf29B8D |
| ERC8004Adapter | Mantle ERC-8004 identity integration | 0x62014c0349D1A9105cf2d82a792FefEC14D975A3 |
| ZerionAdapter | Portfolio risk detection | — |
| GoldRushAdapter | Covalent GoldRush analytics | — |

> **Note:** Addresses above are from Foundry simulation. Actual broadcast requires ~0.53 MNT from Mantle Sepolia faucet (browser-based, requires wallet connection). Deploy command ready: `FOUNDRY_PROFILE=mantle forge script script/DeployMantle.s.sol --rpc-url https://rpc.sepolia.mantle.xyz --broadcast --verify`

## Test Coverage
- 14/14 tests passing
- Full coverage: registration, escrow, reputation, adapters
- ReentrancyGuard, custom errors, gas-optimized
- Dry-run simulation successful on Mantle Sepolia (Chain 5003)
- Estimated deployment cost: 0.532 MNT (gas price ~100 gwei)

## Repository
https://github.com/ProtoJay4789/agent-economy-solana

## Demo
- **Live test suite:** `forge test` (14/14 passing)
- **Simulation:** All 4 contracts deploy successfully on Mantle Sepolia
- **Byreal CLI Integration:** v0.3.6 installed and operational (see below)
- **Video Demo:** Contract interaction on Mantle Sepolia (pending faucet funds)

## Team
**GenTech Labs** — Solo founder building the agent economy infrastructure layer.

## Why Mantle?
Mantle's ERC-8004 standard is the missing piece for agent identity. By building on Mantle, we get:
- Native ERC-8004 support (IdentityRegistry + ReputationRegistry)
- Low gas costs for frequent agent transactions
- EVM compatibility (same contracts deploy everywhere)
- Growing ecosystem of DeFi protocols for agents to interact with

## Byreal Skills CLI Integration
The Agent Economy Protocol integrates with **Byreal CLMM DEX** on Solana for agent-driven DeFi strategies:

### Integration Evidence
- **CLI Version:** `byreal-cli` v0.3.6 installed globally
- **Platform TVL:** $13.2M | **24h Volume:** $10.8M | **108 active pools**
- **Overview API:** Successfully queried platform metrics (TVL, volume, fees)
- **Pools API:** Successfully listed liquidity pools with APR, TVL, and price data

### Use Case: Agent-Driven Liquidity Provision
Agents registered via AEP can autonomously:
1. Query Byreal pools for optimal yield opportunities
2. Provide concentrated liquidity positions via CLMM
3. Rebalance positions based on price movement
4. Earn trading fees as autonomous revenue

This integration demonstrates the "agentic economy" in action — agents earning yield through DeFi protocols without human intervention.

## Video Demo (2 min)
1. Overview of the problem (0:00-0:30)
2. Architecture walkthrough (0:30-1:00)
3. Live contract interaction on Mantle Sepolia (1:00-1:45)
4. Vision for the agentic economy (1:45-2:00)
