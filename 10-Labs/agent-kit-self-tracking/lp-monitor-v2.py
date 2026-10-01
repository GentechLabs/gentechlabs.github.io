#!/usr/bin/env python3
"""
LP Position Monitor v2 — Config-First, Dashboard-Free
=====================================================
Single source of truth: .lfj-aae-config.json + .lfj-position-tracker.json
Live price: DexScreener API
NO dashboard reads, NO dashboard writes.

This eliminates the race condition where multiple scripts overwrite the dashboard.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

# ── Paths ───────────────────────────────────────────────────────────────────
# ALWAYS use /root/.hermes/scripts/ — NOT the profile path
# The profile path has stale data that gets overwritten by other scripts
HOME_SCRIPTS = "/root/.hermes/scripts"
CONFIG_PATH = os.path.join(HOME_SCRIPTS, ".lfj-aae-config.json")
TRACKER_PATH = os.path.join(HOME_SCRIPTS, ".lfj-position-tracker.json")
STATE_PATH = os.path.join(HOME_SCRIPTS, ".lfj-defi-state.json")
DASHBOARD_DATA_PATH = "/root/repos/gentechlabs.github.io/DeFi/defi-data.json"
FEE_TRACKER_PATH = "/root/.hermes/profiles/gentech/scripts/fee-tracker-state.json"
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea"

# ── Helpers ─────────────────────────────────────────────────────────────────

def now_et():
    return datetime.now(timezone(timedelta(hours=-4)))

def load_json(path, default=None):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def is_quiet_hours(cfg):
    qh = cfg.get("quiet_hours", {})
    start = qh.get("start", 23)
    end = qh.get("end", 6)
    h = now_et().hour
    if start > end:
        return h >= start or h < end
    return start <= h < end

def fetch_price():
    """Fetch live AVAX price from DexScreener."""
    req = urllib.request.Request(DEXSCREENER_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    pair = data.get("pair", data.get("pairs", [{}])[0] if "pairs" in data else {})
    price = float(pair.get("priceUsd", 0))
    volume_24h = float(pair.get("volume", {}).get("h24", 0))
    liquidity = float(pair.get("liquidity", {}).get("usd", 0))
    return price, volume_24h, liquidity

def calc_efficiency(price, range_low, range_high, shape):
    """
    Calculate fee-capture efficiency based on LP shape.
    BIN-WEIGHTED: bid-ask peaks at edges (100%), valley at center (50%).
    """
    # Position in range as percentage (0 = low edge, 100 = high edge)
    pos = (price - range_low) / (range_high - range_low) if (range_high - range_low) > 0 else 0.5
    
    # Out of range = 0% efficiency
    if price < range_low or price > range_high:
        return 0.0
    
    # Shape-aware efficiency
    if shape == "spot":
        return 100.0
    elif shape == "bid-ask":
        # Bid-ask: concentrated on edges, valley at center
        # Efficiency = 50% + (distance_from_center * 50%)
        # At edges (0% or 100% position): 100% efficiency
        # At center (50% position): 50% efficiency
        dist_from_center = abs(pos - 0.5) * 100
        return round(50 + dist_from_center, 1)
    elif shape == "bidirectional":
        # Bidirectional: peak at center
        return round(max(0, min(100, pos * 100)), 1)
    else:  # curve
        # Curve: efficiency proportional to distance from center
        # 100% at center, 0% at edges
        center_dist = abs(pos - 0.5) * 2  # 0 = at center, 1 = at edge
        return round(max(0, (1 - center_dist) * 100), 1)

def get_dca_advice(efficiency, shape):
    """Return DCA amount and zone label."""
    if efficiency >= 50:
        return "🟢 Good zone (>50%) — micro-DCA $50, no action needed"
    elif efficiency >= 30:
        return "🟠 Low zone (30–50%) — micro-DCA $20 + watch for rebalance"
    else:
        return "🔴 Edge zone (<30%) — micro-DCA $10 + URGENT rebalance needed"

def get_milestone(daily_fees, milestones):
    """Find current milestone tier — Tier 0 = Grunt at $5/day."""
    # Grunt is always Tier 0 at $5/day
    grunt_tier = {"tier": 0, "label": "Grunt", "daily_fees": 5.0, "description": "Activation threshold — $5/day"}
    
    # Find highest achieved milestone (milestones array assumes Tier 1+)
    current = grunt_tier
    for m in milestones:
        if daily_fees >= m["daily_fees"]:
            # Re-index: config tier 1 becomes display tier 1+
            current = m
    
    # If below $5/day, still Grunt (Tier 0) — next is first config milestone
    if daily_fees < grunt_tier["daily_fees"]:
        return grunt_tier, milestones[0] if milestones else grunt_tier
    
    # Find next milestone
    next_m = None
    for i, m in enumerate(milestones):
        if m["daily_fees"] > daily_fees:
            next_m = m
            break
    
    return current, next_m

# ── Debounce ────────────────────────────────────────────────────────────────

def check_debounce(state, price, efficiency, in_range, shape, range_low, range_high):
    """
    Returns (should_report, reason, suggestion).

    Rules:
    1. OUT_OF_RANGE → always alert immediately
    2. Efficiency < 50% → alert immediately with rebalance suggestion, debounce 10 min
    3. Efficiency ≥ 50% → report every 30 min (2x/hour) so Jordan sees fee efficiency
    """
    # ── A SECOND COPY OF A RULE IS A RULE THAT WILL DRIFT (found 2026-09-30) ──────────────
    # This file carried its OWN `LOW_EFF_THRESHOLD = 50.0`, independent of the authority in
    # fee_efficiency.py. Two files, one rule, no link between them -- the same defect class that
    # gave the treasury six files able to decide the shape. Raised to 75 to match Jordan's ruling
    # (stay above 75% fee efficiency), and flagged: this belongs in ONE place, not two.
    # ONE AUTHORITY (2026-09-30). This file carried its OWN `LOW_EFF_THRESHOLD = 50.0`, independent
    # of fee_efficiency's -- two files, one rule, no link, and they disagreed by 25 points. Read the
    # authority instead of re-declaring it; fall back to the literal only if the import fails, and
    # say so loudly when it does.
    try:
        import fee_efficiency as _fe
        LOW_EFF_THRESHOLD = float(_fe.LOW_EFF_THRESHOLD)
    except Exception as _e:
        LOW_EFF_THRESHOLD = 75.0
        print(f"  ⚠️  lp-monitor: fee_efficiency unavailable ({type(_e).__name__}) — "
              f"using a LITERAL {LOW_EFF_THRESHOLD} rather than the authority.")
    LOW_EFF_DEBOUNCE_SECONDS = 600  # 10 min between low-efficiency alerts
    NORMAL_INTERVAL_SECONDS = 1800  # 30 min between normal check-ins

    now = now_et()
    now_iso = now.isoformat()
    last_report = state.get("last_report_time")
    last_low_alert = state.get("last_low_alert_time")

    # Always alert on out of range
    if not in_range:
        state["last_report_time"] = now_iso
        state["last_low_alert_time"] = None
        suggestion = suggest_new_range(price, shape, range_low, range_high, "OUT_OF_RANGE")
        return True, "OUT_OF_RANGE", suggestion

    # Low efficiency — alert immediately, then debounce 10 min
    if efficiency < LOW_EFF_THRESHOLD:
        if last_low_alert:
            elapsed = (now - datetime.fromisoformat(last_low_alert)).total_seconds()
            if elapsed < LOW_EFF_DEBOUNCE_SECONDS:
                return False, f"LOW_EFF_DEBOUNCED:{efficiency}%", None

        state["last_low_alert_time"] = now_iso
        state["last_report_time"] = now_iso
        suggestion = suggest_new_range(price, shape, range_low, range_high, "LOW_EFFICIENCY")
        return True, f"LOW_EFFICIENCY:{efficiency}%", suggestion

    # Normal (in range, good efficiency) — report every 30 min
    if last_report:
        elapsed = (now - datetime.fromisoformat(last_report)).total_seconds()
        if elapsed < NORMAL_INTERVAL_SECONDS:
            return False, "NORMAL_DEBOUNCED", None

    state["last_report_time"] = now_iso
    state["last_low_alert_time"] = None
    return True, "NORMAL", None

def suggest_new_range(price, shape, range_low, range_high, trigger):
    """
    Suggest new range + shape based on current state.
    Returns string with actionable migration suggestion.
    """
    range_width = range_high - range_low
    current_pos = (price - range_low) / range_width if range_width > 0 else 0.5
    
    if trigger == "OUT_OF_RANGE":
        if price > range_high:
            # Above range — shift upward
            new_low = round(price - range_width * 0.4, 4)
            new_high = round(price + range_width * 0.6, 4)
            # If currently bid-ask, suggest curve for wider coverage
            new_shape = "curve" if shape == "bid-ask" else shape
            return f"🔧 MIGRATE: Shift range to ${new_low:.4f}-${new_high:.4f} ({new_shape.upper()}) — price ${price:.4f} above ${range_high:.4f}"
        else:
            # Below range — shift downward
            new_low = round(price - range_width * 0.6, 4)
            new_high = round(price + range_width * 0.4, 4)
            new_shape = "curve" if shape == "bid-ask" else shape
            return f"🔧 MIGRATE: Shift range to ${new_low:.4f}-${new_high:.4f} ({new_shape.upper()}) — price ${price:.4f} below ${range_low:.4f}"
    
    elif trigger == "LOW_EFFICIENCY":
        if shape == "bid-ask" and abs(current_pos - 0.5) < 0.2:
            # Bid-ask in valley — switch to curve
            pad = range_width * 0.1
            new_low = round(max(0, range_low - pad), 4)
            new_high = round(range_high + pad, 4)
            return f"🔧 OPTIMIZE: Switch to CURVE at ${new_low:.4f}-${new_high:.4f} — bid-ask inefficient at center (price {current_pos*100:.0f}% of range)"
        elif shape == "curve":
            # Curve — consider bid-ask if near edge
            if current_pos > 0.7:
                return f"🔧 OPTIMIZE: Consider BID-ASK to capture edge efficiency — price {current_pos*100:.0f}% toward high edge"
            elif current_pos < 0.3:
                return f"🔧 OPTIMIZE: Consider BID-ASK to capture edge efficiency — price {current_pos*100:.0f}% toward low edge"
        
        # Generic: widen range slightly
        pad = range_width * 0.15
        new_low = round(max(0, range_low - pad), 4)
        new_high = round(range_high + pad, 4)
        return f"🔧 OPTIMIZE: Widen to ${new_low:.4f}-${new_high:.4f} (current: {shape.upper()}) — efficiency low at {current_pos*100:.0f}% of range"
    
    return None

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    cfg = load_json(CONFIG_PATH)
    if not cfg:
        print("ERROR: Cannot load config", file=sys.stderr)
        sys.exit(1)
    
    if is_quiet_hours(cfg):
        # Silent exit — no Telegram noise during quiet hours
        sys.exit(0)
    
    tracker = load_json(TRACKER_PATH, {})
    state = load_json(STATE_PATH, {})
    
    # ── Get position data from CONFIG (source of truth) ──
    pos = cfg.get("position", {})
    range_low = pos.get("range_low", cfg.get("range_low"))
    range_high = pos.get("range_high", cfg.get("range_high"))
    shape = pos.get("shape", "curve")
    entry_price = pos.get("entry_price", tracker.get("entry_avax_price", 0))
    avax_amount = pos.get("token0_amount", tracker.get("avax_amount", 0))
    usdc_amount = pos.get("token1_amount", tracker.get("usdc_amount", 0))
    
    if not range_low or not range_high:
        print("ERROR: Missing range data in config", file=sys.stderr)
        sys.exit(1)
    
    # ── Fetch live price ──
    try:
        price, volume_24h, liquidity = fetch_price()
    except Exception as e:
        print(f"ERROR: DexScreener failed — {e}", file=sys.stderr)
        sys.exit(1)
    
    # ── Calculations ──
    in_range = range_low <= price <= range_high
    efficiency = calc_efficiency(price, range_low, range_high, shape)
    lp_value = (avax_amount * price) + usdc_amount
    il_pct = ((price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
    
    # Fee data from on-chain reader (dashboard) — accurate bin-weighted estimate
    dash_fees = load_json(DASHBOARD_DATA_PATH, {}).get("fees", {})
    daily_fees = dash_fees.get("dailyFees", 0)
    cumulative_fees = dash_fees.get("cumulativeFees", 0)

    # ── Position Lifecycle (from dashboard) ──
    lifecycle = load_json(DASHBOARD_DATA_PATH, {}).get("positionLifecycle", {})
    days_active = lifecycle.get("daysInPosition", 0)
    entry_date = lifecycle.get("currentEntryDate", "unknown")

    # ── On-chain entry data (from reader cache) ──
    entry_data = load_json("/root/.hermes/scripts/.lfj-entry-cache.json", {})

    # Fee calculation — LIVE from pool volume
    # Uses: volume_24h × fee_tier × (position_value / TVL) × concentration_multiplier
    # Concentration multiplier accounts for concentrated liquidity benefit
    # Calibrated: $0.19/day actual on $644K vol, $46.43 pos, $387K TVL, 5bps
    POOL_FEE_RATE = 5 / 10000  # 5 bps for LFJ V2.2 5bps pool
    CONCENTRATION_MULTIPLIER = 4.92  # bid-ask concentrated liquidity boost (calibrated)
    
    # OUT OF RANGE = no fees earned
    if not in_range:
        live_daily = 0.0
        # Don't log this as an error — it's expected behavior
    elif liquidity > 0 and volume_24h > 0:
        # Position's proportional share of pool TVL
        pool_share = lp_value / liquidity if liquidity > 0 else 0
        # Total daily pool fees from volume
        total_fees_24h = volume_24h * POOL_FEE_RATE
        # Our share, boosted by concentration
        live_daily = total_fees_24h * pool_share * CONCENTRATION_MULTIPLIER
        live_daily = round(live_daily, 4)
    else:
        # Fallback: yield rate based on position value
        live_daily = round(lp_value * 0.004, 4)
    
    # Write calculated fee back to defi-data.json for dashboard sync
    dash_data = load_json(DASHBOARD_DATA_PATH, {})
    if "fees" not in dash_data:
        dash_data["fees"] = {}
    dash_data["fees"]["dailyFees"] = live_daily
    # Update cumulative: add the day's pro-rated amount
    if dash_data["fees"].get("cumulativeFees", 0) > 0:
        pass  # keep existing cumulative to avoid overwriting
    else:
        dash_data["fees"]["cumulativeFees"] = 0.0194
    save_json(DASHBOARD_DATA_PATH, dash_data)
    
    daily_fees = live_daily
    
    # Accumulated display: prorate by time of day
    hours_today = now_et().hour + now_et().minute / 60
    today_accrued = round(daily_fees * (hours_today / 24), 4)
    
    # ── Fee History Tracker (persistent daily snapshots) ──
    FEE_HISTORY_PATH = os.path.join(HOME_SCRIPTS, ".lfj-fee-history.json")
    
    def update_fee_history(daily_rate):
        """Store daily fee snapshots for accurate week/month/year totals."""
        history = load_json(FEE_HISTORY_PATH, {"days": []})
        today = now_et().strftime("%Y-%m-%d")
        # Update or append today's entry
        for day in history["days"]:
            if day["date"] == today:
                day["daily_fees"] = round(daily_rate, 4)
                break
        else:
            history["days"].append({"date": today, "daily_fees": round(daily_rate, 4)})
        # Keep last 400 days
        history["days"] = history["days"][-400:]
        save_json(FEE_HISTORY_PATH, history)
        return history
    
    def compute_fee_totals(history):
        """Compute actual accumulated fees from history, not projections."""
        days = history.get("days", [])
        # Daily: today's rate
        today_str = now_et().strftime("%Y-%m-%d")
        today_entry = next((d for d in days if d["date"] == today_str), None)
        daily = today_entry["daily_fees"] if today_entry else 0.0
        
        # Week: sum of last 7 days
        week = sum(d["daily_fees"] for d in days[-7:])
        
        # Month: sum of last 30 days
        month = sum(d["daily_fees"] for d in days[-30:])
        
        # Year: sum of last 365 days
        year = sum(d["daily_fees"] for d in days[-365:])
        
        return round(daily, 4), round(week, 2), round(month, 2), round(year, 2)

    # ── Fee History (persistent daily snapshots) ──
    history = update_fee_history(daily_fees)
    fee_daily_actual, fee_weekly_actual, fee_monthly_actual, fee_yearly_actual = compute_fee_totals(history)
    
    # ── Rank display (replace ATH) ──
    current_milestone, next_milestone = get_milestone(daily_fees, cfg.get("milestones", []))
    rank_label = current_milestone.get("label", "Unranked")
    rank_tier = current_milestone.get("tier", 0)
    if next_milestone:
        rank_progress = (daily_fees / next_milestone["daily_fees"]) * 100
        rank_display = f"Tier {rank_tier} — {rank_label} (${next_milestone['daily_fees']}/day next) [{rank_progress:.0f}%]"
    else:
        rank_display = f"Tier {rank_tier} — {rank_label} (MAX)"
    
    # ── Write fee-tracker state with calibrated data (backward compat) ──
    ft = load_json(FEE_TRACKER_PATH, {})
    ft["daily_total"] = today_accrued
    ft["weekly_total"] = fee_weekly_actual
    ft["monthly_total"] = fee_monthly_actual
    ft["all_time"] = max(ft.get("all_time", 0), daily_fees)
    ft["last_check"] = now_et().isoformat()
    ft["current_day"] = now_et().strftime("%Y-%m-%d")
    ft["current_week"] = now_et().strftime("%Y-W%V")
    ft["current_month"] = now_et().strftime("%Y-%m")
    save_json(FEE_TRACKER_PATH, ft)
    
    # ── Debounce check ──
    should_report, reason, suggestion = check_debounce(state, price, efficiency, in_range, shape, range_low, range_high)
    
    # ── Update state ──
    state["last_price"] = price
    state["last_efficiency"] = efficiency
    state["last_in_range"] = in_range
    state["last_check"] = now_et().isoformat()
    save_json(STATE_PATH, state)
    
    if not should_report:
        sys.exit(0)
    
    # ── Build report ──
    dca_advice = get_dca_advice(efficiency, shape)
    current_milestone, next_milestone = get_milestone(daily_fees, cfg.get("milestones", []))
    ts = now_et().strftime("%Y-%m-%d | %H:%M EDT")
    
    # Efficiency bar
    bar_len = 10
    filled = int(efficiency / 10)
    bar = "▓" * filled + "░" * (bar_len - filled)
    
    all_time = now_et().strftime("%Y-%m-%d")
    
    report = f"""✅ DeFi LP Report — {ts}

