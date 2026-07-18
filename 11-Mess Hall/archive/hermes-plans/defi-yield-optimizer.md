# DeFi Yield Optimizer — Build Plan

**Date:** 2026-05-23
**Status:** 🟢 In Progress
**Repo:** github.com/ProtoJay4789/genlayer-yield-optimizer (new)

## Problem
DeFi yield farming requires manually checking dozens of protocols across multiple chains. Users miss optimal yields because data is scattered and changes rapidly. An Intelligent Contract that reads live yield data and recommends allocation showcases GenLayer's unique capability.

## Architecture
GenLayer Intelligent Contract that:
1. Fetches live yield data from DeFi Llama API (no oracle needed)
2. Compares APY across protocols (Aave, Compound, Curve, Yearn, etc.)
3. Considers risk factors (TVL, audit status, protocol age)
4. Recommends optimal allocation based on risk tolerance
5. Stores recommendation history on-chain

## Key APIs
- **DeFi Llama Yields API**: `https://yields.llama.fi/pools` — free, no key needed
  - Returns: pool info, APY, TVL, chain, project, symbol, il7d, apyMean30d
  - This is the primary data source

## Risk Model
- TVL > $100M = low risk, TVL $10-100M = medium, TVL < $10M = high
- Protocol age > 1 year = trusted, 3-12 months = moderate, < 3 months = speculative
- Stablecoin pools = lower risk multiplier
- IL (impermanent loss) 7-day history as volatility indicator

## Tasks

### Task 1: Project Scaffold
- Directory structure
- requirements.txt
- README.md
- Files: `genlayer-yield-optimizer/`

### Task 2: Yield Optimizer Contract
- Python class-based GenLayer Intelligent Contract
- `@contract` decorator
- `optimize(chains, risk_tolerance, amount)` — main method
  - Fetches from DeFi Llama
  - Filters by chain
  - Scores pools by: APY, TVL, risk, stability
  - Returns top 5 recommendations with allocation %
- `get_history()` — past recommendations
- `get_pool_details(pool_id)` — single pool deep dive
- Files: `contracts/yield_optimizer.py`

### Task 3: Tests
- pytest tests for risk scoring
- Test pool filtering by chain
- Test allocation calculation
- Test edge cases (no pools found, API errors)
- At least 12 test cases
- Files: `tests/test_optimizer.py`

### Task 4: Demo Script
- Standalone demo with simulated DeFi Llama data
- Shows optimization across 3 chains (Ethereum, Arbitrum, Base)
- Pretty-prints recommendations with APY, risk, allocation
- Files: `scripts/demo.py`

## Verification
- All tests pass
- Demo runs and produces formatted output
- Contract syntax valid
