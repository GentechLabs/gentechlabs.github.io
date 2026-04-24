# AAE 5-Layer Architecture — Code Readiness Assessment

**Date:** 2026-04-18
**Assessor:** Hermes Agent
**Scope:** Map existing 3 hackathon repos to Jordan's 5-layer AAE vision

---

## AAE Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  Layer 5: Marketplace + Escrow (Kite AI)        │  ← Most code exists here
├─────────────────────────────────────────────────┤
│  Layer 4: Enforcement — SLAs, disputes, slash   │  ← Partially built
├─────────────────────────────────────────────────┤
│  Layer 3: Brain — Evolve / Learn                │  ← Stub only
├─────────────────────────────────────────────────┤
│  Layer 2: Agent Risk Intel                       │  ← Stub only
├─────────────────────────────────────────────────┤
│  Layer 1: Fee LP Auto-Balance (Autopilot)       │  ← Not started
└─────────────────────────────────────────────────┘
```

---

## Layer-by-Layer Assessment

### Layer 1: Fee LP Auto-Balance (Autopilot) — AVAX Retro9000
**Status: ❌ NOT STARTED**
**Code exists:** None
**Expected contract:** `FeeAutopilot.sol` or similar
**What it should do:**
- Auto-rebalance LP positions for fee optimization
- Monitor fee accrual and rebalance thresholds
- Interact with AMM/LP protocols on Avalanche
**Gaps:**
- No LP interaction contracts
- No fee tracking or accrual logic
- No rebalance trigger mechanism
- No integration with DEX routers

**To build:** Need LP position management, fee tracking, rebalance threshold logic, and AMM integration. Estimated 2-3 days.

---

### Layer 2: Agent Risk Intel — ETHGlobal Open Agents
**Status: 🟡 STUB ONLY**
**Code exists:** `AgentRegistry.sol` (partially relevant)
**What it should do:**
- Track agent risk scores based on task history
- Monitor completion rates, dispute rates, response times
- Provide risk ratings for marketplace display
**Current code:**
- `AgentRegistry` tracks agent metadata and skill hashes ✅
- No risk scoring ❌
- No historical performance tracking ❌
- No risk-based filtering ❌
**Gaps:**
- No `AgentRiskProfile` struct or scoring logic
- No event history aggregation
- No slashing/risk degradation on failures
- Skills are stored via 0G Storage root hash but no verification

**To build:** Risk scoring contract that reads from TaskManager completion/dispute history. Estimated 1-2 days.

---

### Layer 3: Brain (Evolve / Learn) — ETHGlobal Open Agents
**Status: 🟡 STUB ONLY**
**Code exists:** `AgentKeeper.sol` (closest match)
**What it should do:**
- Agents register conditions and actions for autonomous execution
- KeeperHub triggers execution based on conditions
- Agents can "learn" by updating strategies based on outcomes
**Current code:**
- `AgentKeeper` has job registration ✅
- `executeJob` is entirely stubbed (TODOs) ❌
- No condition evaluation ❌
- No execution dispatch ❌
- No learning/evolution mechanism ❌
- Zero tests ❌
**Gaps:**
- Condition checking logic (time-based, oracle-based, state-based)
- Execution dispatch (what actions agents can take)
- Outcome tracking for "learning"
- Integration with off-chain AI agents

**To build:** Full condition engine, action dispatcher, outcome feedback loop. Estimated 2-3 days.

---

### Layer 4: Enforcement — SLAs, Disputes, Slashing (Kite AI)
**Status: 🟡 PARTIALLY BUILT**
**Code exists across:**
- `TaskManager.sol` — dispute initiation (incomplete)
- `AgentPaymentFlow.sol` — spending limits (functional)
- `AgentEscrow.sol` — validation/release (functional but buggy)

**What works:**
- `TaskManager.disputeTask()` — can mark tasks as disputed ✅
- `AgentPaymentFlow` — daily spending limits enforced ✅
- `AgentEscrow` — validation and release paths ✅

**What's missing:**
- `disputeTask` has no resolution logic — disputed funds stuck forever ❌
- No SLA definition contract (response times, quality thresholds) ❌
- No slashing mechanism (stake-based penalties) ❌
- No arbitration (who resolves disputes?) ❌
- No timeout auto-release ❌

**Gaps:**
```
Needed: SLARegistry.sol (define SLAs per service type)
Needed: DisputeArbiter.sol (resolve disputes with evidence)
Needed: SlashingVault.sol (stake-based penalties)
Needed: TimeoutEscrow.sol (auto-release after deadline)
```

**To build:** SLA definition, dispute resolution with evidence submission, slashing vault, timeout mechanism. Estimated 2-3 days.

---

### Layer 5: Marketplace + Escrow (Kite AI primary)
**Status: ✅ MOSTLY BUILT**
**Code exists:**
- `AgentEscrow.sol` — USDC escrow with AI validation (arc-hackathon)
- `AgentPaymentFlow.sol` — ETH payments with limits (agent-economy-kite)
- `TaskManager.sol` — Task posting, claiming, completion (ethglobal-open-agents)
- `AgentRegistry.sol` — Agent discovery (ethglobal-open-agents)

**What works:**
- Escrow lifecycle: create → validate → release/refund ✅
- Agent registration with skill hashes ✅
- Task posting with ETH payment ✅
- Daily spending limits ✅
- EIP712 off-chain validation ✅

**What's missing:**
- No unified marketplace contract (agents can't browse services) ❌
- No service discovery/indexing ❌
- No pricing negotiation ❌
- No reputation/rating system ❌
- `claimTask` doesn't verify agent ownership (bug) ⚠️
- `validateWork` check ordering (bug) ⚠️

**To build:** Marketplace aggregator, service registry with search, reputation system. Estimated 1-2 days.

---

## Modularity Assessment

### Current Architecture Problems

**1. Monolithic contracts**
- `AgentEscrow` mixes escrow, validation, and admin functions in one contract
- `TaskManager` bundles task lifecycle + escrow + dispute initiation
- No separation between "what" (escrow) and "how" (validation method)

**2. No interface-driven design**
- `arc-hackathon`: No interfaces at all — direct concrete dependencies
- `agent-economy-kite`: No interfaces
- `ethglobal-open-agents`: Has interfaces ✅ but contracts don't implement them consistently

**3. Incompatible payment models**
- arc-hackathon: USDC ERC20
- agent-economy-kite: Native ETH
- ethglobal-open-agents: Native ETH
- No unified payment abstraction

**4. Chain-specific assumptions**
- arc-hackathon: Hardcoded to Avalanche/Base RPCs in foundry.toml but contracts use constructor params ✅
- agent-economy-kite: No chain config
- ethglobal-open-agents: Generic

### Refactoring Recommendations

#### Phase 1: Extract Interfaces (1 day)
```
src/interfaces/
├── IEscrow.sol          ← Escrow create/release/refund
├── IValidator.sol       ← Validation interface (pluggable)
├── IMarketplace.sol     ← Service discovery
├── IRiskEngine.sol      ← Risk scoring
└── ISLA.sol             ← SLA definitions
```
All existing contracts should implement these interfaces.

#### Phase 2: Separate Escrow from Validation (1 day)
```
src/escrow/
├── EscrowVault.sol      ← Pure escrow hold/release
├── USDCVault.sol        ← ERC20 implementation
└── ETHVault.sol         ← Native ETH implementation

