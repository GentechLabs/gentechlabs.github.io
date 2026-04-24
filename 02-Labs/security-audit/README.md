# 🔒 Gentech Labs — Security Audit

Self-assessment framework for all Gentech smart contracts before hackathon submission or production deployment.

## Scope

| Contract | Location | Status |
|----------|----------|--------|
| TechPaymentRouter | `02-Labs/tech-payment-router/` | ⏳ Pending |
| TECHToken (burn logic) | `03-Projects/tech-burn-test/` | ⏳ Pending |

## Audit Checklist

### 1. Access Control
- [ ] Owner/admin functions properly gated
- [ ] No unprotected `onlyOwner` bypasses
- [ ] Role-based access where needed (OpenZeppelin AccessControl)

### 2. Reentrancy
- [ ] Checks-Effects-Interactions pattern followed
- [ ] ReentrancyGuard on external calls
- [ ] No cross-function reentrancy vectors

### 3. Oracle / Price Feed Security
- [ ] Chainlink price feed freshness check (stale data protection)
- [ ] Fallback behavior if oracle returns 0 or reverts
- [ ] No hardcoded prices as production values
- [ ] Sequencer uptime check (L2 deployments)

### 4. Input Validation
- [ ] Zero-address checks on all address params
- [ ] Zero-amount checks on transfers
- [ ] Array length validation for batch operations

### 5. Integer Arithmetic
- [ ] Solidity 0.8+ overflow protection (or SafeMath if older)
- [ ] Division precision loss handled
- [ ] No unsafe casting (uint256 → uint128, etc.)

### 6. Token Handling
- [ ] Safe ERC20 transfer patterns (OpenZeppelin SafeERC20)
- [ ] Fee-on-transfer token compatibility
- [ ] Revert vs. silent failure on transferFrom
- [ ] Allowance management (infinite approval risks)

### 7. Upgradeability (if applicable)
- [ ] Storage layout collision protection
- [ ] Initializer called exactly once
- [ ] UUPS/Transparent proxy patterns correct

### 8. Economic / Game Theory
- [ ] Flash loan attack vectors
- [ ] Sandwich attack exposure
- [ ] MEV extraction risk on swaps
- [ ] Fee manipulation possibilities

### 9. Gas & DoS
- [ ] No unbounded loops over user-controlled arrays
- [ ] Gas griefing on external calls
- [ ] Block gas limit awareness

### 10. Chainlink-Specific Checks
Since Jordan is working through Cyfrin's Chainlink course, these are priority:
- [ ] AggregatorV3Interface usage correct
- [ ] `latestRoundData()` return values checked (price, roundId, updatedAt)
- [ ] Stale price threshold configured (e.g., >1hr = reject)
- [ ] Heartbeat monitoring per chain
- [ ] LINK token handling if applicable

## How to Use

1. Pick a contract from the Scope table above
2. Go through each checklist section
3. Document findings in `[contract-name]-findings.md`
4. Categorize: 🔴 Critical | 🟡 Medium | 🟢 Low | ⚪ Info
5. Fix 🔴 and 🟡 before any deployment

## References

- [Cyfrin Updraft — Chainlink Course](https://updraft.cyfrin.io/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/5.x/)
- [SWC Registry (Smart Contract Weaknesses)](https://swcregistry.io/)
- [DeFi Security Summit Resources](https://github.com/defi-security-summit)
- [Chainlink Best Practices](https://docs.chain.link/best-practices)
