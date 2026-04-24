# Auto-Rebalance Gas Abstraction — Spec Draft

**Date:** April 21, 2026
**Author:** DMOB (Labs)
**Status:** Draft v1 — Pending YoYo financial review

---

## 1. Overview

Gas-subsidized LP management on TraderJoe v2.2 (AVAX/USDC). User deposits once, system handles rebalancing + gas automatically. Zero manual intervention.

## 2. User Flow

```
User deposits USDC/AVAX
    ↓
Contract receives deposit
    ↓
Split: LP deployment (98%) + Gas reserve (2%)
    ↓
Deploy LP tokens to TraderJoe v2.2 range [9.00, 9.40]
    ↓
[Cron/Oracle monitors price range]
    ↓
Price exits range → trigger rebalance
    ↓
Contract auto-executes:
  1. Remove liquidity from old range
  2. Swap tokens to rebalance ratio
  3. Re-deposit to new range
  ↓
Gas deducted from reserve pool
    ↓
User LP position stays active — no action needed
```

## 3. Contract Architecture

### 3.1 Core Contracts

| Contract | Purpose |
|----------|---------|
| `GasAbstractionVault` | Holds user deposits, manages gas reserve split |
| `LPManager` | Interfaces with TraderJoe v2.2 — deposit, withdraw, rebalance |
| `RebalanceExecutor` | Permissioned keeper call — checks range, executes rebalance |
| `PriceOracle` | Monitors AVAX/USDC price, determines range status |

### 3.2 State Variables

```solidity
// GasAbstractionVault
mapping(address => uint256) public userDeposits;
mapping(address => uint256) public gasReserve;
uint256 public totalGasReserve;
uint256 public constant GAS_RESERVE_BPS = 200; // 2%
uint256 public constant MIN_GAS_RESERVE = 0.5 * 1e6; // 0.5 USDC floor

// LPManager
address public lpToken; // TraderJoe v2.2 LP
int24 public tickLower;
int24 public tickUpper;
uint256 public totalLPTokens;

// RebalanceExecutor
address public keeper; // authorized keeper (cron bot)
uint256 public lastRebalanceTimestamp;
uint256 public constant REBALANCE_COOLDOWN = 1 hours;
```

### 3.3 Core Functions

```solidity
// GasAbstractionVault
function deposit(uint256 amount) external;           // User deposits USDC
function withdraw(uint256 amount) external;           // User withdraws (burns LP + returns reserve)
function getGasReserve(address user) external view returns (uint256);

// LPManager
function deployLiquidity(uint256 amount0, uint256 amount1, int24 lower, int24 upper) external;
function removeLiquidity(uint256 lpAmount) external;
function rebalance(int24 newLower, int24 newUpper) external;

// RebalanceExecutor
function checkAndRebalance() external;                // Keeper-only, checks range + executes
function estimateRebalanceCost() external view returns (uint256);

// PriceOracle
function isOutOfRange() external view returns (bool);
function getCurrentTick() external view returns (int24);
function getOptimalRange() external view returns (int24 lower, int24 upper);
```

## 4. Access Control

| Role | Permissions |
|------|-------------|
| **User** | deposit(), withdraw() |
| **Keeper** | checkAndRebalance() — permissioned, can be decentralized later |
| **Admin** | setKeeper(), updateOracle(), pause() |
| **Emergency** | Emergency withdraw — user can always pull funds |

## 5. Security Considerations

### 5.1 Critical Checks
- [ ] checks-effects-interactions on all external calls
- [ ] ReentrancyGuard on deposit/withdraw/rebalance
- [ ] Slippage protection on swaps during rebalance
- [ ] Minimum gas reserve check — pause rebalancing if reserve too low
- [ ] Cooldown between rebalances (prevent spam drain)

### 5.2 Edge Cases
- Reserve depleted → pause rebalancing, emit event, notify user
- LP token price manipulation → use TWAP oracle, not spot
- Keeper goes offline → user can trigger manual rebalance or withdraw
- Extreme price movement → emergency withdraw reverts to stablecoin

### 5.3 Oracle Risks
- Single oracle = single point of failure
- Recommended: Chainlink AVAX/USDC feed + TWAP from TraderJoe pool
- Dispute mechanism for stale prices

## 6. Gas Budget Model (Pending YoYo Review)

| Operation | Estimated Gas | Cost @ 25 gwei AVAX |
|-----------|---------------|----------------------|
| Remove liquidity | ~200k gas | ~$0.05 |
| Swap (rebalance) | ~150k gas | ~$0.04 |
| Re-deposit LP | ~250k gas | ~$0.06 |
| **Total per rebalance** | **~600k gas** | **~$0.15** |
| **2% reserve on $100 deposit** | | **$2.00** |
| **Rebalances covered per $100** | | **~13 rebalances** |

⚠️ These are rough estimates. YoYo needs to validate against current AVAX gas prices and LP fee structures.

## 7. Questions for YoYo

1. What's the optimal reserve %? 2% seems safe but depends on rebalance frequency
2. How do we handle reserve surplus? Refund on withdraw or roll into LP?
3. Revenue model — do we charge a small fee on rebalance (e.g., 0.1% of swapped amount)?
4. Multi-user pool vs. individual vaults — gas efficiency vs. isolation tradeoff

## 8. Next Steps

- [ ] YoYo reviews gas budget model + financial assumptions
- [ ] DMOB scaffolds Foundry project with contract stubs
- [ ] Define keeper infrastructure (Chainlink Automation vs. custom cron)
- [ ] Audit checklist before testnet deployment
