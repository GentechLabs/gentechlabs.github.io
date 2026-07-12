# Solana/Anchor Cheat Sheet for EVM Developers

> Created: 2026-04-18 | Purpose: Quick reference for EVM devs jumping to Solana
> Target: Hackathon prep (May 11), future security auditing career path

---

## 🧠 Mental Model Translation

| EVM World | Solana World |
|---|---|
| Contract = code + state together | **Program** = stateless code. **Accounts** = separate data |
| `msg.sender` is automatic | You pass the **signer account** explicitly |
| Storage slots (256-bit words) | **Account data** (raw bytes, you define structure) |
| Deploy contract → gets address | Deploy program → gets **Program ID** (random keypair) |
| `CREATE2` for deterministic addresses | **PDAs** (Program Derived Addresses) for deterministic accounts |
| `require()` reverts everything | `require!()` macro, same effect, Rust syntax |
| Events (`emit`) | **No events** — use `msg!()` for logs (indexers parse these) |
| Proxy upgrades (complex) | **Built-in upgrade authority** (or make immutable) |
| Gas paid by caller | **Compute units** + **rent** for storage |

---

## 🔧 Environment Setup (One-Time)

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Solana CLI (v2.x latest)
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"

# Install Anchor (Solana's "Hardhat")
cargo install --git https://github.com/coral-xyz/anchor avm --force
avm install latest
avm use latest

# Verify
solana --version    # Should be 2.x
anchor --version    # Should be 0.30+
rustc --version     # Should be 1.75+

# Set to devnet
solana config set --url devnet
solana-keygen new --outfile ~/.config/solana/id.json
solana airdrop 2   # Get free devnet SOL
```

---

## 📁 Anchor Project Structure

```
my-escrow/
├── Anchor.toml          # Config (like hardhat.config.js)
├── Cargo.toml           # Rust dependencies
├── programs/
│   └── my-escrow/
│       ├── Cargo.toml
│       └── src/
│           └── lib.rs   # Your program (like contracts/)
├── tests/
│   └── my-escrow.ts     # TypeScript tests (like test/)
├── app/                 # Frontend (optional)
└── migrations/
    └── deploy.ts        # Deploy script
```

**Key file: `Anchor.toml`**
```toml
[programs.devnet]
my_escrow = "YourProgramIdHere"

[provider]
cluster = "devnet"
wallet = "~/.config/solana/id.json"
```

---

## 📦 Solidity → Anchor Syntax Cheat

### Program Entry Point

**Solidity:**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Escrow {
    mapping(address => uint256) public balances;
    
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
}
```

**Anchor:**
```rust
use anchor_lang::prelude::*;

declare_id!("YourProgramIdHere");

#[program]
pub mod my_escrow {
    use super::*;

    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;
        escrow.amount += amount;
        
        // Transfer SOL from buyer to escrow account
        let ix = anchor_lang::system_program::Transfer {
            from: ctx.accounts.buyer.to_account_info(),
            to: ctx.accounts.vault.to_account_info(),
        };
        anchor_lang::system_program::transfer(
            CpiContext::new(ctx.accounts.system_program.to_account_info(), ix),
            amount,
        )?;
        
        Ok(())
    }
}

// Account validation struct (the "require" equivalent)
#[derive(Accounts)]
pub struct Deposit<'info> {
    #[account(mut)]
    pub buyer: Signer<'info>,                    // Who's signing (like msg.sender)
    
    #[account(
        init_if_needed,                          // Create if doesn't exist
        payer = buyer,                           // Who pays for account creation
        space = 8 + 32 + 8 + 1,                 // 8 (discriminator) + 32 (pubkey) + 8 (u64) + 1 (bool)
        seeds = [b"escrow", buyer.key().as_ref()], // PDA seeds
        bump                                     // PDA bump
    )]
    pub escrow: Account<'info, EscrowState>,     // Your state account
    
    #[account(mut)]
    /// CHECK: Vault PDA for holding SOL
    pub vault: UncheckedAccount<'info>,
    
    pub system_program: Program<'info, System>,  // Required for SOL transfers
}

// State struct (like your contract storage)
#[account]
pub struct EscrowState {
    pub buyer: Pubkey,
    pub amount: u64,
    pub is_complete: bool,
}
```

