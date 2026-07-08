# Solana for EVM Devs — Cheat Sheet
> A quick-reference guide for Solidity/Foundry devs stepping into Solana + Anchor.
> Created: 2026-04-18

---

## 🧠 The One Sentence That Explains Everything

**EVM:** Code + data live together inside contracts.
**Solana:** Code (programs) is *stateless*. Data lives in *accounts* you create separately.

If you internalize this, everything else clicks faster.

---

## 🔄 Concept Mapping: EVM → Solana

| EVM Concept | Solana Equivalent | Key Difference |
|---|---|---|
| Smart Contract | **Program** (stateless) | Programs can't store data themselves |
| Contract storage | **Accounts** (PDAs or signer accounts) | You create accounts *before* using them |
| `deploy` | `solana program deploy` | Programs are immutable by default (upgradeable with upgrade authority) |
| `msg.sender` | `ctx.accounts.signer` | Always passed explicitly |
| `address(this)` | **PDA** (Program Derived Address) | Deterministic, no private key, owned by program |
| `mapping` | Custom account + PDA seeds | You derive a unique account per key manually |
| `event` | **Events** (via Anchor `emit!`) | Similar but logged differently |
| `modifier` | Anchor **constraints** (`#[account(...)]`) | Declarative validation on accounts |
| `constructor` | `initialize` instruction | One-time setup is just another instruction |
| `receive()` / `fallback` | ❌ Doesn't exist | Solana has no "catch-all" |
| Gas | **Compute units** (1.4M max per tx) | Similar concept, different limits |

---

## 🏗️ Anchor Project Structure (≈ Hardhat/Foundry)

```
my-anchor-project/
├── Anchor.toml          # Like hardhat.config.js
├── Cargo.toml           # Rust dependencies (like package.json)
├── programs/
│   └── my_program/
│       ├── Cargo.toml
│       └── src/
│           └── lib.rs   # ≈ Your main .sol contract
├── tests/
│   └── my-program.ts    # TypeScript tests (like JS tests in Hardhat)
├── app/                 # Frontend (optional)
└── migrations/
    └── deploy.ts
```

---

## ✍️ Side-by-Side: Token Vault

### Solidity (EVM)
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TokenVault {
    mapping(address => uint256) public balances;
    
    event Deposited(address indexed user, uint256 amount);
    
    function deposit() external payable {
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }
    
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient");
        balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
    }
}
```

### Anchor (Solana)
```rust
use anchor_lang::prelude::*;

declare_id!("YourProgramIdHere1111111111111111111111");

#[program]
pub mod token_vault {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        ctx.accounts.vault.balance = 0;
        ctx.accounts.vault.authority = ctx.accounts.user.key();
        Ok(())
    }

    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {
        // Transfer SOL from user to vault PDA
        let ix = anchor_lang::solana_program::system_instruction::transfer(
            &ctx.accounts.user.key(),
            &ctx.accounts.vault_pda.key(),
            amount,
        );
        anchor_lang::solana_program::program::invoke(
            &ix,
            &[
                ctx.accounts.user.to_account_info(),
                ctx.accounts.vault_pda.to_account_info(),
            ],
        )?;
        ctx.accounts.vault.balance += amount;
        emit!(Deposited {
            user: ctx.accounts.user.key(),
            amount,
        });
        Ok(())
    }

    pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
        let vault = &mut ctx.accounts.vault;
        require!(vault.balance >= amount, VaultError::InsufficientBalance);
        
        // Transfer SOL from vault PDA back to user
        **ctx.accounts.vault_pda.try_borrow_mut_lamports()? -= amount;
        **ctx.accounts.user.try_borrow_mut_lamports()? += amount;
        
        vault.balance -= amount;
        Ok(())
    }
}

// Account structs (this is where EVM devs get tripped up)
#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = user,
        space = 8 + 32 + 8, // 8 (discriminator) + 32 (pubkey) + 8 (u64)
        seeds = [b"vault", user.key().as_ref()],
        bump
    )]
    pub vault: Account<'info, VaultState>,
    /// CHECK: This is a PDA, safe
    #[account(seeds = [b"vault", user.key().as_ref()], bump)]
    pub vault_pda: UncheckedAccount<'info>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Deposit<'info> {
    #[account(mut, seeds = [b"vault", user.key().as_ref()], bump)]
    pub vault: Account<'info, VaultState>,
    /// CHECK: PDA holding SOL
    #[account(mut, seeds = [b"vault", user.key().as_ref()], bump)]
    pub vault_pda: UncheckedAccount<'info>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(mut, seeds = [b"vault", user.key().as_ref()], bump, has_one = authority)]
    pub vault: Account<'info, VaultState>,
    /// CHECK: PDA holding SOL
    #[account(mut, seeds = [b"vault", user.key().as_ref()], bump)]
    pub vault_pda: UncheckedAccount<'info>,
    pub authority: Signer<'info>,
    #[account(mut)]
    pub user: SystemAccount<'info>,
}

