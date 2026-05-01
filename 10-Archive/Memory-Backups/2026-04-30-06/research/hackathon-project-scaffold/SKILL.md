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
sh -c "$(curl -sSfL https://release.anza.xyz/v2.1.21/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
solana config set --url devnet
```

### Rust (if not installed or too old)
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env
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

### Google Agent Starter Pack
```bash
# Uses uv (Python package manager)
uvx agent-starter-pack create PROJECT_NAME --agent adk --prototype --yes

# Or with the newer agents-cli
uvx google-agents-cli setup
```

**Note:** Agent Starter Pack is in maintenance mode — `agents-cli` is the successor. Use `agents-cli` for new projects if available.

## Phase 2: Project Structure

```
project-root/
├── colosseum-programs/          # Anchor workspace (Solana programs)
│   ├── Anchor.toml
│   ├── programs/
│   │   └── colosseum-programs/
│   │       └── src/
│   │           ├── lib.rs           # Program entry point
│   │           ├── agent_registry.rs
│   │           ├── job_escrow.rs
│   │           └── reputation.rs
│   └── tests/
├── colosseum-frontier/          # Google Agent Starter Pack project
│   ├── app/
│   │   ├── agent.py              # ADK agent definition
│   │   └── solana_tools.py       # Python tools for Solana interaction
│   ├── tests/
│   └── Makefile
├── demo.py                      # Demo script for recording
├── DEMO_STORYBOARD.md           # Scene-by-scene video plan
└── README.md
```

### Creating the Anchor Workspace
```bash
anchor init colosseum-programs --template single
```

### Creating the Agent Project
```bash
uvx agent-starter-pack create colosseum-frontier --agent adk --prototype --yes
```

## Phase 3: Solana Programs (Anchor)

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
solana-keygen new --outfile ~/.config/solana/id.json

# Get devnet SOL
solana airdrop 2

# Build and deploy
cd colosseum-programs
anchor build
anchor deploy --provider.cluster devnet
```

## Phase 4: Python Integration (Function Tools)

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

## Phase 5: Demo Script + Storyboard

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

- **Anchor cargo install fails** — Rust too old for edition2024; download binary instead
- **Agent Starter Pack in maintenance mode** — `agents-cli` is the successor; check availability
- **GCP auth required** — `gcloud auth login --update-adc` needed even for prototype mode
- **Module import errors** — ADK imports fail if google-adk not installed; use direct file import for demo
- **JobInfo dataclass order** — Default values must come after required fields
- **solana airdrop rate limits** — Devnet airdrop limited; don't request too frequently
- **Explorer URLs** — Use `?cluster=devnet` suffix or URLs 404

## Related Skills

- `hackathon-tech-stack-evaluation` — Evaluate before building (this skill is the build phase)
- `crypto-hackathon-bounty-scout` — Find hackathons (this skill builds after finding)
- `architecture-diagram` — Generate architecture diagrams for demo video
- `claude-design` — Design HTML artifacts for hackathon presentation
