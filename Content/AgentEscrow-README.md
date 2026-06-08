# AgentEscrow

> **x402-native payments for the AI agent economy on Solana**

[![Solana](https://img.shields.io/badge/Solana-Anchor-purple)](https://solana.com)
[![x402](https://img.shields.io/badge/x402-Protocol-blue)](https://x402.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Colosseum Solana Frontier Hackathon** — Agents + Tokenization Track

---

## The Problem

AI agents can't pay for things online.

The web was built for humans — sessions, accounts, credit cards. When an autonomous agent needs to access an API, buy data, or compensate another agent for work, there's no native payment layer. Agents run through human-controlled wallets (centralized bottleneck) or don't transact at all (broken economics).

## The Solution

**AgentEscrow** — an escrow-based agent payment protocol built natively on Solana, powered by x402.

Agents pay per-request through HTTP 402 ("Payment Required") — the web's missing status code. Funds move into on-chain escrow before work begins. Release happens automatically when work is verified. No accounts. No subscriptions. No human in the loop.

## Why Solana

| Property | Value | Why It Matters |
|---|---|---|
| Finality | 400ms | Agents can't wait 12s for payment confirmation |
| Transaction cost | $0.00025 | $0.001 API calls are viable, not absurd |
| Parallel execution | Sealevel | 1000 agents paying simultaneously |
| x402 volume | 37M+ tx | We build where agents already transact |

## Architecture

### Programs

```
agent-escrow/
├── programs/
│   ├── agent_registry/    # On-chain agent identity (PDA-based)
│   ├── agent_escrow/      # Core escrow: create → accept → complete → dispute → refund
│   ├── x402_handler/      # HTTP 402 payment verification + escrow creation
│   └── agent_marketplace/ # Discovery + one-click hiring
├── tests/                 # TypeScript integration tests
└── app/                   # Demo frontend
```

### How It Works

```
Agent A (buyer)                    AgentEscrow                     Agent B (seller)
     |                                  |                                |
     |---- POST /api/task ------------->|                                |
     |<--- 402 Payment Required --------|                                |
     |     (price: 0.001 USDC)          |                                |
     |                                  |                                |
     |---- PAYMENT-SIGNATURE ---------->|                                |
     |     (signed USDC transfer)       |                                |
     |                                  |-- Create escrow PDA            |
     |                                  |                                |
     |                                  |-------- notify seller -------->|
     |                                  |                                |
     |                                  |<--- submit work proof ---------|
     |                                  |                                |
     |                                  |-- Verify → release to seller   |
     |                                  |-- Or → auto-refund on timeout  |
     |<--- 200 OK + task result --------|                                |
```

## Quick Start

```bash
# Prerequisites
# - Rust + Solana CLI + Anchor
# - Node.js 18+

# Clone
git clone https://github.com/ProtoJay4789/agent-escrow.git
cd agent-escrow

# Install
yarn install

# Build
anchor build

# Test
anchor test

# Deploy to devnet
anchor deploy --provider.cluster devnet
```

## Programs

### Agent Registry

On-chain identity for AI agents. Each agent is a PDA derived from their wallet.

```rust
// Register an agent
agent_registry::register(
    metadata_uri: "ipfs://Qm...",
    skills: vec!["trading".into(), "research".into()],
    price_per_job: 1_000_000, // 1 USDC
)
```

### Agent Escrow

Core escrow logic. Create jobs, accept, complete, approve, dispute, refund.

```rust
// Create a job with escrow
agent_escrow::create_job(
    agent: agent_pubkey,
    description: "Analyze LP position",
    deadline: Clock::get()?.unix_timestamp + 3600, // 1 hour
)
```

### x402 Handler

HTTP 402 payment verification + escrow creation in one transaction.

```rust
// Process an x402 payment
x402_handler::process_payment(
    payment_amount: 1_000_000, // 1 USDC
    service_endpoint: "https://api.example.com/analyze",
)
```

### Agent Marketplace

Discovery layer. Find agents by skill, price, reputation.

```rust
// Hire an agent in one transaction
agent_marketplace::hire_agent(
    agent: agent_pubkey,
    description: "Review smart contract",
    deadline: deadline_timestamp,
)
```

## x402 Integration

Built on the Solana-first x402 ecosystem:

- **[Corbits](https://corbits.dev)** — Server-side x402 payment gating
- **[PayAI](https://payai.network)** — Solana facilitator for payment verification
- **[x402scan](https://x402scan.com)** — Explorer for the x402 ecosystem

## Security

Solana's account model eliminates EVM vulnerabilities:

- **No reentrancy** — programs can't share state across transactions
- **No integer overflow** — Rust panics or checked math
- **Account validation** — Anchor enforces ownership + signer checks

Solana-specific mitigations:

- **Account stuffing** — PDA seed validation on every instruction
- **Signer verification** — every escrow action requires correct authority
- **Timeout auto-refund** — funds can't be locked forever

## Traction

### x402 on Solana Today

- **37M+ transactions** processed
- **20K+ buyers and sellers** active
- **70% of all x402 volume** flows through Solana
- **$10M+ in volume** since launch

## Team

| Role | Who |
|---|---|
| Smart Contracts (Anchor/Rust) | DMOB |
| Security Auditor | Jordan |
| Strategy & Research | YoYo |
| Content & Pitch | Desmond |
| Coordination | Gentech |

## License

MIT

---

*"Agents can't shake hands. They need escrow."*
