# Vault Entry Format Specification — LFJ LP Monitoring

## Field Reference

| Field | Required | Format | Source | Notes |
|-------|----------|--------|--------|-------|
| `## YYYY-MM-DD Update` | ✅ | `## 2026-05-02 Update` | date | top-level H2 header |
| `**AVAX Price**` | ✅ | `$9.0951` | CMC/DexScreener | 4dp |
| `**Price Range**` | ✅ | `$9.00–$9.45` | config position range | en dash, no spaces |
| `Target` | ✅ | `$8.95–$9.36` | D5 milestone tracker | inside parenthetical |
| `**Balances**` | ✅ | `11.16 AVAX (~$101.48) + … = **$134.95**` | on-chain decode | bold total |
| `**Wallet**` | ✅ | `0.0969 AVAX (~$0.88)` | Routescan/RPC | include dust |
| `**Combined Total**` | ✅ | `**$135.83**` | sum | bold |
| `**Fees (24h)**` | ✅ | `$0.19 (est. …)` | volume × 5bps × share | note oracle status |
| `**IL**` | ✅ | `+1.1% (vs. HODL of $134.33)` | calc vs entry deposit | sign included |
| `**Rewarded Bin**` | ✅ | `✅ Bin 8363172 within [8363161–8363210]` | on-chain check | or `❌` |
| `**Efficiency**` | ✅ | `42.2%` | avg share pct | 1dp |
| `**Action**` | ✅ | text | rule-based | see triggers |
| `**D5 Milestone Alignment**` | ✅ | 4 bullets | D5 tracker | required block |
| `**Other Pools**` | ✅ | static sentence | detection result | must appear |

## Negative Examples (do NOT use)

❌ `**Price Range**: $9.00 - $9.45` (use en-dash `–`)
❌ `**Balances**: 11.16 AVAX ($101.48) + 33.47 USDC ($33.47) = 134.95` (total must be bold)
❌ `**IL**: 1.1%` (missing sign and HODL baseline)
❌ `**Fees**: $0.1909` (no estimation note; over-precise)
❌ `Action: No rebalance` (missing trailing period, should be `No rebalance needed.`)
❌ `other pools: …` (lowercase label; must be `**Other Pools**`)

## Template Skeleton

```markdown
## YYYY-MM-DD Update
**AVAX Price**: $X.XXXX
**Price Range**: $LOW–$HIGH (Target: $TARGET_LOW–$TARGET_HIGH)
**Balances**: AVAL AVAX (~$AVAX_USD) + USDC_USD USDC (~$USDC_USD) = **$TOTAL**
**Wallet**: WALLET_AVAX AVAX (~$WALLET_USD) | **Combined Total**: **$COMBINED**
**Fees (24h)**: $FEES (METHOD_NOTE)
**IL**: {+/-}X.X% (vs. HODL of $HODL_TOTAL)
**Rewarded Bin**: {✅/❌} Bin BIN_ID within position range [START–END]
**Efficiency**: X.X%
**Action**: ACTION_TEXT

**D5 Milestone Alignment**:
- Position value ($VALUE) aligns with **TIER_LABEL** tier ($DAILY_TARGET/day target).
- Price {inside/outside} strategic target band ($TARGET_LOW–$TARGET_HIGH).
- IL {IL_STATUS}.
- Efficiency {EFF_STATUS}.

**Other Pools**: {POOLS_STATEMENT}
```

## Example (Complete)

```markdown
## 2026-05-02 Update
**AVAX Price**: $9.0951
**Price Range**: $9.00–$9.45 (Target: $8.95–$9.36)
**Balances**: 11.16 AVAX (~$101.48) + 33.47 USDC (~$33.47) = **$134.95**
**Wallet**: 0.0969 AVAX (~$0.88) | **Combined Total**: **$135.83**
**Fees (24h)**: $0.19 (est. from volume × 5 bps × 0.015% share; on-chain oracle not configured)
**IL**: +1.1% (vs. HODL of $134.33)
**Rewarded Bin**: ✅ Bin 8363172 within position range [8363161–8363210]
**Efficiency**: 42.2%
**Action**: Rebalance suggested: IL +1.1% + efficiency <50% → DCA trigger

**D5 Milestone Alignment**:
- Position value ($135.83) aligns with **Scout** tier ($3/day target).
- Price inside strategic target band ($8.95–$9.36).
- IL 1.1% ✓ below 2% threshold.
- Efficiency 42.2% <50% → Micro-DCA boost triggered.

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.
```
