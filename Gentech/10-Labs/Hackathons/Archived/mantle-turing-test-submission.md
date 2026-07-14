# Agent Economy — Mantle Turing Test Hackathon Submission

**Track:** Agentic Wallets & Economy ($120K pool)
**Submission:** 0xAAC4 — Agent Economy (AAE)
**Team:** GenTech Labs (ProtoJay4789)
**Deadline:** June 15, 2026

---

## Executive Summary

Agent Economy is a modular, 6-contract on-chain infrastructure for autonomous AI agents to establish identity, build reputation, transact via escrow, and execute conditionally — all backed by the ERC-8004 Identity NFT standard on Mantle.

The core thesis: AI agents need their own economy before they can participate in ours. Agent Economy gives them wallets with identity, reputation, and autonomous execution — the missing primitives for the agentic future.

---

## Problem

Today's AI agents have no on-chain identity, no payment rails, and no autonomous execution layer. They operate as API endpoints, not economic actors. To build a real agentic economy, agents need:

1. **Persistent identity** — not just an EOA, but a verifiable agent profile with skills and reputation
2. **Trustless payments** — escrowed jobs with dispute resolution, not "send ETH and pray"
3. **Autonomous triggers** — conditions that execute actions without human intervention
4. **Composable data** — risk signals from DeFi protocols feeding into agent decisions

---

## Architecture: 5 Layers, 6 Contracts

```
┌─────────────────────────────────────────────┐
│              ERC-8004 Identity              │
│  (Mantle IdentityRegistry + Reputation)     │
├─────────────────────────────────────────────┤
│  AgentRegistry    │  AgentKeeper            │
│  (identity/rep)   │  (autonomous triggers)  │
├───────────────────┼─────────────────────────┤
│  JobEscrow        │  Data Adapters          │
│  (payment/dispute)│  (Zerion, GoldRush)     │
└───────────────────┴─────────────────────────┘
```

### Layer 0: Identity — ERC-8004 Adapter

**Contract:** `ERC8004Adapter.sol` (68 lines)

Bridges Agent Registry to the ERC-8004 Identity NFT standard deployed on Mantle Sepolia:
- IdentityRegistry: `0x8004A818BFB912233c491871b3d84c89A494BD9e`
- ReputationRegistry: `0x8004B663056A597Dffe9eCcC1965A193B7388713`

Every registered agent gets an on-chain identity NFT. This is what makes agents *portable* — their reputation follows them across protocols.

### Layer 1: Core — Agent Registry

**Contract:** `AgentRegistry.sol` (180 lines)

The backbone. Every agent is registered here with:
- Owner address, name, skill hash (IPFS/0G reference)
- Reputation score on a 0–10,000 scale (starts at 5,000)
- Job count, active status, registration timestamp

Key design decisions:
- **OpenZeppelin AccessControl** — ADMIN_ROLE for core operations, ORACLE_ROLE for reputation updates
- **ReentrancyGuard** — all state-changing functions protected
- **One agent per address** — prevents Sybil attacks at the registration level
- **RBAC reputation** — only oracles and admins can update reputation scores

### Layer 1: Core — Job Escrow

**Contract:** `JobEscrow.sol` (181 lines)

Full payment lifecycle for agent jobs:
- `Created → Accepted → Completed → Resolved` state machine
- `Disputed → Resolved` for conflict resolution
- Deadline enforcement, payment escrow, arbitrator role

The escrow model ensures trustless transactions between humans and agents, or between agents themselves. Disputes are resolved by designated arbitrators.

### Layer 2: Risk Intelligence — Agent Keeper

**Contract:** `AgentKeeper.sol` (147 lines)

The autonomous execution engine. Agents register conditions:
- **PriceAbove / PriceBelow** — trigger when oracle-reported prices cross thresholds
- **TimeElapsed** — trigger after a delay (e.g., auto-release payment after 6 hours)
- **Custom** — extensible for future condition types

When conditions are met, the keeper executes arbitrary calls on target contracts. This is how agents become *autonomous* — they set up rules, and the chain enforces them.

Oracle adapters push price data via `updatePrice()` / `updatePrices()`.

### Layer 3: Data Adapters

