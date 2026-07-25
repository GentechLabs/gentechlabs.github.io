# Multi-Wallet Treasury Manager

> Expand the Agentic Treasury to manage multiple wallets with per-wallet strategies, automatic rebalancing, and unified reporting.
> One agent, many wallets, one brain.

## Why Multi-Wallet?

A single treasury wallet is a single point of failure and limits strategy. Real treasury management requires:

| Wallet Type | Purpose | Risk | Rebalance Freq |
|-------------|---------|------|----------------|
| **Hot Wallet** | Daily operations, gas, x402 settlements | Higher | Daily |
| **Cold Wallet** | Long-term holdings, protocol deposits | Minimal | Monthly |
| **Yield Wallet** | AAE/Dex liquidity pools, farming | Medium | Weekly |
| **Operational Wallet** | Agent salaries, dev costs, gas | Medium | Weekly |
| **Reserve Wallet** | Emergency fund, insurance | None | Quarterly |
| **Per-Chain Wallets** | Base, Solana, AVAX, Arc, Arbitrum | Varies | Per-strategy |

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  Treasury Brain                    │
│  (orchestrator — one agent manages all wallets)   │
└────────┬──────────┬──────────┬────────────────────┘
         │          │          │
    ┌────▼────┐ ┌──▼───┐ ┌───▼────┐
    │ Hot     │ │ Yield│ │ Cold   │  ← Per-wallet configs
    │ Wallet  │ │Wallet│ │Wallet  │    (chain, strategy,
    │ $5K     │ │$20K  │ │$75K    │     threshold)
    └────┬────┘ └──┬───┘ └───┬────┘
         │         │         │
    ┌────▼─────────▼─────────▼────┐
    │     Rebalance Engine        │
    │  • Threshold triggers       │
    │  • Gas-aware routing        │
    │  • Slippage protection      │
    │  • Multi-chain settlement   │
    └─────────────────────────────┘
```

## Wallet Configuration

Each wallet has a config that defines its behavior:

```json
{
  "id": "hot-base",
  "name": "Hot Wallet — Base",
  "chain": "base",
  "type": "hot",
  "address": "0x...",
  "target_balance_usdc": 5000,
  "min_balance_usdc": 1000,
  "max_balance_usdc": 10000,
  "strategy": "liquidity",
  "rebalance": {
    "frequency": "daily",
    "trigger_delta_pct": 20,
    "gas_threshold_usdc": 0.50,
    "target_allocation_pct": 15
  },
  "allowed_actions": [
    "send", "receive", "swap", "deposit_lp", "withdraw_lp"
  ],
  "notification_thresholds": {
    "low_balance": 1000,
    "large_tx": 500
  }
}
```

## Multi-Wallet Strategies

### 1. Proportional Allocation

Split capital across wallets by fixed percentages:

```python
allocations = {
    "hot": 0.15,    # 15%
    "yield": 0.35,  # 35%
    "cold": 0.35,   # 35%
    "operational": 0.10,  # 10%
    "reserve": 0.05  # 5%
}
```

Agent checks each wallet's actual balance vs target. If deviation exceeds threshold, trigger rebalance.

### 2. Threshold-Based Rebalancing

Each wallet has a min/max range. When a wallet hits its min or max, the rebalance engine moves funds:

```
Hot wallet min hit ($1K) → Pull $4K from Yield wallet
Cold wallet max hit ($80K) → Move $5K to Reserve
Gas running low on Solana → Bridge $200 from Base hot wallet
```

### 3. Yield Optimization

The Yield Brain scans for best pools and allocates across wallets:

```python
for wallet in yield_wallets:
    best_pool = find_best_pool(wallet.chain, wallet.target_apy)
    if best_pool.apy > wallet.current_apy + rebalance_threshold:
        execute_rebalance(wallet, best_pool)
```

### 4. Cross-Chain Rebalancing

When one chain has cheap gas and another has high yield:

```python
# Avalanche has 25% APY on LFJ, Base has 8% on Aero
# Move 30% of Base yield allocation to Avalanche
rebalance_op = {
    "from": {"chain": "base", "wallet": "yield-base", "amount": 6000},
    "to": {"chain": "avax", "wallet": "yield-avax", "target_pool": "LFJ-USDC"},
    "route": "cctp",  # Circle CCTP for cheap bridging
    "max_gas": 2.00,
}
```

## CLI Usage

```bash
# List all wallets and their status
python treasury_manager.py --wallets

# Check a specific wallet
python treasury_manager.py --wallet hot-base

# Run rebalance check (dry run)
python treasury_manager.py --rebalance --dry-run

# Execute rebalance
python treasury_manager.py --rebalance

# Rebalance a specific wallet
python treasury_manager.py --rebalance --wallet yield-base

# Get unified balance report
python treasury_manager.py --report

# Watch mode
python treasury_manager.py --watch --interval 3600
```

## Unified Dashboard Metrics

| Metric | Description |
|--------|-------------|
| **Total AUM** | Sum of all wallet balances in USDC |
| **Per-wallet P&L** | Gain/loss per wallet since tracking started |
| **Allocation Drift** | How far each wallet is from target % |
| **Rebalance Opportunities** | Wallets outside their target range |
| **Gas Spend** | Cumulative gas costs across all chains |
| **Yield Earned** | Total yield across all yield wallets |
| **Slippage** | Cost of rebalancing (swaps + bridges) |

## Files

```
10-Labs/gentech-multiwallet-treasury/
├── SKILL.md              # This file
└── scripts/
    ├── treasury_manager.py  # Core multi-wallet logic
    └── rebalance.py         # Rebalancing engine
```
