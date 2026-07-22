# EVM → Solana Port Map: What Translates

> Mapping existing AAE Solidity contracts to Anchor/Rust programs

---

## What We Have (EVM/Avalanche)

| Contract | Lines | Purpose | Status |
|---|---|---|---|
| `AgentRegistry.sol` | 223 | On-chain agent identity, skills, reputation | ✅ Written, tested |
| `JobEscrow.sol` | 238 | Agent-to-agent job escrow with USDC | ✅ Written, tested |
| `AgentMarketplace.sol` | 169 | Discovery + one-click hiring | ✅ Written |
| `AgentNFT.sol` | — | Lifecycle + burn floor mechanics | ✅ Written |
| `AgentToken.sol` | — | Per-agent token | ✅ Written |
| `AgentTokenFactory.sol` | — | Token creation | ✅ Written |
| `TECH.sol` | — | Protocol token | ✅ Written |
| `SharedMemory.sol` | — | Cross-agent state | ✅ Written |
| `AgentCoordinator.sol` | — | Multi-agent orchestration | ✅ Written |
| `StrategyVault.sol` | — | Strategy storage | ✅ Written |

**Total: 10 contracts, all written. Tests passing (44 tests).**

---

## What Ports to Solana (Anchor/Rust)

### Direct Port: AgentRegistry.sol → `agent_registry`

**EVM Pattern:**
```solidity
mapping(uint256 => Agent) public agents;
mapping(address => uint256) public agentIdByOwner;

struct Agent {
    uint256 id;
    address owner;
    string metadataURI;
    string[] skills;
    uint256 pricePerJob;
    uint256 reputationScore;
    uint256 jobsCompleted;
    bool isActive;
}
```

**Solana Pattern:**
```rust
// PDA-based: one account per agent, derived from owner pubkey
#[account]
pub struct AgentProfile {
    pub owner: Pubkey,
    pub metadata_uri: String,
    pub skills: Vec<String>,
    pub price_per_job: u64,        // in lamports or USDC amount
    pub reputation_score: u64,     // 0-10000
    pub jobs_completed: u64,
    pub is_active: bool,
    pub bump: u8,
}

// Seeds: ["agent", owner.key().as_ref()]
```

**Key translation:**
| EVM | Solana |
|---|---|
| `mapping(address => Agent)` | PDA derived from `["agent", owner]` |
| `address` | `Pubkey` |
| `uint256` | `u64` (sufficient for our use) |
| `string[]` | `Vec<String>` |
| `msg.sender` | `ctx.accounts.owner.key()` |
| `block.timestamp` | `Clock::get()?.unix_timestamp` |

---

### Direct Port: JobEscrow.sol → `agent_escrow`

**EVM Pattern:**
```solidity
mapping(uint256 => Job) public jobs;

enum JobState { Created, Accepted, Completed, Approved, Disputed, Refunded }

function createJob(address agent, string description, uint256 deadline) external payable;
function approveJob(uint256 jobId) external;
function disputeJob(uint256 jobId) external;
function refundExpired(uint256 jobId) external;
```

**Solana Pattern:**
```rust
#[account]
pub struct Job {
    pub id: u64,
    pub creator: Pubkey,
    pub agent: Pubkey,
    pub description: String,
    pub payment: u64,           // USDC or SOL amount
    pub fee: u64,
    pub deadline: i64,
    pub state: JobState,
    pub created_at: i64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum JobState {
    Created,
    Accepted,
    Completed,
    Approved,
    Disputed,
    Refunded,
}

// Seeds: ["job", creator.key().as_ref(), job_counter.to_le_bytes().as_ref()]
```

**Key translation:**
| EVM | Solana |
|---|---|
| `mapping(uint256 => Job)` | PDA per job, sequential ID from counter |
| `payable` function | SOL transfer via `system_program::transfer` |
| USDC payment | SPL Token transfer via CPI to Token Program |
| Reentrancy guard | **Not needed** — Solana doesn't have reentrancy |
| Pull-over-push | PDA authority pattern (program signs for transfers) |

**Escrow pattern on Solana:**
```rust
// Create: transfer USDC from creator to escrow PDA
anchor_spl::token::transfer(
    CpiContext::new(
        ctx.accounts.token_program.to_account_info(),
        anchor_spl::token::Transfer {
            from: ctx.accounts.creator_token.to_account_info(),
            to: ctx.accounts.escrow_token.to_account_info(),  // PDA-owned token account
            authority: ctx.accounts.creator.to_account_info(),
        },
    ),
    payment_amount,
)?;

// Approve: transfer from escrow PDA to agent
anchor_spl::token::transfer(
    CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        anchor_spl::token::Transfer {
            from: ctx.accounts.escrow_token.to_account_info(),
            to: ctx.accounts.agent_token.to_account_info(),
            authority: ctx.accounts.escrow.to_account_info(),
        },
        &[&[b"escrow", escrow_seed, &[bump]]],  // PDA signs
    ),
    agent_payment,
)?;
```

---

### Direct Port: AgentMarketplace.sol → `agent_marketplace`

**EVM Pattern:**
```solidity
function hireAgent(address agent, string description, uint256 deadline) external payable;
function getActiveAgents(uint256 offset, uint256 limit) external view;
function getAgentsBySkill(string skill, uint256 offset, uint256 limit) external view;
```

