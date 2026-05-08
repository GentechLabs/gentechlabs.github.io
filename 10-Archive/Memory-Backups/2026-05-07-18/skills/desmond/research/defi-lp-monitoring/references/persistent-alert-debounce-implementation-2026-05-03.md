# Persistent Alert Debounce — Implementation Notes

**Date:** 2026-05-03  
**Agent:** Desmond (Creative) + DMOB consultation  
**Trigger:** Jordan's feedback — "the D5 milestone job runs every 10 minutes and it's getting annoying when everything's bad but no change"  

## Problem

The DeFi Milestone tracker (`defi-milestone-tracker.py`) runs every 10 minutes via cron. When conditions are persistently bad (out-of-range OR efficiency <30%), it reports in ALERT mode every cycle — causing notification spam even when nothing has changed.

## Solution

**Two-consecutive-alert debounce → silence until next hour:**
1. First alert: "Condition detected" (immediate, as always)
2. Second consecutive alert (10 min later): "Condition persists" (also sent, confirms it's not a transient)
3. Further consecutive alerts: **silenced** until the hour flips
4. Hour rollover: counter resets, next alert wins fresh slot

This provides the necessary awareness without flooding the chat.

## Code Changes Made

**File patched:** `/root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py`

### 1. State schema extension (load_state)

Added fields:
```python
"consecutive_alert_count": 0,
"alert_silence_until": None,
```

### 2. Silence-window gate (should_send_in_alert_mode)

Inserted after docstring, before active-alert checks:
```python
now = time.time()
silence_until = state.get("alert_silence_until")
if silence_until and now < silence_until:
    return False, "persistent alert silence until next hour"
```

### 3. Silence activation (after sending an alert report)

In main flow, inside `if should_send and current_mode == MODE_ALERT:`:
```python
state["consecutive_alert_count"] = state.get("consecutive_alert_count", 0) + 1
if state["consecutive_alert_count"] == 2:
    next_hour_dt = now_et().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    state["alert_silence_until"] = next_hour_dt.timestamp()
```

### 4. Silence clearance

Two places:
- **On mode exit to NORMAL** (`update_state_after_report` → `if current_mode != MODE_ALERT:`):
  ```python
  state["consecutive_alert_count"] = 0
  state["alert_silence_until"] = None
  ```
- **On hour rollover** (start of `should_send_in_alert_mode`):
  ```python
  now_ts = time.time()
  if silence_until and now_ts >= silence_until:
      state["consecutive_alert_count"] = 0
      state["alert_silence_until"] = None
  ```

## Behavior Table

| Condition state | 1st run (t0) | 2nd run (t0+10m) | 3rd–6th runs (same hour) | After hour flips |
|-----------------|--------------|------------------|--------------------------|------------------|
| **ALERT mode** (persistently bad) | SEND (count=1) | SEND (count=2 → set silence_until=next_hour) | SILENT (within window) | NEW hour → window cleared → SEND if still alert (count=1) |
| **NORMAL mode** (good) | Baseline report (subject to 2-clean-run debounce already present) | — | — | — |
| **Debounced alert fires** during silence window | **SEND regardless** (breaks through) | Resets counter to 1 | May set new silence after 2nd send | — |

## Why "2" and "until next hour"?

- **2:** You see the first alert (condition detected) and a follow-up confirming it's not a wick. That's enough context. More is noise.
- **Hour boundary:** Natural cadence marker. Provides a periodic "heartbeat" check even if condition persists all day, so you know it's still there.
- **Respects quiet hours:** The script already exits during `QUIET_HOURS` window; hour-based silence only applies during waking hours.

## Verification

Script compiles (`py_compile` OK). Cron already points to this script:

```
*/10 * * * * HERMES_HOME=/root/.hermes/profiles/yoyo /usr/bin/env python3 /root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py
```

Deployed live. Observe:  
- ALERT mode → two pings, then silence until hour change  
- NEW active debounced alert (e.g., efficiency drops further) → breaks through  

## Related Skill Sections

- `defi-lp-monitoring` SKILL.md → **Persistent Alert Debounce (Hourly Silence After Confirmation)** section (added concurrently)
- Two-Stage Alert Escalation — separate mechanism for first-detection warning → red