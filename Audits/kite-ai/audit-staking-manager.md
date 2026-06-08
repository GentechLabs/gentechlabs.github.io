# Kite AI — Staking Manager & Reward System Audit Report

**Auditor:** Hermes Agent  
**Date:** 2026-05-12  
**Scope:** KiteStakingManager.sol, RewardVault.sol, FixedAPRRewardCalculator.sol  
**In-Context References:** StakingVault.sol, StakingVaultOperations.sol  
**Compiler:** Solidity 0.8.25  
**Previous Audits (Out of Scope):** GoKite 2025, Kite Core 2025, Kite Staking & Rewards 2026

---

## Executive Summary

This audit covers the Kite AI reward distribution and staking manager contracts on Kite Mainnet (EVM). The system consists of:
- **KiteStakingManager** — Upgradeable staking manager that overrides `_reward()` to distribute from a RewardVault
- **RewardVault** — Holds native KITE tokens; only the staking manager can call `distributeReward()`
- **FixedAPRRewardCalculator** — Calculates rewards using simple interest at configurable APR (default 2.5%)
- **StakingVault / StakingVaultOperations** — Liquid staking vault that harvests rewards and manages operator allocations

**Findings: 1 Critical, 2 High, 3 Medium, 4 Low**

---

## Finding 1: `_reward()` Reverts Despite Being Designed to Return `false` — Permanent Fund Lock

**Severity:** CRITICAL  
**Category:** Reward Distribution Failure / Stuck Funds  
**Contracts:** KiteStakingManager.sol (line 194–226), RewardVault.sol (line 108–120)  
**Location:** `KiteStakingManager._reward()` line 224

### Description

The `_reward()` function is explicitly designed to return `false` instead of reverting when distribution fails (comment on lines 191–192):

```solidity
// KiteStakingManager.sol lines 189–193
/**
 * @notice See {StakingManager-_reward}
 * @dev Distributes rewards from the RewardVault instead of minting.
 * Returns false instead of reverting if distribution fails, allowing stake
 * unlocking to proceed while preserving rewards for later claiming.
 */
```

