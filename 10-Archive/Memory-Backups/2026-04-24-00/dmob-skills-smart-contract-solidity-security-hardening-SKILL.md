---
name: solidity-security-hardening
description: Systematic approach to fixing security audit findings in Solidity contracts — batch hardening, access control, reentrancy, oracle hardening, and ECDSA signature fixes.
category: smart-contract
triggers:
  - security audit fix
  - contract hardening
  - openzeppelin security
  - oracle staleness check
  - ecrecover malleability
  - reentrancy guard
  - access control fix
---

# Solidity Security Hardening Playbook

Systematic approach to batch-fixing security audit findings. Based on hardening the TechPaymentRouter + BurnSplitter + DiscountCalculator + AgentEscrow contracts (Apr 2026).

## Fix Order (By Severity)

Always fix in this order — higher severity findings can mask lower ones:

1. **CRITICAL** — Access control no-ops (anyone can call privileged functions)
2. **HIGH** — Reentrancy, oracle manipulation, signature malleability
3. **MEDIUM** — Missing admin access control, oracle staleness
4. **LOW** — Cosmetic, event granularity, hardcoded constants

## Pattern 1: Access Control No-Op → Real Check

**Before (CRITICAL):**
```solidity
modifier onlyRouter() {
    // In production: restrict to TechPaymentRouter
    // For now, anyone can call (testing)
    _;
}
```

**After:**
```solidity
address public router;

modifier onlyRouter() {
    require(msg.sender == router, "Contract: only router");
    _;
}

function setRouter(address newRouter) external onlyRouter {
    require(newRouter != address(0), "Contract: zero address");
    router = newRouter;
}
```

**Rule:** Never deploy with commented-out access control. Use a proper state variable + require.

## Pattern 2: Reentrancy Guard

**Before (HIGH):**
```solidity
function payWithTech(...) external returns (...) {
    // external calls without protection
}
```

**After:**
```solidity
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract TechPaymentRouter is ReentrancyGuard {
    function payWithTech(...) external nonReentrant returns (...) {
        // safe — reentrancy blocked
    }
}
```

**Cost:** ~2,500 gas per call. Cheap insurance.

## Pattern 3: Ownable Admin Functions

**Before (MEDIUM):**
```solidity
function setDiscountCalculator(address _addr) external {
    require(_addr != address(0));
    discountCalculator = DiscountCalculator(_addr);
}
```

**After:**
```solidity
import "@openzeppelin/contracts/access/Ownable.sol";

contract TechPaymentRouter is Ownable {
    constructor(...) Ownable(msg.sender) { ... }

    function setDiscountCalculator(address _addr) external onlyOwner {
        require(_addr != address(0));
        discountCalculator = DiscountCalculator(_addr);
    }
}
```

**Rule:** Every setter/admin function needs `onlyOwner`. No exceptions.

## Pattern 4: Oracle Staleness + Round Completeness

**Before (HIGH):**
```solidity
function _getOraclePrice() internal view returns (uint256) {
    (, int256 answer,,,) = priceFeed.latestRoundData();
    require(answer > 0, "Invalid price");
    return uint256(answer) * (10 ** (18 - decimals));
}
```

**After:**
```solidity
function _getOraclePrice() internal view returns (uint256) {
    (
        uint80 roundId,
        int256 answer,
        ,
        uint256 updatedAt,
        uint80 answeredInRound
    ) = priceFeed.latestRoundData();

    require(answer > 0, "Oracle: invalid price");
    require(answeredInRound >= roundId, "Oracle: stale round");
    require(block.timestamp - updatedAt < 1 hours, "Oracle: stale price");

    return uint256(answer) * (10 ** (18 - decimals));
}
```

**Why three checks:**
- `answer > 0` — prevents negative/zero prices
- `answeredInRound >= roundId` — ensures round completed (not in-progress)
- `updatedAt < 1 hours` — prevents stale prices (L2 sequencer down, feed deprecated)

**For L2s (Base/Arbitrum/Optimism):** Also add sequencer uptime check from Chainlink docs.

## Pattern 5: ECDSA Signature Malleability Fix

**Before (HIGH):**
```solidity
function validateAndRelease(
    uint256 _escrowId,
    uint8 v,
    bytes32 r,
    bytes32 s
) external {
    address signer = ecrecover(digest, v, r, s);
    if (signer != validator) revert InvalidSignature();
}
```

**After:**
```solidity
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

function validateAndRelease(
    uint256 _escrowId,
    bytes calldata _signature
) external nonReentrant {
    // ECDSA.recover handles malleability (rejects high-s values)
    address signer = ECDSA.recover(digest, _signature);
    if (signer != validator) revert InvalidSignature();

    // Prevent signature reuse
    bytes32 signatureHash = keccak256(_signature);
    if (usedSignatures[signatureHash]) revert InvalidSignature();
    usedSignatures[signatureHash] = true;
}
```

**Why `bytes calldata` instead of `(v, r, s)`:** OpenZeppelin's `ECDSA.recover()` takes `bytes` signature (65 bytes: r+s+v). Cleaner API and handles edge cases automatically.

**Add replay protection:**
```solidity
mapping(bytes32 => bool) public usedSignatures;
```

## Pattern 6: Circular Dependency Resolution

When Contract A needs Contract B's address and vice versa:

1. Deploy "owned" contract with temporary owner (deployer/test)
2. Deploy "owner" contract with owned contract's address
3. Wire: call `setRouter`/`setOwner` from the temporary owner

See `foundry-testing-patterns` skill — Pitfall 13 for full example.

## Test Adaptation Checklist

After hardening, update tests:

- [ ] All direct calls to hardened functions need `vm.prank(authorizedAddress)`
- [ ] Constructor changes may require updating `setUp()` deployment
- [ ] Add tests for access control: `vm.expectRevert` when unauthorized calls
- [ ] Add tests for reentrancy: simulate reentrant calls
- [ ] Add tests for oracle staleness: mock stale price feeds

## Verification Command

```bash
# Compile + run all tests
cd /path/to/project && ~/.foundry/bin/forge test -vv

# Run specific test after a fix
forge test --matchTest test_burnSplit -vvv

# Full trace for debugging
forge test --matchTest testName -vvvv
```

## Quick Reference

| Finding | OZ Import | Fix |
|---------|-----------|-----|
| Reentrancy | `ReentrancyGuard` | `nonReentrant` modifier |
| Access control | `Ownable` | `onlyOwner` modifier |
| Signature malleability | `ECDSA` | `ECDSA.recover()` |
| Oracle staleness | None (manual) | Check `updatedAt`, `answeredInRound` |
| Integer overflow | Built-in (0.8+) | Automatic |
| Missing zero-address check | None (manual) | `require(_addr != address(0))` |
