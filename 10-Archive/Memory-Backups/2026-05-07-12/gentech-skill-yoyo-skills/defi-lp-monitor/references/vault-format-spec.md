# Vault Update Format Specification

## File Location
`/root/vaults/gentech/03-Projects/DeFi/LFJ-AVAX-USDC.md`

## Entry Template

```markdown
## YYYY-MM-DD Update
**Price Range**: $[min]–$[max] (Target: $8.95–$9.36)
**Balances**: [AVAX] AVAX (~$[USD]) + [USDC] USDC (~$[USD]) = **$[Total]**
**Fees (24h)**: $[fees_24h]
**IL**: [±X]% (vs. HODL)
**Rewarded Bin**: [✅/❌] [Price]
**Action**: [No rebalance needed | Rebalance suggested: reason]

**D5 Milestone Alignment**:
- Position value ($[value]) [aligns/does not align] with **Scout** tier ($5/day target).
- Price [is inside/is outside] the strategic target band ($8.95–$9.36).
- IL [✓ below/🔴 above] 2% threshold.
- Efficiency [✓ ≥/🔴 <] 50% → [No action / Micro-DCA boost / Rebalance needed].

**Other Pools**: [List additional positions or "None detected"]
```

## Field Definitions

| Field | Source | Format | Notes |
|-------|--------|--------|-------|
| `YYYY-MM-DD` | System date | ISO 8601 | No spaces, use current UTC date |
| `Price Range` | DexScreener pool data | `$min–$max` | Current concentrated liquidity range |
| `Target` | POOL config | Fixed `$8.95–$9.36` | Strategic band from D5 tracker |
| `Balances` | Snowtrace wallet query | `X.XX AVAX (~$XXX.XX)` | Round AVAX to 2 decimals, USD to 2 decimals |
| `Fees (24h)` | DexScreener volume estimate OR on-chain oracle | `$X.XX` | Estimate: `volume * 0.0005 * position_share` |
| `IL` | Constant product formula | `±X.X%` | Always show sign; use total IL vs. HODL |
| `Rewarded Bin` | On-chain bin tracker | `✅` or `❌` + price | Active bin within position range? |
| `Action` | Decision engine | Free text (short) | One of: "No rebalance needed", "Rebalance suggested: ...", "Rebalance needed: ..." |

## Skip Logic (When NOT to write)

Do NOT append a new entry if **all** of:
- IL change < 0.5% absolute (|ΔIL| < 0.5)
- Price remains within target range ($8.95–$9.36)
- No other material event (compounding threshold crossed, tier upgrade, etc.)

**Rationale**: Vault hygiene. Only material state changes get timestamped.

## Material Change Triggers

| Condition | Threshold | Action |
|-----------|-----------|--------|
| IL move | ≥ 0.5% | Write entry |
| Price out of range | Any | Write entry |
| IL exceeds 2% | Any | Write entry + Telegram alert |
| Efficiency drops below 50% | Any | Note in D5 alignment; may trigger entry if persistent |
| Tier upgrade | Any | Write entry |
| Compound threshold crossed | ≥ $50 | Write entry |

## Markdown Hygiene

- Use H3 heading (`##`) for date entries
- No trailing spaces on lines
- Two blank lines between sections (except within D5 alignment bullet list)
- Bold values with `**` only for totals and key metrics
- Italicize notes with `_` sparingly
- Use `✅` / `❌` emojis, not `[x]` or `[ ]`

## Example Entry (from 2026-05-03)

```markdown
## 2026-05-03 Update
**Price Range**: $9.00–$9.45 (Target: $8.95–$9.36)
**Balances**: 11.64 AVAX (~$105.79) + 29.15 USDC (~$29.15) = **$134.94**
**Fees (24h)**: $0.05
**IL**: +0.5% (vs. HODL of $134.33)
**Rewarded Bin**: ✅ Active bin 8363171 within position range [8363161–8363210]
**Efficiency**: 38.2%
**Action**: Rebalance suggested: Efficiency <50% → Micro-DCA boost triggered

**D5 Milestone Alignment**:
- Position value ($135.82) and range health align with **Scout** tier ($5/day target).
- Price is inside the strategic target band ($8.95–$9.36).
- IL +0.5% ✓ below 2% threshold.
- Efficiency 38.2% <50% → Micro-DCA boost triggered.

**Other Pools**: No additional LFJ pools detected.
```

## Validation Regex

Before writing, validate:
- Date: `^\d{4}-\d{2}-\d{2}$`
- Price range: `^\$\d+\.\d+–\$\d+\.\d+$`
- Balance: `^\d+\.\d+ AVAX \(\~\$\d+\.\d+\) \+\ \d+\.\d+ USDC \(\~\$\d+\.\d+\) \=\ \$\d+\.\d+$`
- IL: `^[\+\-]\d+\.\d+%`
- Action line: non-empty, < 100 chars

Python snippet:
```python
import re
assert re.match(r'^\d{4}-\d{2}-\d{2}$', date_str)
assert re.match(r'^\$\d+\.\d+–\$\d+\.\d+ \(Target:', range_line)
```

## Migration Notes

- Existing entries pre-2026-04-30 used different IL calculation; keep as-is for historical accuracy.
- New entries must use constant product formula.
- If updating old entries, add `[UPDATED]` tag and note formula change in comment.