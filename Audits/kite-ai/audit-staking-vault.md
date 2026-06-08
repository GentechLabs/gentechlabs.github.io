# Kite AI Staking Vault — Security Audit Report

**Contracts Audited:**
- `StakingVault.sol` (1239 lines) — Main vault: ERC-20 shares, deposits, withdrawals, epoch processing
- `StakingVaultOperations.sol` (1540 lines) — Extension: validator/delegator lifecycle, operator management, harvesting

**Date:** May 2026
**Compiler:** Solidity 0.8.25
**Pattern:** UUPS proxy + ERC-7201 namespaced storage + delegatecall extension (Diamond-like)

> **Note:** `StakingVaultStorage.sol` and `StakingVaultInternals.sol` are external library dependencies not available in the provided sources. Analysis of their behavior is inferred from usage patterns in the audited contracts.

---

## Executive Summary

The StakingVault is a well-architected liquid staking protocol with strong defensive patterns: reentrancy guards on all external state-changing functions, ERC-7201 namespaced storage, a 1e9 virtual share offset for first-depositor protection, and CEI-aware claim flow. The withdrawal queue uses gas-bounded iteration with MAX_PROCESS_PER_CALL / MAX_ADVANCE_PER_CALL caps.

The audit identified **1 Medium**, **4 Low**, and **3 Informational** findings. No Critical or High severity issues were found. The most significant finding is a class of silent accounting clamping in the state-sync functions that could allow an operator to exceed their allocation cap under accounting drift conditions.

---

## Findings

### M-1: Silent Accounting Clamping in State Sync Allows Operator Allocation Bypass

**Severity:** Medium
**Location:** `StakingVaultOperations.sol` lines 719–794 (`_syncDelegatorState`, `_syncValidatorState`)
**Type:** Accounting Error / Privilege Escalation

**Description:**
When validator or delegator removal completes, `_syncDelegatorState` and `_syncValidatorState` attempt to decrement `operators[operator].activeStake` and aggregate counters. If the tracked amount exceeds the current value (accounting drift from prior mismatches, slashing, or bugs), the code silently clamps to 0 instead of reverting:

```solidity
// StakingVaultOperations.sol, lines 727–734 (_syncDelegatorState)
if ($.operators[operatorAddr].activeStake >= amount) {
    $.operators[operatorAddr].activeStake -= amount;
} else {
    emit IStakingVaultOperations.StakingVault__AccountingMismatchDetected(
        "syncDelegatorActiveStake", amount, $.operators[operatorAddr].activeStake
    );
    $.operators[operatorAddr].activeStake = 0;  // ← silently clamped
}
```

The same pattern exists for `totalDelegatedStake` (lines 737–744) and `totalValidatorStake` (lines 767–774 in `_syncValidatorState`).

**Exploit Scenario:**
1. Due to a prior accounting bug or edge case (e.g., double-decrement from race conditions across multiple `completeDelegatorRemoval` calls via the adoption path at line 394–397), an operator's `activeStake` is decremented below its true value.
2. The clamping sets `activeStake = 0`, even though the operator still has active validators/delegators tracked in the StakingManager.
3. The operator then calls `initiateValidatorRegistration` or `initiateDelegatorRegistration`. The `_checkBufferAndAllocation` function (line 1341–1348) uses `op.activeStake` to verify allocation limits:
   ```solidity
   uint256 maxAllocation = (totalPooled * op.allocationBips) / StakingVaultStorageLib.BIPS_DENOMINATOR;
   if (op.activeStake + amount > maxAllocation) { revert ...; }
   ```
4. With `activeStake = 0`, the operator can register additional validators/delegators beyond their intended allocation, concentrating more vault funds under their control than intended.
5. This increases the vault's risk concentration in a single operator and reduces the liquidity buffer safety margin for other operators' withdrawal requests.

**Impact:** An operator can exceed their allocation cap by an arbitrary amount, concentrating risk. Combined with exit debt manipulation, this could delay user withdrawals if the over-allocated operator's stake is locked for the minimum duration.