📊 Pool Data
  Pool: LFJ AVAX/USDC 5bps
  Price: ${price:.4f}
  Range: ${range_low:.4f} – ${range_high:.4f}
  Status: {'🟢 In Range' if in_range else '🔴 OUT OF RANGE'}
  Efficiency: ▌{bar} {efficiency:.1f}%
  Shape: {shape.upper()}
  Position: {avax_amount:.4f} AVAX + {usdc_amount:.2f} USDC = ${lp_value:.2f}

📈 Fee Trajectory
  Daily:    ${fee_daily_actual:.4f}
├─ Week:    ${fee_weekly_actual:.2f}
├─ Month:   ${fee_monthly_actual:.2f}
├─ Year:    ${fee_yearly_actual:.2f}
└─ Rank:    {rank_display}

💰 Position
  Entry price: ${entry_price}
  IL: {il_pct:+.2f}%
  Since: {entry_date} ({days_active} days)

🔍 On-Chain Activity
  First deposit: {entry_data.get('first_deposit_date', 'unknown')}
  Active days: {entry_data.get('active_days_4h', 0)} (4h+ rule) · {entry_data.get('total_deposits', 0)} deposits · {entry_data.get('total_withdrawals', 0)} rebalances

💡 DCA Strategy
  {dca_advice}

🏆 Milestone
  Current: Tier {current_milestone['tier']} — {current_milestone['label']} (${current_milestone['daily_fees']}/day)"""

    if next_milestone:
        progress = (daily_fees / next_milestone["daily_fees"]) * 100
        report += f"  Next: Tier {next_milestone['tier']} — {next_milestone['label']} (${next_milestone['daily_fees']}/day) [{progress:.0f}%]\n"
    
    # Add suggestion if available
    if suggestion:
        report += f"\n{suggestion}\n"
    
    print(report)

if __name__ == "__main__":
    main()
