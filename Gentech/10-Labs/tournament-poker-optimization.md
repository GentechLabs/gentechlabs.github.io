# Tournament Poker Agent — Optimization Guide

## Architecture Decisions

### Why Daemon Mode (Continuous Loop) Over Cron Watchdog

The S8 Playground uses a cron-based watchdog (`poker_loop.py`, `* * * * *`) with 8s polling intervals and a ~4s gap between cron ticks. This works for S8 because:
- 30s action clock (enough margin for the gap)
- Lower stakes, lower variance impact

**S7 Tournament uses a continuous daemon** (`poker_tournament_daemon.py`) because:
- **20s action clock** — a 4s gap can easily miss a hand
- **Tournament variance** — one missed premium hand can cost the tournament
- **Adaptive polling**: 3s when at a table, 8s when in queue

### PID File Protection
The daemon writes a PID file to `/tmp/poker-tournament-s7.pid`. On startup, it checks for a running instance and refuses to duplicate. The cron watchdog was paused to prevent conflicts.

### Adaptive Polling Strategy

| State | Poll Interval | Rationale |
|-------|:-----------:|-----------|
| At table (acting) | 3s | Must catch 20s clock reliably with margin |
| In queue / waiting | 8s | No rush, reduces API load |
| Busted | 8s | Waiting for user to fund rebuy |

### Reasoning Field (Tournament Requirement)

The S7 tournament API requires a `reasoning` field in all action requests (S8 Playground uses `message` only). The daemon generates structured reasoning for every decision:
- Preflop: hand strength + position + stack considerations
- Postflop: hand score + pot odds + board texture
- Deadline tight: explicitly notes the clock pressure

### Rebuy Policy
**Manual only.** The tournament costs MON (real tokens) to rebuy. The daemon detects `paymentRequirements` in join responses and logs a message — it never auto-rebuys. Jordan funds and triggers rebuys manually.

## Running the Daemon

```bash
# Start
python3 /root/.hermes/profiles/gentech/scripts/poker_tournament_daemon.py &

# Stop
kill $(cat /tmp/poker-tournament-s7.pid)

# Check status
cat /root/.arena-poker-state-tournament
```

## Monitoring

State file: `/root/.arena-poker-state-tournament`
Key fields:
- `chip_state`: "available" / "locked_in_play" / "busted"
- `current_stack`: chips currently on the table
- `bankroll`: chips available in bankroll (not on table)
- `hands_played` / `hands_won`: performance stats

## Possible Improvements

1. **Stack-depth awareness**: Adjust raise sizes based on effective stack-to-pot ratio
2. **Blind-level tracking**: Account for increasing blinds in tournament structure
3. **Opponent modeling**: Track VPIP/PFR of known opponents
4. **ICM awareness**: Consider tournament payout structure for push/fold decisions
5. **Auto-rebuy toggle**: Config option for when MON wallet is funded
