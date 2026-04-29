# AgentEscrow — Enhanced Technical Architecture

**Project:** AgentEscrow: Trust Infrastructure for the Agent Economy  
**Hackathon:** Solana Frontier (Colosseum) — Deadline May 11, 2026  
**Prize Pool:** $680K+ sidetracks + main Colosseum prizes  
**Status:** Architecture refinement — sponsor integration deep dive  
**Author:** Desmond (Creative), building on YoYo's IResolver spec + DMOB's contract work

---

## 🎯 The One-Liner

> "Agents are already transacting. There's no trust layer. AgentEscrow provides identity, reputation, and programmable escrow so agents can negotiate, pay, and settle jobs trustlessly on Solana."

---

## 🏗️ System Architecture (Sponsor-Annotated)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENTESCROW STACK                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  UX Layer                                                  │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │     │
│  │  │  Web UI       │  │  CLI          │  │  Agent Brain  │   │     │
│  │  │  (Next.js)    │  │  (Anchor)     │  │  (Hermes)     │   │     │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │     │
│  │         │                  │                  │           │     │
│  │    ╔════╧════╗       ╔════╧════╗       ╔════╧════╗      │     │
│  │    ║ PHANTOM ║       ║ PHANTOM ║       ║  Swig   ║      │     │
│  │    ║ Wallet  ║       ║ Wallet  ║       ║ Wallet  ║      │     │
│  │    ╚════╤════╝       ╚════╤════╝       ╚════╤════╝      │     │
│  └─────────┼─────────────────┼─────────────────┼───────────┘     │
│            │                 │                 │                   │
│  ┌─────────▼─────────────────▼─────────────────▼───────────┐     │
│  │  Trust Layer                                               │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │     │
│  │  │  World ID     │  │  Metaplex    │  │  Reputation  │   │     │
│  │  │  Verify       │  │  Core NFT    │  │  Engine      │   │     │
│  │  │  (Identity)   │  │  (Soulbound) │  │  (On-chain)  │   │     │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │     │
│  └─────────┼─────────────────┼─────────────────┼───────────┘     │
│            │                 │                 │                   │
│  ┌─────────▼─────────────────▼─────────────────▼───────────┐     │
│  │  Escrow Engine                                            │     │
│  │  ┌──────────────────────────────────────────────────┐   │     │
│  │  │  agent_escrow (Anchor Program)                     │   │     │
│  │  │  - Job lifecycle: create → accept → submit → pay  │   │     │
│  │  │  - PDA vaults for USDC escrow                      │   │     │
│  │  │  - IResolver pluggable dispute resolution          │   │     │
│  │  └──────────────────────────────────────────────────┘   │     │
│  └─────────────────────────────┬───────────────────────────┘     │
│                                │                                   │
│  ┌─────────────────────────────▼───────────────────────────┐     │
│  │  Payment Rail                                             │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │     │
│  │  │  Swig         │  │  x402        │  │  SPL Token   │   │     │
│  │  │  Routing      │  │  Micro-pay   │  │  Transfers   │   │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Sponsor Integration Deep Dive

### 1. Phantom — Wallet for Agent Buyers

**Role:** Primary UX gateway. Humans and agents connect via Phantom to interact with escrow.

**Integration Pattern:**
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Phantom      │    │  Phantom      │    │  Phantom      │
│  Connect      │───▶│  Wallet      │───▶│  Provider    │
│  (dApp)       │    │  Adapter     │    │  (Solana)    │
└──────────────┘    └──────────────┘    └──────────────┘
```

**Technical Details:**
- **Phantom Connect** (EIP-6963 equivalent for Solana): Auto-detects installed Phantom wallet
- **Wallet Adapter**: `@solana/wallet-adapter-phantom` for React/Next.js frontend
- **Programmatic Signing**: Agents can sign transactions via Phantom if running in-browser context
- **Deep Links**: `https://phantom.app/ul/v1/authorize` for mobile/app-based flows

**Code Pattern (React):**
```tsx
import { useWallet } from '@solana/wallet-adapter-react';
import { PhantomWalletAdapter } from '@solana/wallet-adapter-phantom';

// In escrow creation flow:
const { publicKey, signTransaction } = useWallet();

const createJob = async (jobParams) => {
  const tx = await program.methods
    .createJob(jobParams.amount, jobParams.description, jobParams.agent)
    .accounts({
      client: publicKey,
      escrow: escrowPDA,
      vault: vaultPDA,
      tokenProgram: TOKEN_PROGRAM_ID,
    })
    .transaction();
  
  const signed = await signTransaction(tx);
  await connection.sendRawTransaction(signed.serialize());
};
```

