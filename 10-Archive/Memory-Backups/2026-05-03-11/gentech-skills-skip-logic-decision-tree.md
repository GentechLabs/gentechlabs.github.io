# Skip Logic Decision Tree — LFJ LP Monitoring

## Purpose

Avoid noisy vault updates. Only append a timestamped entry when a **material change** has occurred since the last report.

## Material Change Definition

A change is **material** when ANY of these holds:

1. **IL delta ≥ 0.5 percentage points**  
   `|il_current - il_last| ≥ 0.5`  
   Example: IL moved from `0.0%` → `+1.1%` (delta = 1.1 ≥ 0.5) → **material**

2. **Price outside strategic target band**  
   `price < TARGET_LOW` OR `price > TARGET_HIGH`  
   Example: target `$8.95–$9.36`, price `$9.50` → **material**  
   Once out-of-range, subsequent entries **always material** until price returns

3. **Efficiency threshold crossed**  
   `efficiency ≥ 50%` previously → now `< 50%` (OR reverse)  
   Example: `74%` → `42%` (crossed below 50%) → **material**  
   Staying on same side of 50% → **not material**

4. **Rewarded bin status change**  
   `active_bin_in_range` flipped `True → False` (or vice versa)  
   Example: previously `✅`, now `❌` due to price drift beyond bin coverage → **material**

5. **Fee value jump ≥ $0.10**  
   Only applies when last entry had a **numeric** fee value (not `unavailable`).  
   Example: `$0.03` → `$0.19` (delta $0.16) → **material**

## Skip Condition

Skip update if **ALL** are true:

```python
skip = (
    abs(il_delta) < 0.5 and
    target_low <= price <= target_high and
    (efficiency >= 50) == (last_efficiency >= 50) and   # same side of threshold
    bin_status_unchanged and
    same_calendar_day(last_date, current_date)           # not first entry of day
)
```

**Exception — first entry of day**: If no entry exists for today's date, **force write** even if skip conditions all true. This maintains daily cadence.

## Decision Flowchart

```
                                ┌─────────────────────┐
                                │  Read last vault     │
                                │  entry (prev)        │
                                └──────────┬──────────┘
                                           │
                                ┌──────────▼──────────┐
                                │  Compute:           │
                                │  - IL_delta         │
                                │  - price_in_target? │
                                │  - eff_cross_50?    │
                                │  - bin_status_same? │
                                │  - fee_delta        │
                                └──────────┬──────────┘
                                           │
                   ┌───────────────────────┼───────────────────────┐
                   │                       │                       │
         IL_delta ≥0.5?             price_out_of_target?         eff_cross_50?
                   │                       │                       │
            YES ──┼─────┐          YES ──┼─────┐          YES ──┼─────┐
                   │      │                 │      │                 │
         [MATERIAL] │      │         [MATERIAL] │      │         [MATERIAL]
                   │      │                 │      │                 │
        bin_status_change?        bin_status_change?        fee_delta ≥0.10?
                   │      │                 │      │                 │
        YES ──┼─────┐  NO ─┼─────>  YES ──┼─────┐  NO ─┼─────>  YES ──┼─────┐
               │      │            │      │            │      │
         [MATERIAL] [EVAL]    [MATERIAL] [EVAL]    [MATERIAL] [EVAL]
                   │      │            │      │            │      │
        ANY material found? ──NO──> SKIP (no vault write)
                   │
                 YES
                   │
          APPEND VAULT ENTRY
```

## Examples

### Example 1 — IL crosses threshold (write)
```
Last entry May 1:  IL = 0.0%, efficiency 74%, in-range, fees $0.03
Current:           IL = +1.1%, efficiency 42%, in-range, fees $0.19
→ IL_delta = 1.1 ≥ 0.5  →  MATERIAL
→ Write new entry.
```

### Example 2 — Stable, no change (skip)
```
Last entry May 1:  IL = +1.1%, efficiency 42%, out-of-range? no, fees $0.19
Current:           IL = +1.2%, efficiency 43%, in-range, fees $0.21
→ IL_delta = 0.1 < 0.5
→ Efficiency cross? no (both <50%)
→ In range? yes
→ Bin status same? yes
→ Fee delta $0.02 < $0.10
→ ALL skip conditions true → SKIP
```

### Example 3 — Price exit target (always material)
```
Last entry: price $9.10 (in $8.95–$9.36)
Current:  price $9.50 (above $9.36)
→ Outside target band → MATERIAL (must write and flag for review)
```

### Example 4 — First entry of the day (force write)
```
Date: 2026-05-02 08:15 — no prior entry on this date
→ Last entry was May 1 20:15
→ Force write regardless of materiality (normalizes daily cadence)
```

## Edge Cases

| Edge case | Decision |
|-----------|----------|
| Last entry is 2+ days old (missed run) | Force write — catch-up |
| IL sign flips but magnitude similar (e.g., `-0.3%` → `+0.3%`, delta=0.6) | Material (sign flip matters) |
| Efficiency fluctuates 49%→51%→49% same day | Each cross triggers write; subsequent re-cross same day → material again |
| Bin status `✅` → `❌` → `✅` on same run (rare, price volatile) | Any status change → material (write) |
| Fees jump from `unavailable` → `$0.19` | Material (newly measurable) |

## Why Not Simpler Thresholds?

Strict threshold skip logic would miss meaningful regime shifts (e.g., efficiency dropping from 74% → 42% crosses 50% even if IL only moved 0.3%). The multi-criteria approach captures:

- **Trend acceleration** (IL delta)
- **Structural breach** (price out-of-range)
- **Capital degradation** (efficiency)
- **Protocol state change** (bin/active reward)

This aligns with D5 milestone trigger philosophy: track *strategic posture* not just point-in-time numbers.

---

*Reference — update when skip logic thresholds or D5 alignment rules evolve*
