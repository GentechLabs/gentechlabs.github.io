# AAE Tactical Retreat — Active Defense for LP Positions

> Strategy v0.1 | 2026-07-19
> Agentic Treasury — Yield Engine Core

## Problem

Standard LP positions earn fees until price exits the range. Once out of range, the position earns $0/day while waiting for manual rebalance. In volatile markets (macro events, Fed meetings, geopolitics), this idle time compounds into real opportunity cost.

## Solution

An active defense loop: the position deploys aggressively to earn (bid-ask at macro events), retreats to stablecoin safety when the move goes against it, and re-enters when conditions normalize.

---

## The Loop

```
DEPLOY → EARNING → BREAKOUT? → HOLD (2-5 min) → RECOVER? → RETREAT → SENTINEL → RE-ENTER
```

### Phase 1: Deploy (Bid-Ask)

- Liquidity deployed as bid-ask at the active edge
- Peak fee efficiency as price crosses the edge
- Normal LP monitoring runs every 10 min

### Phase 2: Breakout Detected

When price exits the bin range and stays out:

1. **Immediate:** Note exit time → set `defenseTimerStart`
2. **Wait 2-5 min:** Does price re-enter the range?
   - If YES → resume normal operation, reset timer
   - If NO → trigger **Phase 3**

### Phase 3: Tactical Retreat

Agent converts the LP position to 100% USDC (stablecoin):

- Withdraw LP from the pool
- Swap AVAX side to USDC
- Position sits in stablecoin — earning $0 but preserving capital
- System logs: exit price, IL realized, volume conditions

### Phase 4: Sentinel Mode

Monitor market conditions at reduced cadence (every 30 min instead of 10 min):

| Signal | Source | Threshold |
|--------|--------|-----------|
| Fear & Greed | Tradesta / CoinMarketCap | Rising from Extreme Fear (25) → Fear (35+) |
| 1h volume | DexScreener | Returning to 24h average |
| Price consolidation | Pyth / DexScreener | Price holding within a narrow range for 2+ hours |
| Macro calendar | fed-event-tracker | Next scheduled event > 48h away |

Entry signal: **3 of 4 signs positive** → Phase 5

### Phase 5: Re-enter

Agent re-deploys the position:

- Determine shape (CURVE for chop, bid-ask if next macro event < 48h)
- Set range centered on current price with appropriate width
- Deposit LP back into the pool
- Resume normal 10 min monitoring
- Log: entry price, fees earned during retreat period

---

## State Machine

```
        ┌─────────────────────────────────────────┐
        │                                         │
        ▼                                         │
┌──────────────┐    breakout?     ┌────────────┐  │
│  NORMAL (10m) │ ──────────────> │  HOLD (2-5m)│  │
│   In Range    │                 │  Timer      │  │
└──────┬───────┘                 └──────┬───────┘  │
       │                                │          │
       │ price returns       │          │          │
       │ <───────────────────┘          │          │
       │                    no return   │          │
       │                    ┌───────────┘          │
       │                    ▼                     │
       │          ┌──────────────────┐             │
       │          │    RETREAT       │             │
       │          │  100% USDC       │             │
       │          └───────┬──────────┘             │
       │                  │                       │
       │                  ▼                       │
       │          ┌──────────────────┐             │
       │          │   SENTINEL (30m) │             │
       │          │  Monitor signals  │            │
       │          └───────┬──────────┘             │
       │                  │                       │
       │       3/4 signals positive               │
       │          ┌───────────┘                    │
       │          ▼                               │
       │   ┌──────────────┐                       │
       └── │  RE-ENTER    │ ───────────────────────┘
           └──────────────┘
```

## Configuration

```json
{
  "tacticalDefense": {
    "enabled": true,
    "retreatTimerSeconds": 300,
    "sentinelIntervalMinutes": 30,
    "reEntryThreshold": 0.75,
    "signals": {
      "fearAndGreed": { "minValue": 35, "weight": 0.25 },
      "volumeStabilization": { "windowHours": 1, "weight": 0.25 },
      "priceConsolidation": { "minHours": 2, "weight": 0.25 },
      "macroCalendarClear": { "minHoursUntilNext": 48, "weight": 0.25 }
    },
    "shapes": {
      "default": "curve",
      "preMacroEvent": "bid-ask",
      "macroEventHoursBefore": 24,
      "macroEventHoursAfter": 24
    }
  }
}
```

## Integration Points

| System | Role |
|--------|------|
| **LP Monitor v2** | 10-min cadence, breakout detection, state file |
| **fed-event-tracker.py** | Macro calendar for shape selection |
| **AAE config** (.lfj-aae-config.json) | Defense mode settings |
| **defi-data.json** | Position state + defense status |
| **run-reader.sh** | On-chain verification after retreat / re-entry |
| **Tradesta signal** | Market sentiment for sentinel mode |

## Future Enhancements

- Partial retreat (50% USDC / 50% deployed)
- Multi-tier defense (retreat at -5%, hard retreat at -10%)
- Telegram alerts on each phase transition
- Backtesting against historical Fed meetings
