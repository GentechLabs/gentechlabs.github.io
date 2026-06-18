# Compound vs. Extract Protocol

> "The best LP strategy isn't about choosing between compounding and extracting — it's about doing both optimally."

## Overview

A protocol that lets LP providers **compound or extract accumulated fees without closing their position**. This is the flagship DeFi module for the GenTech Agent Kit (AAE).

## The Problem

LP providers on concentrated liquidity DEXs face a binary choice:
1. **Leave fees in** → fees sit idle, don't compound, lose buying power
2. **Close position to extract** → lose range, pay gas to re-enter, miss fee generation

Neither option is optimal.

## The Solution

Extract profits while keeping your position active:
- **Compound Mode**: Reinvest fees back into the position → grows principal
- **Extract Mode**: Pull out accumulated fees → send to wallet
- **Auto Mode**: AI decides based on market conditions, gas prices, and user preferences

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Dashboard  │  │   Settings  │  │   History   │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         └────────────────┴────────────────┘             │
│                        │                                │
│  ┌─────────────────────┴─────────────────────────┐    │
│  │              API Gateway / Router              │    │
│  └──────────────────────┬────────────────────────┘    │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│                   CORE ENGINE                           │
│  ┌──────────────┐  ┌────┴─────┐  ┌──────────────┐    │
│  │ Fee Monitor  │  │ Decision │  │   Executor   │    │
│  │ (Tracking)   │  │ Engine   │  │ (Compound/   │    │
│  │              │  │ (AI)     │  │  Extract)    │    │
│  └──────────────┘  └──────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Modules

### 1. Fee Monitor (`fee_monitor.py`)
- Track real-time fee accumulation per LP position
- Calculate fee velocity (hourly/daily rate)
- Persist state to disk

### 2. Decision Engine (`decision_engine.py`)
- AI-powered compound vs. extract decisions
- Rule-based in Phase 1, ML optimization in Phase 2
- Considers: market volatility, gas prices, user preferences

### 3. Executor (Phase 2)
- Execute compound or extract operations
- Swap routing via Jupiter (Solana) or 0x (EVM)
- Gas optimization and slippage protection

## Supported DEXs

| DEX | Chain | Status |
|-----|-------|--------|
| LFJ (Trader Joe) | Avalanche | ✅ Phase 1 |
| Uniswap V3 | Ethereum/Base | 🔲 Phase 2 |
| Aerodrome | Base | 🔲 Phase 2 |
| Meteora | Solana | 🔲 Phase 2 |

## Quick Start

```bash
# Run tests
python3 tests/test_basic.py

# Initialize monitor
python3 -c "
from src.fee_monitor import FeeMonitor
monitor = FeeMonitor(data_dir='./data')
print('Fee Monitor initialized')
"

# Initialize decision engine
python3 -c "
from src.decision_engine import DecisionEngine
engine = DecisionEngine(config_dir='./config')
print('Decision Engine initialized')
"
```

## Revenue Model

| Stream | Fee | Notes |
|--------|-----|-------|
| Extraction fee | 0.1-0.5% | On extracted amount |
| Compound fee | 0.05-0.1% | On compounded amount |
| Premium auto-mode | $5/mo | AI decision engine |
| API access | $20/mo | For other protocols |

## Competitive Advantage

| Feature | Bankr | GOAT SDK | AAE (Us) |
|---------|-------|----------|----------|
| Fee extraction | Basic | Basic | **Optimized** |
| Auto-compound | ❌ | ❌ | **✅** |
| AI decision engine | ❌ | ❌ | **✅** |
| Gas optimization | ❌ | ❌ | **✅** |

## Build Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Fee Monitoring | 2-3 days | Real-time tracking |
| Phase 2: Extract Execution | 3-5 days | Manual extract |
| Phase 3: Compound Execution | 2-3 days | Auto-compound |
| Phase 4: Auto Mode | 1 week | AI decision engine |
| Phase 5: Multi-DEX | 2 weeks | Uniswap, Aerodrome |

**MVP (Phase 1-3): ~2 weeks**

## License

MIT — GenTech Agent Kit
