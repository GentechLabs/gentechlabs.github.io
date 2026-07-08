# Kite AI — Code4rena Bug Bounty Audit Report

**Auditor:** Gentech (GenTech Labs)
**Date:** May 12, 2026
**Bounty:** $10,000 USDC (Critical) / $2,000 USDC (High)
**Scope:** Smart Contracts + .gokite.ai websites

---

## Executive Summary

Deep audit of Kite AI's in-scope smart contracts for the Code4rena bug bounty program. Reviewed StakingManager, StakingVault, StakingVaultOperations, RewardVault, FixedAPRRewardCalculator, Algebra DEX (Factory, SwapRouter, NonfungiblePositionManager), and Lucid Bridge AssetController. Identified **5 Medium**, **4 Low-Medium**, and multiple Low/Informational findings across the contracts.

---

## Findings Summary

| # | Severity | Contract | Title |
|---|----------|----------|-------|
| 1 | **Medium** | USDCController | Multi-bridge `receiveMessage` amount inconsistency enables over-minting |
| 2 | **Medium** | StakingVaultOperations | Harvest functions trust SM return values without verifying ETH inflows |
| 3 | **Medium** | StakingVaultOperations | Silent accounting mismatch floors `activeStake` to zero, enabling allocation bypass |
| 4 | **Medium** | StakingManager | Missing `nonReentrant` on `forceInitiateValidatorRemoval` / `forceInitiateDelegatorRemoval` |
| 5 | **Medium** | StakingManager | Missing `nonReentrant` on `completeDelegatorRegistration` |
| 6 | **Low-Medium** | StakingManager | Delegator reward claim doesn't cap `currentTime` for `Invalidated` validators |
| 7 | **Low-Medium** | StakingVaultOperations | `forceClaimOperatorFees` irreversibly forfeits operator fees on recipient revert |
| 8 | **Low-Medium** | StakingVaultOperations | `removeOperator` deletes pending amounts while in-flight removals still tracked |
| 9 | **Low-Medium** | USDCController | Single-bridge `receiveMessage` lacks adapter whitelist check |
| 10 | **Low** | StakingManager | `_calculateAndSetDelegationReward` uses `=` instead of `+=` for redeemable rewards |
| 11 | **Low** | StakingVaultOperations | `_getStakingValidatorInfo` silently returns zeroed struct, skipping fees |
| 12 | **Low** | StakingVaultOperations | `completeValidatorRegistration` permissionless, emits misleading events |
| 13 | **Low** | StakingVaultOperations | Phantom contribution in delegation removal adoption inflates exit debt paydown |
| 14 | **Low** | USDCController | `_checkUniqueness` arithmetic underflow on empty array |
| 15 | **Low** | USDCController | `resendTransfer` (single-bridge) allows re-relaying already-executed transfers |
| 16 | **Informational** | StakingManager | `ValidatorRewardClaimed` event underreports total reward |
| 17 | **Informational** | StakingVaultOperations | Missing implementations for `recoverStranded*` functions |
| 18 | **Informational** | NonfungiblePositionManager | No reentrancy guard on periphery contracts |
| 19 | **Informational** | AlgebraFactory | No pool removal/delist mechanism |

---

## Detailed Findings

### Finding 1 — MEDIUM: Multi-bridge `receiveMessage` Amount Inconsistency Enables Over-Minting

**Contract:** USDCController.sol (lines 447–464)
**Severity:** Medium (could escalate to Critical depending on adapter trust model)

**Description:**
In the multi-bridge path of `receiveMessage`, only the **first** adapter to relay a given `transferId` sets the `amount` in `ReceivedTransfer`. All subsequent adapters only increment `receivedSoFar` — the `transfer.amount` from their messages is completely ignored. Critically, `transferId` does not encode the amount (`keccak256(abi.encode(destChainId, block.chainid, nonce))`), so there is no on-chain way to verify that the amount matches the original.

