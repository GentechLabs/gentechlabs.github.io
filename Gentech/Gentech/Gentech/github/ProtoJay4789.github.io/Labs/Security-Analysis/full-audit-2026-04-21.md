# 🔒 Full Security Audit — Gentech Smart Contracts
**Date:** 2026-04-21
**Auditor:** YoYo (Strategies) — awaiting DMOB technical review
**Methodology:** Manual line review + pattern matching

---

## Executive Summary

**Contracts Audited:** 4
**Critical Findings:** 1
**High Findings:** 3
**Medium Findings:** 4
**Low/Informational:** 5

**Bottom Line:** The contracts follow good patterns (CEI, SafeERC20, custom errors) but have several issues that MUST be fixed before mainnet. The BurnSplitter `onlyRouter` modifier is currently a no-op — this is the critical finding.

---

## Contract 1: TechPaymentRouter.sol

### Architecture Assessment
- ✅ Uses SafeERC20 for token transfers
- ✅ Checks-effects-interactions in `payWithTech` (line 67: cumulative update before external call)
- ✅ Zero-address checks on admin functions
- ✅ Event logging for auditability
- ✅ Immutable token reference prevents hijacking

### Findings

#### 🔴 HIGH-1: `payWithTech` has no `nonReentrant` modifier
**Lines:** 50-79
**Risk:** If `BurnSplitter.split()` or the token has callback logic (ERC-777, hooks), reentrancy is possible.
**Fix:** Add `nonReentrant` from OpenZeppelin's ReentrancyGuard. Import and inherit.
```solidity
contract TechPaymentRouter is ReentrancyGuard {
    function payWithTech(...) external nonReentrant returns (...) {
```

#### 🟡 MEDIUM-1: `_getOraclePrice()` has no staleness check
**Lines:** 113-117
**Risk:** Chainlink feeds go stale if the sequencer is down (L2s) or if the feed is deprecated. A stale price means wrong discount calculations.
**Fix:** Check `updatedAtTimestamp` from `latestRoundData()` and require it's within N hours.
```solidity
(, int256 answer, , uint256 updatedAt,,) = discountCalculator.priceFeed().latestRoundData();
require(block.timestamp - updatedAt < 1 hours, "Oracle: stale price");
```

#### 🟡 MEDIUM-2: Admin functions lack access control
**Lines:** 97-109
**Risk:** `setDiscountCalculator()` and `setBurnSplitter()` are `external` with no `onlyOwner`. ANYONE can call them.
**Fix:** Add `onlyOwner` or a custom `onlyAdmin` modifier. Constructor needs an owner.
```solidity
contract TechPaymentRouter is Ownable, ReentrancyGuard {
    function setDiscountCalculator(address _addr) external onlyOwner {
```

#### 🟢 LOW-1: `previewPayment` not marked `view` on cumulativeSpent check
**Lines:** 82-93
**Impact:** Gas estimation issue for frontend. Function is correctly marked `view` though, this is cosmetic.

---

## Contract 2: DiscountCalculator.sol

