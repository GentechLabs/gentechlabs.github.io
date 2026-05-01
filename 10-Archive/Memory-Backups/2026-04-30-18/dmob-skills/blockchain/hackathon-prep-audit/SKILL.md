---
name: hackathon-prep-audit
description: "Blockchain hackathon preparation: install dev tools, clone repos, audit smart contracts for security, produce gap analysis, and run mid-hackathon sprint reviews against submission deadlines."
version: 1.0.0
author: DMOB
license: MIT
metadata:
  hermes:
    tags: [hackathon, solidity, anchor, solana, security-audit, smart-contracts, foundry]
    related_skills: [codebase-inspection, github-repo-management]
prerequisites:
  commands: [forge, anchor, solana, git, cargo]
---

# Blockchain Hackathon Preparation Audit

End-to-end workflow for preparing hackathon submissions: environment setup, codebase audit, security review, and gap analysis.

## When to Use

- Starting work on a new hackathon submission
- Onboarding to an existing smart contract codebase
- After a reinstall/environment reset — need to rebuild dev toolchain
- Before a submission deadline — assess what's done vs what's missing
- Jordan says "look at the repos and tell me what we've got"
- Mid-hackathon status check — "review", "what's left", "what are we looking at"
- After new technical research (e.g., protocol deep dive) — assess integration fit

## Phase 1: Environment Setup

### Install Dev Tools

```bash
# Foundry (EVM/Solidity)
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc && ~/.foundry/bin/foundryup

# Solana CLI
sh -c "$(curl -sSfL https://release.anza.xyz/v2.1.21/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
solana config set --url devnet

# Anchor via AVM (requires Rust)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install 0.30.1 && avm use 0.30.1

# Verify
forge --version && anchor --version && solana --version
```

### Clone Repos

```bash
mkdir -p ~/repos && cd ~/repos
git clone https://github.com/ORG/repo-name.git
```

## Phase 2: Codebase Audit (Use Subagents)

For each repo, run a parallel audit via `delegate_task`. Audit template:

```
Audit the [REPO] at ~/repos/[REPO]/. Read ALL contracts, tests, scripts, README, config.
Provide:
1. Contract inventory — what each does, lines, purpose
2. Test coverage — what's tested, what's missing
3. Security findings — list by severity (CRITICAL/HIGH/MEDIUM/LOW/INFO)
4. OpenZeppelin usage — correct? missing patterns?
5. Incomplete/stub functions
6. Deployment scripts — exist? correct?
7. Code quality rating (1-5 stars)
8. What's missing for hackathon submission
```

### Security Checklist (Solidity)

Every contract review MUST check:
- [ ] ReentrancyGuard on all state-changing functions with external calls
- [ ] Checks-Effects-Interactions pattern
- [ ] Access control (onlyOwner, roles, or signature verification)
- [ ] Integer overflow (Solidity 0.8+ has built-in, but check unchecked blocks)
- [ ] SafeERC20 for all token transfers
- [ ] Custom errors vs require strings (gas efficiency)
- [ ] Event emissions on state changes
- [ ] Signature replay protection (EIP-712 domain separator)
- [ ] Front-running vulnerabilities (especially for DEX-related contracts)
- [ ] Oracle manipulation risks
- [ ] Upgradeability patterns (if applicable)

### Security Checklist (Anchor/Solana)

- [ ] Signer checks on all privileged instructions
- [ ] Account validation (PDA seeds, bump seeds, owner checks)
- [ ] Rent exemption for all accounts
- [ ] Close account pattern (return rent to user)
- [ ] CPI guard checks
- [ ] No duplicate account reuse in same instruction

## Phase 3: Vault Brain Dive

Search the vault for context:

```bash
# Find hackathon-related files
grep -r "hackathon" /root/vaults/gentech/02-Labs/ --include="*.md" -l

# Find handoff docs
ls /root/vaults/gentech/09-Green Room/*handoff*.md

# Find specs and architecture
ls /root/vaults/gentech/02-Labs/Hackathons/
```

Key files to read:
- `02-Labs/Hackathons/Active/` — active hackathon specs
- `09-Green Room/*handoff*.md` — context from other agents
- `02-Labs/AAE-Reference/` — architecture and naming
- `09-Green Room/IResolver-interface-spec.md` — dispute resolution design

## Phase 4: Gap Analysis

Compare existing code against submission requirements:

| Requirement | Status | Effort | Priority |
|-------------|--------|--------|----------|
| [feature] | ✅ Done / ❌ Missing / ⚠️ Partial | [hours] | 🔴/🟡/🟢 |

