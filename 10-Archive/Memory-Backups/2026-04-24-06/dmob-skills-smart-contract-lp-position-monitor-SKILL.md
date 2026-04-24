---
name: LP Position Monitor
category: smart-contract
description: DeFi LP position monitoring via DexScreener API — price range checks, fee efficiency, alert rules, and cron deployment. Reusable for any LP pair.
---

# LP Position Monitor

Monitor any DEX liquidity pool position for range status, fee efficiency, and alert when action is needed.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Cron (10m)  │────▶│ Python Script    │────▶│ Telegram    │
│ ~/.hermes/  │     │ DexScreener API  │     │ Alert       │
│ scripts/    │     │ + State File     │     │             │
└─────────────┘     └──────────────────┘     └─────────────┘
```

## Key Decisions

### Data Source: DexScreener (no auth)
- **Endpoint:** `https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}`
- **No API key needed** — public endpoint
- Returns: price, volume, liquidity, price change
- Use `curl` or `urllib.request` (Python stdlib only, no deps)

### NOT using on-chain RPC
- LFJ/Trader Joe subgraph is unreliable
- DexScreener aggregates from on-chain data with good caching
- For fee efficiency, we **calculate** from range position (no on-chain call needed)

## Alert Rules (Jordan's Spec)

| Condition | Fee Efficiency | Action |
|-----------|---------------|--------|
| ✅ In range | 75–100% | **Silent** — no alert |
| ⚠️ In range | < 75% | **Alert** — "Fee efficiency dropping" |
| ⚠️ Out of range | Any | **Wait 5 min**, recheck. Alert if still out. |
| 🌙 Quiet hours | — | **Paused** — skip checks |

### Confirmation Delay Pattern
On first out-of-range check: note the time but DON'T alert. On second consecutive check: alert. This prevents false alerts from brief dips.

State tracking:
```python
state = {
    "out_of_range_since": None,      # timestamp of first OOR
    "out_of_range_first_check": True,  # flag for confirmation
    "last_alert": None,                # cooldown tracking
    "last_price": None,
    "last_check": None
}
```

## Fee Efficiency Formula (Curve Shape)

```python
position = (price - RANGE_LOW) / (RANGE_HIGH - RANGE_LOW)
fee_efficiency = (1 - abs(position - 0.5) * 2) * 100
```

- **Center (50%)** → 100% efficiency → SILENT
- **Edge (0% or 100%)** → 0% efficiency → ALERT

## Cron Deployment

### Script Location Requirement
Cron scripts **MUST** be in `~/.hermes/scripts/` — absolute paths are rejected:
```
Error: Script path must be relative to ~/.hermes/scripts/. 
Got absolute or home-relative path. Place scripts in ~/.hermes/scripts/ 
and use just the filename.
```

Copy vault script to cron location:
```bash
cp /root/vaults/gentech/03-Strategies/scripts/lp-range-monitor.py ~/.hermes/scripts/
```

### Cron Create Pattern
```python
cronjob(
    action='create',
    name='LP Range Monitor (PAIR)',
    schedule='*/10 * * * *',          # every 10 min
    script='lp-range-monitor.py',      # filename only, not path
    deliver='telegram:CHAT_ID',
    prompt='Read script output, format alert...'
)
```

### Quiet Hours
- Built into the script (check EDT hour)
- 11PM–6:30AM → script prints "QUIET_HOURS" and exits
- No separate pause/resume cron jobs needed

## Script Template

See: `/root/vaults/gentech/03-Strategies/scripts/lp-range-monitor.py`

Core structure:
1. `is_quiet_hours()` — check EDT time
2. `fetch_pool_data()` — DexScreener API call
3. `calc_fee_efficiency(price)` — curve position math
4. State management — load/save JSON, confirmation delay
5. Output routing: SILENT / OUT_OF_RANGE_CONFIRMING / ALERT:reason + report

## Vault References
- Rules: `03-Strategies/LP-Monitor-Rules.md`
- Job Registry: `02-Labs/cron-jobs-registry.md`
- Cron Reference: `03-Strategies/Cron-Jobs-Reference.md`
- Script: `03-Strategies/scripts/lp-range-monitor.py`

## Consolidation Note
User prefers **consolidated reports** — LP pool data combined with token price watchlists in a single cron job, not separate LP-only alerts. See `consolidated-crypto-watchlist` skill for the combined pattern. When the user has an active LP position, default to the consolidated approach rather than standalone LP monitors.
