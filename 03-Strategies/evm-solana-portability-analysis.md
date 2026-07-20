# EVM → Solana Portability Analysis

**Author:** YoYo (Strategies)
**Date:** 2026-04-21
**Status:** Complete — DMOB's Solana port is 90% done already

---

## TL;DR

DMOB already ported the core AgentEscrow contract to Solana. The `agent-escrow-solana` repo has a complete Anchor program with all the essential logic. What's left is integration wiring (x402 handler, tests, deployment), not architecture.

---

## Feature-by-Feature Comparison

| Feature | EVM (arc-hackathon) | Solana (agent-escrow-solana) | Ported? |
|---|---|---|---|
| **Initialize config** | Constructor (owner, validator, USDC) | `initialize()` — PDA config account | ✅ Done |
| **Create escrow** | `createEscrow(seller, amount)` | `create_escrow(amount)` — PDA + vault | ✅ Done |
| **AI validation (direct)** | `validateWork(id)` — onlyValidator | `validate_work()` — ai_validator or admin signs | ✅ Done |
| **AI validation (signed)** | `validateWithSignature(id, timestamp, sig)` — EIP712 | `validate_with_signature(timestamp)` — Ed25519 precompile | ✅ Done |
| **Release funds** | `releaseFunds(id)` — buyer or admin | `release_funds()` — buyer or admin | ✅ Done |
| **Refund buyer** | `refundBuyer(id)` — admin only | `refund_buyer()` — admin only | ✅ Done |
| **Update validator** | `updateValidator(new)` — admin | `update_validator()` — admin | ✅ Done |
| **User escrow list** | `userEscrows(address)[]` — mapping | ❌ Not in Solana version | 🟡 Missing |
| **Deposit/withdraw (contract)** | `depositFunds()` / `withdrawFunds()` | ❌ Not needed (SPL vaults) | ✅ N/A |
| **EIP712 signature replay** | `usedSignatures` mapping | Ed25519 precompile (runtime-enforced) | ✅ Better |
| **x402 handler** | ❌ Not in EVM yet either | ❌ Not built | 🔴 Needed |
| **Timeout auto-refund** | ❌ Not in EVM | ❌ Not in Solana | 🔴 Needed |

---

## What's Already Ported (✅)

### 1. Core State Machine
```
EVM:  Created → Validated → Released/Refunded
Sol:  Created → Validated → Released/Refunded  ← Identical
```

### 2. Escrow Struct
| Field | EVM | Solana | Match? |
|---|---|---|---|
| id | uint256 | u64 | ✅ |
| buyer | address | Pubkey | ✅ |
| seller | address | Pubkey | ✅ |
| amount | uint256 | u64 | ✅ |
| status | enum | enum | ✅ |
| validated | bool | bool | ✅ |
| createdAt | uint256 (block.timestamp) | i64 (Clock) | ✅ |
| validatedAt | uint256 | i64 | ✅ |

### 3. Error Codes
All 9 EVM errors ported 1:1 to Solana `#[error_code]` enum, plus 3 new Solana-specific errors:
- `SignatureReplay` — Ed25519 replay protection
- `InvalidTokenMint` — SPL mint validation
- `Overflow` — Rust checked math

### 4. Signature Validation — IMPROVED
| Aspect | EVM | Solana |
|---|---|---|
| Standard | EIP712 typed data | Ed25519 precompile |
| Replay protection | `usedSignatures` mapping (manual) | Runtime-enforced (precompile rejects) |
| Gas overhead | High (ECDSA recovery) | Zero (runtime does it for free) |
| Who can submit | Anyone with valid sig | Anyone with valid precompile tx |

**Solana is strictly better here.** The Ed25519 precompile approach means the Solana runtime verifies the signature BEFORE our program executes. No manual tracking needed.

---

## What's Missing (🔴)

### 1. x402 Handler Program
**Status:** Neither EVM nor Solana has this yet.

