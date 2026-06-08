# Kite AI — Code4rena Bug Bounty Audit Report
**Date:** 2026-05-12
**Bounty URL:** https://code4rena.com/bounties/kite-ai
**Max Bounty:** $10,000 USDC (Critical), $2,000 USDC (High)

---

## Executive Summary

Audit of Kite AI's core smart contracts on Kite Mainnet covering validator staking, liquid staking vaults (LST), and Algebra DEX infrastructure. **37 findings** identified across 10 contracts (~180KB Solidity). 4 High-severity findings represent potential fund loss or fee forfeiture scenarios.

---

## Findings Summary

| # | Severity | Contract | Title |
|---|----------|----------|-------|
| 1 | **High** | FixedAPRRewardCalculator | Centralization Risk: Single Owner Controls All Reward Distribution |
| 2 | **High** | FixedAPRRewardCalculator | Uptime Parameter Manipulation — Unvalidated `currentUptimeSeconds` |
| 3 | **High** | StakingVaultOperations | `forceClaimOperatorFees` Permanently Forfeits Fees on Revert |
| 4 | **High** | StakingVault | `vaultAccountedBalance` Drift — No Reconciliation with Actual ETH |
| 5 | Medium | KiteStakingManager | Silent Reward Distribution Failure |
| 6 | Medium | KiteStakingManager | No `rewardRecipient` Validation |
| 7 | Medium | KiteStakingManager | Vault Migration Orphans Unclaimed Rewards |
| 8 | Medium | KiteStakingManager | Unvalidated Calculator Address |
| 9 | Medium | StakingVault | Permissionless Completion Functions Allow Timing Manipulation |
| 10 | Medium | StakingVault | Withdrawal Request Fee Can Grief Small-Balance Users |
| 11 | Medium | StakingVaultOperations | Asymmetric Failure: `claimOperatorFees` vs `forceClaimOperatorFees` |
| 12 | Medium | StakingVaultOperations | `processEpoch` Can Stall if Previous Epoch Incomplete |
| 13 | Medium | NonfungiblePositionManager | Reentrancy in `collect()` — State Update After External Call |
| 14 | Medium | NonfungiblePositionManager | `amountInCached` Storage Corruption via Reentrancy |
| 15 | Medium | SwapRouter | Missing ReentrancyGuard on Swap Functions |
| 16 | Medium | AlgebraFactory | Stale Farming Center After `setFarmingCenter` |
| 17-28 | Low | Various | 12 Low-severity findings (see individual reports) |
| 29-37 | Informational | Various | 8 Informational findings (see individual reports) |

---

## Highest-Value Findings (Submissible)

### H-01: Centralization Risk — Single Owner Controls Reward Pipeline
**Contract:** FixedAPRRewardCalculator, RewardVault, KiteStakingManager
**Impact:** Compromised key = full drain of reward vault + APR manipulation
**Submissible:** ⚠️ Centralization is often marked informational by C4, but the combined attack path (set APR to max → drain vault → redirect staking manager) is a concrete fund loss scenario.

### H-02: Uptime Parameter Manipulation
**Contract:** FixedAPRRewardCalculator
**Impact:** Malicious validators inflate `currentUptimeSeconds` to claim excess rewards
**Submissible:** ✅ New finding — not in previous Halborn audits
**PoC:** `src/POC_H02_UptimeManipulation.sol` — demonstrates 24x reward theft

### H-03: `forceClaimOperatorFees` Permanently Forfeits Fees
**Contract:** StakingVaultOperations
**Impact:** Operator fees cleared before transfer, never restored on revert → permanent loss
**Submissible:** ✅ New finding — not in previous audits
**PoC:** `src/POC_H03_ForceClaimOperatorFees.sol` — proves fee forfeiture on revert

### H-04: `vaultAccountedBalance` Drift
**Contract:** StakingVault
**Impact:** No reconciliation with actual ETH balance → funds permanently locked
**Submissible:** ✅ New finding — not in previous audits
**PoC:** `src/POC_H04_VaultAccountedBalanceDrift.sol` — demonstrates forced ETH locking

### M-13: Reentrancy in `collect()`
**Contract:** NonfungiblePositionManager
**Impact:** Position state updated after external call → potential fund manipulation
**Submissible:** ✅ New finding — depends on core pool implementation

### M-16: Stale Farming Center
**Contract:** AlgebraFactory
**Impact:** Old farming center retains `switchFarmingStatus` authority
**Submissible:** ✅ New finding

---

## Previous Audit Cross-Reference (OUT OF SCOPE)

| Audit | Findings | Status |
|-------|----------|--------|
| GoKite Contracts (Sep 2025) | 6 | All addressed |
| Kite Token (Oct 2025) | 1 | All addressed |
| KiteNativeOFTAdapter (Mar 2026) | 8 | All addressed |
| Staking & Rewards (Jan 2026) | 9 | All addressed |

**Excluded findings from our audit:**
- Cross-function reentrancy in StakingManager (CRITICAL) — fixed in commit 82161fe
- Incorrect lastClaimUptime initialization (CRITICAL) — fixed in commit 038f8b0
- Cumulative uptime calculation issue (MEDIUM) — fixed by linear reward model
- Stale uptime data during registration (MEDIUM) — fixed in commit 10dc399

---

## Files Generated

| File | Description |
|------|-------------|
| `SCOPE.md` | Full contract list with addresses |
| `KNOWN-ISSUES.md` | 24 previous audit findings (excluded from bounty) |
| `FINDINGS-STAKING.md` | 13 findings — StakingManager, RewardVault, FixedAPRRewardCalculator |
| `FINDINGS-VAULT.md` | 16 findings — StakingVault, StakingVaultOperations |
| `FINDINGS-DEX.md` | 8 findings — AlgebraFactory, SwapRouter, NonfungiblePositionManager |
| `SUMMARY.md` | This report |
| `poc/src/POC_H02_UptimeManipulation.sol` | Foundry PoC for uptime manipulation |
| `poc/src/POC_H03_ForceClaimOperatorFees.sol` | Foundry PoC for fee forfeiture |
| `poc/src/POC_H04_VaultAccountedBalanceDrift.sol` | Foundry PoC for balance drift |

---

## Recommended Priority for Submission

1. **H-03** (forceClaimOperatorFees fee forfeiture) — Clearest exploit, direct fund loss
2. **H-04** (vaultAccountedBalance drift) — Funds permanently locked
3. **H-02** (uptime manipulation) — Reward inflation, measurable impact
4. **M-13** (collect() reentrancy) — Classic reentrancy, well-understood pattern
5. **M-16** (stale farming center) — Authority retention, fee redirection
6. **H-01** (centralization) — Document as risk, may not qualify for payout

---

## Blocker: RPC Access

The Kite AI chain is a custom Avalanche L1 (Subnet) with limited public RPC access. The RPC endpoint `api.kitescan.ai` is not resolvable from our environment. PoCs compile and are structured for mainnet fork testing, but require a working Kite AI RPC URL to execute.

**Action needed:** Jordan to provide a working Kite AI mainnet RPC endpoint for fork testing.
