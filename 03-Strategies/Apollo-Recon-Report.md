# Apollo (Apolo) Protocol — Recon Report
**Date:** 2025-04-25
**Agent:** YoYo
**Status:** Complete
**Source:** github.com/DarienPerezGit/Apolo, apolo-protocol.xyz, X @_A_polo__

---

## Executive Summary

**Recommendation: MONITOR — do not integrate on critical path.**

Apollo is a **simple escrow contract + off-chain relayer** built on BNB Chain with GenLayer AI adjudication. It validates our thesis but offers minimal integration value today: **zero mainnet volume**, **single-dev team**, **trusted-relayer centralization**, and **no token or incentive layer**. Worth a lightweight relationship play for GenLayer ecosystem access, but do not build dependencies on it.

---

## What Apollo Actually Does (Under the Hood)

### Core Architecture

```
Client → funds ApoloEscrow.sol (BNB Mainnet)
              │
              ▼
    Off-chain Solver (Node.js on Render)
              │ calls
              ▼
    DeliveryValidator.py (GenLayer studionet)
              │ fetches slaUrl, AI adjudicates
              ▼
    Solver signs + executes
         ┌────┴────┐
         ▼         ▼
    release()  refund()
    (merchant) (client)
```

### Contracts

| Contract | Address | Purpose |
|----------|---------|---------|
| `ApoloEscrow.sol` | `0x055ad3F93Cca3B7df30a9C11AD37EBBe8b41cd4d` | Simple 5-state escrow (PENDING→FUNDED→VALIDATING→RELEASED/REFUNDED) |
| `ApoloSessionRouter.sol` | — | Session keys with spend limits + EIP-712 signatures |
| `ZKVerifier.sol` | — | Optional Groth16 ZK proof verification (disabled by default) |

### Key Mechanics

1. **fund()** — Client locks BNB in escrow against an `intentHash`
2. **fundWithZK()** — Same but with optional Groth16 ZK proof of intent correctness (currently disabled)
3. **markValidating()** — Relayer moves state to VALIDATING
4. **release() / refund()** — **Only relayer can call**. Relayer is a single EOA: `0xa2e036eD6f43baC9c67B6B098E8B006365b01464`
5. **GenLayer adjudication** — Non-deterministic Python contract checks the real API endpoint and returns approved/rejected

### A2A Agent Integration

- `ApoloSLAWatcherAgent` built on A2A protocol
- Monitors SLA endpoints autonomously
- Triggers settlement without human step
- Deployed on Render

---

## Competitive Comparison: Apollo vs AgentEscrow + x402

| Dimension | Apollo | Gentech (AgentEscrow + x402) |
|-----------|--------|------------------------------|
| **Chain** | BNB Mainnet + GenLayer studionet | Multi-chain (AVAX, Base, etc.) |
| **Payment rail** | Direct BNB escrow | x402 per-request micropayments |
| **Adjudication** | GenLayer AI (off-chain Python) | TBD (ours) |
| **Trust model** | Trusted relayer (single EOA) | TBD |
| **ZK** | Optional Groth16 (unproven, disabled) | None yet |
| **Session keys** | Yes (spend limits) | TBD |
| **Agent protocol** | A2A | Custom / Hermes-native |
| **Live volume** | **0 escrows, 0 BNB locked** | TBD |
| **Maturity** | Hackathon → mainnet (2 dev cycles) | Internal |
| **Team** | 1 dev | Gentech |
| **Token** | None | $TECH |

### Where Apollo Wins
- **Live on mainnet** — They shipped. We can learn from their deployment pattern.
- **GenLayer integration** — Real-world example of x402 → escrow → GenLayer adjudication → settlement
- **A2A protocol agent** — Shows how autonomous agents can close escrow loops
- **ZK forward-compatibility** — Circuit architecture exists even if unused

### Where We Win
- **x402 integration** — Per-request micropayments are more flexible than lump-sum escrow
- **Multi-chain** — Not locked to BNB Chain
- **Token incentive layer** — $TECH burn/recycle mechanism (see `tech-payment-router` skill)
- **Team depth** — Multi-agent org vs solo dev
- **No trusted relayer** — Our design can avoid single-EOA settlement risk

---

## Complementary or Competing?

**Thesis: Complementary. Implementation: Mildly competing.**

