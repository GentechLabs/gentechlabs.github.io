# 🔍 Smart Contract Security Checklist

Use this template for every audit pass. Copy to a new file: `Audit-[RepoName]-[Date].md`

---

## Pre-Audit

- [ ] `forge build` — zero warnings
- [ ] `forge test` — all pass, no flaky tests
- [ ] `forge coverage` — note % and gaps
- [ ] Dependencies pinned (no floating versions)

## Access Control

- [ ] Owner/admin roles properly gated
- [ ] `onlyOwner` / `AccessControl` where needed
- [ ] No unguarded `mint` / `burn` / `withdraw`
- [ ] Multi-sig considered for admin functions

## Reentrancy

- [ ] Checks-Effects-Interactions pattern followed
- [ ] External calls after state changes
- [ ] ReentrancyGuard on critical functions
- [ ] No cross-function reentrancy risk

## Oracle Security (Chainlink Focus)

- [ ] Price feed staleness check (`updatedAt` within tolerance)
- [ ] Fallback mechanism if oracle goes down
- [ ] No single-source dependency for critical pricing
- [ ] Sequencer uptime check (L2 deployments)
- [ ] VRF request fulfillment handling + timeout

## Token Logic

- [ ] Transfer hooks don't break accounting
- [ ] Fee-on-transfer tokens handled
- [ ] No decimal mismatches in calculations
- [ ] Flash loan resistance if applicable

## Upgradeability (if proxy)

- [ ] Storage layout collision check
- [ ] initializer modifier on implementation
- [ ] UUPS vs Transparent — correct pattern
- [ ] Upgrade timelock / governance

## Economic / MEV

- [ ] Front-running vectors identified
- [ ] Sandwich attack resistance
- [ ] Flashbot / private mempool considerations
- [ ] Slippage protection in swaps

## Gas & Efficiency

- [ ] Custom errors instead of `require` strings
- [ ] Pack storage variables
- [ ] Use `unchecked` where overflow-proof
- [ ] Avoid unnecessary SSTORE / SLOAD

## Deployment Safety

- [ ] Constructor params validated
- [ ] Contract verified on explorer
- [ ] Emergency pause mechanism exists
- [ ] Funds recovery path exists

## Final

- [ ] All findings classified: Critical / High / Medium / Low / Info
- [ ] Remediation committed + re-tested
- [ ] Report saved to `Labs/Security-Analysis/`