**Solana Pattern:**
```rust
pub fn hire_agent(
    ctx: Context<HireAgent>,
    description: String,
    deadline: i64,
) -> Result<()> {
    // Verify agent is active
    require!(ctx.accounts.agent_profile.is_active, EscrowError::AgentNotActive);
    
    // Create job via CPI to escrow program
    let cpi_accounts = CreateJob {
        creator: ctx.accounts.creator.clone(),
        agent: ctx.accounts.agent.clone(),
        // ... escrow accounts
    };
    let cpi_ctx = CpiContext::new(ctx.accounts.escrow_program.to_account_info(), cpi_accounts);
    agent_escrow::cpi::create_job(cpi_ctx, description, deadline)?;
    
    Ok(())
}
```

**Key insight**: Solana doesn't have on-chain iteration like EVM (too expensive). For "get active agents" queries:
- **Option A**: Off-chain indexing (The Graph equivalent: Helius, Triton)
- **Option B**: Event-driven — emit events, index off-chain
- **Option C**: PDA derivation — derive agent PDAs from known seeds

**For hackathon**: Use Option A (Helius API) for discovery, keep programs focused on core logic.

---

### New: x402 Handler (Solana-Specific)

This doesn't exist on EVM side — it's new for the Solana build:

```rust
#[program]
pub mod x402_handler {
    use super::*;

    /// Called when an agent receives a 402 Payment Required response
    /// Verifies the payment, creates escrow, all in one transaction
    pub fn process_x402_payment(
        ctx: Context<ProcessX402Payment>,
        payment_amount: u64,
        service_endpoint: String,
    ) -> Result<()> {
        // 1. Verify USDC transfer from buyer to escrow
        anchor_spl::token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                anchor_spl::token::Transfer {
                    from: ctx.accounts.buyer_token.to_account_info(),
                    to: ctx.accounts.escrow_token.to_account_info(),
                    authority: ctx.accounts.buyer.to_account_info(),
                },
            ),
            payment_amount,
        )?;

        // 2. Create job record
        let job = &mut ctx.accounts.job;
        job.creator = ctx.accounts.buyer.key();
        job.payment = payment_amount;
        job.state = JobState::Created;
        // ... rest of job init

        // 3. Emit event for off-chain tracking
        emit!(X402PaymentProcessed {
            job_id: job.id,
            buyer: ctx.accounts.buyer.key(),
            amount: payment_amount,
            service: service_endpoint,
        });

        Ok(())
    }
}
```

---

## What Doesn't Port (Solana-Specific Changes)

| EVM Feature | Solana Equivalent | Change Required |
|---|---|---|
| `mapping` storage | PDAs | Redesign data model |
| Contract storage | Account data | All state in accounts |
| `msg.sender` | `ctx.accounts.signer` | Different access pattern |
| `block.timestamp` | `Clock::get()` | Clock sysvar |
| Events (`emit`) | Anchor events | `emit!(EventName { ... })` |
| `require()` | `require!()` macro | Similar syntax |
| Reentrancy guards | **Not needed** | Remove entirely |
| `address(0)` checks | `Pubkey::default()` | Different check |
| `uint256` | `u64` | Sufficient for our scale |
| OpenZeppelin | Anchor built-in | No import needed |
| Foundry tests | Anchor tests (TS) | Rewrite in TypeScript |

---

## What Stays on EVM (Not Porting)

For the Colosseum hackathon, we focus on the **core payment stack**:

| Contract | Port? | Reason |
|---|---|---|
| `AgentRegistry` | ✅ Yes | Core identity |
| `JobEscrow` | ✅ Yes | Core escrow |
| `AgentMarketplace` | ✅ Yes | Discovery layer |
| `x402Handler` | 🆕 New | Solana-native x402 |
| `AgentNFT` | ❌ No | Not needed for hackathon |
| `AgentToken` | ❌ No | Phase 2 |
| `AgentTokenFactory` | ❌ No | Phase 2 |
| `TECH.sol` | ❌ No | EVM token, separate concern |
| `SharedMemory` | ❌ No | Complex, Phase 2 |
| `AgentCoordinator` | ❌ No | Complex, Phase 2 |

**Hackathon scope: 3 existing ports + 1 new = 4 programs**

---

## Implementation Order

| Week | Program | Why This Order |
|---|---|---|
| **Week 1** | `agent_registry` | Foundation — everything depends on identity |
| **Week 2** | `agent_escrow` | Core value prop — the escrow |
| **Week 3** | `x402_handler` | Differentiation — x402 integration |
| **Week 4** | `agent_marketplace` | Polish — discovery + one-click hiring |

---

## Resource Mapping

| EVM Resource | Solana Equivalent |
|---|---|
| `@openzeppelin/contracts` | Anchor built-in + `anchor_spl` |
| `forge-std` | `anchor-lang` test framework |
| Foundry (`forge test`) | `anchor test` |
| Hardhat | Anchor CLI |
| `ethers.js` | `@solana/web3.js` + `@coral-xyz/anchor` |
| Avalanche C-Chain | Solana Devnet → Mainnet |
| USDC (ERC-20) | USDC (SPL Token) |
| Etherscan | Solscan / Explorer.solana.com |

---

*Created: Apr 21, 2026*
*For: DMOB + Jordan — Solana native build reference*
*Source: `/root/gentech/aae-contracts/src/`*
