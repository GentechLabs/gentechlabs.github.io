---
name: solana-hackathon-build
description: |
  Bootstrap a Solana hackathon project from zero — toolchain install, Anchor project init, smart contract scaffolding, off-chain agent setup, and demo video prep. Also covers mid-hackathon sponsor integration: weaving newly announced protocols into existing multi-layer projects across Rust programs, TypeScript SDK, docs, and tests.
tags: [solana, hackathon, anchor, blockchain, smart-contracts]
related_skills: [hackathon-tracker, defi-onchain-position-reader]
---

# Solana Hackathon Build

Set up a complete Solana development environment and bootstrap a hackathon project with smart contracts + off-chain agent.

## When to Use

- Starting a new Solana hackathon project from scratch
- Need to install Solana toolchain (Rust, CLI, Anchor) on a fresh machine
- Scaffolding Anchor programs for a hackathon submission
- Building a Python/JS agent that interacts with Solana programs
- Preparing demo materials for hackathon judges
- **Integrating a new sponsor protocol mid-hackathon** (see Section 8)

## Prerequisites

- Linux (Ubuntu/Debian) or macOS. For Windows: use WSL2 first.
- `curl`, `git` installed
- ~2GB free disk space for toolchain

## 1. Install Solana Toolchain

### Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
rustc --version  # Should be 1.85.0+
```

### Solana CLI (Agave client)
```bash
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
solana --version  # Should be 3.x+
```

### Generate Keypair
```bash
solana-keygen new --no-bip39-passphrase
solana config set --url devnet
```

### Anchor Framework
```bash
cargo install --git https://github.com/coral-xyz/anchor avm --force
avm install latest
avm use latest
anchor --version  # Should be 1.0.x+
```

### Node.js + Yarn (for TypeScript tests)
```bash
npm install -g yarn
```

## 2. Initialize Anchor Project

```bash
anchor init <project-name> --template multiple
cd <project-name>
```

This creates:
- `programs/<project-name>/src/lib.rs` — main entry point
- `programs/<project-name>/src/state/` — account structs
- `programs/<project-name>/src/instructions/` — instruction handlers
- `programs/<project-name>/src/error.rs` — custom errors
- `programs/<project-name>/src/constants.rs` — PDA seeds, limits
- `tests/` — TypeScript or Rust tests
- `Anchor.toml` — project config

### Update Anchor.toml for devnet
```toml
[provider]
cluster = "devnet"
wallet = "~/.config/solana/id.json"
```

## 3. Multi-Program Workspace

For hackathons requiring multiple programs (e.g., escrow + identity + reputation), use Anchor's multiple-program template:

```bash
anchor init <project-name> --template multiple
```

This creates a workspace with `programs/` containing multiple program crates. Add additional programs manually:

```toml
# Anchor.toml
[[programs.genesis]]
program = "AgentRegistry111111111111111111111111111111"
workspace = "programs/agent-registry"

[[programs.genesis]]
program = "JobEscrow111111111111111111111111111111111"
workspace = "programs/job-escrow"
```

```toml
# Root Cargo.toml (workspace)
[workspace]
members = [
    "programs/agent-registry",
    "programs/job-escrow",
    "programs/reputation",
    "programs/dispute-resolver",
]
resolver = "2"

[workspace.dependencies]
anchor-lang = "0.30.1"
```

### Common Multi-Program Patterns

**Shared types crate:**
```
programs/
├── common/           # Shared types, constants, errors
│   └── src/lib.rs
├── agent-registry/
├── job-escrow/
└── reputation/
```

**Cross-program CPI:**
```rust
use anchor_lang::prelude::*;

// Call another program from within a CPI
let cpi_accounts = agent_registry::cpi::accounts::UpdateAgent {
    agent: ctx.accounts.agent.clone(),
    owner: ctx.accounts.owner.clone(),
};
let cpi_program = ctx.accounts.agent_registry_program.clone();
agent_registry::cpi::update_agent(cpi_program, cpi_accounts, new_data)?;
```

### Sponsor Integration Patterns

**Phantom (wallet adapter):**
```typescript
import { useWallet } from '@solana/wallet-adapter-phantom';
const { publicKey, signTransaction } = useWallet();
```

**Swig (programmatic agent wallets):**
```typescript
import { createSwigWallet } from '@swig-wallet/solana';
// Agents get PDA-based wallets that sign via CPI
```

**Metaplex Core (soulbound NFTs):**
```rust
// Non-transferable reputation tokens
use metaplex_core::state::TokenStandard;
// Freeze plugin = soulbound
```

**World ID (Sybil resistance):**
```typescript
import { IDKitWidget } from '@worldcoin/idkit';
// Nullifier hash stored on-chain, prevents double-verification
```

## 4. Smart Contract Patterns

### PDA Account Structure
```rust
#[account]
pub struct MyAccount {
    pub owner: Pubkey,      // 32 bytes
    pub data: u64,          // 8 bytes
    pub bump: u8,           // 1 byte
}
```

### PDA Seeds
```rust
pub fn find_pda(program_id: &Pubkey, seeds: &[&[u8]]) -> (Pubkey, u8) {
    Pubkey::find_program_address(seeds, program_id)
}
```

### Instruction Pattern (Anchor 1.0+)
```rust
pub fn my_instruction(ctx: Context<MyContext>, arg: u64) -> Result<()> {
    let account = &mut ctx.accounts.my_account;
    account.data = arg;
    emit!(MyEvent { data: arg });
    Ok(())
}
```

### Error Handling
```rust
#[error_code]
pub enum ErrorCode {
    #[msg("Unauthorized")]
    Unauthorized,
    #[msg("Invalid amount")]
    InvalidAmount,
}
```

## 4. Build & Test

```bash
# Build programs
anchor build