**Exploit Scenario:**
1. User initiates a multi-bridge transfer for 100 USDC to chain B with threshold=3, relayed via adapters A, B, C
2. Attacker compromises (or operates) adapter A on chain B
3. Adapter A front-runs on chain B's mempool, calling `receiveMessage` with the same `transferId` but a fabricated `Transfer` struct containing `amount = 1,000,000`
4. The first-relay branch stores `amount: 1,000,000` in `receivedTransfers`
5. Legitimate adapters B and C relay correctly (amount=100), but the code only increments `receivedSoFar` — the correct amount is never validated
6. `receivedSoFar (3) >= threshold (3)` → `execute()` mints **1,000,000 USDC** instead of 100

**Impact:** Unlimited token minting with only one compromised whitelisted adapter. The multi-bridge consensus mechanism is fundamentally broken for amount validation.

**Recommendation:** When `receivedSoFar > 0`, validate `transfer.amount == receivedTransfer.amount`. Alternatively, include the amount in the `transferId` hash.

**Note:** This is related to but distinct from the known #5/#6 (consensus bypass). The known issues focus on the first-adapter-wins parameter injection; this finding specifically addresses the amount validation gap.

---

### Finding 2 — MEDIUM: Harvest Functions Trust SM Return Values Without Verifying ETH Inflows

**Contract:** StakingVaultOperations.sol (lines 1139–1160, 1205–1247)
**Severity:** Medium

**Description:**
The harvest functions (`_harvestOperatorValidators`, `_harvestOperatorDelegators`) credit `vaultAccountedBalance` based on the return value decoded from the staking manager's `claimValidatorRewards` / `claimDelegatorRewards` calls, without measuring actual ETH balance changes.

In contrast, ALL removal/completion functions correctly use the balance-difference pattern:
```solidity
// Removal functions (CORRECT):
uint256 balBefore = address(this).balance;
// ... staking manager call ...
uint256 actualInflow = address(this).balance - balBefore;
$.vaultAccountedBalance += actualInflow;
```

vs.
```solidity
// Harvest functions (TRUST return value):
uint256 reward = _callU256(mgr, abi.encodeWithSelector(SEL_CLAIM_VALIDATOR_REWARDS, ...));
$.vaultAccountedBalance += totalRewards; // trust decoded return, not actual ETH
```

**Exploit Scenario:**
If the staking manager returns a reward value higher than the actual ETH transferred (due to a bug, upgrade regression, or compromise), `vaultAccountedBalance` becomes inflated above `address(this).balance`. This causes:
1. Exchange rate inflation — new depositors receive fewer shares per ETH
2. Withdrawal claim failures — `_sendWithdrawalOrEscrow` can't transfer the full amount
3. The inflated accounting persists indefinitely since no correction mechanism exists

**Recommendation:** Add balance-difference measurement to harvest functions, matching the pattern used in removal functions.

---

### Finding 3 — MEDIUM: Silent Accounting Mismatch Floors `activeStake` to Zero, Enabling Allocation Bypass

**Contract:** StakingVaultOperations.sol (lines 719–794)
**Severity:** Medium

**Description:**
`_syncDelegatorState` and `_syncValidatorState` use a pattern that floors at zero instead of reverting on accounting mismatch:
```solidity
if ($.operators[operatorAddr].activeStake >= amount) {
    $.operators[operatorAddr].activeStake -= amount;
} else {
    emit StakingVault__AccountingMismatchDetected(...);
    $.operators[operatorAddr].activeStake = 0;
}
```

If `activeStake` is already lower than the removal amount, the mismatch is silently absorbed. With an understated `activeStake`, the operator can register **more** validators/delegations than their allocation should allow via `_checkBufferAndAllocation`:
```solidity
if (op.activeStake + amount > maxAllocation) { revert; }
```

**Recommendation:** Revert on accounting mismatch instead of silently zeroing.

---

### Finding 4 — MEDIUM: Missing `nonReentrant` on `forceInitiateValidatorRemoval` / `forceInitiateDelegatorRemoval`

**Contract:** StakingManager.sol (lines 656, 1355)
**Severity:** Medium

**Description:**
Both functions are `external` and lack `nonReentrant`, unlike their counterparts:
- `initiateValidatorRemoval` (line 630) → HAS `nonReentrant`
- `initiateDelegatorRemoval` (line 1331) → HAS `nonReentrant`

`forceInitiateDelegatorRemoval` calls `_initiateDelegatorRemoval` which, when the validator is `Completed`, invokes `_completeDelegatorRemoval` → `_withdrawDelegationRewards` → `_reward()` — an abstract function performing an external token transfer. A malicious reward recipient contract could reenter during the transfer.

