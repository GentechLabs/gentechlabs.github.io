# Aerodrome Finance — Integration Guide

## Overview

Aerodrome is the central liquidity hub on Base, combining Curve + Convex + Uniswap mechanics. Our vault will use it for USDC-WETH and USDC-USDbC LP positions to earn trading fees and AERO emissions.

## Contract Addresses (Base Mainnet)

| Contract | Address |
|----------|---------|
| Router | `0xcF77a3Ba9A5CA399B7c97c8b328D78F8BF0B6322` |
| Voter | `0x166155DbB2Eb90F6D0c6baC690F06C5A0a22b287` |
| Gauge Factory | `0x4F6B8DA5e41E1c4cC2E17A698B92F64829F6d2C7` |
| Pool Factory (Basic) | `0x4248d35E9b0c68c9c406a207F8B2B77b0fC73582` |
| Pool Factory (Slipstream) | `0xc5d563A36AE78145C45a50134d48A1215220f80a` |
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| WETH | `0x4200000000000000000000000000000000000006` |

## Contract Addresses (Base Sepolia Testnet)

| Contract | Address |
|----------|---------|
| Router | `0xcF77a3Ba9A5CA399B7c97c8b328D78F8BF0B6322` |
| USDC | `0x036CbD53842c54125e43f1602f08130F5045d35A` |

## SDK Options

### Option 1: Sugar SDK (Python) — Recommended
```bash
pip install velodrome-sugar
```

```python
from sugar.chains import BaseChain, AsyncBaseChain

chain = BaseChain(rpc_url="https://mainnet.base.org")
pools = await chain.get_pools()
```

### Option 2: Direct Contract Calls (Web3.py)
```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
router = w3.eth.contract(
    address="0xcF77a3Ba9A5CA399B7c97c8b328D78F8BF0B6322",
    abi=ROUTER_ABI
)
```

## Key Router Functions

### 1. Add Liquidity (Dual Token)
```solidity
function addLiquidity(
    address pool,
    uint amount0Desired,
    uint amount1Desired,
    uint amount0Min,
    uint amount1Min,
    address to,
    uint deadline
) external returns (uint amount0, uint amount1);
```

### 2. Add Liquidity (Single Token — Zap)
```solidity
function addLiquiditySingle(
    address pool,
    uint amountIn,
    address tokenIn,
    uint amountOutMin,
    address to,
    uint deadline
) external returns (uint amountIn, uint amountOut);
```

### 3. Remove Liquidity
```solidity
function removeLiquidity(
    address pool,
    uint liquidity,
    uint amount0Min,
    uint amount1Min,
    address to,
    uint deadline
) external returns (uint amount0, uint amount1);
```

### 4. Remove Liquidity Single
```solidity
function removeLiquiditySingle(
    address pool,
    uint liquidity,
    address tokenOut,
    uint amountOutMin,
    address to,
    uint deadline
) external returns (uint amountOut);
```

### 5. Swap (Multi-hop)
```solidity
struct Route {
    address from;
    address to;
    bool stable;
}

function swap(
    Route[] calldata routes,
    uint amountIn,
    uint amountOutMin,
    address to,
    uint deadline
) external returns (uint amountIn, uint amountOut);
```

### 6. Zap (Add Liquidity with Single Token)
```solidity
function zap(
    address pool,
    uint liquidityAmount,
    address tokenIn,
    uint amountIn,
    uint minAmount0,
    uint minAmount1,
    address to,
    uint deadline
) external returns (uint amount0, uint amount1);
```

## Pool Types

### vAMM (Volatile)
- For volatile pairs (e.g., AERO/USDC)
- Variable fee rate
- Higher APY potential

### sAMM (Stable)
- For stable pairs (e.g., USDC/USDbC)
- Low fee rate (0.01-0.04%)
- Lower APY but very safe

### Slipstream (Concentrated Liquidity)
- Uniswap V3-style concentrated liquidity
- Higher capital efficiency
- Requires active management

## Strategy for Our Vault

### Conservative: USDC-USDbC (sAMM)
- Type: Stable pool
- Risk: Very low (0.1)
- Expected APY: 2-5%
- Good for parking dry powder

### Moderate: USDC-WETH (vAMM)
- Type: Volatile pool
- Risk: Medium (0.3)
- Expected APY: 6-12%
- Good for yield farming

## Workflow

1. Approve USDC/WETH to Router
2. Call `addLiquidity()` or `addLiquiditySingle()`
3. Receive LP tokens (NFT for Slipstream, ERC-20 for Basic)
4. Optionally stake in Gauge for AERO emissions
5. To exit: `removeLiquidity()` → receive tokens back

## Gas Costs (Base)

- Add Liquidity: ~0.0001 ETH ($0.25)
- Remove Liquidity: ~0.0001 ETH ($0.25)
- Swap: ~0.00005 ETH ($0.12)
- Claim Rewards: ~0.00005 ETH ($0.12)

## Notes

- Aerodrome uses ve(3,3) mechanics — locked AERO gives boosted yields
- For MVP, we skip locking and use basic LP only
- Slipstream pools require more complex bin management
- Basic pools (vAMM/sAMM) are simpler for our use case
