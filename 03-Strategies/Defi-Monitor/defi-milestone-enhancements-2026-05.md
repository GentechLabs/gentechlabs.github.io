---
title: DeFi Milestone Cron Enhancements
date: 2026-05-02
status: 🚀 Active
owner: Gentech (CEO) → DMOB + YoYo
priority: P0
---

## Context

Jordan voice-approved enhancements to the existing `defi-master-cron.py` consolidation job on **May 2, 2026**. The current script (v1) runs 4× daily and aggregates CMC watchlist + LP milestone tracking. These rules tighten monitoring, add debounce logic, and introduce edge-case strategies.

## Directive (from Jordan)

> "From now on, whenever we consolidate a cron job, we don't have to call it 'consolidated.' For this one, we just call it the DeFi milestone."
>
> "We want the same rules that the LP tracker had: the DeFi milestone tracks our LP. If it goes out of a certain range, it'll send one warning, then wait **5 minutes** to confirm breakout/breakdown, then send a bigger alert: 'hey you need to rebalance.'"
>
> "Different strategies: with a curve, fee efficiency on the edges is closer to 30% or below. When it gets to that range, we want to suggest rebalancing."
>
> "We also want to suggest adding extra — depending on the situation, maybe go ahead and DCA it if it's low enough, or if there's a bid-ask and we're down on the lower edges, we use this as a buying opportunity."

## Current State

**Script:** `03-Strategies/scripts/defi-master-cron.py` (473 lines)
- Fetches CMC watchlist (BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM) — alerts if |Δ24h| ≥ 3%
- Fetches LP position via DexScreener + DeBank wallet API
- Calculates efficiency via curve math (`calc_efficiency`)
- DCA sizing by efficiency band (≥70%: $50, 50–70%: $30, 30–50%: $20, <30%: $10)
- Milestone ladder: Scout ($5/d), Raider ($20/d), Warlord ($55/d), Sovereign ($200/d)
- Silent unless: CMC ≥3%, out of range, efficiency <50%, compound ready ($50+), Monday, wallet low-balance
- No state persistence → no breakout confirmation delay

**Config:** `00-HQ/config/defi-lp-config.env` (pool ranges, wallet addresses)

**State files:**
- `~/.hermes/scripts/.cmc-watchlist-state.json`
- `~/.hermes/scripts/.lfj-aae-state.json`

**Vault logging:** None currently — needs to write to `03-Strategies/Defi-Monitor/` daily

## Required Enhancements

### 1. Breakout Confirmation (5-Minute Debounce)

**Problem:** Current `should_alert()` fires immediately on condition change.

**Implementation:**
- On first detection of **out-of-range** OR **efficiency <30%**, write a pending-confirmation record to state file:
  ```json
  {
    "pending_breakout": {
      "condition": "out_of_range" | "efficiency_low",
      "first_seen": "2026-05-02T14:10:00-04:00",
      "price": 9.02,
      "efficiency": 28.5,
      "confirmed": false
    }
  }
  ```
- On subsequent runs (≥5 minutes later), re-check condition:
  - **If still true** → set `confirmed: true` and **SEND BIG ALERT** ( Telegram message with ⚠️ CONFIRMED BREAKOUT label + rebalance action)
  - **If false** → clear pending (false positive stabilized)
- If <5 minutes and still true, send **mini-warning** only (different Telegram format — softer tone, "monitoring" vs "action required")

**State file:** Extend `~/.hermes/scripts/.lfj-aae-state.json`

**Edge cases:**
- Cron runs every 15 min — need ≤5 min precision → store timestamp with minute resolution
- If script restarts, recover pending state from file
- Once confirmed, keep `confirmed: true` until condition clears, then reset on next cycle

### 2. Efficiency Threshold Tightening

**Current:** triggers rebalance consideration at `eff < 40%` (line 416)

**New rule:** When `eff ≤ 30%` → immediately suggest rebalance (no 5-min wait needed — efficiency decay is continuous, not discrete breakout)

**Implementation:**
```python
if lp['eff'] <= 30:
    urgency = "URGENT"
    action = "Rebalance suggested: efficiency ≤30% (edge zone)"
elif lp['eff'] < 50:
    urgency = "WATCH"
    action = "Consider rebalancing: efficiency below 50%"
```

**Update `should_alert()` to bypass 5-min wait for efficiency≤30%** (different pathway — immediate alert).

### 3. Bid-Ask Edge Strategy (Lower Bound Opportunity)

**Condition:** Price near lower range edge **AND** efficiency in low zone (30–50%)

