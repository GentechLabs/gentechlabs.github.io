---
name: defi-intelligence
description: DeFi LP position analysis, fee analytics, and range optimization across EVM chains. Agents can query position status, fee accrual, range efficiency, and portfolio health.
allowed-tools: Read, Write, Edit, Bash(curl:*), WebFetch
model: any
license: MIT
metadata:
  author: gentech-labs
  version: '1.0.0'
---

# DeFi Intelligence — LP Position Analysis

Analyze liquidity positions across EVM chains. Get real-time position status, fee analytics, range optimization, and portfolio health — all via x402 payment protocol.

> **Payment:** All endpoints use x402 (HTTP 402 + payment instructions). Base USDC required. See `/pricing` for current rates.

## Endpoints

### Position Status
`GET /api/v1/position/status?chain={chain}&pool={poolAddress}&tokenId={tokenId}`

Returns: pair, price range, TVL, in-range status, current tick.

**Price:** $0.005

### Fee Analytics
`GET /api/v1/position/fees?chain={chain}&pool={poolAddress}&tokenId={tokenId}`

Returns: accrued fees, fee velocity, estimated APY, historical fee breakdown.

**Price:** $0.01

### Range Optimization
`GET /api/v1/position/range?chain={chain}&pool={poolAddress}&tokenId={tokenId}`

Returns: position shape (Curve/Bid-Ask/Gamma/Range/Stable), edge proximity, rebalance triggers, efficiency score.

**Price:** $0.025

### Portfolio Sync
`GET /api/v1/portfolio/sync?address={walletAddress}&chain={chain}`

Returns: all positions, PnL, risk score, aggregate TVL.

**Price:** $0.01

### Macro Events
`GET /api/v1/market/macro`

Returns: fed schedule, volatility index, stablecoin flow data.

**Price:** $0.005

## Usage

```bash
# Query position status
curl -H "Accept: application/json" \
  "https://gentech-defi-intelligence.jordanjones0902.workers.dev/api/v1/position/status?chain=ethereum&pool=0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640&tokenId=1"
```

The first request returns HTTP 402 with payment instructions. Pay the invoice and retry with the payment token to get your data.

## Supported Chains

Ethereum, Base, Arbitrum, Optimism, Polygon, BNB Chain, Avalanche, X Layer

## Additional Resources

- Full API docs: https://gentech-defi-intelligence.jordanjones0902.workers.dev/openapi.json
- Pricing: https://gentech-defi-intelligence.jordanjones0902.workers.dev/pricing
- Health: https://gentech-defi-intelligence.jordanjones0902.workers.dev/health
