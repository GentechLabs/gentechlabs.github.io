---
name: hackathon-project-scaffold
description: "Scaffold a hackathon project from zero: install toolchains, write smart contracts, create AI agent integration, build demo scripts and storyboard. Covers Solana/Anchor + Google Agent Starter Pack patterns."
tags:
  - hackathon
  - scaffold
  - solana
  - anchor
  - google-adk
  - agent-starter-pack
  - demo
  - smart-contracts
  - python-integration
triggers:
  - Jordan decides to pursue a hackathon and needs to start building
  - Setting up Solana/Anchor programs for a hackathon
  - Scaffolding Google Agent Starter Pack project
  - Writing demo scripts and storyboard for hackathon submission
  - Connecting Python AI agent to on-chain Solana programs
  - Building full-stack hackathon project (blockchain + AI)
---

# Hackathon Project Scaffold

Full build workflow for hackathon projects: toolchain install → project scaffold → smart contracts → agent integration → demo preparation.

## When to Use

- Jordan says "set it up" or "start building" for a hackathon
- Need to scaffold a project combining Solana + Google Cloud AI
- Writing Anchor programs for agent marketplace / escrow / reputation patterns
- Creating demo scripts that show the full flow
- Building Python integration between ADK agents and Solana programs

## Prerequisites Check

Before installing anything, check what's already available:

```bash
# Check existing tools
which solana && solana --version
which rustc && rustc --version
which anchor && anchor --version
which uvx && uvx --version
python3 --version
which gcloud
which node && node --version
```

## Phase 1: Toolchain Installation

### Solana CLI
```bash
# Use v2.2.x+ — v2.1.x ships platform-tools with Cargo 1.79 which can't handle edition2024 deps
sh -c "$(curl -sSfL https://release.anza.xyz/v2.2.14/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
solana config set --url devnet
```

**Pitfall:** The `sh -c "$(curl ...)"` installer can fail in environments with non-standard `$HOME` (e.g., Hermes agent profiles). Fallback: download tarball directly:
```bash
cd /tmp
curl -sSfL "https://release.anza.xyz/v2.2.14/solana-release-x86_64-unknown-linux-gnu.tar.bz2" -o solana.tar.bz2
tar xjf solana.tar.bz2
mv solana-release ~/.local/share/solana/install/releases/2.2.14/
ln -sf ~/.local/share/solana/install/releases/2.2.14 ~/.local/share/solana/install/active_release
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

**Pitfall:** Platform-tools are NOT bundled in the tarball — they download on first `cargo-build-sbf` run. This is normal. First build will be slow (~5-10 min) while it fetches them.

### Rust (if not installed or too old)
**Minimum: Rust 1.85+** — edition2024 is required by transitive dependencies (e.g., `cpufeatures v0.3.0`). Rust 1.75-1.84 will fail with `feature 'edition2024' is required`.
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
source ~/.cargo/env
rustc --version  # Should be 1.85+
```

### Anchor Framework
```bash
# Preferred: download binary directly (cargo install is slow)
ANCHOR_VERSION="1.0.1"
curl -sL "https://github.com/solana-foundation/anchor/releases/download/v${ANCHOR_VERSION}/anchor-${ANCHOR_VERSION}-x86_64-unknown-linux-gnu" -o /usr/local/bin/anchor
chmod +x /usr/local/bin/anchor

# Verify
anchor --version
```

**Pitfall:** `cargo install --git https://github.com/coral-xyz/anchor avm` requires very recent Rust (edition2024 feature). If Rust is old, download the binary instead.

**Pitfall:** Anchor CLI version (e.g., 1.0.1) may not match `anchor-lang` crate version in Cargo.toml (e.g., 0.30.1). This causes warnings but usually compiles. To suppress, add to `Anchor.toml`:
```toml
[toolchain]
anchor_version = "0.30.1"  # Match the version in your Cargo.toml
```

### Google Agent Starter Pack
```bash
# Uses uv (Python package manager)
uvx agent-starter-pack create PROJECT_NAME --agent adk --prototype --yes

# Or with the newer agents-cli
uvx google-agents-cli setup
```

