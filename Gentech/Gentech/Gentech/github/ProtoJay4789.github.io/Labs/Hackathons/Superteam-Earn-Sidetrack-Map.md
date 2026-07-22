# 🎯 Superteam Earn Sidetrack → AAE Layer Map

> $680K+ in sidetrack prizes. 5 modular layers. One codebase, multiple submissions.

**Deadline:** May 11, 2026 (same as Colosseum Frontier main hackathon)
**Strategy:** Each AAE layer is a standalone module that can be wrapped/extended for specific sidetrack requirements.

---

## Architecture: Why Modular Wins

```
┌─────────────────────────────────────────────────────────────────┐
│                    AAE CORE (shared across all)                  │
│  AgentRegistry | Escrow | Marketplace | Token | Tests           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Layer 1  │ │ Layer 2  │ │ Layer 3  │ │ Layer 4  │           │
│  │ LP Auto  │ │ Risk Intel│ │ Brain    │ │ Social   │           │
│  │ Balance  │ │ Alerts   │ │ Memory   │ │ Arena    │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                   │
│  ┌────▼─────┐ ┌────▼─────┐ ┌────▼─────┐ ┌────▼─────┐           │
│  │ WRAPPER  │ │ WRAPPER  │ │ WRAPPER  │ │ WRAPPER  │           │
│  │ per-track│ │ per-track│ │ per-track│ │ per-track│           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│       │            │            │            │                   │
│  ┌────▼─────┐ ┌────▼─────┐ ┌────▼─────┐ ┌────▼─────┐           │
│  │Sidetrack│ │Sidetrack│ │Sidetrack│ │Sidetrack│           │
│  │    A     │ │    B     │ │    C     │ │    D     │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

**The pattern:** Core contracts are the engine. Each sidetrack gets a thin adapter/wrapper that demonstrates integration with their specific tool/SDK. Same tests, different demo.

---

## Sidetrack Matrix

### 🎯 HIGH PROBABILITY (Direct fit — layer maps 1:1)

| Sidetrack | Prize | AAE Layer | Contract(s) | Integration |
|-----------|-------|-----------|-------------|-------------|
| **Autonomous Onchain Agent (Zerion CLI)** | $5,000 USDC | Layer 2 (Risk Intel) + Layer 5 (Coord) | AgentKeeper.sol | Zerion CLI for portfolio data → agent triggers |
| **Build with GoldRush (Covalent)** | $3,000 USDC | Layer 2 (Risk Intel) | RiskOracle.sol | GoldRush API for on-chain analytics feed |
| **Agentic Engineering (Superteam)** | ~200 USDG | Layer 3 (Brain) | AgentBrain.sol | Agent engineering patterns, skill evolution |
| **Dune Analytics** | TBD | Layer 2 (Risk Intel) | Dashboard + contracts | Dune queries → risk scoring pipeline |

### 🟡 MEDIUM PROBABILITY (Requires adaptation)

| Sidetrack | Prize | AAE Layer | Contract(s) | Integration |
|-----------|-------|-----------|-------------|-------------|
| **Any DeFi Integration** | varies | Layer 1 (LP Balance) | LPRebalancer.sol | LP position management on Solana DEX |
| **Agent-to-Agent** | varies | Layer 5 (Coord) | TaskManager.sol | Multi-agent task delegation |
| **On-chain Identity** | varies | Foundation | AgentRegistry.sol | ERC-8004 / Solana agent identity |
| **Tokenization** | varies | Foundation + Layer 4 | AgentToken.sol | Agent tokenization, staking |

### 🔵 STRETCH (Requires new work but core is reusable)

| Sidetrack | Prize | AAE Layer | Contract(s) | Notes |
|-----------|-------|-----------|-------------|-------|
| **Any Solana-native** | varies | Any | Port needed | Anchor rewrite of existing Solidity |
| **Privacy-focused** | varies | Layer 3 (Brain) | ZK proof of agent performance | New ZK circuit |
| **Cross-chain** | varies | Layer 5 (Coord) | Bridge contracts | Agent coordination across chains |

---

## Submission Strategy: One Layer, Multiple Tracks

### Layer 2: Agent Risk Intelligence
**Primary sidetrack:** Zerion CLI ($5K)
**Also eligible:** GoldRush ($3K), Dune Analytics
**Contracts:** AgentKeeper.sol, RiskOracle.sol
**Demo:** Agent monitors portfolio via Zerion → detects risk → triggers rebalance via KeeperHub

```
Sidetrack A (Zerion):    AgentKeeper + ZerionCLI adapter
Sidetrack B (GoldRush):  AgentKeeper + GoldRushAPI adapter
Sidetrack C (Dune):      AgentKeeper + DuneQuery adapter
```

### Layer 3: Brain (Evolve/Learn)
**Primary sidetrack:** Agentic Engineering (~200 USDG)
**Contracts:** AgentBrain.sol, MemoryStore.sol
**Demo:** Agent learns from LP performance → adapts strategy → stores learning on-chain

### Layer 5: Cross-Agent Coordination
**Primary sidetrack:** Zerion CLI ($5K) — agents coordinating portfolio strategies
**Contracts:** TaskManager.sol, Coordinator.sol
**Demo:** Agent A detects risk → delegates rebalance to Agent B → verifies completion

### Foundation: Agent Marketplace + Escrow
**Primary sidetrack:** Tokenization / Identity tracks
**Contracts:** AgentRegistry.sol, JobEscrow.sol, AgentMarketplace.sol
**Demo:** Full agent lifecycle — register → hire → escrow → complete → rate

---

## Modular Dev Workflow

### Step 1: Core Contracts (shared)
```
contracts/
├── core/
│   ├── AgentRegistry.sol      # Agent identity + reputation
│   ├── JobEscrow.sol          # Payment escrow
│   ├── AgentMarketplace.sol   # Buy/sell agents
│   └── AgentToken.sol         # Agent tokenization
├── layers/
│   ├── L1-LP/
│   │   ├── LPRebalancer.sol
│   │   ├── FeeCollector.sol
│   │   └── RangeOptimizer.sol
│   ├── L2-Risk/
│   │   ├── AgentKeeper.sol
│   │   └── RiskOracle.sol
│   ├── L3-Brain/
│   │   ├── AgentBrain.sol
│   │   └── MemoryStore.sol
│   ├── L4-Social/
│   │   ├── Leaderboard.sol
│   │   └── Reputation.sol
│   └── L5-Coord/
│       ├── TaskManager.sol
│       └── Coordinator.sol
├── adapters/
│   ├── ZerionAdapter.sol      # Thin wrapper for Zerion CLI
│   ├── GoldRushAdapter.sol    # Thin wrapper for Covalent
│   ├── DuneAdapter.sol        # Thin wrapper for Dune
│   └── KeeperHubAdapter.sol   # Thin wrapper for KeeperHub
└── interfaces/
    ├── IAgentRegistry.sol
    ├── IJobEscrow.sol
    ├── IAgentKeeper.sol
    └── IAdapter.sol
