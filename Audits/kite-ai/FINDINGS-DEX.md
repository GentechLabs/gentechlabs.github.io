# Kite AI Algebra DEX — Deep Security Findings

**Scope:** AlgebraFactory, SwapRouter, NonfungiblePositionManager (Algebra Integral 1.2.2)
**Chain:** Kite Mainnet
**Solidity:** 0.8.20
**Date:** 2026-05-12
**Auditor:** Hermes Agent (deep automated audit)

---

## Finding Summary

| # | Title | Severity | Contract | Lines |
|---|-------|----------|----------|-------|
| 1 | Reentrancy in `collect()` — External Call Before State Update | Medium | NonfungiblePositionManager | 362-411 |
| 2 | `amountInCached` Storage Slot Enables Cross-Call State Corruption | Medium | SwapRouter | 38, 74, 250-252 |
| 3 | Missing Reentrancy Guard on SwapRouter Functions | Medium | SwapRouter | 22-29 |
| 4 | `switchFarmingStatus` Retains Stale Farming Center After `setFarmingCenter` | Medium | NonfungiblePositionManager | 438-451, 454-457 |
| 5 | `increaseLiquidity` Unchecked uint128+uint128 Overflow | Low | NonfungiblePositionManager | 295-301 |
| 6 | Unchecked Arithmetic in Fee Growth Calculation | Low | NonfungiblePositionManager | 230-244 |
| 7 | Farming Status (`tokenFarmedIn`) Not Cleared on NFT Transfer | Low | NonfungiblePositionManager | 509-517 |
| 8 | `computeCustomPoolAddress` Uses Standard Pool Init Code Hash | Low | AlgebraFactory | 88-97 |
| 9 | Factory Owner Can Grief Pool Creation via Vault Hook | Low | AlgebraFactory | 159-162 |
| 10 | No Token Address Validation in Pool Creation | Low | AlgebraFactory | 117-119 |
| 11 | `amountInCached` Commented as "Transient Storage" but Uses Regular Storage | Informational | SwapRouter | 37-38 |
| 12 | Owner Can Set Zero Default Fee, Creating Unprofitable Pools | Informational | AlgebraFactory | 175-180 |
| 13 | No Re-entrancy Guard on Position Manager External Functions | Informational | NonfungiblePositionManager | 252, 309, 362 |
| 14 | `burn()` Requires Zero `tokensOwed` — Users Must Collect Before Burn | Informational | NonfungiblePositionManager | 416 |

---

## Finding 1: Reentrancy in `collect()` — External Call Before State Update

**Severity:** Medium
**Contract:** `NonfungiblePositionManager.sol`
**Lines:** 362-411 (critical path: 377, 402, 407)

### Description

The `collect()` function performs an external call to `pool.collect()` at line 402, transferring tokens to the `recipient`, **before** updating `position.tokensOwed0/1` at line 407. This violates the checks-effects-interactions pattern.

The execution flow:

```
1. Read tokensOwed from position storage        (line 377)
2. If liquidity > 0: update fee snapshots        (lines 378-392)
3. Compute amounts to collect                    (lines 396-398)
4. EXTERNAL CALL: pool.collect(recipient, ...)   (line 402) ← tokens transferred here
5. Update position.tokensOwed                   (line 407) ← state updated AFTER transfer
```

If `recipient` is a contract, the token transfer at step 4 can trigger a callback (e.g., ERC-777 `tokensToSend` hook, ERC-721 `onERC721Received`, or a malicious fallback). During this callback, the attacker can reenter `collect()` before `position.tokensOwed` is decremented at step 5.

### Code Snippet

```solidity
// NonfungiblePositionManager.sol, lines 396-408
(uint128 amount0Collect, uint128 amount1Collect) = (
    params.amount0Max > tokensOwed0 ? tokensOwed0 : params.amount0Max,
    params.amount1Max > tokensOwed1 ? tokensOwed1 : params.amount1Max
);

// the actual amounts collected are returned
(amount0, amount1) = pool.collect(recipient, tickLower, tickUpper, amount0Collect, amount1Collect);
// ^^^ EXTERNAL CALL — tokens transferred to recipient

// sometimes there will be a few less wei than expected due to rounding down in core
unchecked {
    (position.tokensOwed0, position.tokensOwed1) = (tokensOwed0 - amount0Collect, tokensOwed1 - amount1Collect);
}
// ^^^ State update AFTER external call
```

### Exploit Scenario

**Preconditions:** The core Algebra pool's `collect()` function must not internally track per-position collected amounts (i.e., it must re-transfer on repeated calls with the same parameters). If the core pool properly tracks this (like Uniswap V3 core does), the attack is mitigated at the pool level.

