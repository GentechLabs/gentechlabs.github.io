# Beams SDK — Consolidated Research & Integration Analysis

**Date:** 2026-04-21
**Author:** DMOB
**Status:** Active research — building on Apr 18-19 findings

---

## ⚠️ Critical Clarification: Two "Beam" Entities

| Entity | URL | What It Is | Relevance |
|--------|-----|------------|-----------|
| **Beam Network** | onbeam.com | Avalanche subnet (EVM L1) — gaming/fintech chain | 🔶 **Where we deploy contracts** |
| **Beam Cloud** | beam.cloud | Serverless AI runtime — stateful agents, GPU inference | 🔶 **Where we run agent compute** |

**Both matter for us.** Beam Network = our on-chain home. Beam Cloud = our AI compute layer.

---

## Part 1: Beam Network (Avalanche Subnet)

### Chain Specs
- **Chain ID:** 4337
- **EVM-compatible** — our Solidity contracts deploy directly
- **Gas token:** $BEAM
- **TVL:** $1.08M (low, but grants program is active)
- **Bridge:** LayerZero
- **DEX:** Beam Swap, Inferno Swap

### Why Deploy Here
1. **EVM-native** — AgentRegistry, JobEscrow, AgentMarketplace all deploy as-is
2. **Grants program** — Active, looking for real DeFi + AI infra (not "AI slop")
3. **AVAX subnet** — same ecosystem as our Retro9000 play
4. **Low competition** — 2 protocols, we'd be a top-3 project by default
5. **Cross-app agent vision** — our Agent Passport concept aligns with Beam's ecosystem goals

### Smart Contract Deployment Path
```
Our EVM Contracts → Beam Network (Chain ID 4337)
├── AgentRegistry.sol ✅ (ERC-8004 pattern, ready)
├── JobEscrow.sol ✅ (AVAX escrow, ready)
├── AgentMarketplace.sol ✅ (ready)
├── AgentToken.sol ✅ (ERC-20, ready)
├── AgentTokenFactory.sol ✅ (ready)
└── Bin-AMM.sol 🔄 (in development — Dmob)
```

**All contracts are EVM-compatible → deploy with zero code changes.**

---

## Part 2: Beam Cloud (AI Agent Runtime)

### What It Is
Open-source serverless runtime for AI workloads. Python SDK, sub-second container boot, scale-to-zero, GPU support.

### SDK Primitives
| Primitive | Use Case | Maps to AAE Layer |
|-----------|----------|-------------------|
| `@endpoint` | Serverless inference (risk scoring, market analysis) | L2 Risk Intel |
| `@bot` | Stateful agents with memory + transitions | L3 Brain |
| `@task_queue` | Background jobs (rebalancing, monitoring) | L6 Orchestration |
| `Sandbox` | Isolated code execution (strategy backtesting) | L3 Brain |
| `@function` | Fan-out parallel workloads | L6 Orchestration |

### Agent Framework Features
- **Stateful memory** — `remember()`, persistent context across sessions
- **Transition networks** — `@bot.network`, `@bot.location`, `@bot.transition`
- **Concurrency** — built-in session management
- **Context commands** — `confirm()`, `prompt()`, `say()`, `send_file()`
- **Development workflow** — `beam serve app.py:bot` (hot-reload)

### Why Beam Cloud Fits Our Stack
1. **Sub-second boot** — agent spawning is fast enough for real-time DeFi
2. **Stateful agents** — persistent memory = our L3 Brain requirement
3. **GPU inference** — run risk models, market analysis without managing infra
4. **Scale-to-zero** — pay only when agents are active (crucial for hackathon economics)
5. **Open-source** — self-hostable if we need sovereignty later

---

## Part 3: Integration Map — How Beam Fits Our Stack

