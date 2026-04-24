# LP Monitor Update — April 19, 2026

## What Changed
- **Range:** Updated to $9.0061 - $9.4068
- **Shape:** Set to **Curve** (liquidity concentrated in center)
- **Active Bin:** ~$9.19
- **Alert Logic:** Curve-specific — silent in center, alert at edges, confirm breakout after 5 min

## Why Changed
Jordan rebalanced his LFJ AVAX/USDC position with a new range and curve distribution shape.

## New Alert Rules
| Condition | Action |
|-----------|--------|
| Price in center (~$9.10-$9.30) | 🔇 Silent |
| Price near edges ($9.00-$9.10 or $9.32-$9.40) | ⚠️ Low fee efficiency |
| Out of range (>5 min) | 🚨 Confirmed breakout |
| >3% price move | 🚨 Alert |

## Cron Job
- Job ID: `400f99be0cad`
- Schedule: `*/10 * * * *` (every 10 min)
- State file: `/opt/hermes-agents/desmond/cache/lp_monitor_state.json`