**Recommendation:** Add `nonReentrant` to both functions for consistency with their non-force counterparts.

---

### Finding 5 — MEDIUM: Missing `nonReentrant` on `completeDelegatorRegistration`

**Contract:** StakingManager.sol (line 1268)
**Severity:** Medium

**Description:**
`completeDelegatorRegistration` is `external` with NO `nonReentrant` modifier. When the validator is `Completed`, it calls `_completeDelegatorRemoval` which performs `_unlock(delegator.owner, stakeAmount)` — an external token transfer. Every other function that can trigger token transfers has `nonReentrant`.

**Recommendation:** Add `nonReentrant` to `completeDelegatorRegistration`.

---

### Finding 6 — LOW-MEDIUM: Delegator Reward Claim Doesn't Cap `currentTime` for `Invalidated` Validators

**Contract:** StakingManager.sol (lines 541–546)
**Severity:** Low-Medium

**Description:**
The `currentTime` cap only handles `PendingRemoved` and `Completed` statuses:
```solidity
if (validator.status == ValidatorStatus.PendingRemoved || validator.status == ValidatorStatus.Completed) {
    currentTime = validator.endTime;
}
```

If a validator is `Invalidated`, the cap is not applied. Delegators calling `claimDelegatorRewards` would calculate rewards using `block.timestamp` as the end time, potentially overclaiming for time the validator was not active.

**Recommendation:** Add `ValidatorStatus.Invalidated` to the cap condition.

---

### Finding 7 — LOW-MEDIUM: `forceClaimOperatorFees` Irreversibly Forfeits Operator Fees

**Contract:** StakingVaultOperations.sol (lines 667–691)
**Severity:** Low-Medium

**Description:**
State is updated before the external call:
```solidity
$.totalAccruedOperatorFees -= fees;
op.accruedFees = 0;
$.vaultAccountedBalance -= fees;
```
Then the ETH transfer is attempted. On failure, `vaultAccountedBalance` is restored but `op.accruedFees` and `$.totalAccruedOperatorFees` are NOT restored. The operator permanently loses their accrued fees, absorbed by the vault pool.

**Recommendation:** Restore `op.accruedFees` and `$.totalAccruedOperatorFees` on transfer failure, or implement an escrow pattern like `_sendProtocolFee`.

---

### Finding 8 — LOW-MEDIUM: `removeOperator` Deletes Pending Amounts While In-Flight Removals Still Tracked

**Contract:** StakingVaultOperations.sol (lines 583–613, 1377–1428)
**Severity:** Low-Medium

**Description:**
`removeOperator` deletes `operatorPriorEpochPendingAmount` and `operatorCurrentEpochPendingAmount`. When these removals complete, `_decrementInFlight` receives `initiatedEpoch` and tries to decrement from the deleted buckets. If the operator is re-added later, old in-flight removals may incorrectly decrement from the new operator's fresh buckets.

**Recommendation:** Defer pending amount deletion until all in-flight removals complete.

---

### Finding 9 — LOW-MEDIUM: Single-bridge `receiveMessage` Lacks Adapter Whitelist Check

**Contract:** USDCController.sol (lines 414–438)
**Severity:** Low-Medium

**Description:**
For single-bridge transfers (threshold=1), `receiveMessage` does not validate that `msg.sender` is a whitelisted adapter. The multi-bridge path correctly requires `multiBridgeAdapters[msg.sender]`, but the single-bridge path has no equivalent check. The minting limit check provides practical mitigation (default limit = 0 for unconfigured addresses).

**Recommendation:** Add adapter whitelist validation to the single-bridge path for defense-in-depth.

---

### Finding 10 — LOW: `_calculateAndSetDelegationReward` Uses `=` Instead of `+=`

**Contract:** StakingManager.sol (line 1519)
**Severity:** Low

**Description:**
```solidity
$._redeemableDelegatorRewards[delegationID] = reward;  // assignment, not +=
```
If called twice for the same delegationID, the second call overwrites the first. Currently safe due to status guards, but fragile and inconsistent with `_redeemableValidatorRewards` which uses `+=`.