**Note:** Agent Starter Pack is in maintenance mode — `agents-cli` is the successor. Use `agents-cli` for new projects if available.

## Phase 2: Audit Existing Code First

Before writing anything, check what's already on disk. Hackathon projects often have partial code from prior sessions.

```bash
# Find Anchor workspaces
find . -name "Anchor.toml" -type f 2>/dev/null

# Check program count and completeness
find . -name "lib.rs" -path "*/programs/*/src/*" -exec sh -c 'echo "=== {} ==="; head -20 {}; echo' \;

# Count instruction handlers (files with "pub fn handler")
grep -rl "pub fn handler" programs/*/src/instructions/ 2>/dev/null | wc -l

# Check for missing instruction files (referenced in mod.rs but not on disk)
for mod in programs/*/src/instructions/mod.rs; do
    dir=$(dirname "$mod")
    grep "pub mod" "$mod" | sed 's/pub mod //;s/;//' | while read m; do
        [ ! -f "$dir/$m.rs" ] && echo "MISSING: $dir/$m.rs"
    done
done
```

If code already exists, skip to Phase 3 build step. Don't rewrite what's already there.

## Phase 3: Project Structure

### Multi-Program Workspace (preferred for hackathons with 4+ programs)
```
project-root/
├── Anchor.toml                    # Workspace config with all program IDs
├── Cargo.toml                     # Workspace members
├── programs/
│   ├── agent-registry/
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs             # Program entry + declare_id!
│   │       ├── state.rs           # Account structs, enums, constants
│   │       ├── errors.rs          # Custom error codes
│   │       └── instructions/
│   │           ├── mod.rs         # Re-exports all instruction modules
│   │           ├── register_agent.rs   # One file per instruction
│   │           ├── update_agent.rs
│   │           └── ...
│   ├── job-escrow/
│   │   └── src/...
│   ├── reputation/
│   │   └── src/...
│   └── dispute-resolver/
│       └── src/...
├── client/                        # TypeScript client
│   ├── package.json
│   └── src/
│       ├── index.ts
│       ├── agent.ts
│       ├── escrow.ts
│       └── ...
├── tests/
│   └── index.ts
└── README.md
```

### Single-Program (simpler projects)
```
project-root/
├── Anchor.toml
├── programs/
│   └── my-program/
│       └── src/
│           └── lib.rs
└── tests/
```

### Creating the Anchor Workspace
```bash
anchor init colosseum-programs --template single
```

### Creating the Agent Project
```bash
uvx agent-starter-pack create colosseum-frontier --agent adk --prototype --yes
```

## Phase 4: Solana Programs (Anchor)

### Common Patterns for Agent Marketplaces

#### Agent Registry
- Register agent with name, capabilities, stake
- Store reputation score on-chain
- Seeds: `[b"agent", authority.key().as_ref()]`

#### Job Escrow
- Post job with payment locked in PDA
- Worker accepts → submits → gets paid
- Seeds: `[b"job", job_id.as_bytes()]`
- Status enum: open(0) → assigned(1) → submitted(2) → completed(3) → disputed(4)

#### Reputation
- Rate agent 1-5 after job completion
- Update cumulative score on agent account
- Seeds: `[b"rep", agent.key(), job_ref]`

### Anchor Program Template
```rust
use anchor_lang::prelude::*;

declare_id!("YOUR_PROGRAM_ID");

#[program]
pub mod my_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, data: String) -> Result<()> {
        let account = &mut ctx.accounts.account;
        account.data = data;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = user, space = 8 + MyAccount::INIT_SPACE)]
    pub account: Account<'info, MyAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(InitSpace)]
#[account]
pub struct MyAccount {
    pub data: [u8; 64],
    pub data_len: u8,
    pub bump: u8,
}
```

### Deploying to Devnet
```bash
# Generate keypair if needed
solana-keygen new --outfile ~/.config/solana/id.json --no-bip39-passphrase

# Get devnet SOL (try smaller amounts if rate-limited)
solana airdrop 2
# Fallback: solana airdrop 1 (smaller request)

# Build and deploy
cd project-root
anchor build
anchor deploy --provider.cluster devnet
```

