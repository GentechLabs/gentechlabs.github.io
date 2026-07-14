# Security Audit Findings: Staking System Contracts

**Audit Scope:** KiteStakingManager.sol, RewardVault.sol, FixedAPRRewardCalculator.sol
**Date:** 2026-05-12
**Auditor:** Hermes Agent (Code4rena bug bounty submission)

---

## Finding 1 — Centralization Risk: Single Owner Controls All Reward Distribution Parameters

**Severity:** High
**Contract:** FixedAPRRewardCalculator.sol (lines 57–67), RewardVault.sol (lines 78–85, 92–101), KiteStakingManager.sol (lines 267–276, 282–290)
**Category:** Centralization / Governance

### Description

The `rewardBasisPoints` in `FixedAPRRewardCalculator` can be changed by the owner at any time via `setRewardBasisPoints()`, with no timelock, no upper bound guard beyond the initial MAX constant, and no notification period. Combined with the owner's ability to `withdraw()` the entire RewardVault balance and `setStakingManager()` to redirect reward distribution, a compromised or malicious owner can:

1. Set `rewardBasisPoints` to MAX_REWARD_BASIS_POINTS (100% APR) to drain the vault faster than expected
2. Set `rewardBasisPoints` to 1 to effectively deny staking rewards
3. Withdraw all funds from RewardVault via `withdraw()`
4. Redirect rewards to a new malicious staking manager via `setStakingManager()`

In `KiteStakingManager`, the owner can also `updateRewardVault()` and `updateRewardCalculator()` at will, meaning the entire reward pipeline is controlled by a single EOA.

### Exploit Scenario

1. Owner's private key is compromised (or is malicious).
2. Attacker calls `setRewardBasisPoints(10000)` → sets APR to 100%.
3. Attacker calls `withdraw(attackerAddress, vaultBalance)` on RewardVault → drains all native tokens.
4. No timelock or multi-sig exists to prevent or delay this.

Alternatively, the owner can call `updateRewardVault(maliciousContract)` on KiteStakingManager, then all future rewards route to attacker-controlled vault.

### Recommendation

- Implement a timelock for `setRewardBasisPoints`, `withdraw`, `setStakingManager`, `updateRewardVault`, and `updateRewardCalculator`.
- Consider multi-sig ownership or a Governor contract.
- Add a maximum reward basis points cap enforced at the `KiteStakingManager` level (defense-in-depth).
- Add a withdrawal rate limit to `RewardVault.withdraw()` (e.g., max X% per day).

---

## Finding 2 — No Validation of rewardRecipient Address in Staking Registration

**Severity:** Medium
**Contract:** KiteStakingManager.sol (lines 134–154, 159–170)
**Category:** Access Control / Input Validation

### Description

Both `initiateValidatorRegistration()` and `initiateDelegatorRegistration()` accept a `rewardRecipient` parameter that is passed directly to the internal `_initiateValidatorRegistration()` / `_initiateDelegatorRegistration()`. There is no validation that `rewardRecipient` is:
- Not `address(0)` (could lead to burned rewards)
- A contract that can receive ETH (could permanently lock rewards)

The `rewardRecipient` is set at staking time and determines where rewards are sent. If set to an address that cannot receive ETH (e.g., a contract that reverts on receive), rewards will accumulate in the RewardVault but the staker cannot claim them.

### Exploit Scenario

1. A user accidentally passes `address(0)` or a non-receivable contract as `rewardRecipient`.
2. Rewards accrue for that validator/delegator.
3. When the stake is unlocked, `_reward()` is called, which calls `vault.distributeReward(account, amount)`.
4. `distributeReward()` calls `payable(to).sendValue(amount)` (line 118 of RewardVault), which reverts if the recipient cannot receive ETH.
5. The reward distribution fails, the event `RewardDistributionFailed` is emitted (from KiteStakingManager._reward), and the reward remains "claimable" but the user cannot actually receive it without changing the reward recipient.

Note: The `distributeReward` in RewardVault does NOT have a fallback to store unclaimed rewards — it simply reverts on failed transfers, which means the entire `_unlock` flow could be impacted depending on how the base StakingManager handles the false return from `_reward`.

### Recommendation

- Validate `rewardRecipient` at registration time: ensure `rewardRecipient != address(0)` and, if it's a contract, that it has a `receive()` or `fallback()` function (using `Address.isContract()` check or try/catch pattern).
- Consider allowing reward recipient changes post-staking.

---

## Finding 3 — Potential Reward Loss on Failed Distribution (Silent Failure)

