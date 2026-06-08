#!/usr/bin/env python3
"""
DeFi Milestone + LP Monitor — Consolidated Smart Tracker
Replaces: "Crypto Watchlist + LP Monitor" + "DeFi Milestone + LP Monitor"
Features:
  - 2-clean-run debounce: after 2 consecutive quiet checks, silent until next hour
  - 5-minute debounce on range breakouts & low-efficiency alerts
  - Fee efficiency zones → DCA sizing strategy
  - Shape-aware rebalancing suggestions (curve/spot/bidirectional)
  - Quiet hours respect
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
import urllib.request

# ── Path Resolution ─────────────────────────────────────────────────────────
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")

def hermes_path(filename: str) -> str:
    return os.path.join(HOME_SCRIPTS_DIR, filename)

# ── Config ──────────────────────────────────────────────────────────────────
AAE_CONFIG_PATH = hermes_path(".lfj-aae-config.json")
STATE_FILE = hermes_path(".lfj-defi-state.json")
POSITION_TRACKER_PATH = hermes_path(".lfj-position-tracker.json")

DEXSCREENER_URL_TEMPLATE = "https://api.dexscreener.com/latest/dex/pairs/avalanche/{pool_address}"

JORDAN_WAL_ADDRESS = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
CHAIN = "avalanche"

# Alert thresholds (debounce durations in seconds)
OUT_OF_RANGE_DEBOUNCE_SEC = 300    # 5 minutes
EFFICIENCY_LOW_DEBOUNCE_SEC = 300  # 5 minutes
EFFICIENCY_CRITICAL_PCT = 30.0

# Alert suppression: once alerted on a condition, stay silent until it resolves
# Condition resolves when: price returns to range (for OOR) or efficiency > 30% (for low eff)

# Quiet hours (ET)
QUIET_START = 23
QUIET_END = 6

# ── Time helpers ─────────────────────────────────────────────────────────────

def now_et():
    return datetime.now(timezone(timedelta(hours=-4)))

# ── State ────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "out_of_range_start": None,
            "efficiency_low_start": None,
            "last_alert_times": {},
            "last_price": None,
            "last_efficiency": None,
            "last_in_range": None,
            "last_zone": None,
            "last_report_time": None,
            "consecutive_quiet_runs": 0,
            "last_report_hour": None,
        }

def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    state["last_check"] = now_et().isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_config() -> dict:
    try:
        with open(AAE_CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Cannot load AAE config at {AAE_CONFIG_PATH}: {e}", file=sys.stderr)
        sys.exit(1)

def load_position_tracker() -> dict:
    try:
        with open(POSITION_TRACKER_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

# ── Data Fetchers ────────────────────────────────────────────────────────────

def fetch_dexscreener() -> dict:
    url = DEXSCREENER_URL_TEMPLATE.format(pool_address=POOL_ADDRESS)
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-DeFi/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    pair = data.get("pair", data.get("pairs", [{}])[0] if data.get("pairs") else {})
    return {
        "source": "dexscreener",
        "price": float(pair.get("priceNative", 0)),
        "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
        "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0)),
        "price_change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
    }

# ── Helpers ──────────────────────────────────────────────────────────────────

def is_quiet_hours() -> bool:
    now = now_et()
    h = now.hour
    if QUIET_START > QUIET_END:
        return h >= QUIET_START or h < QUIET_END
    return QUIET_START <= h < QUIET_END

def calc_fee_efficiency(price: float, range_low: float, range_high: float, shape: str) -> float:
    if price < range_low or price > range_high:
        return 0.0
    pos = (price - range_low) / (range_high - range_low)
    if shape == "spot":
        return 100.0
    elif shape == "bidirectional":
        return round(max(0, min(100, abs(pos - 0.5) * 2 * 100)), 1)
    else:
        return round(max(0, min(100, (1 - abs(pos - 0.5) * 2) * 100)), 1)

def get_dca_amount_by_zone(efficiency: float) -> tuple:
    if efficiency >= 70:
        return 50, "🟢 Center zone (70%+ efficiency) — full $50 DCA"
    elif efficiency >= 50:
        return 30, "🟡 Mid zone (50–70%) — reduced $30 DCA (still earning)"
    elif efficiency >= 30:
        return 20, "🟠 Low zone (30–50%) — micro-DCA $20 + watch for rebalance"
    else:
        return 10, "🔴 Edge zone (<30%) — micro-DCA $10 + URGENT rebalance needed"

def analyze_shape_balance(price: float, range_low: float, range_high: float, shape: str) -> dict:
    if shape != "curve":
        return {"type": "N/A (non-curve shape)", "pct_from_center": None}
    pos = (price - range_low) / (range_high - range_low)
    deviation = pos - 0.5
    pct_dev = abs(deviation) * 100
    if deviation < -0.15:
        return {"type": "🔴 Bottom-heavy (price near lower edge)", "pct_from_center": round(pct_dev, 1)}
    elif deviation > 0.15:
        return {"type": "🔴 Top-heavy (price near upper edge)", "pct_from_center": round(pct_dev, 1)}
    else:
        return {"type": "🟢 Balanced (near range center)", "pct_from_center": round(pct_dev, 1)}

def estimate_rebalance_target(price: float, range_low: float, range_high: float, shape: str) -> str:
    width = range_high - range_low
    if price < range_low:
        new_low = round(price - width * 0.25, 2)
        new_high = round(price + width * 0.75, 2)
        return f"${new_low:.2f} – ${new_high:.2f} (shift down; price below range)"
    elif price > range_high:
        new_low = round(price - width * 0.75, 2)
        new_high = round(price + width * 0.25, 2)
        return f"${new_low:.2f} – ${new_high:.2f} (shift up; price above range)"
    else:
        return f"${range_low:.2f} – ${range_high:.2f} (current is fine; check shape balance)"

# ── Alert Engine ──────────────────────────────────────────────────────────────

def check_alerts(price: float, range_low: float, range_high: float, efficiency: float, shape: str, pool_data: dict) -> dict:
    state = load_state()
    now = time.time()
    alerts = []
    alert_level = "OK"

    out_of_range = price < range_low or price > range_high
    
    # Track condition resolution for "alert once per condition" logic
    # If we previously alerted on a condition, check if it has resolved
    oor_alerted = state.get("oor_alerted", False)
    eff_alerted = state.get("eff_alerted", False)
    
    # Out-of-range condition resolved? Reset alert flag
    if oor_alerted and not out_of_range:
        state["oor_alerted"] = False
        state["oor_alert_time"] = None
    
    # Low efficiency condition resolved? Reset alert flag
    if eff_alerted and efficiency >= EFFICIENCY_CRITICAL_PCT:
        state["eff_alerted"] = False
        state["eff_alert_time"] = None

    # ── Out-of-range debounced alert ──────────────────────────────────────────
    if out_of_range:
        if state.get("out_of_range_start") is None:
            state["out_of_range_start"] = now
            print(f"OUT_OF_RANGE:DETECTED at {now_et().isoformat()} — waiting {OUT_OF_RANGE_DEBOUNCE_SEC}s")
        else:
            elapsed = now - state["out_of_range_start"]
            if elapsed >= OUT_OF_RANGE_DEBOUNCE_SEC:
                # Only alert if we haven't already alerted for this condition
                if not oor_alerted:
                    direction = "below" if price < range_low else "above"
                    alerts.append({
                        "severity": "HIGH",
                        "type": "OUT_OF_RANGE_CONFIRMED",
                        "message": f"Price ${price:.4f} {direction} range [${range_low:.2f}–${range_high:.2f}] for {int(elapsed/60)}min — RECONFIGURE NEEDED",
                        "action": "Rebalance range immediately"
                    })
                    state["oor_alerted"] = True
                    state["oor_alert_time"] = now
                    alert_level = "HIGH"
    else:
        state["out_of_range_start"] = None

    # ── Low-efficiency (<30%) debounced alert ─────────────────────────────────
    if efficiency < EFFICIENCY_CRITICAL_PCT:
        if state.get("efficiency_low_start") is None:
            state["efficiency_low_start"] = now
            print(f"LOW_EFFICIENCY:DETECTED {efficiency:.1f}% — waiting {EFFICIENCY_LOW_DEBOUNCE_SEC}s")
        else:
            elapsed = now - state["efficiency_low_start"]
            if elapsed >= EFFICIENCY_LOW_DEBOUNCE_SEC:
                # Only alert if we haven't already alerted for this condition
                if not eff_alerted:
                    shape_analysis = analyze_shape_balance(price, range_low, range_high, shape)
                    dca_amount, dca_reason = get_dca_amount_by_zone(efficiency)
                    suggested_range = estimate_rebalance_target(price, range_low, range_high, shape)
                    alerts.append({
                        "severity": "MEDIUM",
                        "type": "LOW_EFFICIENCY_REBALANCE",
                        "message": f"Fee efficiency {efficiency:.1f}% — {shape_analysis['type']}",
                        "suggested_range": suggested_range,
                        "dca_amount": dca_amount,
                        "dca_reason": dca_reason,
                        "action": "Consider rebalancing liquidity position"
                    })
                    state["eff_alerted"] = True
                    state["eff_alert_time"] = now
                    alert_level = "MEDIUM"
    else:
        state["efficiency_low_start"] = None

    save_state(state)
    return {"alerts": alerts, "alert_level": alert_level}

# ── Silencing Logic ───────────────────────────────────────────────────────────

def should_send_report(state: dict, price: float, efficiency: float, in_range: bool, alerts: list) -> tuple[bool, str]:
    """
    Decide whether to emit a DeFi Milestone report right now.

    Rules:
    1. Always send if this is the first run (no last_report_time)
    2. Always send if we have active alerts (handled by caller, but treat as material change)
    3. Material change detection → send (price moved >1% or $0.20, zone flip, range status flip)
    4. Otherwise count quiet runs; after 2 consecutive quiet runs, go silent until hour rolls over
    """
    now_dt = now_et()
    now_ts = time.time()

    # Hour rollover resets quiet counter
    last_hour = state.get("last_report_hour")
    if last_hour is not None and last_hour != now_dt.hour:
        state["consecutive_quiet_runs"] = 0
        state["last_report_hour"] = now_dt.hour

    last_report = state.get("last_report_time")

    # First run ever — conditionally send
    if last_report is None:
        # High-efficiency stability: skip even baseline report
        if efficiency >= 70.0 and in_range and not alerts:
            state["consecutive_quiet_runs"] = 2   # mark quiet for the hour
            state["last_report_hour"] = now_dt.hour
            return False, "high-efficiency stable — silent"
        state["consecutive_quiet_runs"] = 0
        state["last_report_hour"] = now_dt.hour
        return True, "first run"

    # Material change checks
    reasons = []
    last_price = state.get("last_price")
    if last_price and last_price > 0:
        price_change_pct = abs((price - last_price) / last_price * 100)
        price_change_abs = abs(price - last_price)
        if price_change_pct >= 1.0 or price_change_abs >= 0.20:
            reasons.append(f"price {price_change_pct:.1f}%")

    current_zone = "zone_70_plus" if efficiency >= 70 else "zone_50_70" if efficiency >= 50 else "zone_30_50" if efficiency >= 30 else "zone_below_30"
    if current_zone != state.get("last_zone"):
        reasons.append(f"zone → {current_zone}")

    if in_range != state.get("last_in_range"):
        reasons.append("range status flip")

    if alerts:
        reasons.append(f"{len(alerts)} alert(s)")

    if reasons:
        state["consecutive_quiet_runs"] = 0  # reset counter on any change
        state["last_report_hour"] = now_dt.hour
        return True, "; ".join(reasons)

    # No material change — high-efficiency stability override?
    # When efficiency ≥70%, in range, and no alerts, stay silent all hour
    if efficiency >= 70.0 and in_range and not alerts:
        state["consecutive_quiet_runs"] = 2   # mark as already quiet
        state["last_report_hour"] = now_dt.hour
        return False, "high-efficiency stable — silent"

    # Normal debounce: after 2 consecutive quiet runs, silence until hour rolls over
    consecutive = state.get("consecutive_quiet_runs", 0)
    current_hour = now_dt.hour

    if consecutive >= 2 and last_hour == current_hour:
        return False, f"quiet — {consecutive} consecutive clean runs this hour"
    else:
        # First or second quiet run this hour → still send
        return True, f"clean run #{consecutive + 1} this hour"

def update_state_after_check(state: dict, price: float, efficiency: float, in_range: bool, was_sent: bool):
    """Persist metrics for next cycle."""
    state["last_price"] = price
    state["last_efficiency"] = efficiency
    state["last_in_range"] = in_range
    state["last_zone"] = "zone_70_plus" if efficiency >= 70 else "zone_50_70" if efficiency >= 50 else "zone_30_50" if efficiency >= 30 else "zone_below_30"

    if was_sent:
        state["last_report_time"] = time.time()
        state["consecutive_quiet_runs"] = state.get("consecutive_quiet_runs", 0) + 1
        state["last_report_hour"] = now_et().hour
    # If not sent, we don't increment consecutive_quiet_runs (it stays at 2+ to keep silence)

    save_state(state)

# ── Report ────────────────────────────────────────────────────────────────────

def format_report(price: float, in_range: bool, efficiency: float, pool_data: dict,
                  position_tracker: dict, alerts: list, alert_level: str, shape: str,
                  change_reason: str) -> str:
    emoji = "✅" if alert_level == "OK" else "⚠️" if alert_level == "LOW" else "🚨"
    lines = [f"{emoji} **DeFi Milestone + LP Report** — {now_et().strftime('%Y-%m-%d %H:%M EDT')}", ""]

    lines.append("**📊 Pool Data**")
    lines.append(f"  Pool: LFJ AVAX/USDC 5bps")
    lines.append(f"  Price: ${price:.4f}")
    lines.append(f"  Range: ${pool_data.get('range_low', '?'):.2f} – ${pool_data.get('range_high', '?'):.2f}")
    lines.append(f"  Status: {'🟢 In Range' if in_range else '🔴 OUT OF RANGE'}")
    lines.append(f"  Efficiency: {efficiency:.1f}%")
    lines.append(f"  Shape: {shape.upper()}")
    lines.append("")

    entry_price = position_tracker.get("entry_avax_price", "?")
    il_pct = 0.0
    if entry_price != "?" and float(entry_price) > 0:
        il_pct = ((price - float(entry_price)) / float(entry_price)) * 100

    lines.append("**💰 Position**")
    lines.append(f"  Entry price: ${entry_price}")
    lines.append(f"  IL: {il_pct:+.2f}%")
    lines.append("")

    if alerts:
        lines.append("**🚨 Alerts & Actions**")
        for a in alerts:
            sev = a.get("severity", "INFO")
            icon = "🔴" if sev == "HIGH" else "🟡" if sev == "MEDIUM" else "🟢"
            lines.append(f"  {icon} [{a['type']}] {a['message']}")
            for key in ["suggested_range", "dca_amount", "dca_reason", "action"]:
                if key in a:
                    lines.append(f"      → {key.replace('_', ' ').title()}: {a[key]}")
        lines.append("")

    dca_amt, dca_reason = get_dca_amount_by_zone(efficiency)
    lines.append("**💡 DCA Strategy**")
    lines.append(f"  {dca_reason}")
    lines.append("")

    lines.append(f"`Source: DexScreener | Debounce: 2-clean-run | Check: {now_et().strftime('%H:%M EDT')}`")
    return "\n".join(lines)

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if is_quiet_hours():
        print("QUIET_HOURS — no report")
        sys.exit(0)

    cfg = load_config()
    pos_cfg = cfg.get("position", {})
    range_low = pos_cfg.get("range_low")
    range_high = pos_cfg.get("range_high")
    shape = pos_cfg.get("shape", "curve").lower()

    if not all([range_low, range_high]):
        print("ERROR: Invalid AAE config — missing range", file=sys.stderr)
        sys.exit(1)

    try:
        pool = fetch_dexscreener()
        price = pool["price"]
    except Exception as e:
        print(f"ERROR: DexScreener failed — {e}", file=sys.stderr)
        sys.exit(1)

    in_range = range_low <= price <= range_high
    efficiency = calc_fee_efficiency(price, range_low, range_high, shape)
    position_tracker = load_position_tracker()

    alert_result = check_alerts(price, range_low, range_high, efficiency, shape, pool)
    alerts = alert_result["alerts"]
    alert_level = alert_result["alert_level"]

    # Decide whether to send
    state = load_state()
    should_send, change_reason = should_send_report(state, price, efficiency, in_range, alerts)

    if not should_send:
        # Still update state (so quiet counter increments), but don't print
        update_state_after_check(state, price, efficiency, in_range, was_sent=False)
        sys.exit(0)

    # Generate and emit report
    report = format_report(
        price=price,
        in_range=in_range,
        efficiency=efficiency,
        pool_data={**pool, "range_low": range_low, "range_high": range_high},
        position_tracker=position_tracker,
        alerts=alerts,
        alert_level=alert_level,
        shape=shape,
        change_reason=change_reason
    )
    print(report)

    update_state_after_check(state, price, efficiency, in_range, was_sent=True)

    # Exit codes for cron monitoring
    if alert_level == "HIGH":
        sys.exit(2)
    elif alert_level == "MEDIUM":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
