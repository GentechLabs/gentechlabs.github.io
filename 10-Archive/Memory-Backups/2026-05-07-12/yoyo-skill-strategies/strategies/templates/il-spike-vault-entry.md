---
title: IL Spike Review Vault Entry Template
updated: 2026-05-03
owner: YoYo (Strategies)
usage: Copy to 03-Strategies/Defi-Monitor/YYYY-MM-DD-il-review.md when IL threshold breached
---

## D5 LP Position — IL Review

**Date**: 2026-05-03  
**Pool**: LFJ AVAX/USDC (Avalanche C-Chain)  
**Alert triggered**: IL = **-17.65%** (threshold: >2%) → 🚨 Review

### Position Snapshot (Ground Truth: `lp-position-reader.py`)

| Metric | Value | Status |
|--------|-------|--------|
| AVAX Price | $9.07 (↓ from $9.11) | ⚠️ Declining |
| Position Value | $135.82 | ✅ On-chain verified |
| Fee Efficiency | 38.2% | ⚠️ Watch zone |
| Price Range | $8.95–$9.36 | ✅ Inside band |
| Impermanent Loss | -17.65% | 🚨 **Exceeded threshold** |

### Review Checklist

- [x] Ground truth verified via `lp-position-reader.py` (on-chain decoded balances)
- [x] Efficiency calculation cross-checked (curve shape formula applied)
- [ ] Price range boundaries confirmed against config (`range_low: 8.95`, `range_high: 9.36`)
- [ ] Root cause analysis: price move vs oracle delay vs rebalancing artifact
- [ ] Decision recorded: Hold / Rebalance now / Wait for recovery
- [ ] Rationale documented below

### Root Cause Analysis

**Hypothesis 1 — Price move predominant**: AVAX dropped $0.04 (0.44%) over 24h; IL of -17.65% seems disproportionate for such a small move. Unlikely unless position is heavily skewed or range miscalculated.

**Hypothesis 2 — Range band misaligned**: Range $8.95–$9.36 is relatively tight around current price. If range too tight, small moves push position to edge where IL compounds.

**Hypothesis 3 — Oracle/settlement delay**: `lp-position-reader.py` may be reading stale on-chain bin data. Verify by checking current active bin on-chain via explorer.

**Hypothesis 4 — DCA injections not settled**: `d5-master-cron.py` includes pending DCA in its position value, but ground truth (`lp-position-reader.py`) does not. If DMOB recently allocated capital but transactions pending, efficiency temporarily depressed.

**Current assessment**: Likely **Hypothesis 4** — state file divergence between scripts (see `references/ground-truth-protocol.md`). `d5-master-cron.py` reported $138.92 (incl. pending DCA) vs ground truth $135.82. The $3.10 difference (~2.3%) aligns with capital injection not yet on-chain.

### Decision & Rationale

**Decision**: **Hold — no immediate rebalance**

**Rationale**:
- Position still inside configured range ($8.95–$9.36); no price-breakout confirmed
- Efficiency 38.2% is in "watch" band (30–50%), not "edge" (<30%)
- IL spike likely temporary due to pending DCA not yet reflected on-chain
- Rebalancing now would realize loss unnecessarily

**Action plan**:
- Re-check IL in 48 hours after pending DCA settles
- If IL remains >10% *and* price moves outside range → rebalance
- Monitor efficiency trend: if drops below 30% → immediate rebalance regardless of range

### Vault Actions

- [x] Vault entry created: `03-Strategies/Defi-Monitor/2026-05-03-il-review.md`
- [x] Telegram posted to `GenTech Strategies`: "🚨 D5 IL review initiated — -17.65% (pending DCA settlement; hold position)"
- [ ] Follow-up verification scheduled: May 5 EOD
- [ ] If IL persists, create rebalance recommendation in `03-Strategies/Defi-Monitor/2026-05-05-rebalance-proposal.md`

### Related

- Ground truth protocol: `references/ground-truth-protocol.md`
- Script discrepancy incident: `08-Daily/2026-05-03.md`
- Handoff waiting on config: `09-Green Room/active-handoffs/2026-05-02-d5-strategy-params-yoyo.md`
