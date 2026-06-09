# BNB Hack: AI Trading Agent Edition — Evaluation

## Overview
- **Prize:** $36,000 total
- **Duration:** June 3-21, 2026 (12 days left)
- **Platform:** DoraHacks
- **Required Stack:** CoinMarketCap + Trust Wallet + BNB Chain

## Tracks

### Track 1: Autonomous Trading Agents ($24K pool)
Build an agent that:
- Reads markets via CMC
- Makes trading decisions
- Signs and executes transactions via Trust Wallet
- All within user-defined rules

### Track 2: Strategy Skills ($6K pool)
Build strategy components that agents can use:
- Technical analysis signals
- Narrative detection
- Risk management
- Portfolio rebalancing

### Partner Awards ($2K each × 3)
- Best use of CMC data
- Best use of Trust Wallet
- Best overall agent

## Our Fit Analysis

### ✅ What We Already Have
| Asset | Source | Relevance |
|-------|--------|-----------|
| CMC rotation engine | Just built | Direct — market data + narrative detection |
| Agent trading strategies | AEG Phase 1 | Direct — market engine, portfolio management |
| Multi-chain architecture | AAE stack | High — same contracts deploy to BNB |
| TradeRoast | MVP deployed | Medium — could add BNB chain support |
| ERC-8004 identity | Mantle build | High — agent identity on BNB |

### 🔧 What We Need to Build
| Component | Effort | Priority |
|-----------|--------|----------|
| BNB Chain adapter | Low | P0 — swap RPC, update chain ID |
| Trust Wallet integration | Medium | P0 — TWAK SDK for execution |
| CMC API wrapper | Low | P0 — we already have the data flow |
| Trading strategy module | Medium | P1 — port from AEG |
| Demo UI | Low | P1 — single-page agent dashboard |

## Recommended Track: Autonomous Trading Agents

**Why Track 1 over Track 2:**
1. Higher prize pool ($24K vs $6K)
2. More visible — complete product, not just a component
3. Directly showcases our agent economy vision
4. We already have 80% of the stack

## Project Angle: "Agent TradeRoast"

**Concept:** An autonomous trading agent that reads market data via CMC, makes trades on BNB Chain, and generates roast-style performance reports. Combines TradeRoast's viral appeal with real trading execution.

**Flow:**
1. User sets risk parameters (max position size, stop loss, narrative preferences)
2. Agent monitors CMC for opportunities
3. Agent executes trades via Trust Wallet TWAK
4. Agent generates performance reports (roast cards)
5. User can share roast cards on social media

**Differentiation:**
- Not just another trading bot — it's entertaining
- Viral by nature (shareable roast cards)
- Built-in risk management (user-defined rules)
- Agent identity via ERC-8004

## Timeline
| Day | Task |
|-----|------|
| Jun 9-10 | Scaffold BNB Chain adapter + Trust Wallet integration |
| Jun 11-12 | Port trading strategy from AEG |
| Jun 13-14 | Build demo UI + roast integration |
| Jun 15-16 | Test on BNB testnet |
| Jun 17-18 | Record demo video |
| Jun 19-20 | Polish + submit |
| Jun 21 | Deadline |

## Next Steps
1. Register on DoraHacks
2. Create repo (or fork existing)
3. Scaffold BNB Chain adapter
4. Port CMC rotation engine data flow
5. Integrate Trust Wallet TWAK SDK
