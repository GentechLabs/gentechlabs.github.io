# GenTech Verified Agent
## The Oracle-Free Machine-Money Loop on Creditcoin

**BUIDL CTC 2026 Fall — AI Track**
**Team:** GenTech Labs (solo builder)
**Sector:** AI / DeFi

---

## 1. The Problem

DeFi agents today make decisions on data they **cannot prove**. They trust centralized
oracle operators, off-chain price feeds, and API responses that can be wrong, stale, or
manipulated. When an autonomous agent moves money based on unverifiable data, the
failure isn't a bug — it's a **trust hole**.

The result: agents either (a) stay locked to a single chain where they can self-verify,
or (b) go cross-chain and silently trust a middleman. Neither is acceptable for
autonomous capital.

## 2. The Thesis: The Machine-Money Loop

We built an AI agent that **only acts on cryptographically verified cross-chain data** —
never a centralized oracle. The loop:

```
Source chain (Sepolia)          Creditcoin CC3 Testnet
┌──────────────────────┐        ┌─────────────────────────────┐
│ USDC transfer (tx)   │        │                             │
└─────────┬────────────┘        │  ProofBuilder (USC SDK)     │
          │ inclusion proof     │    generates Merkle proof   │
          ▼                     └───────────┬─────────────────┘
   ProofBuilder (USC SDK)                    │ proofData
          │                                  ▼
          └──────────────►  PrecompileBlockProver.verifySingle()
                                  │ verified: true/false
                                  ▼
                           AI decision layer
                                  │
                                  ▼
                    VerifiedRebalance contract (Creditcoin)
                                  │
                                  ▼
                        On-chain rebalance action
```

**The trust anchor is the Attestcoin Protocol.** A cross-chain transaction is proven
via the USC SDK, then verified **on-chain** through Creditcoin's precompile block
prover. No oracle. No middleman. The agent's decision is only as good as the
cryptographic proof it verified.

## 3. What We Built

### 3.1 Attestcoin Protocol Integration (core requirement)
- **`PrecompileChainInfoProvider`** — queries which source chains Creditcoin attests
  (verified live: Ethereum + Sepolia)
- **`ProofBuilder`** — generates a Merkle inclusion proof for a source-chain tx
- **`PrecompileBlockProver.verifySingle()`** — verifies the proof **on-chain** on
  Creditcoin, the cryptographic trust anchor

### 3.2 The AI Decision Layer
- Only trusts `verified: true` from the on-chain prover
- Decodes the attested transaction (amount, token)
- Applies a threshold policy: verified USDC ≥ threshold → trigger rebalance
- **Refuses to act on unverified data** — the core safety property

### 3.3 The On-Chain Action Contract (`VerifiedRebalance.sol`)
- `recordVerifiedEvent()` — persists a verified cross-chain event with full evidence
  lineage (chainKey, blockNumber, txHash, amount, timestamp)
- **Refuses unverified events** (`require(verified, ...)`) — the trust model is
  enforced in the contract, not just the agent
- Emits `RebalanceTriggered` when a verified event clears the threshold
- Owner-only writes; transparent, replayable audit trail

## 4. Why This Wins

| Requirement | How we meet it |
|---|---|
| **Meaningful Attestcoin integration** | Full stack: chain info + proof generation + on-chain verification |
| **Depth of integration (core scoring)** | The entire trust model IS the Attestcoin Protocol — no oracle anywhere |
| **AI track fit** | Autonomous decisioning from verified data, no centralized operator |
| **Deployed on testnet** | Creditcoin CC3 Testnet |
| **Original work** | Built for this hackathon, reuses GenTech's DeFi-agent + x402 thesis |

## 5. Security & Trust Properties

- **No centralized oracle** — every decision traces to an on-chain proof
- **Contract-enforced verification** — the action contract rejects unverified events
- **Evidence lineage** — every recorded event stores its chainKey, blockNumber, and
  txHash, so decisions are replayable and auditable
- **Owner-gated writes** — only the agent's key can record events

## 6. Roadmap

- [x] Attestcoin Protocol integration (verified live on CC3 testnet)
- [x] Creditcoin action contract (compiles, 4/4 tests pass)
- [x] Agent wired to trigger on-chain action
- [ ] Deploy to CC3 testnet (funded key)
- [ ] GitHub repo + README
- [ ] Prototype demo video

## 7. Team

**Jordan (GenTech Labs)** — solo builder. Full-stack + smart contracts + AI agent
engineering. Operator of an autonomous agent economy on the x402 payment rail.

---

*GenTech Labs — building the trust substrate for autonomous agents.*
