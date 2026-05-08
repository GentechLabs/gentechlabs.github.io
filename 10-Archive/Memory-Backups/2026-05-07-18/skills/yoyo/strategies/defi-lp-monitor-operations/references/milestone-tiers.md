# LFJ Milestone Tiers

## Config Location
`/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json` → `milestones[]`

## Tiers

| Tier | Label | Daily Fees | Shapes Unlocked | Notes |
|------|-------|------------|-----------------|-------|
| 1 | Scout | $5.00 | CURVE | Entry level. Current target. |
| 2 | Raider | $20.00 | SPOT + BIDIRECTIONAL | Needs 4x current volume |
| 3 | Warlord | $50.00 | Multi-pool | Requires multi-pool positions |
| 4 | Sovereign | $100.00 | Custom + mentorship | Top tier |

## Scout Progress Bar Calculation

Source files:
- `cumulative_fees_est` → `.lfj-position-tracker.json`
- Scout threshold → `.lfj-aae-config.json` → `milestones[0].daily_fees` (5.0)

```
progress_pct = min(cumulative_fees_est / 5.00 * 100, 100)
bar_filled = round(progress_pct / 10)  # 0-10 blocks
bar = "█" * bar_filled + "░" * (10 - bar_filled)
```

Output format:
```
🎯 Scout Progress
[████████░░] 46% — $2.29 / $5.00 daily fees
```

## Cron Integration

The cron job `3258c64b` ("Defi Milestone") appends this section to the script output. The prompt instructs the LLM to:
1. Run `d5-lp-consolidated.py` and forward output as-is
2. Read position tracker + config for fee data
3. Calculate and append the Scout progress bar
4. Add NO other sections (no reward bin, no price watch)

## Position Tracker Fields

```json
{
  "cumulative_fees_est": 2.29,  // Total fees earned since entry
  "entry_date": "2026-03-31",
  "entry_avax_price": 8.85,
  "last_rebalance": "2026-04-27"
}
```

## Open Questions

- Does `cumulative_fees_est` reset on rebalance? (Currently doesn't seem to)
- Is there an API to pull actual on-chain fee accumulation vs estimate?
- How does squad contribution affect milestone calculation? (config has `squad.contribution_pct: 100.0`)
