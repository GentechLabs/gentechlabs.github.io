# Vault Entry Template — DeFi LP Monitoring

Copy this skeleton, fill placeholders, and append to `03-Projects/DeFi/LFJ-AVAX-USDC.md`.

## Active Position Template

```markdown
## YYYY-MM-DD Update
**AVAX Price**: $X.XXXX
**Price Range**: $LOW–$HIGH (Target: $TARGET_LOW–$TARGET_HIGH)
**Balances**: AVAL AVAX (~$AVAX_USD) + USDC_USD USDC (~$USDC_USD) = **$TOTAL**
**Wallet**: WALLET_AVAX AVAX (~$WALLET_USD) | **Combined Total**: **$COMBINED**
**Fees (24h)**: $FEES (METHOD_NOTE)
**IL**: {+/-}X.X% (vs. HODL of $HODL_TOTAL)
**Efficiency**: X.X%
**Action**: ACTION_TEXT

**D5 Milestone Alignment**:
- Position value ($VALUE) aligns with **TIER_LABEL** tier ($DAILY_TARGET/day target).
- Price {inside/outside} strategic target band ($TARGET_LOW–$TARGET_HIGH).
- IL {IL_STATUS}.
- Efficiency {EFF_STATUS}.

**Other Pools**: {POOLS_STATEMENT}
```

## Withdrawn Position Template

Use when on-chain scan returns zero positions (see Phase 2 — Empty Position Detection):

```markdown
## YYYY-MM-DD Update
**AVAX Price**: $X.XXXX (+X.XX% 24h) ⚠️ PRICE ALERT (if >1.5%)
**LP Position**: 🚨 **EMPTY** — No active LFJ position detected on-chain
**Wallet**: WALLET_AVAX AVAX (~$WALLET_USD) + WALLET_USDC USDC (~$USDC_USD) = **$COMBINED**
**Fees (24h)**: $0.00 (no active position)
**IL**: N/A (position withdrawn)
**Efficiency**: N/A
**Action**: 🚨 CRITICAL: LP position withdrawn — wallet holds only dust balances.

**D5 Milestone Alignment**:
- 🚨 **No active position** — Scout tier suspended until position is re-established.
- AVAX $PRICE is {inside/outside} target band $TARGET_LOW–$TARGET_HIGH.
- IL: N/A.
- Efficiency: N/A.

**Other Pools**: No additional LFJ pools detected with active positions for this wallet.

**Recent Transactions** (YYYY-MM-DD):
- HH:MM UTC: X.XXX AVAX sent to 0x...
```

---

## Filled Example (Active Position)

```markdown
## 2026-05-02 Update
**AVAX Price**: $9.0951
**Price Range**: $9.00–$9.45 (Target: $8.95–$9.36)
**Balances**: 11.16 AVAX (~$101.48) + 33.47 USDC (~$33.47) = **$134.95**
**Wallet**: 0.0969 AVAX (~$0.88) | **Combined Total**: **$135.83**
**Fees (24h)**: $0.19 (est. from volume × 5 bps × 0.015% share; on-chain oracle not configured)
**IL**: +1.1% (vs. HODL of $134.33)
**Efficiency**: 42.2%
**Action**: Rebalance suggested: IL +1.1% + efficiency <50% → DCA trigger

**D5 Milestone Alignment**:
- Position value ($135.83) aligns with **Scout** tier ($3/day target).
- Price inside strategic target band ($8.95–$9.36).
- IL 1.1% ✓ below 2% threshold.
- Efficiency 42.2% <50% → Micro-DCA boost triggered.

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.
```

## Filled Example (Withdrawn Position)

```markdown
## 2026-05-05 Update
**AVAX Price**: $9.4000 (+2.84% 24h) ⚠️ PRICE ALERT
**LP Position**: 🚨 **EMPTY** — No active LFJ position detected on-chain
**Wallet**: 0.0971 AVAX (~$0.91) + 0.000009 USDC (~$0.00) = **$0.91**
**Fees (24h)**: $0.00 (no active position)
**IL**: N/A (position withdrawn)
**Efficiency**: N/A
**Action**: 🚨 CRITICAL: LP position withdrawn — wallet holds only dust balances.

**D5 Milestone Alignment**:
- 🚨 **No active position** — Scout tier suspended until position is re-established.
- AVAX $9.40 is OUTSIDE target band $9.25–$9.59 (above upper bound).
- IL: N/A.
- Efficiency: N/A.

**Other Pools**: No additional LFJ pools detected with active positions for this wallet.

**Recent Transactions** (2026-05-05):
- 12:49 UTC: 8.207 AVAX sent to 0x18556da13313f3532c54711497a8fedac273220e
- 11:13 UTC: 6.822 AVAX sent to 0x18556da13313f3532c54711497a8fedac273220e
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
| `ACTION_TEXT` | string | One of the [Rebalance Triggers](SKILL.md#6-rebalance-triggers) |