**If the core pool does NOT track collected amounts:**

1. Attacker creates a position with significant fees owed.
2. Attacker calls `collect()` with a malicious `recipient` contract.
3. `pool.collect()` transfers `amount0Collect` and `amount1Collect` tokens to the malicious contract.
4. The malicious contract's callback fires. It reenters `collect()` on the NFT position manager.
5. `position.tokensOwed0/1` still has the original values (not yet decremented).
6. The reentrant `collect()` call computes the same `amount0Collect/amount1Collect` and calls `pool.collect()` again.
7. If the core pool re-transfers, the attacker receives double fees.
8. Original `collect()` resumes, decrements `position.tokensOwed` — but tokens are already stolen.

### Impact

- **If core pool does not track collected amounts:** Double-spending of accumulated fees, draining fees from other LPs in the same tick range.
- **If core pool properly tracks:** No direct fund loss, but the reentrancy still exists as an architectural concern. The reentrant call would result in a revert from the pool (zero transfer), wasting gas and potentially causing unexpected behavior in downstream code.

### Dependency Risk

The severity of this finding depends entirely on the core Algebra pool's `collect()` implementation. The Algebra Integral 1.2.2 core pool should track collected amounts internally (similar to Uniswap V3), but this cannot be confirmed without auditing the core contract. **This is a finding because the periphery contract does not defensively protect against reentrancy.**

### Recommended Mitigation

1. **Add `nonReentrant` modifier** to `collect()`, `increaseLiquidity()`, `decreaseLiquidity()`, and `burn()`.
2. **Move state update before external call:**
```solidity
// Update state BEFORE external call
unchecked {
    (position.tokensOwed0, position.tokensOwed1) = (tokensOwed0 - amount0Collect, tokensOwed1 - amount1Collect);
}
// THEN make external call
(amount0, amount1) = pool.collect(recipient, tickLower, tickUpper, amount0Collect, amount1Collect);
```

---

## Finding 2: `amountInCached` Storage Slot Enables Cross-Call State Corruption

**Severity:** Medium
**Contract:** `SwapRouter.sol`
**Lines:** 38, 74, 250-252

### Description

The `SwapRouter` uses a regular storage variable `amountInCached` (line 38) to communicate the computed input amount from the innermost callback of a multi-hop `exactOutput` swap back to the outer `exactOutput` function. This variable is shared mutable state across all calls to the contract.

In a single-hop exact-output swap (lines 237-253), the flow is:

1. `exactOutput` calls `exactOutputInternal` (line 243)
2. `exactOutputInternal` calls `pool.swap(...)` (line 198)
3. The pool invokes `algebraSwapCallback` (line 57)
4. In the single-hop case (line 74): `amountInCached = amountToPay; pay(tokenIn, data.payer, msg.sender, amountToPay);`
5. Control returns to `exactOutput`, which reads `amountIn = amountInCached` (line 250)

The `pay()` call at step 4 executes `SafeERC20.safeTransferFrom()`. If the token being transferred has a callback mechanism (e.g., ERC-777 `tokensToSend` hook, or a custom hook on a malicious token), the attacker can reenter `exactOutput` before `amountInCached` is consumed at step 5.

The reentrant call would set `amountInCached` to a different value, and when the original call resumes, it reads the corrupted value. The `require(amountIn <= params.amountInMaximum)` check on line 251 would then validate against the attacker-controlled value rather than the actual amount owed.

### Code Snippet

```solidity
// SwapRouter.sol, line 38
uint256 private amountInCached = DEFAULT_AMOUNT_IN_CACHED;

// SwapRouter.sol, line 74 (inside algebraSwapCallback)
amountInCached = amountToPay;
tokenIn = tokenOut;
pay(tokenIn, data.payer, msg.sender, amountToPay); // <-- reentrancy via malicious token

// SwapRouter.sol, lines 250-252 (inside exactOutput)
amountIn = amountInCached;
require(amountIn <= params.amountInMaximum, 'Too much requested');
amountInCached = DEFAULT_AMOUNT_IN_CACHED;
```

### Exploit Scenario

