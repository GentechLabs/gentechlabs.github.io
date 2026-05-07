---
name: lfj-rebalance-handler
description: "Process LFJ rebalance screenshots from Jordan — parse position data, update config/state files, and flag cron jobs needing range updates."
triggers:
  - Jordan sends LFJ screenshot with rebalance note
  - Jordan mentions new range, shape change, or "rebalance"
  - Any message containing LFJ screenshot + price range numbers
tags: [defi, lfj, avax-usdc, rebalance, state-management]
---

# LFJ Rebalance Screenshot Handler

When Jordan sends an LFJ screenshot with a rebalance update, follow this workflow:

## Step 1: Parse the Screenshot

Extract from the image:
- **Current price**: `1 AVAX = X USDC`
- **New range**: Min Price – Max Price
- **Liquidity shape**: Spot / Curve / Bid-Ask
- **Position value**: Total USD, AVAX amount, USDC amount
- **Pool stats**: Liquidity TVL, 24H Volume, Fees, APR
- **Pool config**: Bin steps, Pool version, Base/Max fee

## Step 2: Update `.lfj-aae-config.json`

File: `~/.hermes/scripts/.lfj-aae-config.json`

Update the `position` object:
```json
{
  "position": {
    "total_usd": <new_total>,
    "token0_amount": <avax_amount>,
    "token1_amount": <usdc_amount>,
    "range_low": <min_price>,
    "range_high": <max_price>,
    "shape": "<spot|curve|bid-ask>"
  }
}
```

## Step 3: Update `.lfj-aae-state.json`

File: `~/.hermes/scripts/.lfj-aae-state.json`

Update these fields:
- `last_price` — from screenshot
- `last_position_usd` — from screenshot
- `last_check` — current timestamp
- Append to `price_history` — new price
- Append to `tvl_history` — new TVL
- Update `last_rebalance` object with full snapshot:
  ```json
  "last_rebalance": {
    "timestamp": "<ISO timestamp>",
    "shape": "<shape>",
    "range_low": <min>,
    "range_high": <max>,
    "position_value_usd": <value>,
    "avax_amount": <amount>,
    "usdc_amount": <amount>,
    "fees_24h_usd": <fees>,
    "liquidity_usd": <tvl>,
    "volume_24h_usd": <volume>,
    "apr_7d": <apr>
  }
  ```

## Step 4: Check Cron Jobs

The main cron job that references LP position data:
- **Defi Milestone** (`faed4f588aef`) — reads from `.lfj-aae-config.json`

If the config file is the source of truth and cron reads from it, no cron update needed.
Only update cron prompts if they have **hardcoded ranges** (check with `cronjob action=list`).

## Step 5: Confirm to Jordan

Send a brief confirmation:
```
✅ Position updated
Range: {low} – {high} | Shape: {shape}
Value: ${total} ({avax} AVAX + {usdc} USDC)
APR: {apr}% | 24H Fees: ${fees}
```

## Pitfalls

- **Don't overwrite the entire config** — only update the `position` section
- **Don't reset state history** — append to arrays, don't replace
- **Timestamp format** — use ISO 8601 with timezone offset
- **If Jordan mentions "took profit"** — note the position decrease, don't treat as error
- **Shape names must match LFJ**: `spot`, `curve`, `bid-ask` (lowercase, hyphenated)

## Verification

After updating, read back both files to confirm writes succeeded:
```bash
cat ~/.hermes/scripts/.lfj-aae-config.json | python3 -m json.tool
cat ~/.hermes/scripts/.lfj-aae-state.json | python3 -m json.tool
```
