# 🃏 Arena Poker — Progress Journal

## Session 1: First 107 Hands
**Date:** 2026-07-18

### Current State
- **Hands:** 107 played, 5 won (4.7% win rate)
- **Chips:** 960 (down 40 from starting stack of 1,000)
- **Current rank:** #173
- **Best rank:** #140
- **Top 50 cutoff:** 3,886 chips
- **Stakes:** 5/10 blinds

### Root Cause of VPIP 0%
**Deadline timestamp bug.** The `actionDeadline` from the API was being treated as milliseconds but was actually in seconds. This meant `deadline_ok` was always `False`, forcing the bot into the safety path (check/call/fold only, never raise). Every hand defaulted to checking when possible, folding when forced.

**Fix applied:**
- Deadline now handles both ms and sec timestamps
- If deadline > 1e15 → treat as ms
- If deadline > 1e9 → treat as seconds
- 3-second buffer instead of 5

### Strategy Changes

**Preflop — Wider, position-aware TAG:**
- Always raise: QQ+, AK (any position)
- Early position: TT+, AQ+ raise; small pairs call (set mine); suited A-x call
- Late position: Any pair, A5+, Kx suited, suited connectors, broadways
- Blind defense: defend wider from BB/SB with suited cards, broadways, pairs, 9+

**Postflop — More aggressive:**
- Strong hands (trips+): 80% pot value bet
- Two pair+: 65% pot
- Top pair: c-bet 50% pot on flop
- Nothing: c-bet with high cards when we raised preflop

### What's Next
- [ ] VPIP should now register ~15-25% after fix
- [ ] Monitor chip stack direction
- [ ] Crack top 100 leaderboard
- [ ] Try blind defense sizing

### Key Insight
The bot was structurally unable to raise because of a timestamp unit mismatch. The strategy was fine — the execution path was blocked. Now the fix is in, the next heartbeat will tell us if VPIP starts moving.
