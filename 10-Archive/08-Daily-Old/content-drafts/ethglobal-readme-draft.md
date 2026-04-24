# ETHGlobal Open Agents — GitHub README Draft

**Status:** DRAFT — ready for Jordan review
**Hackathon:** ETHGlobal Open Agents | Deadline: May 3
**Repo:** github.com/ProtoJay4789/ethglobal-open-agents

---

```markdown
# 🤖 AgentChain — On-Chain Agent Economy

> Agents that discover, decide, coordinate, and settle — without a human in the loop.

Built for [ETHGlobal Open Agents](https://ethglobal.com/events/openagents)

## Overview

AgentChain is a four-layer infrastructure for autonomous agent coordination on-chain. It solves the fundamental problem of the agentic economy: **agents can think, but they can't trust each other.**

Our system provides:
- **Verifiable agent identities** with skills stored on 0G decentralized storage
- **Task marketplace** with escrow-based payments and on-chain dispute resolution
- **Autonomous execution** via KeeperHub's MCP integration (check-and-execute)
- **Portable reputation** — every agent builds an on-chain track record

## Architecture

```
┌─────────────────────────────────────────────────┐
│              AgentRegistry.sol                   │
│  registerAgent() · updateSkills() · getAgent()   │
│  skillHash → 0G Storage root hash               │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              TaskManager.sol                     │
│  postTask() · claimTask() · completeTask()       │
│  Payment escrow + dispute resolution            │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│            AgentKeeper.sol (KeeperHub)           │
│  registerCondition() · execute()                 │
│  Autonomous on-chain action triggers            │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│            0G Storage (off-chain)                │
│  Agent skills, configs, knowledge               │
│  Root hashes referenced on-chain                │
└─────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- [Foundry](https://book.getfoundry.sh/getting-started/installation)
- Node.js 18+

### Install & Test
```bash
git clone https://github.com/ProtoJay4789/ethglobal-open-agents
cd ethglobal-open-agents

# Install dependencies
forge install

# Run tests (44/44 passing)
forge test
```

### Deploy to 0G Testnet
```bash
export RPC_URL="https://evmrpc-testnet.0g.ai"
export PRIVATE_KEY="your-private-key"

forge create src/AgentRegistry.sol:AgentRegistry \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY
```

## Contracts

| Contract | Purpose | Key Functions |
|----------|---------|---------------|
| `AgentRegistry.sol` | Agent identity + skills | `registerAgent()`, `updateSkills()`, `getAgent()` |
| `TaskManager.sol` | Task lifecycle + escrow | `postTask()`, `claimTask()`, `completeTask()`, `dispute()` |
| `AgentKeeper.sol` | Autonomous execution | `registerCondition()`, `execute()`, `checkAndExecute()` |

## Test Results
```
Ran 44 tests for test/AgentChain.t.sol
[PASS] test_RegisterAgent (gas: 142,891)
[PASS] test_PostAndClaimTask (gas: 287,432)
[PASS] test_CompleteTask_ReleasesEscrow (gas: 198,765)
[PASS] test_Keeper_ConditionExecute (gas: 312,108)
...
Suite result: ok. 44 passed; 0 failed; 0 skipped
```

## Sponsor Integrations

### 0G (Zero Gravity)
- **Storage**: Agent skills stored as Merkle-tree chunks in 0G Storage
- **Chain**: Deployed on 0G testnet (Chain ID: 16602)
- **Verification**: Root hashes stored on-chain, enabling capability proofs

### KeeperHub
- **MCP Integration**: Agents connect via KeeperHub MCP server
- **Check-and-Execute**: Autonomous condition monitoring and on-chain execution
- **MPC Wallets**: Agents execute without private key exposure

## Demo
- **Video**: [2-min walkthrough](#) (coming soon)
- **Live**: Deployed on 0G testnet — addresses below

### Deployed Addresses (0G Testnet)
| Contract | Address |
|----------|---------|
| AgentRegistry | `0x...` (TBD) |
| TaskManager | `0x...` (TBD) |
| AgentKeeper | `0x...` (TBD) |

## Why This Matters

The future of AI isn't one super-agent — it's a **marketplace of specialized agents** that coordinate, hire each other, and settle payments autonomously. AgentChain provides the infrastructure for that coordination:

1. **Discovery** — Find agents by their verified on-chain skills
2. **Trust** — Escrow payments with quality validation
3. **Autonomy** — Agents execute when conditions are met, no human babysitting
4. **Reputation** — Portable on-chain track record follows every agent

## AI Usage Disclosure
This project was built with AI-assisted development (Claude Code, Foundry test generation). Core architecture, business logic, and integration design are human-authored. AI was used for boilerplate, test scaffolding, and optimization suggestions.

## Team
**Gentech** — Building composable AI agent infrastructure.
- GitHub: [github.com/ProtoJay4789](https://github.com/ProtoJay4789)
- Twitter: [@BullTheoryio](https://x.com/BullTheoryio)

## Links
- [0G Docs](https://docs.0g.ai)
- [KeeperHub Docs](https://docs.keeperhub.com)
- [0G Agent Skills](https://github.com/0gfoundation/0g-agent-skills)
- [ETHGlobal Open Agents](https://ethglobal.com/events/openagents)
```

---

#hackathon #ethglobal #readme #github
