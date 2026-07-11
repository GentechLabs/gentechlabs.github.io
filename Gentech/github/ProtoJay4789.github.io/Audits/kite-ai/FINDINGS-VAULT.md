# Security Audit: StakingVault & StakingVaultOperations

**Auditor:** Hermes Agent
**Date:** 2026-05-12
**Scope:** `StakingVault.sol` (1240 lines), `StakingVaultOperations.sol` (1541 lines)
**Solidity:** 0.8.25
**Framework:** UUPS Proxy + ERC-7201 Namespaced Storage + Diamond-like Delegatecall Split

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 2 |
| Medium | 4 |
| Low | 4 |
| Informational | 6 |

---

## H-01: `forceClaimOperatorFees` Permanently Forfeits Operator Fees on Recipient Revert

**Severity:** High
**Contract:** StakingVaultOperations
**Lines:** 667-691

### Description

In `forceClaimOperatorFees`, the operator's `accruedFees` is zeroed and `totalAccruedOperatorFees` is decremented **before** the ETH transfer is attempted. If the recipient's `.call{value}` reverts, the ETH is returned to `vaultAccountedBalance` but the operator's fee accounting is already cleared. The operator permanently loses all accrued fees.

```solidity
// L678-690
$.totalAccruedOperatorFees -= fees;
op.accruedFees = 0;                    // ← Cleared BEFORE transfer
$.vaultAccountedBalance -= fees;

address recipient = op.feeRecipient != address(0) ? op.feeRecipient : operator;
(bool success,) = payable(recipient).call{value: fees}("");
if (success) {
    emit OperatorFeesClaimed(operator, fees);
} else {
    // Fees forfeit to pool — operator set a reverting recipient
    $.vaultAccountedBalance += fees;     // ← ETH returned to vault
    emit OperatorFeesForfeited(operator, fees);
    // BUT op.accruedFees is still 0 — operator lost fees
}
```

### Exploit Scenario

1. Operator accrues 100 ETH in fees over time.
2. Operator temporarily deploys a fee recipient contract that has a bug or is temporarily full.
3. `OPERATOR_MANAGER_ROLE` holder calls `forceClaimOperatorFees(operator)`.
4. The low-level `.call` to the recipient fails.
5. Operator permanently loses 100 ETH in accrued fees. Fees are added to `vaultAccountedBalance` (distributed to all depositors).
6. Operator has no recourse — `accruedFees` is already 0.

Note: The self-call `claimOperatorFees()` does NOT have this issue — it uses `sendValue` which reverts the entire transaction on failure, preserving state.

### Recommendation

Restore `op.accruedFees` and `$.totalAccruedOperatorFees` on transfer failure, similar to the escrow pattern used elsewhere. Alternatively, revert the entire transaction on failure (like `claimOperatorFees` does):

```solidity
if (!success) {
    $.totalAccruedOperatorFees += fees;
    op.accruedFees = fees;
    $.vaultAccountedBalance += fees;
    revert StakingVault__OperatorFeeClaimFailed(operator, fees);
}
```

---

## H-02: `vaultAccountedBalance` Has No Reconciliation with Actual ETH Balance

**Severity:** High
**Contract:** StakingVault
**Lines:** Multiple (deposit L365, requestWithdrawal L389, claimWithdrawal L1037, etc.)

### Description

`vaultAccountedBalance` is tracked as a separate accounting variable and is never reconciled against `address(this).balance`. This variable determines how much ETH the vault "thinks" it holds. If it drifts from the actual balance — due to accounting edge cases, forced ETH via `selfdestruct` (still functional on Avalanche C-Chain), or any other mechanism — the consequences are:

- **If `vaultAccountedBalance > actual balance`:** Withdrawals and claim operations will revert with arithmetic underflow on `$.vaultAccountedBalance -= amount`, permanently locking funds.
- **If `vaultAccountedBalance < actual balance`:** Excess ETH is permanently locked in the contract with no recovery mechanism.

The vault tracks `actualInflow = address(this).balance - balBefore` in several places (completeValidatorRemoval L168, completeDelegatorRegistration L308, etc.) but only accounts for the *net* flow. There is no periodic or trigger-based reconciliation function.

