# Shape Recommendation Engine — Volatility-Based

**Added:** May 5, 2026
**Script:** `lp-aae-signal-monitor.py`
**Trigger:** Jordan noted that bid/ask shapes earn near-zero fees when price stays flat in the middle of range.

## Core Logic

```
volatility = (max(price_history_24h) - min(price_history_24h)) / mid_price * 100
```

### Recommendation Matrix

| Volatility | Current Shape | Recommendation | Rationale |
|------------|--------------|----------------|-----------|
| <2% | BIDIRECTIONAL | → CURVE | Price stable, bid/ask earns less |
| <2% | CURVE, efficiency <40% | → Narrow range | Price stable but spread too wide |
| <2% | CURVE, efficiency >70% | ✅ Optimal | Concentrated at center = max fees |
| 2-5% | CURVE, efficiency >50% | ✅ Good | Moderate swings suit CURVE |
| 2-5% | BIDIRECTIONAL, efficiency <50% | → CURVE | Efficiency low, try concentration |
| >5% | CURVE | → BIDIRECTIONAL | High volatility = swing capture wins |
| >5% | BIDIRECTIONAL | ✅ Optimal | Already correct shape |
| >10% | Any | → WIDEN + BIDIRECTIONAL | Extreme moves, range may not hold |

### Current Volatility Thresholds (in code)

```python
VOLATILITY_LOW = 2.0    # <2% = price stable
VOLATILITY_HIGH = 5.0   # >5% = high volatility
VOLATILITY_EXTREME = 10.0  # >10% = extreme
```

### Output in Human Report

```
🔬 **Shape Analysis:** Volatility 3.7% (24h)
• ✅ Position healthy — moderate volatility suits current shape
```

Appears only when recommendation is not "maintain current range" (i.e., when there's actionable advice).

### Data Source

- Uses `state["price_history"]` (last 100 hourly price points, capped at 24 for 24h window)
- If <2 data points available, volatility = 0.0 (no recommendation triggered)
- Price history is updated every hourly cron run

### Integration Point

In `lp-aae-signal-monitor.py`:
- `calc_price_volatility(price_history)` — computes volatility %
- `suggest_shape(volatility, current_shape, efficiency, price, range_low, range_high)` — returns recommendation string
- Both called in `build_aae_signal()`, results stored in `AAESignal.price_volatility_pct` and `AAESignal.shape_suggestion`
- Displayed in `format_human_report()` under "🔬 **Shape Analysis:**" heading
