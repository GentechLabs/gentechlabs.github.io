#!/usr/bin/env python3
"""
DeFi Milestone + LP Monitor — Consolidated Smart Tracker
Replaces: "Crypto Watchlist + LP Monitor" + "DeFi Milestone + LP Monitor"
Features:
  - 5-minute debounce on range breakouts & low-efficiency alerts
  - Fee efficiency zones → DCA sizing strategy
  - Shape-aware rebalancing suggestions (curve/spot/bidirectional)
  - Bid-ask spread opportunity detection
  - Milestone tracking integration
  - Quiet hours respect
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
import urllib.request

# ── Path Resolution ─────────────────────────────────────────────────────────
# Hermes sets HERMES_HOME to the profile root (e.g. /root/.hermes/profiles/yoyo)
# The runtime "home" where scripts expect to read/write is $HERMES_HOME/home/.hermes/
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")

def hermes_path(filename: str) -> str:
    """Return absolute path inside the Hermes profile's script directory."""
    return os.path.join(HOME_SCRIPTS_DIR, filename)

# ── Config ──────────────────────────────────────────────────────────────────
AAE_CONFIG_PATH = hermes_path(".lfj-aae-config.json")
STATE_FILE = hermes_path(".lfj-defi-state.json")
POSITION_TRACKER_PATH = hermes_path(".lfj-position-tracker.json")

DEXSCREENER_URL_TEMPLATE = "https://api.dexscreener.com/latest/dex/pairs/avalanche/{pool_address}"

# Constants
JORDAN_WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
CHAIN = "avalanche"

# Alert thresholds
OUT_OF_RANGE_DEBOUNCE_SEC = 300    # 5 minutes
EFFICIENCY_LOW_DEBOUNCE_SEC = 300  # 5 minutes
EFFICIENCY_CRITICAL_PCT = 30.0
EFFICIENCY_WARN_PCT = 50.0

# Quiet hours (ET)
QUIET_START = 23
QUIET_END = 6

# ── State ────────────────────────────────────────────────────────────────────

def now_et():
    return datetime.now(timezone(timedelta(hours=-4)))

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
            "last_check": None,
            "tracking_started": now_et().isoformat()
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


def est_daily_fees(volume: float, liq: float, pos_usd: float, fee_bps: int) -> float:
    """Estimated daily fees earned by this position."""
    if liq <= 0 or volume <= 0 or pos_usd <= 0:
        return 0.0
    return round((volume * fee_bps / 10000) * (pos_usd / liq), 2)

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


# ── CMC Watchlist ───────────────────────────────────────────────────────────────

COINS = [
    {"symbol": "BTC",  "cmc_id": "1"},
    {"symbol": "SOL",  "cmc_id": "5426"},
    {"symbol": "LINK", "cmc_id": "1975"},
    {"symbol": "AVAX", "cmc_id": "5805"},
    {"symbol": "TAO",  "cmc_id": "22974"},
    {"symbol": "XAUt", "cmc_id": "5176"},
    {"symbol": "BEAM", "cmc_id": "28298"},
]

CMC_THRESHOLD = 3.0  # % change to trigger watchlist alert

def load_cmc_key() -> str:
    cfg = hermes_path("cmc_config.json")
    if os.path.exists(cfg):
        try:
            with open(cfg) as f:
                return json.load(f).get("coinmarketcap_api_key", "")
        except Exception:
            pass
    return os.environ.get("CMC_API_KEY", "")

