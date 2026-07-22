# AgentEscrow — Technical Architecture

**Sprint:** Colosseum Solana Frontier (deadline: May 11, 2026)
**Positioning:** "x402 solves payments. We solve trust."
**Repo:** https://github.com/ProtoJay4789/agent-escrow
**Devnet Program:** `4kX9b9hytCTrC6qikjVpnWYrvDK7NG97qCUDUTk9fMmn`

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      OFF-CHAIN LAYER                        │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Phantom  │  │   Swig   │  │ Metaplex │  │  World   │  │
│  │ Wallet   │  │ Pay Route│  │ NFT Mgr  │  │ ID Verify│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │              │         │
│  ┌────▼──────────────▼──────────────▼──────────────▼────┐  │
│  │              TypeScript Client SDK                    │  │
│  │   (agent registration → job lifecycle → settlement)   │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
├─────────────────────────┼───────────────────────────────────┤
│                    ON-CHAIN LAYER                           │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │              AgentRegistry Program                    │  │
│  │   register_agent / update_agent / deactivate_agent   │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │              JobEscrow Program                        │  │
│  │   post_job → accept → submit → approve/dispute       │  │
│  │   PDA-locked funds, auto-refund on timeout            │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │              Reputation Program                       │  │
│  │   rate_agent / get_reputation / soulbound NFT mint   │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │              DisputeResolver Program                  │  │
│  │   dispute_job → resolve (AI-assisted + manual)       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Sponsor Integration Map

### 2.1 Phantom — Wallet for Agent Buyers

**Role:** Primary wallet UX for human users posting jobs and funding escrow.
**Judge Points:** Embedded wallet, social login, frictionless onboarding.

**Integration:**
```typescript
// Phantom Wallet Adapter
import { useWallet } from '@solana/wallet-adapter-phantom';

// User connects Phantom → posts job → funds escrow
const postJob = async (jobSpec: JobSpec) => {
  const { publicKey, signTransaction } = useWallet();
  
  // Build ix: transfer SOL to job escrow PDA
  const escrowIx = SystemProgram.transfer({
    fromPubkey: publicKey,
    toPubkey: jobEscrowPDA,
    lamports: jobSpec.payment * LAMPORTS_PER_SOL,
  });
  
  // Sign + send via Phantom
  const tx = await signTransaction(new Transaction().add(escrowIx));
  return sendAndConfirmTransaction(connection, tx);
};
```

**Demo Flow:**
1. User opens demo → Phantom popup → connect
2. User fills job form (description, payment, deadline)
3. Phantom signs escrow funding transaction
4. Job appears on-chain with locked funds

---

### 2.2 Swig — Payment Routing + Agent Wallets

**Role:** Programmatic wallet management for AI agents. Agents can't hold private keys — Swig provides smart wallet accounts that agents control programmatically.
**Judge Points:** Multi-token support, agent-native wallets, payment routing.

**Integration:**
```rust
// Swig provides "accounts" — programmatic wallets for agents
// Each agent gets a Swig account that can sign transactions

// Agent accepts job → Swig account signs the accept instruction
use swig::state::account::Account;

// Agent wallet PDA (derived from agent registry entry)
let agent_wallet = Pubkey::find_program_address(
    &[b"agent_wallet", agent_name.as_bytes()],
    &program_id,
).0;

// When agent submits work, the Swig account signs
// No human keypair needed — the agent IS the signer
```

**Why This Matters:**
- Agents can receive payments directly to their Swig account
- Agents can pay for services (sub-agents, compute, data)
- Multi-token: SOL, USDC, or any SPL token
- Payment routing: split fees, escrow release, dispute holds

---

### 2.3 Metaplex — Soulbound Reputation NFTs

**Role:** Non-transferable reputation tokens that follow agents across the ecosystem.
**Judge Points:** Identity layer, portable reputation, on-chain provenance.

**Integration:**
```rust
// Metaplex Core — lightweight NFT standard
// Each agent gets a SOULBOUND (non-transferable) reputation NFT

use metaplex_core::state::TokenStandard;

// Mint reputation NFT after first completed job
#[derive(Accounts)]
pub struct MintReputationNFT<'info> {
    #[account(
        mut,
        has_one = agent @ ColosseumError::NotAgentOwner,
    )]
    pub agent_account: Account<'info, AgentAccount>,
    
    #[account(mut)]
    pub mint: Signer<'info>,
    
    /// CHECK: Metaplex token account
    #[account(mut)]
    pub token_account: AccountInfo<'info>,
    
    pub metaplex_program: Program<'info, MetaplexCore>,
}

// Reputation NFT stores:
// - Agent name + capabilities (metadata)
// - Total jobs completed
// - Average rating
// - Tier (Scout → Rookie → Legend)
// - Verification status (World ID verified = ✓)
```

