# 🏆 Colosseum Frontier Hackathon — Sidetrack Submission Map

**Deadline:** May 11, 2026
**Total Sidetrack Prizes:** $680,000+ ($315K original + $365K new)
**Plus:** Main Frontier prizes from Colosseum + Superteam Agentic Engineering Grant
**Status:** 🟢 ACTIVE

---

## The Strategy: One Core, Many Submissions

We build the **Agent Economy core once** (Solana-native), then adapt individual layers to hit multiple sidetracks. Each sidetrack gets a focused submission that showcases one capability slice.

```
                    ┌─────────────────────┐
                    │  AGENT ECONOMY CORE │
                    │  (Solana programs)  │
                    └─────────┬───────────┘
          ┌──────────┬────────┼────────┬──────────┐
          ▼          ▼        ▼        ▼          ▼
      Sidetrack   Sidetrack Sidetrack Sidetrack Sidetrack
         A           B         C         D          E
```

---

## Sidetrack → Layer Mapping

### 🎯 Tier 1: Direct Hits (High Confidence)

| Sidetrack | Prize | Layer | What We Submit |
|-----------|-------|-------|----------------|
| **Autonomous Onchain Agent (Zerion CLI)** | $5,000 | Layer 5 (Coordination) | Agent that auto-discovers, evaluates, and delegates tasks to other agents via CLI |
| **Agentic Engineering (Superteam)** | ~200 USDG | Layer 3 (Brain) | Agent memory + learning system — proof that agents evolve from outcomes |
| **Build with GoldRush (Covalent)** | $3,000 | Layer 2 (Risk Intel) | Agent risk dashboard pulling real-time position data via GoldRush API |
| **Dune Analytics** | TBD | Layer 2 + 4 | Agent performance analytics — leaderboards, risk scores, historical stats |

### 🔶 Tier 2: Good Fit (Adapt + Submit)

| Sidetrack | Prize | Layer | What We Submit |
|-----------|-------|-------|----------------|
| **Agent Commerce / Payments** | TBD | Foundation (Escrow) | JobEscrow — agents hire, pay, verify on-chain |
| **AI x DeFi** | TBD | Layer 1 (LP Auto-Balance) | Agent that auto-manages LP ranges on Raydium/Orca |
| **Social / Reputation** | TBD | Layer 4 (Social) | On-chain agent reputation graph, endorsements, leaderboards |
| **Security / Auditing** | TBD | Layer 2 (Risk) | Agent risk scoring, liquidation alerts, anomaly detection |

### 🔍 Tier 3: Worth Exploring (Stretch)

| Sidetrack | Prize | Notes |
|-----------|-------|-------|
| **Any data/API integration track** | Varies | Leverage GoldRush/Dune integration we're already building |
| **Cross-chain / Interop** | Varies | Bridge concept: Avalanche escrow ↔ Solana enforcement |

---

## Submission Schedule

```
Week of Apr 20-26
├── ARC Hackathon escrow polish (carry-over work)
├── Solana programs: Start AgentRegistry + JobEscrow (Anchor)
└── Zerion CLI integration research

Week of Apr 27 - May 3
├── ETHGlobal Open Agents (Layers 2,3,4,5 on EVM)
├── Solana: AgentBrain + RiskScore programs
├── GoldRush API integration
└── Dune dashboard creation

Week of May 4-10
├── Solana: Final programs + tests
├── Demo videos for each sidetrack submission
├── README polish per submission
├── GitHub repo organization
└── **May 11: SUBMIT EVERYTHING**
```

---

## Modular Architecture for Multi-Submit

### Core Solana Programs (build once)

| Program | Purpose | Used By |
|---------|---------|---------|
| `agent_registry` | Agent identity, skills, stake | ALL sidetracks |
| `job_escrow` | Payment flow, escrow, release | Payments, Commerce |
| `agent_brain` | Memory, learning, skill evolution | Agentic Engineering, Zerion |
| `risk_oracle` | Position health, alerts, scoring | Risk, GoldRush, Dune |
| `task_manager` | Cross-agent task delegation | Zerion CLI, Coordination |
| `reputation` | Scores, endorsements, leaderboard | Social, Reputation |

### Adapter Modules (swap per submission)

| Adapter | Wraps | Purpose |
|---------|-------|---------|
| `adapters/zerion_cli` | task_manager + agent_brain | Zerion CLI integration |
| `adapters/goldrush` | risk_oracle | Covalent GoldRush data feed |
| `adapters/dune` | risk_oracle + reputation | Dune Analytics queries |
| `adapters/raydium` | job_escrow | LP management via Raydium |

---

## Demo Strategy

Each sidetrack gets its own:
1. **Focused demo** — 2 min video showing ONE thing working
2. **README** — Explains the specific capability, links to full architecture
3. **GitHub branch** — `sidetrack/<name>` with the relevant code isolated

But they ALL reference the same core architecture doc, showing judges this isn't a toy — it's a system.

---

## What D-Mob Needs To Build (Priority Order)

### Sprint 1: Foundation (NOW → Apr 26)
- [ ] Anchor project scaffold: `~/repos/agent-economy-solana/`
- [ ] `agent_registry` program — register agent, set skills, stake tokens
- [ ] `job_escrow` program — create job, deposit, complete, release
- [ ] Tests for both

### Sprint 2: Intelligence (Apr 27 → May 3)
- [ ] `agent_brain` program — store/retrieve memory, skill evolution
- [ ] `risk_oracle` program — position monitoring, health scores
- [ ] GoldRush adapter — fetch position data from Covalent API
- [ ] Tests

### Sprint 3: Social + Coordination (May 4 → May 8)
- [ ] `reputation` program — score, endorse, leaderboard query
- [ ] `task_manager` program — create task, delegate, complete
- [ ] Zerion CLI adapter — agent discovers + delegates via CLI
- [ ] Tests

### Sprint 4: Polish + Submit (May 9 → May 11)
- [ ] Demo videos per sidetrack
- [ ] READMEs per submission
- [ ] GitHub branches per sidetrack
- [ ] Submit to all sidetracks

---

## Prize Potential

| Category | Amount | Confidence |
|----------|--------|------------|
| Tier 1 (direct hits) | $8,000+ | High |
| Tier 2 (good fit) | $5,000+ | Medium |
| Tier 3 (stretch) | $2,000+ | Low |
| Superteam AE Grant | ~200 USDG | High |
| **Main Frontier prizes** | **$20K-$100K+** | **If we ship well** |
| **TOTAL POTENTIAL** | **$680K+ pool** | |

---

## Tags
#frontier #hackathon #solana #sidetracks #submission-map #active
