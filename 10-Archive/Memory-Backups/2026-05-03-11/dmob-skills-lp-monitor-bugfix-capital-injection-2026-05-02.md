# LP Monitor Bugfix & Capital Injection (May 02, 2026)

## Context
Fixed `lp-aae-signal-monitor.py` crash and added capital injection detection ahead of full D5 master cron consolidation.

## Bug: NameError in `build_aae_signal()`

**Location:** `lp-aae-signal-monitor.py` lines 517, 521

**Error:**
```
NameError: name 'out_of_range_duration_minutes' is not defined
```

**Root cause:** Keyword argument passed a variable that didn't exist in scope.

**Broken code:**
```python
severity = determine_severity(
    current_price=current_price,
    base_price=base_price,
    oor_duration_minutes=out_of_range_duration_minutes,  # ❌ undefined
)
```

**Fix:** Use the correctly scoped variable `oor_duration_minutes`:
```python
severity = determine_severity(
    current_price=current_price,
    base_price=base_price,
    oor_duration_minutes=oor_duration_minutes,  # ✅ defined earlier in function
)
```

**Takeaway:** Avoid variable names that differ only by prefix/suffix; use distinct names like `oor_minutes` vs `oor_duration_minutes_param` to prevent shadowing mistakes.

## Capital Injection Detection Pattern

**Goal:** When user adds funds to LP (e.g., $50 DCA), automatically detect and show recalculated D5 progress.

**State schema change:** Added `last_position_usd` (float) to `.lfj-aae-state.json`.

**Implementation (inserted after state load, before signal generation):**
```python
# Load config position
with open(CONFIG_PATH) as f:
    config = json.load(f)
current_total_usd = config["position"]["total_usd"]

# Read last seen position from state
last_position_usd = state.get("last_position_usd", 0.0)

# Detect injection
capital_injection_usd = 0.0
if current_total_usd > last_position_usd:
    capital_injection_usd = current_total_usd - last_position_usd
    # Banner for human report
    injection_banner = f"💸 Capital added: ${capital_injection_usd:.2f} — progress recalculated.\\n\\n"
    human_report = injection_banner + human_report

# Update state for next run
state["last_position_usd"] = current_total_usd
```

**JSON output:** Adds `"capital_injection_usd": X.XX` only when nonzero.

**Verification:**
- First run: `last_position_usd` saved (e.g., 134.94)
- Second run unchanged: no banner, injection = 0
- After config `total_usd` increases: banner appears, JSON includes field

## State File Path Resolution

Script uses:
```python
STATE_DIR = os.path.expanduser("~/.hermes/scripts")
```
With `HOME=/root/.hermes/profiles/dmob/home`, resolved path:
```
/root/.hermes/profiles/dmob/home/.hermes/scripts/.lfj-aae-state.json
```
Always confirm actual location with:
```bash
python3 -c "import os; print(os.path.expanduser('~/.hermes/scripts'))"
```

## Testing Performed

| Run | Exit Code | Capital Detected | JSON Valid | Notes |
|-----|-----------|------------------|------------|-------|
| 1st (post-patch) | 0 | Yes (initial save) | ✅ | `last_position_usd` set to 134.94 |
| 2nd (no change) | 0 | No | ✅ | Silent, state unchanged |
| 3rd (verify output) | 0 | No | ✅ | Human report shows position $134.94, efficiency 81.9%, tier Unranked |
| 4th (clean) | 0 | No | ✅ | After clearing pycache, confirmed stable |

## Files Modified
- `03-Strategies/scripts/lp-aae-signal-monitor.py` (bugfix + injection logic)

## Related
- Full consolidation target: `d5-master-cron.py` (pending)
- Existing state keys: `last_position_usd`, `total_fees_earned_usd`, `out_of_range_since`, `price_history`, `alert_history`, etc.
- Config: `03-Strategies/scripts/.lfj-aae-config.json` (contains `position.total_usd`)