**NFT Metadata Schema:**
```json
{
  "name": "AgentEscrow: CodeBreaker",
  "symbol": "AE-REP",
  "uri": "https://api.agentescrow.io/metadata/codebreaker.json",
  "seller_fee_basis_points": 0,
  "creators": [],
  "collection": { "name": "AgentEscrow Reputation", "verified": true },
  "token_standard": "NonFungible"
}
```

**Tiers:**
| Tier | Jobs | Min Rating | Unlock |
|------|------|-----------|--------|
| Scout | 0 | — | Basic registration |
| Rookie | 3+ | 3.0+ | Job acceptance |
| Pro | 10+ | 4.0+ | Dispute priority |
| Legend | 25+ | 4.5+ | Protocol governance |

---

### 2.4 World — Agent Identity Verification

**Role:** World ID verification to prove agents are backed by real humans (or verified entities). Prevents Sybil attacks on the reputation system.
**Judge Points:** Trust primitive, Sybil resistance, unique identity.

**Integration:**
```typescript
// World ID verification — proves unique human behind agent
import { IDKitWidget } from '@worldcoin/idkit';

// On registration: verify human → mint World ID proof → attach to agent
const verifyWithWorld = async () => {
  return new Promise((resolve) => {
    IDKitWidget({
      app_id: "app_agentescrow_mainnet",
      action: "register_agent",
      handleVerify: async (proof) => {
        // Send proof to backend → verify on-chain
        // Attach verified: true to agent account
        await sendVerification(proof);
        resolve(true);
      },
    });
  });
};
```

**On-chain verification:**
```rust
// World ID nullifier hash stored with agent account
// Prevents same human from registering multiple agents
#[account]
pub struct AgentAccount {
    pub name: String,              // 32 chars max
    pub owner: Pubkey,             // Phantom wallet
    pub capabilities: Vec<String>, // up to 10
    pub stake_lamports: u64,
    pub jobs_completed: u32,
    pub reputation_sum: u32,
    pub active: bool,
    pub world_id_nullifier: Option<[u8; 32]>, // World verification
    pub swig_wallet: Option<Pubkey>,           // Swig agent wallet
    pub reputation_nft: Option<Pubkey>,        // Metaplex NFT
    pub created_at: i64,
    pub bump: u8,
}
```

---

## 3. Program Architecture

### 3.1 Account Structures

```rust
// ── Agent Registry ──────────────────────────────────────────
#[account]
pub struct AgentAccount {
    pub owner: Pubkey,                 // Human wallet (Phantom)
    pub name: String,                  // Unique agent name
    pub capabilities: Vec<String>,     // What this agent does
    pub stake_lamports: u64,           // Skin in the game
    pub jobs_completed: u32,
    pub reputation_sum: u32,           // Sum of all ratings
    pub reputation_count: u32,         // Number of ratings
    pub active: bool,
    pub world_id_verified: bool,       // World ID check
    pub swig_wallet: Option<Pubkey>,   // Programmatic wallet
    pub reputation_nft: Option<Pubkey>,// Soulbound NFT mint
    pub created_at: i64,
    pub bump: u8,
}

// ── Job Escrow ──────────────────────────────────────────────
#[account]
pub struct JobAccount {
    pub job_id: String,                // Unique ID
    pub poster: Pubkey,                // Job creator
    pub worker: Option<Pubkey>,        // Assigned agent owner
    pub description: String,
    pub requirements: Vec<String>,
    pub payment_lamports: u64,         // Locked in PDA
    pub deadline: i64,
    pub status: JobStatus,
    pub deliverable: Option<String>,   // IPFS hash of work
    pub created_at: i64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum JobStatus {
    Open,
    Accepted,
    Submitted,
    Approved,
    Disputed,
    Completed,
    Cancelled,
    Expired,
}

// ── Dispute ─────────────────────────────────────────────────
#[account]
pub struct DisputeAccount {
    pub job: Pubkey,
    pub initiator: Pubkey,
    pub reason: String,
    pub resolution: Option<String>,
    pub resolved: bool,
    pub created_at: i64,
}
```

### 3.2 Job Lifecycle State Machine

```
                    ┌──────────┐
                    │   OPEN   │ ← poster funds escrow
                    └────┬─────┘
                         │ worker accepts
                    ┌────▼─────┐
                    │ ACCEPTED │ ← worker assigned
                    └────┬─────┘
                         │ worker submits
                    ┌────▼─────┐
                    │ SUBMITTED│ ← deliverable on-chain
                    └────┬─────┘
                    ┌────┴─────┐
               ┌────▼───┐ ┌───▼────┐
               │APPROVED│ │DISPUTED│
               └────┬───┘ └───┬────┘
                    │         │
               ┌────▼───┐ ┌───▼────┐
               │COMPLETED│ │RESOLVED│
               └────────┘ └────────┘
               
    Timeout path: OPEN/ACCEPTED → EXPIRED → auto-refund
    Cancel path: OPEN → CANCELLED → auto-refund
```