### Exploit Scenario

1. Any external contract (or protocol upgrade) sends ETH to the vault outside the expected flow (e.g., via `selfdestruct`, governance migration, or mistaken transfer).
2. `vaultAccountedBalance` does not increase.
3. The excess ETH is permanently locked.
4. Over time, as validators return rewards and stake is withdrawn, `vaultAccountedBalance` approaches the true balance minus the phantom ETH.
5. Eventually, a large withdrawal attempt causes `vaultAccountedBalance` underflow, locking all remaining withdrawals.

### Recommendation

Add a reconciliation function callable by the admin that adjusts `vaultAccountedBalance` to match `address(this).balance - totalEscrowedWithdrawals - totalPendingFees`. Consider adding an invariant check:

```solidity
function reconcileBalance() external onlyRole(VAULT_ADMIN_ROLE) {
    uint256 actual = address(this).balance;
    uint256 accounted = $.vaultAccountedBalance;
    if (actual > accounted) {
        uint256 surplus = actual - accounted;
        $.vaultAccountedBalance = actual;
        // attribute surplus to pool or protocol
    }
}
```

---

## M-01: Permissionless `completeValidatorRegistration` / `completeDelegatorRegistration` Can Be Griefed

**Severity:** Medium
**Contract:** StakingVaultOperations
**Lines:** 125-131, 293-323

### Description

Both `completeValidatorRegistration` and `completeDelegatorRegistration` have no access control — anyone can call them with a `messageIndex` to complete a pending registration. While this is by design for permissionless L1/L2 completion, it introduces risks:

1. **Timing manipulation:** A third party can complete registration at an unfavorable moment (e.g., when the vault is over-allocated, before a pending withdrawal is processed, or during a fee change).
2. **`completeDelegatorRegistration` abort path (L310-317):** If the delegator registration was aborted by the StakingManager (`smOk && status == 0 && smAmount == 0`), the function returns early after syncing state. A third party can trigger this abort completion, which is irreversible.

### Exploit Scenario

1. An operator initiates validator registration during a period of high network congestion.
2. A third party monitors the mempool for `completeValidatorRegistration` messages.
3. The third party front-runs the operator's completion, completing the registration at a moment when the vault's liquidity buffer is tight.
4. The operator's validator is now active with an unexpected timing relative to withdrawal processing.

### Recommendation

Consider allowing only the operator (or a designated completer) to complete registrations, or add a time-lock window after which permissionless completion is allowed. At minimum, document this as an intentional design decision.

---

## M-02: `requestWithdrawal` Fee Can Grief Small Withdrawals

**Severity:** Medium
**Contract:** StakingVault
**Lines:** 385-396

### Description

The `withdrawalRequestFee` is deducted from `stakeAmount` before the withdrawal is enqueued. If `stakeAmount <= fee`, the transaction reverts (L387). This means there exists a minimum withdrawal amount below which users cannot withdraw. If the admin sets a high fee, it can effectively lock small-balance users out of the vault.

```solidity
uint256 fee = $.withdrawalRequestFee;
if (fee > 0) {
    if (stakeAmount <= fee) revert StakingVault__InvalidAmount();
    stakeAmount -= fee;
    ...
}
```

### Exploit Scenario

1. Admin sets `withdrawalRequestFee` to a significant amount (e.g., 0.1 ETH).
2. A user with 0.05 ETH in shares cannot call `requestWithdrawal` — the transaction always reverts.
3. The user's funds are effectively locked until they accumulate enough shares, or the fee is reduced.

### Recommendation

Add a minimum withdrawal threshold as a protocol parameter, and/or document that the fee is expected to remain below the minimum deposit amount. Consider implementing a graduated fee structure based on withdrawal size.

---

## M-03: `forceClaimOperatorFees` Uses Low-Level Call Bypassing CEI, Asymmetric with `claimOperatorFees`

**Severity:** Medium
**Contract:** StakingVaultOperations
**Lines:** 667-691 vs 649-664

### Description