# Run tests
anchor test

# Deploy to devnet
anchor deploy --provider.cluster devnet
```

### Common Build Issues
- **`anchor-cli` version mismatch**: Check `Anchor.toml` `[toolchain]` section matches installed version
- **Rust compilation errors**: Ensure `rustup update stable`
- **Keypair not found**: Run `solana-keygen new --no-bip39-passphrase`
- **Insufficient SOL**: `solana airdrop 2` on devnet

## 4b. Anchor 0.30.x Compatibility (Older Projects)

Many existing Solana projects (and hackathon starters) use Anchor 0.30.x with `solana-program 1.18`. These are **not compatible with the latest toolchain out of the box.** The critical constraint is **platform-tools Rust version**, not your system Rust.

### Platform-Tools Version Matrix
| Agave CLI | Platform-Tools | Bundled Rust | edition2024? |
|-----------|---------------|-------------|-------------|
| 1.18.x    | 1.41          | 1.75        | ❌          |
| 2.1.x     | 1.43          | 1.79        | ❌          |
| 2.2.x     | 1.47          | 1.84        | ❌ (needs 1.85) |

**None of the current stable Agave releases ship platform-tools with Rust 1.85+.** This means any crate using `edition = "2024"` in its Cargo.toml will fail to compile under `cargo-build-sbf`, regardless of your host Rust version.

### The edition2024 Problem

When `anchor build` or `cargo-build-sbf` fails with:
```
feature `edition2024` is required
The package requires the Cargo feature called `edition2024`, but that feature is not stabilized in this version of Cargo (1.XX.X)
```

This means a transitive dependency has released a version using `edition = "2024"`, and your platform-tools Cargo can't parse it. The fix is to **pin the offending dependency to the last pre-edition2024 version**.

### Dependency Pinning Recipe (Anchor 0.30.x + Agave 2.2.x)

Run these in order from the project root after the first failed build:

```bash
# 1. blake3 1.8.x pulls cpufeatures 0.3.0 (edition2024)
cargo update -p blake3 --precise 1.5.5

# 2. indexmap 2.14.0 uses edition2024 (needed >= 2.13 by toml_edit)
cargo update -p indexmap@2.14.0 --precise 2.13.0

# 3. proc-macro-crate 3.5.0 pulls toml_edit 0.25 + toml_datetime 1.1 (edition2024)
cargo update -p proc-macro-crate@3.5.0 --precise 3.2.0

# 4. borsh 1.6.x may pull newer deps
cargo update -p borsh@1.6.1 --precise 1.5.3

# 5. unicode-segmentation 1.13.x requires rustc 1.85
cargo update -p unicode-segmentation@1.13.2 --precise 1.12.0
```

**Important:** Pin `proc-macro-crate` BEFORE `toml_datetime` — the former is what pulls in the latter. If you try to pin `toml_datetime` directly, cargo will refuse because `toml_edit 0.25.x` requires `toml_datetime ^1.1.1`.

### Workaround: cargo-build-sbf When anchor build Fails on IDL

`anchor build` does two things: (1) compiles programs to `.so` via `cargo-build-sbf`, (2) generates IDL JSON via a separate build. Step 2 often fails on older projects because IDL generation uses the host Rust (not platform-tools) and pulls in different deps.

If `anchor build` fails but you see the programs compiling, **build each program individually**:

```bash
for prog in agent-registry job-escrow reputation dispute-resolver; do
    cargo-build-sbf --manifest-path "programs/$prog/Cargo.toml"