### 3.3 Error Handling

```rust
#[error_code]
pub enum ColosseumError {
    // Registry
    #[msg("Agent name too long (max 32 chars)")]
    NameTooLong,
    #[msg("Too many capabilities (max 10)")]
    TooManyCapabilities,
    #[msg("Stake amount too low (min 0.01 SOL)")]
    StakeTooLow,
    #[msg("Agent is not active")]
    AgentNotActive,
    #[msg("Agent already verified with World ID")]
    AlreadyVerified,
    #[msg("World ID verification required")]
    VerificationRequired,
    
    // Escrow
    #[msg("Job payment too low")]
    PaymentTooLow,
    #[msg("Job is not open for acceptance")]
    JobNotOpen,
    #[msg("Only the assigned worker can submit work")]
    NotAssignedWorker,
    #[msg("Only the job poster can approve work")]
    NotJobPoster,
    #[msg("Job deadline has passed")]
    DeadlinePassed,
    #[msg("Job cannot be cancelled after acceptance")]
    CannotCancelAfterAccept,
    #[msg("Insufficient funds in escrow")]
    InsufficientEscrow,
    
    // Reputation
    #[msg("Invalid reputation score (1-5)")]
    InvalidScore,
    #[msg("Cannot rate yourself")]
    SelfRating,
    #[msg("Agent has no completed jobs")]
    NoCompletedJobs,
    #[msg("Already rated this job")]
    AlreadyRated,
}
```

---

## 4. x402 Payment Integration

### 4.1 How x402 Works

x402 is the HTTP 402 "Payment Required" standard for agent-to-agent micropayments:

```
Agent A wants data from Agent B
  → Agent A sends request
  → Agent B responds with HTTP 402 + payment details
  → Agent A pays via Solana transaction
  → Agent B delivers the data
```

### 4.2 Integration with AgentEscrow

```typescript
// x402 handler — enables agent-to-agent micropayments
// For jobs under a threshold, use x402 instead of full escrow

const X402_THRESHOLD = 0.01 SOL; // Below this, use x402

async function handleAgentPayment(
  payer: Keypair,      // Agent A's Swig wallet
  payee: PublicKey,    // Agent B's Swig wallet
  amount: number,      // In lamports
  memo: string,        // "data-fetch:eth-price"
) {
  // Direct SOL transfer with memo (x402 pattern)
  const tx = new Transaction().add(
    SystemProgram.transfer({
      fromPubkey: payer.publicKey,
      toPubkey: payee,
      lamports: amount,
    }),
    // Memo program for payment metadata
    new TransactionInstruction({
      keys: [],
      programId: new PublicKey('MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'),
      data: Buffer.from(memo),
    })
  );
  
  return await sendAndConfirmTransaction(connection, tx, [payer]);
}
```

### 4.3 Dual Payment Model

| Payment Size | Method | Why |
|-------------|--------|-----|
| < 0.01 SOL | x402 direct | Fast, no escrow overhead |
| ≥ 0.01 SOL | JobEscrow PDA | Full protection, dispute resolution |
| Recurring | Swig auto-pay | Subscription-like agent services |

---

## 5. Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| **Programs** | Anchor + Rust | Standard Solana framework |
| **Wallet** | Phantom Adapter | Best UX for human users |
| **Agent Wallets** | Swig | Programmatic wallets for agents |
| **Reputation NFTs** | Metaplex Core | Standard, lightweight |
| **Identity** | World ID | Sybil resistance |
| **Payments** | x402 + SOL/USDC | Agent micropayments |
| **Client** | TypeScript SDK | Demo + integrations |
| **Test** | Anchor + solana-test-validator | Local devnet |
| **Deploy** | Solana Devnet | Hackathon demo |

---

## 6. Directory Structure

```
agent-escrow/
├── Anchor.toml
├── Cargo.toml
├── programs/
│   └── colosseum_programs/
│       └── src/
│           ├── lib.rs              # Entry point + dispatch
│           ├── agent_registry.rs   # Agent registration + World ID
│           ├── job_escrow.rs       # Escrow lifecycle + x402
│           ├── reputation.rs       # Ratings + Metaplex NFT mint
│           ├── dispute_resolver.rs # Dispute resolution
│           └── errors.rs           # Custom error codes
├── client/
│   ├── package.json
│   └── src/
│       ├── index.ts               # SDK entry
│       ├── wallet.ts              # Phantom integration
│       ├── agent.ts               # Registration + Swig
│       ├── escrow.ts              # Job lifecycle
│       ├── reputation.ts          # NFT + ratings
│       ├── world-id.ts            # Verification
│       └── x402.ts                # Micropayment handler
├── demo/
│   ├── demo.py                    # Main demo script
│   ├── DEMO_STORYBOARD.md         # Recording guide
│   └── fixtures/                  # Test data
└── tests/
    ├── agent_registry.test.ts
    ├── job_escrow.test.ts
    ├── reputation.test.ts
    └── integration.test.ts
```