src/validation/
├── AIValidator.sol      ← Current EIP712 validator
├── MultiSigValidator.sol ← N-of-M validation
└── AutoValidator.sol    ← Oracle-based auto-validation
```
EscrowVault accepts a pluggable IValidator — validation method is independent of escrow logic.

#### Phase 3: Build Enforcement Layer (2 days)
```
src/enforcement/
├── SLARegistry.sol
├── DisputeArbiter.sol
├── SlashingVault.sol
└── TimeoutManager.sol
```

#### Phase 4: Risk + Marketplace (2 days)
```
src/risk/
├── RiskEngine.sol
└── ReputationOracle.sol

src/marketplace/
├── ServiceRegistry.sol
├── MarketplaceRouter.sol
└── PricingEngine.sol
```

---

## Readiness Scorecard

| Layer | Code Exists | Tests | Modular | Production Ready |
|-------|-------------|-------|---------|------------------|
| L1: Fee Autopilot | ❌ | ❌ | ❌ | 0% |
| L2: Risk Intel | 🟡 | ❌ | ❌ | 10% |
| L3: Brain | 🟡 | ❌ | ❌ | 5% |
| L4: Enforcement | 🟡 | 🟡 | ❌ | 25% |
| L5: Marketplace | ✅ | ✅ | ❌ | 60% |

**Overall AAE Readiness: ~20%**

---

## Recommended Sprint Plan (7 days to Arc deadline)

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1 | Fix bugs | arc-hackathon check ordering, claimTask ownership |
| 2 | Reentrancy + interfaces | Add guards, extract IEscrow/IValidator |
| 3 | Layer 4 enforcement | DisputeArbiter with timeout + resolution |
| 4 | Layer 5 marketplace | ServiceRegistry with discovery |
| 5 | Layer 2 risk | RiskEngine basic scoring from TaskManager data |
| 6 | Layer 3 brain | Wire AgentKeeper condition checking |
| 7 | Integration + tests | End-to-end test of full stack |

**Layer 1 (Fee Autopilot)** is out of scope for this hackathon cycle — defer to post-hackathon.

---

## Key Architectural Decision Needed

**Should we consolidate into a single unified contract suite or keep 3 separate repos?**

**Recommendation:** Consolidate. The current 3 repos have overlapping but incompatible implementations. For Arc hackathon, pick ONE repo (suggest: `arc-hackathon` as base) and integrate the best patterns from the others:
- Use `AgentEscrow` escrow pattern (USDC + EIP712) ✅
- Borrow `AgentRegistry` discovery pattern ✅
- Borrow `TaskManager` lifecycle (fix bugs first) ✅
- Add enforcement layer from scratch ⬜
- Skip `AgentPaymentFlow` (ETH-only, no escrow, lowest value)
