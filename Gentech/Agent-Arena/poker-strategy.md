# 🃏 Gentech Poker Arena Strategy

## Overview

Two-bot multi-competition approach on DevFun Arena. Each competition runs its own script watchdog — independent, no cross-contamination.

| Competition | File | Polling | Action Clock | Rebuy Cost |
|---|---|---|---|---|
| [Poker] Playground S8 | `scripts/poker-playground-s8.py` | 4 × 8s per tick | 30s | Free |
| [Poker] Tournament S7 | `scripts/poker-tournament-s7.py` | 4 × 8s per tick | 20s | MON (~$0.02/ea) |

## Architecture

Script-based watchdog pattern (no_agent cron):
- **Cron fires every minute** → Python script runs
- **Script loops internally**: 4 polls × 8s intervals = 32s active window per tick
- **Silent by default** — only prints output on bust/error events
- **Hourly heartbeat** summarizes performance to HQ

## Hand Strategy (TAG)

**Preflop** — Tight-Aggressive:
- Premiums (QQ+, AK): raise always
- Mid pairs (TT-JJ) + AQ+: raise in position
- Small pairs: set mine with 20BB+ effective
- Suited connectors: call in position
- Trash: fold

**Postflop** — Value-oriented:
- Trips+: big value bets (80% pot)
- Two pair: 65% pot value
- Top pair: 50% c-bet on dry boards
- Nothing: check it down, tiny c-bet range only with big cards

**Deadline fallback**: check > call > fold (never timeout)

## Tournament-Specific Rules

- **20s action clock** (vs 30s in Playground) — tighter deadline buffer set to 4s
- **Free entry, paid rebuys** — bot prints bust message, waits for Jordan's approval to rebuy (never auto-rebuys with MON)
- **Elimination format** — one champion remains; leaderboard is by total chips

## Known Issues & Fix History

- **Jul 18: VPIP 0% bug** — `holeCards` was being read from `table` root instead of `seats[]`. Also `availableActions` not `actions` inside `allowedActions`. Fixed, VPIP now reading 3.57%.
- **Jul 18: Single-poll latency** — Original script only polled once per minute. Both scripts upgraded to 4 × 8s internal polling.

## State Files

- `/root/.arena-poker-state` — Playground S8
- `/root/.arena-poker-state-tournament` — Tournament S7

## Cron Jobs

| Job | ID | Schedule |
|---|---|---|
| Playground S8 Watchdog | `eb0dea9a772c` | `* * * * *` |
| Tournament S7 Watchdog | `63338e126293` | `* * * * *` |
| Poker Heartbeat (1hr summary) | `2052d444a593` | `30 9-23/1 * * *` |
