---
name: solana-anchor-development
description: "Full Solana/Anchor development workflow — toolchain setup, building, testing, and auditing Anchor programs. Covers Rust toolchain management, Cargo.lock compatibility, workspace configuration, and systematic program review."
category: blockchain
tags:
  - class-level
  - solana
  - anchor
  - rust
  - development
  - umbrella
status: active
---

# Solana/Anchor Development Skill

End-to-end workflow for building, testing, and auditing Solana programs using the Anchor framework. Covers environment setup through production audit.

## When to Use

- Setting up Rust/Anchor toolchain for Solana development
- Building or compiling Anchor workspace programs
- Running tests against local validator
- Systematically reviewing Anchor program code
- Fixing compilation issues (Cargo.lock, dependency conflicts)
- Pre-hackathon or pre-launch program validation

## Prerequisites

- Linux environment (tested on Ubuntu/Debian)
- `curl` and standard build tools (`build-essential`)
- Root or sudo access for system-level installs

---

## 1. Toolchain Setup

### Rust Installation

The system Rust is often too old for modern Solana dependencies. Install via rustup:

```bash
# MUST set these to avoid HOME directory conflicts in containerized environments
export RUSTUP_HOME=/root/.rustup
export CARGO_HOME=/root/.cargo

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable

# Source the env
source /root/.cargo/env

# Verify — need 1.85+ for Anchor 0.30.x, 1.95+ recommended
rustc --version
cargo --version
```

**Pitfall**: If `$HOME` differs from euid-obtained home (common in containers), rustup will fail with `$HOME differs from euid-obtained home directory`. Setting `RUSTUP_HOME` and `CARGO_HOME` explicitly to `/root/` paths works around this.

### Anchor CLI

```bash
# Install via avm (Anchor Version Manager) or direct
cargo install --git https://github.com/coral-xyz/anchor avm --locked
avm install latest
avm use latest

# Verify
anchor --version
# Should show anchor-cli 0.30.x or 1.0.x
```

### Solana CLI

```bash
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
solana --version
```

---

## 2. Workspace Structure

Standard Anchor workspace layout:

```
project/
├── Anchor.toml          # Anchor config (program IDs, test config)
├── Cargo.toml           # Workspace root (members list)
├── programs/
│   ├── program-a/
│   │   ├── Cargo.toml   # Program dependencies
│   │   └── src/
│   │       ├── lib.rs   # Entry point + instruction dispatch
│   │       ├── state.rs # Account structs + enums
│   │       ├── errors.rs # Custom error codes
│   │       └── instructions/
│   │           ├── mod.rs
│   │           └── *.rs  # One file per instruction
│   └── program-b/
│       └── ...
└── tests/
    └── *.ts             # TypeScript integration tests
```

### Cargo.toml (workspace root)

```toml
[workspace]
members = [
    "programs/program-a",
    "programs/program-b",
]
resolver = "2"

[workspace.metadata.anchor]
anchor-version = "0.30.1"

[profile.release]
overflow-checks = true
lto = "fat"
codegen-units = 1
opt-level = 3
```

### Program Cargo.toml

```toml
[package]
name = "program-name"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib", "lib"]
name = "program_name"

[features]
default = []
no-entrypoint = []
no-idl = []
no-log-ix-name = []
cpi = ["no-entrypoint"]
idl-build = ["anchor-lang/idl-build"]

[dependencies]
anchor-lang = { version = "0.30.1", features = ["init-if-needed"] }
# Add anchor-spl, solana-program as needed
```

**Pitfall**: `crate-type` must include both `"cdylib"` (for BPF deployment) and `"lib"` (for testing/CPI). Missing `"cdylib"` = won't deploy. Missing `"lib"` = can't test.

---

## 3. Building

### First Build

```bash
cd /path/to/workspace

# If Cargo.lock is v4 but Rust < 1.85, regenerate it
rm -f Cargo.lock
cargo generate-lockfile

# Check compilation (faster than full build)
cargo check 2>&1 | tail -40

# Full build
cargo build 2>&1 | tail -40
```

### Common Build Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `lock file version 4 requires -Znext-lockfile-bump` | Cargo.lock v4 + old Rust | `rm Cargo.lock && cargo generate-lockfile` |
| `feature edition2024 is required` | Dependency needs newer Rust | Upgrade Rust: `rustup update stable` |
| `$HOME differs from euid-obtained home` | Container env | Set `RUSTUP_HOME=/root/.rustup CARGO_HOME=/root/.cargo` |
| `unexpected cfg condition value: anchor-debug` | Anchor version vs Rust mismatch | Cosmetic warning, safe to ignore |

### Anchor Build

```bash
# Full Anchor build (generates IDL + BPF programs)
anchor build

# Build specific program
anchor build -- --package program-name
```

### Fallback: `cargo-build-sbf` (When Anchor CLI Fails)

Anchor CLI versions may not compile or may panic on version mismatches. The Solana CLI ships `cargo-build-sbf` which is what `anchor build` calls under the hood. Use it directly:

```bash
# Requires Solana CLI installed (see Solana CLI section above)
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Build a specific program
cargo-build-sbf --manifest-path programs/my-program/Cargo.toml

# Build all programs in workspace (loop)
for prog in program-a program-b program-c; do
  echo "=== Building $prog ==="
  cargo-build-sbf --manifest-path programs/$prog/Cargo.toml 2>&1 | tail -5
done
```

**When to use `cargo-build-sbf` directly:**
- Anchor CLI 0.30.1 fails to compile on Rust 1.95+ (time crate incompatibility)
- Anchor CLI 1.0.1 panics with `No such file or directory` when project uses anchor-lang 0.30.1
- You only need to verify compilation, not generate IDL
- CI environment where Anchor CLI install is slow

