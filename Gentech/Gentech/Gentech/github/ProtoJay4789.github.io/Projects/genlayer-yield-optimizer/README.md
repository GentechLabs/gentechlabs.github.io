# DeFi Yield Optimizer — GenLayer Intelligent Contract

Autonomous yield optimization with gas escrow for rebalancing. Reads live yield data from DeFi Llama, compares across protocols, and recommends/records rebalance actions.

**Part of GenLayer Builder Program — Intelligent Contract Templates**
Built by GenTech Labs

## What It Does

1. **Gas Escrow** — Users fund a gas balance ($5, $10, etc.) that pays for rebalancing
2. **Yield Scanning** — Fetches live APY data from DeFi Llama (500+ pools)
3. **LLM Analysis** — AI compares yields, considers risk, recommends rebalancing
4. **Rebalance Execution** — Moves funds to higher yields, deducts gas automatically
5. **Threshold Alerts** — Flags when gas runs low, prompts for top-up

## Why This Matters

The core insight: **rebalancing fees eat up yield gains**. Most users give up on yield optimization because gas costs exceed the benefit. This contract solves that:

- User funds $5 gas → agent rebalances as opportunities arise
- Each rebalance costs a fraction of the yield gain
- Gas runs low → alert triggers → user tops up
- Agent works autonomously within gas budget

This showcases GenLayer's unique capability: **reading live external data inside a smart contract**.

## Architecture

```
User → deposit_gas_escrow() → Vault created
  ↓
scan_yields() → DeFi Llama API → Cache yields
  ↓
get_recommendation() → LLM analyzes → Returns best opportunity
  ↓
execute_rebalance() → Deducts gas → Records action → Checks threshold
  ↓
check_gas_status() → "Gas low! Top up soon."
```

## Quick Start

```bash
# 1. Clone and install
cd genlayer-yield-optimizer
pip install -r requirements.txt

# 2. Start GenLayer Studio (local sandbox)
genlayer network

# 3. Deploy the contract
genlayer deploy

# 4. Set your contract address
export YIELD_OPTIMIZER_ADDRESS=0x...

# 5. Scan yields (no contract needed)
python cli.py scan

# 6. Get a recommendation
python cli.py recommend --protocol aave --apy 3.5 --value 10000
```

## CLI Client

Full command-line interface for interacting with the contract.

### Scanning Yields
```bash
python cli.py scan                          # Scan all yields
python cli.py scan --protocol aave          # Filter by protocol
```

### Getting Recommendations
```bash
python cli.py recommend                     # No position (just find best)
python cli.py recommend --protocol aave --apy 3.5 --value 10000
python cli.py recommend --chain ethereum --pool 0x123...
```

### Managing Gas Escrow
```bash
python cli.py deposit 0.01                  # Deposit 0.01 ETH
python cli.py gas-status                    # Check balance & remaining actions
```

### Executing Rebalances
```bash
python cli.py rebalance \
  --from aave --to curve \
  --from-pool 0xabc... --to-pool 0xdef... \
  --amount 10000000000000000000 \
  --reason "2.3% APY improvement"
```

### History & Stats
```bash
python cli.py history                       # Your past rebalances
python cli.py stats                         # Global contract stats
python cli.py compare                       # Protocol comparison table
```

## Monitoring Agent

Standalone monitoring script — runs without the GenLayer SDK.

### Single Scan
```bash
python monitor.py
python monitor.py --protocol aave --min-tvl 500000
```

### Continuous Monitoring
```bash
python monitor.py --loop --interval 3600   # Hourly scans
python monitor.py --loop --threshold 2.0    # Alert if >2% improvement
```

### Notifications
```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN=your_bot_token
export TELEGRAM_CHAT_ID=your_chat_id

python monitor.py --loop --notify tg       # Telegram alerts
```

### Save Reports
```bash
python monitor.py --output reports/scan.json
python monitor.py --loop --output reports/latest.json
```

### As a Cron Job
```bash
# Add to crontab (hourly scan)
0 * * * * cd /path/to/genlayer-yield-optimizer && python monitor.py --notify tg --output reports/latest.json
```

## Contract Features

### Gas Escrow System
- `deposit_gas_escrow()` — Fund gas with ETH
- `set_gas_threshold()` — Set alert threshold
- `set_gas_cost_per_rebalance()` — Configure per-action cost
- `get_gas_status()` — Check balance, threshold, remaining actions

### Yield Intelligence
- `scan_yields(protocol_filter)` — Fetch from DeFi Llama
- `get_recommendation()` — LLM-powered analysis with risk assessment
- `get_yield_comparison()` — View all cached protocol yields

### Rebalancing
- `execute_rebalance()` — Move funds, deduct gas, log action
- `get_user_history()` — View past rebalances
- `get_total_stats()` — Global contract statistics

## API Sources

- **DeFi Llama Yields** — `https://yields.llama.fi/pools` (500+ pools, 100+ protocols)
- **Risk Scoring** — Deterministic fallback based on protocol reputation
- **LLM Analysis** — Consensus-based recommendation via GenLayer's equivalence principle

## Risk Categories

| Protocol Type | Risk Score | Examples |
|--------------|------------|----------|
| Blue-chip lending | 85 | Aave, Compound |
| Established DEX | 80 | Curve, Uniswap |
| Yield booster | 75 | Convex |
| Yield aggregator | 70 | Yearn, Beefy |
| Yield trading | 65 | Pendle |
| Perpetual DEX | 60 | GMX |
| Unknown | 50 | New/unaudited |

## Testing

```bash
# Requires GenLayer Studio running
gltest
```

Tests cover:
- Initial state validation
- Yield data fetching and filtering
- Yield comparison across protocols
- Recommendation generation (with/without position)
- Gas status and threshold logic
- Data structure validation

## Deployment

```bash
# Start GenLayer Studio
genlayer network

# Deploy
genlayer deploy

# Tests
gltest
```

## Gas Escrow Flow

```
1. User deposits 0.01 ETH gas escrow
   → Vault created, balance = 0.01 ETH

2. Agent finds 2% APY improvement opportunity
   → Calls execute_rebalance()
   → Deducts 0.0005 ETH gas
   → Records action, checks threshold

3. After 15 rebalances:
   → Balance = 0.01 - (15 × 0.0005) = 0.0025 ETH
   → Threshold alert triggers (0.001 ETH)
   → User notified: "Gas low! Top up soon."

4. User deposits more gas → cycle continues
```

## Key GenLayer Features Used

- `gl.nondet.web.get()` — Fetch live yield data from DeFi Llama
- `gl.nondet.exec_prompt()` — LLM yield analysis and recommendations
- `gl.eq_principle.strict_eq()` — Validator consensus on non-deterministic outputs
- `TreeMap` — On-chain storage for vaults, yields, recommendations
- `@gl.public.write.payable` — Accept ETH deposits for gas escrow

## Project Structure

```
genlayer-yield-optimizer/
├── contracts/
│   └── yield_optimizer.py       # Main Intelligent Contract (806 lines)
├── tests/
│   └── test_yield_optimizer.py  # Integration tests (gltest)
├── deploy/
│   └── deployScript.ts          # GenLayer deployment script
├── config/
│   └── config.yaml              # Default configuration
├── cli.py                       # CLI client
├── monitor.py                   # Monitoring agent
├── requirements.txt
├── .env.example
├── package.json
└── README.md
```

## License

MIT — Built by GenTech Labs for the GenLayer Builder Program