#[account]
pub struct VaultState {
    pub authority: Pubkey,
    pub balance: u64,
}

#[event]
pub struct Deposited {
    pub user: Pubkey,
    pub amount: u64,
}

#[error_code]
pub enum VaultError {
    #[msg("Insufficient balance")]
    InsufficientBalance,
}
```

> **Notice:** The Solana version has ~3x the lines. Most of it is account definitions. That's normal — Anchor is verbose but safe.

---

## 🧩 PDAs — The Big Concept

**PDA = Program Derived Address**

Think of it as a *deterministic keyless address* owned by your program.

```rust
// EVM equivalent: mapping(address => Vault) — one vault per user
// Solana: derive a unique PDA per user

let (vault_pda, bump) = Pubkey::find_program_address(
    &[b"vault", user.key().as_ref()],  // seeds
    &program_id,                        // program that owns it
);
```

**Why it matters:**
- PDAs have **no private key** — only your program can sign for them
- They're deterministic — same seeds = same address every time
- They replace `mapping`, `msg.sender` checks, and access control patterns

---

## ⚡ Quick Command Reference

| Task | EVM (Foundry) | Solana (Anchor) |
|---|---|---|
| Init project | `forge init` | `anchor init my_project` |
| Build | `forge build` | `anchor build` |
| Test | `forge test` | `anchor test` |
| Deploy (local) | `forge script --broadcast` | `anchor deploy` |
| Deploy (devnet) | `forge script --rpc-url sepolia` | `anchor deploy --provider.cluster devnet` |
| Run local node | `anvil` | `solana-test-validator` |
| Check balance | `cast balance` | `solana balance` |
| Send tx | `cast send` | `solana transfer` |
| Get account | `cast call` | `solana account <pubkey>` |
| Verify contract | `forge verify-contract` | `anchor verify <program_id>` |

---

## 🚨 Common Gotchas (EVM → Solana)

### 1. "Where's my state variable?"
There are no state variables on programs. You need to create an **account** for every piece of storage.

### 2. "Why is my transaction too large?"
Solana tx limit is **1232 bytes**. If you're passing too many accounts or large data, you hit this. Solution: split into multiple txs or compress.

### 3. "Why do I need to specify account size?"
`space = 8 + 32 + 8` — you calculate exact bytes upfront. If your struct has a `String` or `Vec`, it gets worse (need to allocate max size).

### 4. "What's the 8-byte discriminator?"
Anchor prepends an 8-byte hash to every account to identify its type. Always account for it in `space` calculations.

### 5. "How do I do a reentrancy?"
You don't — Solana's runtime prevents it. The same account can't be mutably borrowed twice in one instruction. Free security.

### 6. "Where's the equivalent of `approve`/`transferFrom`?"
Solana's SPL Token program has `approve` + `transfer` too, but the mechanics are different (token accounts with delegates).

---

## 📚 Learning Path (Suggested Order)

1. **Rust basics** — [Rust Book Ch 1-10](https://doc.rust-lang.org/book/) (skip macros chapter)
2. **Solana concepts** — [Solana Cookbook](https://solanacookbook.com/)
3. **Anchor framework** — [Anchor Docs](https://www.anchor-lang.com/)
4. **Build something** — Clone a simple escrow or staking contract
5. **Solana Program Library (SPL)** — Token, Associated Token Account programs
6. **Gigastaking angle** — Research Marinade, Jito, Sanctum for liquid staking patterns

---

## 🎯 For Gentech Specifically

Given our GigaStaking + AAE platform context:
- **Liquid staking on Solana:** Look at Marinade (mSAL), Jito (jitoSOL), Sanctum (LST aggregation)
- **Agent economy patterns:** PDAs map well to per-agent escrow/vault patterns
- **Social AI + Solana:** Dialect, Solana Actions/Blinks for on-chain social integration
- **Tooling we already know:** TypeScript for tests transfers directly from our Foundry JS scripts

---

## 🔗 Key Resources

| Resource | URL |
|---|---|
| Anchor Docs | https://www.anchor-lang.com |
| Solana Cookbook | https://solanacookbook.com |
| Solana Playground (browser IDE) | https://beta.solpg.io |
| Anchor Examples | https://github.com/coral-xyz/anchor/tree/master/examples |
| Seahorse (Python → Anchor) | https://seahorse-lang.org |
| Solana Stack Exchange | https://solana.stackexchange.com |

> **Pro tip:** [Solana Playground](https://beta.solpg.io) lets you build + deploy Anchor programs in the browser. Zero setup. Start there.

---

*Last updated: 2026-04-18 by Desmond*
