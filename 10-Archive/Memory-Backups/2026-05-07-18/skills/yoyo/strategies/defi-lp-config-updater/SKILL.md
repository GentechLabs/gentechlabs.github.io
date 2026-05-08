---
name: defi-lp-config-updater
version: 1.0.0
displayName: DeFi LP Configuration Updater
overview: Automatically update AVAX/USDC LP configuration when user provides new range and shape data.
description: This skill provides a procedure for updating the DeFi LP configuration files when the user provides new range and shape parameters from screenshots or manual input. It handles parsing, validation, file updates, and confirmation.
icon: 
---
# DeFi LP Configuration Updater

This skill enables automatic updating of the AVAX/USDC LP configuration when the user provides new range and shape data from screenshots or manual input.

## Trigger Conditions
- User provides new liquidity range and shape information
- User says things like: "Update range to X-Y, shape Z" or "New range is X-Y, shape is Z"
- User uploads a screenshot with accompanying data about the LP position

## Procedure

### 1. Parse User Input
Extract the new range (low and high values) and shape from the user's message.

**Patterns to recognize:**
- `Update range to 9.40-9.63, curve`
- `New range is 9.40-9.63, shape curve`
- `Range: 9.40-9.63, Shape: curve`
- `Rebalanced to 9.40-9.63 with curve shape`

### 2. Validate Inputs
- Ensure range_low < range_high
- Ensure shape is one of: `curve`, `spot`, `bidirectional`

### 3. Update Configuration Files
- **Main config**: `/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json`
  - Update `position.range_low`
  - Update `position.range_high`
  - Update `position.shape`
- **State file**: `/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-range-state.json`
  - Update `range_low`
  - Update `range_high`
  - Update `position_shape`

### 4. Verify Changes
- Read back the config files to confirm updates
- Display old vs new values to user

### 5. Notify User
- Confirm that the configuration has been updated
- Inform that cron jobs will pick up changes on next run
- Optionally offer to trigger an immediate run

## Files Modified
- `.lfj-aae-config.json` (main strategy configuration)
- `.lfj-range-state.json` (monitoring state)

## Validation
After update, verify:
- Config file contains new values
- State file contains new values
- No syntax errors in JSON

## Example Usage
User: "Hey YoYo, I've updated my LFJ AVAX/USDC position. New range is 9.40-9.63 with curve shape."
Agent: 
1. Parse: range_low=9.40, range_high=9.63, shape=curve
2. Update files
3. Respond: "✅ DeFi LP config updated successfully! Old: 9.25-9.54 (curve) → New: 9.40-9.63 (curve)"

## Error Handling
- If files not found: report error and suggest manual update
- If validation fails: explain issue and ask for corrected values
- If write fails: report error and suggest checking permissions

## Notes
- The cron job `Defi Milestone` runs every 10 minutes and will automatically use the new configuration
- No need to restart the cron job manually; it reads the config fresh each run
- For immediate effect, the user can wait for the next scheduled run or trigger it manually via appropriate command

## Related Skills
- `cron-job-management`
- `defi-lp-monitor-operations`
- `strategies/cron-consolidation`