**Pitfall:** `anchor build` may rewrite program IDs in `Anchor.toml` on first build. This is normal — it syncs declared IDs with generated keypairs. Rebuild after to use the updated artifacts.

## Phase 5: Python Integration (Function Tools)

Create `solana_tools.py` with function tools the ADK agent can call:

```python
def register_agent(name: str, capabilities: list[str], stake_sol: float) -> str:
    """Register this agent on the Solana blockchain.
    
    Args:
        name: Unique agent name (max 32 chars)
        capabilities: List of skills this agent offers
        stake_sol: Amount of SOL to stake as bond (min 0.01)
    
    Returns:
        Transaction confirmation with on-chain address
    """
    # For demo: simulate on-chain state in Python dicts
    # For production: use solders + solana-py to call programs
    ...
```

### Key Pattern: Simulated vs Real On-Chain

For hackathon demos, simulate on-chain state in Python dicts for speed:
```python
_agents = {}
_jobs = {}

def register_agent(name, capabilities, stake_sol):
    agent = AgentInfo(name=name, capabilities=capabilities, ...)
    _agents[name] = agent
    return json.dumps({"success": True, "agent_name": name, ...})
```

For production, use `solders` + `solana-py`:
```python
from solders.keypair import Keypair
from solana.rpc.api import Client

client = Client("https://api.devnet.solana.com")
# Build transaction, sign, send
```

### Import Pattern (avoid ADK dependency for demo)
```python
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "solana_tools",
    os.path.join(os.path.dirname(__file__), "app", "solana_tools.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
```

## Phase 6: Demo Script + Storyboard

### Demo Script Structure
```python
def banner(text, delay=0.5):
    print(f"\n{'='*60}\n  {text}\n{'='*60}\n")
    time.sleep(delay)

def step(num, text):
    print(f"\n  [{num}] {text}\n  {'─'*50}")

def main():
    banner("STEP 1: CHECK WALLET BALANCE")
    step(1, "Checking SOL balance...")
    result = json.loads(get_sol_balance())
    print(f"  💰 Balance: {result['balance_sol']} SOL")
    # ... continue through full flow
```

### Storyboard Template
9 scenes, 2:30–3:00 minutes:
1. **Hook** (0:00–0:15): "What if AI agents could trust each other?"
2. **Problem** (0:15–0:30): Agents are siloed, no reputation
3. **Registration** (0:30–1:00): Agent registers on-chain
4. **Job Posting** (1:00–1:30): Payment locked in escrow
5. **Discovery** (1:30–1:45): Find agents by reputation
6. **Work Flow** (1:45–2:10): Accept → submit
7. **Payment** (2:10–2:25): Approve → release funds
8. **Architecture** (2:25–2:50): Clean diagram
9. **CTA** (2:50–3:00): Logo + links

### Recording Checklist
- [ ] Record Solana Explorer showing real transactions
- [ ] Record full demo.py flow in clean terminal
- [ ] Record architecture diagram (use `claude-design` or `architecture-diagram` skill)
- [ ] Add text overlays in DaVinci Resolve or CapCut
- [ ] Add background music (lo-fi or synthwave)
- [ ] Export at 1080p, 60fps

## Known Pitfalls

- **Solana CLI v2.1.x breaks on edition2024 deps** — Platform-tools v1.43 ships Cargo 1.79, can't parse `cpufeatures v0.3.0` and other crates requiring edition2024. Use v2.2.x+ (e.g., 2.2.14).
- **Rust < 1.85 fails on edition2024 transitive deps** — Error: `feature 'edition2024' is required`. The culprit is usually `cpufeatures` or similar crates pulled in by Solana dependencies. `rustup update stable` fixes it.
- **Platform-tools not in tarball** — First `cargo-build-sbf` run downloads them automatically (~5-10 min). This is normal; don't panic.
- **Anchor CLI vs anchor-lang version mismatch** — CLI 1.0.1 + anchor-lang 0.30.1 = warnings. Usually compiles but add `anchor_version` to Anchor.toml `[toolchain]` to suppress.
- **Solana installer fails in non-standard HOME** — Hermes profiles, containers, chroots. Fallback: download tarball directly from `https://release.anza.xyz/vX.Y.Z/solana-release-x86_64-unknown-linux-gnu.tar.bz2`.
- **Anchor cargo install fails** — Rust too old for edition2024; download binary instead
- **Agent Starter Pack in maintenance mode** — `agents-cli` is the successor; check availability
- **GCP auth required** — `gcloud auth login --update-adc` needed even for prototype mode
- **Module import errors** — ADK imports fail if google-adk not installed; use direct file import for demo
- **JobInfo dataclass order** — Default values must come after required fields
- **solana airdrop rate limits** — Devnet airdrop limited; don't request too frequently. Try `solana airdrop 1` (smaller amounts) or use faucet.
- **Explorer URLs** — Use `?cluster=devnet` suffix or URLs 404

