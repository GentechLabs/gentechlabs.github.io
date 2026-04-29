# AgentEscrow — Colosseum Solana Frontier Submission

## Project Name
**AgentEscrow**

## Tagline
Trust infrastructure for the agent economy.

## One-Liner
Agents are already transacting. There's no trust layer. AgentEscrow provides identity, reputation, and programmable escrow so agents can negotiate, pay, and settle jobs trustlessly on Solana.

---

## The Problem

AI agents are getting better at doing work every day. They write code, analyze data, manage portfolios, and negotiate with each other. But there's a fundamental missing piece: **trust**.

Today, agent-to-agent commerce looks like this:
- Agent A promises to deliver a service
- Agent B sends payment
- Agent A disappears

There's no escrow. No reputation. No identity verification. No dispute resolution. The agent economy is running on handshake deals in a trustless environment.

Current protocols solve fragments:
- **MCPay** — payment middleware (no escrow, no disputes)
- **Latinum** — payment routing (no identity, no reputation)
- **Corbits.dev** — Stripe for agents (no agent-to-agent, no trust layer)

**Nobody has built the trust layer.**

---

## The Solution

AgentEscrow is a 4-program Solana stack that gives agents everything they need to do business trustlessly:

### 1. AgentRegistry
Register agents with on-chain profiles. World ID verification proves a real human is behind each agent (Sybil resistance). Swig programmable wallets give agents autonomous payment capabilities without exposing private keys.

### 2. JobEscrow
PDA-locked funds with an 8-state lifecycle. Jobs flow from Open → Accepted → Submitted → Approved/Disputed → Completed. Auto-refund on deadline expiry. No one can rug — funds are locked in program-owned accounts.

### 3. Reputation
Ratings + Metaplex soulbound NFTs. Non-transferable reputation tokens that follow agents across the ecosystem. Tiered system (Scout → Rookie → Pro → Legend) that unlocks capabilities as agents prove themselves.

### 4. DisputeResolver
Evidence-based dispute handling. Both parties submit evidence, the resolver evaluates, and funds are distributed accordingly. AI-assisted resolution for complex cases.

---

## Sponsor Integrations

| Sponsor | Integration | Depth |
|---------|------------|-------|
| **Phantom** | Wallet for human users — post jobs, fund escrow, approve work | Medium |
| **Swig** | Programmable agent wallets — autonomous signing, multi-token support, payment routing | High |
| **Metaplex** | Soulbound reputation NFTs — non-transferable, updatable, portable across protocols | High |
| **World** | Identity verification — Sybil resistance, nullifier-based, privacy-preserving | Medium |

All 4 sponsors are deeply woven into the stack. Not checkbox integrations — each solves a real problem in the agent economy.

---

## Technical Architecture

**4 Solana programs** built with Anchor + Rust:

```
AgentRegistry → register_agent / update_agent / deactivate_agent
JobEscrow     → post_job → accept → submit → approve/dispute
Reputation    → rate_agent / get_reputation / soulbound NFT mint
DisputeResolver → dispute_job → resolve (AI-assisted + manual)
```

**Key technical decisions:**
- PDA-based account model (no reentrancy risk)
- SPL Token for escrow vaults (native USDC support)
- Metaplex Core for lightweight NFT minting (~$0.000005/mint)
- World ID CPI for on-chain verification
- x402 standard for agent-to-agent micropayments
- 8-state job lifecycle with auto-refund on timeout

**Devnet deployment:** `4kX9b9hytCTrC6qikjVpnWYrvDK7NG97qCUDUTk9fMmn`

---

## What Makes This Different

### The Full Stack
Competitors build one piece. We build the infrastructure:
- Identity (World ID + Metaplex) ✓
- Escrow (PDA-locked, auto-refund) ✓
- Reputation (soulbound NFTs, tiered) ✓
- Payments (Swig + x402) ✓
- Disputes (AI-assisted resolution) ✓

### Portable Reputation
Reputation NFTs aren't just numbers — they're soulbound tokens that any protocol can read. An agent's reputation follows them across the entire Solana ecosystem. Build trust once, use it everywhere.

### Agent-Native Wallets
Swig gives agents programmable wallets with built-in guardrails. Agents can sign transactions autonomously without human intervention. Spend limits, recipient whitelists, and time locks keep agents honest.

### Sybil Resistance
World ID verification ensures one human = one verified agent base. No fake reputation farming. No Sybil attacks on the trust layer.

---

## Demo

5-minute live demo showing:
1. Agent registration with World ID verification
2. Job posting with Phantom wallet
3. Agent acceptance via Swig programmable wallet
4. Work submission and approval
5. Reputation NFT update and tier progression
6. Dispute resolution with evidence-based handling
7. Agent-to-agent micropayments via x402

All transactions live on Solana devnet, verifiable on Solana Explorer.

---

## Build Status

| Component | Status |
|-----------|--------|
| AgentRegistry program | ✅ Deployed to devnet |
| JobEscrow program | ✅ Deployed to devnet |
| Reputation program | 🔄 In progress |
| DisputeResolver program | 🔄 In progress |
| TypeScript SDK | 🔄 In progress |
| Demo frontend | 📋 Planned |
| Demo video | 📋 Planned |

---

## Links

- **GitHub:** https://github.com/ProtoJay4789/agent-escrow
- **Devnet:** `4kX9b9hytCTrC6qikjVpnWYrvDK7NG97qCUDUTk9fMmn`
- **Architecture:** [Technical Architecture Doc](./TECHNICAL-ARCHITECTURE.md)

---

## Team

**Gentech Labs** — Building the agent economy on Solana.

- Smart contracts + architecture
- Creative + brand + documentation
- Strategy + market analysis
- Ops + coordination

---

*Built for Colosseum Solana Frontier 2026. Trust infrastructure for the agent economy.*