### Architecture Assessment
- ✅ Immutable price feed (can't be swapped post-deploy)
- ✅ Bounded discount range (10-30% base + up to 5% loyalty)
- ✅ Linear interpolation is clean and predictable
- ✅ Fallback to MIN_DISCOUNT if SMA is zero (line 101)
- ⚠️ SMA update mechanism is completely open

### Findings

#### 🔴 HIGH-2: `updateSMA()` has no access control
**Lines:** 89-94
**Risk:** ANYONE can call `updateSMA()` and manipulate the discount curve. At line 89, the comment says "In production: restrict to keeper/admin" but it's not implemented.
**Attack scenario:** Attacker sets SMA to 1 wei → base discount always MAX (30%) → protocol loses margin.
**Fix:** Add `onlyOwner` or use Chainlink Automation (keepers) with a registry check.
```solidity
function updateSMA(uint256 newSma) external onlyOwner {
```

#### 🔴 HIGH-3: Oracle price manipulation via `latestRoundData()` without checks
**Lines:** 129-136
**Risk:** `latestRoundData()` returns 5 values but we only use `answer`. Missing checks:
1. **Staleness** — `updatedAt` timestamp could be old
2. **Round completeness** — `answeredInRound` should equal `roundId`
3. **Negative price** — Chainlink can return negative for some feeds (though rare)

**Fix:**
```solidity
function _getOraclePrice() internal view returns (uint256) {
    (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) = priceFeed.latestRoundData();

    require(answer > 0, "DiscountCalculator: invalid oracle price");
    require(answeredInRound >= roundId, "DiscountCalculator: stale round");
    require(block.timestamp - updatedAt < 1 hours, "DiscountCalculator: stale price");

    return uint256(answer) * (10 ** (18 - decimals()));
}
```

#### 🟡 MEDIUM-3: Division before multiplication in linear interpolation
**Lines:** 113-118
**Risk:** Minor precision loss. Formula: `MAX - (position * (MAX - MIN) / range)`. The division by `range` (40) happens after multiplication, which is correct for Solidity, but precision loss of up to 1 bps is possible at boundary positions.
**Impact:** <0.01% pricing error. Low priority but worth noting.
**Fix:** Use higher internal precision or round up for user-favorable discount.

#### 🟢 LOW-2: Loyalty tiers are hardcoded and irrevocable
**Lines:** 20-30
**Impact:** Cannot adjust tier thresholds or bonuses after deploy. Consider making these updatable via admin with events.

---

## Contract 3: BurnSplitter.sol

### Architecture Assessment
- ✅ Simple, clean contract
- ✅ Dead address for burn (standard pattern)
- ✅ `previewSplit` for frontend
- ⚠️ `onlyRouter` modifier is completely broken

### Findings

#### 🔴 CRITICAL-1: `onlyRouter()` modifier does nothing
**Lines:** 39-43
```solidity
modifier onlyRouter() {
    // In production: restrict to TechPaymentRouter
    // For now, anyone can call (testing)
    _;
}
```
**Risk:** `split()` is callable by ANY address. An attacker can:
1. Call `split(victim, amount)` — pulls tokens from victim to BurnSplitter
2. If victim approved BurnSplitter (which the test does), attacker splits arbitrary amounts

**Fix:** This MUST be fixed before any deployment.
```solidity
address public router;
modifier onlyRouter() {
    require(msg.sender == router, "BurnSplitter: only router");
    _;
}
constructor(address _techToken, address _treasury, address _router) {
    router = _router;
}
```

#### 🟡 MEDIUM-4: `setTreasury()` has no access control
**Lines:** 78-83
**Risk:** Anyone can redirect treasury funds.
**Fix:** Add `onlyOwner`.

#### 🟢 LOW-3: No reentrancy guard on `split()`
**Lines:** 48-68
**Impact:** If the token has hooks (ERC-777), reentrancy through `safeTransferFrom` is possible. Mitigated by SafeERC20, but adding `nonReentrant` is cheap insurance.

---

## Contract 4: AgentEscrow.sol

### Architecture Assessment
- ✅ Excellent use of EIP-712 for signature validation
- ✅ ReentrancyGuard on all state-changing functions
- ✅ Custom errors (gas efficient)
- ✅ Proper CEI pattern throughout
- ✅ Immutable references (USDC, AI_VALIDATOR)
- ✅ Pull-over-push pattern (no forced transfers)

### Findings

#### 🔴 HIGH-4: `ecrecover` is malleable
**Lines:** 176
**Risk:** `ecrecover` accepts both `s` values (high and low). An attacker could submit a different but valid signature.
**Fix:** Use OpenZeppelin's `ECDSA.recover()` which handles malleability:
```solidity
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
// Then:
address signer = ECDSA.recover(digest, abi.encodePacked(r, s, v));
```

#### 🟡 MEDIUM-5: No validation expiry on signatures
**Lines:** 169-174
**Risk:** The EIP-712 signature includes `block.timestamp` but the contract doesn't enforce a max age. A validator could sign a message and it could be submitted much later.
**Fix:** Add a signature validity window:
```solidity
uint256 constant SIGNATURE_VALIDITY = 1 hours;
// In the struct hash, use a passed-in timestamp, not block.timestamp
require(block.timestamp - sigTimestamp <= SIGNATURE_VALIDITY, "Signature expired");
```

#### 🟢 LOW-4: `refund()` allows refund during `Validated` state
**Lines:** 195-212
**Impact:** If validator signs but `validateAndRelease()` hasn't been called yet, buyer could refund during this window. Consider blocking refunds in `Validated` state.

#### 🟢 LOW-5: No events for state transitions from `Created` to `Completed`
**Lines:** 139-150
**Impact:** Minor — `EscrowCompleted` is emitted, but the state machine could be more granular with events for each transition.

---

## Oracle-Specific Analysis (Chainlink Focus)

Since you're studying Chainlink at Cyfrin — here's what matters for our setup:

### Current Oracle Usage
- **DiscountCalculator** uses `IAggregatorV3Interface` (Chainlink-compatible)
- Price feed: configured at deploy time, immutable
- SMA: manually updated (should be Chainlink Automation or keeper)

### Chainlink Hardening Checklist
| Check | TechPaymentRouter | DiscountCalculator |
|-------|-------------------|-------------------|
| Check `answeredInRound >= roundId` | ❌ | ❌ |
| Check `updatedAt` staleness | ❌ | ❌ |
| Verify feed is not deprecated | ❌ | ❌ |
| Handle negative prices | N/A | ⚠️ partial (`answer > 0`) |
| L2 sequencer uptime check | ❌ | ❌ |

### Recommendations for Production
1. **Use Chainlink Automation** for SMA updates instead of open `updateSMA()`
2. **Add a Sequencer Uptime Feed** if deploying to Arbitrum/Base/Optimism
3. **Wrap oracle calls in a PriceFeedAdapter** contract that handles all edge cases in one place
4. **Consider Chainlink Functions** for off-chain computation if loyalty tiers get complex

---

## Test Coverage Analysis

Current tests cover:
- ✅ Discount at various SMA positions
- ✅ Loyalty tiers (Silver, Gold, Diamond)
- ✅ Absolute cap enforcement
- ✅ Burn/treasury split ratios
- ✅ Full payment flow end-to-end
- ✅ Price movement impact on payments
- ✅ Zero payment revert
- ✅ Cumulative tracking
- ✅ Dust handling

Missing tests:
- ❌ Reentrancy attack simulation
- ❌ Fuzz testing on discount bounds
- ❌ Oracle staleness scenarios
- ❌ Admin access control (calling from non-owner)
- ❌ Signature malleability on AgentEscrow
- ❌ Edge case: max uint256 payment amounts
- ❌ Edge case: oracle returning 0 or negative

---

## Priority Fix List (Deployment Blockers)

1. **CRITICAL:** Fix BurnSplitter `onlyRouter` — add real access control
2. **HIGH:** Add `nonReentrant` to `payWithTech()`
3. **HIGH:** Add `onlyOwner` to all admin functions (Router + BurnSplitter)
4. **HIGH:** Fix `updateSMA()` access control
5. **HIGH:** Add oracle staleness + round completeness checks
6. **HIGH:** Replace `ecrecover` with `ECDSA.recover()` in AgentEscrow
7. **MEDIUM:** Add signature validity window to AgentEscrow

---

## Next Steps
- [ ] DMOB technical review (cross-reference with Cyfrin best practices)
- [ ] Run Foundry fuzz tests on discount boundaries
- [ ] Deploy to testnet with real Chainlink feeds (Base Sepolia or Fuji)
- [ ] Consider Slither/Mythril automated analysis pass
- [ ] External audit if deploying with real TVL

---

*Audit conducted by YoYo — Strategies Department*
*Awaiting DMOB peer review in Green Room*
*2026-04-21*