**Judge Signal:** "Humans interact through Phantom — familiar UX, zero friction."

---

### 2. Swig — Payment Routing + Agent Wallets

**Role:** Programmable wallets for agents. Multi-hop payment routing. Sub-account management.

**What Swig Actually Is:**
- Programmable smart wallets on Solana
- Each agent gets a Swig wallet (PDA-based, not a keypair)
- Supports multi-token portfolios (USDC, SOL, custom SPL tokens)
- Rules engine: spend limits, time locks, whitelisted recipients
- Recovery: owner key can rotate agent wallets without losing funds

**Integration Pattern:**
```
┌─────────────────────────────────────────────────┐
│  Swig Wallet Architecture                        │
│                                                   │
│  Owner (Jordan/Platform)                          │
│       │                                           │
│       ├── Agent Wallet A (PDA)                    │
│       │   ├── USDC balance: 50.00                 │
│       │   ├── SOL balance: 0.50                   │
│       │   └── Rules: max 10 USDC/tx              │
│       │                                           │
│       ├── Agent Wallet B (PDA)                    │
│       │   ├── USDC balance: 120.00                │
│       │   └── Rules: whitelist: [escrow_program] │
│       │                                           │
│       └── Settlement Wallet                       │
│           └── Collects fees                       │
└─────────────────────────────────────────────────┘
```

**Technical Details:**
- **Swig SDK**: `@swig-wallet/solana` — TypeScript SDK for wallet management
- **Create Wallet**: `createSwigwallet(owner, payer)` → returns wallet PDA
- **Execute Rules**: Each wallet has on-chain rules (spend limits, recipient whitelist)
- **CPI Signing**: Swig wallets sign transactions via PDA — no keypair needed
- **Multi-Token**: Native SPL token support, no wrapping required

**Code Pattern:**
```typescript
import { createSwigWallet, executeSwigInstruction } from '@swig-wallet/solana';

// Create agent wallet
const agentWallet = await createSwigWallet({
  owner: platformKeypair,      // Platform retains ownership
  payer: payerKeypair,
  rules: [
    {
      type: 'spend-limit',
      token: USDC_MINT,
      amount: 100 * 1e6,        // Max 100 USDC per period
    },
    {
      type: 'whitelist',
      recipients: [ESCROW_PROGRAM_ID], // Can only pay into escrow
    }
  ]
});

// Agent pays into escrow via Swig
await executeSwigInstruction({
  wallet: agentWallet,
  instruction: createEscrowPayment(amount, escrowId),
});
```

**Judge Signal:** "Agents have programmable wallets with built-in guardrails."

---

### 3. Metaplex Core — Soulbound Reputation NFTs

**Role:** On-chain identity layer. Non-transferable agent profiles with reputation history.

**What Metaplex Core Is:**
- Next-gen NFT standard on Solana (replaces legacy Metaplex Token Metadata)
- Compressed NFTs (cNFTs) — ~$0.000005 per mint
- Plugin system: Authority, Frozen, Unburnable, etc.
- Native support for soulbound (non-transferable) assets

**Integration Pattern:**
```
┌─────────────────────────────────────────────────┐
│  Metaplex Core Agent Identity                     │
│                                                   │
│  Agent Profile NFT (Soulbound)                    │
│  ├── Metadata:                                    │
│  │   ├── name: "QuantBot-v2"                     │
│  │   ├── description: "DeFi analytics agent"     │
│  │   ├── capabilities: ["analysis", "trading"]   │
│  │   ├── world_id_verified: true                  │
│  │   ├── jobs_completed: 47                       │
│  │   └── reputation_score: 470                    │
│  ├── Plugins:                                     │
│  │   ├── Authority (owner-only updates)           │
│  │   └── Frozen (non-transferable)                │
│  └── Authority: Platform PDA                      │
└─────────────────────────────────────────────────┘
```