1. Attacker deploys a malicious ERC-20 token `MalToken` with a `tokensToSend` or `transferFrom` callback that reenters `SwapRouter.exactOutput()`.
2. A pool exists for `MalToken/WETH`.
3. Attacker calls `exactOutputSingle` requesting `amountOut = X MalToken`, with `amountInMaximum = 100 WETH`.
4. Pool invokes `algebraSwapCallback`. The callback computes `amountToPay = 50 WETH` and stores it in `amountInCached`.
5. `pay()` triggers WETH transfer. If WETH has no callback, the attacker uses a path where an intermediate token has a callback, or the `data.payer` contract has a `tokensToSend` hook.
6. The hook reenters `exactOutputSingle` with a different swap that sets `amountInCached = 5 WETH`.
7. The original callback completes. `exactOutput` reads `amountInCached = 5 WETH`, the `require(5 <= 100)` passes.
8. The actual amount paid to the pool is determined by the pool's computation (50 WETH), but the router's accounting and return value report 5 WETH.

### Impact

- Return value of `exactOutput`/`exactOutputSingle` is unreliable under reentrancy.
- `amountInMaximum` slippage protection is bypassed if the reentrant call sets a lower `amountInCached`.
- External protocols relying on the return value to compute refunds or verify execution could lose funds.
- In multi-hop `exactOutput`, the corruption could cascade through all subsequent hops.

### Recommended Mitigation

1. Add OpenZeppelin's `ReentrancyGuard` (`nonReentrant` modifier) to all public/external functions in `SwapRouter`.
2. Consider using EIP-1153 transient storage (TSTORE/TLOAD) for `amountInCached` to eliminate cross-call persistence (requires Solidity ≥0.8.24).

---

## Finding 3: Missing Reentrancy Guard on SwapRouter Functions

**Severity:** Medium
**Contract:** `SwapRouter.sol`
**Lines:** Entire contract (no `nonReentrant` modifier present)

### Description

The `SwapRouter` contract inherits from `PeripheryImmutableState`, `PeripheryValidation`, `PeripheryPaymentsWithFee`, `Multicall`, and `SelfPermit`, but does **not** inherit `ReentrancyGuard` and does not apply `nonReentrant` to any function. This is in contrast to `AlgebraFactory`, which does use `ReentrancyGuard` on its `createPool` and `createCustomPool` functions.

Every public swap function — `exactInputSingle` (line 108), `exactInput` (line 124), `exactInputSingleSupportingFeeOnTransferTokens` (line 157), `exactOutputSingle` (line 218), and `exactOutput` (line 237) — is callable without reentrancy protection.

This is a prerequisite for Finding 2 and independently increases the attack surface of the contract. Any callback-based reentrancy during token transfers (via `pay()`) could corrupt the shared `amountInCached` storage slot or trigger unexpected behavior in multi-hop swap loops.

### Code Snippet

```solidity
// SwapRouter.sol - contract declaration (lines 22-29)
contract SwapRouter is
    ISwapRouter,
    PeripheryImmutableState,
    PeripheryValidation,
    PeripheryPaymentsWithFee,
    Multicall,
    SelfPermit
{
    // NOTE: No ReentrancyGuard imported or used
    // NOTE: No nonReentrant modifier on any function
```

### Exploit Scenario

Same as Finding 2. The absence of a reentrancy guard is what enables the `amountInCached` corruption.

### Impact

- All swap functions are vulnerable to reentrancy via malicious token callbacks or payer contracts.
- The `Multicall` inheritance compounds this: batching swaps in a multicall while a reentrancy is in progress could corrupt state across multiple calls.

### Recommended Mitigation

Add `ReentrancyGuard` to the inheritance chain and apply `nonReentrant` to all external state-changing functions: `exactInputSingle`, `exactInput`, `exactInputSingleSupportingFeeOnTransferTokens`, `exactOutputSingle`, and `exactOutput`.

---

## Finding 4: `switchFarmingStatus` Retains Stale Farming Center After `setFarmingCenter`

**Severity:** Medium
**Contract:** `NonfungiblePositionManager.sol`
**Lines:** 438-451 (`switchFarmingStatus`), 454-457 (`setFarmingCenter`)

### Description

When the factory owner calls `setFarmingCenter(newFarmingCenter)` (line 454), the `farmingCenter` state variable is updated, but existing `tokenFarmedIn` entries still reference the **old** farming center address.

The `switchFarmingStatus` function (lines 438-451) has two access paths:
- `toActive == true`: requires `farmingApprovals[tokenId] == _farmingCenter` (the new center). Since `farmingApprovals` is cleared on transfer (line 514), old approvals reference the old center, so this path is safe.
- `toActive == false`: allows `msg.sender == tokenFarmedIn[tokenId]` (line 447). Since `tokenFarmedIn` still holds the old center's address, the **old farming center can still call `switchFarmingStatus(tokenId, false)`** for any position that was farmed under its tenure.

### Code Snippet

