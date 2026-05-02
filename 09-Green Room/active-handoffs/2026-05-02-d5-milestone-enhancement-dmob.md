---
handoff_id: H2026-05-02-01
from: Gentech (CEO)
to: DMOB (GenTech Labs)
date: 2026-05-02
status: 🚀 Pending Ack
priority: P0
deadline: 2026-05-03 (EOD)
---

## Task

Implement **D5 Milestone Cron Enhancements** — add 5-minute breakout confirmation, state persistence, and dual-tier alerting to `d5-master-cron.py`.

## Background

Jordan voice-approved (May 2, 12:42 PM) tighter monitoring rules for the consolidated D5 milestone cron job. Current script is solid but fires immediately on condition changes. Need debounce logic + bid-ask edge strategy.

**Reference doc:** `03-Strategies/Defi-Monitor/d5-milestone-enhancements-2026-05.md`

## What Needs To Be Done

### 1. Breakout Confirmation Logic (5-min debounce)

File: `03-Strategies/scripts/d5-master-cron.py`

- Extend state file schema (`~/.hermes/scripts/.lfj-aae-state.json`) with:
  ```json
  {
    "pending_breakout": {
      "condition": "out_of_range" | "efficiency_low",
      "first_seen": "ISO_TIMESTAMP",
      "price": float,
      "efficiency": float,
      "confirmed": boolean
    }
  }
  ```
- On first detection of `out_of_range` OR `eff < 30%` (but ≥ 30% uses immediate alert), set `pending_breakout` with `confirmed: false`, timestamp = now
- On subsequent runs: if `pending_breakout.confirmed == false` AND `(now - first_seen) >= 5 minutes`:
  - Re-check condition
  - If **still true** → `confirmed: true` + **SEND CONFIRMED ALERT** (Telegram 🚨)
  - If **false** → clear pending (false positive resolved)
- If `pending_breakout.confirmed == true`, keep sending confirmed alert on every run until condition clears
- On condition clear → reset `pending_breakout = {}`

### 2. Two-Tier Telegram Messaging

- **Mini-warning** (pending, <5 min): `⚠️ D5 Monitor: condition detected — monitoring for 5min confirmation`
- **Confirmed action** (≥5 min, confirmed): `🚨 D5 Milestone — ACTION REQUIRED: [out-of-range | efficiency low] — rebalance suggested. Price: $X, Efficiency: Y%`
- Send to home channel (`TELEGRAM_HOME_CHANNEL` env var)

### 3. Efficiency Thresholds

- Immediate alert if `eff ≤ 30%` (bypass 5-min wait — continuous decay)
- Watch alert if `30% < eff < 50%` (with debounce like out-of-range)
- Keep existing `eff < 50%` action suggestion but tighten urgency descriptors

### 4. Bid-Ask Edge Strategy

In the DCA recommendation block:
```python
if price <= POOL['range_low'] * 1.02 and 30 <= eff < 50:
    dca_note += " | 📈 Bid-ask edge — consider DCA boost"
    # Also suggest boost multiplier if config exists
```
Read `BID_ASK_BOOST_MULTIPLIER` from `00-HQ/config/defi-lp-config.env` (default 1.5)

### 5. Vault Logging

Create `03-Strategies/Defi-Monitor/` daily entries:
- Every calendar date, first run writes a header entry even if silent
- Format: `## YYYY-MM-DD Update` with price, efficiency, range status, fees
- Use template from `defi-lp-monitoring` skill's `templates/vault-entry-template.md`

## Files to Modify

| File | Changes |
|------|---------|
| `03-Strategies/scripts/d5-master-cron.py` | Main logic (state machine, alert tiers, bid-ask check) |
| `~/.hermes/scripts/.lfj-aae-state.json` | State schema update (add pending_breakout object) |
| `00-HQ/config/defi-lp-config.env` | Add `BID_ASK_BOOST_MULTIPLIER=1.5` (DMOB to propose value, YoYo to approve) |

## Acceptance Criteria (Definition of Done)

- [ ] State file persists across runs; `pending_breakout` survives script restart
- [ ] Mini-warning appears once (no spam) while pending, then confirmed alert once (single escalation)
- [ ] Efficiency ≤30% bypasses debounce, sends confirmed alert immediately
- [ ] Bid-ask edge note appears in Telegram when `price ≤ range_low*1.02`
- [ ] Vault entry written daily (check file exists in `03-Strategies/Defi-Monitor/`)
- [ ] No uncaught exceptions in cron runs (check logs)
- [ ] YoYo has approved config value in `defi-lp-config.env`

## Dependencies

- **YoYo** must provide confirmed thresholds (BID_ASK_BOOST_MULTIPLIER, maybe LOWER_EDGE_BUFFER_PCT if not 2%)
- Script must have write access to `~/.hermes/scripts/` for state file
- Telegram credentials in `.env` must be valid (already assumed)

## Questions for DMOB

1. Can you implement the state machine within ~200 lines? (current script 473 lines total — keep it clean)
2. Prefer state in separate `.json` or extend existing `.lfj-aae-state.json`? (suggestion: extend existing)
3. Should we add a `last_alert_sent` timestamp to avoid duplicate confirmed alerts within same window?
4. Verify: DexScreener fetch is reliable enough for 5-min precision, or should we add on-chain fallback?

## Coordination

- After code complete, update this handoff status to `🟡 In Review`
- Post summary in `GenTech Labs` group linking to vault doc
- Ping YoYo for config sync
- Self-assign: `DMOB — D5 milestone cron enhancements by May 3`

---

**BRAIN LAYER REGISTRATION:** Yes — handoff registered under Active Handoffs