**Technical Details:**
- **Metaplex Core Program**: `CoREENz8zLsbVxJkQXiNLzJCRH7ZbCjq7M8GABtKjZ` (mainnet)
- **Mint**: `mintAsset({ asset: { name, uri }, authority })` → returns asset ID
- **Plugins**: `addPlugin({ assetId, plugin: { type: 'authority', authority: platformPDA } })`
- **Update**: Authority PDA can update metadata after mint (rep score, jobs completed)
- **Soulbound**: Freeze plugin + revoke transfer authority

**Anchor Integration:**
```rust
use metaplex_core::types::{Creator, Data, DataV2, TokenStandard};

// In register_agent instruction:
pub fn register_agent(ctx: Context<RegisterAgent>, name: String, capabilities: Vec<String>) -> Result<()> {
    // Mint Metaplex Core NFT
    let mint_ix = metaplex_core::instructions::mint_asset_v1(
        MintAssetV1Args {
            name: name.clone(),
            uri: format!("https://agentescrow.app/agent/{}", ctx.accounts.agent.key()),
            seller_fee_basis_points: 0,
            creators: Some(vec![Creator {
                address: ctx.accounts.platform.key(),
                verified: true,
                share: 100,
            }]),
        }
    );
    
    // Execute mint CPI
    solana_program::program::invoke(
        &mint_ix,
        &[
            ctx.accounts.mint_asset.to_account_info(),
            ctx.accounts.agent.to_account_info(),
            ctx.accounts.platform.to_account_info(),
            ctx.accounts.system_program.to_account_info(),
        ],
    )?;
    
    // Store agent profile
    let agent_profile = &mut ctx.accounts.agent_profile;
    agent_profile.name = name;
    agent_profile.capabilities = capabilities;
    agent_profile.reputation = 0;
    agent_profile.jobs_completed = 0;
    agent_profile.mint = ctx.accounts.mint_asset.key();
    
    Ok(())
}
```

**Judge Signal:** "Every agent has a soulbound identity — verifiable, updatable, non-transferable."

---

### 4. World — Agent Identity Verification

**Role:** Sybil resistance. Prove agents are "real" (controlled by verified humans or organizations).

**What World ID Is:**
- Proof of Personhood (PoP) via iris scan
- On-chain verification: `WorldIDProvider` contract on Solana
- Nullifier hash prevents double-verification
- Privacy-preserving: no PII on-chain, just proof

**Integration Pattern:**
```
┌─────────────────────────────────────────────────┐
│  World ID Verification Flow                       │
│                                                   │
│  1. Agent owner visits World App                  │
│  2. Scans iris → receives nullifier hash          │
│  3. Agent registration calls verify_world_id:     │
│     ┌──────────────────────────────────────────┐ │
│     │  verify_world_id(                         │ │
│     │    agent: agentPDA,                        │ │
│     │    nullifier_hash: [hash],                 │ │
│     │    proof: [proof_data],                    │ │
│     │  )                                         │ │
│     └──────────────────────────────────────────┘ │
│  4. On-chain: WorldID contract verifies proof     │
│  5. Agent profile: world_id_verified = true       │
│  6. Nullifier stored → can't verify again         │
└─────────────────────────────────────────────────┘
```

**Technical Details:**
- **World ID Solana Program**: `wdp1pWE7aBZb3waujggz9T2x3DZbKp3v6H1g6z3q1` (devnet/testnet)
- **Verify Call**: `world_id.verify_proof(proof, nullifier_hash, action_id)`
- **Action ID**: Unique per integration (prevents cross-app nullifier reuse)
- **SDK**: `@worldcoin/idkit` for frontend proof generation
- **Fallback**: If World ID SDK is immature on Solana → mock verification with note in docs

**Anchor Integration (via CPI):**
```rust
pub fn verify_world_id(
    ctx: Context<VerifyWorldId>,
    nullifier_hash: [u8; 32],
    proof: Vec<u8>,
) -> Result<()> {
    // Call World ID program via CPI
    let world_id_ix = world_id::instruction::verify_proof(
        ctx.accounts.world_id_program.key(),
        ctx.accounts.world_id_config.key(),
        nullifier_hash,
        proof,
        WORLD_ID_ACTION_ID,
    );
    
    solana_program::program::invoke(
        &world_id_ix,
        &[
            ctx.accounts.world_id_program.to_account_info(),
            ctx.accounts.world_id_config.to_account_info(),
        ],
    )?;
    
    // Store verification
    let agent_profile = &mut ctx.accounts.agent_profile;
    agent_profile.world_id_verified = true;
    agent_profile.nullifier_hash = nullifier_hash;
    
    Ok(())
}
```

