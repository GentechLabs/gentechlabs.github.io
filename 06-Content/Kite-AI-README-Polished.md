# AgentEscrow — Trust Layer for the Agentic Economy

**Track:** Novel Track — Kite AI Global Hackathon 2026  
**Team:** Gentech Labs  
**GitHub:** [github.com/ProtoJay4789/arc-hackathon](https://github.com/ProtoJay4789/arc-hackathon)  
**Demo Video:** [Link TBD]  
**Live Demo:** [Link TBD]

---

## 🎯 The Problem

AI agents are about to autonomously execute billions in transactions. But there's no trust layer for agent payments.

- A user asks an agent to *"analyze Solana LST yields and recommend the best one"*
- The agent needs to call 3 paid APIs (Birdeye, DeFiLlama, custom data)
- **Who pays? How do they know the agent did the work? What if it hallucinates the result?**

Today, agents either run on prepaid budgets (no proof of work), require human approval per transaction (not autonomous), or use traditional payment rails (slow, KYC-heavy, not agent-native).

**AgentEscrow fixes this.**

---

## ✨ Our Solution

AgentEscrow is a **modular, chain-agnostic trust layer** for agent-to-service payments. It combines three primitives:

1. **Smart Contract Escrow** — USDC locked on-chain with programmable release conditions
2. **AI Validation** — Autonomous agents verify work quality before funds release
3. **x402 Payments** — HTTP-native stablecoin payments (no accounts, no friction)

### The Flow

```
User requests analysis
        │
        ▼
Agent quotes job: "3 API calls = $0.50"
        │
        ▼
┌───────────────┐
│  AgentEscrow    │  ← USDC locked on-chain
│  (Kite Chain)   │
└───────────────┘
        │
        ▼
Agent autonomously calls APIs
        │
        ▼
AI Validator verifies: "Data is real, sources match"
        │
        ▼
Funds release to service provider
        │
        ▼
Attestation posted to Kite chain
        │
        ▼
User receives verified analysis
```

---

## 🏗️ Architecture

![Architecture Diagram](./agentescrow-kite-architecture.html)

### Core Contracts

| Contract | Purpose | Lines | Tests |
|----------|---------|-------|-------|
| `AgentEscrow.sol` | USDC escrow with AI-validated release | ~240 | 14/14 ✅ |
| `X402PaymentHandler.sol` | x402 payment middleware | ~180 | 10/10 ✅ |
| `GenLayerOracleResolver.sol` | Oracle dispute resolver | ~120 | 14/14 ✅ |
| `HumanDisputeResolver.sol` | Human fallback resolution | ~100 | 15/15 ✅ |

**Total: 53 tests passing, 0 failures.**

### Key Features

- **EIP-712 signatures** — AI validator cryptographically signs off on work quality
- **ReentrancyGuard + Checks-Effects-Interactions** — Production security patterns
- **Pull-over-push** — Funds claimed by recipient, not pushed (gas optimization)
- **Deadline-based refunds** — Buyer can refund if seller doesn't deliver in 7 days
- **Signature replay protection** — Every signature is bound to a unique escrow ID + timestamp

---

## 🔗 Kite AI Integration

This is where it gets interesting. AgentEscrow is **modular by design** — chain-specific integrations are swappable modules.

### What We Use from Kite

| Kite Feature | How We Use It |
|--------------|---------------|
| **Agent Passport** | Agent identity + reputation scoring |
| **AA SDK** | Gasless transactions via EIP-3009 relayer |
| **Attestations** | Proof-of-execution posted on Kite chain |
| **x402 Native** | Native x402 support (we currently use Dexter SDK v3) |

### The Kite-Enhanced Flow

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Hermes     │──────▶│  Agent       │──────▶│  Kite Chain      │
│  (AI Agent) │     │  Passport    │     │  (Settlement)  │
└─────────────┘     └──────────────┘     └───────────────┘
       │                    │                      │
       ▼                    ▼                      ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Service    │     │  AA Vault    │     │  Attestation   │
│  Discovery  │     │  (Spending)  │     │  (Proof)       │
└─────────────┘     └──────────────┘     └───────────────┘
```

**The attestation is the killer feature:** After the agent executes API calls and the AI validator signs off, an attestation is posted to Kite chain. This creates an **immutable, verifiable record** that:
- The agent performed the work
- The data was validated by AI
- Payment was settled fairly

This turns every agent transaction into a **reputation event** — agents build on-chain track records of reliability.

---

## 🧪 Live Demo

### Quick Start

```bash
# Clone
git clone https://github.com/ProtoJay4789/arc-hackathon.git
cd arc-hackathon

# Install + test
forge install
forge build
forge test  # 53/53 passing
```

### The Demo Flow

1. **Create Escrow** — Buyer locks USDC for a service
2. **Execute Work** — Agent calls APIs autonomously
3. **AI Validate** — Validator signs EIP-712 message approving work
4. **Release Funds** — Seller claims payment
5. **Or Refund** — If deadline passes, buyer gets funds back

### Why Avalanche (For Now)

We built on Avalanche first because:
- Mature testnet infrastructure
- x402 SDK v3 fully supported
- Fast iteration for hackathon timelines

**Kite AI is our next target.** The architecture is designed for this — swap Avalanche RPC for Kite testnet, add Agent Passport identity, and post attestations. Estimated **2-3 days of focused work** to port.

---

## 🌐 Real-World Applicability

This isn't a toy. AgentEscrow solves a real problem that's about to be massive:

| Use Case | Why It Matters |
|----------|---------------|
| **AI Data Brokers** | Agents pay for real-time data without human approval |
| **Autonomous Trading** | Trading bots verify execution before releasing funds |
| **DeFi Automation** | Yield optimizers pay for cross-protocol rebalancing |
| **Agent Marketplaces** | Buyers escrow, agents deliver, AI validates |

**Market timing:** OpenAI's Operator, Anthropic's Computer Use, and Google's Project Mariner are all shipping agentic AI in 2025-2026. None of them have a trust layer for payments. AgentEscrow is that layer.

---

## 🎨 Novelty & Creativity

What makes AgentEscrow unique:

1. **AI-as-Validator** — Not just a signer. The AI actually evaluates work quality (data freshness, source credibility, result accuracy) before approving release.

2. **Modular by Design** — Core contracts are chain-agnostic. Kite integration is a module. Next week: Base. Next month: Solana (via Wormhole). The architecture doesn't care.

3. **x402-Native** — Built for the new HTTP payment standard. No accounts, no KYC, no friction. Agent-to-agent payments via HTTP headers.

4. **Reputation as Collateral** — Attestations on Kite chain create agent reputation scores. High-reputation agents get better rates, lower escrow requirements, faster settlement.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Smart Contracts** | Solidity ^0.8.20 + OpenZeppelin |
| **Testing** | Foundry (53 tests passing) |
| **Payments** | USDC + x402 (Dexter SDK v3 / Kite native) |
| **Validation** | EIP-712 signatures |
| **Identity** | ERC-8004 (Agent Registration) |
| **Chain (Current)** | Avalanche Fuji testnet |
| **Chain (Target)** | Kite AI testnet (Chain ID 2368) |

---

## 🗺️ Roadmap

- [x] Core escrow contracts (production-grade)
- [x] x402 payment router
- [x] AI validation via EIP-712
- [x] 53/53 tests passing
- [ ] Kite AI testnet deployment
- [ ] Agent Passport integration
- [ ] Attestation posting on Kite chain
- [ ] React dashboard for escrow management
- [ ] Multi-chain support (Base, Polygon, Solana via Wormhole)

---

## 👥 Team

**Gentech Labs** — A multi-agent AI team building autonomous systems for Web3.

| Member | Role |
|--------|------|
| **D-Mob** | Smart contract engineering |
| **YoYo** | Research & strategy |
| **Desmond** | Content & submissions |
| **Jordan** | Operations & coordination |

---

## 📁 Resources

- **GitHub:** [github.com/ProtoJay4789/arc-hackathon](https://github.com/ProtoJay4789/arc-hackathon)
- **Architecture Diagram:** [agentescrow-kite-architecture.html](./agentescrow-kite-architecture.html)
- **x402 Spec:** [402.xyz](https://402.xyz)
- **Kite AI Docs:** [docs.kite.ai](https://docs.kite.ai)

---

*Built with passion, tested with rigor, designed for the agentic future.*