There is an asymmetric behavior between `claimOperatorFees` and `forceClaimOperatorFees`:

| Aspect | `claimOperatorFees` | `forceClaimOperatorFees` |
|--------|---------------------|--------------------------|
| Transfer method | `sendValue` (reverts on failure) | Low-level `.call` (continues on failure) |
| State on failure | Fully reverted (safe) | `accruedFees=0` but ETH returned to vault (funds lost) |
| Access control | Any operator | `OPERATOR_MANAGER_ROLE` |

This means `forceClaimOperatorFees` (called by a trusted role) has WORSE failure semantics than the self-service function. An operatorManager who calls this during a temporary recipient issue causes permanent loss.

### Recommendation

Align the failure semantics. Either:
1. Revert `forceClaimOperatorFees` on transfer failure (matching `claimOperatorFees`), or
2. Restore the operator's accounting on failure (as recommended in H-01).

---

## M-04: `processEpoch` Can Stall If Previous Epoch Not Fully Processed

**Severity:** Medium
**Contract:** StakingVault
**Lines:** 488-560

### Description

`processEpoch` checks `currentEpoch <= $.lastEpochProcessed` and reverts if true (L493-495). If a previous epoch's processing hit the `scanCapHit` (L509), `lastEpochProcessed` is NOT updated (L552-554). This means the next call to `processEpoch` must wait for a new epoch to begin, even though partial progress was made via `queueProcessHead`.

During this gap:
- Withdrawal requests from previous epochs remain unfulfilled (marked `withdrawalClaimable[i] = true` but not fully processed).
- `queueProcessHead` has advanced but `lastEpochProcessed` hasn't, so the next `processEpoch` call starts fresh from the new epoch.
- Users must wait an additional epoch duration before their withdrawals can be processed.

### Exploit Scenario

1. A large number of users request withdrawals, creating a long queue.
2. `processEpoch` is called but hits the gas/scan cap — `scanCapHit = true`.
3. The epoch ends and a new epoch starts.
4. The next `processEpoch` call processes requests from the NEW epoch, potentially skipping older unprocessed requests because `startIdx` starts from `queueProcessHead` which has already advanced past some items.

Wait — actually `startIdx = $.queueProcessHead > $.queueHead ? $.queueProcessHead : $.queueHead` (L503), and the loop breaks when `request.requestEpoch >= currentEpoch` (L516). So old requests are skipped in the new epoch. They remain unfulfilled until another call processes them in yet another epoch.

### Recommendation

Allow `processEpoch` to process requests from any epoch ≤ current epoch regardless of `lastEpochProcessed`. Alternatively, add a function that specifically targets unprocessed requests from previous epochs.

---

## L-01: `_sendWithdrawalOrEscrow` Can Permanently Lock ETH for Non-Reverting Contracts

**Severity:** Low
**Contract:** StakingVault
**Lines:** 1031-1048

### Description

When a user's withdrawal claim fails (e.g., the user is a contract that reverts on ETH receipt), the ETH is escrowed under `withdrawalEscrow[user]`. The user can later call `claimEscrowedWithdrawal(recipient)` to recover. However, if the user is a contract that has no function to call `claimEscrowedWithdrawal`, and `receive()` always reverts, the ETH is permanently locked.

### Recommendation

Add a `rescueEscrowedWithdrawal` admin function that can sweep long-dormant escrowed funds back to the vault after a timelock.

---

## L-02: `_checkDebtFreeze` Threshold Floor of 1 May Allow Excessive Stake for Small Operators

**Severity:** Low
**Contract:** StakingVaultOperations
**Lines:** 1291-1311

### Description

```solidity
uint256 threshold = (op.allocationBips * getTotalPooledStake() * DEBT_FREEZE_THRESHOLD_BIPS) 
    / (BIPS_DENOMINATOR * BIPS_DENOMINATOR);
if (threshold == 0 && op.allocationBips > 0) threshold = 1;
```

When an operator has very small `allocationBips` or the pool is small, the threshold calculation truncates to 0, and the floor of 1 is applied. This means an operator with tiny allocation can accumulate unlimited exit debt (since the debt only needs to exceed 1 wei to trigger the freeze). In practice, this means the debt freeze is ineffective for small operators.