### Time Estimation Rule of Thumb

- Fix security issue: 30min-2hr
- Port Solidity → Anchor: 4-6hr per contract
- Build demo UI: 4-8hr
- Write submission docs: 2-3hr
- Record demo video: 2-4hr
- Deploy to testnet: 1-2hr

### Sprint Planning

```
Available hours = days remaining × productive hours/day (usually 4)
If total effort > available hours → prioritize:
1. Security fixes (always first)
2. Core contracts (Registry, Escrow)
3. Deployment + tests
4. Demo UI
5. Documentation
6. Nice-to-haves
```

## Phase 5: Remediation (Fix Issues Found)

After identifying issues, fix them in priority order:

### Common Solidity Fixes

**Add ReentrancyGuard:**
```solidity
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
contract MyContract is ReentrancyGuard {
    function withdraw() external nonReentrant { ... }
}
```

**Fix CEI (Checks-Effects-Interactions) violations:**
```solidity
// ❌ BAD — state update after external call
token.safeTransfer(addr, amount);
totalSent += amount;

// ✅ GOOD — state update before external call
totalSent += amount;
token.safeTransfer(addr, amount);
```

**Add missing tests for untested functions:**
```solidity
function test_createEscrowWithDeadline() public {
    uint256 deadline = block.timestamp + 30 days;
    vm.prank(buyer);
    uint256 id = escrow.createEscrowWithDeadline(seller, AMOUNT, deadline);
    (, , , uint256 d, , ) = escrow.getEscrow(id);
    assertEq(d, deadline);
}
```

**Standardize error handling (replace require strings with custom errors):**
```solidity
// ❌ require(_treasury != address(0), "ZeroAddress");
// ✅ if (_treasury == address(0)) revert ZeroAddress();
```

### Anchor/Solana Scaffolding Pattern

When porting Solidity → Anchor, create this file structure:
```
programs/my-program/src/
├── lib.rs              # declare_id! + #[program] dispatch
├── state.rs            # #[account] structs (PDA state)
├── errors.rs           # #[error_code] enum
└── instructions/
    ├── mod.rs          # re-exports
    ├── instruction_a.rs
    └── instruction_b.rs
```

Each instruction file contains:
- `#[derive(Accounts)]` struct with PDA validation
- Handler function with business logic
- CPI calls to other programs if needed

**Multi-program pattern:** For hackathons with 3+ programs (e.g., Registry + Escrow + Reputation + DisputeResolver), put each as a separate module in `src/` and re-export via `lib.rs`. Dispatch via `mod_name::function_name(ctx, args)` in the `#[program]` block. Use `delegate_task` subagents to write modules in parallel — each subagent gets the shared account structs and error enum as context.

## Phase 5b: Anchor Build & Fix Cycle

After scaffolding, run the build-fix cycle:

```bash
# 1. Initial build (expect errors)
cd colosseum-programs && anchor build 2>&1 | tail -20

# 2. Check for version mismatches
anchor --version          # CLI version
grep 'anchor-lang' programs/*/Cargo.toml  # library version
# If mismatch: avm install <lib-version> && avm use <lib-version>

# 3. Check rust-toolchain.toml
cat rust-toolchain.toml
# Must be >= 1.82 for edition2024 crates (indexmap, etc.)
# If pinned to old version, update: channel = "1.95.0"

# 4. Fix test compilation
# Tests reference instruction structs that change when you add/remove instructions
# Always rewrite test_initialize.rs to test a real instruction, not a deleted one

# 5. Iterate until clean
anchor build 2>&1 | grep "^error" | head -5
# Should produce 0 errors, only warnings
```

### Common Anchor Compilation Errors & Fixes

When building multi-program Anchor workspaces, these errors recur frequently. Fix them in this order:

**1. Corrupted pubkeys (31 bytes instead of 32)**
```
error: pubkey array is not 32 bytes long: len=31
```
Cause: base58 address has a typo or was truncated. Verify with Python:
```python
import base58
addr = "THE_ADDRESS_HERE"
print(f"Bytes: {len(base58.b58decode(addr))}")  # Must be 32
```
Fix: Look up the correct program ID (search GitHub/web for the official address). For placeholder addresses (e.g., World ID verifier), generate a valid 32-byte one:
```python
import base58, os
base58.b58encode(os.urandom(32)).decode()  # Valid 32-byte placeholder
```

