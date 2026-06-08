# Meteora DLMM SDK — Integration Guide

## Overview

Meteora's Dynamic Liquidity Market Maker (DLMM) is the leading concentrated liquidity AMM on Solana. Our vault will use it to earn yield on SOL-USDC and USDC-USDT pools.

## Package Info

- **NPM Package:** `@meteora-ag/dlmm`
- **Latest Version:** 1.9.10 (as of June 2026)
- **Language:** TypeScript (Node.js)
- **Program ID (Mainnet):** `LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo`
- **Program ID (Devnet):** Same address (deployed simultaneously)
- **GitHub:** https://github.com/MeteoraAg/dlmm-sdk

## Installation

```bash
npm install @meteora-ag/dlmm @solana/web3.js@^1.87.0 @solana/spl-token
```

## Key API Methods

### 1. DLMM Instance Creation
```typescript
import { DLMM } from '@meteora-ag/dlmm';
import { Connection, Keypair } from '@solana/web3.js';

const connection = new Connection('https://api.mainnet-beta.solana.com');
const dlmm = await DLMM.create(connection, poolAddress);
```

### 2. Add Liquidity (Deposit)
```typescript
// By Strategy - recommended for concentrated liquidity
const tx = await dlmm.addLiquidityByStrategy({
  positionPubKey: positionPubKey,
  userPubKey: wallet.publicKey,
  maxActiveBinSlippage: 10,
  liquidityAmount: new BN(liquidityAmount),
  strategy: {
    maxBinStep: 10,
    baseBinStep: 5,
    binStepDistribution: [
      { binStep: 5, distribution: 0.4 },  // 40% in tight range
      { binStep: 10, distribution: 0.3 }, // 30% in medium range
      { binStep: 20, distribution: 0.3 }, // 30% in wide range
    ],
  },
});
```

### 3. Remove Liquidity (Withdraw)
```typescript
// Remove from specific bin range
const tx = await dlmm.removeLiquidityByRange({
  positionPubKey: positionPubKey,
  userPubKey: wallet.publicKey,
  binIdLower: lowerBinId,
  binIdUpper: upperBinId,
});
```

### 4. Initialize Position
```typescript
const { transaction, signers } = await dlmm.initializePositionAndAddLiquidityByStrategy({
  userPubKey: wallet.publicKey,
  maxActiveBinSlippage: 10,
  positionBinRange: 30,
  liquidityAmount: new BN(liquidityAmount),
  strategy: { /* ... */ },
});
```

### 5. Claim Fees
```typescript
const tx = await dlmm.claimAllFeeV2({
  ownerPubKey: wallet.publicKey,
  positions: [positionPubKey],
});
```

### 6. Close Position
```typescript
const tx = await dlmm.removeLiquidityByRangeAndClaimAllV2({
  positionPubKey: positionPubKey,
  userPubKey: wallet.publicKey,
  binIdLower: -100,
  binIdUpper: 100,
});
```

### 7. Get Pool Info
```typescript
const poolInfo = await DLMM.create(connection, poolAddress);
console.log(poolInfo); // Contains reserves, bin step, active bin, etc.
```

## Pool Discovery

```typescript
// Get all pools
const allPools = await DLMM.getLbPairs(connection);

// Filter for USDC pools
const usdcPools = allPools.filter(pool => 
  pool.baseMint === USDC_MINT || pool.quoteMint === USDC_MINT
);
```

## Strategy for Our Vault

### Conservative (USDC-USDT)
- Bin range: ±10 bins (tight, stablecoin pair)
- Active bin: current price
- Risk: Very low (0.05)
- Expected APY: 3-8%

### Moderate (SOL-USDC)
- Bin range: ±30 bins (medium volatility)
- Active bin: current price
- Risk: Medium (0.4)
- Expected APY: 8-15%

## Key Addresses

| Token | Address |
|-------|---------|
| USDC (Solana) | EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v |
| SOL | So11111111111111111111111111111111111111112 |
| USDT | Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB |

## Devnet Testing

- Same program ID on devnet
- Use devnet SOL from faucet: `solana airdrop 2`
- Test pools available with mock tokens

## Notes

- SDK requires Solana wallet (Keypair) for signing
- All transactions are VersionedTransaction (v0)
- Priority fees recommended for faster inclusion
- SDK handles bin calculations internally
