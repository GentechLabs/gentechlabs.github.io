# SDK Comparison Tracker

**Purpose:** Compare SDKs and dev tools against AgentEscrow/Kite needs. "Eat the meat, spit out the bones."

**Strategy:** Modular SDK architecture — pick the best tool for each layer. Optimized for **hackathon speed** and **ETHGlobal (May 3)**.

---

## Evaluation Criteria

| Criteria | What We're Asking |
|----------|-------------------|
| **Core Function** | What does it actually do? (not marketing) |
| **Kite Fit** | Which Kite layer(s) does it touch? |
| **Hackathon Speed** | Hours to prototype? Can we build it in a weekend? |
| **Meat** | What's genuinely useful for AgentEscrow |
| **Bones** | What's noise / not applicable / hype |
| **Verdict** | Build on it? Integrate? Ignore? |

---

## SDKs Evaluated

### 1. GenLayer SDK
- **Status:** ✅ Evaluated
- **Core Function:** Python smart contracts with native LLM + web access, on-chain consensus for subjective decisions
- **Kite Fit:** L4 (Enforcement/SLAs), L5 (Escrow — dispute layer)
- **Hackathon Speed:** ⚡ High — boilerplate ready, Python contracts, Studio for quick testing
- **Meat:** Subjective dispute resolution, on-chain escrow, Python > Solidity, built-in appeals, web/image access in contracts
- **Bones:** "Skills" plugin is dev tooling not revenue SDK, LLM consensus latency kills high-frequency ops, no background monitoring, opaque gas model
- **Verdict:** ✅ **Build L4 Enforcement on it for ETHGlobal** — fastest path to a working demo with real AI consensus
- **Research:** `./GenLayer-vs-Beam.md`, `./AgentEscrow-vs-GenLayer.md`, `../GenLayer-SDK/Technical Assessment.md`

### 2. Beam Cloud SDK
- **Status:** ✅ Evaluated
- **Core Function:** Fast GPU inference, stateful bots, multi-agent orchestration
- **Kite Fit:** L2 (Risk Intel), L3 (Brain/Memory), L6 (Composition/Orchestration)
- **Hackathon Speed:** ⚡ High — stateful bots deploy fast, multi-agent workflows ready
- **Meat:** Fast real-time inference, persistent agent memory, multi-agent workflows, sandbox execution
- **Bones:** No blockchain settlement, no trust/consensus layer, no native payment rails
- **Verdict:** ✅ **Build L2 Risk + L3 Brain + L6 Orchestration on it** — complements GenLayer perfectly
- **Research:** `./GenLayer-vs-Beam.md`, `../Beams-Research.md`

### 3. Custom (Build Our Own)
- **Status:** ⏳ Not started
- **Core Function:** DeFi routing, LP automation, governance mechanics
- **Kite Fit:** L1 (AgentFi/Fee LP), L7 (Governance)
- **Hackathon Speed:** TBD — depends on scope
- **Verdict:** Build custom — neither SDK covers these well
- **Research:** N/A

---

## Hackathon Module Strategy

For hackathons, we don't build the full stack. We pick **the best SDK for each layer** and swap adapters per event:

| Hackathon Target | Primary SDK | Layer(s) | Why |
|------------------|-------------|----------|-----|
| Kite AI (Apr 26) | GenLayer + Beam | L4 Enforcement + L3 Brain | Enforcement: AI consensus disputes. Brain: stateful agent memory |
| ETHGlobal Open Agents (May 3) | GenLayer | L4 + L5 | AI consensus + on-chain escrow — "agents that police themselves" |
| Dev3pack (May 8) | Beam Cloud | L3 Brain | Stateful AI agent with memory — fast GPU, visual demo |
| Superteam Frontier (May 11) | All SDKs | Full stack | Modular submission — Beam for brain/risk, GenLayer for enforcement/escrow |
| Any DeFi-focused | Custom | L1 AgentFi | Our core IP — LP automation + fee routing |

**The Rule:** Build each layer once. Assemble per hackathon like LEGO. No rewriting.

---

## Decision Log

| Date | SDK | Decision | Reason |
|------|-----|----------|--------|
| 2026-04-19 | GenLayer | ✅ Build L4 Enforcement for ETHGlobal + Kite AI | Best hackathon fit — AI consensus demo, weekend-buildable, Python |
| 2026-04-19 | GenLayer | ✅ Use for L5 Escrow disputes | On-chain settlement + evidence. Discovery stays off-chain |
| 2026-04-19 | Beam Cloud | ✅ Build L2 Risk + L3 Brain + L6 Orchestration | Complements GenLayer — fast inference, stateful memory, multi-agent workflows |
| 2026-04-19 | Custom | ⏳ Build L1/L7 post-hackathon | Core IP, but not hackathon-ready |
| 2026-04-19 | **Modular Strategy** | ✅ **Adopt multi-SDK architecture** | GenLayer (trust layer) + Beam (compute layer) = complementary, not competing |

---
#SDK #AgentEscrow #Kite #research #comparisons #hackathon
