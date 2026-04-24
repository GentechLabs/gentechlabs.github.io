# Spec: Bin Book Liquidity Module for AgentEscrow

**From:** YoYo (Strategies) → **Dmob (Labs)
**Status:** Draft — awaiting Dmob review
**Date:** 2026-04-19

## Concept
Adapt LFJ's Liquidity Book discrete-bin architecture for AgentEscrow's revenue-tier LP system. Instead of price bins, bins represent **revenue allocation tiers** — users define how their liquidity is distributed across agent revenue streams.

## Core Architecture

### Bin Definition
Each bin maps to an agent tier/revenue stream:
- `binId`: unique identifier (maps to tier: free, starter, pro, enterprise)
- `binStep`: fee multiplier per tier (analogous to LFJ's binStep)
- `liquidity`: user-deposited amount in this bin
- `accumulatedFees`: fees accrued to this bin
- `weight`: dynamic weight based on agent activity/revenue

### User Position
- User deposits into multiple bins with custom ratios (not forced 50/50 or curve-locked)
- Position is represented as a vector: `{binId → amount}` across N bins
- Fees distribute proportionally to bin weights + user's bin allocation

### Key Functions
```
deposit(binId, amount)           // Add to specific bin
withdraw(binId, amount)          // Remove from specific bin
swap(sourceBin, targetBin, amt)  // Rebalance between bins (no withdraw needed)
claimFees(positionId)            // Claim accrued fees per bin
setWeights(binId[], weight[])    // Governance-controlled bin weights
```

### LFJ Fork vs Build From Scratch
- **Fork LFJ V2** (MIT license): proven bin math, ~3K LOC, battle-tested
- **Replace:** price oracle → revenue oracle, swap routing → rebalancing engine
- **Keep:** fee accounting per bin, position tracking, discrete bin structure
- **New:** revenue oracle (on-chain fee tracking per agent tier), dynamic weight calculation

### Revenue Oracle (New Component)
- Tracks per-tier revenue (agent subscription fees, command usage fees)
- Updates bin weights dynamically (e.g., pro tier generating 3x fees = higher weight)
- Can be simple: on-chain fee accumulator + periodic weight recalculation
- Or oracle-based: if pulling data from PaperPilot API

### Risks & Unknowns
- Bin weight manipulation if revenue data is manipulable
- User experience: need UI that visualizes bin allocation clearly (LFJ does this well)
- Gas costs: per-bin operations add up; consider batch functions
- Initial liquidity bootstrapping: first bins need seed liquidity

## Dmob — Your Call
1. Does forking LFJ Liquidity Book make sense here, or is the abstraction gap too wide?
2. What's the minimal viable version? (e.g., 3 fixed bins, manual rebalancing)
3. How does this integrate with existing AgentEscrow Solidity (agent-escrow repo)?

## Sources
- LFJ Liquidity Book docs: docs.lfj.gg
- LFJ contracts (MIT): github.com/traderjoe-xyz/joe-v2
- AgentEscrow existing Solidity: agent-escrow repo
