# Kite AI Algebra DEX — Security Audit Report

**Scope:** AlgebraFactory, SwapRouter, NonfungiblePositionManager (Algebra Integral 1.2.2)
**Chain:** Kite Mainnet
**Solidity:** 0.8.20
**Date:** 2026-05-12
**Auditor:** Hermes Agent (automated)

---

## Executive Summary

This audit reviews the Algebra DEX periphery contracts deployed on Kite Mainnet as part of a bug bounty program. The contracts are a fork of Algebra Integral 1.2.2 (itself derived from Uniswap V3 periphery patterns). The audit focuses on deployment-specific issues, integration risks, and novel vulnerability classes rather than upstream Algebra bugs (which are typically out of scope for bug bounties).

**Finding Summary:**

| # | Title | Severity | Contract |
|---|-------|----------|----------|
| 1 | `amountInCached` Storage Slot Enables Cross-Call State Corruption via Reentrancy | Medium | SwapRouter |
| 2 | Missing Reentrancy Guard on SwapRouter Functions | Medium | SwapRouter |
| 3 | Unchecked Arithmetic in Fee Growth Calculation Enables Silent Fee Theft | Low | NonfungiblePositionManager |
| 4 | Farming Status (`tokenFarmedIn`) Not Cleared on NFT Transfer | Low | NonfungiblePositionManager |
| 5 | `computeCustomPoolAddress` Uses Standard Pool Init Code Hash | Low | AlgebraFactory |
| 6 | Owner Can Set Zero Default Fee, Creating Unprofitable Pools | Informational | AlgebraFactory |
| 7 | `amountInCached` Commented as "Transient Storage" but Uses Regular Storage | Informational | SwapRouter |
| 8 | No Re-entrancy Guard on `increaseLiquidity` or `decreaseLiquidity` | Informational | NonfungiblePositionManager |

---

## Finding 1: `amountInCached` Storage Slot Enables Cross-Call State Corruption via Reentrancy

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
5. Before paying, `pay()` transfers WETH. If WETH itself is not exploitable, the attacker can instead use a path where MalToken is the intermediate token in a multi-hop swap. Alternatively, if `data.payer` is a contract with a `tokensToSend` hook (as the attacker-controlled caller), the hook fires during `transferFrom`.
6. The hook reenters `exactOutputSingle` with a different swap that sets `amountInCached = 5 WETH`.
7. The original callback completes. `exactOutput` reads `amountInCached = 5 WETH`, the `require(5 <= 100)` passes, and the transaction succeeds.
8. The actual amount paid to the pool is determined by the pool's swap computation (50 WETH), but the router's accounting and return value report 5 WETH, causing downstream integrators (e.g., aggregators, limit-order protocols) to misreport the actual cost.

### Impact

- Return value of `exactOutput`/`exactOutputSingle` is unreliable under reentrancy.
- `amountInMaximum` slippage protection is bypassed if the reentrant call sets a lower `amountInCached`.
- External protocols relying on the return value to compute refunds or verify execution could lose funds.

### Recommended Mitigation

1. Add OpenZeppelin's `ReentrancyGuard` (`nonReentrant` modifier) to all public/external functions in `SwapRouter`.
2. Consider using EIP-1153 transient storage (TSTORE/TLOAD) for `amountInCached` to eliminate cross-call persistence (requires Solidity ≥0.8.24).

---

## Finding 2: Missing Reentrancy Guard on SwapRouter Functions

**Severity:** Medium
**Contract:** `SwapRouter.sol`
**Lines:** Entire contract (no `nonReentrant` modifier present)

### Description

The `SwapRouter` contract inherits from `PeripheryImmutableState`, `PeripheryValidation`, `PeripheryPaymentsWithFee`, `Multicall`, and `SelfPermit`, but does **not** inherit `ReentrancyGuard` and does not apply `nonReentrant` to any function. This is in contrast to `AlgebraFactory`, which does use `ReentrancyGuard` on its `createPool` and `createCustomPool` functions.

Every public swap function — `exactInputSingle` (line 108), `exactInput` (line 124), `exactInputSingleSupportingFeeOnTransferTokens` (line 157), `exactOutputSingle` (line 218), and `exactOutput` (line 237) — is callable without reentrancy protection.

This is a prerequisite for Finding 1 and independently increases the attack surface of the contract. Any callback-based reentrancy during token transfers (via `pay()`) could corrupt the shared `amountInCached` storage slot or trigger unexpected behavior in multi-hop swap loops.

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

