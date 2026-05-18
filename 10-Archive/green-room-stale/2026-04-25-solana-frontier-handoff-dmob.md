# 🟢 Green Room Handoff — Solana Frontier (Colosseum)

**From:** YoYo (Strategies)  
**To:** DMOB (Labs)  
**Date:** 2026-04-25  
**Deadline:** May 11, 2026 (16 days)  
**Prize:** $230K+ + $250K accelerator  
**Priority:** 🔥 P0 — PRIMARY TARGET

---

## Status

Jordan confirmed: **Start Solana Frontier now.** Kite AI is P1 (still needs gas). Solana Frontier is the bigger bag and the immediate build target.

---

## What We Know

| Field | Value |
|-------|-------|
| **Host** | Colosseum (arena.colosseum.org) |
| **Track** | Agents + Tokenization |
| **Chain** | Solana |
| **Deadline** | May 11, 2026 |
| **Prize** | $230K+ pool |
| **Accelerator** | $250K pre-seed for winners |
| **Registration** | NOT DONE YET — Jordan needs to register |

**Strategy:** Solana = public beta. Avalanche = production (Retro9000, July 14). Port our existing AAE Solidity contracts to Anchor (Rust).

---

## Existing AAE Contracts (Solidity → Anchor Port)

All live at `~/repos/AAE/`:

| Solidity Contract | Anchor Equivalent | Status |
|-------------------|-------------------|--------|
| `AgentRegistry.sol` | `agent_registry` program | 🔴 Not started |
| `JobEscrow.sol` | `job_escrow` program | 🔴 Not started |
| `AgentMarketplace.sol` | `agent_marketplace` program | 🔴 Not started |
| `AgentToken.sol` | `agent_token` program (SPL) | 🔴 Not started |
| `AgentTokenFactory.sol` | `agent_token_factory` program | 🔴 Not started |
| `AgentRiskScore.sol` | `agent_risk_score` program | 🔴 Not started |
| `AgentBrain.sol` | `agent_brain` program | 🔴 Not started |

**Tests:** 24 tests passing in Solidity. Need Anchor equivalents.

---

## What DMOB Needs To Deliver

### Phase 1: Scaffold (This Week — Apr 25-28)
- [ ] Anchor project scaffold
- [ ] Devnet connection configured
- [ ] `AgentRegistry` program — agent registration, metadata
- [ ] Basic tests for AgentRegistry

### Phase 2: Core Programs (Apr 29-May 4)
- [ ] `JobEscrow` program — SOL payment escrow, completion flow
- [ ] `AgentMarketplace` program — job posting, hiring, payment
- [ ] `AgentToken` program — SPL token for agent reputation/utility
- [ ] Tests for all three

### Phase 3: Advanced (May 5-8)
- [ ] `AgentRiskScore` — health checks, performance tracking
- [ ] `AgentBrain` — on-chain memory/learning (if feasible in Anchor)
- [ ] Integration tests
- [ ] Deploy to devnet

### Phase 4: Demo + Submit (May 9-11)
- [ ] Minimal UI (single HTML + web3.js/anchor.js)
- [ ] Demo video script (Desmond will draft)
- [ ] Record demo video
- [ ] Submit to Colosseum

---

## Jordan's Tasks (Parallel)

- [ ] Register on arena.colosseum.org
- [ ] Fund Solana devnet wallet
- [ ] Get KITE testnet gas for Kite AI (separate track)

---

## Resources

- Anchor Book: https://book.anchor-lang.com/
- Solana Playground: https://beta.solpg.io/
- Existing AAE: `~/repos/AAE/`
- EVM-to-Solana cheat sheet: `02-Labs/Reference/Solana-Anchor-EVM-Cheat-Sheet.md`

---

**YoYo** — Standing by for strategy/prize track questions. Building is yours.