**2. Missing `solana_program` dependency**
```
error[E0433]: failed to resolve: could not find `solana_program`
```
Fix: Add `solana-program = "1.18"` to the program's `Cargo.toml`:
```toml
[dependencies]
anchor-lang = { version = "0.30.1", features = ["init-if-needed"] }
solana-program = "1.18"
```
Alternatively, use `use anchor_lang::solana_program;` if the dependency is already transitively available.

**3. Missing derives on enums/structs**
```
error[E0277]: the trait bound `JobStatus: anchor_lang::Space` is not satisfied
error[E0277]: `ResolutionOutcome` doesn't implement `Debug`
```
Fix: Add `#[derive(InitSpace)]` to any enum/struct used in `space = 8 + Foo::INIT_SPACE`. Add `Debug` to any type used in `msg!()` format strings:
```rust
#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq, Debug, InitSpace)]
pub enum JobStatus { Open, Accepted, Submitted, ... }
```

**4. `u16` vs `usize` type mismatches in require! macros**
```
error[E0308]: mismatched types — expected `u16`, found `usize`
```
Cause: Constants defined as `usize` (e.g., `MAX_NAME_LENGTH: usize = 64`) compared against `u16` instruction args.
Fix: Cast the constant: `name_len <= MAX_NAME_LENGTH as u16`

**5. Borrow checker violations in lamport transfers**
```
error[E0502]: cannot borrow `ctx.accounts.vault` as immutable because it is also borrowed as mutable
```
Cause: `let vault = &mut ctx.accounts.vault;` then later `ctx.accounts.vault.to_account_info()`.
Fix: Get `AccountInfo` references BEFORE the mutable borrow, or use `ctx.accounts.X` directly:
```rust
// ✅ Correct pattern
let payment = ctx.accounts.escrow_vault.amount;
let vault_info = ctx.accounts.escrow_vault.to_account_info();
let worker_info = ctx.accounts.worker.to_account_info();
**vault_info.try_borrow_mut_lamports()? -= payment;
**worker_info.try_borrow_mut_lamports()? += payment;
ctx.accounts.escrow_vault.claimed = true;
```
Note: `Account<T>` doesn't have `try_borrow_mut_lamports()` — always call `.to_account_info()` first.

**6. `has_one` vs explicit constraint for Pubkey comparison**
```
error[E0277]: can't compare `&Pubkey` with `Pubkey`
```
Cause: `has_one = owner` may fail with certain Anchor versions or account types.
Fix: Replace with explicit constraint:
```rust
#[account(
    mut,
    constraint = agent_account.owner == owner.key() @ Error::Unauthorized,
)]
pub owner: Signer<'info>,
```

**7. Missing instruction arguments in `#[instruction]` attribute**
```
error[E0425]: cannot find value `proof_hash` in this scope
```
Cause: `proof_hash` used in PDA seeds but not listed in `#[instruction(...)]`.
Fix: Add it to the attribute:
```rust
#[instruction(proof: Vec<[u8; 32]>, proof_hash: [u8; 32])]
```

**8. Missing struct imports**
```
error[E0412]: cannot find type `AgentAccount` in this scope
```
Fix: Add to the file's imports: `use crate::state::{AGENT_SEED, AgentAccount};`

**9. Missing error variants**
```
error[E0599]: no variant or associated item named `Unauthorized` found for enum `JobEscrowError`
```
Fix: Add the variant to `errors.rs`:
```rust
#[msg("Unauthorized: not poster or worker")]
Unauthorized,
```

**Build-fix iteration pattern:**
```bash
# Get all errors at once
anchor build 2>&1 | grep "^error" | head -10
# Fix errors program-by-program (start with the one that blocks others)
# Rebuild after each program fix
# Iterate until 0 errors
```

### Verification After Fixes

```bash
forge test -vv          # All tests must pass
forge test --gas-report # Check gas didn't regress
```

## Phase 6: Report

Write a comprehensive report to `02-Labs/Audit-[Project]-[Date].md`:

```markdown
---
title: Security Audit — [Project Name]
date: YYYY-MM-DD
type: audit
tags: [hackathon, solidity, security-audit]
---

# Security Audit: [repo-name]
**Auditor:** DMOB (Labs)
**Test Suite:** X/Y passing

## Contract Inventory
| Contract | Lines | Purpose |
|----------|-------|---------|
| ... | ... | ... |

## Security Findings
### MEDIUM
#### M-1: [Title]
**Contract:** File.sol:line
**Description:** ...
**Impact:** ...
**Recommendation:** ...

### LOW / INFO / ...

## Positive Security Patterns ✅
| Pattern | Contract A | Contract B |
|---------|------------|------------|
| ReentrancyGuard | ✅ | ❌ |

## Test Coverage Analysis
| Function | Covered | Missing |
|----------|---------|---------|
| ... | ✅ | ... |

## Overall Rating: ⭐⭐⭐⭐ (4/5)
## Recommended Fixes (Priority Order)
1. [Fix] — X minutes
```

