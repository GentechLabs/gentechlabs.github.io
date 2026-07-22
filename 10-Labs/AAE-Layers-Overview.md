# AAE — Layer Architecture & Hackathon Map

**Created:** 2026-04-18
**Updated:** 2026-04-19 — Mapped to new 8-layer Kite architecture
**Status:** Active Development
**Purpose:** Master view of all AAE layers, which repo they live in, and which hackathon targets them

> **Note:** The original 5-layer numbering below maps to the current **8-layer Kite architecture** as follows:
> - Old L1 (Fee LP) → New L1 (Fee LP Auto-Balance)
> - Old L2 (Risk Intel) → New L6 (Enforcement)
> - Old L3 (Brain) → New L1 + L3 (Brain + Strategy)
> - Old L4 (Leaderboards) → New L5 (Leaderboards)
> - Old L5 (Coordination) → New L4 (Coordination)
> - New L7 (Transaction Construction) and L8 (Lifecycle & Economics) are additions from the Phase 3 burn floor spec

---

## The 8 Layers + Marketplace

```
┌─────────────────────────────────────────────────────────────┐
│                    AAE Agent Economy                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 8: Lifecycle & Economics (Burn floor, survival)      │
│  Layer 7: Transaction Construction (Gas, MEV, simulation)   │
│  Layer 6: Enforcement (Constitutional guardrails)           │
│  Layer 5: Social Leaderboards / Reputation                  │
│  Layer 4: Cross-Agent Coordination                          │
│  Layer 3: Strategy (Playbook & decision logic)              │
│  Layer 2: Personality (Communication style)                 │
│  Layer 1: Brain (Model selection)                           │
├─────────────────────────────────────────────────────────────┤
│  Foundation: Agent Marketplace + Escrow                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Foundation: Agent Marketplace + Escrow
- **Repo:** `~/repos/AAE/` (Avalanche) + `~/repos/arc-hackathon/` (Arc x402)
- **Contracts:** AgentRegistry, JobEscrow, AgentMarketplace, AgentToken, AgentTokenFactory
- **Status:** 5 contracts written, 2 test suites, deployed structure exists
- **Standards:** ERC-8004 (agent identity), ERC-8183 (escrow)
- **Target Hackathon:** Arc (x402, ERC-8004) — ongoing

### Layer 1: Fee LP Auto-Balance
- **What:** Automated LP position management — rebalance ranges, compound fees, optimize capital efficiency
- **Repo:** `~/repos/agent-economy-kite/` or new `~/repos/AAE-layer1-lp/`
- **Contracts:** LPRebalancer.sol, FeeCollector.sol, RangeOptimizer.sol
- **Target Hackathon:** **AVAX Retro9000** ($75K, Jul 14) — LFJ/TraderJoe ecosystem
- **Why AVAX:** LFJ liquidity book is native, Retro9000 loves infra/DeFi tooling

### Layer 2: Agent Risk Intelligence
- **What:** Agents monitoring on-chain risk — liquidation alerts, position health, market anomalies
- **Repo:** `~/repos/ethglobal-open-agents/` (AgentKeeper.sol)
- **Contracts:** AgentKeeper.sol (condition-based execution), RiskOracle.sol
- **Target Hackathon:** **ETHGlobal Open Agents** ($50K, May 3)
- **Pair with:** KeeperHub ($5K) for autonomous execution triggers

### Layer 3: Brain (Evolve/Learn/Memory)
- **What:** Persistent agent memory, skill evolution, learning from outcomes
- **Repo:** `~/repos/ethglobal-open-agents/` + 0G Storage integration
- **Contracts:** AgentRegistry.sol (skill hashes), MemoryStore.sol (0G-backed)
- **Target Hackathon:** **ETHGlobal Open Agents** ($50K, May 3)
- **Pair with:** 0G ($15K) for decentralized storage + INFT

### Layer 4: Social Leaderboards / Reputation
- **What:** On-chain reputation scores, leaderboards, social proof for agents
- **Repo:** `~/repos/AAE/` (AgentRegistry already has reputation system)
- **Contracts:** AgentRegistry.sol (reputation 0-10000 scale), Leaderboard.sol
- **Target Hackathon:** **ETHGlobal Open Agents** or Solana social track
- **Status:** Reputation system already built in AAE

### Layer 5: Cross-Agent Coordination
- **What:** Multi-agent orchestration — agents hiring agents, task delegation, composition
- **Repo:** `~/repos/ethglobal-open-agents/` (TaskManager.sol)
- **Contracts:** TaskManager.sol (task lifecycle), Coordinator.sol
- **Target Hackathon:** **ETHGlobal Open Agents** ($50K, May 3)
- **Why:** "Open Agents" = agents working together, this is the core thesis

---

## Hackathon → Layer Mapping

| Hackathon | Deadline | Prize | Layers | Repo | Status |
|---|---|---|---|---|---|
| ETHGlobal Open Agents | May 3 | $50K | 2, 3, 4, 5 | ~/repos/ethglobal-open-agents/ | 3 contracts, 44 tests ✅ |
| Arc (ongoing) | Ongoing | varies | Foundation (escrow) | ~/repos/arc-hackathon/ | 1 contract written |
| **Superteam Earn Sidetracks** | **May 11** | **$680K+** | **2, 3, 5 + Foundation** | **Shared core + adapters** | **🟡 Planning** |
| Solana Frontier (main) | May 11 | $230K+ | All layers (Solana) | New Solana port | 🟡 Planning |
| AVAX Retro9000 | Jul 14 | $75K | 1 (LP balance) | New or agent-economy-kite | Planning |

### Superteam Earn Sidetrack Breakdown ($680K+)
| Sidetrack | Prize | Layer | Adapter |
|---|---|---|---|
| Zerion CLI (Autonomous Agent) | $5,000 | L2+L5 | ZerionAdapter.sol |
| GoldRush (Covalent) | $3,000 | L2 | GoldRushAdapter.sol |
| Dune Analytics | TBD | L2 | DuneAdapter.sol |
| Agentic Engineering | ~200 USDG | L3 | AgentBrain.sol |
| Other sidetracks | varies | Any | Thin wrappers |

**Full sidetrack map:** `Hackathons/Superteam-Earn-Sidetrack-Map.md`

---

## Timeline

```
Apr 18 ──── May 3 ──────── Jul 14 ──── TBD
  │           │               │          │
  │      ETHGlobal Open    AVAX Retro   Solana
  │      (Layers 2,3,4,5)  (Layer 1)    (Layer 4/Marketplace)
  │           │               │
  └─── Arc ongoing ──────────┘
      (Foundation/Escrow)
```

---

## Key Repos

| Repo | Purpose | Contracts | Tests |
|---|---|---|---|
| `~/repos/AAE/` | Core agent economy (AVAX) | 5 | 2 suites |
| `~/repos/ethglobal-open-agents/` | ETHGlobal submission | 3 | 44 passing |
| `~/repos/arc-hackathon/` | Arc x402/escrow | 1 | — |
| `~/repos/agent-economy-kite/` | Kite AI (earlier attempt) | — | — |

---

## Tags
#AAE #architecture #hackathon #layers #plan

---

## Product Vision (Apr 19 — Jordan)

**Multi-agent workflow logic is core IP.** The provider/model selection pattern (OpenRouter-style) becomes a monetizable feature:

- **Pay-per-launch pricing** — users pick their own AI provider + model combo
- **Social layer gamification** — "What combination of layers creates the best trader? staker? yield farmer?"
- Users compete and optimize layer + model combinations → interesting social content
- Everybody wins: users get choice, we get revenue from launches, social layer gets engagement
