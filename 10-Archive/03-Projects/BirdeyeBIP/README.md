# 🦉 BirdeyeAdapter — On-Chain Market Data for Agent Economies

> **Birdeye BIP Competition — Sprint 1 Submission**
> *Bringing Birdeye Data Services into the on-chain agent economy via x402 pay-per-request*

---

## What This Is

**BirdeyeAdapter** is an on-chain smart contract that feeds real-time Solana market data (prices, volumes, liquidity) into agent decision engines. It follows the AAE (Agent Economy) adapter pattern — a thin wrapper that accepts off-chain oracle data and makes it available to other smart contracts.

### The Problem It Solves

AI agents that trade, manage LP positions, or make DeFi decisions need **reliable, real-time market data on-chain**. Currently:
- Agents rely on centralized APIs (single point of failure)
- Data freshness is uncertain (stale prices → bad decisions)
- No standardized interface for market data feeds
- LP position monitoring requires manual checks

**BirdeyeAdapter fixes this** by providing:
1. **Standardized on-chain interface** for token market data
2. **Oracle-gated data pushes** (only authorized oracles can update)
3. **Automatic LP range breach detection** with on-chain events
4. **Staleness protection** (old data flagged, doesn't trigger false alarms)
5. **Batch processing** (push multiple tokens in one transaction)

---

## Architecture

```
┌─────────────────┐     x402 pay-per-request      ┌─────────────────┐
│  Birdeye Data   │◄──────────────────────────────│  Oracle Script  │
│  Services API   │   $0.003/request (USDC)        │  (Python)       │
│                 │                                │                 │
│  /defi/price    │   Token prices, volumes,       │  Polls Birdeye  │
│  /defi/multi_   │   liquidity, OHLCV             │  Encodes data   │
│  price          │                                │  Signs tx       │
└─────────────────┘                                └────────┬────────┘
                                                           │
                                              pushTokenData()
                                                           │
                                              ┌────────────▼────────────┐
                                              │    BirdeyeAdapter.sol   │
                                              │                        │
                                              │  ✓ Price feeds         │
                                              │  ✓ Volume tracking     │
                                              │  ✓ Liquidity data      │
                                              │  ✓ LP range monitor    │
                                              │  ✓ Staleness guard     │
                                              │  ✓ Batch processing    │
                                              └────────────┬────────────┘
                                                           │
                                              Events + view functions
                                                           │
                                              ┌────────────▼────────────┐
                                              │   Agent Contracts       │
                                              │                        │
                                              │  • AgentKeeper (triggers)
                                              │  • AgentRegistry (rep)  │
                                              │  • LP Manager           │
                                              │  • Custom strategies    │
                                              └─────────────────────────┘
```

---

## Contract Features

### Token Data Feed
| Function | Access | Description |
|----------|--------|-------------|
| `pushTokenData(token, price, volume, liquidity)` | Oracle only | Push single token snapshot |
| `processData(batch)` | Oracle only | Push multiple tokens in one tx |
| `getTokenSnapshot(token)` | Public | Read latest market data |

### LP Range Monitoring
| Function | Access | Description |
|----------|--------|-------------|
| `registerLPPosition(tokenA, tokenB, lower, upper)` | Anyone | Register position to monitor |
| `isLPInRange(positionId)` | Public | Check if position is within bounds |
| `deactivatePosition(positionId)` | Owner | Stop monitoring a position |

### Events
- `TokenDataUpdated(token, price, volume, liquidity, timestamp)` — on every data push
- `LPRangeBreached(agent, token, currentPrice, lowerBound, upperBound)` — when price exits range

---

## Oracle Script

The `oracle.py` script polls Birdeye's x402 API and pushes data on-chain:

```bash
# Data-only mode (no chain)
python oracle.py --api-key YOUR_KEY

# With on-chain pushes
python oracle.py \
  --rpc https://your-rpc.com \
  --adapter 0xYOUR_ADAPTER_ADDRESS \
  --key YOUR_PRIVATE_KEY \
  --api-key YOUR_BIRDEYE_KEY \
  --interval 60
```

### x402 Cost Model
| Interval | Requests/day | Daily Cost | Monthly Cost |
|----------|-------------|------------|--------------|
| 60s | 1,440 | $4.32 | $129.60 |
| 5 min | 288 | $0.86 | $25.92 |
| 15 min | 96 | $0.29 | $8.64 |

---

## Quick Start

### Install
```bash
git clone https://github.com/ProtoJay4789/birdeye-adapter-bip.git
cd birdeye-adapter-bip
forge build
```

### Test
```bash
forge test -vvv
```

### Deploy
```bash
forge script script/Deploy.s.sol --rpc-url $RPC --private-key $KEY --broadcast
```

---

## Why Birdeye + x402?

Birdeye's x402 pay-per-request model ($0.003/request) is the perfect data layer for agent economies:

1. **No subscriptions** — agents pay per query, not per month
2. **USDC settlement** — native crypto payments, no fiat rails
3. **Solana + Base** — dual-chain settlement aligns with multi-chain agents
4. **Full API access** — all endpoints, no tier gating
5. **2-second settlement** — fast enough for real-time agent decisions

Combined with the BirdeyeAdapter contract, this creates a **fully on-chain, pay-per-request market data pipeline** for agent economies.

---

## Tags

`birdeye` `x402` `solana` `agent-economy` `defi` `oracle` `lp-monitoring` `data-feed` `bip`

---

*Built by YoYo (GenTech Strategies) for the Birdeye BIP Competition — Sprint 1*
