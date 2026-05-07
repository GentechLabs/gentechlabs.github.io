# LFJ AVAX/USDC Vault Entry Template

**Copy this template and fill in the current-price sections.**

**Date format**: `YYYY-MM-DD` (ISO 8601, zero-padded)

**Required fields (all must be present):**
- `## YYYY-MM-DD Update` (header)
- `**AVAX Price**: $X.XXXX (±X.XX% 24h)` — from DexScreener or CoinGecko
- `**Price Range**: $min–$max (Target: $8.95–$9.36)` — computed from bin positions
- `**Balances**: N AVAX (~$USD) + M USDC (~$USD) = **$TOTAL**` — from position scan
- `**Wallet**: 0.0969 AVAX (~$0.89) | **Combined Total**: **$TOTAL+wallet**` — include native AVAX
- `**Fees (24h)**: $value` — estimated or unavailable note
- `**IL**: ±X.X% (vs. HODL of $baseline)` — impermanent loss
- `**Rewarded Bin**: ✅/❌ description` — whether current rewards bin overlaps position
- `**Efficiency**: X%` — share_pct weighted average
- `**Action**: ...` — rebalance suggestion or no-action
- `**D5 Milestone Alignment**:` — bullet points tying to tier thresholds
- `**Other Pools**: ...` — usually "None detected"
- Separator: `---` after entry

**Template:**

```markdown
## YYYY-MM-DD Update
**AVAX Price**: $9.XXXX (±X.XX% 24h)
**Price Range**: $X.XX–$X.XX (Target: $8.95–$9.36)
**Balances**: XX.XX AVAX (~$XXXX.XX) + XX.XX USDC (~$XX.XX) = **$XXXX.XX**
**Wallet**: 0.0969 AVAX (~$0.89) | **Combined Total**: **$XXXX.XX**
**Fees (24h)**: $X.XXX [or: unavailable — fee oracle not configured]
**IL**: ±X.X% (vs. HODL of $XXXX.XX)
**Rewarded Bin**: ✅ Active bin <BIN_ID> within position range [<MIN>–<MAX>]
**Efficiency**: XX%
**Action**: [No rebalance needed | Rebalance suggested: IL >2% | Micro‑DCA triggered: efficiency <50%]

**D5 Milestone Alignment**:
- Position value ~$XXXX aligns with **Scout** tier ($X/day target).
- Price $X.XX within strategic band $8.95–$9.36.
- IL ±X.X% ✓ [above/below] 2% review trigger.
- Efficiency XX% → [no action | Micro‑DCA boost active].

**Other Pools**: No additional LFJ pools (AVAX/JOE, USDC/JOE, etc.) detected with active positions for this wallet.

---

*Next check: 4× daily (08:15 / 12:15 / 16:15 / 20:15 UTC).*
```

**Important**: Do not create duplicate date headers. If updating an existing entry's date, replace in-place rather than appending. Use `scripts/atomic-vault-append.py` which handles deduplication automatically.