### Full Architecture
```
┌─────────────────────────────────────────────────────┐
│                  Kite / AAE Stack                     │
├─────────────────────────────────────────────────────┤
│  L2 Risk Intel   → Beam Cloud (@endpoint)            │
│  L3 Brain        → Beam Cloud (@bot stateful agents)  │
│  L6 Orchestration→ Beam Cloud (@task_queue, @function)│
├─────────────────────────────────────────────────────┤
│  L4 Enforcement  → GenLayer (subjective consensus)    │
│  L5 Escrow       → Beam Network (Solidity contracts)  │
├─────────────────────────────────────────────────────┤
│  L1 Fee LP       → Solana/AVAX (DeFi native)          │
│  L7 Governance   → Custom (voting, treasury)           │
│  L8 Lifecycle    → Custom (burn floor, economics)      │
└─────────────────────────────────────────────────────┘
```

### Hackathon Sprint Mapping
| Hackathon | Date | Beam Component | What We Ship |
|-----------|------|----------------|--------------|
| **ARC** | Apr 20-26 | Beam Network (deploy escrow contracts) | AgentEscrow on Beam testnet |
| **Kite AI** | Apr 26 | Beam Cloud (L3 brain demo) | Stateful agent managing LP |
| **ETHGlobal** | May 3 | Both — full stack demo | Brain + Enforcement + Escrow |
| **Retro9000** | Jul 14 | Beam Network (full protocol) | Production deployment |

---

## Part 4: Specific Integration Points

### 1. AgentEscrow → Beam Network
**Current state:** 5 Solidity contracts, 24 tests passing, deployed on Avalanche
**Action:** Deploy to Beam testnet (Chain ID 4337) — same code, different RPC
**Effort:** Minimal — change RPC endpoint, verify on Beam explorer

### 2. Live LP Agent → Beam Cloud
**Current state:** Python agent monitoring AVAX/USDC on LFJ, cron-based
**Action:** Migrate to Beam Cloud `@bot` — add stateful memory, transition networks
**Effort:** Medium — refactor from cron scripts to stateful bot framework
**Value:** Agent remembers position history, learns from rebalancing outcomes

### 3. Risk Engine → Beam Cloud
**Current state:** Manual risk assessment via YoYo's research
**Action:** Build `@endpoint` for real-time risk scoring
**Effort:** Medium — need to define risk model, but infra is ready
**Value:** Instant risk scores for enforcement layer

### 4. Agent Passport → Beam Network NFT
**Current state:** Concept documented, not built
**Action:** Implement as ERC-721 (Soul-Bound Token) on Beam Network
**Effort:** High — new contract, but follows ERC-721 patterns we know
**Value:** Cross-app identity, portable reputation

---

## Part 5: Action Items

### Immediate (This Week)
- [ ] Set up Beam Network testnet RPC in Foundry config
- [ ] Deploy AgentRegistry to Beam testnet
- [ ] Deploy JobEscrow to Beam testnet
- [ ] Verify contracts on Beam explorer
- [ ] Install Beam Cloud SDK (`pip install beam-client`)

### Short-term (Pre-Kite AI Apr 26)
- [ ] Prototype LP agent as Beam Cloud `@bot`
- [ ] Demo: stateful agent remembers position state across sessions
- [ ] Document Beam Cloud agent architecture

### Medium-term (Pre-ETHGlobal May 3)
- [ ] Full Beam Cloud integration (L2 + L3 + L6)
- [ ] Beam Network contracts (L5 + Agent Passport)
- [ ] Cross-platform demo: Beam Cloud brain → Beam Network escrow

### Grant Application
- [ ] Finalize Beam Foundation grant draft (`Labs/Beam-Grant-Application-DRAFT.md`)
- [ ] Include deployed testnet contracts as proof of work
- [ ] Submit to grants.onbeam.com

---

## References
- Beam Cloud Docs: https://docs.beam.cloud/
- Beam Cloud GitHub: https://github.com/beam-cloud/beta9
- Beam Network Docs: https://docs.onbeam.com/
- Beam Grants: https://grants.onbeam.com/apply
- SDK Comparison: `Labs/SDK-Comparisons/Beams vs GenLayer.md`
- Agent Passport Concept: `Labs/Beam-Agent-Passport.md`
- Grant Draft: `Labs/Beam-Grant-Application-DRAFT.md`

---

*Updated: April 21, 2026*
*Next review: After first Beam testnet deployment*
#Beams #research #integration #AVAX
