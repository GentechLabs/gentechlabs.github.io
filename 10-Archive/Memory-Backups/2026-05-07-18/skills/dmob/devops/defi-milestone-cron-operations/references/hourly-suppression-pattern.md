# Hourly Suppression Pattern for High-Frequency Monitors

**Context:** The DeFi Milestone job runs every 10 minutes but should not spam "OK" status messages. Instead, it broadcasts at most one OK-status per hour after an initial stabilization period.

## State Schema

```json
{
  "consecutive_ok_count": 0,
  "last_ok_hour": null
}
```

- `consecutive_ok_count`: Incremented on each clean run (no alerts). Reset to 0 on any alert.
- `last_ok_hour`: The hour (0–23 ET) of the last OK-status broadcast. Subsequent runs in the same hour are suppressed once `consecutive_ok_count >= 2`.

## Decision Logic (insert in `main()` after `check_alerts()`)

```python
# Reload state to capture any updates from check_alerts (debounces, timestamps)
state = load_state()
now = now_et()
state.setdefault("consecutive_ok_count", 0)
state.setdefault("last_ok_hour", None)

if alerts:
    # Any alert breaks silence and resets the OK-counter
    state["consecutive_ok_count"] = 0
    should_send = True
else:
    # No alerts → clean run
    state["consecutive_ok_count"] += 1
    if state["consecutive_ok_count"] < 2:
        should_send = True  # first 2 OK runs always send
    elif state.get("last_ok_hour") != now.hour:
        should_send = True  # hour changed → send one more
    else:
        should_send = False  # suppress
    if should_send:
        state["last_ok_hour"] = now.hour

if not should_send:
    save_state(state)  # persist counter before silent exit
    sys.exit(0)
```

## Rules

1. **First 2 clean runs:** always send OK-status (establishes baseline stability)
2. **After 2+ clean runs in same hour:** suppress output (silent)
3. **On hour change:** one OK-status allowed (resumes notification)
4. **Any alert:** breaks silence, resets `consecutive_ok_count` to 0, and sends immediately
5. **Quiet hours:** checked earlier in `main()` — exits before this logic if in quiet window

## Rationale

- Avoids missing slow-developing issues (first two runs confirm stability)
- Reduces noise: at most ~1 notification per hour instead of 6 per hour during stable periods
- Compatible with existing debounce logic (5-minute out-of-range/efficiency confirmations)
- Works with quiet hours (ET-based) as a separate pre-filter

## Applied In

- **Script:** `03-Strategies/scripts/d5-lp-consolidated.py` (DeFi Milestone + LP Monitor)
- **Job ID:** `3258c64b` (every 10 min, 6 AM–11 PM UTC)
- **Deployed:** 2026-05-03

## Testing Notes

See `references/hourly-suppression-test-2026-05-03.md` for manual test runs demonstrating:
- Initial OK send (count=1 → send)
- Second OK send (count=2 → send, sets `last_ok_hour`)
- Subsequent runs suppressed (count=3,4,5 → silent)
- Hour-flip unblocks (different `last_ok_hour` → send)
- Alert breaks silence and resets counter
