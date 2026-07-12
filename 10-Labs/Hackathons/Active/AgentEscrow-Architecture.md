# AgentEscrow — Technical Architecture

**Project:** AgentEscrow: Trust Infrastructure for the Agent Economy
**Hackathon:** Solana Frontier (Colosseum) — Deadline May 11, 2026
**Prize Pool:** $680K+ sidetracks + main Colosseum prizes
**Cluster:** Solana AI Agent Infrastructure (325 projects, 14 winners)

---

## 🎯 The Pitch

> "Agents are already transacting. There's no trust layer.
> AgentEscrow provides identity, reputation, and programmable escrow
> so agents can negotiate, pay, and settle jobs trustlessly on Solana."

**One-liner:** Trust infrastructure for agent-to-agent commerce on Solana.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTESCROW STACK                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Demo Layer: Web UI + CLI for agent job lifecycle       │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Agent Brain: Hermes agents with x402 payment hooks     │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Trust Layer: World ID + Metaplex Soulbound + Reputation│   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Escrow Engine: Anchor program (escrow + dispute + settlement)│
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │  Payment Rail: Swig wallets + USDC (SPL) + x402        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Program Architecture (Anchor)

### Program 1: `agent_escrow` (Core)

The main escrow program handling job lifecycle.

```
PDA Layout:
  Config PDA [b"config"]                    — singleton, global settings
  Escrow PDA [b"escrow", job_id.to_bytes()] — one per job
  Vault PDA  [b"vault", job_id.to_bytes()]  — USDC SPL token account
```

**Instructions:**
1. `initialize_config` — Set platform fee, dispute window, authority
2. `create_job` — Client posts job, deposits USDC into escrow vault
3. `accept_job` — Agent accepts, locks commitment
4. `submit_work` — Agent submits deliverable (off-chain hash stored)
5. `approve_and_release` — Client approves, funds release to agent
6. `dispute_job` — Either party escalates (starts dispute window)
7. `resolve_dispute` — Authority/arbiter resolves
8. `cancel_job` — Pre-acceptance cancellation, refund

**Key Design Decisions:**
- Solana account model = no reentrancy risk (accounts locked per tx)
- PDA vault = no separate contract deployment per escrow
- SPL Token CPI for USDC transfers
- Clockwork/Pyth for automated dispute timeout

### Program 2: `agent_identity` (Trust + Reputation)

Agent identity and reputation tracking via Metaplex Core.

```
PDA Layout:
  Agent Profile PDA [b"agent", owner_pubkey] — one per agent
  Reputation PDA    [b"rep", agent_pubkey]   — on-chain rep score
```

**Instructions:**
1. `register_agent` — Create Metaplex Core NFT (soulbound) with agent metadata
2. `update_reputation` — Increment/decrement rep based on job outcomes
3. `get_agent_profile` — Read agent metadata + rep score
4. `verify_world_id` — Link World ID verification to agent profile

**Metaplex Core Integration:**
- Use Metaplex Core program (mpl-core) for compressed NFTs
- Soulbound = transfer authority revoked (non-transferable)
- Metadata: name, description, capabilities, rep_score, jobs_completed, world_id_verified
- Plugins: Authority Plugin (owner-only updates), Frozen (soulbound)

### Program 3: `agent_payments` (x402 + Swig)

Payment routing and micro-payment settlement.

```
PDA Layout:
  Payment Channel PDA [b"channel", agent_a, agent_b] — persistent payment channel
  Settlement PDA      [b"settle", channel_id]         — settlement state
```

**Instructions:**
1. `open_channel` — Open persistent payment channel between two agents
2. `x402_pay` — Micro-payment via x402 protocol (sub-cent, instant)
3. `settle_channel` — Close channel, settle final balance on-chain
4. `route_payment` — Swig-mediated multi-hop payment routing

**x402 on Solana:**
- Use x402 SDK for Solana (existing standard)
- USDC (SPL) as settlement token
- Sub-cent payments: agent pays 0.001 USDC per API call
- Payment channels = batched settlement (saves gas)

---

## 🔌 Sponsor Integration Map

| Sponsor | Program | Integration | Judge Signal |
|---------|---------|-------------|--------------|
| **Metaplex** | `mpl-core` | Agent identity NFTs (soulbound) | "Agents have on-chain identity" |
| **World** | World ID SDK | Agent identity verification | "We know who our agents are" |
| **Swig** | Swig SDK | Multi-token payment routing | "Agents can pay anyone" |
| **Phantom** | Phantom Connect | Wallet for agent buyers | "Seamless UX for humans" |

**Total: 4 sponsor integrations** — strong signal for judges.

---

## 🎬 Demo Flow (5 minutes)

### Scene 1: Agent Registration (30s)
1. Show World ID verification → agent gets verified badge
2. Metaplex Core NFT minted → agent profile created with rep=0
3. Agent appears in "Agent Registry" UI

### Scene 2: Job Posting (30s)
1. Client (human) posts a job: "Analyze SOL/USDC volatility for next 24h"
2. Deposits 5 USDC into escrow vault (PDA)
3. Job appears in "Open Jobs" feed

### Scene 3: Agent Accepts + Executes (1min)
1. Agent sees job, accepts (locks commitment)
2. Agent brain (Hermes) processes task:
   - Fetches price data via Switchboard oracle
   - Runs analysis model
   - Produces deliverable
3. Agent submits work (hash stored on-chain)

### Scene 4: Settlement + Rep Update (30s)
1. Client approves work
2. USDC releases from vault → agent wallet
3. Reputation NFT updated: rep += 10, jobs_completed += 1
4. Transaction shows on Solana Explorer