- **Complementary** — We both believe agents need blockchain-native money handling. Apollo validates our market. Their GenLayer relationship could open doors.
- **Competing** — If we both build "agent escrow," we're solving the same problem differently. But Apollo has ~0 users, so they're not a competitive threat.
- **No token overlap** — They have no token. No liquidity conflicts.
- **Chain overlap minimal** — They're BNB-native. We're AVAX/Base/Solana.

---

## Risk Assessment

| Risk | Probability | Impact | Score |
|------|-------------|--------|-------|
| Trusted relayer rugs or gets compromised | High | High | 🔴 **Critical** |
| Single-dev bus factor | High | Medium | 🔴 **High** |
| GenLayer studionet instability | Medium | Medium | 🟡 **Medium** |
| Zero adoption / abandoned | Medium | Low | 🟡 **Medium** |
| ZK layer never activated | High | Low | 🟢 **Low** |

**Red flags:**
1. **Relayer is a single EOA.** The `0xa2e...` address can unilaterally release or refund ALL funds. No multi-sig, no threshold, no timelock.
2. **0 mainnet volume.** Site shows 0 escrows, 0 BNB locked, 0 settled, 0 refunded. README claims 2 test cycles but stats say otherwise.
3. **Solo dev.** DarienPerezGit is the only committer. 4 GitHub stars. 57 X followers.
4. **Pivoted from "Rebyt."** Commit message says "pivot Rebyt -> Apolo" — previous project didn't work.
5. **No audits.** No mention of audit. Foundry tests exist but coverage unknown.

**Green flags:**
1. Shipped mainnet contract — execution bias
2. Clean monorepo structure — good engineering hygiene
3. GenLayer ecosystem player — strategic network value
4. MIT license — open to fork/learn from
5. A2A protocol integration — forward-thinking

---

## Scenario Recommendations

### Hackathon / Demo
- **Use as reference, not dependency.** Study their GenLayer adjudication pattern for our own hackathon submissions.
- **Do NOT build on top of Apollo.** Their relayer can brick our demo.

### Pilot Integration
- **Lightweight relationship only.** Follow on X, join their Discord if any, maybe do a joint tweet/thread about agentic commerce.
- **No code integration.** Their contracts are too immature and centralized.

### Production
- **Not ready.** Wait for:
  - Multi-party threshold signing (their V2 roadmap)
  - Real volume > $10K locked
  - Audit report
  - Team expansion beyond 1 dev

---

## Strategic Take for Jordan

You said: *"We're going to integrate with most of these projects because of network effect of being early to the space."*

**My pushback:** Apollo offers **relationship value, not technical value**. Here's the right play:

1. **Monitor & learn** — Their GenLayer + x402 + escrow flow is a working reference implementation. DMOB should read their contracts (especially `ApoloEscrow.sol`) to compare against our AgentEscrow design.
2. **Relationship, not integration** — Follow them, engage on X, maybe do a "agentic commerce ecosystem" thread tagging Apollo + other players. Costs nothing. Builds network.
3. **Do NOT route payments through them** — Trusted relayer = counterparty risk we don't need.
4. **If GenLayer becomes strategic** — Apollo is a friendly ecosystem player. They could intro us to GenLayer Labs team or builders.

---

## Next Steps

| Step | Owner | Priority |
|------|-------|----------|
| DMOB reviews `ApoloEscrow.sol` vs our AgentEscrow | DMOB | Medium |
| Follow @_A_polo__ on X, monitor updates | YoYo | Low |
| Add Apollo to `02-Labs/Apollo-Agent-Infrastructure.md` competitive tracker | YoYo | Done |
| Evaluate GenLayer studionet for our own use | DMOB / Gentech | Medium |
| Revisit if/when Apollo hits >$10K volume or V2 threshold signing | YoYo | Future |

---

## Raw Data

- **GitHub:** `DarienPerezGit/Apolo` (4 stars, 98 commits, 1 contributor)
- **Contract:** `0x055ad3F93Cca3B7df30a9C11AD37EBBe8b41cd4d` (BNB Mainnet)
- **Relayer:** `0xa2e036eD6f43baC9c67B6B098E8B006365b01464`
- **Frontend:** `project-apolo.vercel.app`
- **Solver:** `apolo-solver.onrender.com`
- **X:** `@_A_polo__` (57 followers)
- **License:** MIT
- **Stack:** Solidity + Foundry, Node.js ESM, React + Vite, GenLayer Python SDK, A2A Protocol