---

## 7. Demo Flow (5 minutes)

### Act 1: Trust Setup (60s)
1. **Human opens Phantom** → connects wallet
2. **Registers agent "CodeBreaker"** → stakes 0.5 SOL
3. **World ID verification** → popup → proof → on-chain ✓
4. **Metaplex NFT minted** → Scout tier reputation NFT

### Act 2: Job Lifecycle (90s)
5. **Posts job** → "Review Solana program for vulns" → 0.5 SOL escrow
6. **Agent "DataMiner" discovers job** → matches capabilities
7. **Swig wallet accepts** → agent signs programmatically
8. **Agent submits work** → IPFS hash on-chain

### Act 3: Settlement (60s)
9. **Human approves** → escrow releases to agent's Swig wallet
10. **Rates agent 5/5** → reputation NFT updates
11. **Agent tier upgrades** → Scout → Rookie (3+ jobs)

### Act 4: Dispute (60s)
12. **Agent "WriterBot" submits bad work**
13. **Human disputes** → reason on-chain
14. **DisputeResolver evaluates** → evidence + resolution
15. **Funds returned** → worker reputation penalized

### Act 5: Agent-to-Agent (30s)
16. **CodeBreaker pays DataMiner** via x402 (0.005 SOL)
17. **DataMiner delivers data** → instant settlement
18. **Both agents' reputation NFTs update**

---

## 8. PDA Derivation

```rust
// Agent PDA — seeded by name
let (agent_pda, agent_bump) = Pubkey::find_program_address(
    &[b"agent", name.as_bytes()],
    &program_id,
);

// Job PDA — seeded by job_id
let (job_pda, job_bump) = Pubkey::find_program_address(
    &[b"job", job_id.as_bytes()],
    &program_id,
);

// Escrow PDA — seeded by job + poster (holds funds)
let (escrow_pda, escrow_bump) = Pubkey::find_program_address(
    &[b"escrow", job_pda.key().as_ref()],
    &program_id,
);

// Dispute PDA — seeded by job
let (dispute_pda, dispute_bump) = Pubkey::find_program_address(
    &[b"dispute", job_pda.key().as_ref()],
    &program_id,
);

// Reputation NFT — seeded by agent
let (rep_nft_pda, rep_bump) = Pubkey::find_program_address(
    &[b"reputation", agent_pda.key().as_ref()],
    &program_id,
);
```

---

## 9. Security Considerations

| Risk | Mitigation |
|------|-----------|
| Reentrancy | Anchor auto-checks; no cross-program calls in critical sections |
| Integer overflow | Rust u64/u32 + Anchor checked math |
| PDA collision | Seeds include unique identifiers (name, job_id) |
| Stuck funds | Deadline-based auto-refund via `expire_job` |
| Sybil attacks | World ID nullifier prevents duplicate humans |
| Fake reputation | Only completed jobs → rating → NFT update |
| Rug pull | Escrow PDA requires both parties' consent for release |
| Admin key compromise | No admin keys — all logic is on-chain |

---

## 10. Build Commands

```bash
# Install
cd agent-escrow
anchor build

# Test
anchor test

# Deploy to devnet
anchor deploy --provider.cluster devnet

# Run demo
cd demo && python3 demo.py
```

---

## 11. Judge Scorecard

| Criterion | How AgentEscrow Wins |
|-----------|---------------------|
| **Technical Depth** | 4 Solana programs, PDA escrow, x402, Metaplex NFTs |
| **Sponsor Utilization** | 4/4 sponsors integrated (Phantom, Swig, Metaplex, World) |
| **Real Problem** | Agent economy needs trust layer — nobody else has this |
| **Demo Quality** | Live on-chain demo with real transactions |
| **Novelty** | First protocol combining escrow + reputation + identity + payments |
| **Completion** | Working prototype with test suite |

---

## 12. Competitive Edge

| Competitor | What They Have | What We Have |
|-----------|---------------|-------------|
| MCPay | Payment middleware | Escrow + reputation + disputes |
| Latinum | Payment routing | Full trust layer |
| Corbits.dev | Stripe for agents | Agent-to-agent marketplace |
| AI Economy Protocol | Agent framework | On-chain identity + NFT reputation |

**Our moat:** Competitors solve payments. We solve **trust**. Payments are a commodity. Trust is infrastructure.

---

*Last updated: 2026-04-28*
*Author: DMOB (Labs)*
*Status: Architecture draft — ready for implementation*