---

## 🔑 Key Concepts Mapped

### 1. Storage / State

**EVM:** `mapping(address => uint256) public balances;` — lives inside contract

**Solana:** State lives in **separate accounts**. You create them, size them, pay rent.

```rust
// In Anchor, state is defined as a struct:
#[account]
pub struct EscrowState {
    pub buyer: Pubkey,      // 32 bytes
    pub amount: u64,        // 8 bytes
    pub is_complete: bool,  // 1 byte
}

// Space calculation (CRITICAL — get this wrong, account creation fails):
// 8 (Anchor discriminator) + 32 + 8 + 1 = 49 bytes
// Always round up to 8-byte boundary: use 49 or 56
```

**Discriminator:** Anchor prefixes every account with 8 bytes (hash of struct name). You must include this in `space`.

### 2. Access Control

**EVM:**
```solidity
modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    _;
}
```

**Anchor:** Validated in the account struct:
```rust
#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(
        mut,
        has_one = owner  // ← This IS your "onlyOwner" modifier
    )]
    pub escrow: Account<'info, EscrowState>,
    
    pub owner: Signer<'info>,  // Must match escrow.owner
}
```

**Common constraints:**
- `has_one = field` — account.field must match another account
- `constraint = expr` — arbitrary boolean check
- `Signer<'info>` — account must have signed the transaction
- `#[account(mut)]` — account is writable
- `#[account(address = pubkey)]` — account must match specific pubkey

### 3. Token Handling

**EVM:** You write ERC-20 from scratch (or import OpenZeppelin)

**Solana:** SPL Token is a **standard program** — you interact with it via CPI:
```rust
use anchor_spl::token::{self, Transfer, TokenAccount, Token};

pub fn transfer_tokens(ctx: Context<TransferTokens>, amount: u64) -> Result<()> {
    let transfer_ctx = CpiContext::new(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.source.to_account_info(),
            to: ctx.accounts.destination.to_account_info(),
            authority: ctx.accounts.authority.to_account_info(),
        },
    );
    token::transfer(transfer_ctx, amount)?;
    Ok(())
}
```

### 4. PDA (Program Derived Address)

**EVM equivalent:** `CREATE2` with salt

**Solana:** Deterministic address derived from seeds + program ID. No private key — only the program can sign for it.

```rust
// Creating a PDA account
#[account(
    init,
    payer = user,
    space = 8 + 32,
    seeds = [b"config", user.key().as_ref()],  // Seeds make it deterministic
    bump                                      // Bump = nonce to find valid address
)]
pub config: Account<'info, Config>,

// Finding a PDA in TypeScript (tests/client)
const [configPDA, bump] = PublicKey.findProgramAddressSync(
    [Buffer.from("config"), user.publicKey.toBuffer()],
    programId
);
```

### 5. Cross-Program Invocation (CPI)

**EVM:** `otherContract.someFunction()` — external call

**Solana:** CPI — you pass accounts to another program:
```rust
// Calling another Anchor program
let cpi_ctx = CpiContext::new(
    ctx.accounts.other_program.to_account_info(),
    other_program::cpi::accounts::DoSomething {
        account_a: ctx.accounts.account_a.to_account_info(),
        account_b: ctx.accounts.account_b.to_account_info(),
    },
);
other_program::cpi::do_something(cpi_ctx, args)?;
```

---

## ⚠️ Security Patterns (EVM → Solana)

