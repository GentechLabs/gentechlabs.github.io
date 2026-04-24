---
name: anchor-solana-escrow
description: Anchor 1.0 Solana program development — setup, common errors, and idiomatic patterns for on-chain escrow/payment contracts.
category: smart-contract
---

# Anchor Solana Escrow Development

## Environment Setup

Install order (none are in PATH by default):
1. **Rust** — see rustup.rs, then `source "$HOME/.cargo/env"`
2. **Solana CLI** — see docs.anza.xyz/cli/install, installs to `~/.local/share/solana/install/active_release/bin/`
3. **AVM** — `cargo install --git https://github.com/coral-xyz/anchor avm --locked`, then `avm install latest`
4. **Yarn** — `npm install -g yarn` (needed by `anchor init`)

Always set PATH explicitly:
```bash
export PATH="$HOME/.cargo/bin:$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

## Anchor 1.0 Compilation Gotchas

### 1. `CpiContext::new` takes `Pubkey`, not `AccountInfo`
Anchor 1.0 changed the first argument:
```rust
// WRONG (old API):
let ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), ...);
// CORRECT (Anchor 1.0):
let ctx = CpiContext::new(ctx.accounts.token_program.key(), ...);
// Same for CpiContext::new_with_signer
```

### 2. `anchor-spl` needs `idl-build` feature
SPL token types (`Mint`, `TokenAccount`) fail with `no function create_type found` without it:
```toml
# Cargo.toml
[features]
idl-build = ["anchor-lang/idl-build", "anchor-spl/idl-build"]
```

### 3. Glob re-export ambiguity with `handler` names
Multiple instruction modules with `pub fn handler()` cause ambiguous re-exports when glob-imported. Rename each:
```rust
pub fn initialize_handler(...) { ... }
pub fn create_escrow_handler(...) { ... }
pub fn release_funds_handler(...) { ... }
```

### 4. `solana-program` as explicit dependency
Needed for types like `solana_program::sysvar::instructions::*`. Add explicitly:
```toml
[dependencies]
anchor-lang = "1.0.0"
anchor-spl = "1.0.0"
solana-program = "3.0.0"
```

### 5. Ed25519 on-chain verification
`solana_program::ed25519_program::verify` does NOT exist. Use the **precompile pattern** instead:
- Off-chain: Validator signs `(data)` with Ed25519 key
- Client: Builds tx with `[Ed25519PrecompileIx, your_instruction]`
- Runtime: Verifies precompile before your program runs
- Program: Trusts the precompile verification (optionally check instruction sysvar for defense-in-depth)

## Idiomatic Escrow Pattern

### PDA State Layout
```
EscrowConfig PDA [b"config"]       — singleton, global settings
Escrow PDA [b"escrow", id.to_le_bytes()]  — one per escrow
Vault TokenAccount [b"escrow", id, b"vault"] — SPL token, authority = escrow PDA
```

### SPL Token Transfer (buyer → vault)
```rust
let transfer_ctx = CpiContext::new(
    ctx.accounts.token_program.key(),
    Transfer {
        from: ctx.accounts.buyer_token.to_account_info(),
        to: ctx.accounts.vault.to_account_info(),
        authority: ctx.accounts.buyer.to_account_info(),
    },
);
token::transfer(transfer_ctx, amount)?;
```

### SPL Token Transfer from PDA vault (vault → seller)
```rust
let seeds = &[b"escrow", &id.to_le_bytes(), &[bump]];
let signer_seeds = &[&seeds[..]];

let ctx = CpiContext::new_with_signer(
    ctx.accounts.token_program.key(),
    Transfer {
        from: vault.to_account_info(),
        to: seller_token.to_account_info(),
        authority: escrow.to_account_info(),
    },
    signer_seeds,
);
token::transfer(ctx, amount)?;
```

## Security Audit Checklist for Escrow Programs

### Critical: Ed25519 Precompile Pubkey Verification
The precompile pattern trusts that the runtime verified a signature, but **does NOT check WHO signed**. Without an instruction sysvar check, any valid Ed25519 signature from any keypair can validate an escrow.

**Defense-in-depth fix** — read the InstructionsSysvar and extract the precompile ix pubkey:
```rust
use solana_program::sysvar::instructions::load_instruction_at_checked;

pub fn handler_validate_signed(ctx: Context<ValidateWork>, timestamp: i64) -> Result<()> {
    let ixs = ctx.accounts.instructions.to_account_info();
    let ed25519_ix = load_instruction_at_checked(0, &ixs)
        .map_err(|_| EscrowError::InvalidSignature)?;

    // Ed25519 precompile layout: pubkey starts at byte 16 (after header)
    let precompile_pubkey_bytes: [u8; 32] = ed25519_ix.data[16..48]
        .try_into()
        .map_err(|_| EscrowError::InvalidSignature)?;
    let precompile_pubkey = Pubkey::new_from_array(precompile_pubkey_bytes);

    require_keys_eq!(
        precompile_pubkey,
        ctx.accounts.config.ai_validator,
        EscrowError::InvalidSignature
    );

    // Optional: also verify the signed message contains escrow_id + timestamp

    apply_validation(&mut ctx.accounts.escrow)
}
```

Account struct addition:
```rust
/// CHECK: Instructions sysvar — used to read precompile ix
#[account(address = solana_program::sysvar::instructions::ID)]
pub instructions: UncheckedAccount<'info>,
```

### Other Audit Checks
- **Replay protection**: `AlreadyValidated` + `EscrowAlreadyCompleted` constraints on escrow state
- **Token mint validation**: Always constrain `buyer_token.mint == config.usdc_mint` on create/release
- **Self-transfer guard**: `buyer_token.key() != vault.key()` prevents drain via refund to vault
- **PDA authority**: Vault `token::authority` must be the escrow PDA, not the program or a signer
- **Seller unchecked**: `seller` in CreateEscrow is intentionally unconstrained (buyer chooses) — document the tradeoff

## Pitfalls
- `anchor test` tries to spawn `surfpool` — may fail on headless servers. Use `cargo test` for unit tests instead.
- Solana CLI installs to a non-standard path — always set PATH explicitly.
- `init` constraint for token accounts needs `token::mint` and `token::authority` — not `associated` like in older Anchor versions.
- EVM mental model (mappings, msg.sender, ERC20 transferFrom) does NOT map directly — think in PDAs, CPIs, and signer seeds.

## Built: agent-escrow-solana (Apr 21 2026)

Native Solana AgentEscrow — compiled, pushed to github.com/ProtoJay4789/agent-escrow-solana.

- **7 instructions**: initialize, create_escrow, validate_work, validate_with_signature, release_funds, refund_buyer, update_validator
- **State**: EscrowConfig PDA (singleton) + per-escrow PDAs + SPL token vaults
- **Ed25519 precompile**: Validator signs off-chain, runtime verifies before program runs
- **Build**: `anchor build` → `target/deploy/agent_escrow_solana.so` + IDL JSON
- **Tests**: 2 placeholder unit tests (need LiteSVM integration tests)

### Next Build Priorities
1. **x402 middleware** — wire PayAI facilitator to escrow (Axum server + `x402-axum` crate)
2. **AgentRegistry Solana** — PDA per agent, skills/reputation, mirrors EVM AgentRegistry.sol
3. **Enhanced lifecycle** — add accept_job + dispute/resolve_dispute instructions
4. **Devnet deploy** — `solana program deploy` + TypeScript client
5. **UNWANTED NFT collection** (P2) — Metaplex Core, B&W sticker aesthetic, agent identity NFTs