done
```

This skips IDL generation and builds only the BPF binaries. The `.so` files appear in `target/deploy/`. IDLs can be generated later or hand-written for hackathon demos.

### Agave CLI Version Selection

The `anza.xyz/stable` installer sometimes returns a minimal install (missing `solana` binary). **Pin a specific version** instead:

```bash
# Preferred: pin to a known-good version
sh -c "$(curl -sSfL https://release.anza.xyz/v2.2.14/install)"

# Avoid: "stable" may give partial installs
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
```

### Program IDs

`anchor build` auto-generates keypairs in `target/deploy/` and syncs program IDs between `lib.rs` and `Anchor.toml`. Each rebuild may generate new IDs. For devnet deployment, **deploy once and lock the IDs** — don't rebuild unnecessarily after deployment.

## 5. Off-Chain Agent (Python)

For hackathons combining AI agents + Solana:

### Dependencies
```toml
[project]
dependencies = [
    "solana>=0.34.0",
    "solders>=0.21.0",
    "google-adk>=1.0.0",  # If using Google ADK
    "python-dotenv>=1.0.0",
    "aiohttp>=3.9.0",
]
```

### Agent Pattern
```python
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey

class SolanaAgent:
    def __init__(self, rpc_url: str, keypair: Keypair):
        self.client = Client(rpc_url)
        self.keypair = keypair

    def register_on_chain(self, program_id: Pubkey, name: str):
        """Call AgentRegistry program to register agent identity."""
        # Derive PDA for agent account
        # Build instruction data
        # Send transaction
        pass

    def discover_jobs(self, program_id: Pubkey):
        """Read JobEscrow accounts to find open jobs."""
        # Get all accounts owned by program
        # Filter for Open status
        pass
```

### Google Agent Starter Pack
```bash
# Install
uvx agent-starter-pack list  # See available templates
uvx agent-starter-pack create my-agent -a adk_a2a  # ADK + A2A template

