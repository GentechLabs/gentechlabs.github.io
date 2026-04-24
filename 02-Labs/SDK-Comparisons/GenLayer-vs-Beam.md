# SDK Comparison: GenLayer vs Beam Cloud

**Date:** 2026-04-19
**Purpose:** Which SDK fits which Kite layer? Eat the meat, spit out the bones.

---

## Layer-by-Layer Comparison

| Layer | GenLayer | Beam Cloud | Verdict |
|-------|----------|------------|---------|
| **L1 AgentFi / Fee LP** | ❌ Not built for DeFi routing | ❌ No blockchain settlement | Build our own |
| **L2 Risk Intel** | ⚠️ Too slow — LLM consensus per call | ✅ Fast inference, sandboxed execution | **Beam** |
| **L3 Brain / Memory** | ❌ No real-time memory/learning | ✅ Stateful bots, persistent memory, fast GPU | **Beam** |
| **L4 Enforcement / SLAs** | ✅ Subjective consensus = core strength | ❌ No trust layer, no dispute resolution | **GenLayer** |
| **L5 Marketplace / Escrow** | ✅ On-chain settlement, dispute-aware escrow | ❌ No blockchain, no on-chain payments | **GenLayer** |
| **L6 Composition / Orchestration** | ⚠️ Single-contract scope, async messaging only | ✅ Multi-agent workflows, stateful routing | **Beam** |
| **L7 Governance** | ⚠️ Possible but overkill for voting | ⚠️ Possible but not the core use case | Build our own |

---

## Meat vs Bones

### GenLayer — 🥩 Meat
- Subjective dispute resolution with AI consensus (L4)
- On-chain escrow with evidence-based settlement (L5)
- Python contracts — easier to build/audit than Solidity
- Built-in appeal process (no custom dispute escalation needed)
- Web access + image processing inside contracts
- EVM-compatible via zkSync L2 anchor

### GenLayer — 🦴 Bones
- "Skills" plugin marketplace — it's a dev tool, not a revenue model
- 10-20% builder revenue share — not documented, likely misunderstood
- High-frequency operations — LLM consensus is too slow
- Background/continuous monitoring — contracts only run when called
- Gas model — opaque for LLM-heavy workloads

### Beam Cloud — 🥩 Meat
- Fast GPU inference for real-time risk scoring (L2)
- Stateful bots with persistent memory (L3 Brain)
- Multi-agent workflow orchestration (L6)
- Sandbox execution environments
- Developer-friendly deployment pipeline

### Beam Cloud — 🦴 Bones
- No blockchain settlement — can't handle on-chain escrow
- No trust/consensus layer — can't resolve subjective disputes
- No native payment rails — needs external integration
- Limited composability with DeFi protocols

---

## Decision Log

| Date | SDK | Decision | Reason |
|------|-----|----------|--------|
| 2026-04-19 | GenLayer | **Build L4 (Enforcement) on it** | Perfect fit for subjective dispute resolution. Target ETHGlobal (May 3) |
| 2026-04-19 | GenLayer | **Use for L5 (Escrow) dispute layer** | On-chain settlement + evidence-based disputes. Keep discovery off-chain |
| 2026-04-19 | Beam Cloud | **Build L2 (Risk Intel) + L3 (Brain) on it** | Fast inference, stateful memory, multi-agent orchestration |
| 2026-04-19 | Build Our Own | **L1 (Fee LP) + L7 (Governance)** | Neither SDK covers these well |

---

## Architecture Implication

Kite isn't "build on one platform." It's a **multi-SDK architecture**:

```
L7 Governance    → Custom
L6 Orchestration → Beam Cloud (multi-agent workflows)
L5 Escrow        → GenLayer (on-chain settlement + disputes)
L4 Enforcement   → GenLayer (subjective consensus)
L3 Brain         → Beam Cloud (stateful memory + fast inference)
L2 Risk Intel    → Beam Cloud (fast inference + sandbox exec)
L1 AgentFi       → Custom (DeFi routing + LP)
```

**Key insight:** GenLayer and Beam are complementary, not competing. GenLayer is the trust layer for subjective decisions. Beam is the compute layer for real-time agent intelligence. Kite uses both where they're strongest.

---
#GenLayer #Beam #SDK #AgentEscrow #Kite #comparison