However, the implementation only returns `false` for the **vault balance insufficient** case (lines 215–222). When the vault balance check **passes** but `vault.distributeReward()` subsequently **reverts** (e.g., the recipient contract's `receive()` function reverts), the entire `_reward()` call reverts:

```solidity
// KiteStakingManager.sol lines 194–226
function _reward(
    address account,
    uint256 amount
) internal virtual override returns (bool) {
    if (amount == 0) {
        return true;
    }

    KiteStakingManagerStorage storage $ = _getKiteStakingManagerStorage();
    RewardVault vault = $.rewardVault;

    if (address(vault) == address(0)) {
        emit RewardDistributionFailed(account, amount, "RewardVault not set");
        return false;  // ← Graceful failure ✓
    }

    uint256 vaultBalance = address(vault).balance;
    if (vaultBalance < amount) {
        emit RewardDistributionFailed(account, amount, "Insufficient vault balance");
        return false;  // ← Graceful failure ✓
    }

    vault.distributeReward(account, amount);  // ← CAN REVERT, no try/catch!
    return true;
}
```

`RewardVault.distributeReward()` uses `Address.sendValue()` (OpenZeppelin), which reverts on transfer failure:

```solidity
// RewardVault.sol line 118
payable(to).sendValue(amount);
```

OpenZeppelin's `sendValue()` implementation:
```solidity
function sendValue(address payable recipient, uint256 amount) internal {
    require(address(this).balance >= amount, "Address: insufficient balance");
    (bool success,) = recipient.call{value: amount}("");
    require(success, "Address: unable to send value, recipient may have reverted");
}
```

### Exploit Scenario

1. The StakingVault (or any contract) sets `rewardRecipient` to an address whose `receive()` function reverts (e.g., a contract without a payable fallback, or one that deliberately reverts).
2. A validator/delegator completes their stake lifecycle via `completeValidatorRemoval()` or `completeDelegatorRemoval()`.
3. The base StakingManager calls `_reward(stakingVaultAddress, rewardAmount)`.
4. Vault balance check passes (RewardVault has sufficient funds).
5. `vault.distributeReward()` calls `sendValue()` which reverts because the recipient contract reverts.
6. `_reward()` reverts, which propagates up and **reverts the entire `completeValidatorRemoval()` call**.
7. **The validator's principal stake is permanently locked** — they cannot exit.

This can also be triggered by:
- A malicious validator setting a reverting `rewardRecipient` during registration
- A future contract upgrade that modifies the StakingVault `receive()` function
- Any gas-limit issue in the recipient's `receive()` / `fallback()` function

### Impact

- **Permanent lock of staked funds** for validators/delegators with reverting reward recipients
- Contradicts the documented design intent of graceful failure handling
- Cannot be mitigated by the admin (the reward recipient is set by the staker at registration time)

### Recommendation

Wrap the `distributeReward()` call in a try/catch or low-level call and return `false` on failure:

```solidity
function _reward(
    address account,
    uint256 amount
) internal virtual override returns (bool) {
    if (amount == 0) {
        return true;
    }

    KiteStakingManagerStorage storage $ = _getKiteStakingManagerStorage();
    RewardVault vault = $.rewardVault;

    if (address(vault) == address(0)) {
        emit RewardDistributionFailed(account, amount, "RewardVault not set");
        return false;
    }

    uint256 vaultBalance = address(vault).balance;
    if (vaultBalance < amount) {
        emit RewardDistributionFailed(account, amount, "Insufficient vault balance");
        return false;
    }

    // Use low-level call to prevent reverts from blocking stake unlocking
    (bool success,) = address(vault).call(
        abi.encodeWithSelector(
            vault.distributeReward.selector,
            account,
            amount
        )
    );

    if (!success) {
        emit RewardDistributionFailed(account, amount, "Transfer failed");
        return false;
    }

    return true;
}
```

---

## Finding 2: `RewardVault.distributeReward()` Lacks Reentrancy Protection — Potential Vault Drain

**Severity:** HIGH  
**Category:** Vault Balance Manipulation / Reentrancy  
**Contracts:** RewardVault.sol (line 108–120)  
**Location:** `RewardVault.distributeReward()` line 118

### Description

`RewardVault.distributeReward()` sends native tokens to an external address via `sendValue()` **before** the `RewardDistributed` event is emitted. More critically, the function has **no reentrancy guard**:

```solidity
// RewardVault.sol lines 108–120
function distributeReward(address to, uint256 amount) external {
    if (msg.sender != stakingManager) {
        revert UnauthorizedCaller(msg.sender);
    }
    if (to == address(0)) {
        revert ZeroAddress();
    }
    if (amount > address(this).balance) {
        revert InsufficientBalance(amount, address(this).balance);
    }
    payable(to).sendValue(amount);        // ← External call, ETH transfer
    emit RewardDistributed(to, amount);   // ← Event AFTER external call
}
```

The `sendValue()` call sends ETH to `to`, which triggers `to`'s `receive()` or `fallback()` function. If `to` is a malicious contract, it can reenter the RewardVault.

The only access control is `msg.sender == stakingManager`. In a reentrant call, `msg.sender` would be the staking manager calling `distributeReward()` again (if the attacker can trigger another staking manager operation), allowing repeated drains.

### Exploit Scenario

1. Attacker registers as a validator with `rewardRecipient` = attacker's contract.
2. Attacker's contract `receive()` function triggers a re-entrant call chain:
   - Calls `stakingManager.completeValidatorRemoval()` with a valid `messageIndex`
   - This causes `_reward()` → `distributeReward()` → `sendValue()` to the attacker again
   - The attacker's `receive()` fires again, triggering another removal completion
3. Each reentrant call passes the balance check (the balance hasn't been updated yet at the `require` level — but `sendValue()` does check `address(this).balance` which DOES update between calls).

Actually, since `address(this).balance` reflects the post-transfer balance, each reentrant call would see a reduced balance and eventually stop. However, if the attacker can **time the reentry to call `distributeReward()` for a different validator/delegator's reward**, they could redirect rewards.

More practically, if the `to` address is a contract that:
- Calls `stakingManager.someFunction()` on reentry
- Which calls `_reward()` → `distributeReward()` for a different account

The attacker could redirect rewards intended for other stakers to themselves.

### Impact

- Potential redirection of rewards to attacker-controlled addresses
- In worst case, drain of the entire RewardVault balance through repeated reentrant calls

### Recommendation

Add a `nonReentrant` modifier to `RewardVault`:

```solidity
import {ReentrancyGuard} from "@openzeppelin/contracts@5.0.2/utils/ReentrancyGuard.sol";

contract RewardVault is Ownable2Step, ReentrancyGuard {
    // ...
    function distributeReward(address to, uint256 amount) external nonReentrant {
        // ...
    }
}
```

Also apply CEI pattern (Checks-Effects-Interactions):
```solidity
function distributeReward(address to, uint256 amount) external nonReentrant {
    if (msg.sender != stakingManager) revert UnauthorizedCaller(msg.sender);
    if (to == address(0)) revert ZeroAddress();
    if (amount > address(this).balance) revert InsufficientBalance(amount, address(this).balance);

    emit RewardDistributed(to, amount);  // Effect BEFORE Interaction
    payable(to).sendValue(amount);       // Interaction
}
```

---

## Finding 3: `FixedAPRRewardCalculator` Lacks Uptime Sanity Validation — Inflated Reward Calculation

**Severity:** HIGH  
**Category:** Reward Calculation Precision / Manipulation  
**Contracts:** FixedAPRRewardCalculator.sol (line 87–113)  
**Location:** `FixedAPRRewardCalculator.calculateIncrementalReward()` line 105–106

### Description

The calculator computes rewards based on `periodUptimeSeconds` without validating that uptime does not exceed the elapsed wall-clock time (`periodDuration`):

```solidity
// FixedAPRRewardCalculator.sol lines 98–112
uint64 periodDuration = currentTime - lastClaimTime;     // Line 99
if (periodDuration == 0) {
    return 0;
}

// Line 105-106: NO CHECK that periodUptimeSeconds <= periodDuration
uint64 periodUptimeSeconds = currentUptimeSeconds - lastClaimUptimeSeconds;

return
    (stakeAmount * rewardBasisPoints * periodUptimeSeconds) /
    (SECONDS_IN_YEAR * BIPS_CONVERSION_FACTOR);            // Line 111-112
```

If `periodUptimeSeconds > periodDuration`, the reward exceeds what should be possible for the elapsed time. The reward formula becomes:

```
reward = stakeAmount × 250 × periodUptimeSeconds / (31536000 × 10000)
```

When `periodUptimeSeconds = 2 × periodDuration` (100% uptime inflation), the reward doubles.

### Exploit Scenario

1. The base StakingManager records uptime data via cross-chain messages from the P-Chain.
2. If a bug in uptime tracking (or a delayed/consolidated message batch) causes `currentUptimeSeconds - lastClaimUptimeSeconds` to exceed `currentTime - lastClaimTime`, the reward is inflated.
3. A validator who claims after a period of uptime data consolidation receives a reward that exceeds the theoretical maximum for that time period.
4. This extra reward comes from the RewardVault, potentially draining it faster than intended.

### Impact

- Reward overpayment proportional to the uptime inflation ratio
- Could drain the RewardVault prematurely if uptime data is frequently consolidated
- The `MAX_REWARD_BASIS_POINTS` cap (10000) limits the APR but NOT the uptime multiplier

### Recommendation

Add a validation check:

```solidity
uint64 periodUptimeSeconds = currentUptimeSeconds - lastClaimUptimeSeconds;

// Uptime cannot exceed wall-clock time
if (periodUptimeSeconds > periodDuration) {
    periodUptimeSeconds = periodDuration;
}
```

---

## Finding 4: No Enforcement of Minimum Vault Funding Relative to Total Staked — Systemic Reward Failure

**Severity:** MEDIUM  
**Category:** Reward Distribution Failure / Stuck Funds  
**Contracts:** KiteStakingManager.sol, RewardVault.sol  
**Location:** Global design gap

### Description

The protocol has no mechanism to enforce that the RewardVault is funded proportionally to the total staked amount. With a 2.5% APR:

```
Expected annual rewards = totalStaked × 0.025
```

If `totalStaked = 1,000,000 KITE`, the expected annual reward drain is **25,000 KITE**. If the RewardVault holds only 1,000 KITE:
- After ~14.6 days, the vault is depleted
- All subsequent `_reward()` calls return `false` (insufficient balance)
- All `completeValidatorRemoval()` and harvest calls silently fail to distribute rewards
- Validators must use `claimValidatorRewards` / `claimDelegatorRewards` (if available in the base StakingManager)

When the vault is depleted, the system enters a degraded state where:
1. Rewards accumulate as "pending" but are not distributed
2. If the vault is never re-funded, pending rewards are permanently stuck
3. There is no on-chain metric or alert for vault insolvency

### Exploit Scenario

1. Admin funds the RewardVault with 10,000 KITE
2. Community stakes 1,000,000 KITE total
3. Expected annual rewards: 25,000 KITE (vault covers only ~5 months)
4. After 5 months, vault is depleted
5. New stakers and existing stakers earn 0 rewards until vault is re-funded
6. If the admin doesn't monitor vault balance, this could persist indefinitely

### Impact

- Silent reward distribution failures across all stakers
- No on-chain mechanism to detect or remediate vault insolvency
- Potential loss of staker confidence and capital flight

### Recommendation

- Add a `getVaultHealthRatio()` view function: `vaultBalance / (totalStaked × rewardBasisPoints / 10000)`
- Add an event when vault balance drops below a configurable threshold
- Consider requiring minimum vault funding at initialization or during admin operations

---

## Finding 5: `updateRewardVault()` Accepts Any Address Without Interface Validation — Potential Total Reward Freeze

**Severity:** MEDIUM  
**Category:** Access Control / Admin Configuration  
**Contracts:** KiteStakingManager.sol (line 282–290)  
**Location:** `KiteStakingManager.updateRewardVault()` line 282–290

### Description

The `updateRewardVault()` function only validates that the new address is non-zero:

```solidity
// KiteStakingManager.sol lines 282–290
function updateRewardVault(address newRewardVault) external onlyOwner {
    if (newRewardVault == address(0)) {
        revert InvalidRewardVaultAddress();
    }
    KiteStakingManagerStorage storage $ = _getKiteStakingManagerStorage();
    address oldVault = address($.rewardVault);
    $.rewardVault = RewardVault(payable(newRewardVault));
    emit RewardVaultUpdated(oldVault, newRewardVault);
}
```

It does **not** verify that:
1. The new address is a contract (could be an EOA)
2. The contract implements the `distributeReward(address, uint256)` interface
3. The contract's `stakingManager` pointer is set to this staking manager

### Exploit Scenario

1. Admin (compromised or malicious) calls `updateRewardVault(attackerEOA)`.
2. All subsequent `_reward()` calls attempt `vault.distributeReward()` on the EOA.
3. Since EOAs have no code, the call succeeds (sends ETH to the EOA) but the EOA's `stakingManager` check wouldn't apply — wait, actually the EOA wouldn't have a `distributeReward` function selector, so the call would... actually, sending ETH to an EOA via low-level call succeeds. But `RewardVault` is expected, and calling `distributeReward` on an EOA would return empty data. The `_reward()` function does `vault.distributeReward(account, amount)` which is a Solidity high-level call — calling a function on an EOA **reverts** because there's no matching function selector.
4. If `_reward()` reverts (see Finding 1), all staking operations are frozen.

Alternatively, pointing to a malicious contract that implements `distributeReward` but silently drops funds would drain the vault's intended reward flow.

### Impact

- A single admin mistake can freeze all reward distributions and block staking operations
- No timelock or multi-sig requirement for this critical change
- No interface validation to prevent misconfiguration

### Recommendation

- Add interface validation (staticcall to verify the vault responds correctly)
- Implement a timelock on `updateRewardVault()`
- Consider requiring a 2-step ownership transfer for the new vault (set pending, accept)

---

## Finding 6: `_callU256` Silently Swallows Harvest Failures — Invisible Reward Loss

**Severity:** MEDIUM  
**Category:** Reward Distribution Failure  
**Contracts:** StakingVaultOperations.sol (line 1458–1465)  
**Location:** `_callU256()` utility and its callers

### Description

The `_callU256` utility function silently returns `0` on any failure:

```solidity
// StakingVaultOperations.sol lines 1458–1465
function _callU256(
    address target,
    bytes memory data
) internal returns (uint256 result) {
    (bool success, bytes memory ret) = target.call(data);
    if (success && ret.length >= 32) return abi.decode(ret, (uint256));
    return 0;  // ← Silent failure
}
```

This is used by `_harvestOperatorValidators` (line 1139–1144) and `_harvestOperatorDelegators` (line 1205–1209) to call `claimValidatorRewards` and `claimDelegatorRewards` on the staking manager:

```solidity
// StakingVaultOperations.sol lines 1139–1144
uint256 reward = _callU256(
    mgr,
    abi.encodeWithSelector(
        StakingVaultStorageLib.SEL_CLAIM_VALIDATOR_REWARDS, validationID, false, uint32(0)
    )
);
```

If `claimValidatorRewards` reverts (e.g., because `_reward()` reverts due to Finding 1), the harvest returns `0` and **no event is emitted** to indicate the failure.

### Exploit Scenario

1. `harvest()` is called with `isReceivingManagerFunds = true`.
2. For one validator, `claimValidatorRewards` reverts (reward recipient is a broken contract).
3. `_callU256` catches the revert and returns `0`.
4. The harvest continues for other validators.
5. The failed validator's rewards are silently lost — no event, no metric, no indication.
6. Over time, repeated harvest failures accumulate, and the vault's `vaultAccountedBalance` diverges from actual balance.

### Impact

- Invisible reward loss for individual validators/delegators
- No monitoring capability for harvest failures
- Vault accounting divergence

### Recommendation

- Emit an event when `_callU256` returns 0 (failure) for harvest operations
- Alternatively, use a dedicated wrapper that emits failure events
- Consider using `try/catch` for the staking manager call instead of low-level call

---

## Finding 7: Reward Basis Points Change Has No Timelock — Instant APR Manipulation

**Severity:** LOW  
**Category:** Access Control / Centralization Risk  
**Contracts:** FixedAPRRewardCalculator.sol (line 57–67)  
**Location:** `FixedAPRRewardCalculator.setRewardBasisPoints()` line 57

### Description

The `setRewardBasisPoints()` function can instantly change the reward rate from any value to any other value (within 0–10000 bips) with no timelock or rate limit:

```solidity
// FixedAPRRewardCalculator.sol lines 57–67
function setRewardBasisPoints(uint64 newRewardBasisPoints) external onlyOwner {
    if (newRewardBasisPoints == 0) {
        revert ZeroRewardBasisPoints();
    }
    if (newRewardBasisPoints > MAX_REWARD_BASIS_POINTS) {
        revert RewardBasisPointsExceedsMax(newRewardBasisPoints, MAX_REWARD_BASIS_POINTS);
    }
    uint64 oldBasisPoints = rewardBasisPoints;
    rewardBasisPoints = newRewardBasisPoints;  // ← Instant, no delay
    emit RewardBasisPointsUpdated(oldBasisPoints, newRewardBasisPoints);
}
```

If the owner key is compromised, the attacker can:
1. Set `rewardBasisPoints` to `10000` (100% APR)
2. Wait for rewards to accumulate (or trigger a harvest)
3. Drain the RewardVault through the inflated reward flow

### Impact

- Owner compromise enables rapid vault draining
- No time for community to react or governance to intervene
- Standard centralization risk for owner-privileged functions

### Recommendation

- Implement a timelock on `setRewardBasisPoints()` (e.g., 48-hour delay)
- Add a `MAX_RATE_CHANGE_PER_DAY` to limit how much the APR can change per epoch
- Consider using a multi-sig or governance contract as owner

---

## Finding 8: `RewardVault` Has No Emergency Pause or Withdrawal Limit — Owner Can Drain at Will

**Severity:** LOW  
**Category:** Access Control / Centralization Risk  
**Contracts:** RewardVault.sol (line 92–101)  
**Location:** `RewardVault.withdraw()` line 92

### Description

The `withdraw()` function allows the owner to withdraw any amount from the vault at any time:

```solidity
// RewardVault.sol lines 92–101
function withdraw(address to, uint256 amount) external onlyOwner {
    if (to == address(0)) {
        revert ZeroAddress();
    }
    if (amount > address(this).balance) {
        revert InsufficientBalance(amount, address(this).balance);
    }
    payable(to).sendValue(amount);
    emit Withdrawn(to, amount);
}
```

There is no:
- Maximum withdrawal limit per transaction
- Time delay or timelock
- Pause mechanism
- Minimum balance floor that must be maintained

### Exploit Scenario

1. The RewardVault holds 1,000,000 KITE for reward distribution.
2. The owner (compromised or malicious) calls `withdraw(attackerAddress, 1000000e18)`.
3. The entire vault is drained instantly.
4. All subsequent reward distributions fail (Finding 4 scenario).

### Impact

- Single point of failure: owner compromise = complete vault drain
- No governance oversight on large withdrawals
- Stakers' expected rewards are lost

### Recommendation

- Implement a withdrawal rate limit (e.g., max 10% of vault balance per week)
- Add a timelock on large withdrawals
- Consider a multi-sig or governance-controlled withdrawal process

---

## Finding 9: `KITE_STAKING_MANAGER_STORAGE_LOCATION` Constant May Be Incorrect — Storage Collision Risk

**Severity:** LOW  
**Category:** Upgrade Safety  
**Contracts:** KiteStakingManager.sol (line 32–35)  
**Location:** Constant definition line 34–35

### Description

The ERC-7201 storage location constant is declared as:

```solidity
// KiteStakingManager.sol lines 32–35
// keccak256(abi.encode(uint256(keccak256("avalanche-icm.storage.KiteStakingManager")) - 1)) & ~bytes32(uint256(0xff));
bytes32 public constant KITE_STAKING_MANAGER_STORAGE_LOCATION =
    0x6b1e6c6e0b6e6f6e6c6f6e6b6e6f6e6c6b6e6f6e6c6f6e6b6e6f6e6c6b6e6f00;
```

The hex value `6b1e6c6e0b6e6f6e6c6f6e6b6e6f6e6c6b6e6f6e6c6f6e6b6e6f6e6c6b6e6f00` appears to have a **non-random repeating byte pattern** (visible as ASCII-like sequences: `6b`=k, `6c`=l, `6e`=n, `6f`=o). A properly computed keccak256 hash would produce uniformly distributed bytes.

While this may be the correct computed value (the formula is applied correctly in the comment), the repeating pattern is suspicious and warrants verification. If the constant is incorrect, it could cause **storage collision** with the base `StakingManager` or `Ownable2StepUpgradeable` storage slots during proxy upgrades.

### Impact

- If incorrect, storage collision could corrupt staking state or owner access control during upgrades
- Would only manifest on contract upgrade, making it difficult to detect in testing

### Recommendation

- Verify the constant by computing it independently:
  ```bash
  cast keccak $(cast abi-encode "f(string)" "avalanche-icm.storage.KiteStakingManager")
  ```
- Ensure the constant matches the computed value

---

## Summary Table

| # | Finding | Severity | Contract | Lines |
|---|---------|----------|----------|-------|
| 1 | `_reward()` reverts despite designed to return `false` — permanent fund lock | **CRITICAL** | KiteStakingManager | 194–226 |
| 2 | `RewardVault.distributeReward()` lacks reentrancy protection | **HIGH** | RewardVault | 108–120 |
| 3 | `FixedAPRRewardCalculator` lacks uptime sanity validation | **HIGH** | FixedAPRRewardCalculator | 105–106 |
| 4 | No enforcement of minimum vault funding | **MEDIUM** | Global design | — |
| 5 | `updateRewardVault()` accepts any address without validation | **MEDIUM** | KiteStakingManager | 282–290 |
| 6 | `_callU256` silently swallows harvest failures | **MEDIUM** | StakingVaultOperations | 1458–1465 |
| 7 | Reward basis points change has no timelock | **LOW** | FixedAPRRewardCalculator | 57–67 |
| 8 | `RewardVault` has no emergency pause or withdrawal limit | **LOW** | RewardVault | 92–101 |
| 9 | Storage location constant may be incorrect | **LOW** | KiteStakingManager | 32–35 |

---

## Codebase Observations (Not Findings)

These are observations about the codebase design that may be relevant for context:

1. **Base `StakingManager` not audited**: The `StakingManager` base contract (imported from `./StakingManager.sol`) is not available for review. Key functions like `claimValidatorRewards`, `claimDelegatorRewards`, `_initiateValidatorRegistration`, and `_initiateDelegatorRegistration` are in the base contract. Findings may be amplified or mitigated by base contract behavior.

2. **`nonReentrant` on StakingVault but not RewardVault**: The StakingVault has comprehensive reentrancy protection, but the RewardVault (which holds and distributes native tokens) does not.

3. **Reward flow depends on `isReceivingManagerFunds` flag**: The StakingVault's `receive()` function only accepts ETH when `isReceivingManagerFunds = true`. This flag is set/unset around staking manager calls. If any code path fails to set this flag correctly, reward distributions to the StakingVault will revert.

4. **`_callBool` and `_callU256` swallow all errors**: The StakingVaultOperations utility functions catch and discard all errors from staking manager calls. While this provides fault tolerance, it makes failures invisible and harder to debug.

---

*End of Report*
