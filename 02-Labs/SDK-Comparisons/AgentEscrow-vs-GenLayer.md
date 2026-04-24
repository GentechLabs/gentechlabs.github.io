# AgentEscrow: Current Architecture vs GenLayer

**Date:** 2026-04-19
**Purpose:** Side-by-side comparison of our current approach vs what GenLayer provides. Identify what to adopt, what to keep.

---

## Architecture Comparison

| | **Our Approach** | **GenLayer** | **Verdict** |
|---|---|---|---|
| **Contract Language** | Solidity (Foundry) | Python | 🔄 Adopt Python for GenLayer contracts — faster to build |
| **Chain** | AVAX subnet (endgame) | GenLayer (zkSync L2) | 🔄 Use GenLayer for hackathon, AVAX for endgame |
| **Dispute Resolution** | Manual or external oracle | Native AI consensus | ✅ Adopt — GenLayer's core strength |
| **Agent Quality Check** | External AI validator | `gl.nondet.exec_prompt()` built-in | ✅ Adopt — no external dependency needed |
| **Payments** | x402 (USDC) | $GEN token | ⚠️ Keep USDC — add GEN as secondary for GenLayer |
| **Web Access in Contract** | ❌ Need oracle/external | ✅ `gl.nondet.web.*` native | ✅ Adopt — huge advantage for SLA monitoring |
| **Image Processing** | ❌ External | ✅ `gl.nondet.exec_prompt(images=...)` | ✅ Adopt — visual evidence for disputes |
| **Appeal Process** | Custom build required | ✅ Built-in multi-round appeals | ✅ Adopt — saves weeks of dev |
| **Background Monitoring** | Custom watchers | ❌ Contracts only run when called | ⚠️ Keep our approach — GenLayer can't do this |
| **High-Frequency Ops** | ✅ Fast on AVAX | ❌ LLM consensus too slow | ⚠️ Keep our approach for speed-critical paths |
| **Memory/State** | Custom on-chain state | `TreeMap`/`DynArray` persistent | 🔄 GenLayer storage is sufficient for L4 |

---

## What GenLayer Replaces (Good)
- Manual dispute resolution → AI consensus
- External oracle for web checks → native `gl.nondet.web.*`
- Custom appeal system → built-in multi-round appeals
- Image evidence processing → native LLM image evaluation
- Solidity contracts for L4 → Python contracts (faster to build)

## What We Keep (Good)
- x402 USDC payments — established, user-friendly
- AVAX subnet for endgame — our chain, our rules
- Background monitoring/SLA watchers — GenLayer can't do this
- High-frequency marketplace operations — GenLayer too slow

## What We Need to Build Anyway
- L1 AgentFi (DeFi routing, LP automation) — neither SDK covers this
- L7 Governance — neither SDK is optimized for this
- Cross-chain bridging (USDC ↔ GEN) — needed for GenLayer integration

---

## ETHGlobal Strategy

For **ETHGlobal Open Agents (May 3)**, we build L4 Enforcement on GenLayer because:

1. **AI consensus demo** = impressive, hackathon-friendly
2. **Python contracts** = faster to build than Solidity
3. **Built-in appeals** = no custom dispute logic needed
4. **Web access** = demo SLA monitoring without oracles
5. **Boilerplate ready** = clone → build → deploy in days

**Demo scenario:** Agent fails SLA → user submits evidence → GenLayer LLM evaluates → consensus → automatic payout/slashing. End-to-end in one transaction.

---
#GenLayer #AgentEscrow #comparison #hackathon #ETHGlobal
