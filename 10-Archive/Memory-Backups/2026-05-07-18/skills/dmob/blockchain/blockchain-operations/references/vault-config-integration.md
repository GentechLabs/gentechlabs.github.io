# Vault-Based Config Integration Pattern

**Purpose:** Store LP position configuration in a version-controlled vault location for persistence and multi-profile consistency.

## When to Use
- When you want a single source of truth for LP position parameters
- When integrating user-provided data from screenshots
- When multiple profiles need access to the same config
- For audit trail and versioning of position changes

## Configuration Structure

```json
{
  "position": {
    "range_low": 9.4,
    "range_high": 9.63,
    "shape": "Curve"
  },
  "pair": "AVAX/USDC",
  "dex": "LFJ",
  "fee_tier": 5,
  "last_updated": "2026-05-06T14:27:33.866151",
  "reserves": {
    "AVAX": 170549,
    "USDC": 2372096
  },
  "user_notes": "Rebalanced to Curve shape with tight range"
}
```

## Integration Steps

### 1. Create Vault Config File
```bash
mkdir -p /root/vaults/gentech/02-Labs/lp-config
nano /root/vaults/gentech/02-Labs/lp-config/avax-usdc-lp.json
```

### 2. Update Monitoring Scripts
Modify scripts to read from vault path instead of home directory:

```python
# Replace this:
AAE_CONFIG_PATH = os.path.join(HOME_SCRIPTS_DIR, ".lfj-aae-config.json")

# With this:
VAULT_LP_CONFIG = "/root/vaults/gentech/02-Labs/lp-config/avax-usdc-lp.json"
AAE_CONFIG_PATH = VAULT_LP_CONFIG
```

### 3. Update Cron Jobs (Optional)
Add current position parameters to cron job prompts for context:

```python
# In Defi Milestone jobs, add to prompt:
POSITION_SHAPE: Curve
PRICE_RANGE: 9.40 - 9.63
FEE_TIER: 5 bps
```

### 4. Sync Across Profiles
Each Hermes profile has its own home directory. To keep configs in sync:

```bash
# Find all copies
find /root/.hermes/profiles -name ".lfj-aae-config.json"

# Update each copy manually or use symlink
```

## User-Initiated Updates (Jordan Provides New Data)

When Jordan sends a screenshot or message with new position data:

1. **Extract parameters** from image/vision or text
2. **Update vault config** file with new values
3. **Update memory** with new range/shape
4. **Confirm with user**: price, range, position %, shape
5. **Update cron job prompts** (optional)
6. **Verify** by running the script

## Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| Multiple config copies | Use `find` to locate all; update each manually |
| Script reads wrong config | Verify with `python3 -c "import json; print(json.load(open(os.path.expanduser('~/.hermes/scripts/.lfj-aae-config.json')))['position'])"` |
| Unicode in memory replace | Add new memory entry instead of replacing |
| Vision model errors | Fallback to `tesseract` OCR extraction |

## Verification

After updating, test the script:
```bash
python3 /root/.hermes/profiles/dmob/scripts/lp-aae-signal-monitor.py
```

Should output current position with correct range and efficiency.

## References
- [LP Range Rebalance Workflow](blockchain-operations.md#6-lp-range-rebalance)
- [Unified LP Monitoring Architecture](blockchain-operations.md#7-unified-lp-monitoring-with-milestone-tracking)
- [Config Copy Debug Script](scripts/config-copy-debug.py)
- [Screenshot OCR Fallback](screenshot-ocr-fallback.md)