**Recommendation:**
Revert instead of clamping when accounting mismatches occur. The existing `StakingVault__AccountingMismatchDetected` event indicates the developers are aware of the possibility — it should be an error, not a silent correction:
```solidity
if ($.operators[operatorAddr].activeStake < amount) {
    revert IStakingVault.StakingVault__AccountingMismatch(
        "syncDelegatorActiveStake", amount, $.operators[operatorAddr].activeStake
    );
}
$.operators[operatorAddr].activeStake -= amount;
```

---

### L-1: CEI Violation in `requestWithdrawal` — External Call Before `_burn`

**Severity:** Low
**Location:** `StakingVault.sol` lines 385–398
**Type:** CEI Violation (Mitigated by nonReentrant)

**Description:**
In `requestWithdrawal`, the protocol fee is sent via an external call BEFORE the user's shares are burned:

```solidity
// StakingVault.sol, lines 385–398
uint256 fee = $.withdrawalRequestFee;
if (fee > 0) {
    if (stakeAmount <= fee) revert StakingVault__InvalidAmount();
    stakeAmount -= fee;
    $.vaultAccountedBalance -= fee;
    (bool feeSuccess,) = $.protocolFeeRecipient.call{value: fee}("");  // ← external call
    if (!feeSuccess) {
        $.vaultAccountedBalance += fee;
        $.pendingProtocolFees += fee;
        ...
    }
}
_burn(msg.sender, shares);  // ← state change AFTER external call
```

While the `nonReentrant` guard prevents direct reentrancy, and the `receive()` gate (`isReceivingManagerFunds`) blocks ETH re-entrancy, this violates the Checks-Effects-Interactions pattern. If the `protocolFeeRecipient` is a contract, it receives execution control with the shares still in the user's balance.

**Exploit Scenario (Theoretical):**
If a future code change removes the `nonReentrant` guard or introduces a cross-contract reentrancy path, the fee recipient could call back into the vault and re-enter `requestWithdrawal` with shares still unburned, creating duplicate withdrawal requests.

**Impact:** Low — currently mitigated by `nonReentrant` and `receive()` gate. Code smell that increases fragility for future changes.

**Recommendation:**
Move `_burn` before the fee transfer, or restructure to set `request.fulfilled = true` equivalent state before external calls.

---

### L-2: CEI Violation in `_sendWithdrawalOrEscrow` — State Rollback on Failed Transfer

**Severity:** Low
**Location:** `StakingVault.sol` lines 1036–1048
**Type:** CEI Violation (Mitigated by nonReentrant)

**Description:**
The function decrements `vaultAccountedBalance` before the external call, then increments it back on failure:

```solidity
// StakingVault.sol, lines 1037–1047
$.vaultAccountedBalance -= stakeAmount;

(bool success,) = payable(user).call{value: stakeAmount}("");
if (success) {
    emit IStakingVault.StakingVault__WithdrawalClaimed(user, requestId, stakeAmount);
} else {
    $.vaultAccountedBalance += stakeAmount;         // ← rollback
    $.withdrawalEscrow[user] += stakeAmount;
    $.totalEscrowedWithdrawals += stakeAmount;
    ...
}
```

During the external call, `vaultAccountedBalance` is in a temporarily inconsistent state (decremented but funds not yet sent). Combined with L-1, multiple CEI violations exist in the same call chain.

**Impact:** Low — mitigated by `nonReentrant` guard. The same pattern in `_sendProtocolFee` (lines 1480–1487) has the same issue.

**Recommendation:** Consider using a try/catch pattern or restructuring to maintain invariant consistency throughout the function.

---

### L-3: `completeValidatorRegistration` Is Permissionless — Front-Running Risk

**Severity:** Low
**Location:** `StakingVaultOperations.sol` lines 125–131
**Type:** Access Control Gap

**Description:**
`completeValidatorRegistration` has no role check — only `nonReentrant`:

```solidity
// StakingVaultOperations.sol, lines 125–131
function completeValidatorRegistration(
    uint32 messageIndex
) external nonReentrant returns (bytes32 validationID) {
    StakingVaultStorageLib.StakingVaultStorage storage $ = StakingVaultStorageLib._getStorage();
    validationID = $.stakingManager.completeValidatorRegistration(messageIndex);
    emit IStakingVaultOperations.StakingVault__ValidatorRegistrationCompleted(validationID);
}
```

