# Compound vs. Extract Protocol — Product Spec

**Added:** Jun 17, 2026
**Status:** SPEC COMPLETE → Building in Labs
**Priority:** HIGH — Flagship Agent Kit DeFi module
**Owner:** Jordan (product) + Gentech (build)

---

## The Problem

LP providers on concentrated liquidity DEXs face a binary choice:
1. **Leave fees in** → fees sit idle, don't compound, lose buying power to inflation
2. **Close position to extract** → lose range, pay gas to re-enter, miss fee generation during exit

Neither option is optimal. There's no clean way to extract *only* profits while keeping the position active.

## The Solution

A protocol that lets LP providers **compound or extract accumulated fees without closing their position**.

### Core Mechanics

**Fee Accumulation Layer:**
- Track real-time fee accrual per position
- Display accumulated fees separate from principal
- Auto-detect optimal extraction timing (gas price, fee velocity, market conditions)

**Compound Mode:**
- Claim fees → swap to LP token pair → add back to position
- Optimized: batch during low-gas windows, minimize swap slippage
- Growth multiplier: compounds daily fees back into the position

**Extract Mode:**
- Claim fees → swap to stablecoin → send to user wallet
- Partial extraction: user specifies amount, protocol calculates timing
- Example: "Extract $10" → monitor until fees hit $10 → auto-extract

**Hybrid Mode (Auto):**
- Configurable split: "Compound 70%, Extract 30%"
- AI decision engine optimizes based on:
  - Market volatility (stable → compound, volatile → extract)
  - Gas prices (high gas → wait, low gas → execute)
  - Fee velocity (accelerating → compound, decelerating → extract)
  - User balance (low stablecoin → extract more, high → compound more)

## User Experience

### Dashboard Integration
- New tab: "Compound / Extract"
- Shows: position value, accumulated fees, compound rate, extraction history
- Toggle: Compound | Extract | Auto
- Settings: extraction threshold, compound/extract split, gas limit

### Example Flow
```
User has AVAX/USDC LP position on LFJ
Fees accumulate: $1.67/day
User sets: "Extract when fees hit $10"
Day 1: $1.67 accumulated
Day 2: $3.34 accumulated
Day 3: $5.01 accumulated
Day 4: $6.68 accumulated
Day 5: $8.35 accumulated
Day 6: $10.02 → AUTO-EXTRACT triggered
  → Claim $10.02 in fees
  → Swap to USDC via Jupiter
  → Send to user wallet
  → Position continues earning
  → User notification: "Extracted $10.02 USDC"
```

## Technical Architecture

### Layer 1: Fee Monitoring (MVP)
- RPC calls to DEX factory contracts
- Parse LP position NFT metadata
- Track fee accumulation per position
- Real-time dashboard display

### Layer 2: Execution Engine
- Smart contract interaction for `collect()` / `withdraw()`
- Swap routing via Jupiter (Solana) or 0x (EVM)
- Gas optimization: batch operations, time for low-gas periods
- Slippage protection: max slippage parameter

### Layer 3: Decision Engine (AI)
- Market condition analysis
- Gas price prediction
- Fee velocity tracking
- User preference learning
- Optimal timing calculation

### Layer 4: User Interface
- Dashboard tab with position overview
- Compound/Extract/Auto toggle
- Extraction history
- Settings panel

## Supported DEXs (Phase 1)

| DEX | Chain | Fee Claim Method | Status |
|-----|-------|-----------------|--------|
| LFJ (Trader Joe) | Avalanche | `collect()` on position NFT | ✅ Live — we have integration |
| Uniswap V3 | Ethereum/Base | `collect()` on position NFT | 🔲 Phase 2 |
| Aerodrome | Base | Fee claim via gauge | 🔲 Phase 2 |
| Meteora | Solana | Fee claim via position | 🔲 Phase 2 |

## Revenue Model

| Stream | Fee | Notes |
|--------|-----|-------|
| Extraction fee | 0.1-0.5% | On extracted amount |
| Compound fee | 0.05-0.1% | On compounded amount (lower since it grows the position) |
| Premium auto-mode | $5/mo | AI decision engine, gas optimization |
| API access | $20/mo | For other protocols to integrate |

## Build Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Fee Monitoring | 2-3 days | Real-time fee tracking, dashboard display |
| Phase 2: Extract Execution | 3-5 days | Manual extract, swap routing, slippage protection |
| Phase 3: Compound Execution | 2-3 days | Auto-compound back into position |
| Phase 4: Auto Mode | 1 week | AI decision engine, hybrid mode |
| Phase 5: Multi-DEX | 2 weeks | Uniswap V3, Aerodrome, Meteora |

**MVP (Phase 1-3): ~2 weeks**
**Full product (Phase 1-5): ~6 weeks**

## Agent Kit Integration

This becomes the **DeFi Yield Module** in the GenTech Agent Kit:
- `agent-kit/modules/defi-yield/` — compound/extract logic
- `agent-kit/modules/fee-monitor/` — real-time tracking
- `agent-kit/modules/swap-router/` — Jupiter/0x integration
- `agent-kit/modules/decision-engine/` — AI optimization

## Competitive Advantage

| Feature | Bankr | GOAT SDK | AAE (Us) |
|---------|-------|----------|----------|
| Fee extraction | Basic | Basic | **Optimized** |
| Auto-compound | ❌ | ❌ | **✅** |
| AI decision engine | ❌ | ❌ | **✅** |
| Gas optimization | ❌ | ❌ | **✅** |
| Multi-DEX | Base only | Multi-chain | **Phase 1: LFJ, Phase 2: Multi** |
| Dashboard | Basic | None | **Full visualization** |

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Smart contract exploit | HIGH | Audit before mainnet, testnet first |
| Slippage on swap leg | MEDIUM | Max slippage parameter, DEX aggregation |
| Gas spikes during execution | MEDIUM | Gas prediction, batch operations |
| Position goes out of range during compound | LOW | User notified, can cancel |
| DEX fee claim mechanism changes | LOW | Abstracted layer, easy to update |

## Next Steps

1. ✅ Product spec complete
2. 🔲 Architecture doc in Labs
3. 🔲 Phase 1: Fee monitoring MVP
4. 🔲 Phase 2: Extract execution
5. 🔲 Phase 3: Compound execution
6. 🔲 Phase 4: Auto mode
7. 🔲 Phase 5: Multi-DEX expansion

---

*"The best LP strategy isn't about choosing between compounding and extracting — it's about doing both optimally."*
