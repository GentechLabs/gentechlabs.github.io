---
name: evm-to-solana-port
description: Systematic approach to porting Solidity contracts to Anchor/Rust on Solana. Produces a portability matrix mapping each EVM concept to its Solana equivalent.
category: blockchain
---

# EVM to Solana Portability Analysis

Systematic approach to analyzing Solidity contracts for porting to Anchor/Rust on Solana. Produces a portability matrix mapping each EVM concept to its Solana equivalent.

## When to Use
- Porting any Solidity contract to native Solana programs
- Evaluating whether an EVM project can be "one build, multiple pitches" across chains
- Planning Anchor scaffold from existing Foundry codebase

## Methodology

### Step 1: Inventory EVM Contracts
Read each .sol file and catalog:
- Core structs and state variables
- External/public functions (the API surface)
- Events and errors
- External dependencies (OpenZeppelin, etc.)

### Step 2: Classify Portability by Category

**🟢 Direct 1:1 ports** — same logic, different syntax:
- State structs → Anchor account structs with Borsh serialization
- State transitions (enum) → Anchor instruction + account mutability
- ERC20 transfers → SPL Token CPI (`transfer`, `transfer_checked`)
- Time-based logic (`block.timestamp`) → `Clock::get()?.unix_timestamp`
- Access control (`onlyOwner`) → `has_one = authority` constraint
- Cumulative counters → Anchor account fields

**🟡 Needs rethinking** — different paradigm, needs design:
- EIP-712 signatures → Ed25519 program or simple `Signer` checks (actually simpler)
- `ecrecover` → Solana has no ecrecover; use `anchor_lang::solana_program::ed25519_program`
- Global sequential IDs (`nextId++`) → PDA seeds (unique by construction)
- `msg.sender` → `Signer<'info>` or `ctx.accounts.authority.key()`
- Mapping storage → PDA derivation or Anchor account maps

**🔴 Drop entirely** — not needed on Solana:
- `ReentrancyGuard` → Solana has no reentrancy by design
- `SafeERC20` → SPL Token transfers are safe by default
- `approve`/`allowance` → SPL Token has delegated transfers built-in

**🔵 New for Solana** — not in EVM version, needed for native feel:
- Agent identity (PDA-based registry)
- x402 handler (bridges HTTP 402 to on-chain escrow)
- Dispute resolution (separate program for arbitration)

### Step 3: Identify What's Actually Simpler
Solana eliminates entire vulnerability classes. Document what gets dropped:
- No reentrancy attacks possible
- No integer overflow (Rust panics or checked math)
- Account validation enforced by Anchor
- No delegatecall exploits

### Step 4: Generate Anchor Scaffold
For each 🟢 and 🟡 item, produce:
- Anchor account struct
- Instruction handler signature
- Required account validations
- PDA seed scheme

## Common Patterns

### Escrow State Machine (EVM → Anchor)
```solidity
// EVM
enum EscrowState { Created, Completed, Validated, Released, Refunded }
mapping(uint256 => Escrow) public escrows;
```

```rust
// Anchor
#[account]
pub struct Escrow {
    pub buyer: Pubkey,
    pub seller: Pubkey,
    pub amount: u64,
    pub deadline: i64,
    pub state: EscrowState,
    pub created_at: i64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum EscrowState {
    Created,
    Completed,
    Validated,
    Released,
    Refunded,
}
```

### PDA Seeds (replaces sequential IDs)
```rust
#[account(
    init,
    payer = buyer,
    space = 8 + Escrow::LEN,
    seeds = [b"escrow", buyer.key().as_ref(), seller.key().as_ref(), &timestamp.to_le_bytes()],
    bump
)]
pub escrow: Account<'info, Escrow>,
```

### SPL Token Transfer (replaces SafeERC20)
```rust
use anchor_spl::token::{self, Transfer, TokenAccount};

let transfer_ctx = CpiContext::new(
    ctx.accounts.token_program.to_account_info(),
    Transfer {
        from: ctx.accounts.buyer_token.to_account_info(),
        to: ctx.accounts.escrow_token.to_account_info(),
        authority: ctx.accounts.buyer.to_account_info(),
    },
);
token::transfer(transfer_ctx, amount)?;
```

## Pitfalls
- Don't try to replicate mapping-based storage — use PDAs
- Don't forget `bump` in PDA seeds — store it in the account
- SPL Token accounts must be created before first transfer (ATA pattern)
- Rent exemption: Anchor `init` handles this, but be aware of account size limits (10KB)
- Solana has no events — use `msg!()` macro for logging or emit via CPI

## Verification
After porting:
1. Run `anchor test` — should mirror Foundry test coverage
2. Verify all state transitions match EVM behavior
3. Check PDA derivation produces unique accounts per escrow
4. Test timeout/refund logic with `solana-test-validator` clock manipulation