**Note:** `cargo-build-sbf` does NOT generate IDL files. For IDL generation, you need a working Anchor CLI. For hackathon submissions where compilation proof matters more than IDL, `cargo-build-sbf` is sufficient.

---

## 4. Testing

### TypeScript Integration Tests

```bash
# Run all tests
anchor test

# Run with local validator
anchor test --provider.cluster localnet

# Or manually with ts-mocha
yarn run ts-mocha -p ./tsconfig.json -t 1000000 tests/**/*.ts
```

### Test Structure

```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey } from "@solana/web3.js";
import { expect } from "chai";

describe("program-name", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.ProgramName;

  it("Does something", async () => {
    const account = anchor.web3.Keypair.generate();
    await program.methods
      .initialize(/* args */)
      .accounts({
        account: account.publicKey,
        signer: provider.wallet.publicKey,
      })
      .signers([account])
      .rpc();

    const data = await program.account.someAccount.fetch(account.publicKey);
    expect(data.field).to.equal(expectedValue);
  });
});
```

**Pitfall**: All tests as `expect(true).to.be.true` are stubs. They pass but test nothing. Real tests must call program methods and assert on fetched account state.

### Rust Unit Tests

Add `#[cfg(test)]` modules for logic that doesn't need Solana runtime:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tier_calculation() {
        let agent = AgentAccount { /* mock */ };
        assert_eq!(agent.tier(), AgentTier::Scout);
    }
}
```

---

## 5. Systematic Audit Methodology

When reviewing Anchor programs, follow this sequence:

### Phase 1: Compilation Check
```bash
cargo check 2>&1 | grep -E "^error" | wc -l
# Must be 0 errors
```

### Phase 2: State Definition Review
For each program's `state.rs`:
- Account structs have `#[account]` and `#[derive(InitSpace)]`
- All fields have explicit types (no `Option<T>` without reason)
- PDA seed constants defined
- Enum variants cover all lifecycle states

### Phase 3: Instruction Handler Review
For each instruction file:
- Account constraints enforce access control (`constraint =`, `has_one =`)
- Signer checks on authority accounts (`Signer<'info>`)
- Status transitions are valid (check enum `can_*()` methods)
- Fund transfers use CPI or direct lamport manipulation correctly
- No arithmetic without `checked_*` methods

### Phase 4: Fund Flow Audit
For programs handling money:
- Escrow pattern: funds move in on init, out on completion/refund
- `claimed` flag prevents double-withdrawal
- Deadline-based refund logic is correct
- Dispute resolution actually transfers funds (not just marks resolved)

### Phase 5: Cross-Program References
- Program IDs in `declare_id!()` match deployment
- CPI calls validate target program ID
- Shared state accounts (if any) use consistent PDA seeds

### See Also
- `references/anchor-common-bugs.md` — patterns we've found in real audits
- `references/bpf-toolchain-compat.md` — BPF rustc version pinning, Anchor CLI compatibility matrix
- `solana-vulnerability-scanner` — 6 critical vulnerability patterns

---

## 6. Pitfalls

1. **Cargo.lock version mismatch** — Solana repos often have v4 lockfiles from CI. Regenerate with `cargo generate-lockfile` on your local Rust version.

2. **HOME directory in containers** — rustup, cargo, and solana CLI all use `$HOME` for state. In containers where `$HOME != ~root`, set `RUSTUP_HOME`, `CARGO_HOME`, and `SOLANA_HOME` explicitly.

3. **Anchor warnings are usually safe** — `anchor-debug` cfg warnings and ambiguous glob re-exports are cosmetic. Focus on actual errors.

4. **`init_if_needed` is dangerous** — It initializes an account if it doesn't exist, but can be exploited if the discriminator check is wrong. Use `init` + separate init instruction when possible.

5. **Fixed-size arrays for strings** — `[u8; N]` with a `len` field is the Anchor pattern for variable-length strings. Don't forget to validate `len <= N` in every instruction.

6. **PDA bump must be stored** — Always save `ctx.bumps.account_name` in the account state. Never let users provide bump values.

7. **Escrow vaults need `claimed` flag** — Without it, double-refund or double-release is possible. The flag must be set atomically with the fund transfer.

8. **Dispute resolution must transfer funds** — Marking a dispute as "resolved" without moving escrow funds is a common scaffolding bug. Always trace the money.

9. **BPF toolchain has old rustc** — The Solana CLI ships platform-tools with rustc ~1.79.0-dev. Modern transitive dependencies (e.g., `unicode-segmentation >= 1.13`) may require rustc 1.85+. Build will fail with `rustc X is not supported by the following package`. Fix: pin the dependency to an older compatible version:
   ```bash
   cargo update unicode-segmentation@1.13.2 --precise 1.11.0
   ```
   The error message tells you the exact package and minimum rustc version. Pin to the latest version that supports the BPF toolchain's rustc.

10. **Init constraint on owner always fails** — If an account is being `init`ed, its fields are all zeros. A constraint like `constraint = account.owner == signer.key()` on the signer account will fail because `account.owner` is `Pubkey::default()` during init. Remove the constraint from the signer in init instructions; validate ownership in update/deactivate instructions instead.

---

## Verification

```bash
# 1. Toolchain check
source /root/.cargo/env && rustc --version && anchor --version

# 2. Compilation check
cd /path/to/workspace && cargo check 2>&1 | grep "^error" | wc -l
# Should output: 0

# 3. Test check
anchor test 2>&1 | tail -5
# Should show passing tests (not just stubs)
```