```solidity
// NonfungiblePositionManager.sol, lines 438-451
function switchFarmingStatus(uint256 tokenId, bool toActive) external override {
    address _farmingCenter = farmingCenter;  // NEW farming center
    bool accessAllowed = msg.sender == _farmingCenter;
    address newFarmForToken;
    if (toActive) {
        require(farmingApprovals[tokenId] == _farmingCenter, 'Not approved for farming');
        newFarmForToken = _farmingCenter;
    } else {
        // can be switched off by current farming center or by the farming center in which nft is farmed
        accessAllowed = accessAllowed || msg.sender == tokenFarmedIn[tokenId];  // OLD farming center!
    }
    require(accessAllowed, 'Only FarmingCenter');
    tokenFarmedIn[tokenId] = newFarmForToken;  // set to address(0) when toActive==false
}
```

### Exploit Scenario

1. Factory owner sets `farmingCenter = CenterA`.
2. Alice mints position #42 and farms it. `tokenFarmedIn[42] = CenterA`.
3. Factory owner changes `farmingCenter = CenterB` (line 454).
4. CenterA is now a "stale" farming center, but `tokenFarmedIn[42]` still points to CenterA.
5. CenterA calls `switchFarmingStatus(42, false)`.
6. Access check: `accessAllowed = (CenterB == CenterB) || (CenterA == tokenFarmedIn[42])` → `true || true` = `true`.
7. `tokenFarmedIn[42]` is set to `address(0)`, disabling farming for Alice's position.
8. Alice cannot re-farm under CenterB without re-approving, and her farming rewards under CenterA are interrupted.

### Impact

- Old farming center retains unilateral ability to disable farming for positions farmed under its tenure.
- If the old farming center is compromised or malicious, it can grief users by disabling farming on arbitrary positions.
- The stale reference creates an inconsistent state where the old center has more authority than it should after being replaced.

### Recommended Mitigation

1. Clear `tokenFarmedIn[tokenId]` when `setFarmingCenter` is called (iterate over affected positions, or accept the gas cost).
2. Alternatively, modify `switchFarmingStatus` to only check the **current** `farmingCenter`, not `tokenFarmedIn`:
```solidity
accessAllowed = accessAllowed; // remove: || msg.sender == tokenFarmedIn[tokenId];
```
3. Add a migration function that allows the new farming center to take over positions from the old center.

---

## Finding 5: `increaseLiquidity` Unchecked uint128+uint128 Overflow

**Severity:** Low
**Contract:** `NonfungiblePositionManager.sol`
**Lines:** 295-301

### Description

In `increaseLiquidity`, the position's liquidity is updated in an `unchecked` block:

```solidity
unchecked {
    if (tokensOwed0 | tokensOwed1 != 0) {
        position.tokensOwed0 += tokensOwed0;
        position.tokensOwed1 += tokensOwed1;
    }
    position.liquidity = positionLiquidity + liquidity;  // line 300
}
```

Both `positionLiquidity` (`uint128`, read from storage at line 266) and `liquidity` (`uint128`, returned from `addLiquidity`) are `uint128`. Their sum is computed in unchecked arithmetic. If the sum exceeds `type(uint128).max` (≈3.4×10³⁸), the result silently wraps around.

The pool core tracks total liquidity independently, so the pool would have the correct total. But the NFT position manager's record would be wrong — the position would show less liquidity than was actually added. The excess liquidity would be "orphaned" under the NFT manager's address in the pool, earning fees that can never be collected.

### Code Snippet

```solidity
// NonfungiblePositionManager.sol, lines 295-301
unchecked {
    if (tokensOwed0 | tokensOwed1 != 0) {
        position.tokensOwed0 += tokensOwed0;  // also unchecked overflow risk
        position.tokensOwed1 += tokensOwed1;  // also unchecked overflow risk
    }
    position.liquidity = positionLiquidity + liquidity;  // uint128 overflow
}
```

### Practical Exploitability

For `uint128` overflow to occur, a single position would need >2^128 tokens of liquidity (≈3.4×10³⁸). This is far larger than any token supply in existence. Even with 18-decimal tokens, this represents more tokens than could ever exist. **Practically unexploitable** but technically a vulnerability.

The `tokensOwed0/1` overflow in the same unchecked block is even less practical since fees are a fraction of traded volume.

### Impact

- Theoretical loss of position data integrity.
- In practice, overflow is impossible given real-world token supplies.

### Recommended Mitigation

Remove the `unchecked` block around the liquidity update, or add a `require`:
```solidity
require(positionLiquidity + liquidity >= positionLiquidity, "Liquidity overflow");
position.liquidity = positionLiquidity + liquidity;
```