Anyone can observe a pending validator registration on the P-Chain and front-run the operator by completing it first.

**Exploit Scenario:**
1. Operator A submits a validator registration and waits for P-Chain confirmation.
2. Attacker monitors the P-Chain and sees the confirmation.
3. Attacker calls `completeValidatorRegistration` with the correct `messageIndex` before the operator does.
4. The validator is registered under the vault (as intended), but the operator loses the timing advantage. The validator's uptime clock starts earlier than expected, which could affect reward calculations depending on SM behavior.

**Impact:** Low — the validator still registers correctly under the vault. The main impact is operational (timing disruption for the operator).

**Recommendation:** Consider adding `onlyOperator` to `completeValidatorRegistration`, or at minimum document this as intended behavior.

---

### L-4: `claimWithdrawalFor` Enables Gas Griefing via Frontrunning

**Severity:** Low
**Location:** `StakingVault.sol` lines 436–441
**Type:** Front-Running / Gas Griefing

**Description:**
`claimWithdrawalFor` allows anyone to claim any fulfilled withdrawal request on behalf of the original user:

```solidity
function claimWithdrawalFor(
    uint256 requestId
) external nonReentrant {
    (address user, uint256 stakeAmount) = _claimWithdrawalInternal(requestId, false);
    _sendWithdrawalOrEscrow(user, requestId, stakeAmount);
}
```

The ETH always goes to `request.user`, not `msg.sender`. However, an attacker can frontrun a user's `claimWithdrawal` transaction, causing the user's transaction to revert (since the request is already marked `fulfilled`).

**Exploit Scenario:**
1. User A has a claimable withdrawal at requestId = 42.
2. User A submits `claimWithdrawal(42)` with a gas price of 30 gwei.
3. Attacker sees this in the mempool and submits `claimWithdrawalFor(42)` with gas price of 31 gwei.
4. Attacker's transaction mines first, claiming the withdrawal. User A's transaction reverts.
5. User A paid gas for a reverted transaction. The attacker also paid gas but received no profit.

**Impact:** Low — no funds lost (ETH goes to the correct user), but the user wastes gas and must resubmit.

**Recommendation:** Consider removing `claimWithdrawalFor` or restricting it to whitelisted relayer addresses if batch-claiming is not needed.

---

### I-1: Fallback Mechanism Forwards All Unknown Selectors to OperationsImpl

**Severity:** Informational
**Location:** `StakingVault.sol` lines 163–165
**Type:** Architecture / Trust Assumption

**Description:**
```solidity
fallback() external payable {
    _delegateToOperations();
}
```

Any function selector not defined on `StakingVault` is forwarded to `operationsImpl` via `delegatecall`. The only validation is `_validateOperationsImpl` (line 1183–1192), which checks:
1. `impl.code.length > 0`
2. `impl != address(this)`
3. `impl != _getERC1967Implementation()`

It does NOT validate that the impl implements the expected interface. A buggy or malicious operations impl (set by `DEFAULT_ADMIN_ROLE`) would get full control of the proxy's storage.

**Impact:** This is the standard Diamond proxy pattern. The security relies entirely on the admin's integrity when setting `operationsImpl`. Worth noting that `setOperationsImpl` (line 325) has no timelock.

**Recommendation:** Consider adding a timelock to `setOperationsImpl` or requiring multi-sig approval, similar to how `_authorizeUpgrade` has a delay via `AccessControlDefaultAdminRules`.

---

### I-2: `_validateOperationsImpl` Lacks Interface Compatibility Check

**Severity:** Informational
**Location:** `StakingVault.sol` lines 1183–1192
**Type:** Missing Validation

**Description:**
The validation only checks address sanity. It doesn't verify that the new impl actually implements the `IStakingVaultOperations` interface. Setting an incompatible impl would cause all forwarded calls to revert, bricking the vault's operational functions while keeping core functions (deposit, withdraw) working.

**Impact:** If admin accidentally sets a wrong address as `operationsImpl`, all operator/validator/delegator management functions become unusable until `setOperationsImpl` is called again.

