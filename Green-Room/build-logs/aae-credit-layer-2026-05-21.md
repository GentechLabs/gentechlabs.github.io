# AAE Credit Layer — Build Log
**Date:** 2026-05-21
**Status:** ✅ Shipped
**Repo:** `/root/workspace/aae-game/`

## What We Built
Complete credit layer for the AAE trading simulation game. Three interconnected modules that teach real DeFi mechanics without real money.

## Modules

### Credit Score Engine (`credit_engine.py` — 172 LOC)
- Composite 0-1000 scoring from: win_rate, trades, account_age, risk-adjusted return, bot_interaction
- 5 tiers: Bronze (0-100) → Silver (100-300) → Gold (300-600) → Diamond (600-850) → Principal (850+)
- Inactivity decay, score penalties for defaults

### Trading Engine (`trading.py` — 190 LOC)
- Spot buy/sell with position tracking
- Average price averaging on multiple buys
- PnL calculation, win/loss counting, trade history

### Borrowing Mechanics (`borrowing.py` — 264 LOC)
- Tier-based borrow limits (0.5x-5x balance)
- Simple daily interest accrual
- Revenue Router pattern: 30% of PnL auto-repays debt
- Missed payment detection → score penalty → reduced limit

### Risk & Liquidation (`risk.py` — 233 LOC)
- Margin tracking per position
- Configurable liquidation threshold
- Auto-close positions when margin breached
- Liquidation penalty: score drop + 7-day borrow freeze
- Recovery path: rebuild score through successful trades

### Game Loop (`game.py` — 318 LOC)
- Turn-based flow: interest → missed payments → liquidation → display → bot advisor → action → score
- Terminal UI with emoji status
- Bot advisors with contextual tips ("you're overleveraged", "consider selling")

## Tests
**73/73 passing** across 5 test files:
- `test_credit_engine.py` — scoring, tiers, decay, penalties
- `test_trading.py` — buy/sell/PnL/trade history
- `test_borrowing.py` — limits, interest, auto-repay, defaults
- `test_risk.py` — margin checks, liquidation, portfolio summary
- `test_integration.py` — full game loop flows

## Total: 2,263 LOC (1,280 source + 983 tests)