Same as Finding 1. The absence of a reentrancy guard is what enables the `amountInCached` corruption.

### Recommended Mitigation

Add `ReentrancyGuard` to the inheritance chain and apply `nonReentrant` to all external state-changing functions: `exactInputSingle`, `exactInput`, `exactInputSingleSupportingFeeOnTransferTokens`, `exactOutputSingle`, and `exactOutput`.

---

## Finding 3: Unchecked Arithmetic in Fee Growth Calculation Enables Silent Fee Theft

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

Under normal operation, fee growth accumulators in Algebra pools are monotonically increasing, so the subtraction `feeGrowthInside0LastX128 - position.feeGrowthInside0LastX128` is always non-negative. However, if a pool plugin or a future pool upgrade introduces fee growth resets, rollbacks, or migrations, the subtraction could silently underflow in the `unchecked` block, producing a massive `uint256` value. The subsequent `uint128()` cast would truncate this to a large but bounded value, potentially allowing a position to claim far more fees than it is owed.

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

## Finding 4: Farming Status (`tokenFarmedIn`) Not Cleared on NFT Transfer

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

// NonfungiblePositionManager.sol, line 63
mapping(uint256 tokenId => address farmingCenterAddress) public tokenFarmedIn;

// NonfungiblePositionManager.sol, line 419 (burn only)
delete tokenFarmedIn[tokenId];
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

## Finding 5: `computeCustomPoolAddress` Uses Standard Pool Init Code Hash

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

## Finding 6: Owner Can Set Zero Default Fee, Creating Unprofitable Pools

**Severity:** Informational
**Contract:** `AlgebraFactory.sol`
**Lines:** 175-180

### Description

The `setDefaultFee` function has no minimum fee check. The owner can set `defaultFee` to 0, causing all newly created pools (via `createPool`) to have zero swap fees. This means LPs earn no fees while bearing full impermanent loss risk.

While this may be intentional for certain pool types (e.g., stable pairs), it represents a centralization risk: a compromised or malicious owner could set fees to 0 to grief LPs.

### Code Snippet

```solidity
// AlgebraFactory.sol, lines 175-180
function setDefaultFee(uint16 newDefaultFee) external override onlyOwner {
    require(newDefaultFee <= Constants.MAX_DEFAULT_FEE);  // only upper bound checked
    require(defaultFee != newDefaultFee);
    defaultFee = newDefaultFee;  // can be set to 0
    emit DefaultFee(newDefaultFee);
}
```

### Impact

- Owner can grief LPs by setting fees to 0.
- LPs who provide liquidity to new pools would earn no fees.

### Recommended Mitigation

Consider adding `require(newDefaultFee >= MIN_DEFAULT_FEE)` if a minimum fee is desired for LP protection. Alternatively, document that zero fees are intentional.

---

## Finding 7: `amountInCached` Commented as "Transient Storage" but Uses Regular Storage

**Severity:** Informational
**Contract:** `SwapRouter.sol`
**Lines:** 37-38

### Description

The NatSpec comment on line 37 states `"Transient storage variable"` but `amountInCached` is declared as a regular `uint256 private` storage variable, not using EIP-1153 transient storage (TSTORE/TLOAD). Transient storage was introduced in Solidity 0.8.24 with the `transient` keyword. The contract uses Solidity 0.8.20.

This is misleading to auditors and developers. It may also be a gas optimization missed — transient storage is significantly cheaper (100 gas vs 20,000 gas for SSTORE/SLOAD) and would be semantically correct since the value is only needed within a single transaction.

### Code Snippet

```solidity
// SwapRouter.sol, lines 37-38
/// @dev Transient storage variable used for returning the computed amount in for an exact output swap.
uint256 private amountInCached = DEFAULT_AMOUNT_IN_CACHED;
```

### Impact

- Misleading documentation for auditors and developers.
- Gas inefficiency: each SSTORE costs ~20,000 gas vs 100 gas for TSTORE.
- Also eliminates the cross-call state corruption issue from Finding 1 (transient storage is cleared at end of transaction).

### Recommended Mitigation

If upgrading to Solidity ≥0.8.24, change to:
```solidity
uint256 private transient amountInCached = DEFAULT_AMOUNT_IN_CACHED;
```
Otherwise, update the comment to say "storage variable."

