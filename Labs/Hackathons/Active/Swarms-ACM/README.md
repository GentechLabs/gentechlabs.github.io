# DeFi LP Monitor — Swarms Marketplace Agent

Monitors concentrated liquidity LP positions with IL tracking, efficiency scoring, and rebalance alerts.

## What It Does

- **Real-time price tracking** via CoinGecko API
- **Pool state reading** via DexScreener (TVL, volume, fees, APR)
- **Impermanent loss calculation** with concentration-aware modeling
- **Rebalance recommendations** based on position distance from range edges
- **Multi-chain support** — Avalanche, Ethereum, Base, and more

## How to Use

```bash
# Set your Swarms API key
export SWARMS_API_KEY=your_key_here

# Run the agent
python3 lp_monitor_agent.py

# Or use individual tools
from lp_monitor_agent import fetch_token_prices, read_pool_state, calculate_il, lp_position_report

# Fetch prices
prices = fetch_token_prices("AVAX,USDC")

# Read pool state
pool = read_pool_state("0x864d4e5ee7318e97483db7eb0912e09f161516ea", "avalanche")

# Calculate IL
il = calculate_il(entry_price=9.95, current_price=10.17, range_low=10.15, range_high=10.38)

# Full report
report = lp_position_report(range_low=10.15, range_high=10.38, entry_price=9.95)
```

## Tools

| Tool | Description |
|------|-------------|
| `fetch_token_prices` | Get token prices from CoinGecko |
| `read_pool_state` | Read LP pool data from DexScreener |
| `calculate_il` | Calculate impermanent loss with concentration modeling |
| `lp_position_report` | Generate complete position report with recommendations |

## Supported Chains

- Avalanche (LFJ/Trader Joe)
- Ethereum (Uniswap V3)
- Base (Uniswap V3)
- Any chain supported by DexScreener

## Pricing

**$9.99 one-time** — includes all tools and future updates.

## Built For

Swarms ACM Hackathon — Finance & Market Analysis track