---

## Finding 6: Unchecked Arithmetic in Fee Growth Calculation

**Severity:** Low
**Contract:** `NonfungiblePositionManager.sol`
**Lines:** 230-244

### Description

The `_updateUncollectedFees` function computes uncollected fees using `unchecked` arithmetic on the fee growth difference:

```solidity
unchecked {
    tokensOwed0 = uint128(
        FullMath.mulDiv(
            feeGrowthInside0LastX128 - position.feeGrowthInside0LastX128,
            positionLiquidity,
            Constants.Q128
        )
    );
}
```

Under normal operation, fee growth accumulators in Algebra pools are monotonically increasing, so the subtraction is always non-negative. However, if a pool plugin introduces fee growth resets, rollbacks, or migrations, the subtraction could silently underflow in the `unchecked` block, producing a massive `uint256` value. The subsequent `uint128()` cast would truncate this to a large but bounded value, potentially allowing a position to claim far more fees than it is owed.

Additionally, if a position's `feeGrowthInside*LastX128` is somehow set higher than the current pool accumulator (e.g., via a pool migration bug or a plugin interacting with position state incorrectly), this underflow would trigger.

### Code Snippet

```solidity
// NonfungiblePositionManager.sol, lines 230-244
unchecked {
    tokensOwed0 = uint128(
        FullMath.mulDiv(
            feeGrowthInside0LastX128 - position.feeGrowthInside0LastX128,  // potential underflow
            positionLiquidity,
            Constants.Q128
        )
    );
    tokensOwed1 = uint128(
        FullMath.mulDiv(
            feeGrowthInside1LastX128 - position.feeGrowthInside1LastX128,  // potential underflow
            positionLiquidity,
            Constants.Q128
        )
    );
}
```

### Exploit Scenario

1. A pool plugin implements a fee growth migration that resets the accumulator (hypothetical, depending on plugin implementation).
2. A position was created before the reset, with `feeGrowthInside0LastX128` set to a high value.
3. After the reset, the current `feeGrowthInside0LastX128` is lower than the position's stored value.
4. The `unchecked` subtraction wraps around to a very large number.
5. `FullMath.mulDiv` computes a massive `tokensOwed0`.
6. The `uint128()` cast truncates but still yields a large fee amount.
7. The position collects fees far in excess of what was earned.

### Impact

- Under specific pool plugin behaviors or pool migration scenarios, a position could extract more fees than legitimately owed, draining fees from other LPs in the same tick range.
- Under normal Algebra operation, fee growth is monotonically increasing and this cannot occur, so practical exploitability depends on plugin behavior.

### Recommended Mitigation

Add a bounds check before the subtraction:
```solidity
require(feeGrowthInside0LastX128 >= position.feeGrowthInside0LastX128, "Fee growth underflow");
```
Or remove the `unchecked` block for this specific operation.

---

## Finding 7: Farming Status (`tokenFarmedIn`) Not Cleared on NFT Transfer

**Severity:** Low
**Contract:** `NonfungiblePositionManager.sol`
**Lines:** 509-517 vs. 63, 419

### Description

When an NFT position is transferred (via `_beforeTokenTransfer`, lines 509-517), the contract clears `_positions[tokenId].operator` (line 513) and `farmingApprovals[tokenId]` (line 514). However, `tokenFarmedIn[tokenId]` (line 63) is **not** cleared during transfer. It is only cleared in `burn()` (line 419).

This creates an inconsistency: after a transfer, the new owner inherits a position that may still be marked as actively farmed, but the farming approval has been cleared. The farming center can still interact with the position through the farming system, but the new owner has no approval and cannot control the farming status.

### Code Snippet

```solidity
// NonfungiblePositionManager.sol, lines 509-517
function _beforeTokenTransfer(address from, address to, uint256 tokenId, uint256 batch) internal override {
    if (from != address(0)) {
        _positions[tokenId].operator = address(0);       // cleared ✓
        delete farmingApprovals[tokenId];                 // cleared ✓
        // NOTE: tokenFarmedIn[tokenId] is NOT cleared ✗
    }
    super._beforeTokenTransfer(from, to, tokenId, batch);
}
```

### Exploit Scenario

1. Alice owns position NFT #42 which is actively farmed in the farming center.
2. Alice transfers NFT #42 to Bob (e.g., via sale on a marketplace).
3. After transfer: `farmingApprovals[42]` is cleared (Bob has no farming approval), but `tokenFarmedIn[42]` still points to the farming center.
4. The farming center can still call `switchFarmingStatus(42, false)` because `accessAllowed = msg.sender == tokenFarmedIn[tokenId]` evaluates to true (line 447).
5. Bob cannot call `switchFarmingStatus(42, false)` because he is neither the farming center nor the `tokenFarmedIn` address.
6. Bob's position continues to be farmed without his consent, and he has no way to opt out without interacting with the farming center.