## Phase 7: Mid-Hackathon Sprint Review (Repeatable)

When work is already in progress and you need a status check — NOT a fresh audit. Trigger: Jordan says "review", "what's left", "sprint status", or "what are we looking at".

### Step 1: Pull Existing Audit Reports

```bash
# Find latest audit files
ls -lt /root/vaults/gentech/02-Labs/Audit-*.md | head -5

# Read them — don't re-audit from scratch
# Note which findings were fixed vs still open
```

### Step 2: Check Repo State

```bash
cd ~/repos/[REPO]
git log --oneline -5           # Recent commits
git status --short             # Uncommitted changes
forge test --summary           # Current test count + pass/fail
```

Cross-reference test counts against the audit. If tests went up, fixes were applied.

### Step 3: Verify Deploy Readiness

```bash
# Check deploy script exists and is configured
cat scripts/Deploy.s.sol
cat foundry.toml               # RPC endpoints, chain ID, explorer config
```

### Step 4: Produce Sprint Summary

Use this template:

```markdown
## [Project] — Current State

**Repo:** [name] | **Deadline:** [date] | **Tests:** X/Y ✅

### ✅ Done
| Item | Status |
|------|--------|
| [contract/feature] | ✅ [notes] |

### ❌ What's Left
| Item | Effort | Blocker? |
|------|--------|----------|
| [task] | [hours] | 🔴/🟡 |

### 🎯 The Sprint (X days remaining)
[Day-by-day plan]
```

Key rules:
- Always check if audit fixes were applied (git diff the specific lines)
- Calculate available hours: `days remaining × 4 productive hrs/day`
- Flag blockers (e.g., "needs testnet gas from Jordan", "needs API key")
- Prioritize: security fixes > core contracts > deploy > UI > docs > nice-to-haves

## Pitfalls

1. **`anchor init` requires yarn** — If you get "yarn install failed: No such file or directory", install yarn first: `npm install -g yarn`. Anchor uses yarn, not npm, for dependency installation.
2. **Rust version matters** — Anchor AVM needs Rust 1.75+. If `cargo install` fails with "edition2024" error, update Rust first via `rustup update`. **After a Hermes reinstall**, the system Rust may be ancient (e.g., 1.75 from 2023). Always run `rustup update` before installing Anchor AVM.
3. **Anchor CLI vs library version mismatch** — If `anchor-lang = "1.0.1"` in Cargo.toml but `anchor --version` shows 0.30.1, you'll get weird build errors. Install the matching version: `avm install 1.0.1 && avm use 1.0.1`. The anchor CLI version MUST match the anchor-lang dependency version.
4. **`rust-toolchain.toml` pins old Rust** — Projects may have a `rust-toolchain.toml` pinning to an old Rust (e.g., 1.89.0). This overrides `rustup update`. Edit the file directly: `channel = "1.95.0"`. Without this, `anchor build` uses the pinned old version even if newer is installed.
5. **`include_bytes!` needs quoted paths** — In test files, `include_bytes!(../../../path/file.so)` fails silently with "takes 1 argument". Must be `include_bytes!("../../../path/file.so")` with quotes.
6. **Repo names can be misleading** — A repo named "solana" might contain only Solidity code. Always check file extensions. Verify with `find . -name "*.rs"` vs `find . -name "*.sol"`.
7. **Git submodules** — Foundry projects use git submodules for dependencies (`lib/`). After cloning, run `git submodule update --init --recursive`.
8. **Empty lib/ dirs** — If `lib/` is empty after clone, dependencies weren't committed. Run `forge install` to fetch them.
9. **Test counts can be inflated** — README may claim more tests than exist. Always verify with `forge test` or `cargo test`.
10. **Single validator key** — Common hackathon pattern but flagged as centralization risk. Note it but don't block on it.
11. **Delegate parallel audits AND builds** — When building 3+ modules, use `delegate_task` subagents for parallel execution. Each module takes ~60-120 seconds; parallel saves 3-5 minutes total. Same applies for audits.
12. **Old test files break after refactoring** — When you add/remove/rename instructions, existing test files reference deleted structs. Check `tests/` after any `lib.rs` changes.
