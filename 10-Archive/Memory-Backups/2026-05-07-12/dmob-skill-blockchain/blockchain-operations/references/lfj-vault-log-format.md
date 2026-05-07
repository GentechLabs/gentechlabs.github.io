---
title: LFJ-AVAX-USDC Vault Log Format
description: Daily position update format for Jordan's LFJ LP position tracking
updated: 2026-05-03
---

## File Location

`03-Projects/DeFi/LFJ-AVAX-USDC.md`

## Update Header Pattern

Each date gets its own top-level `## YYYY-MM-DD Update` section. Do NOT overwrite — append only.

## Sample Entry (May 3, 2026)

```markdown
## 2026-05-03 Update
**AVAX Price**: $9.07 (-0.18% 24h)
**Price Range**: $9.00–$9.45 (Target: $8.95–$9.36)
**Balances**: 11.64 AVAX (~$105.57) + 29.15 USDC (~$29.15) = **$134.72**
**Wallet**: 0.0969 AVAX (~$0.88) | **Combined Total**: **$135.60**
**Fees (24h)**: $0.04 (est. from pool volume ~$2.48M × 5 bps × 3.5% share)
**IL**: -17.65% (vs. HODL)
**Rewarded Bin**: ✅ Active bin 8363171 within position range [8363161–8363210]
**Efficiency**: 31.1%
**Action**: ⚠️ REVIEW NEEDED — IL exceeded 2% threshold; investigate rebalance.

**D5 Milestone Alignment**:
- Position value ($134.72) aligns with **Scout** tier ($5/day target).
- Price is inside the strategic target band ($8.95–$9.36).
- 🔴 IL 17.65% > 2% threshold → **Review required**.
- Efficiency 31.1% < 50% → Micro-DCA boost remains active.

**Other Pools**: No additional LFJ pools detected.
**Telegram Alert**: ⚠️ IL EXCEEDED 2% — Sent to -1002916759037 at 11:43 UTC.
```

## Field Reference

| Field | Source | Notes |
|-------|--------|-------|
| AVAX Price | DexScreener or on-chain | Current price used for USD conversion |
| Price Range | Tracker config range | Format: `$low–$high` |
| Balances | LP position read | `amount AVAX (~$usd_value) + amount USDC` |
| Wallet | External wallet balance | Separate from LP; included in combined total |
| Fees (24h) | Pool volume × position TVL share | If fee oracle not available, estimate from DexScreener |
| IL | Impermanent loss vs HODL | Calculated: (LP_value - HODL_value) / HODL_value |
| Efficiency | Position range utilization | For CURVE shape: `(1 - |(price-low)/(high-low) - 0.5| × 2) × 100` |
| Rewarded Bin | LFJ active bin ID | Confirms position is actively earning |
| Telegram Alert | Alert sent timestamp | UTC timestamp + channel ID |

## Triggers for New Entry

- IL ≥ 0.5% change
- Price exits configured range
- Efficiency crosses threshold (30%, 50%, 70%)
- Daily cron run (4×/day at 08:15, 12:15, 16:15, 20:15 UTC)

## Archive Policy

Entries are never deleted. Old entries remain in file history. If file exceeds 2000 lines, archive to `10-Archive/` with date-prefixed filename and reset log to current week only.

## Integration with S2S Report

The `S2S Milestone Report` generator reads this file's most recent entry to:
1. Determine `current_total` (combined LP + wallet)
2. Detect IL trend (extract from latest IL line)
3. Cross-check efficiency value (should align with state file)
4. Verify if Telegram alert was sent (for audit trail)
