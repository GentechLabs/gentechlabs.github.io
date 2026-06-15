# DeFi Dashboard Sync — Agent Kit Template

> Universal template for auto-updating DeFi dashboards from a single position input.
> Part of GenTech Agent Kit — DevOps & Automation bundle.

## What This Does

**Single input → full sync.** When you provide LP position data (range, shape, balances, fees), this template updates ALL files automatically:

1. Dashboard data source (JSON)
2. Dashboard renderer (HTML)
3. Hub embedded tab (HTML)
4. LFJ config (JSON)
5. Cron job script (Python)
6. Environment config (env)
7. Trading journal (Markdown)

## The Pattern

```
User Input (screenshot or text)
  ↓
Extract Position Data
  ↓
Calculate Derived Values (efficiency, bins, milestones)
  ↓
Update All 7 Files (parallel patches)
  ↓
Commit + Push
  ↓
Verify (deploy-and-verify)
  ↓
Report
```

## Input Format

```
Shape: [bidirectional/curve/spot]
Range: [low] - [high]
Balance: [AVAX] AVAX + [USDC] USDC
Fees 24h: $[amount]
```

## Efficiency Calculation

| Shape | Center | Edges | Logic |
|-------|--------|-------|-------|
| Curve | High (100%) | Low (0%) | Bell curve, maximum at center |
| Bid-Ask | Low (0%) | High (100%) | U-shape, maximum at edges |
| Spot | 100% everywhere | 100% | Single point, all-or-nothing |

## Curve Bin Generation

### Bid-Ask (U-Shape)
- Edges: depth 0.95-1.0
- Center: depth 0.05
- Transitions: smooth gradient

### Curve (Bell Shape)
- Center: depth 1.0
- Edges: depth 0.05
- Transitions: smooth gradient

## File Update Templates

Each file has known patterns to replace. The skill uses `patch` for targeted updates.

### Key Constants to Update
```
RANGE_LOW, RANGE_HIGH, SHAPE, AVAX_QTY, USDC_QTY, POSITION_USD
```

### Key Sections to Update
- `hero` section in defi-data.json
- `lpPosition` section in defi-data.json
- `curveData.bins` array in defi-data.json
- `POOL` dict in defi-master-cron.py
- `position` object in .lfj-aae-config.json
- Constants in hub.html
- Hardcoded range in defi-dashboard.html

## Agent Kit Usage

To adapt this template for your own LP position:

1. **Copy this skill** to your Hermes profile
2. **Update file paths** to match your project structure
3. **Update pool data** (address, chain, fee tier)
4. **Keep the same pattern** — 7-file sync, curve generation, efficiency calc

**The pattern is universal.** The specifics are configurable.

## Revenue Integration

This skill pairs with the Agent Node Network:
- Each sync operation = a "task" that can be verified
- Dashboard shows sync history (like blockchain blocks)
- Earnings tracked per sync operation
- Reputation built on sync accuracy and speed