# Or use the newer agents CLI
uvx google-agents-cli setup
```

**Important**: `agent-starter-pack` is interactive — pipe input for deployment target selection:
```bash
echo "4" | uvx agent-starter-pack create my-agent -a adk  # "4" = no cloud deployment
```

## 6. Demo Video Prep

Hackathon judges (especially Solana ecosystem) want to see:

1. **The Problem** (30s) — AI agents have no identity/payment rail
2. **The Solution** (30s) — On-chain identity + escrow + reputation
3. **Live Demo** (60s) — Agent registers → takes job → gets paid → reputation updates
4. **Why It Matters** (30s) — Trust layer for agent economy

### Demo Recording Tips
- Use `asciinema` or screen recording for terminal demos
- Show Solana Explorer transactions as proof
- Keep it under 3 minutes
- Sub-second finality is a selling point — emphasize speed

## 7. Submission Checklist

- [ ] GitHub repo with README
- [ ] Demo video (2-3 min)
- [ ] Smart contracts deployed to devnet
- [ ] Agent working end-to-end
- [ ] Architecture diagram
- [ ] Registered on hackathon platform

## 8. Mid-Hackathon Sponsor Integration

When a new protocol/partner announcement drops mid-hackathon and you need to integrate it into an existing project, follow this structured workflow:

### Trigger Conditions
- A sponsor announces a new SDK, plugin, or partnership mid-hackathon
- A protocol you're already watching releases something directly relevant
- Judges would reward composability with an emerging standard
- Team decides to adopt a new sponsor tool after initial scaffolding

### Integration Workflow (5 layers, top-down)

**Layer 1: Evaluate & Decide (10 min)**
- Read the announcement thoroughly — what does it actually provide on-chain?
- Map it to your existing architecture: does it replace something you built, or sit on top?
- Decision framework:
  - **Complementary** (builds on top of your stack) → integrate as a new layer
  - **Competing** (overlaps with something you built) → evaluate if it's better; switch if yes
  - **Parallel** (solves a different problem) → mention in narrative, light integration
- Write a 1-paragraph integration strategy before touching code

**Layer 2: On-Chain Programs (Rust/Anchor)**
- Add new instruction to the relevant program (e.g., `link_metaplex_identity`)
- Add state fields to existing accounts if needed (e.g., `core_asset: Pubkey`)
- Add error variants for the new integration
- Update `instructions/mod.rs` to export the new module
- Update `lib.rs` to register the new instruction
- Fix any `Cargo.toml` issues (e.g., `idl-build` feature referencing nonexistent deps)

**Layer 3: Client SDK (TypeScript)**
- Create a new integration module (e.g., `client/src/oobe.ts`) with:
  - Type definitions for the external protocol's data
  - Functions for the integration flow (create → link → fetch profile)
  - Helper functions (URL builders, status checks)
- Update existing client files to reference the new module
- Update `index.ts` header with integration credits

**Layer 4: Documentation**
- **Submission writeup**: Reposition the project as "built on top of" the new protocol
- **Social thread**: Add a tweet about the partnership; update sponsor list
- **Integration strategy doc**: Architecture diagram, sponsor table, creative positioning
- Key narrative pattern: "[Protocol X] handles [problem]. We handle [problem]. Together: [full-stack claim]."

**Layer 5: Tests & Verification**
- Add integration test stubs in the relevant describe block
- Add E2E lifecycle test that includes the new integration step
- Run `cargo check` (or `anchor build`) to verify programs compile
- If build fails, check: Cargo.toml deps, Rust version, Anchor version mismatch

### Example: OOBE Protocol Integration

**Context:** OOBE announced AgentIdentity plugin for Metaplex Core mid-hackathon. Our agent-registry program already had basic identity. Decision: integrate OOBE as the identity layer rather than rebuilding.

**What changed:**
- `state.rs`: Added `core_asset: Pubkey` field to `AgentAccount`
- `instructions/link_metaplex_identity.rs`: New instruction linking Metaplex Core asset
- `errors.rs`: Added `CoreIdentityAlreadyLinked`, `InvalidCoreAsset`, `IdentityNotLinked`
- `client/src/oobe.ts`: 251-line integration module with types + functions
- `SUBMISSION-WRITEUP.md`: Repositioned as "built on OOBE's identity layer"
- `SOCIAL-THREAD.md`: Added OOBE partnership tweet, updated to 9-tweet thread

**Result:** 5-sponsor integration narrative, composability story for judges.

### Pitfalls

- **Solana CLI PATH**: Must export in every new terminal session, or add to `.bashrc`/`.zshrc`
- **Anchor version lock**: Pin Anchor version in `Anchor.toml` to avoid build mismatches
- **Devnet SOL resets**: Don't store real value on devnet; airdrop limits exist
- **PDA collisions**: Always include owner pubkey in PDA seeds to avoid conflicts
- **Interactive CLIs**: `agent-starter-pack create` and `avm install` may need piped input in non-interactive shells
- **`solana-py` vs `solders`**: `solders` is the lower-level crate; `solana-py` wraps it. Use `solders` for instruction building
- **Multi-program workspaces**: Each program needs its own `Cargo.toml` with `anchor-lang` dependency. Root `Cargo.toml` must list all members.
- **Cross-program CPI**: Use `anchor_lang::program::invoke` or `invoke_signed` for PDA-signed CPIs. Remember to pass the target program's account info.
- **Sponsor SDK versions**: Metaplex Core, Swig, and World ID SDKs may have breaking changes. Pin versions in `package.json` and test early.
- **Platform-tools Rust is the real constraint**: Your system `rustc --version` is irrelevant for BPF builds. `cargo-build-sbf` uses the Rust bundled with Solana platform-tools. Check with: the version printed in `cargo-build-sbf --version` output.
- **edition2024 cascade**: One dep using edition2024 causes a cascade of failures. Always pin the ROOT dep (usually `blake3` or `proc-macro-crate`), not the leaf dep (`cpufeatures` or `toml_datetime`).
- **Gentech profile HOME**: On multi-profile Hermes setups, `HOME=/root/.hermes/profiles/gentech/home`. All tool installs (rustup, cargo, solana) resolve relative to this. Anchor.toml `wallet = "~/.config/solana/id.json"` resolves correctly only if `HOME` is set.

### Scaffolding via Sub-Agent

For complex multi-program workspaces, use `delegate_task` to have a coding agent scaffold the full project. Provide:
1. Architecture doc (program list, account structs, instruction signatures)
2. Sponsor integration requirements
3. Directory structure template
4. Expected output path

This avoids context window limits and produces cleaner code than manual scaffolding.

## Verification

After setup, confirm:
- [ ] `rustc --version` returns 1.85+
- [ ] `solana --version` returns 3.x+ (or 2.2.x for Anchor 0.30.x projects)
- [ ] `anchor --version` matches project's Anchor dependency version
- [ ] `solana config get` shows devnet
- [ ] `anchor build` compiles successfully (or `cargo-build-sbf` for each program)
- [ ] `solana balance` shows SOL (after airdrop)
- [ ] `target/deploy/*.so` files exist for all programs
- [ ] No `edition2024` errors in build output (if Anchor 0.30.x — check dep pins)

### Quick Sanity Check for Anchor 0.30.x Projects
```bash
# Verify platform-tools Rust version
cargo-build-sbf --version  # Look for "rustc X.XX.X" in output

# If edition2024 errors appear, apply the pinning recipe:
cargo update -p blake3 --precise 1.5.5
cargo update -p proc-macro-crate@3.5.0 --precise 3.2.0
cargo update -p indexmap@2.14.0 --precise 2.13.0
```
