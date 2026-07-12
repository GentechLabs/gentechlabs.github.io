# Casper Agentic Buildathon 2026 — Submission Plan

**Hackathon:** [Casper Agentic Buildathon 2026](https://dorahacks.io/hackathon/casper-agentic-buildathon)
**Prize Pool:** $150,000 USD
**Deadline:** June 30, 2026 (~20 days from June 10)
**Platform:** DoraHacks
**Submission Requirements:** GitHub repo link + Demo video

---

## 1. Project Name & Tagline

### **CasperNet — The Agent Economy Protocol**

> *"Agents pay, trade, and settle — natively on Casper."*

An autonomous agent marketplace where AI agents discover services, negotiate prices, execute tasks, and settle payments — all via x402 micropayments on Casper Network. No API keys. No billing accounts. Just agents paying agents.

---

## 2. Track Selection: DeFi & Payments

### Why DeFi & Payments

| Factor | Assessment |
|--------|-----------|
| **Our existing stack** | `agentic-payments` SDK (x402 + MPP middleware) is production-ready TypeScript. `agent-escrow` has full settlement loop. We've built this exact pattern 3 times (BNB, Mantle, Kite). |
| **Casper's killer feature** | x402 is the *payment* protocol — it's literally the DeFi & Payments track's core technology. |
| **Competitive landscape** | The main competitor (kite-builds) is in the Innovation Track (Agentic AI × DeFi × RWA). The DeFi & Payments track is less crowded. |
| **Judge alignment** | Casper Association wants to see agents *using* x402 — building the payment infrastructure IS the DeFi track. |
| **Differentiation** | We're not just using x402 (like the RWA agent). We're building the *commerce layer* ON TOP of x402 — agent-to-agent payments, reputation, escrow. |

### Why NOT other tracks
- **Agentic AI:** Too broad, we'd compete with everyone. DeFi is more focused.
- **Cross-Chain:** Would require bridging Casper to other chains — complex, risky in 20 days.
- **RWA Tokenization:** The kite-builds competitor already dominates this space with RWA rent settlement. We'd be second-best.

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CasperNet: Agent Economy Protocol                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    AGENT LAYER (TypeScript)                      │   │
│  │                                                                  │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────────┐  │   │
│  │  │  Agent   │   │  Agent   │   │  Agent   │   │   Agent    │  │   │
│  │  │ Registry │   │ Payments │   │  Escrow  │   │ Reputation │  │   │
│  │  │ (Identity)│   │ (x402)  │   │(Escrow)  │   │  (Trust)   │  │   │
│  │  └────┬─────┘   └────┬─────┘   └────┬─────┘   └─────┬──────┘  │   │
│  │       │              │              │               │          │   │
│  │       └──────────────┼──────────────┼───────────────┘          │   │
│  │                      ▼              ▼                          │   │
│  │              ┌──────────────┐  ┌──────────┐                    │   │
│  │              │   Agent      │  │  x402    │                    │   │
│  │              │   Commerce   │  │ Payment  │                    │   │
│  │              │   Router     │  │ Gateway  │                    │   │
│  │              └──────┬───────┘  └────┬─────┘                    │   │
│  └─────────────────────┼──────────────┼───────────────────────────┘   │
│                        │              │                                │
├────────────────────────┼──────────────┼────────────────────────────────┤
│  CASPER BLOCKCHAIN     │              │                                │
│                        ▼              ▼                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 SMART CONTRACTS (Odra/Rust → WASM)              │   │
│  │                                                                 │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │   │
│  │  │ AgentRegistry│  │ ServiceMarket│  │  AgentEscrow        │   │   │
│  │  │ (Identity +  │  │ (Service     │  │  (x402 Settlement + │   │   │
│  │  │  Reputation) │  │  Listings)   │  │   EIP-7702 style)   │   │   │
│  │  └─────────────┘  └──────────────┘  └─────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                        │                                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              x402 FACILITATOR (Live on Mainnet)                  │   │
│  │  Agent calls endpoint → HTTP 402 → Agent signs → Data returned  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Data Flow:
  1. Agent A discovers Agent B's service via AgentRegistry
  2. Agent A calls Agent B's endpoint → HTTP 402 + price
  3. Agent A signs x402 payment → Agent B's facilitator verifies
  4. Agent B executes task, returns result
  5. Payment settles on-chain via AgentEscrow contract
  6. Reputation updated on AgentRegistry
```

---

## 4. Tech Stack

### Agent Layer (TypeScript)
| Component | Technology | Why |
|-----------|-----------|-----|
| Agent SDK | `casper-js-sdk` (npm) | Official Casper TypeScript SDK |
| x402 Client | Custom x402 adapter using `@x402/core` | We already built this for agentic-payments |
| Agent Logic | Python + TypeScript hybrid | Python for agent decision-making, TS for Casper integration |
| Payment Gateway | Adapted from `agentic-payments` SDK | Our dual-protocol middleware, adapted for Casper x402 |

### Smart Contracts (Rust → WASM)
| Component | Technology | Why |
|-----------|-----------|-----|
| Contract Framework | Odra | Official Casper smart contract framework |
| Compilation | `cargo odra build` → WASM | Rust → WASM is the native path |
| Settlement | AgentEscrow contract | Escrow with x402 proof settlement |
| Registry | AgentRegistry contract | On-chain agent identity + reputation |

### Infrastructure
| Component | Technology | Why |
|-----------|-----------|-----|
| RPC | CSPR.cloud API | Enterprise middleware, REST + Streaming |
| Wallet | CSPR.build Agent Skills | Wallet creation, signing, transaction handling |
| Testing | Odra test framework | Rust-native testing, same as competitor |
| Demo | Remotion (hackathon-demos) | Our existing demo video factory |

---

## 5. Component Breakdown

### Component 1: AgentRegistry (Smart Contract)
**Language:** Rust (Odra)
**Purpose:** On-chain agent identity + reputation system

```
AgentRegistry Contract:
  - register_agent(name, capabilities, endpoint) → agent_id
  - update_reputation(agent_id, score_delta)
  - get_agent(agent_id) → AgentRecord
  - list_agents(capability_filter) → AgentRecord[]
  - AgentRecord { id, name, owner, capabilities[], endpoint, reputation, created_at }
```

### Component 2: ServiceMarket (Smart Contract)
**Language:** Rust (Odra)
**Purpose:** On-chain service listings with x402 pricing

```
ServiceMarket Contract:
  - list_service(agent_id, name, description, price_cspr, endpoint) → service_id
  - update_service(service_id, price, endpoint)
  - get_service(service_id) → ServiceRecord
  - list_services(category_filter) → ServiceRecord[]
  - ServiceRecord { id, agent_id, name, description, price, endpoint, active }
```

### Component 3: AgentEscrow (Smart Contract)
**Language:** Rust (Odra)
**Purpose:** x402 payment settlement with escrow protection

```
AgentEscrow Contract:
  - create_escrow(buyer, service_id, amount) → escrow_id
  - release_escrow(escrow_id, provider, x402_proof)
  - cancel_escrow(escrow_id, buyer)
  - EscrowRecord { id, buyer, provider, service_id, amount, state, created_at }
```

### Component 4: x402 Payment Gateway (TypeScript)
**Purpose:** HTTP 402 middleware for agent endpoints

- Adapted from our `agentic-payments` SDK
- Casper-specific x402 adapter (CSPR token, not USDC)
- Facilitator integration with Casper mainnet
- Supports both x402 and MPP protocols

### Component 5: Agent Commerce Router (TypeScript)
**Purpose:** Multi-agent orchestration + task execution

- Agent discovers services via AgentRegistry
- Negotiates price (dynamic or fixed via x402)
- Executes task via provider's endpoint
- Settlement through AgentEscrow
- Reputation update after completion

### Component 6: Demo & Documentation
**Purpose:** Hackathon submission polish

- Demo video via Remotion (hackathon-demos)
- README with architecture, setup, demo instructions
- 8+ passing tests (match competitor's quality)
- Deployed to Casper testnet

---

## 6. What We Have vs What We Need to Build

### ✅ Already Built (Reuse)
| Asset | Location | Adaptation Needed |
|-------|----------|------------------|
| x402 + MPP middleware | `/root/repos/agentic-payments/` | Adapt for Casper CSPR (not USDC/EVM) |
| Agent escrow pattern | `/root/repos/agent-escrow/` | Port Solidity → Odra Rust |
| Agent commerce flow | `/root/repos/kite-agent-commerce/` | Port Kite testnet → Casper testnet |
| Demo video factory | `/root/repos/hackathon-demos/` | Add Casper config, record new demo |
| EIP-712 signature flow | `agent-escrow/tests/` | Adapt for Casper signing scheme |

### 🔧 Need to Build (New)
| Component | Effort | Priority |
|-----------|--------|----------|
| Casper x402 adapter | Medium | **P0** — core differentiator |
| AgentRegistry contract (Odra/Rust) | Medium | **P0** — needed for agent identity |
| ServiceMarket contract (Odra/Rust) | Medium | **P1** — needed for service discovery |
| AgentEscrow contract (Odra/Rust) | Medium | **P0** — needed for settlement |
| casper-js-sdk integration | Low | **P0** — TypeScript agent SDK |
| Integration tests (8+ tests) | Medium | **P0** — match competitor quality |
| Demo video | Low | **P1** — submission requirement |
| README + docs | Low | **P1** — submission requirement |

### ⚠️ Risk Assessment
| Risk | Mitigation |
|------|-----------|
| Rust/Odra learning curve | We've written Solidity; Rust is similar in contract logic. Use Odra's examples. |
| x402 on Casper uses CSPR (not USDC) | Adapt our adapter; CSPR is simpler (no stablecoin math). |
| 20-day timeline | Focus on core: x402 + escrow + registry. Skip nice-to-haves. |
| Casper testnet access | Use CSPR.cloud APIs; testnet is free. |

---

## 7. Competitive Advantages Over kite-builds/casper-rwa-agent

| Dimension | kite-builds (RWA Agent) | CasperNet (Ours) |
|-----------|------------------------|------------------|
| **Scope** | Single-purpose (RWA rent settlement) | Full commerce protocol (any service) |
| **Marketplace** | No service discovery | On-chain ServiceMarket + AgentRegistry |
| **Identity** | None (just an agent wallet) | Agent reputation + identity on-chain |
| **Escrow** | Simple x402 pay-per-call | Escrow with dispute resolution |
| **Payment** | x402 only | x402 + MPP dual-protocol |
| **Agent-to-Agent** | No (human → agent only) | Full agent-to-agent commerce |
| **Reusability** | One-off demo | Framework for any agent economy |
| **SDK** | Rust-only | TypeScript + Python (accessible to more devs) |
| **Demo Quality** | 8/8 tests, testnet deployed | Match or exceed (10+ tests planned) |
| **Innovation** | Incremental (x402 on RWA) | Foundational (agent economy infrastructure) |

**Key Differentiator:** kite-builds built an *agent that uses x402*. We're building the *infrastructure that enables any agent to use x402 for commerce*. It's the difference between building one shop and building the marketplace.

---

## 8. Timeline (20 Days)

### Week 1: Foundation (June 11-17)

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 1-2 | Setup Casper dev environment, install Odra, casper-js-sdk | Jordan | Working dev environment |
| 3-4 | Adapt x402 adapter for Casper (CSPR, not USDC) | Jordan | `casper-x402-adapter.ts` |
| 5-6 | Write AgentRegistry contract (Odra/Rust) | Jordan | `agent_registry/` with tests |
| 7 | Write ServiceMarket contract (Odra/Rust) | Jordan | `service_market/` with tests |

### Week 2: Core (June 18-24)

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 8-9 | Write AgentEscrow contract (Odra/Rust) | Jordan | `agent_escrow/` with tests |
| 10-11 | Build Agent Commerce Router (TypeScript) | Jordan | `agent-router/` |
| 12-13 | Integration tests (all contracts + x402) | Jordan | 10+ passing tests |
| 14 | Deploy to Casper testnet | Jordan | Live on testnet |

### Week 3: Polish & Submit (June 25-30)

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 15-16 | Demo video production (Remotion) | Jordan | `demo.mp4` |
| 17-18 | README, architecture docs, setup guide | Jordan | Complete README.md |
| 19 | Final testing, bug fixes | Jordan | Clean repo |
| 20 | Submit to DoraHacks | Jordan | ✅ Submitted |

### Critical Path
```
Day 1-2: Environment Setup
    ↓
Day 3-4: x402 Adapter (BLOCKS everything)
    ↓
Day 5-9: Smart Contracts (parallel if possible)
    ↓
Day 10-11: Agent Router
    ↓
Day 12-14: Tests + Deploy
    ↓
Day 15-20: Polish + Submit
```

---

## 9. Research Findings

### Casper AI Toolkit Capabilities (Live on Mainnet, Jun 4 2026)

1. **x402 Micropayments** — Production facilitator on mainnet. Agents pay per API call via HTTP 402 status. No API keys, no billing accounts. Cryptographic proof of payment.

2. **Odra Framework** — Rust smart contracts compiled to WASM. Agents can write, test, and deploy contracts autonomously. Type-safe, production-ready.

3. **Account Abstraction** (Planned) — Agent on-chain identities, spending controls, fixed-cost transactions. Under development per Casper Manifest.

4. **MCP Servers** — Model Context Protocol for agent capabilities. Standardized tool access for AI agents.

5. **CSPR.build Agent Skills** — Wallet connections, transaction signing, event handling, API access. Plug-and-play agent capabilities.

6. **CSPR.cloud APIs** — Enterprise middleware with REST, Streaming, and Node API layers. Scales blockchain interaction.

7. **CSPR.click** — SSO through social platforms (Google, Apple). Simplified Web3 auth.

### x402 on Casper vs EVM

| Aspect | Casper x402 | EVM x402 (Base/BSC) |
|--------|-------------|---------------------|
| **Token** | CSPR (native) | USDC/USDT (ERC-20) |
| **Settlement** | Native on-chain | ERC-20 transfer + facilitator |
| **Facilitator** | Casper mainnet (production) | Base/BSC facilitators |
| **Gas Model** | Predictable, WASM-native | EVM gas (variable) |
| **Account Model** | Ed25519/Secp256k1 keys | EOA or smart contract |
| **Smart Contracts** | Odra (Rust → WASM) | Solidity → EVM bytecode |
| **Speed** | ~2s finality | ~2s finality (L1) |

### SDKs Available (No Rust Required for Agent Logic)

- **TypeScript:** `casper-js-sdk` (npm) — mature, official, full API
- **Python:** Supported via Casper SDKs (mentioned on CoinList docs)
- **Go:** Supported
- **Rust:** Required ONLY for smart contracts (Odra). Agent logic can be TypeScript/Python.

**Verdict:** We do NOT need to learn Rust for the agent layer. Only the smart contracts need Rust/Odra. The agent SDK is TypeScript. This is a major advantage — we can build fast.

### Buildathon Submission Requirements

- **GitHub repo** with source code
- **Demo video** showing the project in action
- **Tracks:** Agentic AI, DeFi & Payments, Cross-Chain, RWA Tokenization
- **Deadline:** June 30, 2026 (July 5 per some sources — verify on DoraHacks)
- **Community voting:** CSPR.fans mini-app for finalist selection

---

## 10. Success Criteria

### Must-Have (Minimum Viable Submission)
- [ ] x402 payment flow working on Casper testnet
- [ ] AgentRegistry contract deployed
- [ ] AgentEscrow contract deployed
- [ ] TypeScript agent that discovers services and pays via x402
- [ ] 5+ passing tests
- [ ] README with setup + demo instructions
- [ ] Demo video (2-3 minutes)
- [ ] GitHub repo submitted to DoraHacks

### Nice-to-Have (Differentiation)
- [ ] ServiceMarket contract (full marketplace)
- [ ] Agent reputation system
- [ ] 10+ tests (match/exceed competitor)
- [ ] Multiple agent types (buyer, provider, validator)
- [ ] MCP server integration
- [ ] Deployed to mainnet (if testnet proves stable)

---

## 11. Budget & Resources

### Time Investment
- Jordan: ~160 hours over 20 days (8 hours/day average)
- Focus: Smart contracts (Rust) + TypeScript agent + testing + demo

### Infrastructure Costs
- Casper testnet: Free
- CSPR.cloud API: Free tier sufficient
- Demo video: Existing Remotion setup (no cost)
- Domain/hosting: Not required (demo via terminal/screen recording)

### Potential Prize Allocation
- 1st Place: $50,000-$75,000 (if we win DeFi & Payments track)
- 2nd/3rd: $20,000-$30,000
- Innovation Track bonus: Possible if we cross-pollinate

---

## 12. Key Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Rust/Odra learning curve | High | Medium | Use Odra examples, focus on simple contracts first |
| x402 adapter complexity | Medium | High | Start with simplest case (single payment), iterate |
| Testnet instability | Low | High | Deploy early (Day 14), have fallback plan |
| Demo video quality | Medium | Medium | Use existing Remotion factory, record early |
| Competitor quality | High | Medium | Focus on scope (full protocol vs single agent) |
| Time overrun | Medium | High | Strict scope: core components only, no extras |

---

## 13. Decision Record

### Why NOT Rust-only
The competitor (kite-builds) went Rust/Odra for everything. We're going TypeScript for agent logic + Rust for contracts. This is intentional:
- **Faster development** — TypeScript is our strength
- **Wider appeal** — More devs can understand and extend our code
- **Proven pattern** — We've built x402 middleware in TypeScript 3 times
- **Rust only where needed** — Smart contracts require it; agent logic doesn't

### Why NOT Cross-Chain
Cross-chain adds bridging complexity that we can't solve in 20 days. Casper's x402 is already the "cross-chain" of agent payments — it's HTTP-native, chain-agnostic at the protocol level.

### Why NOT RWA Track
kite-builds already has a polished RWA agent (8/8 tests, testnet deployed). We'd be competing for 2nd place. Better to win DeFi & Payments with a unique angle.

---

*Document prepared: June 10, 2026*
*Status: Ready for Jordan's review*
*Next action: Jordan approves → Begin Day 1 setup*