### Impact

- The new NFT owner inherits farming status they did not agree to.
- The new owner cannot disable farming without cooperation from the farming center.
- Could lead to griefing if farming center has malicious or restrictive withdrawal logic.

### Recommended Mitigation

Add `delete tokenFarmedIn[tokenId];` to `_beforeTokenTransfer` when `from != address(0)`.

---

## Finding 8: `computeCustomPoolAddress` Uses Standard Pool Init Code Hash

**Severity:** Low
**Contract:** `AlgebraFactory.sol`
**Lines:** 88-97

### Description

Both `computePoolAddress` (line 88) and `computeCustomPoolAddress` (line 93) use the same `POOL_INIT_CODE_HASH` constant (line 60). If custom pools use different bytecode than standard pools (which is the purpose of custom pool deployers), the computed address from `computeCustomPoolAddress` would be incorrect — it would not match the actual CREATE2 address where the custom pool is deployed.

While the factory's internal `poolByPair`/`customPoolByPair` mappings store the actual deployed address (line 150-151) and are unaffected, external tools, frontends, and other contracts that rely on `computeCustomPoolAddress` to predict pool addresses would get wrong results.

### Code Snippet

```solidity
// AlgebraFactory.sol, line 60
bytes32 public constant POOL_INIT_CODE_HASH = 0x62441ebe4e4315cf3d49d5957f94d66b253dbabe7006f34ad7f70947e60bf15c;

// AlgebraFactory.sol, lines 88-97
function computePoolAddress(address token0, address token1) public view override returns (address pool) {
    pool = address(uint160(uint256(keccak256(abi.encodePacked(
        hex'ff', poolDeployer, keccak256(abi.encode(token0, token1)), POOL_INIT_CODE_HASH
    )))));
}

function computeCustomPoolAddress(address deployer, address token0, address token1) public view override returns (address customPool) {
    customPool = address(uint160(uint256(keccak256(abi.encodePacked(
        hex'ff', poolDeployer, keccak256(abi.encode(deployer, token0, token1)), POOL_INIT_CODE_HASH  // same hash!
    )))));
}
```

### Exploit Scenario

1. The factory owner configures a custom pool deployer that uses different bytecode for custom pools (e.g., a pool with custom fee logic).
2. A user or frontend calls `computeCustomPoolAddress(deployer, tokenA, tokenB)` to get the expected pool address.
3. The computed address is wrong because it uses the standard pool's init code hash.
4. The frontend shows the wrong address, or an on-chain contract that uses this address for routing sends funds to a non-existent or wrong contract.

### Impact

- Off-chain tools and frontends display incorrect custom pool addresses.
- On-chain integrators that precompute custom pool addresses could interact with wrong contracts.
- The factory's own internal logic is unaffected (uses actual deployed addresses).

### Recommended Mitigation

Either:
- Accept a `customPoolInitCodeHash` parameter in `computeCustomPoolAddress`, or
- Store the custom pool deployer's init code hash as a separate immutable/constant, or
- Document clearly that `computeCustomPoolAddress` is only valid if custom pools use the same bytecode as standard pools.

---

## Finding 9: Factory Owner Can Grief Pool Creation via Vault Hook

**Severity:** Low
**Contract:** `AlgebraFactory.sol`
**Lines:** 159-162

### Description

During pool creation, the factory calls `vaultFactory.createVaultForPool(pool, creator, deployer, token0, token1)` (line 160) followed by `IAlgebraPool(pool).setCommunityVault(vault)` (line 161). If the vault factory reverts, the entire pool creation transaction reverts.

The `vaultFactory` is set by the owner via `setVaultFactory` (line 199). A compromised or malicious vault factory could:
1. **Grief pool creation** by reverting on all calls.
2. **Set a malicious community vault** that redirects fees to an attacker.
3. **Prevent community fee collection** by returning a contract that accepts but never releases funds.

Since the vault is set once during pool creation and `setCommunityVault` is presumably not callable again, a malicious vault would permanently lock community fees for that pool.

### Code Snippet

```solidity
// AlgebraFactory.sol, lines 159-162
if (address(vaultFactory) != address(0)) {
    address vault = vaultFactory.createVaultForPool(pool, creator, deployer, token0, token1);
    IAlgebraPool(pool).setCommunityVault(vault);
}
```