**Recommendation:** Change to `+=` for consistency and safety.

---

### Finding 11 — LOW: `_getStakingValidatorInfo` Silently Returns Zeroed Struct

**Contract:** StakingVaultOperations.sol (lines 1434–1451)
**Severity:** Low

**Description:**
When the staticcall to the staking manager fails, the function returns a zeroed struct (delegationFeeBips = 0), causing the external validator fee path to be skipped entirely. Over time with repeated failures, the protocol loses fee revenue.

**Recommendation:** Revert the harvest/removal if the staking manager call fails for external validators.

---

### Finding 12 — LOW: `completeValidatorRegistration` Permissionless, Emits Misleading Events

**Contract:** StakingVaultOperations.sol (lines 125–131)
**Severity:** Low

**Description:**
No access control. Anyone can call it with any `messageIndex`. The emitted `StakingVault__ValidatorRegistrationCompleted` event may reference a validationID belonging to a different vault, confusing off-chain indexers.

**Recommendation:** Validate the returned validationID is tracked by this vault.

---

### Finding 13 — LOW: Phantom Contribution in Delegation Removal Adoption

**Contract:** StakingVaultOperations.sol (lines 969–1062)
**Severity:** Low

**Description:**
For `status == 3` (PendingRemoved) adoptions, `contribution += principal` is counted before state verification. If the delegation's principal in the vault doesn't match the SM's actual amount (e.g., due to slashing), the contribution is over-counted, reducing the operator's exit debt unfairly.

---

### Finding 14 — LOW: `_checkUniqueness` Arithmetic Underflow on Empty Array

**Contract:** USDCController.sol (lines 716–724)
**Severity:** Low

**Description:**
`length - 1` where `length` is `uint256`. If called with an empty adapters array, this reverts with arithmetic underflow instead of a clean error.

---

### Finding 15 — LOW: `resendTransfer` (Single-bridge) Allows Re-relaying Already-Executed Transfers

**Contract:** USDCController.sol (lines 295–310)
**Severity:** Low

**Description:**
`resendTransfer` for single-bridge transfers does not check whether the transfer has already been executed. The destination will reject the duplicate, but the user pays bridge fees for a guaranteed-to-fail relay.

---

### Finding 16 — INFORMATIONAL: `ValidatorRewardClaimed` Event Underreports Total Reward

**Contract:** StakingManager.sol (lines 438–442)
**Severity:** Informational

**Description:**
The event emits only `stakingReward`, not `stakingReward + delegationFees`. Off-chain indexers would undercount the total validator reward.

---

### Finding 17 — INFORMATIONAL: Missing Implementations for `recoverStranded*` Functions

**Contract:** StakingVault.sol (lines 202–213)
**Severity:** Informational

**Description:**
These functions are declared in the interface and have forwarding stubs but no implementation in StakingVaultOperations.sol. Calling them would revert.

---

## Out of Scope (Known Issues)

The following were already reported and are excluded from this audit:
- #18: StakingManager ERC-7201 storage slot mismatch
- #4: stKITE shares transferable despite non-transferable design
- #7/#11: Double-fee on external delegation harvests
- #8: processEpoch FIFO queue blocks withdrawals
- #9: Withdrawal queue griefing via dust requests
- #10: Forced ETH injection inflates vault accounting
- #5/#6: Multi-bridge consensus bypass in receiveMessage
- #12: pauseTransfersToChain emergency stop incomplete
- #17: GokiteAccountFactory.addStake missing access control
- #3: Unsigned serviceProvider bypasses session spending rules
- #16: Stale LP NFT permit replay
- #13/#14/#15: Web API access control issues

---

## Recommendations

1. **Immediate:** Address the multi-bridge amount validation gap (Finding 1) — this is the highest-impact issue
2. **High Priority:** Add balance-difference verification to harvest functions (Finding 2)
3. **High Priority:** Revert on accounting mismatch instead of silent zeroing (Finding 3)
4. **Medium Priority:** Add `nonReentrant` to all force/complete functions (Findings 4, 5)
5. **Medium Priority:** Fix operator fee forfeiture on revert (Finding 7)
6. **Low Priority:** Address all Low/Informational findings

---

*Report generated by Gentech for Code4rena bug bounty submission.*