### Recommendation

Consider setting a minimum absolute threshold rather than a floor of 1 wei, or document that small operators are expected to be managed via other mechanisms.

---

## L-03: Operator Can Set feeRecipient to a Contract That Reverts, Locking Fees in `claimOperatorFees`

**Severity:** Low
**Contract:** StakingVaultOperations
**Lines:** 694-706, 649-664

### Description

An operator can call `setOperatorFeeRecipient(address)` to set any address as their fee recipient. If they set it to a contract that always reverts on ETH receipt, then `claimOperatorFees` (which uses `sendValue` and reverts on failure) will always fail. The operator's fees are locked until they call `setOperatorFeeRecipient` again with a valid address.

However, if `OPERATOR_MANAGER_ROLE` then calls `forceClaimOperatorFees`, the fees are forfeited per H-01.

### Recommendation

Document that operators are responsible for ensuring their fee recipient can receive ETH. Consider adding validation in `setOperatorFeeRecipient` (e.g., a low-level call with 0 value to verify the recipient can receive).

---

## L-04: `withdrawalQueue` Grows Unboundedly

**Severity:** Low
**Contract:** StakingVault
**Lines:** 402-412, 1097-1114

### Description

The withdrawal queue is a dynamic array that only grows (via `push`) and is cleaned via `_advanceQueueHead` which deletes leading fulfilled entries. The `MAX_ADVANCE_PER_CALL` constant limits how many entries can be deleted per call. If the advance rate doesn't keep up with the push rate, the queue grows unboundedly, increasing storage costs and gas for iterations.

### Recommendation

Monitor queue length and ensure `_advanceQueueHead` and `processEpoch` are called frequently enough. Consider adding a `pruneQueue` function that can be called by the admin.

---

## I-01: `_delegateToOperations` Forwards All Calldata Including ETH Value

**Severity:** Informational
**Contract:** StakingVault
**Lines:** 1013-1023

### Description

The `_delegateToOperations` function copies the entire calldata and forwards via `delegatecall`. If any operations function is called with `msg.value > 0` when it shouldn't be, the delegatecall will execute in the vault's context with that value available. The stub functions in `StakingVault.sol` use `external` visibility without `payable`, so Solidity will reject ETH for those specific functions. However, the `fallback()` (L163) IS `payable` and forwards to operations — meaning any unknown function selector can receive ETH.

### Recommendation

Ensure that the operations implementation reverts on unexpected ETH values. Consider adding a `nonpayable` check in the fallback for non-payable operations functions.

---

## I-02: `forceRemoveValidator` Does Not Check Operator Has No Pending Delegator Removals

**Severity:** Informational
**Contract:** StakingVaultOperations
**Lines:** 190-213

### Description

`forceRemoveValidator` only checks `validatorPendingRemoval[validationID]` (L200). It does not check whether the validator has active delegations that would be affected by the removal. Force-removing a validator while delegations are active could leave delegators in an inconsistent state.

### Recommendation

Consider adding a check that the validator has no active delegations, or document that delegator state will be cleaned up when the removal completes.

---

## I-03: `_splitDelegatorRemovalRewards` Fee Capping Can Lose Protocol Fee

**Severity:** Informational
**Contract:** StakingVaultOperations
**Lines:** 1512-1530

### Description

For external validators, `protocolFee` is computed as:
```
baseProtocolFee = (rewards * protocolFeeBips) / BIPS
extraProtocolFee = ((rewards * delegationFeeBips / (BIPS - delegationFeeBips)) * protocolFeeBips) / BIPS
totalProtocolFee = baseProtocolFee + extraProtocolFee
```

Then capped: `if (operatorFee + protocolFee > rewards) { protocolFee = rewards - operatorFee; }`

Since `operatorFee` is 0 for external validators, this becomes `if (protocolFee > rewards)`. The `extraProtocolFee` could push the total above the cap, causing some of the protocol fee to be silently lost.

### Recommendation

Compute `protocolFee` more conservatively or split the cap between base and extra protocol fees.