| EVM Vulnerability | Solana Equivalent | How to Prevent |
|---|---|---|
| Reentrancy | **Not possible** (single runtime lock) | N/A — but watch for **CPI reentrancy** in older patterns |
| Missing access control | **Missing signer check** | Always use `Signer<'info>` for authorized accounts |
| Integer overflow | **Rust panics** (not wrapping) | Rust 1.67+ auto-panics. Use `checked_*` for explicit handling |
| tx.origin phishing | **Account substitution** | Use `constraint =` or `has_one =` to validate accounts |
| Unchecked return values | **Unchecked accounts** | Never use `UncheckedAccount` without `/// CHECK:` and validation |
| Storage collision | **Account data corruption** | Use Anchor's `#[account]` — it handles serialization safely |
| Frontrunning | **MEV / Jito bundles** | Similar problem, different solution (Jito tips) |
| Denial of service | **Compute exhaustion** | Solana has compute unit limits per transaction |

### Top Solana-Specific Attack Vectors (for your security career)

1. **Missing account validation** — #1 bug. Passing wrong accounts to bypass checks
2. **Duplicate mutable accounts** — passing same account twice in different slots
3. **PDA privilege escalation** — creating PDAs that mimic authority
4. **Account data confusion** — not checking account owner (who initialized it)
5. **Rent drain** — forcing creation of many accounts to drain SOL
6. **Insufficient space allocation** — writing past account data bounds

---

## 🧪 Testing Pattern (TypeScript)

```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MyEscrow } from "../target/types/my_escrow";
import { expect } from "chai";

describe("my-escrow", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.MyEscrow as Program<MyEscrow>;
  const buyer = provider.wallet;

  it("Creates escrow", async () => {
    // Derive PDA
    const [escrowPDA] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("escrow"), buyer.publicKey.toBuffer()],
      program.programId
    );

    // Call program
    await program.methods
      .deposit(new anchor.BN(1_000_000)) // 0.001 SOL
      .accounts({
        buyer: buyer.publicKey,
        escrow: escrowPDA,
        systemProgram: anchor.web3.SystemProgram.programId,
      } as any)
      .rpc();

    // Verify
    const escrow = await program.account.escrowState.fetch(escrowPDA);
    expect(escrow.amount.toNumber()).to.equal(1_000_000);
  });
});
```

**Run tests:**
```bash
anchor test    # Builds + starts local validator + runs tests
# or
anchor test --skip-local-validator  # If validator already running
```

---

## 🚀 Deploy Workflow

```bash
# Build
anchor build

# Get your program ID
solana address -k target/deploy/my_escrow-keypair.json

# Update Anchor.toml and lib.rs with the real program ID
# Then rebuild:
anchor build

# Deploy to devnet
anchor deploy --provider.cluster devnet

# Verify deployment
solana program show <PROGRAM_ID> --url devnet
```

---

## 📚 Best Resources (EVM-Dev Friendly)

### Crash Courses (Pick One)
1. **Solana Bootcamp (Official)** — YouTube, free, ~6 hours
2. **Anchor Docs "Quick Start"** — gets you from zero to deployed in 2 hours
3. **"Solana for EVM devs" blog posts** — several exist, search this exact phrase

### Deep Dives
- **Solana Cookbook** — recipes for common patterns
- **Anchor Book** — framework-specific reference
- **Sealevel (Solana runtime)** — understand the parallel execution model

### Security
- **Neodyme blog** — Solana security research
- **OtterSec** — audit reports and attack pattern writeups
- **Solana CTF challenges** — Wormhole, Marinade, etc.

---

## 🎯 Hackathon Minimum Viable Checklist

For May 11 — get these working:

- [ ] `anchor init` creates project
- [ ] Can write a struct with `#[account]`
- [ ] Can write an instruction with `#[derive(Accounts)]`
- [ ] Can create a PDA account
- [ ] Can transfer SOL between accounts
- [ ] Can write a basic test in TypeScript
- [ ] Can deploy to devnet
- [ ] Can call deployed program from tests

**Bonus (impress judges):**
- [ ] SPL token transfer (not just SOL)
- [ ] Frontend with wallet adapter
- [ ] Multiple instructions (create, execute, cancel)

---

*Last updated: 2026-04-18 by YoYo*
*Save location: 06-Reference/Solana-Anchor-EVM-Cheat-Sheet.md*