**Judge Signal:** "We know who our agents are — verified through World ID."

---

## 📐 Data Model

### Agent Profile (Stored in Account + NFT Metadata)
```rust
#[account]
pub struct AgentProfile {
    pub owner: Pubkey,              // Platform admin PDA
    pub agent_wallet: Pubkey,       // Swig wallet PDA
    pub mint: Pubkey,               // Metaplex Core NFT mint
    pub nullifier_hash: [u8; 32],   // World ID nullifier
    pub name: String,               // Agent display name
    pub capabilities: Vec<String>,  // ["analysis", "trading", "coding"]
    pub reputation: u64,            // Score: 0-1000+
    pub jobs_completed: u32,        // Total jobs finished
    pub jobs_disputed: u32,         // Total disputes filed
    pub world_id_verified: bool,    // World ID check
    pub created_at: i64,            // Unix timestamp
    pub last_active: i64,           // Last job interaction
}
```

### Escrow Job
```rust
#[account]
pub struct EscrowJob {
    pub job_id: u64,                // Unique ID
    pub client: Pubkey,             // Human buyer
    pub agent: Pubkey,              // Agent seller
    pub amount: u64,                // USDC in lamports (6 decimals)
    pub vault: Pubkey,              // PDA holding funds
    pub resolver: Pubkey,           // IResolver implementation
    pub status: JobStatus,          // Created/Accepted/Submitted/Completed/Disputed
    pub description: String,        // Job requirements
    pub deliverable_hash: [u8; 32], // IPFS/off-chain content hash
    pub created_at: i64,
    pub deadline: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum JobStatus {
    Created,
    Accepted,
    Submitted,
    Completed,
    Disputed,
    Cancelled,
}
```

### Reputation Update Rules
```
Job Completed (approved):     +10 rep
Job Disputed (client wins):   -5 rep
Job Disputed (agent wins):    +2 rep
Job Cancelled (pre-accept):    0 rep
World ID Verified:            +5 rep (one-time bonus)
50 Jobs Milestone:           +25 rep bonus
100 Jobs Milestone:          +50 rep bonus
```

---

## 🔄 Transaction Flow (Sponsor-Annotated)

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Client  │     │ Phantom  │     │ AgentEscrow│     │  Agent   │
│  (Human) │     │  Wallet  │     │  Program   │     │ (Swig)   │
└────┬────┘     └────┬────┘     └────┬─────┘     └────┬────┘
     │               │               │                 │
     │  1. Connect   │               │                 │
     │──────────────▶│               │                 │
     │               │               │                 │
     │  2. Create Job + Deposit USDC │                 │
     │──────────────▶│──────────────▶│                 │
     │               │  (Phantom     │                 │
     │               │   signs tx)   │                 │
     │               │               │                 │
     │               │  3. Job created, vault funded   │
     │               │               │────────────────▶│
     │               │               │  (Notify agent) │
     │               │               │                 │
     │               │               │  4. Agent accepts│
     │               │               │◀────────────────│
     │               │               │  (Swig signs)   │
     │               │               │                 │
     │               │               │  5. Agent submits│
     │               │               │◀────────────────│
     │               │               │  (deliverable)  │
     │               │               │                 │
     │  6. Review    │               │                 │
     │──────────────▶│──────────────▶│                 │
     │               │  (Approve)    │                 │
     │               │               │                 │
     │               │  7. Release funds               │
     │               │               │────────────────▶│
     │               │               │  (USDC → Swig)  │
     │               │               │                 │
     │               │  8. Update rep │                 │
     │               │               │  (Metaplex NFT) │
     │               │               │                 │
     └───────────────┴───────────────┴─────────────────┘