### Scene 5: x402 Micro-Payments (30s)
1. Show agent paying 0.001 USDC per API call via x402
2. Payment channel opens, 100 micro-payments batched
3. Channel settled, final balance on-chain

### Scene 6: Agent Marketplace (30s)
1. Show agent registry with rep scores
2. Filter by reputation, capabilities
3. "Hire this agent" button → creates escrow

**Total: ~3 min demo + 2 min architecture explanation**

---

## 📁 Repository Structure

```
agent-escrow/
├── programs/
│   ├── agent-escrow/          # Core escrow program
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── state.rs       # Escrow, Config, Vault PDAs
│   │   │   ├── instructions/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── initialize_config.rs
│   │   │   │   ├── create_job.rs
│   │   │   │   ├── accept_job.rs
│   │   │   │   ├── submit_work.rs
│   │   │   │   ├── approve_release.rs
│   │   │   │   ├── dispute.rs
│   │   │   │   └── resolve_dispute.rs
│   │   │   └── errors.rs
│   │   └── Cargo.toml
│   ├── agent-identity/        # Identity + reputation program
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── state.rs       # AgentProfile, Reputation PDAs
│   │   │   ├── instructions/
│   │   │   │   ├── register_agent.rs
│   │   │   │   ├── update_reputation.rs
│   │   │   │   └── verify_world_id.rs
│   │   │   └── errors.rs
│   │   └── Cargo.toml
│   ├── agent-payments/        # x402 + Swig payment channels
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── state.rs       # PaymentChannel, Settlement PDAs
│   │   │   ├── instructions/
│   │   │   │   ├── open_channel.rs
│   │   │   │   ├── x402_pay.rs
│   │   │   │   └── settle_channel.rs
│   │   │   └── errors.rs
│   │   └── Cargo.toml
│   └── common/                # Shared types across programs
│       ├── src/lib.rs
│       └── Cargo.toml
├── tests/
│   ├── agent-escrow.ts        # Anchor tests for escrow
│   ├── agent-identity.ts      # Identity + rep tests
│   └── agent-payments.ts      # Payment channel tests
├── app/                       # Demo frontend (Next.js)
│   ├── components/
│   │   ├── AgentRegistry.tsx
│   │   ├── JobBoard.tsx
│   │   ├── EscrowDashboard.tsx
│   │   └── RepDisplay.tsx
│   └── pages/
│       └── index.tsx
├── scripts/
│   ├── deploy.ts              # Deploy all programs
│   ├── register-agent.ts      # CLI: register an agent
│   └── create-job.ts          # CLI: create a job
├── Anchor.toml
├── Cargo.toml
└── README.md
```

---

## 🛠️ Build Order (Sprint Plan)

### Phase 1: Core Escrow (Days 1-3)
- [ ] Scaffold Anchor workspace
- [ ] Implement `agent_escrow` program (all instructions)
- [ ] Write tests for full escrow lifecycle
- [ ] Deploy to Solana devnet

### Phase 2: Identity + Rep (Days 4-5)
- [ ] Implement `agent_identity` program
- [ ] Metaplex Core NFT minting (soulbound)
- [ ] World ID verification hook
- [ ] Reputation update logic

### Phase 3: Payment Channels (Days 6-7)
- [ ] Implement `agent_payments` program
- [ ] x402 micro-payment flow
- [ ] Swig integration for routing
- [ ] Payment channel open/settle

### Phase 4: Demo + Submission (Days 8-10)
- [ ] Build demo frontend (Next.js)
- [ ] Record demo video (5 min)
- [ ] Write README + submission docs
- [ ] Deploy all programs to devnet
- [ ] Submit to Colosseum

---

## ⚠️ Risks + Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Metaplex Core API changes | Can't mint soulbound NFTs | Use legacy Metaplex as fallback |
| World ID Solana SDK incomplete | Can't verify agents | Mock verification, note in docs |
| x402 SDK immature on Solana | Payment channels don't work | Use raw SPL Token transfers |
| 3 programs too ambitious | Incomplete demo | Ship escrow + identity only, payments as "coming soon" |
| Demo doesn't impress judges | Low score | Invest in video quality, clear narration |

---

## 🏆 What Judges Want to See

Based on winning patterns (Project Plutus $20K, Encifher):

1. **Clear problem statement** — "Agents need trust infrastructure"
2. **Working code** — Not just slides, deployed programs
3. **Technical depth** — Anchor programs with real PDA logic
4. **Sponsor usage** — 4 sponsors = strong signal
5. **Demo quality** — Live tx on Solana Explorer
6. **Narrative** — "The trust layer for the agent economy"

**Our edge:** No competitor has the full stack (identity + reputation + escrow + payments). Most build one piece. We build the infrastructure.

---

## 📊 Competitive Positioning

| Feature | AEP | Agent-Cred | Nexus Escrow | **AgentEscrow** |
|---------|-----|------------|--------------|-----------------|
| Escrow | ✅ | ❌ | ✅ | ✅ |
| Agent Identity | ❌ | ✅ | ❌ | ✅ |
| Reputation NFTs | ❌ | ❌ | ❌ | ✅ |
| x402 Payments | ❌ | ✅ | ❌ | ✅ |
| World ID Verification | ❌ | ❌ | ❌ | ✅ |
| Payment Channels | ❌ | ❌ | ❌ | ✅ |
| Sponsor Integrations | 0 | 1 | 1 | **4** |

**Positioning:** "Competitors solve one piece. We solve the trust problem."
