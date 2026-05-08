# Common Anchor Program Bugs

Patterns found in real audits. Each includes the bug, why it's wrong, and the fix.

---

## 1. Backwards Constraint on First-Mint Guard

**Bug**: Constraint prevents first mint by requiring non-default value that doesn't exist yet.

```rust
// WRONG — blocks first mint because asset_id IS default on init
#[account(
    mut,
    seeds = [REPUTATION_NFT_SEED, agent.as_ref()],
    bump = reputation_nft.bump,
    constraint = !reputation_nft.asset_id.eq(&Pubkey::default()) @ Error::AlreadyMinted,
)]
pub reputation_nft: Account<'info, ReputationNft>,
```

**Fix**: Remove constraint from account validation. Check in handler instead:

```rust
// CORRECT — check in handler, not constraint
pub fn handler(ctx: Context<MintNft>) -> Result<()> {
    let rep_nft = &mut ctx.accounts.reputation_nft;
    // First mint: asset_id is default, that's fine
    // Subsequent mints: check in a separate "update" instruction
    rep_nft.asset_id = ctx.accounts.new_asset.key();
    Ok(())
}
```

**Pattern**: Any "first time only" check that uses `constraint` on account init will fail because the account starts at default values.

---

## 1b. Init Constraint on Owner Signer (Variant of #1)

**Bug**: Signer account has `constraint = linked_account.owner == signer.key()` but the linked account is being `init`ed (all zeros).

```rust
// WRONG — agent_account.owner is Pubkey::default() during init, never matches
#[derive(Accounts)]
pub struct RegisterAgent<'info> {
    #[account(
        mut,
        constraint = agent_account.owner == owner.key() @ Error::Unauthorized,  // ← FAILS
    )]
    pub owner: Signer<'info>,

    #[account(
        init,
        payer = owner,
        seeds = [AGENT_SEED, owner.key().as_ref()],
        bump,
    )]
    pub agent_account: Account<'info, AgentAccount>,
}
```

**Fix**: Remove the constraint from the init instruction's signer. Add ownership check in update/deactivate instructions instead:

```rust
// CORRECT — init instruction: no ownership constraint (account doesn't exist yet)
#[derive(Accounts)]
pub struct RegisterAgent<'info> {
    #[account(mut)]
    pub owner: Signer<'info>,

    #[account(
        init,
        payer = owner,
        seeds = [AGENT_SEED, owner.key().as_ref()],
        bump,
    )]
    pub agent_account: Account<'info, AgentAccount>,
}

// CORRECT — update instruction: ownership constraint on existing account
#[derive(Accounts)]
pub struct UpdateAgent<'info> {
    #[account(
        mut,
        constraint = agent_account.owner == owner.key() @ Error::Unauthorized,  // ← OK here
    )]
    pub owner: Signer<'info>,

    #[account(mut, seeds = [AGENT_SEED, owner.key().as_ref()], bump)]
    pub agent_account: Account<'info, AgentAccount>,
}
```

**Pattern**: Ownership constraints only work on existing accounts. For init instructions, the signer IS the owner by virtue of PDA derivation (seeds include their pubkey).

---

## 2. Dispute Resolution Without Fund Transfer

**Bug**: Dispute is marked "resolved" but escrow funds never move.

```rust
// WRONG — just sets a flag, money stays locked
pub fn handler(ctx: Context<ResolveDispute>) -> Result<()> {
    let dispute = &mut ctx.accounts.dispute_account;
    dispute.status = DisputeStatus::Resolved;
    dispute.resolved = true;
    // Where does the money go? Nowhere.
    Ok(())
}
```

**Fix**: Resolution instruction must include escrow vault and transfer funds:

```rust
#[derive(Accounts)]
pub struct ResolveDispute<'info> {
    pub resolver: Signer<'info>,
    #[account(mut)]
    pub dispute_account: Account<'info, DisputeAccount>,
    // ADD: escrow vault
    #[account(mut, seeds = [ESCROW_SEED, dispute_account.job.as_ref()], bump)]
    pub escrow_vault: Account<'info, EscrowVault>,
    // ADD: recipient accounts
    #[account(mut, constraint = poster.key() == dispute_account.poster)]
    pub poster: AccountInfo<'info>,
    #[account(mut, constraint = worker.key() == dispute_account.worker)]
    pub worker: AccountInfo<'info>,
    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<ResolveDispute>, ...) -> Result<()> {
    // ... resolve dispute ...
    
    // ACTUALLY MOVE THE MONEY
    match outcome {
        ResolutionOutcome::PosterWins => {
            **ctx.accounts.escrow_vault.to_account_info().try_borrow_mut_lamports()? -= amount;
            **ctx.accounts.poster.to_account_info().try_borrow_mut_lamports()? += amount;
        }
        ResolutionOutcome::WorkerWins => {
            **ctx.accounts.escrow_vault.to_account_info().try_borrow_mut_lamports()? -= amount;
            **ctx.accounts.worker.to_account_info().try_borrow_mut_lamports()? += amount;
        }
        ResolutionOutcome::Split { poster_share_bps } => {
            let poster_share = amount * poster_share_bps as u64 / 10000;
            let worker_share = amount - poster_share;
            // transfer both
        }
        _ => {}
    }
    
    ctx.accounts.escrow_vault.claimed = true;
    Ok(())
}
```

