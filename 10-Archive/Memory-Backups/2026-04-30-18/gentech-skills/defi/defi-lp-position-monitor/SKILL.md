---
name: defi-lp-position-monitor
description: "Recurring lightweight DeFi LP position monitoring via off-chain APIs (CoinGecko, DexScreener), with Obsidian vault skip-logic, milestone/D5 alignment checks, and Telegram summary reporting. Designed for cron jobs where full on-chain web3.py reads are unnecessary."
tags: [defi, lp, cron, vault, dexscreener, coingecko, lfj, avalanche, skip-logic]
trigger: "When asked to run, set up, or maintain a recurring DeFi LP watchlist + position monitor job. Use whenever you need: lightweight price alerts, pool status summaries, vault-reported LP metrics, D5/milestone alignment checks, or skip-logic driven cron updates that avoid redundant vault appends."
version: 1.0.0
author: Gentech
related_skills:
  - defi-onchain-position-reader    # deep on-chain web3.py variant
  - market-macro-monitor           # price watchlist tooling only
  - defi-lp-strategy-designer      # systematic strategy design, not recurring ops
---

# DeFi LP Position Monitor (Lightweight / Cron)

Run a recurring LP position + watchlist report using only off-chain APIs, apply vault skip-logic to avoid noise, and flag for milestone review when thresholds are breached.

## When to Use vs. On-Chain Reader

| Situation | Use This Skill | Use `defi-onchain-position-reader` |
|---|---|---|
| Daily cron, price alerts, summary | Yes — lightweight | Overkill — slow |
| Per-bin breakdown, share-of-pool | No — lacks granularity | Yes — web3.py reads |
| Rebalance decision needs exact reserves | No — approximate only | Yes — accurate |
| Mobile/low-bandwidth context | Yes — few API calls | No — heavy RPC |

## Data Sources

### CoinGecko (free, no key)
```bash
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2,joe,usd-coin&vs_currencies=usd&include_24hr_change=true"
```
- Use for watchlist prices and 24h changes.
- Batch all token IDs in a single call.
- Note: CoinGecko IDs are not ticker symbols (e.g., `avalanche-2`, not `AVAX`).

### DexScreener (free, no key)
```bash
curl -s "https://api.dexscreener.com/latest/dex/pairs/avalanche/{POOL_ADDRESS}"
```
- Use for pool volume, TVL, priceNative, priceChange, active bin proxy (priceUsd).
- Verify pool address has contract code before trusting data. If DexScreener returns empty, the address may be stale.

## Workflow (One Cron Run)

1. **Fetch watchlist prices** (CoinGecko)
   - Flag 1.5%+ 24h moves. Skip smaller changes in the report.

2. **Fetch pool data** (DexScreener)
   - Record: `priceUsd`, `priceChange.h24`, `volume.h24`, `liquidity.usd`.
   - Verify pool address matches config. If DexScreener returns `pairs: null`, the address may be wrong — log the error to the vault and abort.

3. **Estimate wallet-level fees** (approximate)
   ```python
   total_fees_24h = volume_24h * fee_rate  # e.g., 0.0005 for 5 bps
   share = position_usd / pool_tvl
   est_wallet_fees = total_fees_24h * share
   ```
   - This is intentionally approximate. Flag in the report: `Est Fees: ~${value}`.

4. **Apply skip-logic before vault update**
   - Compare current price vs. last vault entry price.
   - If `|delta| < 0.5%` AND `IL < 0.5%` AND price within declared target range → **skip vault append**.
   - Never skip if: IL ≥ 1.0% (review), price exited range (review), milestone threshold hit, or fees exceeded compound threshold.

5. **D5 / Milestone Alignment**
   - Load milestone config JSON (e.g., `.lfj-aae-config.json` in scripts path).
   - Check:
     - Current tier active?
     - Daily fees vs. tier target?
     - IL ≥ 2%? Flag for review.
     - Price outside strategic band for >12h? Flag for review.
     - Efficiency ≥ 50%? If yes, no micro-DCA needed.
   - Record: `Tier: X`, `Status: ✅ Stable / ⚠️ Review Needed`, `Next Tier: Y`.

6. **Write vault entry (only if not skipped)**
   - File: `/root/vaults/gentech/03-Projects/DeFi/LFJ-AVAX-USDC.md`
   - Append using ISO 8601 datestamp header (YYYY-MM-DD).
   - Template below.

7. **Telegram summary**
   - Deliver to configured group.
   - Always include: watchlist prices, pool status (✅ Stable / ⚠️ Review Needed), flagged alerts, vault link.

## Vault Entry Template

