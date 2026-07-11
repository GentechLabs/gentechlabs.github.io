# Kite AI / GoKite - Known Issues from Halborn Audits

## Overview
This document contains all known findings from previous Halborn security audits for Kite AI / GoKite. These findings are **EXCLUDED** from the Code4rena bug bounty program as they are considered known issues.

---

## Audit Reports Summary

### 1. GoKite Contracts Audit (2025)
- **URL**: https://www.halborn.com/audits/kite/gokite-contracts-633ec7
- **Date**: September 22-25, 2025
- **Total Findings**: 6 (1 Low, 5 Informational)
- **Status**: 100% Addressed

### 2. Kite Token Audit (2025)
- **URL**: https://www.halborn.com/audits/kite/kite-031103
- **Date**: October 7, 2025
- **Total Findings**: 1 (1 High)
- **Status**: 100% Addressed

### 3. KiteNativeOFTAdapter Audit (2026)
- **URL**: https://www.halborn.com/audits/kite/kitenativeoftadapter-a02205
- **Date**: March 2, 2026
- **Total Findings**: 8 (4 Low, 4 Informational)
- **Status**: 100% Addressed

### 4. Staking & Rewards Contracts Audit (2026)
- **URL**: https://www.halborn.com/audits/kite/staking--rewards-contracts-2a1577
- **Date**: January 13-19, 2026
- **Total Findings**: 9 (2 Critical, 2 Medium, 2 Low, 3 Informational)
- **Status**: 100% Addressed

---

## Detailed Findings by Audit

### Audit 1: GoKite Contracts (Sep 2025)
**Scope**: SubnetRegistry, GokiteAccount, KiteAirdrop contracts