---

## Finding 8: No Re-entrancy Guard on `increaseLiquidity` or `decreaseLiquidity`

**Severity:** Informational
**Contract:** `NonfungiblePositionManager.sol`
**Lines:** 252, 309

### Description

Neither `increaseLiquidity` nor `decreaseLiquidity` uses a `nonReentrant` modifier. While these functions interact with the Algebra pool (which has its own reentrancy lock per-pool), a cross-pool reentrancy scenario could theoretically cause issues if a malicious token's transfer callback reenters the position manager.

In practice, the Algebra pool's reentrancy lock and the fact that `addLiquidity`/`_burnPositionInPool` are pool-level calls that should complete atomically make this very low risk. However, adding `nonReentrant` would be defense-in-depth.

### Code Snippet

```solidity
// NonfungiblePositionManager.sol, lines 252-258
function increaseLiquidity(
    IncreaseLiquidityParams calldata params
)
    external
    payable
    override
    checkDeadline(params.deadline)
    returns (uint128 liquidity, uint256 amount0, uint256 amount1)
{
    // No nonReentrant modifier

// NonfungiblePositionManager.sol, lines 309-317
function decreaseLiquidity(
    DecreaseLiquidityParams calldata params
)
    external
    payable
    override
    isAuthorizedForToken(params.tokenId)
    checkDeadline(params.deadline)
    returns (uint256 amount0, uint256 amount1)
{
    // No nonReentrant modifier
```

### Impact

- Minimal in practice due to pool-level reentrancy locks.
- Defense-in-depth recommendation.

### Recommended Mitigation

Add `nonReentrant` modifier to `increaseLiquidity`, `decreaseLiquidity`, `collect`, and `burn`.

---

## Areas Reviewed Without Findings

The following areas were reviewed and found to be correctly implemented:

1. **Price manipulation via flash loans**: All swap functions have `amountOutMinimum`/`amountInMaximum` slippage checks. Liquidity operations have `amount0Min`/`amount1Min`. Flash loan attacks would be mitigated by proper slippage parameters.

2. **Oracle manipulation / TWAP attacks**: The audited contracts do not directly consume TWAP oracle data. TWAP is maintained at the pool level (upstream Algebra). External protocols consuming Algebra TWAPs should implement their own TWAP staleness checks.

3. **Sandwich attack vectors on swaps**: Standard slippage protection is present. The `checkDeadline` modifier prevents deadline-based attacks. The `limitSqrtPrice` parameter allows users to set price limits for additional protection.

4. **Concentrated liquidity edge cases**: The tick-based position management, fee growth accounting, and liquidity calculations follow the standard Algebra/Uniswap V3 patterns. The `_updateUncollectedFees` function correctly handles fee accumulation (except for the unchecked arithmetic noted in Finding 3).

5. **Position NFT handling**: ERC721 operations (mint, burn, transfer, approve) are correctly implemented. The `_beforeTokenTransfer` hook properly clears operator and farming approvals on transfer. Token ID overflow is practically impossible (`uint176` max ≈ 10^52).

6. **Factory initialization**: The constructor correctly sets `poolDeployer`, `defaultTickspacing`, and `defaultFee`. The use of `Ownable2Step` for ownership transfers provides two-step protection. The `renounceOwnership` function has a 1-day time delay.

7. **Fee calculation**: The `FullMath.mulDiv` computation in `_updateUncollectedFees` correctly handles precision. The `uint128` truncation after `mulDiv` results in at most 1 wei of rounding loss per token per collect, which is standard and documented behavior.

8. **Callback validation**: `CallbackValidation.verifyCallback` in the SwapRouter correctly verifies that callbacks originate from legitimate pool contracts.

---

## Methodology

- Manual code review of all three contracts (AlgebraFactory, SwapRouter, NonfungiblePositionManager)
- Analysis of inter-contract interactions and state management
- Review of access control patterns and modifier usage
- Evaluation of ERC20/ERC721 token handling and transfer patterns
- Assessment of reentrancy attack surfaces via callback mechanisms
- Comparison against known Algebra Integral 1.2.2 vulnerability patterns

## Disclaimer

This audit is not a formal security audit. Findings are based on static analysis of the provided source code without access to test suites, deployment scripts, or on-chain verification. The auditor makes no guarantees about the completeness of findings. Upstream Algebra bugs are considered out of scope per the bug bounty program rules.