## Build Troubleshooting

Common `anchor build` failures and fixes:

| Error | Cause | Fix |
|-------|-------|-----|
| `feature 'edition2024' is required` | Rust too old or SBF Cargo too old | Update Rust (`rustup update stable`) + use Solana CLI v2.2.x+ |
| `anchor-lang version(X) and CLI version(Y) don't match` | Version mismatch | Add `[toolchain] anchor_version = "X"` to Anchor.toml |
| `Adding solana-program as separate dependency might cause conflicts` | Redundant dep | Remove `solana-program` from Cargo.toml, use `anchor_lang::solana_program` instead |
| `Incorrect program id declaration` | Anchor.toml ID doesn't match keypair | Let anchor rewrite it, then rebuild |
| Panic in `cargo-build-sbf` | Platform-tools missing or corrupt | Delete `~/.cache/solana/` and rebuild (re-downloads tools) |
| Airdrop rate limited | Devnet faucet throttle | Use smaller amounts (`solana airdrop 1`) or wait 30s |

## Phase 8: Vault → Repo Sync

Hackathon code lives in the vault (`02-Labs/Hackathons/Active/`) but must be pushed to a GitHub repo for submission. The vault is often a monorepo pointing to a different remote (e.g., GitHub Pages), so you can't push directly from vault paths.

### Workflow

```bash
export GH_TOKEN=$(cat ~/.config/gh/hosts.yml | grep oauth_token | head -1 | awk '{print $2}')

# 1. Clone the target repo to /tmp
gh repo clone ProtoJay4789/<repo-name> /tmp/<repo-name>-sync
cd /tmp/<repo-name>-sync

# 2. Compare source trees (exclude target/, .git/, keypairs)
diff -r <vault-path>/programs <repo>/programs --exclude=target
diff -r <vault-path>/client <repo>/client

# 3. If identical → commit any improvements (.gitignore, IDLs)
# 4. If different → copy changed files, commit, push
git add -A && git commit -m "sync: vault updates" && git push origin master
```

### Key Checks Before Sync
- **Program IDs**: `declare_id!()` in lib.rs must match Anchor.toml must match generated keypairs
- **Anchor.toml**: `anchor build` may rewrite program IDs — verify with `solana-keygen pubkey target/deploy/<program>-keypair.json`
- **.gitignore**: Must exclude `*-keypair.json`, `target/`, `.anchor`, `test-ledger`
- **IDLs**: Commit `idl/*.json` to repo root (not in `target/`) for client SDK integration

### Pitfall: Monorepo Remote Mismatch
The vault git remote often points to a different repo (e.g., ProtoJay4789.github.io). Don't push vault code directly — always clone the target repo fresh and copy source files over.

### Pitfall: gh auth Token Mismatch
`GITHUB_TOKEN` env var may be stale while `~/.config/gh/hosts.yml` has a valid token. Fix:
```bash
export GH_TOKEN=$(cat ~/.config/gh/hosts.yml | grep oauth_token | head -1 | awk '{print $2}')
gh auth login --with-token <<< "$GH_TOKEN"
```

## Related Skills

- `hackathon-tech-stack-evaluation` — Evaluate before building (this skill is the build phase)
- `crypto-hackathon-bounty-scout` — Find hackathons (this skill builds after finding)
- `architecture-diagram` — Generate architecture diagrams for demo video
- `claude-design` — Design HTML artifacts for hackathon presentation
