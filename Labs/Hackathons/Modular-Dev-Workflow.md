# 🏗️ Modular Hackathon Dev Workflow

**Purpose:** Build once, submit everywhere. Swap adapters, not core logic.
**For:** D-Mob (builder), Jordan (reviewer)

---

## Repository Structure

```
~/repos/agent-economy-solana/          ← MAIN SOLANA REPO
├── programs/
│   ├── agent_registry/                ← Core: identity, skills, stake
│   ├── job_escrow/                    ← Core: payment flow
│   ├── agent_brain/                   ← Core: memory, learning
│   ├── risk_oracle/                   ← Core: position monitoring
│   ├── task_manager/                  ← Core: delegation, coordination
│   └── reputation/                    ← Core: scores, leaderboards
├── adapters/                          ← SWAPPABLE per hackathon
│   ├── zerion_cli/                    ← For Zerion sidetrack
│   ├── goldrush/                      ← For Covalent sidetrack
│   ├── dune/                          ← For Dune sidetrack
│   └── raydium/                       ← For LP/DeFi sidetrack
├── tests/
│   ├── unit/                          ← Per-program unit tests
│   ├── integration/                   ← Cross-program tests
│   └── sidetrack/                     ← Per-sidetrack demo tests
├── demos/
│   ├── zerion_cli/                    ← Demo frontend + video script
│   ├── goldrush/                      ← Demo frontend + video script
│   ├── agentic_eng/                   ← Demo frontend + video script
│   └── ...
├── scripts/
│   ├── deploy.sh                      ← Deploy all programs
│   └── deploy_single.sh <program>     ← Deploy one program
└── ARCHITECTURE.md                    ← Master doc all sidetracks reference
```

---

## The Rule: No Chain-Specific Code in Core

```
✅ GOOD:
  programs/agent_brain/src/lib.rs     ← Pure logic, no external API calls
  adapters/zerion_cli/src/lib.rs      ← Calls agent_brain + Zerion API

❌ BAD:
  programs/agent_brain/src/lib.rs     ← Hardcoded Zerion API calls
```

**Test:** If you can delete the `adapters/` folder and all programs still compile, you did it right.

---

## Workflow: Adding a New Sidetrack Submission

### Step 1: Identify which core programs it needs
```yaml
# sidetrack-config.yml
sidetrack: "Autonomous Onchain Agent (Zerion CLI)"
prize: "$5,000 USDC"
deadline: "May 11, 2026"
core_programs:
  - agent_registry    # needs agent identity
  - task_manager      # needs delegation
  - agent_brain       # needs learning/memory
adapter: "zerion_cli" # new adapter needed
demo_dir: "demos/zerion_cli/"
```

### Step 2: Create adapter (if needed)
```rust
// adapters/zerion_cli/src/lib.rs
use agent_registry::AgentRegistry;
use task_manager::TaskManager;
use agent_brain::AgentBrain;

// Thin wrapper: connects core programs to Zerion CLI API
pub struct ZerionAgent {
    registry: AgentRegistry,
    tasks: TaskManager,
    brain: AgentBrain,
}

impl ZerionAgent {
    pub fn discover_and_delegate(&mut self, task: &str) -> Result<()> {
        // 1. Use brain to evaluate task
        // 2. Use registry to find capable agent
        // 3. Use task_manager to delegate
        // All Zerion-specific I/O happens HERE, not in core
    }
}
```

### Step 3: Create demo
```
demos/zerion_cli/
├── index.html          ← Single-page dark theme demo
├── script.js           ← Ethers.js / Solana.js interaction
└── README.md           ← Sidetrack-specific explanation
```

### Step 4: Create submission branch
```bash
git checkout -b sidetrack/zerion-cli
# Include: relevant core programs + zerion_cli adapter + demo
# Exclude: other adapters
```

### Step 5: Record in vault
Update `Labs/Hackathons/Active/01-Frontier-Sidetracks-May11.md` with:
- [ ] Program status (built/tested/deployed)
- [ ] Demo recorded
- [ ] README written
- [ ] Submitted

---

## Build Checklist Template (Copy Per Sidetrack)

```markdown
### [Sidetrack Name] — $X,XXX
**Deadline:** [date]
**Core Programs:** [list]
**Adapter:** [name or "none"]
**Demo:** demos/[name]/

#### Build
- [ ] Core programs compile
- [ ] Adapter compiles + connects to core
- [ ] Unit tests pass
- [ ] Integration test: full flow works
- [ ] Deployed to Solana devnet

#### Demo
- [ ] Demo frontend works (single HTML)
- [ ] Video script written
- [ ] Video recorded (2 min max)
- [ ] Screenshots captured

#### Submission
- [ ] GitHub branch: `sidetrack/[name]`
- [ ] README.md with: what it does, how to run, architecture link
- [ ] Submitted to Colosseum
- [ ] Submitted to Superteam (if applicable)
```

---

## Quick Commands (for D-Mob)

```bash
# Build everything
cd ~/repos/agent-economy-solana && anchor build

# Test one program
anchor test --program-name agent_registry

# Deploy one program to devnet
./scripts/deploy_single.sh agent_registry

# Run specific sidetrack demo
cd demos/zerion_cli && python3 -m http.server 8080
```

---

## Cross-Sidetrack Dependencies

```
agent_registry ─────┬─────► ALL sidetracks (identity required)
                    │
job_escrow ─────────┼─────► Payments, Commerce tracks
                    │
agent_brain ────────┼─────► Zerion, Agentic Engineering
                    │
risk_oracle ────────┼─────► GoldRush, Dune, Risk tracks
                    │
task_manager ───────┼─────► Zerion, Coordination
                    │
reputation ─────────┴─────► Social, Leaderboards
```

**Build order matters:** `agent_registry` first (everything depends on it), then parallelize the rest.

---

## D-Mob → Jordan Handoff Protocol

When a program is ready for review:
1. Push to branch `sidetrack/[name]`
2. Run tests: `anchor test --program-name [name]`
3. Update vault: check off items in sidetrack tracker
4. Drop in Mess Hall: "🟢 [program] ready for review on [branch]"

---

#hackathon #workflow #modular #dmob #dev
