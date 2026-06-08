# Agent Arena Credit Layer — Game Mechanics

**Date:** 2026-05-21
**Status:** 🟢 Approved

## Problem
Players need to learn borrowing, repayment, and liquidation mechanics before touching real DeFi. No existing game teaches these mechanics in a risk-free environment with real progression stakes.

## Proposed Solution
Three interconnected modules that form the credit layer of the Agent Arena trading sim:

### 1. Credit Score Engine
- Scoring formula: composite of trade win rate, account age, risk-adjusted returns, bot interaction score
- Tier system: Bronze → Silver → Gold → Diamond → Principal
- Score decays on inactivity or bad trades (not just goes up)
- Score determines borrowing capacity (higher score = more leverage available)

### 2. Borrowing Mechanics
- Players can borrow virtual capital against their credit score
- Borrowed capital has a simulated interest rate (varies by tier)
- Auto-repayment from trade earnings (Revenue Router pattern)
- Borrowing limit scales with credit score tier
- Missed payments → score penalty → reduced limit

### 3. Risk/Failure Model
- Position sizing enforced by credit tier (can't over-leverage beyond limit)
- Liquidation engine: when unrealized loss exceeds margin, position auto-closes
- Liquidation penalty: score drop + temporary borrowing freeze
- Recovery path: trade back up, rebuild score, learn from the loss
- Game teaches: impatience + ignoring bot advisors = liquidation faster

## Architecture
```
┌─────────────────────────────────────┐
│           Agent Arena Game Engine           │
│  ┌───────────┐  ┌───────────────┐  │
│  │  Trading   │  │  Bot Advisors │  │
│  │   Engine   │  │  (guidance)   │  │
│  └─────┬─────┘  └───────┬───────┘  │
│        │                │          │
│  ┌─────▼────────────────▼───────┐  │
│  │      Credit Score Engine      │  │
│  │  (composite scoring formula)  │  │
│  └─────────────┬────────────────┘  │
│                │                   │
│  ┌─────────────▼────────────────┐  │
│  │     Borrowing Mechanics      │  │
│  │  (capital, interest, repay)  │  │
│  └─────────────┬────────────────┘  │
│                │                   │
│  ┌─────────────▼────────────────┐  │
│  │    Risk / Liquidation        │  │
│  │  (margin check, auto-close)  │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Tech Stack
- **Language:** Python (fast iteration, game logic)
- **Framework:** Terminal-based sim first, web UI later
- **Data:** SQLite for player state (scores, positions, borrow history)
- **Tests:** pytest

## Success Criteria
- [ ] Credit score engine calculates composite score from trade history
- [ ] Players can borrow capital up to their tier limit
- [ ] Auto-repayment deducts from earnings
- [ ] Liquidation triggers when margin exceeded
- [ ] Full game loop works: trade → earn → borrow → leverage → repay (or liquidate)
- [ ] All three modules have pytest coverage
