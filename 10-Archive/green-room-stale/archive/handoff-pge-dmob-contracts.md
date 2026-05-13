---
date: 2026-04-25
from: YoYo (Strategies)
to: DMOB (Smart Contracts)
topic: Personal Goal Engine — Solidity Structs + Functions
priority: P2
---

# Handoff: PGE Smart Contract Spec

**Context:** Jordan approved the Personal Goal Engine. I drafted the full spec at `03-Strategies/Personal-Goal-Engine-Spec.md`. Section 7 has the contract requirements. This handoff extracts what you need.

## New Structs Required

### `GoalProfile`
```solidity
struct GoalProfile {
    uint8 startingCapitalTier;    // 0=zero, 4=significant
    uint256 monthlyCommitment;    // USDC wei
    uint8 riskTolerance;          // 0=conservative, 2=aggressive
    uint8 timeHorizon;            // 0=short, 2=long
    uint8 experienceLevel;        // 0=newcomer, 3=experienced
    uint256 incomeGoal;           // daily target in USDC wei, 0=unset
    uint8 primaryMotivation;      // 0=learn, 3=build
    uint256 goalReadinessScore;   // 0-400 (scaled)
}
```

### `PersonalLadder`
```solidity
struct PersonalLadder {
    uint256[4] dailyTargets;      // 4-tier personalized targets (USDC wei)
    string[4] tierLabels;
    uint256 createdAt;
    bool isCustom;
}
```

### `MilestoneProgress`
```solidity
struct MilestoneProgress {
    uint256 currentTier;          // 1-indexed
    uint256 progressToNextPct;    // 0-100
    uint256 daysInRange;
    uint256 totalFeesEarned;
    uint256 lastTierUpAt;
    uint256 reflectionCount;
    uint256 moduleCompletions;
}
```

### `Reflection`
```solidity
struct Reflection {
    uint256 timestamp;
    string promptId;
    string responseHash;          // IPFS hash
    uint256 associatedEventId;
}
```

## Functions Needed

| Function | Visibility | Purpose |
|----------|------------|---------|
| `createProfile(GoalProfile)` | external | Onboarding |
| `generateLadder(address user)` | public view | Compute personalized ladder from profile |
| `recordMilestone(address user, uint256 feesEarned)` | external | Update progress, check tier-ups |
| `logReflection(address user, string promptId, string responseHash)` | external | Store reflection |
| `getCelebrationTriggers(address user)` | public view | Return pending celebrations |
| `getLossReframe(address user, uint256 eventId)` | public view | Contextual message for underperformance |

## Open Questions for You

1. **On-chain vs off-chain profile?** GoalProfile has 8 fields — cheap to store, but updates are free. Recommend on-chain for composability, off-chain IPFS for reflection text.
2. **REP integration?** Does PGE mint REP directly, or call a central REP contract? I lean toward central REP contract to avoid duplicate authority.
3. **Existing AgentEscrow reuse?** Can we adapt AgentEscrow's state machine pattern for milestone progression? Would save design time.

## Acceptance Criteria
- [ ] All structs compile
- [ ] `generateLadder` produces correct 4-tier output for all 5 startingCapital tiers
- [ ] `recordMilestone` correctly advances tier when `totalFeesEarned` crosses `dailyTargets[currentTier]`
- [ ] Gas estimate < 200k for `createProfile` + `generateLadder` combined

**Priority:** P2 (behind Solana Frontier/Kite AI, but needed for AAE MVP)

**Spec reference:** `03-Strategies/Personal-Goal-Engine-Spec.md` Section 7