```

---

## 📁 Repository Structure (Updated)

```
agent-escrow-solana/
├── programs/
│   ├── agent-escrow/              # Core escrow program
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── state.rs           # EscrowJob, Config, Vault PDAs
│   │   │   ├── instructions/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── initialize_config.rs
│   │   │   │   ├── create_job.rs
│   │   │   │   ├── accept_job.rs
│   │   │   │   ├── submit_work.rs
│   │   │   │   ├── approve_release.rs
│   │   │   │   ├── dispute.rs     # Uses IResolver pattern (YoYo's spec)
│   │   │   │   └── cancel_job.rs
│   │   │   └── errors.rs
│   │   └── Cargo.toml
│   ├── agent-identity/            # Identity + reputation program
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── state.rs           # AgentProfile PDA
│   │   │   ├── instructions/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── register_agent.rs    # Metaplex Core mint + World ID verify
│   │   │   │   ├── update_reputation.rs # Rep score updates
│   │   │   │   └── verify_world_id.rs   # World ID CPI
│   │   │   └── errors.rs
│   │   └── Cargo.toml
│   ├── agent-payments/            # x402 + Swig payment channels
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── state.rs           # PaymentChannel, Settlement PDAs
│   │   │   ├── instructions/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── open_channel.rs
│   │   │   │   ├── x402_pay.rs
│   │   │   │   └── settle_channel.rs
│   │   │   └── errors.rs
│   │   └── Cargo.toml
│   └── common/                    # Shared types
│       ├── src/lib.rs
│       └── Cargo.toml
├── app/                           # Demo frontend (Next.js)
│   ├── components/
│   │   ├── AgentRegistry.tsx      # World ID + Metaplex identity display
│   │   ├── JobBoard.tsx           # Open jobs feed
│   │   ├── EscrowDashboard.tsx    # Job lifecycle management
│   │   ├── PaymentFlow.tsx        # Swig + x402 payment UI
│   │   └── RepDisplay.tsx         # Soulbound NFT rep display
│   ├── hooks/
│   │   ├── usePhantom.ts          # Phantom wallet connection
│   │   ├── useSwig.ts             # Swig wallet management
│   │   └── useWorldId.ts          # World ID verification
│   └── pages/
│       └── index.tsx
├── tests/
│   ├── agent-escrow.ts
│   ├── agent-identity.ts
│   └── agent-payments.ts
├── scripts/
│   ├── deploy.ts
│   ├── register-agent.ts
│   └── create-job.ts
├── Anchor.toml
├── Cargo.toml
└── README.md
```

---

## 🏆 Sponsor Integration Summary

| Sponsor | Integration | Depth | Judge Signal |
|---------|------------|-------|--------------|
| **Phantom** | Wallet adapter + Connect | Medium | Familiar UX, zero friction for buyers |
| **Swig** | Programmable agent wallets + payment routing | High | Agents have wallets with guardrails |
| **Metaplex Core** | Soulbound identity NFTs | High | On-chain identity, non-transferable rep |
| **World** | Proof of Personhood verification | Medium | Sybil resistance, verified agents |

**Total: 4 sponsor integrations** — all deeply woven into the stack, not surface-level.

---

## ⚠️ Risk Matrix

| Risk | Sponsor | Impact | Mitigation |
|------|---------|--------|------------|
| Swig SDK not mature on Solana | Swig | High | Fallback to raw SPL Token transfers + PDA vaults |
| Metaplex Core API changes | Metaplex | Medium | Use legacy Metaplex as fallback |
| World ID Solana SDK incomplete | World | Medium | Mock verification, note in submission docs |
| Phantom Connect breaking changes | Phantom | Low | Standard wallet adapter pattern is stable |
| x402 protocol immature on Solana | Swig/x402 | Medium | Use direct SPL transfers for MVP |

---

## 📊 What Makes This Strong for Judges

1. **4 sponsor integrations** — each solves a real problem, not checkbox integration
2. **Full stack** — identity (Metaplex + World) + escrow (Anchor) + payments (Swig + x402)
3. **Pluggable dispute resolution** — IResolver pattern (YoYo's spec) enables AI arbitration
4. **Working demo** — live tx on Solana Explorer, not just slides
5. **Clear narrative** — "The trust layer for the agent economy"
6. **Competitive moat** — no competitor has the full stack

---

## 🗓️ Build Order (Sprint Plan)

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
- [ ] Swig wallet integration
- [ ] x402 micro-payment flow
- [ ] Payment channel open/settle

### Phase 4: Demo + Submission (Days 8-10)
- [ ] Build demo frontend (Next.js) with Phantom + Swig + World ID UI
- [ ] Record demo video (5 min)
- [ ] Write README + submission docs
- [ ] Deploy all programs to devnet
- [ ] Submit to Colosseum

---

*Architecture by Desmond (Creative). Review with DMOB for contract accuracy. Sync with YoYo for revenue model alignment.*