### Exploit Scenario

1. Owner sets `vaultFactory` to a malicious contract.
2. A user calls `createPool(tokenA, tokenB)`.
3. The pool is deployed, but `vaultFactory.createVaultForPool()` returns a malicious vault address.
4. `pool.setCommunityVault(maliciousVault)` is called.
5. All community fees from swaps in this pool are directed to the malicious vault.
6. The community vault cannot be changed (assuming `setCommunityVault` is a one-time operation).

### Impact

- Pool creation can be griefed (denial of service).
- Community fees can be permanently redirected to a malicious address.
- The owner has full control over this vector (centralization risk).

### Recommended Mitigation

1. Add a `communityFeeReceiver` that can be set independently of the vault factory.
2. Allow pool creators to specify or approve the community vault.
3. Add a timelock on `setVaultFactory` to give LPs time to react.

---

## Finding 10: No Token Address Validation in Pool Creation

**Severity:** Low
**Contract:** `AlgebraFactory.sol`
**Lines:** 117-119

### Description

The `_createPool` function validates `tokenA != tokenB` (line 117) and `token0 != address(0)` (line 119), but does not validate that the token addresses are actual ERC20 contracts. This allows pools to be created with:
- EOAs (which would make swaps always revert)
- Non-standard tokens (rebasing tokens, fee-on-transfer tokens without proper pool support)
-合约 that don't implement the ERC20 interface

While this doesn't directly lead to fund loss (swaps would revert if the token doesn't work), it can:
1. Waste gas on failed pool creation.
2. Create confusion in pool registries and frontends.
3. Be used to create pools that appear legitimate but are non-functional.

### Code Snippet

```solidity
// AlgebraFactory.sol, lines 117-119
require(tokenA != tokenB);
(address token0, address token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
require(token0 != address(0));
// No validation that token0/token1 are actual ERC20 contracts
```

### Impact

- Griefing: wasted gas on non-functional pools.
- Confusion: frontends may display non-functional pools.

### Recommended Mitigation

Add a minimal ERC20 check:
```solidity
require(token0.code.length > 0, "Token0 is not a contract");
require(token1.code.length > 0, "Token1 is not a contract");
```

---

## Finding 11: `amountInCached` Commented as "Transient Storage" but Uses Regular Storage

**Severity:** Informational
**Contract:** `SwapRouter.sol`
**Lines:** 37-38

### Description

The NatSpec comment on line 37 states `"Transient storage variable"` but `amountInCached` is declared as a regular `uint256 private` storage variable, not using EIP-1153 transient storage (TSTORE/TLOAD). Transient storage was introduced in Solidity 0.8.24 with the `transient` keyword. The contract uses Solidity 0.8.20.

This is misleading to auditors and developers. It may also be a gas optimization missed — transient storage is significantly cheaper (100 gas vs 20,000 gas for SSTORE/SLOAD) and would be semantically correct since the value is only needed within a single transaction. Additionally, transient storage would eliminate the cross-call state corruption issue from Finding 2 (transient storage is cleared at end of transaction).

### Recommended Mitigation

If upgrading to Solidity ≥0.8.24, change to:
```solidity
uint256 private transient amountInCached = DEFAULT_AMOUNT_IN_CACHED;
```
Otherwise, update the comment to say "storage variable."

---

## Finding 12: Owner Can Set Zero Default Fee, Creating Unprofitable Pools

**Severity:** Informational
**Contract:** `AlgebraFactory.sol`
**Lines:** 175-180

### Description

The `setDefaultFee` function has no minimum fee check. The owner can set `defaultFee` to 0, causing all newly created pools (via `createPool`) to have zero swap fees. This means LPs earn no fees while bearing full impermanent loss risk.

While this may be intentional for certain pool types (e.g., stable pairs), it represents a centralization risk: a compromised or malicious owner could set fees to 0 to grief LPs.

### Recommended Mitigation

Consider adding `require(newDefaultFee >= MIN_DEFAULT_FEE)` if a minimum fee is desired for LP protection. Alternatively, document that zero fees are intentional.

---

## Finding 13: No Re-entrancy Guard on Position Manager External Functions

**Severity:** Informational
**Contract:** `NonfungiblePositionManager.sol`
**Lines:** 252, 309, 362

### Description

Neither `increaseLiquidity`, `decreaseLiquidity`, `collect`, nor `burn` uses a `nonReentrant` modifier. While these functions interact with the Algebra pool (which has its own reentrancy lock per-pool), a cross-pool reentrancy scenario could theoretically cause issues if a malicious token's transfer callback reenters the position manager.