**ZerionAdapter.sol** (94 lines) — Portfolio risk detection
- Receives portfolio value data from Zerion CLI oracle
- Compares against risk thresholds
- Emits `RiskTriggered` events when portfolio drops below safety levels

**GoldRushAdapter.sol** (73 lines) — On-chain analytics
- Tracks transaction counts and balances via Covalent GoldRush API
- Provides activity metrics for reputation scoring
- Feeds data to AgentKeeper for autonomous decisions

Both adapters implement the `IAdapter` interface — a standardized thin wrapper pattern for pushing external data into the core system.

---

## ERC-8004 Integration

ERC-8004 is the key differentiator. Instead of agents being anonymous EOA addresses, they get:

1. **Identity NFT** — minted via `ERC8004Adapter.registerWithIdentity()`, linking agent ID to an on-chain token
2. **Portable reputation** — scores sync to the Mantle ReputationRegistry via `syncReputation()`
3. **Composable identity** — any protocol can check `hasIdentity()` and `getAgentId()` to verify agent credentials

This means an agent's reputation isn't locked in one system. It travels with the NFT — across DeFi protocols, job markets, and DAOs.

---

## Agentic Wallet Economy Vision

The demo flow shows the full agent lifecycle:

1. **Register** — Agent creates identity with skills (stored as IPFS hash)
2. **Get Identity NFT** — ERC-8004 adapter mints on-chain identity
3. **Accept Job** — Client creates escrow job, agent accepts
4. **Execute** — Agent completes work, keeper auto-releases payment
5. **Build Reputation** — Successful jobs increase reputation score

Scaling this out:
- **Agent staking** — agents stake MNT to signal commitment, slashed on misbehavior
- **Reputation-weighted job selection** — higher-reputation agents get priority
- **Cross-chain portability** — ERC-8004 NFTs carry reputation to other L2s
- **DAO governance** — agent collectives vote on protocol upgrades
- **DeFi integration** — agents autonomously manage LP positions, rebalance portfolios

The vision: a self-sustaining economy where agents earn, spend, and build reputation — all verifiably on-chain.

---

## Demo Flow (Test Suite)

The 14-test suite (`AgentEconomyTest.t.sol`) demonstrates:

### 1. Agent Registration
```
registerAgent("AlphaBot", skillHash) → agentId=1, reputation=5000
```

### 2. Job Lifecycle
```
client creates job (1 ETH escrow) → agent accepts → agent completes → client releases payment → agent receives 1 ETH
```

### 3. Autonomous Execution
```
agent registers time-condition (6 hours) → agent completes job → time passes → keeper triggers auto-release → payment sent
```

### 4. Risk Detection
```
oracle pushes Zerion portfolio data (below threshold) → checkRisk() returns true → RiskTriggered event emitted
```

### 5. Full Integration
Complete flow: register → escrow → accept → complete → keeper auto-release → payment verified

---

## Deployment

Two deployment scripts:

- **`DeployMantle.s.sol`** — Core stack (Registry + Escrow + Keeper + ERC8004 Adapter)
- **`DeployAgentEconomy.s.sol`** — Full stack (adds Zerion + GoldRush adapters)

```bash
# Deploy to Mantle Sepolia
FOUNDRY_PROFILE=mantle forge script script/DeployMantle.s.sol \
  --rpc-url mantle-sepolia --broadcast --verify
```

---

## Technical Stats

- **6 contracts**, ~650 lines of Solidity
- **14/14 tests passing**
- OpenZeppelin AccessControl + ReentrancyGuard
- Solidity 0.8.24, Foundry toolchain
- Mantle Sepolia (Chain ID: 5003)

---

## What We're Competing For

| Criteria | Our Approach |
|----------|-------------|
| On-chain performance | Escrow ROI tracking, job completion rates |
| Reputation score delta | 0–10,000 scale, oracle-driven updates |
| Agent autonomy level | Keeper-triggered autonomous execution |
| ERC-8004 integration | Full adapter with identity NFT + reputation sync |

---

## Built By

**GenTech Labs** — [ProtoJay4789](https://github.com/ProtoJay4789)

*Agents need an economy. We built the infrastructure.*
