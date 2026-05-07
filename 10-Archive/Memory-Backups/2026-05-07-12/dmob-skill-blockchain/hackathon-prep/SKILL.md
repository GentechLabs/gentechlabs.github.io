---
name: hackathon-prep
description: "Blockchain hackathon preparation: research, dev tools, smart contract audits, gap analysis, sprint reviews, and submission workflows."
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [hackathon, research, dev-tools, audit, sprint, submission]
    related_skills: []
---

# Blockchain Hackathon Preparation

End-to-end workflow for hackathon preparation: research, environment setup, codebase audit, security review, gap analysis, and sprint planning.

---

## 0. Pre-Build Audit (MANDATORY — Jordan Directive)

**Before ANY build work, ALWAYS do a clean audit of what already exists.** Check GitHub AND Obsidian. Never trust documentation over filesystem.

### Why This Exists
Session lesson (May 5, 2026): Sprint plan said "2 programs deployed to devnet, 2 in progress." Reality: 1 partially-built program with missing instruction files, no toolchain installed, and 3 separate code locations with the vault version being the most complete. We almost rebuilt everything from scratch.

### Audit Protocol (Run Every Time)
```bash
# 1. Find ALL code locations (repo, vault, projects folder, /tmp)
find ~/repos/ -name "Anchor.toml" -o -name "foundry.toml" 2>/dev/null
find /root/vaults/gentech/02-Labs/ -name "*.rs" -o -name "*.sol" | grep -v node_modules | head -20
find /root/projects/ -name "Anchor.toml" -o -name "foundry.toml" 2>/dev/null

# 2. Check git state
cd <repo> && git log --oneline -5 && git status && git branch -a

# 3. Check toolchain
which anchor && anchor --version
which solana && solana --version
which forge && forge --version

# 4. Count actual code (not just files)
find programs/ -name "*.rs" | xargs wc -l | tail -1
find src/ -name "*.sol" | xargs wc -l | tail -1

# 5. Check for real tests vs boilerplate
grep -r "it(" tests/ 2>/dev/null | wc -l  # real tests have `it(` blocks

# 6. Check deploy state
ls target/deploy/ 2>/dev/null
solana program show <PROGRAM_ID> --url devnet 2>/dev/null
```

### Present Findings as Table
| Location | Programs | Lines | Tests | Deployed | Toolchain |
|----------|----------|-------|-------|----------|-----------|
| git repo | X | X | X | ✅/❌ | ✅/❌ |
| vault | X | X | X | ✅/❌ | ✅/❌ |
| projects/ | X | X | X | ✅/❌ | ✅/❌ |

Then recommend: "Use [location] as canonical. Sync to git."

---

## 0b. One Hackathon at a Time (Jordan Directive, May 2026)

**Core principle:** Do NOT spread across multiple hackathons simultaneously. Complete one fully, submit, then move to the next.

### Why
- Same small team (Jordan + DMOB doing most work)
- Mid-quality submissions everywhere = win nothing
- Sequential focus produces submission-ready work

### Priority Order (based on deadline + prize)
1. **Nearest deadline + highest prize** → primary focus
2. **Everything else** → parked until #1 is submitted
3. No registering for new hackathons while building for current one

### What "Done" Means
- Code deployed to testnet/mainnet
- Demo video recorded
- Submission docs written
- Submitted on platform
- Social thread posted

Only after ALL of the above → assess next hackathon.

---

## 0c. One Product, Multi-Hackathon Strategy

**Core principle (Jordan, May 2026):** Build one product, interchange it for different hackathons. Don't rebuild from scratch — adapt the same codebase.

### How It Works
1. **Build the canonical product** — AgentEscrow / AAE Brain on the primary chain (Solana or EVM)
2. **For each hackathon:** Deploy the same contract logic on the target chain, adjust the narrative to match the track, write chain-specific integration code
3. **Reuse:** Core contracts, test suite, demo video template, submission docs structure
4. **Adapt:** Chain-specific deployment scripts, SDK integrations, sponsor tool hooks

### What Changes Per Hackathon
| Element | Stays the Same | Changes |
|---------|---------------|---------|
| Core logic | ✅ Contract architecture, business logic | — |
| Test suite | ✅ Most tests (unit/integration) | Chain-specific deployment tests |
| Demo | ✅ Same core demo flow | UI tweaks, chain-specific wallets |
| Narrative | ✅ "Agent labor market" story | Track-specific framing (e.g., "Agentic Commerce" for Kite AI) |
| Submission docs | — | Platform-specific format (Devpost vs Cantina) |

### Quick Deadline Triage

When asked "which project is due first?" or "what's the sprint look like?":

```bash
# Pull both tracking files
cat /root/vaults/gentech/01-Agency/active-hackathons.md
cat /root/vaults/gentech/02-Labs/Bug-Bounties/00-Active-Bounties.md
```

Sort by deadline ascending. Present as a prioritized list with days remaining. Flag anything within 7 days as urgent.

---

## 1. Hackathon Research Tracking

Research a hackathon from web sources, assess fit for GenTech's AAE narrative, and update all vault tracking files. This is the **pre-development phase** — happens before any code audit or building.

### When to Use
- Jordan says "add X hackathon" or "research Y hackathon"
- Jordan says "check the status of Z" for a hackathon
- A new hackathon appears on the radar
- Need to verify current details (dates, prizes, requirements) for an already-tracked hackathon
- Updating the active hackathons table in HQ after a change

### Phase 1: Research the Hackathon

#### Colosseum Copilot API (for Solana hackathons)

```bash
# API base: https://copilot.colosseum.com/api/v1
# Token: ~/.hermes/scripts/colosseum-config.json
# Docs: https://docs.colosseum.com/copilot/api-reference

# Search for hackathon projects
curl -X POST "$COLOSSEUM_COPILOT_API_BASE/search/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "agent payments solana"}'

# Get project details by slug
curl "$COLOSSEUM_COPILOT_API_BASE/projects/by-slug/agentescrow" \
  -H "Authorization: Bearer $TOKEN"

# Analyze a project
curl -X POST "$COLOSSEUM_COPILOT_API_BASE/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_ids": ["..."]}'
```

#### Browse the Source

```bash
# Most hackathons are on Devpost
# Navigate to the URL and extract:
# - Exact dates (start + end)
# - Prize pool breakdown
# - Requirements (what to build, tech stack)
# - Team size limits
# - Submission requirements (hosted URL, repo, demo video)
# - Participant count
# - Partner/sponsor details
```

#### Key Data Points to Extract

| Field | Why It Matters |
|-------|---------------|
| Start/end dates | Timeline and sprint planning |
| Prize pool | ROI assessment |
| Tech requirements | Stack fit (Solana? EVM? Google Cloud?) |
| Submission format | What we need to produce |
| Team size | Solo vs. collaboration |
| Participant count | Competition level |
| Partner integrations | MCP servers, APIs we'd use |

### Phase 2: Vault Files to Update

There are **3 files** that need updating for any hackathon change:

#### 1. `01-Agency/active-hackathons.md`
- **Section-based**: Current Focus / Registered / Opportunistic / Skipped
- Move hackathon between sections as status changes
- Keep descriptions concise with key facts

#### 2. `02-Labs/Hackathon-Tracker.md`
- **Detailed entries**: Prize pool, dates, focus, relevance rating, status
- Numbered entries (### 1, ### 2, etc.)
- Status emojis: 🔴 PRIMARY / 🟢 ACTIVE / 🟡 REVIEW / ⏸️ SKIP / ⛔ DROPPED

#### 3. `03-Projects/HACKATHON-ROSTER-2026.md`
- **Table format**: Name | Deadline | Notes | Status
- Concise — one-liner per hackathon
- Sections: Active Focus / Watch for Future / Skipped

### Phase 3: Competitive Landscape Analysis

Before positioning our submission, map the competitive space across chains.

#### Colosseum Copilot — Search Competing Projects

```bash
TOKEN=$(jq -r .token ~/.hermes/scripts/colosseum-config.json)
BASE="https://copilot.colosseum.com/api/v1"

# Search by topic/technology
curl -s -X POST "$BASE/search/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agent payments x402 escrow", "limit": 10}'

# Get cluster data (e.g., v1-c14 = Solana AI Agent Infrastructure)
curl -s "$BASE/clusters/v1-c14" -H "Authorization: Bearer $TOKEN"
```

Key fields per result: `slug`, `name`, `oneLiner`, `prize` (type/amount/placement), `tags` (problemTags, solutionTags, techStack), `crowdedness` (project count in cluster), `cluster.label`.

#### GitHub Search — Cross-Chain Competitors

```bash
# Base chain competitors
curl -s "https://api.github.com/search/repositories?q=agent+escrow+base+chain&sort=updated&order=desc&per_page=10"

# Avalanche competitors
curl -s "https://api.github.com/search/repositories?q=agent+escrow+avalanche&sort=updated&order=desc&per_page=10"

# x402 agent payments across chains
curl -s "https://api.github.com/search/repositories?q=x402+agent+payments+base+OR+avalanche&sort=updated&order=desc&per_page=10"
```

#### Competitive Matrix Template

Build a table comparing our project vs. competitors across dimensions:

| Feature | Competitor A | Competitor B | **Our Project** |
|---------|-------------|-------------|-----------------|
| Core capability (e.g., x402) | ✅ | ✅ | ✅ |
| Gap they don't fill | ❌ | ❌ | ✅ |

**Output**: Clear positioning statement — "Competitors solve X. We solve Y."

### References
- [Hackathon research template](references/hackathon-research-template.md)
- [Colosseum Copilot API guide](references/colosseum-api.md)
- [Zerion API & CLI reference](references/zerion-api-cli.md) — Solana Frontier $5K sidetrack: commands, endpoints, auth, agent skills

---

## 2. Environment Setup

### Install Dev Tools

```bash
# Foundry (EVM/Solidity)
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc && ~/.foundry/bin/foundryup

# ── Solana CLI ──────────────────────────────────────────────────
# ⚠️ VERSION SELECTION MATTERS:
#   - Anchor 0.30.x → Solana 2.1.x (ships platform-tools with cargo ~1.79)
#   - Anchor 1.0.x   → Solana 3.x   (ships platform-tools v1.52+ with cargo ~1.95)
#   - Solana 1.18.x is too old for current crate ecosystem (cargo 1.75)
#
# For Anchor 0.30.1 (our current standard):
sh -c "$(curl -sSfL https://release.anza.xyz/v2.1.21/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
solana config set --url devnet

# ── Rust (via rustup) ──────────────────────────────────────────
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env
rustup default 1.85.0  # Pin to known-good version for Anchor 0.30.x
# ⚠️ PITFALL: Do NOT use `rustup update stable` blindly — latest stable
#    (e.g. 1.95) generates Cargo.lock v4 which SBF cargo can't parse.

# ⚠️ PITFALL: apt-installed Rust (1.75) conflicts with rustup
# If `which rustc` points to /usr/bin/rustc, it's the distro version (too old).
# rustup installs to ~/.cargo/bin/ — ensure that's FIRST in PATH:
export PATH="$HOME/.cargo/bin:$PATH"

# ⚠️ PITFALL: rustup toolchains can have broken shared libraries
# Symptom: "librustc_driver-*.so => not found" when running rustc
# Fix: uninstall and reinstall the broken toolchain
rustup toolchain uninstall <version> && rustup toolchain install <version>

# ── Anchor CLI (compile from source — AVM is unreliable) ───────
# ⚠️ PITFALL: AVM `install` prompts for confirmation which hangs in automation.
#    Use `echo "y" | avm install ...` or compile directly with cargo.
# ⚠️ PITFALL: AVM may resolve to wrong Rust toolchain (e.g. broken 1.79).
#    Set RUSTUP_TOOLCHAIN explicitly:
rm -f ~/.cargo/bin/anchor  # remove AVM symlink if present
RUSTUP_TOOLCHAIN=1.85.0-x86_64-unknown-linux-gnu \
  cargo install --git https://github.com/coral-xyz/anchor \
  --tag v0.30.1 anchor-cli 2>&1 | tail -5
# If compile fails with "feature `edition2024` is required":
#   Your Rust is too old. Ensure rustup toolchain ≥ 1.85.

# Verify
forge --version && anchor --version && solana --version && rustc --version
```

### ⚠️ CRITICAL: Cargo.lock Compatibility with SBF

**Session lesson (May 5, 2026):** System cargo (1.85+) generates `Cargo.lock` version 4, but `cargo-build-sbf` from Solana 2.1.x ships cargo 1.79 which can't parse v4. The build silently fails with `failed to parse lock file`.

**Fix — downgrade lock file version:**
```bash
# After generating Cargo.lock with system cargo:
sed -i 's/^version = 4$/version = 3/' Cargo.lock
```

**Better fix — pin Rust to 1.85.0 for lockfile generation:**
```bash
RUSTUP_TOOLCHAIN=1.85.0-x86_64-unknown-linux-gnu cargo generate-lockfile
# This generates v3 lockfile by default
```

### ⚠️ CRITICAL: edition2024 Dependency Cascade

**Session lesson (May 5, 2026):** When system cargo resolves deps, it picks latest versions that may require `edition2024` (needs rustc ≥ 1.86). The SBF bundled cargo (1.79) can't handle these. You'll see a chain of errors, one at a time.

**Known offenders (pin these immediately after `cargo generate-lockfile`):**
```bash
# Pin in this ORDER — each may reveal the next:
cargo update indexmap@2.14.0 --precise 2.7.1     # toml_edit needs ^2.13
cargo update blake3@1.8.5 --precise 1.5.5        # digest/ctutils/cmov chain
cargo update unicode-segmentation@1.13.2 --precise 1.12.0  # needs rustc 1.85
# Then verify no edition2024 refs remain:
grep -c "edition2024" Cargo.lock  # should be 0
```

**Full recipe:** [references/solana-sbf-dependency-pinning.md](references/solana-sbf-dependency-pinning.md)

### Clone Repos

```bash
mkdir -p ~/repos && cd ~/repos
git clone https://github.com/ORG/repo-name.git
```

### References
- [Dev tools setup guide](references/dev-tools-setup.md)

---

## 3. Codebase Audit

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

#### Signer & Authorization
- [ ] Signer checks on ALL privileged instructions
- [ ] `constraint = account.owner == signer.key()` on every mutable account
- [ ] Worker/poster validated against stored job data, not passed-in accounts
- [ ] Rate-limit or authorization on rating/reputation instructions (prevent sybil)

#### Account Validation
- [ ] PDA seeds + bump verified for every account
- [ ] `AccountInfo<'info>` with `/// CHECK:` comment MUST have actual on-chain constraint
- [ ] Never trust "client validates" — validate on-chain or it's not validated
- [ ] No duplicate account reuse in same instruction

#### Fund Handling
- [ ] Rent exemption for all accounts
- [ ] Close account pattern (return rent to user)
- [ ] CPI guard checks
- [ ] Direct lamport manipulation (`try_borrow_mut_lamports`) only on validated accounts
- [ ] `checked_add`/`checked_sub` on all arithmetic with financial meaning

#### CPI & Integration
- [ ] Stubbed CPI calls (commented-out Metaplex/external calls) must be flagged — these are NOT production-ready
- [ ] Collection/program constraints must reference DIFFERENT accounts (not same key for both)
- [ ] World ID / ZK proof verification must actually verify, not just mark as done
- [ ] Cross-program invocations must have correct program ID constraints

#### Common Vulnerability Patterns (from audits)
- **Unchecked `AccountInfo`**: Any `AccountInfo<'info>` without a constraint is a vector. The `/// CHECK:` comment is documentation, not validation.
- **No-op verification**: If a handler says "we trust the verifier" but makes no CPI to verify, it's broken.
- **Missing worker auth**: If worker is `Signer` but no constraint checks `worker.key() == job.worker`, anyone can submit/approve work.
- **Spoofable dispute accounts**: If poster/worker are passed as `AccountInfo` and only checked against `initiator.key()` (not against job data), disputes can be fabricated.
- **Self-referential constraints**: Checking `collection.key() == METAPLEX_CORE_PROGRAM` AND `metaplex_program.key() == METAPLEX_CORE_PROGRAM` means collection == program, which is wrong.

### Common Anchor Compilation Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Corrupted pubkeys (31 bytes instead of 32) | base58 address typo | Verify with Python: `import base58; print(len(base58.b58decode(addr)))` |
| Missing `solana_program` dependency | Not in Cargo.toml | Add `solana-program = "1.18"` |
| Missing derives on enums/structs | Missing `#[derive(InitSpace)]` or `Debug` | Add derives as needed |
| `u16` vs `usize` type mismatches | Constants defined as `usize` | Cast: `name_len <= MAX_NAME_LENGTH as u16` |
| Borrow checker violations in lamport transfers | Mutable borrow conflict | Get `AccountInfo` references BEFORE mutable borrow |
| `has_one` vs explicit constraint | Pubkey comparison failure | Replace with explicit constraint |
| Missing instruction arguments in `#[instruction]` | Argument used in PDA seeds | Add to `#[instruction(...)]` |
| Missing struct imports | Missing `use crate::state::{AGENT_SEED, AgentAccount};` | Add imports |
| Missing error variants | Variant not in `errors.rs` | Add variant to `errors.rs` |
| IDL build fails (ark-bn254 `MontFp!` panic) | anchor IDL compiler + arkworks incompatibility | `anchor build --no-idl` — programs compile fine, IDL is separate |

### ⚠️ CRITICAL: `cargo check` vs `cargo build-sbf`

**Session lesson (May 5, 2026):** `cargo check` uses the HOST compiler (rustup stable). `cargo build-sbf` uses Solana's BUNDLED platform-tools compiler, which may be a DIFFERENT (older) version. Code that compiles with `cargo check` may FAIL with `cargo build-sbf`.

```bash
# Host compiler (rustup stable) — what cargo check uses
rustc --version  # e.g., 1.95.0

# SBF bundled compiler — what cargo build-sbf uses
$HOME/.local/share/solana/install/active_release/bin/sdk/sbf/dependencies/platform-tools/rust/bin/rustc --version  # e.g., 1.75.0
```

**If `cargo check` passes but `cargo build-sbf` fails with dependency errors:**
1. Check the SBF compiler version: `ls ~/.local/share/solana/install/active_release/bin/sdk/sbf/dependencies/platform-tools/rust/bin/rustc`
2. If the binary is missing: Solana platform-tools need download. Try `cargo build-sbf` (should auto-download), or check if the `~/.cache/solana/` dir has the right version.
3. If the binary exists but is too old: upgrade Solana CLI to get newer platform-tools.

```bash
# Upgrade Solana CLI (installs to ~/.local/share/solana/install/)
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
# Check new platform-tools version
cat $HOME/.local/share/solana/install/active_release/bin/platform-tools-sdk/sbf/env.sh 2>/dev/null | head -5
```

**PITFALL:** Solana CLI v1.18.x ships platform-tools v1.41 with rustc 1.75.0. This is too old for many current Rust crate dependencies (e.g., `indexmap 2.14` needs `edition2024`). Solana CLI v3.x ships platform-tools v1.52+ with rustc 1.95.0+.

---

### ⚠️ CRITICAL: Verify Repo State Before Accepting Sprint Plans

**Session lesson (May 5, 2026):** Sprint plan said "2 programs deployed to devnet, 2 in progress." Reality: 1 partially-built program with missing instruction files and no Solana CLI/Anchor installed. Never trust documentation over filesystem.

#### Pre-Sprint Verification Checklist
Before committing to any deadline or telling Jordan "we're on track":

```bash
# 1. Check toolchain
which anchor && anchor --version
which solana && solana --version
which forge && forge --version

# 2. Check actual program files exist (not just referenced in mod.rs)
find programs/ -name "*.rs" | sort
# Compare against what lib.rs and mod.rs reference — any missing files?

# 3. Check git history
git log --oneline -5
# If only 1-2 commits exist, be suspicious of "deployed" claims

# 4. Check for real tests (not boilerplate)
find tests/ -name "*.ts" -o -name "*.js" | xargs grep -l "it(" 2>/dev/null
# Boilerplate test files have no `it(` blocks

# 5. Check deploy artifacts
ls target/deploy/ 2>/dev/null
# If empty, nothing has been deployed

# 6. Check devnet deployment
solana program show <PROGRAM_ID> --url devnet 2>/dev/null
# If error, it's NOT deployed
```

#### Red Flags That Mean "Not Actually Built"
- Only 1-2 git commits on the repo
- `mod.rs` references instruction files that don't exist on disk
- Test file is boilerplate (`describe("program-name", () => { it("Is initialized!")`)
- No `target/deploy/` directory
- Anchor.toml only lists 1 program when plan says 4
- `which anchor` returns a broken symlink (points to avm but avm isn't functional)

#### When You Discover This
1. Report honestly to Jordan — "The repo state doesn't match the sprint plan"
2. Present actual vs claimed state in a clear table
3. Propose a realistic timeline with toolchain setup included
4. Don't sugarcoat — Jordan values honest assessments over optimistic updates

#### Vault → Repo Code Sync Pattern

When vault code is more complete than the repo (common after agent-driven development):

```bash
# 1. Back up repo config files
cp Anchor.toml Anchor.toml.repo-backup
cp Cargo.toml Cargo.toml.repo-backup

# 2. Remove the old program structure
rm -rf programs/<old-structure>

# 3. Copy vault programs (may be different structure — e.g., 4 separate programs vs monolithic)
cp -r /path/to/vault/programs/ programs/

# 4. Copy vault workspace config (Cargo.toml, Anchor.toml with deployed program IDs)
cp /path/to/vault/Cargo.toml .
cp /path/to/vault/Anchor.toml .

# 5. Copy tests, client, docs
cp -r /path/to/vault/tests/ tests/
cp -r /path/to/vault/client/ client/

# 6. Verify structure matches vault
find programs/ -name "*.rs" | sort
```

⚠️ PITFALL: The repo and vault may have fundamentally different structures (e.g., monolithic single program vs. 4 separate workspace members). Always check both before syncing — don't just `cp -r` blindly.

#### Keypair Reconciliation (After Sync)

After copying vault source → repo, the `declare_id!` values in lib.rs must match the repo's keypairs (not the vault's):

```bash
# 1. Get repo keypair pubkeys
for f in target/deploy/*-keypair.json; do
  name=$(basename "$f" -keypair.json)
  pubkey=$(solana-keygen pubkey "$f")
  echo "$name: $pubkey"
done

# 2. Update declare_id! in each lib.rs to match repo keypairs
# (use sed or Python to replace the pubkey string)

# 3. Update Anchor.toml [programs.*] section with same pubkeys

# 4. Verify consistency
grep -h "declare_id!" programs/*/src/lib.rs
# All 4 should show repo pubkeys, not vault pubkeys
```

⚠️ PITFALL: If you skip this, `anchor build` succeeds but `anchor deploy` fails with "program does not match account" because the deployed program address won't match the declared ID.

### References
- [Security audit template](templates/security-audit-template.md)
- [Anchor build-fix guide](references/anchor-build-fix.md)

---

## 4. Gap Analysis

Compare existing code against submission requirements:

| Requirement | Status | Effort | Priority |
|-------------|--------|--------|----------|
| [feature] | ✅ Done / ❌ Missing / ⚠️ Partial | [hours] | 🔴/🟡/🟢 |

### No-Idle Workflow Directive (Standing)

**Jordan directive:** When reaching a stopping point on any project, immediately queue the next priority and keep working. Stopping points include:
- Waiting for Jordan's approval
- Waiting on a tool/person unavailable (e.g., George, toolchain install)
- Any external dependency that creates idle time

**Queue order matters** — always have a prioritized fallback:
1. Primary submission (e.g., Solana Frontier main track)
2. Sidetrack adapters (e.g., Zerion $5K, GoldRush $3K)
3. Next hackathon scaffold
4. Documentation / docs polish

If you hit a blocker on #1, pivot to #2 immediately. Don't wait and don't ask — just queue and build.

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

### References
- [Gap analysis template](templates/gap-analysis-template.md)

---

## 5. Mid-Hackathon Sprint Review

When work is already in progress and you need a status check — NOT a fresh audit. Trigger: Jordan says "review", "what's left", "sprint status", or "what are we looking at".

### Step 1: Pull Existing Audit Reports

```bash
# Find latest audit files
ls -lt /root/vaults/gentech/02-Labs/Audit-*.md | head -5
```

### Step 2: Check Repo State

```bash
cd ~/repos/[REPO]
git log --oneline -5           # Recent commits
git status --short             # Uncommitted changes
forge test --summary           # Current test count + pass/fail
```

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

### References
- [Sprint review template](templates/sprint-review-template.md)