---

## I-04: `isReceivingManagerFunds` Flag Window Allows Stale ETH Inclusion

**Severity:** Informational
**Contract:** StakingVaultOperations
**Lines:** 164-167 (completeValidatorRemoval), 305-307 (completeDelegatorRegistration), 503-512 (harvest), etc.

### Description

Multiple functions set `$.isReceivingManagerFunds = true` before calling the StakingManager and measure `actualInflow = address(this).balance - balBefore` afterward. During this window, if any ETH is sent to the vault (e.g., via `selfdestruct` on Avalanche C-Chain, or from a callback in the StakingManager flow), it would be counted as inflow/rewards.

While `nonReentrant` prevents re-entrant calls to the vault, it does NOT prevent ETH from being force-sent via `selfdestruct` from a separate contract in the same transaction.

### Recommendation

Consider using a pull-based pattern for ETH receipt verification (e.g., record expected amounts from the StakingManager call and verify actual receipt matches). Alternatively, accept this as a known limitation and document it.

---

## I-05: `_validateOperationsImpl` Does Not Verify Implementation Interface

**Severity:** Informational
**Contract:** StakingVault
**Lines:** 1183-1192

### Description

`_validateOperationsImpl` checks that the implementation has code and is not the proxy itself or the UUPS implementation. It does NOT verify that the implementation:
- Implements the expected `IStakingVaultOperations` interface
- Has no constructor with storage initialization
- Uses the same storage layout conventions

A malicious admin could set an implementation that corrupts storage via delegatecall.

### Recommendation

Add a minimum interface check (e.g., verify expected function selectors exist) or document that operations implementation validation is an admin trust assumption.

---

## I-06: `updateOperatorAllocations` Does Not Validate Individual Bips Values

**Severity:** Informational
**Contract:** StakingVaultOperations
**Lines:** 617-644

### Description

`updateOperatorAllocations` allows setting `allocationBips` to any value as long as the total across all operators doesn't exceed `BIPS_DENOMINATOR`. An individual operator could be set to 0 bips (effectively disabled) or to 10000 (monopolizing all allocation). The check only ensures the total is ≤ 10000, not that individual values are reasonable.

### Recommendation

Consider adding per-operator bounds or documentation that the operator manager should set fair allocations.

---

## Positive Observations

1. **Reentrancy protection:** All external state-changing functions use `nonReentrant` via namespaced storage, which is correctly implemented.

2. **First depositor protection:** The `INITIAL_SHARES_OFFSET = 1e9` virtual offset prevents the classic ERC4626 share inflation attack.

3. **Rounding direction:** Both `_stakeToShares` and `_sharesToStake` round DOWN, correctly protecting the vault.

4. **UUPS + ERC-7201:** The storage layout uses namespaced storage, preventing collisions between OZ upgradeable contracts and custom vault storage.

5. **Graceful fee escrow:** When protocol fee recipient reverts, fees are escrowed in `pendingProtocolFees` rather than lost.

6. **Epoch processing with gas awareness:** `processEpoch` has gas guards and scan caps to prevent DoS.

7. **Operator debt freeze:** The `_checkDebtFreeze` mechanism prevents operators from accumulating excessive exit debt relative to their allocation.

8. **Withdrawal queue FIFO:** The queue ensures fair ordering and prevents front-running of withdrawal processing.

9. **Insolvency protection:** `deposit` reverts when `totalSupply() > 0 && getTotalPooledStake() == 0`, preventing share dilution during insolvency.

10. **OperationsImpl validation:** Prevents setting self-reference or proxy implementation as operations target, avoiding infinite recursion.

---

## Appendix: Threat Model Assumptions

This audit assumes:
- The `DEFAULT_ADMIN_ROLE` and `VAULT_ADMIN_ROLE` holders are trusted
- The `OPERATOR_MANAGER_ROLE` holder is trusted but may make mistakes
- Individual operators are untrusted (can grief but not steal)
- The StakingManager contract is trusted and correctly implemented
- Avalanche C-Chain specifics (e.g., `selfdestruct` still forces ETH) apply
