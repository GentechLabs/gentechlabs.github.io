---
name: LP Position Data Integration
author: DMOB
created: 2026-05-06
description: Automatically integrate user-provided liquidity position parameters into DeFi monitoring cron jobs for real-time tracking and risk assessment
---

# LP Position Data Integration

## Purpose
Automatically incorporate user-provided liquidity position parameters (shape, range, fee tier, etc.) into DeFi monitoring cron jobs for real-time position tracking and risk assessment.

## Trigger Conditions
When user uploads a screenshot of an LFJ/AVAX-USDC position AND provides explicit parameters:
- Liquidity shape (Spot, Curve, Bid-Ask)
- Price range (min/max)
- Fee tier (bps)
- Current price context
- Any recent rebalancing actions

## Integration Protocol

### 1. Data Extraction & Validation
- Parse shape, range, and fee tier from user input
- Validate numerical ranges (min < max, reasonable bin counts)
- Cross-reference with current market price from DEX oracle
- Flag any inconsistencies or high-risk configurations

### 2. Cron Job Updates

#### For "Defi Milestone" jobs (Morning/Evening):
Update the prompt with current position parameters:
```
# Current Position Parameters
POSITION_SHAPE: [Curve/Spot/Bid-Ask]
PRICE_RANGE: [min] - [max]
FEE_TIER: [bps]
CURRENT_PRICE: [price]
RESERVES: [AVAX] AVAX, [USDC] USDC
```

#### For "LP Position Monitor Hourly" script:
Modify `lp-aae-signal-monitor.py` to read from a config file:
```python
# Load position config
with open('/root/vaults/gentech/02-Labs/lp-config/avax-usdc-lp.json') as f:
    config = json.load(f)

CURRENT_SHAPE = config['shape']
CURRENT_RANGE = config['range']
CURRENT_FEE_TIER = config['fee_tier']
```

### 3. Config File Management
Create/update JSON config at `/root/vaults/gentech/02-Labs/lp-config/avax-usdc-lp.json`:
```json
{
  "position": {
    "range_low": 9.44,
    "range_high": 9.74,
    "shape": "bidirectional"
  },
  "pair": "AVAX/USDC",
  "dex": "LFJ",
  "fee_tier": 5,
  "last_updated": "[timestamp]",
  "reserves": {"AVAX": 170549, "USDC": 2372096},
  "user_notes": "Rebalanced to Bid-Ask shape with new range 9.44-9.74"
}
```

### 4. Vault-Wide Update Protocol
When updating position parameters, search and update ALL of these files:
1. **Working Memory**: `/root/vaults/gentech/00-Working-Memory.md`
2. **DeFi Milestones**: `/root/vaults/gentech/03-Projects/defi-milestones.md`
3. **LP Monitor Scripts**: `/root/vaults/gentech/03-Strategies/scripts/lp-range-monitor-v3.py`
4. **Daily Summaries**: `/root/vaults/gentech/11-Mess Hall/daily/*.md`
5. **Memory Backups**: `/root/vaults/gentech/10-Archive/Memory-Backups/*/dmob-memory-MEMORY.md`
6. **Context Files**: `/root/vaults/gentech/11-Mess Hall/2026/W*/today-context.md`

**Search Pattern**: Look for old range patterns like `9.25–9.59`, `9.40–9.63`, `9.25-9.59`, `9.40-9.63` and replace with current range.

### 5. Risk Flagging
If position parameters indicate high risk:
- **Tight range** (<±5%): Flag for frequent rebalancing needs
- **High fee tier** (>0.3%): Flag for potential toxic flow exposure
- **Low bin count**: Flag for capital inefficiency
- **Large position size**: Flag for liquidity mining optimization

### 5. Notification Integration
When config is updated, trigger immediate:
- Update to monitoring cron job prompts
- Refresh of any active dashboards
- Optional alert to user if risk parameters exceed thresholds

## Verification Steps
1. Confirm config file exists and is readable
2. Validate cron job prompts contain current parameters
3. Test script execution with new config
4. Check for any syntax errors in updated files

## Maintenance
- Config file should be version-controlled
- Changes should be logged with timestamps
- User should be able to manually override via direct command