| # | Finding | Severity | Contract | Status | Remediation |
|---|---------|----------|----------|--------|-------------|
| 7.1 | Subnets can reassign any user to any subnet or arbitrary address | Low | SubnetRegistry | SOLVED | [8f7abcd](https://github.com/gokite-ai/contracts-external/commit/8f7abcd98f38d87201ee0cc910c6defdaffb46f6) |
| 7.2 | Insufficient validation on airdrop claim deadline | Informational | KiteAirdrop | SOLVED | [734f869](https://github.com/gokite-ai/contracts-external/commit/734f869a77329706326dc72ae559bb93b5027cf9) |
| 7.3 | Missing two-step process for ownership transfer | Informational | GokiteAccount | ACKNOWLEDGED | N/A |
| 7.4 | Duplicate event emission in pause/unpause functions | Informational | KiteAirdrop | SOLVED | [bb1add4](https://github.com/gokite-ai/contracts-external/commit/bb1add4cbc66639a74dd7a68cfb0aca7f5bc82bc) |
| 7.5 | Unchecked ERC20 transfer return value | Informational | Subnet | ACKNOWLEDGED | N/A |
| 7.6 | Unsafe token transfer pattern during airdrop claim | Informational | KiteAirdrop | ACKNOWLEDGED | N/A |

### Audit 2: Kite Token (Oct 2025)
**Scope**: KiteOFTWithPausable.sol (ERC-20 token)

| # | Finding | Severity | Contract | Status | Remediation |
|---|---------|----------|----------|--------|-------------|
| 7.1 | Missing pause and unpause function in contract | High | KiteOFTWithPausable | SOLVED | [db3fbba](https://github.com/gokite-ai/contracts-external/commit/db3fbba872b42d9d1d3d2e9ff5649852e9a35525) |

### Audit 3: KiteNativeOFTAdapter (Mar 2026)
**Scope**: KiteNativeOFTAdapter.sol (Cross-chain bridging)

| # | Finding | Severity | Contract | Status | Remediation |
|---|---------|----------|----------|--------|-------------|
| 7.1 | Daily outbound limit overcounts bridged volume by using user input instead of actual debited amount | Low | KiteNativeOFTAdapter | SOLVED | [fea6512](https://github.com/gokite-ai/contracts-external/commit/fea651200c2b6446638237fefb11bf4fc9a14204) |
| 7.2 | Incorrect initial oldLimit value emitted in constructor event | Low | KiteNativeOFTAdapter | SOLVED | [04eae2a](https://github.com/gokite-ai/contracts-external/commit/04eae2a2a8b511804c89d3f6367c806e8f9b1e12) |
| 7.3 | Unsafe single-step ownership transfer | Low | KiteNativeOFTAdapter | RISK ACCEPTED | N/A |
| 7.4 | Reducing daily limit below current usage causes unintended underflow revert | Low | KiteNativeOFTAdapter | SOLVED | [6e2d086](https://github.com/gokite-ai/contracts-external/commit/6e2d086a11d53e8b43368de8f7f9ed296ee64596) |
| 7.5 | Deposit cap can be bypassed via direct transfers | Informational | KiteNativeOFTAdapter | ACKNOWLEDGED | N/A |
| 7.6 | depositToLock not restricted during pause | Informational | KiteNativeOFTAdapter | ACKNOWLEDGED | N/A |
| 7.7 | Missing validation for daily outbound limit | Informational | KiteNativeOFTAdapter | ACKNOWLEDGED | N/A |
| 7.8 | Missing validation in admin configuration functions | Informational | KiteNativeOFTAdapter | ACKNOWLEDGED | N/A |

### Audit 4: Staking & Rewards (Jan 2026)
**Scope**: StakingManager, KiteStakingManager, RewardVault contracts

| # | Finding | Severity | Contract | Status | Remediation |
|---|---------|----------|----------|--------|-------------|
| 7.1 | Cross-function reentrancy allowing drainage of the reward vault | **CRITICAL** | StakingManager | SOLVED | [82161fe](https://github.com/gokite-ai/contracts-external/commit/82161fec51af1ec87be29a7fb8d3d4a0f04037b5) |
| 7.2 | Delegators can claim excessive rewards due to incorrect lastClaimUptime initialization | **CRITICAL** | StakingManager | SOLVED | [038f8b0](https://github.com/gokite-ai/contracts-external/commit/038f8b0960f726f14ecf282a9e9176dda5c906df) |
| 7.3 | Cumulative uptime calculation penalizes delegators for validator's post-claim downtime | Medium | StakingManager | SOLVED | [4bfa472](https://github.com/gokite-ai/contracts-external/commit/4bfa472d5b63fcb662035ebdb6b7c4d023e4068d) |
| 7.4 | Stale uptime data benefits delegators during registration | Medium | StakingManager | SOLVED | [10dc399](https://github.com/gokite-ai/contracts-external/commit/10dc39956563aa854d6568f564a87dee249eea7e) |
| 7.5 | Missing input validation in reward calculator | Low | FixedAPRRewardCalculator | SOLVED | [bbdcb35](https://github.com/gokite-ai/contracts-external/commit/bbdcb35b5b85196fda9141dc048f49ac28ecf198) |
| 7.6 | Unused error definitions | Low | StakingManager | SOLVED | [3c1bc94](https://github.com/gokite-ai/contracts-external/commit/3c1bc9438b669bc045768eb0d1c583b531daa1f2) |
| 7.7 | Missing ownership transfer security | Informational | RewardVault, KiteStakingManager | SOLVED | [b750ba7](https://github.com/gokite-ai/contracts-external/commit/b750ba7c16f77d22a3ba2293a6a0ed2adc649df1) |
| 7.8 | Outdated compiler pragma version | Informational | StakingManager | ACKNOWLEDGED | N/A |
| 7.9 | Minimum stake duration change breaks existing delegators | Informational | StakingManager | ACKNOWLEDGED | N/A |

---

## Key Remediation Commits

### Critical Fixes
- **Reentrancy Protection**: [82161fe](https://github.com/gokite-ai/contracts-external/commit/82161fec51af1ec87be29a7fb8d3d4a0f04037b5) - Added nonReentrant modifier and CEI pattern
- **Uptime Initialization**: [038f8b0](https://github.com/gokite-ai/contracts-external/commit/038f8b0960f726f14ecf282a9e9176dda5c906df) - Initialize lastClaimUptimeSeconds during registration

### High/medium Fixes
- **Pause Functionality**: [db3fbba](https://github.com/gokite-ai/contracts-external/commit/db3fbba872b42d9d1d3d2e9ff5649852e9a35525) - Added pause/unpause functions to KITE token
- **Linear Reward Model**: [4bfa472](https://github.com/gokite-ai/contracts-external/commit/4bfa472d5b63fcb662035ebdb6b7c4d023e4068d) - Changed from threshold-based to linear reward model
- **Uptime Updates**: [10dc399](https://github.com/gokite-ai/contracts-external/commit/10dc39956563aa854d6568f564a87dee249eea7e) - Update uptime in completeDelegatorRegistration()

---

## Bounty Exclusion Criteria

Per the Code4rena bounty page, the following are **EXCLUDED** from rewards:
1. All issues submitted by wardens to the Kite AI bounty (once reviewed by sponsors)
2. Every issue opened in the repo
3. Closed PRs
4. Previous contests and audits (including all findings listed above)
5. Any known issues that the project is aware of but has consciously decided not to "fix"

---

## Additional Resources

- **Code4rena Bounty**: https://code4rena.com/bounties/kite-ai
- **GitHub Bounty Repo**: https://github.com/code-423n4/Kite-AI-bug-bounty
- **Kite Docs**: https://docs.gokite.ai/
- **Smart Contracts List**: https://docs.gokite.ai/kite-chain/3-developing/smart-contracts-list
- **Block Explorer**: https://kitescan.ai

---

*Last Updated: May 12, 2026*
*Source: Halborn Security Audits*