```markdown
## 2026-04-30 Update
**AVAX Price**: $[X.XX]
**Price Range**: $[min]–$[max] (Target: $[target_min]–$[target_max])
**Balances**: [X.XX] AVAX (~$[USD]) + [XX.XX] USDC (~$[USD]) = **$[Total]**
**Wallet**: [X.XXXX] AVAX (~$[USD]) | **Combined Total**: **$[Total]**
**Fees (24h)**: $[fees_24h]  *est. from pool volume*
**IL**: [±X]% (vs. HODL)
**Rewarded Bin**: ✅ Active bin [ID] within position range ([N] bins total)
**Efficiency**: [X]%.
**Action**: No rebalance needed / Rebalance suggested: [reason]

**D5 Milestone Alignment**:
- Position value ($[value]) aligns with **[Tier]** tier.
- Price is inside the strategic target band ($[X]–$[Y]) and the config range ($[A]–$[B]).
- IL is well below the 2% review threshold.
- Micro-DCA trigger: Efficiency ≥50% → no bonus DCA required.

**Other Pools**: [List any additional LFJ pools, or "No additional pools detected."]
```

## D5 Milestone Tracker File

Create a separate tracker file at:
`/root/vaults/gentech/03-Projects/DeFi/D5-Milestone-Tracker.md`

Include:
- Tier table (Tier, Label, Daily Target, Status)
- Strategic goals (range, IL threshold, compound threshold, DCA efficiency trigger)
- Rebalance history log

This keeps the main LP vault file focused on per-run telemetry, while the tracker holds strategic context.

## Skip-Logic Rules

| Condition | Action |
|---|---|
| Price delta < 0.5% + IL < 0.5% + in-range | Skip vault append |
| IL ≥ 1.0% | Append vault, flag review |
| Price exits range | Append vault, flag review |
| Milestone tier achieved | Append vault, celebrate |
| Compound threshold met ($50+) | Append vault, flag compound |
| DCA day + efficiency < 50% | Append vault, flag boost DCA |
| Any API call fails | Append vault with error block, notify |

## Error Handling

When an API fails mid-run:
1. Log the failure into the vault entry under an `**Errors**` block.
2. Include the HTTP status or exception message.
3. Flag `Action: Review needed — data incomplete`.
4. Always deliver the Telegram summary mentioning the partial data / error.

## Multi-Pool Monitoring

If additional pools exist (e.g., AVAX/JOE, USDC/JOE):
1. Repeat step 2 for each pool address.
2. Summarize in the "Other Pools" section of the vault entry.
3. If no other pools have active positions for the wallet, explicitly state: `No additional LFJ pools detected with active positions for this wallet.`

## Cron Frequency

Recommended: **4× daily** to catch intraday volatility without being noisy.
- 08:15 UTC — morning check
- 12:15 UTC — midday check
- 16:15 UTC — afternoon check
- 20:15 UTC — evening check

Use the system cron or Hermes cron jobs. On each run, always execute skip-logic independently; do not chain state between runs.

## Key Files

| File | Purpose |
|---|---|
| `/root/.hermes/scripts/.lfj-aae-config.json` | Pool address, D5 milestones, DCA config, alert rules |
| `/root/vaults/gentech/03-Projects/DeFi/LFJ-AVAX-USDC.md` | Live telemetry vault |
| `/root/vaults/gentech/03-Projects/DeFi/D5-Milestone-Tracker.md` | Strategic goals + rebalance history |

## Pitfalls

- **Wrong pool address in runbook:** Always verify the DexScreener response before writing vault data. If `pairs` is null, the address is stale or a typo — use the config address instead.
- **CoinGecko rate limits:** If you get 429, wait 60s or switch to CoinMarketCap if an API key is available.
- **Fee estimation is not on-chain:** It assumes uniform fee distribution. Flag it as estimated, not exact.
- **Skipping too aggressively:** Never skip on errors or threshold breaches. Skip-logic is for stable, in-range, low-IL days only.

## Example Telegram Output

```
📊 YoYo Crypto Watchlist + LP Report [2026-04-30 16:34 UTC]

💰 Price Watchlist (24h)
• AVAX: $9.11 (-0.18%) — stable
• JOE: $0.0463 (+3.51%) ⚠️
• USDC: $0.9996 (-0.02%) — pegged

🔔 JOE +3.51% (>1.5%)

🔹 LFJ AVAX/USDC Pool ✅ Stable
• AVAX Price: $9.11 | Range: $8.95–$9.36
• 24h Pool Volume: $2.72M | Est Fees: ~$0.38
• IL ~0.0% | Action: No rebalance needed

🎯 D5 Milestone: Scout ($3/day) | IL <2% ✅

📝 Vault: /root/vaults/gentech/03-Projects/DeFi/LFJ-AVAX-USDC.md
🎯 D5 Tracker: /root/vaults/gentech/03-Projects/DeFi/D5-Milestone-Tracker.md
```
