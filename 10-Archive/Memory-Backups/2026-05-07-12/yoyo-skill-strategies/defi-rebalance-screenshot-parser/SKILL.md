---
name: defi-rebalance-screenshot-parser
version: 1.0.0
displayName: DeFi Rebalance Screenshot Parser
description: Automatically extract range and shape from LFJ rebalance screenshots and update all relevant cron jobs. Parses the actual values from the screenshot as source of truth.
icon: 
---
# DeFi Rebalance Screenshot Parser

This skill automatically parses LFJ liquidity management screenshots to extract the actual range and shape, then updates all relevant cron jobs and configuration files.

## Trigger Conditions
- User uploads an LFJ liquidity management screenshot
- User mentions rebalancing, updating range, or changing position
- Screenshot shows the "Manage" tab with price range inputs

## Procedure

### 1. Screenshot Analysis
**Extract from screenshot:**
- **Min Price** (from "Min Price:" field)
- **Max Price** (from "Max Price:" field)
- **Liquidity Shape** (which option is selected: Spot, Curve, or Bid-Ask)
- **Num Bins** (optional, for reference)

**Look for these UI elements:**
- Input fields labeled "Min Price:" and "Max Price:"
- Slider positions (visual confirmation)
- Selected shape option (highlighted/selected state)
- Active bin price for validation

### 2. Validate Extracted Values
- Ensure min_price < max_price
- Ensure values are numeric and reasonable (typically within ±50% of current price)
- Cross-validate with active bin price shown in screenshot

### 3. Update Configuration Files
- **Main config:** `/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json`
  - Update `position.range_low`
  - Update `position.range_high`
  - Update `position.shape`
- **State file:** `/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-range-state.json`
  - Update `range_low`
  - Update `range_high`
  - Update `position_shape`

### 4. Update All Relevant Cron Jobs
- **Defi Milestone** (ID: `3258c64b`)
  - Runs every 10 minutes
  - Uses `.lfj-aae-config.json` for range/shape
  - Automatically picks up changes on next run

### 5. Verification and Confirmation
- Read back configuration files to confirm updates
- Display old vs new values
- Show timestamp of when changes will take effect
- Optionally trigger immediate run for verification

## Screenshot Parsing Rules

### Price Extraction
- Look for "Min Price:" label followed by numeric value
- Look for "Max Price:" label followed by numeric value
- Values may appear as: `8.86174444`, `9.44`, `10.27454713`
- Ignore currency symbols ($, USDC) - just extract numbers

### Shape Detection
- **Spot:** Single vertical bar at center
- **Curve:** Bell curve shape (highest at center)
- **Bid-Ask:** Two peaks at edges, valley in middle
- Look for which option is highlighted/selected in the UI

### Validation Cross-Check
- Active bin price should be between min and max
- If extracted values seem off, ask user to confirm
- Typical ranges: ±1-5% from current price

## Example Usage

**User uploads screenshot showing:**
- Min Price: 9.44
- Max Price: 9.74
- Bid-Ask selected

**Agent response:**
```
✅ Rebalance Screenshot Parsed Successfully!

📍 Extracted Values:
   Range: 9.44 - 9.74
   Shape: Bidirectional (Bid-Ask)
   Width: 0.30 (3.1% of range)

🔄 Updating Configuration Files:
   ✅ .lfj-aae-config.json updated
   ✅ .lfj-range-state.json updated

⏰ Changes Effective: Immediately (next cron run ~10 min)

📊 Position Analysis:
   Current Price: ~9.609
   Position: In range (centered)
   Efficiency: Will recalculate on next check
```

## Error Handling

### If Range Cannot Be Extracted
- Ask user to manually provide min/max values
- Show what was detected in the screenshot
- Offer to use manual input instead

### If Values Seem Invalid
- Warn if range width is <0.5% or >20% of price
- Warn if min > max
- Ask for confirmation before applying

### If Screenshot is Unclear
- Request clearer screenshot
- Ask user to zoom in on price inputs
- Offer manual input as fallback

## Files Modified
- `.lfj-aae-config.json` (main strategy configuration)
- `.lfj-range-state.json` (monitoring state)

## Integration Points
- **Defi Milestone cron job** - Reads from config files
- **LP Monitor scripts** - Use same configuration
- **Alert system** - Uses range for out-of-range detection

## Notes
- Screenshot is always the source of truth
- User message provides context, screenshot provides data
- Always validate extracted values before applying
- Keep history of range changes for audit trail