**Recommendation:** Consider adding a interface ID check (e.g., ERC-165) or at minimum a known function selector probe in `_validateOperationsImpl`.

---

### I-3: `harvest()` Unbounded Iteration Can Revert for Large Vaults

**Severity:** Informational
**Location:** `StakingVaultOperations.sol` lines 501–513
**Type:** Denial of Service / Gas Limit

**Description:**
```solidity
function harvest() external nonReentrant returns (uint256 totalRewards) {
    ...
    for (uint256 i; i < opLen;) {
        totalRewards += _harvestOperatorValidators($, i, 0, type(uint256).max);
        totalRewards += _harvestOperatorDelegators($, i, 0, type(uint256).max);
        ...
    }
}
```

With `type(uint256).max` batch size, this processes ALL validators and delegators for ALL operators. For a vault with many operators, each with many validators/delegators, this could exceed the block gas limit.

**Impact:** `harvest()` becomes unusable for large vaults. The batched variants (`harvestValidators`, `harvestDelegators`) exist as alternatives but require manual iteration.

**Recommendation:** Document the gas limits or add a try/catch wrapper so partial harvesting succeeds even if the full iteration exceeds gas.

---

## Areas of Good Design (Not Vulnerabilities)

### Reentrancy Protection
All external state-changing functions use the `nonReentrant` modifier, which delegates to `StakingVaultStorageLib._nonReentrantBefore/_After`. Both the main vault and operations extension share the same reentrancy lock (via delegatecall context). The `receive()` function gates incoming ETH with `isReceivingManagerFunds`, preventing reentrancy during normal operations.

### First Depositor Protection
The `INITIAL_SHARES_OFFSET = 1e9` virtual offset in `_stakeToShares` and `_sharesToStake` makes inflation attacks uneconomical. An attacker would lose ~1e9 wei (~1 gwei) to manipulate the exchange rate by at most 50%, and only when the vault is very small. The insolvency check at `deposit()` line 356 (`if (totalSupply() > 0 && preDepositStake == 0) revert`) blocks deposits when the vault has negative equity.

### Withdrawal Queue Safety
- FIFO processing prevents front-running within the queue
- `MAX_PROCESS_PER_CALL` and `MAX_ADVANCE_PER_CALL` cap gas consumption per call
- `gasleft() <= 120_000` check provides additional gas safety
- `requestId` values are stable (array only grows, entries deleted but not popped)
- Double-claiming is prevented by the `fulfilled` flag checked before state updates

### Epoch-Based Delay
Withdrawal requests have a mandatory epoch delay (`request.requestEpoch >= currentEpoch` causes `processEpoch` to skip), preventing instant drain attacks. The `currentEpochWithdrawalAmount` tracking caps withdrawals per epoch to the available liquidity.

### Operator Allocation Controls
`_checkBufferAndAllocation` enforces both a minimum liquidity buffer and per-operator allocation limits. The buffer uses `getAvailableStake()` which accounts for pending withdrawals, in-flight exits, and the liquidity buffer.

---

## Summary of Findings

| ID | Severity | Title | Location |
|----|----------|-------|----------|
| M-1 | Medium | Silent accounting clamping allows operator allocation bypass | Operations 719–794 |
| L-1 | Low | CEI violation in `requestWithdrawal` fee handling | Vault 385–398 |
| L-2 | Low | CEI violation in `_sendWithdrawalOrEscrow` state rollback | Vault 1036–1048 |
| L-3 | Low | `completeValidatorRegistration` permissionless | Operations 125–131 |
| L-4 | Low | `claimWithdrawalFor` enables gas griefing | Vault 436–441 |
| I-1 | Info | Fallback forwards all selectors to operationsImpl | Vault 163–165 |
| I-2 | Info | `_validateOperationsImpl` lacks interface check | Vault 1183–1192 |
| I-3 | Info | `harvest()` unbounded iteration | Operations 501–513 |

---

*This audit covers the provided source code only. Findings from previous Halborn audits (2025, 2025, 2026) are out of scope. The `StakingVaultStorage.sol` and `StakingVaultInternals.sol` libraries were not available for direct review; their behavior was inferred from usage patterns.*