```

### Step 2: Per-Sidetrack Wrapper
Each sidetrack submission = core contracts + 1 adapter + demo-specific tests.

```bash
# Generate sidetrack submission package
forge build
forge test --match-contract CoreTests      # Shared tests
forge test --match-contract ZerionTests    # Track-specific tests
forge script script/DeployZerion.s.sol     # Track-specific deploy
```

### Step 3: Demo Template
Every sidetrack submission gets the same demo structure:
1. **Problem** (15 sec): "DeFi agents need X but current tools don't Y"
2. **Solution** (30 sec): "AAE Layer N + [Sidetrack SDK] integration"
3. **Live Demo** (60 sec): Register agent → trigger action → see result on-chain
4. **Architecture** (15 sec): Show the layer diagram

### Step 4: GitHub Structure
```
repo/
├── README.md                    # Track-specific README
├── contracts/                   # Shared core + track adapter
├── test/                        # Core + adapter-specific tests
├── script/                      # Deploy scripts per track
├── demo/                        # Frontend/CLI demo
└── docs/
    ├── architecture.md          # Layer diagram
    └── integration-guide.md     # How adapter works
```

---

## Priority Order (by deadline + prize)

| Priority | Sidetrack | Prize | Deadline | Effort | Layer |
|----------|-----------|-------|----------|--------|-------|
| 1 | Zerion CLI | $5,000 | May 11 | Medium | L2+L5 |
| 2 | GoldRush (Covalent) | $3,000 | May 11 | Low | L2 |
| 3 | Dune Analytics | TBD | May 11 | Low | L2 |
| 4 | Agentic Engineering | ~200 USDG | May 11 | Low | L3 |
| 5+ | Other sidetracks | varies | May 11 | Varies | Any |

**Total potential from sidetracks alone:** $8,000+ USDC + other prizes
**Plus main Frontier prizes:** $230K+ (separate submission)
**Plus accelerator:** $250K pre-seed (if winners)

---

## Contract Reuse Matrix

| Contract | Zerion | GoldRush | Dune | Agentic | Main Frontier |
|----------|--------|----------|------|---------|---------------|
| AgentRegistry.sol | ✅ | ✅ | ✅ | ✅ | ✅ |
| AgentKeeper.sol | ✅ | ✅ | ✅ | — | ✅ |
| RiskOracle.sol | — | ✅ | ✅ | — | ✅ |
| AgentBrain.sol | — | — | — | ✅ | ✅ |
| TaskManager.sol | ✅ | — | — | — | ✅ |
| JobEscrow.sol | ✅ | — | — | — | ✅ |

**Key insight:** AgentRegistry + AgentKeeper + TaskManager are the Swiss Army knife. They appear in almost every submission. Build them once, test them thoroughly, reuse everywhere.

---

## What This Means for Dev Workflow

1. **Don't build sidetrack-specific code first** — build the core layer contracts
2. **Adapters are thin** — 50-100 lines max, just wrapping SDK calls
3. **Tests are shared** — core contract tests run for every sidetrack
4. **Demo is templated** — same structure, different data sources
5. **GitHub is modular** — one repo, multiple README branches or subdirectories per track

### Time Budget (if starting now)

| Task | Hours | Notes |
|------|-------|-------|
| Core contracts (polish existing) | 8h | AgentRegistry, AgentKeeper, TaskManager already exist |
| Zerion adapter | 4h | CLI integration + tests |
| GoldRush adapter | 2h | API wrapper + tests |
| Dune adapter | 2h | Query integration + tests |
| Brain layer (new) | 6h | AgentBrain.sol + MemoryStore.sol |
| 4 demo videos | 4h | 1h each, template-based |
| 4 README packages | 2h | Template + track-specific details |
| Security audit pass | 4h | One pass covers all submissions |
| **Total** | **32h** | ~4 days of focused work |

---

## Tags
#superteam #earn #sidetracks #frontier #hackathon #AAE #modular #strategy #solana
