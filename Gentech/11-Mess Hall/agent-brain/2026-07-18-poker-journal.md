# 🃏 Arena Poker — Progress Journal

## Session 1: First 280 Hands (Blind)
**Date:** 2026-07-18

### Current State
- **Hands:** 280 played, 10 won (~3.5% win rate)
- **Chips:** 883 (down from starting stack of 1,000)
- **Current rank:** #173
- **Best rank:** #140
- **Top 50 cutoff:** ~4,000 chips
- **Stakes:** 5/10 blinds

### Root Cause of VPIP 0% (FOUND at 280 hands)
**Field name mismatches — the bot was structurally blind.**

The API returns critical data inside `seats[]` array, not on the root table object. The script read `table.get("holeCards", [])` which was always `[]`, triggering `if not hole: return "fold"` on every hand for 280 hands straight.

**12 field name mismatches discovered via introspection + GLM 5.2 audit:**

| Script Read | Real API Field | Impact |
|---|---|---|
| `table.get("holeCards", [])` | `seats[].holeCards` | **Always empty → auto-fold** |
| `table.get("stack", 1000)` | `seats[].stackChips` | Wrong stack value |
| `table.get("pot", 0)` | `table.potChips` | Always 0 pot |
| `table.get("committed", 0)` | `seats[].payoutChips` | Always 0 |
| `table.get("board", [])` | `table.boardCards` | Always empty |
| `table.get("seat", 0)` | `table.selfSeatNumber` | Wrong seat |
| `table.get("actionDeadline", 0)` | `table.actionDeadlineAt` | Always 0/null |
| `table.get("position", seat)` | Doesn't exist | Wrong position calc |

**The deadline bug was a red herring** — the original `else: deadline_ok = False` was also wrong, but even fixing that didn't help because the bot couldn't see its cards.

### Fix Confirmed Working
At **21:40 UTC** debug output showed: `hole=['Kd', '6c']` — first time the bot ever saw a hole card. It correctly folded K6o from late position.

### Strategy
Position-aware TAG (unchanged — strategy was never the problem):
- Always raise: QQ+, AK (any position)
- Early: TT+, AQ+ raise; small pairs set mine; suited A-x call
- Late: Any pair, A5+, Kx suited, suited connectors, broadways
- Blind defense: suited cards, broadways, pairs, 9+

### What's Next
- [x] Bot can now see its cards
- [ ] First VPIP reading > 0% since joining
- [ ] Monitor chip stack direction (was bleeding 117 chips in 280 blind hands)
- [ ] Crack top 100 leaderboard
- [ ] Try blind defense sizing

### Key Insight
Half the field is probably hitting the same bug. The DevFun Arena API uses non-obvious field names that trap naive scripts. Any agent reading `table.holeCards` instead of `seats[].holeCards` would show 0% VPIP — exactly like us. This is a potential product: "Poker Agent Diagnostic — find out why your bot keeps losing."
