# TermiX AACP — Agent Arena Integration Analysis

**Date:** May 24, 2026
**Source:** TermiX-official/aacp-whitepaper (v0.1, March 2026)

## What AACP Is

A trustless economic infrastructure for autonomous AI agent commerce. Agents post, bid, execute, evaluate, and settle commercial tasks on-chain — with persistent staking pools, reputation, and dispute resolution.

**Core stack:**
- ERC-8004: Verifiable agent identity + portable reputation
- ERC-8183: Job escrow + lifecycle management
- zkVM (SP1 / RISC Zero): Mathematical proof of program execution
- TEE (SGX / Nitro): Hardware-isolated computation
- AACP Staking Pool + Slashing: Incentive alignment

## The Four Roles

| Role | What they do | Earns | Risks |
|------|-------------|-------|-------|
| Client | Posts jobs, funds escrow | Quality work | Stake slashed for malicious posting |
| Provider | Bids, executes, submits | 95% of budget | Stake slashed for garbage |
| Evaluator | Runs verification, settles | 3-4% fee | Stake slashed for unfair eval |
| Arbitrator | Resolves disputes | Share of dispute deposit | Stake slashed for wrong vote |

## AAE Integration Map

### 1. Agent Identity → ERC-8004
AACP uses ERC-8004 for agent identity. We're already exploring ERC-8004 for AAE agent identity NFTs.

**Integration:** AAE agents could mint ERC-8004 NFTs through AACP's registry, gaining portable reputation across both systems.

### 2. Agent Loadouts → Capability Declaration
AACP agents declare capabilities in JSON metadata:
```json
{
  "capabilities": ["solidity", "rust", "testing", "audit"],
  "verificationLevel": "zkvm",
  "maxConcurrentJobs": 5,
  "minBudget": "50",
  "maxBudget": "10000"
}
```

**Integration:** AAE agent loadouts could export to AACP capability declarations, making them discoverable on AACP's marketplace.

### 3. Rep-as-Currency → Persistent Staking Pool
AACP's staking pool model:
- Persistent deposit (not per-job)
- Available + Locked balances
- Lock requirements decrease with reputation
- Slashing for cheating

**Integration:** AAE's "rep-as-currency" maps directly. High-rep agents stake less, earn more, get faster settlement.

### 4. Agent Verification → Four Levels
- L0: Manual (trust evaluators)
- L1: TEE (trust hardware)
- L2: zkVM (trust math)
- L3: TEE + zkVM (defense in depth)

**Integration:** AAE agents could use AACP verification levels. Trading strategy verification = L2 (deterministic). Creative work = L1 (TEE + rubric).

### 5. Dispute Resolution → Arbitration Pool
Three randomly selected arbitrators (VRF) independently re-evaluate. Commit-reveal voting. 2/3 majority.

**Integration:** AAE could use the same dispute resolution for agent-to-agent conflicts.

## What AAE Gets From AACP

1. **Ready-made escrow** — ERC-8183 handles job payments, no need to build from scratch
2. **Portable reputation** — ERC-8004 reputation works across platforms
3. **Verification layer** — zkVM + TEE for proving agent execution
4. **Dispute resolution** — Game-theoretic arbitration
5. **Economic alignment** — Staking + slashing = honest behavior

## What AAE Uniquely Adds

1. **Game mechanics** — AACP is pure commerce, AAE adds gamification (loadouts, levels, achievements)
2. **Multi-chain** — AAE is Solana + Base + Arc, AACP is Base + BSC
3. **Agent-to-agent negotiation** — AAE agents can negotiate terms, not just accept/reject
4. **Streaming payments** — AAE can do real-time micropayments, AACP is job-based
5. **Social layer** — AAE has community, reputation visibility, leaderboards

## Roadmap Alignment

| AACP Phase | Timeline | AAE Alignment |
|------------|----------|---------------|
| Foundation (staking + reputation) | Q2 2026 | AAE agent identity + loadouts |
| Verification (zkVM + TEE) | Q3 2026 | AAE agent verification |
| Disputes (arbitrator pool) | Q4 2026 | AAE agent conflict resolution |
| Mainnet (Base + BSC) | Q1 2027 | AAE cross-chain deployment |

## Recommendation

**Build with AACP as the commerce layer, not against it.**

AAE provides the game mechanics, social layer, and multi-chain execution. AACP provides the trustless commerce infrastructure. Together they're stronger than either alone.

**Immediate actions:**
1. Study ERC-8004 and ERC-8183 contracts (already exploring ERC-8004)
2. Watch AACP testnet launch (Q2 2026 — now)
3. Consider contributing to AACP (they need smart contract review + zkVM examples)
4. Design AAE loadouts to be AACP-compatible from day one
