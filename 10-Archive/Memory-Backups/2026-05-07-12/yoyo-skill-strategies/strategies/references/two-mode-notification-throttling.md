# Two-Mode Notification Pattern — D5 LP Monitoring (May 3, 2026)

## Context

Script: `/root/.hermes/profiles/yoyo/scripts/d5-lp-consolidated.py`
Pool: LFJ AVAX/USDC 5bps (Curve-shaped concentrated LP)
User directive: *"if nothing has changed to much, keep silent"* + *"once an hour after crypto watch list. Every 10 mins if it's below 30 fee efficiency or out of range warn 1 time and wait 5 mins to confirm breakout and send red alert to rebalance."*

## Problem

Original script ran every 10 minutes and sent a report on every run. This created notification spam during normal conditions (efficiency >70%, in range) while still needing rapid alerts when position health degraded.

## Solution Architecture

### Three-State Machine

```
IDLE (quiet hours) → NORMAL → ALERT → NORMAL
            ↑           |         |
            └───────────┴─────────┘  (recovery)
```

- **IDLE**: 23:00–06:00 ET — script exits silently regardless of mode
- **NORMAL**: Health thresholds met — hourly throttled updates, material-change gated
- **ALERT**: Efficiency <30% or price out of range — immediate warning, 5-min debounce, then red alerts

### State File Layout

Path: `$HERMES_HOME/home/.hermes/scripts/.lfj-d5-state.json`
(Note: In May 2026, `HERMES_HOME = /root/.hermes/profiles/yoyo/home`)

```json
{
  "mode": "normal",
  "last_price": 9.1600,
  "efficiency": 94.1,
  "range_low": 9.00,
  "range_high": 9.30,
  "in_range": true,
  "efficiency_zone": "zone_70_plus",
  "last_normal_sent_at": 1714736400.0,
  "warning_sent_at": null,
  "out_of_range_warning_sent": null,
  "last_alert_snapshot": null,
  "last_update": "2026-05-03T16:40:00-04:00"
}
```

### Material Change Thresholds (NORMAL mode)

A change is **material** if any:
- Price moved ≥1% from `last_price` **OR** ≥$0.20 absolute
- `efficiency_zone` changed (e.g., `zone_70_plus` → `zone_50_70`)
- `in_range` flipped (true → false or false → true)
- New alert flags appear: `efficiency < 30` OR `out_of_range`
- First run (no prior state)

Implementation: `significant_change_detected(state, position, new_alerts)`

### Alert Debounce + Suppression (ALERT mode)

1. **Entry**: Condition first detected → send immediate warning, record `warning_sent_at = now_ts`, no snapshot yet.
2. **Debounce wait**: For 5 minutes after warning, no further messages (script exits quietly).
3. **Red alert**: After 5 min, if condition persists → create alert snapshot → send red alert with suggested action → clear `warning_sent_at`.
4. **Subsequent checks**: Compare current metrics vs `last_alert_snapshot`. Only send if:
   - New alert type appears, OR
   - Price moved ≥1% / ≥$0.20, OR
   - Efficiency changed ≥5 percentage points, OR
   - In-range status flipped
5. **Recovery**: Condition clears → send recovery message → mode returns to NORMAL, state cleaned.

### Cron Schedule Strategy

Current: `*/10 6-23 * * *` (every 10 minutes, 6am–11pm ET)

Rationale for keeping high-frequency cron:
- ALERT mode needs 10-minute checks to catch rapid degradation
- NORMAL mode self-throttles to hourly, so cron overhead is minimal (script exits early)
- Alignment with crypto watchlist is handled within script, not via cron coordination

If watchlist schedule becomes known (e.g., runs at :55 past hour), adjust D5 cron offset by setting minutes explicitly:
```bash
# Example: run at :02, :12, :22, ... (just after watchlist at :55)
*/10 6-23 * * * 2
```
(But note: cron doesn't support offset directly; need explicit list like `2,12,22,32,42,52` if precise ordering matters.)