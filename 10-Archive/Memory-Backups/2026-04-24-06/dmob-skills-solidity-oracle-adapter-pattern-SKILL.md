---
name: solidity-oracle-adapter-pattern
description: Pluggable oracle adapter pattern for Solidity dispute resolution — interface-based oracles with auto-resolve callbacks. Used for GenLayer, Chainlink Functions, or custom AI adjudication integration.
category: smart-contract
tags: [solidity, oracle, dispute-resolution, genlayer, chainlink, pattern]
---

# Oracle Adapter Pattern for Dispute Resolution

Reusable architecture for plugging external oracles (AI, Chainlink, custom) into onchain dispute resolution.

## Architecture

```
DisputeResolver (core arbitration)
    ↓ requestOracleAdjudication()
GenLayerOracle / ChainlinkOracle (adapter)
    ↓ emits event → offchain relayer picks up
    ↓ relayer calls submitVerdict()
    ↓ oracle auto-calls resolver.resolveDisputeFromOracle()
DisputeResolver → executeDispute() → funds distributed
```

## Key Contracts

### 1. IAdjudicationOracle (interface)
- `requestAdjudication()` — accepts dispute data + evidence
- `isFulfilled()` / `getVerdict()` — check resolution state
- `disputeResolver()` — returns the resolver address for callbacks

### 2. DisputeResolver (core)
- `requestOracleAdjudication(disputeId)` — either party opts in, pulls evidence, forwards to oracle
- `resolveDisputeFromOracle(disputeId, verdict, reasoning)` — oracle callback, maps verdict enum
- `setOracleAdapter(address)` — admin to swap oracle implementations
- Human arbiter path still works when oracle not requested

### 3. GenLayerOracle (adapter)
- `submitVerdict()` — stores verdict AND auto-resolves in DisputeResolver
- Access control: authorized submitters only (relayer addresses)
- `disputeToRequest` mapping for quick lookup

## Critical Design Decision

**The oracle contract must be the caller of `resolveDisputeFromOracle()`**, not the relayer directly.

Why: `DisputeResolver.resolveDisputeFromOracle()` checks `msg.sender == address(oracleAdapter) || msg.sender == owner()`. If the relayer calls it directly, it reverts with `NotAuthorized()`.

Solution: `submitVerdict()` on the oracle does both operations:
1. Store verdict in oracle state
2. Call `DisputeResolver.resolveDisputeFromOracle()` with `address(this)` as msg.sender

This was discovered through test failures (3 tests failing with `NotAuthorized()` when relayer tried to call resolver directly).

## Enum Mapping

Oracle verdicts and internal resolution enums must map cleanly:

```solidity
// IAdjudicationOracle.Verdict enum:
//   BuyerWins (0), SellerWins (1), Split (2)

// DisputeResolver.Resolution enum:
//   Pending (0), BuyerWins (1), SellerWins (2), Split (3)
```

Map in `resolveDisputeFromOracle()` before storing.

## Test Coverage Checklist

- [x] Request oracle adjudication (buyer, seller)
- [x] Request with evidence forwarded
- [x] Cannot request twice
- [x] Cannot request without adapter set
- [x] Submit verdict + auto-resolve
- [x] Cannot submit verdict twice
- [x] Only authorized submitter can submit
- [x] Only resolver contract can request from oracle
- [x] Human arbiter still works alongside oracle
- [x] Owner fallback for oracle submission

## Upgrade Path

MVP: trusted relayer submits GenLayer verdicts onchain
Production: replace `submitVerdict()` with GenLayer gateway callback + Optimistic Democracy validator consensus + slashing

## Pitfalls

1. **Don't let relayer call resolver directly** — must flow through oracle contract
2. **Circular imports** — GenLayerOracle imports DisputeResolver, DisputeResolver imports IAdjudicationOracle only (no direct oracle import)
3. **Reentrancy** — `submitVerdict()` calls external resolver; use `nonReentrant` on both sides
4. **Evidence window** — oracle request should work even after evidence window closes (evidence already collected)
