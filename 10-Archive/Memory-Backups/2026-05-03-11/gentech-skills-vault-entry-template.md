# Vault Entry Template — DeFi LP Monitoring

Copy this skeleton, fill placeholders, and append to `03-Projects/DeFi/LFJ-AVAX-USDC.md`.

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

---

## Filled Example

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

---

## Placeholder Values

| Placeholder | Type | Description |
|-------------|------|-------------|
| `YYYY-MM-DD` | date | UTC date of report |
| `X.XXXX` | float | AVAX price to 4dp |
| `LOW/HIGH` | float | Config range boundaries, 2dp |
| `AVAL` | float | AVAX amount in LP, 2dp |
| `USDC_USD` | float | USDC amount in LP, 2dp |
| `TOTAL` | float | LP position value, 2dp |
| `WALLET_AVAX` | float | Native AVAX outside LP, 4dp |
| `WALLET_USD` | float | Wallet USDC value (if any), 2dp |
| `COMBINED` | float | LP + wallet total, 2dp |
| `FEES` | float/money | 24h fees estimated, 2dp (or 4dp if <0.01) |
| `METHOD_NOTE` | string | e.g. `"(est. from volume × 5 bps × 0.015% share; on-chain oracle not configured)"` |
| `BIN_ID`, `START`, `END` | int | Active bin and position range bin IDs |
| `ACTION_TEXT` | string | One of the [Rebalance Triggers](SKILL.md#6-rebalance-triggers) |