def fetch_cmc() -> Optional[dict]:
    key = load_cmc_key()
    if not key:
        return None
    ids = ",".join(c["cmc_id"] for c in COINS)
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id={ids}&convert=USD"
    req = urllib.request.Request(url, headers={"X-CMC_PRO_API_KEY": key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None

def build_watchlist(cmc_data: dict) -> tuple[list, list]:
    today = now_et().strftime("%Y-%m-%d")
    state_path = hermes_path(".cmc-watchlist-state.json")
    state = {}
    if os.path.exists(state_path):
        try:
            with open(state_path) as f:
                state = json.load(f)
        except Exception:
            pass
    if state.get("date") != today:
        state = {"date": today, "last_prices": {}}

    results = []
    alerts = []
    for c in COINS:
        q = cmc_data["data"].get(c["cmc_id"], {}).get("quote", {}).get("USD", {})
        price = q.get("price", 0)
        ch = q.get("percent_change_24h", 0) or 0
        mc = q.get("market_cap", 0)
        results.append({"symbol": c["symbol"], "price": price, "ch": ch, "mc": mc})
        if abs(ch) >= CMC_THRESHOLD:
            alerts.append({"symbol": c["symbol"], "price": price, "ch": ch})
            state["last_prices"][c["symbol"]] = price

    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
    return results, alerts


# ── Alert Engine ──────────────────────────────────────────────────────────────

def check_alerts(price: float, range_low: float, range_high: float, efficiency: float, shape: str, pool_data: dict) -> dict:
    state = load_state()
    now = time.time()
    alerts = []
    alert_level = "OK"

    out_of_range = price < range_low or price > range_high
    if out_of_range:
        if state.get("out_of_range_start") is None:
            state["out_of_range_start"] = now
            print(f"OUT_OF_RANGE:DETECTED at {now_et().isoformat()} — waiting {OUT_OF_RANGE_DEBOUNCE_SEC}s")
        else:
            elapsed = now - state["out_of_range_start"]
            if elapsed >= OUT_OF_RANGE_DEBOUNCE_SEC:
                last = state.get("last_alert_times", {}).get("out_of_range", 0)
                if now - last > 300:
                    direction = "below" if price < range_low else "above"
                    alerts.append({
                        "severity": "HIGH",
                        "type": "OUT_OF_RANGE_CONFIRMED",
                        "message": f"Price ${price:.4f} {direction} range [${range_low:.2f}–${range_high:.2f}] for {int(elapsed/60)}min — RECONFIGURE NEEDED",
                        "action": "Rebalance range immediately"
                    })
                    state.setdefault("last_alert_times", {})["out_of_range"] = now
                    alert_level = "HIGH"
    else:
        state["out_of_range_start"] = None

    if efficiency < EFFICIENCY_CRITICAL_PCT:
        if state.get("efficiency_low_start") is None:
            state["efficiency_low_start"] = now
            print(f"LOW_EFFICIENCY:DETECTED {efficiency:.1f}% — waiting {EFFICIENCY_LOW_DEBOUNCE_SEC}s")
        else:
            elapsed = now - state["efficiency_low_start"]
            if elapsed >= EFFICIENCY_LOW_DEBOUNCE_SEC:
                last = state.get("last_alert_times", {}).get("low_efficiency", 0)
                if now - last > 300:
                    shape_analysis = analyze_shape_balance(price, range_low, range_high, shape)
                    dca_amount, dca_reason = get_dca_amount_by_zone(efficiency)
                    suggested_range = estimate_rebalance_target(price, range_low, range_high, shape)
                    severity = "MEDIUM" if efficiency < 30 else "LOW"
                    alerts.append({
                        "severity": severity,
                        "type": "LOW_EFFICIENCY_REBALANCE",
                        "message": f"Fee efficiency {efficiency:.1f}% — {shape_analysis['type']}",
                        "suggested_range": suggested_range,
                        "dca_amount": dca_amount,
                        "dca_reason": dca_reason,
                        "action": "Consider rebalancing liquidity position"
                    })
                    state.setdefault("last_alert_times", {})["low_efficiency"] = now
                    alert_level = severity
    else:
        state["efficiency_low_start"] = None

    save_state(state)
    return {"alerts": alerts, "alert_level": alert_level}

# ── Report ────────────────────────────────────────────────────────────────────

def format_report(price: float, in_range: bool, efficiency: float, pool_data: dict,
                  position_tracker: dict, alerts: list, alert_level: str, shape: str) -> str:
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

    lines.append(f"`Source: DexScreener | Debounce: 5min | Check: {now_et().strftime('%H:%M EDT')}`")
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

    # ── CMC Watchlist ─────────────────────────────────────────────────────────────
    cmc_data = fetch_cmc()
    cmc_results, cmc_alerts = ([], [])
    if cmc_data and "data" in cmc_data:
        cmc_results, cmc_alerts = build_watchlist(cmc_data)

    # ── LP Position ───────────────────────────────────────────────────────────────
    try:
        pool = fetch_dexscreener()
        price = pool["price"]
    except Exception as e:
        print(f"ERROR: DexScreener failed — {e}", file=sys.stderr)
        sys.exit(1)

    in_range = range_low <= price <= range_high
    efficiency = calc_fee_efficiency(price, range_low, range_high, shape)
    position_tracker = load_position_tracker()

    # LP alerts
    alert_result = check_alerts(price, range_low, range_high, efficiency, shape, pool)
    lp_alerts = alert_result["alerts"]
    alert_level = alert_result["alert_level"]

    # Merge CMC alerts (CMC always triggers immediate alert)
    all_alerts = list(cmc_alerts) + lp_alerts
    if cmc_alerts and alert_level == "OK":
        alert_level = "MEDIUM"  # CMC moves are noteworthy

    # ── Report ─────────────────────────────────────────────────────────────────────
    milestones = cfg.get("milestones", [])
    report = format_report(
        price=price,
        in_range=in_range,
        efficiency=efficiency,
        pool_data={**pool, "range_low": range_low, "range_high": range_high},
        position_tracker=position_tracker,
        alerts=all_alerts,
        alert_level=alert_level,
        shape=shape,
        cmc_results=cmc_results,
        milestones=milestones,
        config=cfg,
    )

    print(report)

    # Exit code: 0=OK, 1=MEDIUM, 2=HIGH
    if alert_level == "HIGH":
        sys.exit(2)
    elif alert_level == "MEDIUM":
        sys.exit(1)
    else:
        sys.exit(0)



if __name__ == "__main__":
    main()