**Pattern**: Always trace the money. If an instruction changes a status that should move funds, the funds must move in that same instruction.

---

## 3. Job ID Counter Race Condition

**Bug**: Job ID is user-provided but validated against a counter PDA. If counter starts at 0 and user passes 0, the check `job_id == counter.count` passes but the PDA seed `[b"job", &0u64.to_le_bytes()]` might collide with initialization.

```rust
// Fragile — counter starts at 0, job_id=0 passes check
let counter = &mut ctx.accounts.job_counter;
if counter.count == 0 {
    counter.count = 1; // Sets to 1 AFTER the check
}
require!(job_id == counter.count, Error::InvalidJobStatus);
```

**Fix**: Initialize counter to 1, or use `init_if_needed` with proper discriminator:

```rust
// Better — counter starts at 1, first job is job_id=1
let counter = &mut ctx.accounts.job_counter;
if counter.count == 0 {
    counter.count = 1;
    counter.bump = ctx.bumps.job_counter;
}
require!(job_id == counter.count, Error::InvalidJobStatus);
counter.count = counter.count.checked_add(1).ok_or(Error::Overflow)?;
```

---

## 4. Placeholder CPI Calls

**Bug**: CPI to external programs (Metaplex, SPL Token) is commented out, using placeholder values.

```rust
// WRONG — asset_id is just the agent's pubkey, not a real Metaplex asset
rep_nft.asset_id = ctx.accounts.agent.key();
```

**Fix**: Either implement the real CPI or document it as incomplete:

```rust
// Option A: Real CPI (when ready)
let cpi_accounts = mpl_core::CreateV1 { /* ... */ };
let cpi_program = ctx.accounts.metaplex_program.to_account_info();
mpl_core::cpi::create_v1(cpi_program, cpi_accounts)?;

// Option B: Explicit stub with TODO
msg!("⚠️ STUB: Metaplex CPI not yet implemented");
rep_nft.asset_id = ctx.accounts.agent.key(); // placeholder
```

**Pattern**: Never leave a stub without a `msg!()` or comment marking it as incomplete.

---

## 5. Missing Self-Assignment Check

**Bug**: Worker can accept their own job, creating a circular escrow.

```rust
// WRONG — no check that worker != poster
pub fn handler(ctx: Context<AcceptJob>) -> Result<()> {
    let job = &mut ctx.accounts.job_account;
    job.worker = ctx.accounts.worker.key();
    job.status = JobStatus::Accepted;
    Ok(())
}
```

**Fix**:

```rust
require!(
    ctx.accounts.worker.key() != job.poster,
    JobEscrowError::SelfAssignment
);
```

---

## 6. Ambiguous Glob Re-Exports

**Bug**: Multiple instruction modules all export `handler`, causing compiler warnings.

```rust
// In instructions/mod.rs
pub use register_agent::*;
pub use update_agent::*;
pub use deactivate_agent::*;
// All three export `handler` — ambiguous!
```

**Fix**: Use explicit imports or rename handlers:

```rust
// Option A: Explicit imports
pub use register_agent::handler as register_agent_handler;
pub use update_agent::handler as update_agent_handler;

// Option B: Keep glob but rename handlers
// In register_agent.rs: pub fn register_agent_handler(...) {}
// In update_agent.rs: pub fn update_agent_handler(...) {}
```

---

## 7. Fixed-Size Array String Handling

**Bug**: String passed as `[u8; N]` but `len` field not validated in instruction.

```rust
// State struct has:
pub name: [u8; 64],
pub name_len: u16,

// Instruction doesn't validate len
pub fn handler(ctx: Context<Register>, name: [u8; 64], name_len: u16) -> Result<()> {
    let agent = &mut ctx.accounts.agent_account;
    agent.name = name;
    agent.name_len = name_len; // Could be > 64!
    Ok(())
}
```

**Fix**: Always validate length:

```rust
require!(name_len <= MAX_NAME_LENGTH as u16, Error::NameTooLong);
```

---

## Summary Checklist

Before deploying any Anchor program:

- [ ] No backwards constraints on first-mint/first-init patterns (including owner signer on init)
- [ ] All status changes that should move funds DO move funds
- [ ] Job/resource IDs are validated against counters properly
- [ ] No placeholder CPI calls without explicit `msg!()` marking
- [ ] Self-assignment checks on all accept/claim instructions
- [ ] No ambiguous glob re-exports (or handled via rename)
- [ ] All `[u8; N]` string fields validate `len <= N`
- [ ] PDA bumps are stored in account state, never user-provided
- [ ] `claimed` flags on all escrow vaults prevent double-withdrawal