**What it needs to do:**
- Accept x402 payment header (HTTP 402 flow)
- Verify the payment signature
- Create escrow in one atomic transaction
- Emit events for off-chain indexer

**Solana approach:**
```rust
// New instruction: create_escrow_with_x402
// Takes: seller, amount, x402_payment_signature
// Does: Verify x402 sig → Create escrow PDA → Transfer USDC to vault
// All in ONE transaction (Solana atomicity advantage)
```

**EVM approach:** Would need two transactions (approve + createEscrow) or a multicall.

**Winner:** Solana — atomic multi-step in one tx.

### 2. Timeout Auto-Refund
**Status:** Neither version has this.

**Solana approach:** Add `deadline: i64` to Escrow struct. Anyone can call `auto_refund()` after deadline passes. No admin needed.

**Why this matters for the hackathon demo:** Shows the trustless property — funds can't be locked forever.

### 3. Tests
**EVM:** Has test directory (Foundry tests)
**Solana:** No tests visible in the repo

**DMOB needs to write:**
- `anchor test` suite (TypeScript)
- Unit tests for each instruction
- Integration test: full escrow lifecycle

### 4. Deployment
**EVM:** Has `script/` directory (Foundry deploy scripts)
**Solana:** No deploy config visible

**Needs:**
- `Anchor.toml` cluster config (devnet)
- Deploy script
- Program ID registration

---

## What the EVM Has That Solana Doesn't Need

| EVM Feature | Why Solana Doesn't Need It |
|---|---|
| `depositFunds()` / `withdrawFunds()` | SPL token vaults handle this natively |
| `usedSignatures` mapping | Ed25519 precompile = runtime-enforced |
| `EIP712` inheritance | Not applicable (different sig scheme) |
| `ECDSA` library | Ed25519 native to Solana |
| `IERC20` interface | SPL Token program is standard |
| `mapping(address => uint256[]) userEscrows` | Can be derived from on-chain events |

---

## Solana Advantages Over EVM

| Property | Impact |
|---|---|
| **Atomic transactions** | x402 + escrow creation in ONE tx (EVM needs 2+) |
| **Parallel execution** | 1000 agents creating escrows simultaneously |
| **No reentrancy** | Eliminates entire class of bugs |
| **Ed25519 precompile** | Signature validation is free + runtime-enforced |
| **400ms finality** | Agents don't wait 12s for confirmation |
| **$0.00025 tx cost** | Micro-escrows (0.01 USDC) are viable |

---

## Recommended Build Sequence

### Phase 1: Finish Core (Apr 21-25)
1. ✅ Clone `agent-escrow-solana` — verify `anchor build` passes
2. 🔴 Write tests (follow anchor-escrow-2026 pattern)
3. 🔴 Deploy to devnet
4. 🔴 Add timeout auto-refund

### Phase 2: x402 Integration (Apr 25-May 4)
5. 🔴 Build `create_escrow_with_x402` instruction
6. 🔴 Wire PayAI facilitator
7. 🔴 End-to-end test: x402 payment → escrow creation → validation → release

### Phase 3: Hackathon Polish (May 5-11)
8. 🔴 Demo script (3 x402 payments in one workflow)
9. 🔴 Deploy to Colosseum devnet
10. 🔴 Submit to Colosseum + Superteam sidetracks

---

## The "One Build, Multiple Pitches" Proof

The port is so clean that the pitch writes itself:

| Hackathon | Chain | Adapter | Status |
|---|---|---|---|
| ARC (Apr 25) | Avalanche/EVM | AgentEscrow.sol | 1 contract, needs tests |
| Colosseum (May 11) | Solana | agent-escrow-solana | Full Anchor program |
| ETHGlobal (May 3) | Ethereum | ethglobal-open-agents | 3 contracts, 44 tests ✅ |

**Same logic. Same state machine. Same errors. Different chains.**

That's the modular architecture thesis proven.

---

## Tags
#portability #EVM-to-Solana #architecture #hackathon #strategy