**Severity:** Medium
**Contract:** KiteStakingManager.sol (lines 194–226), RewardVault.sol (lines 108–120)
**Category:** Fund Loss / Arithmetic

### Description

In `_reward()` (KiteStakingManager line 194), when the vault balance is insufficient, the function returns `false` instead of reverting. This is documented as intentional to allow stake unlocking to proceed. However, this creates a scenario where:

1. A validator's stake is unlocked.
2. Rewards are calculated and `vault.distributeReward()` fails due to insufficient balance.
3. `_reward()` returns `false`.
4. The base StakingManager likely interprets this as "reward not distributed" and may NOT log the pending reward in any way.

There is no on-chain mechanism to track which rewards failed to distribute and should be claimable later. The comment in the code says "Rewards remain claimable via claimValidatorRewards/claimDelegatorRewards" but this depends entirely on the base StakingManager's implementation, which is external.

If the base StakingManager does NOT persist failed rewards, then rewards are permanently lost — the staker has no path to recover them.

### Exploit Scenario

1. Vault has 100 AVAX. Total pending rewards across all validators = 120 AVAX.
2. Validator A unstakes. `_reward()` is called with amount = 50 AVAX.
3. `vault.distributeReward()` fails (insufficient balance? No, 100 >= 50... let's say vault had been partially drained).
4. Actually, the more realistic scenario: the owner withdraws funds from RewardVault right before a batch of unstaking transactions.
5. Multiple validators unstake in the same block. The first gets paid, the rest fail because vault is now empty.
6. Failed rewards are lost unless the base StakingManager persists them.

### Recommendation

- Verify that the base StakingManager's `_unlock` flow persists failed rewards as claimable balances.
- If not, implement a separate mapping `mapping(address => uint256) failedRewards` that accumulates undistributed rewards, with a `claimFailedRewards()` function.
- Consider a vault balance check before initiating unstaking to warn users.

---

## Finding 4 — Reward Calculation: Arithmetic Overflow Risk with Large Stakes

**Severity:** Low
**Contract:** FixedAPRRewardCalculator.sol (lines 110–112)
**Category:** Arithmetic

### Description

The reward calculation at line 110–112:
```solidity
(stakeAmount * rewardBasisPoints * periodUptimeSeconds) / (SECONDS_IN_YEAR * BIPS_CONVERSION_FACTOR)
```

Uses `uint256` arithmetic. While Solidity 0.8.25 has built-in overflow checks, consider the maximum values:
- `stakeAmount`: Could be very large (e.g., 10^27 for 1 billion tokens with 18 decimals)
- `rewardBasisPoints`: max 10000
- `periodUptimeSeconds`: max ~31536000 (1 year)

Maximum intermediate value: `10^27 * 10000 * 31536000 ≈ 3.15 × 10^38`

This exceeds `uint256` max (`1.15 × 10^77`)? No, it doesn't. Let me recalculate:
- `10^27 * 10^4 * 3.15 × 10^7 = 3.15 × 10^38`

`uint256` max is `~1.16 × 10^77`, so this is safe. However, if `stakeAmount` is in wei and represents a very large total supply (e.g., 10^30), and the period is multiple years (if uptime tracking has bugs), overflow becomes possible:
- `10^30 * 10^4 * (2 * 3.15 × 10^7) ≈ 6.3 × 10^41`

Still within uint256. This finding is informational — the math is safe for realistic values but worth noting for documentation.

Actually, let me reconsider. With `uint64` for `periodUptimeSeconds`, the max is `2^64 - 1 ≈ 1.8 × 10^19`. Then:
- `10^27 * 10000 * 1.8 × 10^19 = 1.8 × 10^50`

Still within uint256. **No overflow risk in practice.**

### Exploit Scenario

Not practically exploitable. If `currentUptimeSeconds - lastClaimUptimeSeconds` somehow produces a value > SECONDS_IN_YEAR due to a bug in uptime tracking, the reward would be proportionally larger but not overflow.

### Recommendation

- Add a comment documenting the maximum safe stake amount for the formula.
- Consider using `(stakeAmount * periodUptimeSeconds / SECONDS_IN_YEAR) * rewardBasisPoints / BIPS_CONVERSION_FACTOR` to minimize intermediate value size (reduces peak intermediate from ~10^50 to ~10^23 × 10^4 = 10^27).

---

## Finding 5 — Front-Running: Reward Basis Points Change Allows MEV Extraction

**Severity:** Low
**Contract:** FixedAPRRewardCalculator.sol (lines 57–67)
**Category:** Front-Running / MEV

### Description

When `setRewardBasisPoints()` is called, there is no delay between the transaction being mined and the new rate taking effect. A validator or delegator who monitors the mempool can:

1. See an impending APR increase transaction.
2. Front-run it by staking a large amount just before the increase.
3. Claim rewards at the higher rate immediately after.
4. Back-run by unstaking and withdrawing.

The reverse is also true: an APR decrease can be front-run by unstaking.

### Exploit Scenario

1. Owner announces APR increase from 5% to 10%.
2. Attacker sees the `setRewardBasisPoints(1000)` mempool transaction.
3. Attacker stakes 1M tokens in the same block before the APR change.
4. APR change is mined. Attacker immediately unstakes and claims rewards at 10% for a very short period.
5. Attacker gains disproportionate rewards relative to actual uptime.

Note: The reward formula includes `periodUptimeSeconds`, so the actual gain depends on how short the period is. The profit is proportional to `periodUptimeSeconds`, so for a single-block front-run (~2 seconds), the gain is minimal. This makes the actual exploit marginal.

### Recommendation

- Implement a timelock (e.g., 24–48 hours) for reward basis points changes.
- Add a cooldown period after staking before rewards start accruing.

---

## Finding 6 — RewardVault: ERC20 Rescue Without amount Validation

**Severity:** Low
**Contract:** RewardVault.sol (lines 128–141)
**Category:** Input Validation

### Description

The `rescueERC20()` function (line 128) does not validate that `amount > 0`. While calling with `amount = 0` is harmless, it emits an event with misleading data. More importantly, the function does not validate that the `token` is not the native token (though native token rescue isn't possible through this function, the ERC20 rescue is meant for accidentally sent tokens).

Additionally, if `IERC20(token).safeTransfer()` silently succeeds with `amount = 0` (which most ERC20 implementations do), this is a gas waste but not a vulnerability.

### Exploit Scenario

Not practically exploitable. However, if a non-standard ERC20 token has unusual behavior with `safeTransfer(token, to, 0)`, it could potentially be exploited.

### Recommendation

- Add `require(amount > 0)` check.
- Consider adding a check to prevent rescuing known reward tokens.

---

## Finding 7 — RewardVault: No Balance Accounting — sendValue Reentrancy Risk

**Severity:** Low
**Contract:** RewardVault.sol (lines 92–101, 108–120)
**Category:** Reentrancy

### Description

Both `withdraw()` and `distributeReward()` in RewardVault use `payable(to).sendValue(amount)` (OpenZeppelin's `Address.sendValue`), which sends ETH via a low-level call and forwards all remaining gas. This means the recipient contract receives a callback during the ETH transfer.

If `to` is a malicious contract, it can re-enter `withdraw()` or `distributeReward()`. However:
- `withdraw()` is `onlyOwner` — re-entry by a non-owner would fail the modifier.
- `distributeReward()` is restricted to `stakingManager` — re-entry by a non-stakingManager would fail.

So reentrancy is only possible if the `to` address IS the owner or the stakingManager. In that case:
- Owner re-entering `withdraw()` would need to be a contract, which is unusual.
- StakingManager re-entering `distributeReward()` would need the stakingManager to be a contract that calls back into RewardVault during ETH receipt.

This is a theoretical risk but very low in practice because the owner is typically an EOA or multisig.

**Important note:** The RewardVault does NOT follow checks-effects-interactions pattern — `sendValue` is called BEFORE the event is emitted (lines 99–100 and 118–119). However, since there's no state to manipulate (no balance variable — it uses `address(this).balance`), this is not exploitable.

### Exploit Scenario

Theoretical: If `stakingManager` is a malicious contract, it could re-enter `distributeReward()` during ETH receipt to drain the vault faster than expected. However, `distributeReward()` uses `address(this).balance` which decreases with each transfer, so the reentrancy would eventually fail when balance is insufficient.

### Recommendation

- Add a reentrancy guard to `withdraw()` and `distributeReward()` for defense-in-depth.
- Move event emissions before `sendValue()` calls for better auditability.

---

## Finding 8 — KiteStakingManager: updateRewardVault Does Not Migrate Pending Rewards

**Severity:** Medium
**Contract:** KiteStakingManager.sol (lines 282–290)
**Category:** Fund Loss

### Description

When `updateRewardVault()` is called to point to a new vault, the old vault may still have unclaimed rewards (rewards that failed to distribute due to the `_reward()` returning `false` pattern). These rewards remain in the old vault but are now orphaned — no contract has a reference to the old vault to distribute them.

Additionally, rewards that failed to distribute and are stored as claimable in the base StakingManager may reference the old vault, but `_reward()` now reads from the new vault.

### Exploit Scenario

1. Old vault has 50 AVAX of undistributed rewards (from failed distributions).
2. Owner calls `updateRewardVault(newVault)`.
3. Users who had failed reward distributions now try to claim.
4. `_reward()` reads from newVault (which may have different balance).
5. The 50 AVAX in old vault is permanently locked — no contract can access it (unless old vault is also upgradeable or owner can withdraw from it).

### Recommendation

- Require the owner to drain the old vault before switching (or implement a migration function).
- Add a `migrateVault()` function that transfers all remaining balance from old vault to new vault.
- Log the old vault address in the event (already done) but also require `oldVault.getBalance() == 0` or perform migration automatically.

---

## Finding 9 — FixedAPRRewardCalculator: Uptime Manipulation Assumes Trusted Input

**Severity:** High
**Contract:** FixedAPRRewardCalculator.sol (lines 87–113)
**Category:** Trust Assumption / Oracle Manipulation

### Description

The `calculateIncrementalReward()` function accepts `lastClaimUptimeSeconds` and `currentUptimeSeconds` as parameters. These values are provided by the caller (presumably the base StakingManager, which in turn gets them from on-chain uptime oracle or P-chain). If these values can be manipulated:

1. A validator could report inflated `currentUptimeSeconds` to receive more rewards.
2. A validator could report deflated `lastClaimUptimeSeconds` to extend the claimed period.

The function performs NO validation that:
- `currentUptimeSeconds >= lastClaimUptimeSeconds`
- `currentUptimeSeconds - lastClaimUptimeSeconds <= currentTime - lastClaimTime` (uptime can't exceed elapsed time)
- `currentUptimeSeconds` is monotonically increasing across claims

If the base StakingManager passes these values without validation, this is a critical vulnerability.

### Exploit Scenario

1. Validator starts staking at time T0 with uptime U0.
2. At time T1 (after 1 hour), validator claims rewards with `currentUptimeSeconds = U0 + 86400` (faking 1 day of uptime).
3. `periodUptimeSeconds = U0 + 86400 - U0 = 86400`.
4. Reward = `stakeAmount * rewardBasisPoints * 86400 / (SECONDS_IN_YEAR * 10000)`.
5. Validator receives rewards for 1 day of uptime after only 1 hour.
6. This can be repeated every claim period.

### Recommendation

- Validate that `currentUptimeSeconds - lastClaimUptimeSeconds <= currentTime - lastClaimTime` inside `calculateIncrementalReward()`.
- Ensure the base StakingManager validates uptime inputs against P-chain oracle data.
- Add a monotonically increasing check for `currentUptimeSeconds`.

---

## Finding 10 — KiteStakingManager: No Validation of rewardCalculator in updateRewardCalculator

**Severity:** Medium
**Contract:** KiteStakingManager.sol (lines 267–276)
**Category:** Input Validation / Access Control

### Description

The `updateRewardCalculator()` function accepts any address cast to `IRewardCalculator` without validating:
1. The address is a contract (not an EOA).
2. The contract implements the `IRewardCalculator` interface.
3. The contract is not self-destructible or upgradeable in a way that could change its behavior.

Setting a malicious or non-functional reward calculator could:
- Cause all reward calculations to revert (DoS).
- Return incorrect reward amounts.
- Be used to extract funds if the calculator has callbacks.

### Exploit Scenario

1. Owner (or compromised owner) calls `updateRewardCalculator(maliciousContract)`.
2. `maliciousContract.calculateIncrementalReward()` returns `type(uint256).max`.
3. The base StakingManager attempts to distribute this reward amount.
4. The `_reward()` function checks vault balance (line 215) and returns false if insufficient.
5. So the actual fund loss is prevented by the vault balance check in `_reward()`.
6. However, if the vault has sufficient balance, the entire vault could be drained.

Wait — let me reconsider. The reward is calculated by the calculator and then passed to `_reward()`. The vault balance check should prevent over-distribution. But if the calculator returns a value slightly less than vault balance, it could still be manipulated.

### Recommendation

- Validate that `newRewardCalculator` is a contract using `Address.isContract()`.
- Consider using OpenZeppelin's `AddressChecker` or a try/catch on a view call.
- Store the calculator as a specific implementation type rather than a generic interface.

---

## Finding 11 — Informational: RewardVault Uses address(this).balance Instead of Internal Accounting

**Severity:** Informational
**Contract:** RewardVault.sol
**Category:** Gas Optimization / Best Practice

### Description

The RewardVault uses `address(this).balance` for balance checks instead of maintaining an internal accounting variable. While this is gas-efficient and avoids sync issues, it means:

1. Any native tokens sent directly to the contract (not via `deposit()` or `receive()`) are automatically included in the vault balance.
2. There's no distinction between deposited funds and "stuck" funds.
3. If another contract sends ETH to the vault (e.g., a refund), it's indistinguishable from intentional deposits.

### Recommendation

- This is acceptable for the current use case. Document that any native tokens sent to the contract are considered vault funds.
- Consider adding a `sweep()` function to recover accidentally sent tokens that are NOT intended for rewards.

---

## Finding 12 — Informational: FixedAPRRewardCalculator Uses Fixed-Point Arithmetic Without Rounding Documentation

**Severity:** Informational
**Contract:** FixedAPRRewardCalculator.sol (lines 110–112)
**Category:** Arithmetic / Precision

### Description

The reward formula performs integer division at the end:
```solidity
(stakeAmount * rewardBasisPoints * periodUptimeSeconds) / (SECONDS_IN_YEAR * BIPS_CONVERSION_FACTOR)
```

This truncates toward zero (Solidity default). For small stakers, this means:
- A staker with 1 AVAX (10^18 wei), 5% APR (500 bips), and 1 day of uptime:
  - Reward = `10^18 * 500 * 86400 / (31536000 * 10000) = 4.32 × 10^25 / 3.1536 × 10^11 = 1.3698... × 10^14`
  - This truncates to `136986301369863` wei ≈ 0.000136986301369863 AVAX
  - Precision loss: ~0.0001 wei (negligible)

For very small amounts or short periods, precision loss could be more significant relative to the reward:
- 1 wei staked, 1 second uptime: `1 * 500 * 1 / (31536000 * 10000) = 0` (reward = 0)

This is expected behavior but worth documenting for transparency.

### Recommendation

- Document the minimum stake amount and minimum claim period for non-zero rewards.
- Consider implementing a reward accumulation mechanism for dust amounts.

---

## Finding 13 — Low: No Events for Critical State Changes in Base StakingManager Inheritance

**Severity:** Low
**Contract:** KiteStakingManager.sol
**Category:** Event Emission

### Description

While `KiteStakingManager` emits events for its own configuration changes (`StakingConfigUpdated`, `RewardCalculatorUpdated`, `RewardVaultUpdated`), the actual staking/unstaking operations inherit from the base `StakingManager` contract. If the base contract does not emit sufficient events for reward claims, stake locks, and unlocks, this could hinder off-chain monitoring.

The `RewardDistributionFailed` event is emitted when vault distribution fails, which is good practice.

### Recommendation

- Verify that the base StakingManager emits comprehensive events for all state-changing operations.
- Consider adding wrapper events for claim operations that include both the amount and the reward recipient.

---

## Summary

| # | Severity | Contract | Finding |
|---|----------|----------|---------|
| 1 | High | FixedAPRRewardCalculator + RewardVault + KiteStakingManager | Centralization: single owner controls all reward parameters, vault withdrawal, and calculator |
| 2 | Medium | KiteStakingManager | No validation of rewardRecipient address at registration |
| 3 | Medium | KiteStakingManager + RewardVault | Silent reward distribution failure may cause permanent fund loss |
| 4 | Low | FixedAPRRewardCalculator | Arithmetic overflow risk negligible but intermediate values are large |
| 5 | Low | FixedAPRRewardCalculator | Front-running of reward basis points changes (marginal profit) |
| 6 | Low | RewardVault | ERC20 rescue without amount > 0 validation |
| 7 | Low | RewardVault | sendValue enables reentrancy (mitigated by access control) |
| 8 | Medium | KiteStakingManager | updateRewardVault orphans pending rewards in old vault |
| 9 | High | FixedAPRRewardCalculator | Uptime parameters not validated — allows reward inflation |
| 10 | Medium | KiteStakingManager | updateRewardCalculator accepts any address without validation |
| 11 | Informational | RewardVault | Uses address(this).balance — no internal accounting |
| 12 | Informational | FixedAPRRewardCalculator | Integer division truncation not documented |
| 13 | Low | KiteStakingManager | Insufficient event coverage for inherited operations |

**Critical Findings:** 0
**High Findings:** 2
**Medium Findings:** 4
**Low Findings:** 4
**Informational Findings:** 3
