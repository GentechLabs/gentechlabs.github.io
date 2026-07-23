# Compound vs. Extract Protocol — Testnet Deployment Guide

**Network:** Avalanche Fuji (Testnet)  
**Chain ID:** 43113  
**RPC:** https://api.avax-test.network/ext/bc/C/rpc  
**Explorer:** https://testnet.snowtrace.io  
**Date:** June 18, 2026  

## Overview

This directory contains the testnet deployment scaffold for Phase 2 of the Compound vs. Extract Protocol. It validates the full extract and compound flows on Avalanche Fuji before mainnet deployment.

**Current Status:** Scaffold with mocked on-chain calls. No real contract deployed yet.

## Directory Structure

```
testnet/
├── README.md              ← You are here
├── config.json            ← Fuji testnet configuration
├── deploy_fuji.py         ← Deployment scaffold script
├── test_extract.py        ← Extract flow integration tests (5 tests)
├── test_compound.py       ← Compound flow integration tests (6 tests)
└── test_extract_results.json   ← Generated after test run
└── test_compound_results.json  ← Generated after test run
```

## Prerequisites

```bash
# Python 3.9+ (already available)
python3 --version

# Get testnet AVAX from the faucet
# https://faucet.avax.network/
# Send to your wallet address (update config.json)
```

## Quick Start

### 1. Run Extract Tests

```bash
cd /root/vaults/gentech/02-Labs/compound-extract/testnet
python3 test_extract.py
```

**Expected output:**
```
🧪 Compound vs. Extract Protocol — Extract Flow Tests
  ✅ PASS: Extract flow completed
  ✅ PASS: Extract + Monitor integration
  ✅ PASS: Decision engine triggered extract
  ✅ PASS: 0x router extract
  ✅ PASS: Empty fees handled gracefully
  ✅ ALL EXTRACT TESTS PASSED (5/5)
```

### 2. Run Compound Tests

```bash
python3 test_compound.py
```

**Expected output:**
```
🧪 Compound vs. Extract Protocol — Compound Flow Tests
  ✅ PASS: Compound flow completed
  ✅ PASS: Compound + Monitor integration
  ✅ PASS: Decision engine triggered compound
  ✅ PASS: Partial compound ratio working
  ✅ PASS: Zero fees handled (expected failure)
  ✅ PASS: 0x router compound
  ✅ ALL COMPOUND TESTS PASSED (6/6)
```

### 3. Deploy Scaffold (Dry Run)

```bash
python3 deploy_fuji.py --dry-run
```

### 4. Deploy to Fuji (Requires Wallet + AVAX)

```bash
# First, update config.json with your wallet address
# Then get testnet AVAX from https://faucet.avax.network/

python3 deploy_fuji.py
```

## Flows Tested

### Extract Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Claim Fees  │ ──▶ │  Swap to     │ ──▶ │  Transfer to │
│  (LFJ/0x)    │     │  Target Token│     │  Wallet      │
└──────────────┘     └──────────────┘     └──────────────┘
     180k gas            250k gas             50k gas
```

**Steps:**
1. Call `collect` on LFJ Position Manager to claim accumulated fees
2. Swap non-target tokens to target stablecoin (USDC.e) via LFJ router or 0x
3. Transfer received tokens to user wallet (auto after swap)

### Compound Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Claim Fees  │ ──▶ │  Swap Half   │ ──▶ │  Add Liq.    │
│  (LFJ/0x)    │     │  to Pair     │     │  Back        │
└──────────────┘     └──────────────┘     └──────────────┘
     180k gas            250k gas             400k gas
```

**Steps:**
1. Claim accumulated fees from position
2. Swap 50% of each token to the pair's other token
3. Add both tokens back as liquidity via `increaseLiquidity`

## Configuration

### config.json Key Fields

| Field | Description | Default |
|-------|-------------|---------|
| `network.chain_id` | Fuji testnet chain ID | `43113` |
| `network.rpc_url` | Fuji RPC endpoint | `https://api.avax-test.network/ext/bc/C/rpc` |
| `execution.max_slippage` | Max slippage tolerance | `0.5%` |
| `decision_engine.extract_threshold_usd` | Minimum USD to trigger extraction | `$10.00` |
| `decision_engine.compound_split` | % of fees to compound | `70%` |
| `wallet.address` | Your Fuji testnet wallet | Must replace |

### Updating Wallet

Edit `config.json` and replace:
```json
"wallet": {
    "address": "0xYOUR_FUJI_TESTNET_WALLET_ADDRESS"
}
```

## Adapters

| Adapter | Chain | DEX | Status |
|---------|-------|-----|--------|
| `LFJAdapter` | Avalanche | Trader Joe V2.1 | ✅ Scaffold |
| `ZeroXSwapRouter` | EVM (multi-chain) | 0x API | ✅ Scaffold |
| `JupiterSwapRouter` | Solana | Jupiter | 🔲 Phase 3 |

## Architecture Integration

```
                    ┌─────────────────┐
                    │  Fee Monitor     │
                    │  (Phase 1 ✅)    │
                    └────────┬────────┘
                             │ fees data
                    ┌────────▼────────┐
                    │ Decision Engine  │
                    │  (Phase 1 ✅)    │
                    └────────┬────────┘
                             │ action + amount
                    ┌────────▼────────┐
                    │   Executor       │
                    │  (Phase 2 ✅)    │ ◄── This testnet scaffold
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──────┐ ┌────▼─────┐ ┌──────▼───────┐
     │  LFJ Adapter  │ │ 0x Router│ │ Jupiter      │
     │  (Avalanche)  │ │ (EVM)    │ │ (Solana)     │
     └───────────────┘ └──────────┘ └──────────────┘
```

## Next Steps

1. **Write Solidity contract** — Implement `CompoundExtract.sol` with:
   - `claimFees(positionNftId)` 
   - `compoundFees(positionNftId, amount0, amount1)`
   - `extractFees(positionNftId, targetToken, amount)`
2. **Compile with Hardhat/Foundry** — Generate ABI + bytecode
3. **Deploy to Fuji** — Run `deploy_fuji.py` with compiled artifacts
4. **Replace mocks** — Update executor to call real contracts
5. **Fuzz testing** — Test edge cases (reverts, gas spikes, MEV)
6. **Mainnet preparation** — Audit + controlled rollout

## Testing on Real Testnet

Once the contract is deployed, switch from mocked to live by:

```python
# In your scripts, change:
executor = Executor(adapter=adapter, ...)

# To use the real contract:
executor = Executor(
    adapter=adapter,
    wallet_address="0x...",
    contract_address="0x...",  # Deployed contract
    use_mock=False,            # Switch to real calls
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Insufficient AVAX` | Get testnet AVAX from faucet |
| `RPC connection failed` | Check RPC URL in config.json |
| `Position not found` | Verify LFJ position exists on Fuji |
| `Import errors` | Run from `testnet/` directory or add `src/` to PYTHONPATH |

---

*Phase 2 scaffold — June 18, 2026*