**Trigger:** `price ≤ range_low * 1.02` (within 2% of lower bound) **AND** `30% ≤ eff < 50%`

**Action:**
- Flag as "accumulation opportunity" in report
- Suggest **DCA boost** (temporary increase: base × 1.5 for next N cycles)
- Note: "Bid-ask dip — consider scaling in"

**Rationale:** Price near lower edge in curve shape means you're earning fees on downside protection; can add to position at discount.

## Code Changes (DMOB Responsibilities)

**File:** `03-Strategies/scripts/defi-master-cron.py`

1. **Add state schema** at top:
   ```python
   PENDING_STATE_KEYS = ['condition', 'first_seen', 'price', 'efficiency', 'confirmed']
   CONFIRMATION_DELAY_MIN = 5
   ```

2. **Refactor `should_alert()`** into two pathways:
   - `check_breakout_confirmation(lp)` → handles out-of-range with debounce
   - `check_immediate_triggers(lp)` → handles efficiency ≤30%, Monday, compound, wallet alerts

3. **Add `load_pending_state()` / `save_pending_state()`** helpers

4. **Add `format_alert_message(lp, urgency, action, is_confirmed)`** for Telegram (two templates: mini-warning vs confirmed-action)

5. **Update DCA suggestion block** to include bid-ask edge logic:
   ```python
   if price <= POOL['range_low'] * 1.02 and 30 <= eff < 50:
       dca_note += " | 📈 Bid-ask edge — consider DCA boost"
   ```

6. **Vault logging:** Write daily entry to `03-Strategies/Defi-Monitor/YYYY-MM-DD-update.md` using template from `defi-lp-monitoring` skill (even if silent, write first-of-day marker)

**Testing plan:**
- Unit test pending state transitions (pending → confirmed → cleared)
- Simulate price ping-pong across boundary (false positive handling)
- Verify telegrams fire only on confirmed breakout

## Strategy Rules (YoYo Responsibilities)

YoYo to provide numeric thresholds:

1. **Strategic rebalance band:** Update `00-HQ/config/defi-lp-config.env`:
   - `TARGET_LOW` and `TARGET_HIGH` (strategic band inside raw range)
   - Example: range $9.00–$9.45 → target $9.08–$9.36 (avoid edges)

2. **Bid-ask edge buffer:** Confirm 2% is appropriate or specify exact `LOWER_EDGE_BUFFER_PCT`

3. **DCA boost multiplier:** When bid-ask opportunity active, suggest `BOOST_MULTIPLIER` (default 1.5×) for next 3 DCA cycles

4. **DeFi milestone cross-check:** Validate current tier targets against `03-Projects/DeFi/D5-Milestone-Tracker.md` — ensure $5/$20/$55/$200/day align with strategy doc

5. **Fee efficiency baseline:** Confirm 30% threshold for "edge zone" on curve shape; may differ for spot/bidirectional shapes

Deliverable: Updated config file + one-page strategy note in `03-Strategies/Defi-Monitor/strategy-params-2026-05.md`

## Approval & Handoff

**Approval:** This doc serves as Jordan's voice-approval record (May 2, 12:42 PM). No checkbox template needed — direct CEO directive.

**Handoffs:**
- **DMOB** — Implementation: 2–3 hours, priority P0. Target: script updated by EOD May 2 or morning May 3.
- **YoYo** — Strategy review: 30 min. Confirm thresholds, update config, write strategy note.

**Coordination:**
- DMOB posts implementation summary to `GenTech Labs` group
- YoYo posts config updates to `GenTech Strategies` group
- Both link to this vault doc
- Gentech (me) will verify final integration and cron schedule update

## Success Criteria

- [ ] D5 master cron implements 5-minute breakout confirmation with distinct message tiers
- [ ] Efficiency ≤30% triggers immediate rebalance alert (no debounce)
- [ ] Bid-ask edge logic added to DCA recommendation block
- [ ] Config updated in `00-HQ/config/defi-lp-config.env` with new thresholds
- [ ] Vault logging enabled (daily entries in `03-Strategies/Defi-Monitor/`)
- [ ] Telegram reports sent to home channel with correct emoji tagging (⚠️ vs 🚨)
- [ ] No duplicate alerts within 5-minute window (state file prevents spam)

## Forward-Looking Hook

This consolidation gives us a signal-aware, strategy-driven monitoring layer. Once stable, we can extend the same debounce pattern to other position trackers and even market event alerts across the AAE stack. **This is just the beginning of intelligent, stateful cron orchestration.**
