# Out-of-Range Debounce Pattern

## Problem
LP positions frequently ping-pong across range boundaries due to volatility. Need to avoid false alerts.

## Requirements (Jordan)
1. **Wait 10 minutes to confirm** — only start alert process after sustained out-of-range
2. **Wait 5 more minutes (grace)** — after 10 min confirmed, send WATCH level alert, then if still out after 5 more min, escalate to RED alert
3. **If re-entered before 10 min** — clear state, status = OK, no alert

## State Tracking
Add to state file (`.lfj-aae-state.json` or dedicated range state):
```json
{
  "out_of_range_since": null,
  "out_of_range_status": "OK",   // OK | CONFIRMING | WATCH | CRITICAL
  "last_range_check": "2026-05-02T10:21:26Z"
}
```

## Implementation
```python
OUT_OF_RANGE_CONFIRM_SECONDS = 600   # 10 minutes
OUT_OF_RANGE_GRACE_SECONDS = 300      # 5 minutes (after confirm)

def check_out_of_range(price, range_low, range_high, state):
    in_range = range_low <= price <= range_high
    now = time.time()
    
    if in_range:
        # Reset everything if we're back in range
        state['out_of_range_since'] = None
        state['out_of_range_status'] = 'OK'
        return {'status': 'OK', 'message': 'In range'}
    
    # We are out of range
    if state.get('out_of_range_since') is None:
        # First time out — start confirmation timer
        state['out_of_range_since'] = now
        state['out_of_range_status'] = 'CONFIRMING'
        elapsed = 0
    else:
        elapsed = now - state['out_of_range_since']
    
    if state['out_of_range_status'] == 'CONFIRMING':
        if elapsed >= OUT_OF_RANGE_CONFIRM_SECONDS:
            # Confirmed out-of-range after 10 min
            state['out_of_range_status'] = 'WATCH'
            urgency = 'WATCH'
        else:
            # Still in confirmation period
            urgency = 'OK'  # silent
    elif state['out_of_range_status'] == 'WATCH':
        if elapsed >= (OUT_OF_RANGE_CONFIRM_SECONDS + OUT_OF_RANGE_GRACE_SECONDS):
            # Grace period passed — critical alert
            state['out_of_range_status'] = 'CRITICAL'
            urgency = 'CRITICAL'
        else:
            # In grace period — warning level
            urgency = 'WATCH'
    else:  # CRITICAL
        urgency = 'CRITICAL'
    
    minutes_elapsed = round(elapsed / 60, 1)
    return {
        'status': state['out_of_range_status'],
        'urgency': urgency,
        'minutes_out_of_range': minutes_elapsed,
        'message': f'Out of range for {minutes_elapsed} min'
    }
```

## Severity Mapping
| `out_of_range_status` | Alert Severity | Action |
|-----------------------|----------------|--------|
| `OK` | SILENT | Nothing |
| `CONFIRMING` (0–10 min) | SILENT | Wait |
| `WATCH` (10–15 min) | ALERT | "Position out of range — rebalance recommended" |
| `CRITICAL` (15+ min) | CRITICAL | "URGENT: Position out of range for 15+ minutes — immediate rebalance needed" |

## Edge Cases
- **Price flaps in/out rapidly:** Resets timer on every re-entry — prevents alert spam
- **Script restarts:** State persists to disk; timer survives process restart
- **Quiet hours:** If alert would fire during quiet hours, defer until quiet hours end (use `quiet_hours` config)
- **Already in range at startup:** Initialize `out_of_range_since = None`, run one check to set baseline

## Integration with Unified Monitor
```python
range_check = check_out_of_range(price, range_low, range_high, state)
severity = determine_severity(
    in_range=range_check['status'] == 'OK',
    efficiency=efficiency,
    ...,
    out_of_range_status=range_check['status'],
    ...
)
```

## Testing
```python
# Simulate 20-minute out-of-range event
state = {}
for minute in range(20):
    price = 8.90  # below range_low of 8.95
    result = check_out_of_range(price, 8.95, 9.36, state)
    print(f"Minute {minute}: {result['status']} — {result.get('message','')}")
```
Expected output:
- 0–9 min: CONFIRMING (silent)
- 10–14 min: WATCH (alert)
- 15+ min: CRITICAL (red alert)