In practice, the Algebra pool's reentrancy lock and the fact that `addLiquidity`/`_burnPositionInPool` are pool-level calls that should complete atomically make this very low risk. However, adding `nonReentrant` would be defense-in-depth.

### Recommended Mitigation

Add `nonReentrant` modifier to `increaseLiquidity`, `decreaseLiquidity`, `collect`, and `burn`.

---

## Finding 14: `burn()` Requires Zero `tokensOwed` — Users Must Collect Before Burn

**Severity:** Informational
**Contract:** `NonfungiblePositionManager.sol`
**Lines:** 416

### Description

The `burn()` function requires `position.liquidity | position.tokensOwed0 | position.tokensOwed1 == 0`. This means users must:
1. Remove all liquidity via `decreaseLiquidity`
2. Collect all fees via `collect`
3. Only then can they burn the NFT

This is a UX consideration rather than a vulnerability. Users who forget to collect fees before burning will get a revert. Some protocols combine decrease+collect+burn into a single multicall, but this contract doesn't provide such a convenience function.

### Recommended Mitigation

Consider adding a `burnAndCollect` convenience function, or document the requirement clearly in the contract interface.

---

## Areas Reviewed Without Findings

The following areas were reviewed and found to be correctly implemented:

1. **Price manipulation via flash loans**: All swap functions have `amountOutMinimum`/`amountInMaximum` slippage checks. Liquidity operations have `amount0Min`/`amount1Min`. Flash loan attacks would be mitigated by proper slippage parameters.

2. **Oracle manipulation / TWAP attacks**: The audited contracts do not directly consume TWAP oracle data. TWAP is maintained at the pool level (upstream Algebra). External protocols consuming Algebra TWAPs should implement their own TWAP staleness checks.

3. **Sandwich attack vectors on swaps**: Standard slippage protection is present. The `checkDeadline` modifier prevents deadline-based attacks. The `limitSqrtPrice` parameter allows users to set price limits for additional protection.

4. **Concentrated liquidity edge cases**: The tick-based position management, fee growth accounting, and liquidity calculations follow the standard Algebra/Uniswap V3 patterns. The `_updateUncollectedFees` function correctly handles fee accumulation (except for the unchecked arithmetic noted in Finding 6).

5. **Position NFT handling**: ERC721 operations (mint, burn, transfer, approve) are correctly implemented. The `_beforeTokenTransfer` hook properly clears operator and farming approvals on transfer. Token ID overflow is practically impossible (`uint176` max ≈ 10^52).

6. **Factory initialization**: The constructor correctly sets `poolDeployer`, `defaultTickspacing`, and `defaultFee`. The use of `Ownable2Step` for ownership transfers provides two-step protection. The `renounceOwnership` function has a 1-day time delay.

7. **Fee calculation**: The `FullMath.mulDiv` computation in `_updateUncollectedFees` correctly handles precision. The `uint128` truncation after `mulDiv` results in at most 1 wei of rounding loss per token per collect, which is standard and documented behavior.

8. **Callback validation**: `CallbackValidation.verifyCallback` in the SwapRouter correctly verifies that callbacks originate from legitimate pool contracts.

9. **CREATE2 salt manipulation**: The pool creation salt is `keccak256(abi.encode(token0, token1))` for standard pools and `keccak256(abi.encode(deployer, token0, token1))` for custom pools. Since token order is canonical (`token0 < token1`, enforced at line 118), there is no salt manipulation possible.

10. **`_nextPoolId` and `_nextId` overflow**: Both use `unchecked` increment but are `uint80` and `uint176` respectively, making overflow practically impossible.

---

## Methodology

- Manual code review of all three contracts (AlgebraFactory, SwapRouter, NonfungiblePositionManager)
- Analysis of inter-contract interactions and state management
- Review of access control patterns and modifier usage
- Evaluation of ERC20/ERC721 token handling and transfer patterns
- Assessment of reentrancy attack surfaces via callback mechanisms
- Comparison against known Algebra Integral 1.2.2 vulnerability patterns
- Analysis of concentrated liquidity edge cases and fee calculation correctness
- Evaluation of factory CREATE2 address computation and salt manipulation risks
- Review of farming center integration and status management

## Disclaimer

This audit is not a formal security audit. Findings are based on static analysis of the provided source code without access to test suites, deployment scripts, or on-chain verification. The auditor makes no guarantees about the completeness of findings. Upstream Algebra bugs are considered out of scope per the bug bounty program rules. The severity of Finding 1 (collect reentrancy) depends on the core Algebra pool's `collect()` implementation, which was not available for review.
