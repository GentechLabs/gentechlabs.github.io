# Milestone Tracker State Schema

## Primary State File
`~/.hermes/scripts/.lfj-milestone-tracker.json`

## Schema
```json
{
  "total_fees_earned": 0.00,
  "milestones_reached": [1, 2],
  "last_milestone": {"tier": 2, "label": "Raider", "reached_at": "2026-05-01T12:00:00Z"},
  "fee_history": [
    {"timestamp": "2026-04-27 19:48 EDT", "fees": 0.03, "price": 9.2509, "efficiency": 32.7}
  ],
  "session_start": "2026-04-27T23:48:48.553557+00:00",
  "current_tier": 2,
  "next_tier_threshold": 20.0,
  "progress_pct": 12.5
}
```

## Fields
| Field | Type | Meaning |
|-------|------|---------|
| `total_fees_earned` | float | Cumulative USD fees since tracking began |
| `milestones_reached` | array[int] | List of tier numbers achieved |
| `last_milestone` | object | Most recently crossed tier (tier, label, timestamp) |
| `fee_history` | array[object] | Daily fee snapshots (timestamp, fees, price, efficiency) |
| `session_start` | ISO 8601 | When current tracking session began |
| `current_tier` | int | Convenience field — highest reached tier |
| `next_tier_threshold` | float | Daily fee target to reach next tier |
| `progress_pct` | float | Percent progress to next tier (0–100) |

## Cross-Reference with Config
- Milestone definitions live in `.lfj-aae-config.json` → `milestones[]` array
- Daily fee target for tier N = `milestones[N-1].daily_fees` (1-indexed)
- Compound threshold = `.lfj-aae-config.json` → `compound_threshold_usd`

## Update Pattern
```python
def update_milestone_tracker(state, daily_fees_earned, config):
    milestones = config['milestones']
    current_tier = state.get('current_tier', 0)
    
    # Check if we crossed a tier
    for m in milestones:
        if daily_fees_earned >= m['daily_fees'] and m['tier'] > current_tier:
            state['milestones_reached'].append(m['tier'])
            state['last_milestone'] = {
                "tier": m['tier'],
                "label": m['label'],
                "reached_at": datetime.utcnow().isoformat() + "Z"
            }
            state['current_tier'] = m['tier']
    
    # Update progress % to next tier
    next_tier = next((m for m in milestones if m['tier'] > current_tier), None)
    if next_tier:
        state['next_tier_threshold'] = next_tier['daily_fees']
        prev_tier_fees = next((m['daily_fees'] for m in milestones if m['tier'] == current_tier), 0)
        tier_range = next_tier['daily_fees'] - prev_tier_fees
        state['progress_pct'] = ((daily_fees_earned - prev_tier_fees) / tier_range) * 100
    
    return state
```
