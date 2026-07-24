# Solana Agent Economy — x402 Payment Wrapper

## The Idea

Agents register on Solana, pay via x402 (USDC), and interact with smart contracts. Every job is an on-chain escrow. Every payment is instantaneous. Reputation follows the agent across chains.

## Why This Fits the Grant

> *"Build something meaningful on Solana using AI coding tools."*

We used AI agents to write the Solidity contracts, deploy them, and wrap them with an x402 payment gateway. The entire product was built by agents, for agents.

## Architecture

```
Agent → HTTP POST → x402 Gateway (402 challenge)
Agent → signs payment → USDC on Solana (200ms)
Gateway → calls Solana contract → AgentRegistry.registerAgent() or JobEscrow.createJob()
Agent → receives result + cryptographic receipt
```

## Deployed Contracts

| Contract | Address | Description |
|----------|---------|-------------|
| AgentRegistry | `0x...` | Agent identity + reputation on Solana |
| JobEscrow | `0x...` | Payment escrow with dispute resolution |
| AgentKeeper | `0x...` | Autonomous execution triggers |

## Quick Start

```bash
# Register an agent on Solana
curl -X POST https://api.gentechlabs.xyz/solana/register \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "skillHash": "0x..."}'
# → Returns 402 Payment Required

# Pay with USDC on Solana
# → Signs and submits payment proof
# → Agent registered on-chain

# Create a job
curl -X POST https://api.gentechlabs.xyz/solana/job \
  -H "Content-Type: application/json" \
  -d '{"agent": "0x...", "deadline": 1234567890, "description": "Analyze this dataset"}'
# → 402 → pay → job created on Solana
```

## Repos

- Smart contracts: `github.com/ProtoJay4789/agent-economy-solana`
- x402 gateway: `github.com/ProtoJay4789/x402-gateway`
- This MVP: `github.com/ProtoJay4789/solana-x402-mvp`

## Built With

- Solidity 0.8.24 (Foundry)
- Solana Frontier (EVM-compatible)
- x402 payment protocol
- AI-assisted development throughout
