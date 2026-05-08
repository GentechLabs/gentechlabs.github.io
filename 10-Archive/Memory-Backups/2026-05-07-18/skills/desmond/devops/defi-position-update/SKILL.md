---
name: defi-position-update
description: |
  Automated workflow for updating DeFi LP position parameters across all systems.
  Triggered when Jordan uploads a screenshot and says something like "rebalance to X-Y" or "new range is X-Y".
  Updates: config file, cron jobs, and memory in one shot.
category: devops
---

# DeFi Position Update Workflow

## Trigger
Jordan uploads a screenshot + provides new parameters verbally, e.g.:
- "Rebalance to curve shape, range 9.40-9.63"
- "New range 9.44-9.74, bid-ask"
- "Update to spot, 9.50-9.70"

## What to Extract
- **Shape**: Spot | Curve | Bid-Ask
- **Range**: min price – max price
- **Balance**: AVAX qty + USDC qty (from screenshot)
- **Total USD value** (from screenshot)

## Step 1 — Update Config File
```
/root/vaults/gentech/00-HQ/config/defi-lp-config.env
```
Patch these fields:
- RANGE_LOW
- RANGE_HIGH
- POSITION_USD
- SHAPE
- AVAX_QTY
- USDC_QTY
- Update the "Updated:" date in header

## Step 2 — Update Cron Jobs
Use `cronjob(action='list')` then update jobs containing LP/DeFi parameters:

Current known jobs:
- `e00b46103b08` — "Defi Milestone — LP Monitor" (YoYo)

Update the prompt with:
- New shape and range
- New balance figures
- Reference to read config file for latest params

## Step 3 — Update Memory
Use `memory(action='replace')` to update the LFJ LP entry with current params.
Keep it compact — shape, range, price, wallet. No fluff.

## Step 4 — Confirm
Post a brief summary to the group confirming all three updates.

## Pitfalls
- Memory is near capacity (~95%). Always REPLACE the existing LP entry, never ADD new.
- The cron job prompt is long — preserve all existing instructions, only update the position parameters section.
- Config file uses .env format: KEY=value, no spaces around =.
