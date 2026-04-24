#!/usr/bin/env python3
"""
Unified LP Monitor — LFJ AVAX/USDC Pool
Combines range monitoring + compound milestone tracking in one script.

Features:
  - Range monitoring (price vs range, fee efficiency, quiet hours)
  - Compound milestone tracking (fees earned, days to next milestone, DCA schedule)
  - Birdeye x402 data source with DexScreener fallback
  - State persistence across runs for cumulative tracking

Pool: LFJ V2.2 AVAX/USDC, binStep 10
Address: 0x864d4e5ee7318e97483db7eb0912e09f161516ea
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional

# ── Config ──────────────────────────────────────────────────────────────────
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
CHAIN = "avalanche"

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-unified-state.json")
POSITION_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-position-tracker.json")

# Birdeye config
AVAX_ADDRESS = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC_USDC_ADDRESS = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"

# Data source
DEXSCREENER_URL = f"https://api.dexscreener.com/latest/dex/pairs/{CHAIN}/{POOL_ADDRESS}"

# Quiet hours (Eastern Time)
QUIET_START = 23  # 11 PM
QUIET_END = 6     # 6:30 AM

# ── Compound Config ─────────────────────────────────────────────────────────
# Position baseline (loaded from file)
POSITION_SIZE_USD = 83.92
POSITION_AVAX = 3.762
POSITION_USDC = 48.37

# Milestone schedule (daily fee targets)
MILESTONES = [
    {"label": "$3/day",   "daily_fees": 3.0},
    {"label": "$5/day",   "daily_fees": 5.0},
    {"label": "$8/day",   "daily_fees": 8.0},
    {"label": "$10/day",  "daily_fees": 10.0},
    {"label": "$15/day",  "daily_fees": 15.0},
    {"label": "$20/day",  "daily_fees": 20.0},
]

# DCA schedule
DCA_AMOUNT = 50
DCA_DAY_OF_WEEK = 0

# Compound threshold
COMPOUND_THRESHOLD_USD = 50.0

# Import Birdeye client if available
BIRDEYE_AVAILABLE = False
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from birdeye_x402_client import BirdeyeClient, BirdeyeConfig
    BIRDEYE_AVAILABLE = True
except ImportError:
    pass

# ── Data Fetchers ───────────────────────────────────────────────────────────

def fetch_dexscreener() -> dict:
    req = urllib.request.Request(DEXSCREENER_URL, headers={"User-Agent": "Gentech-Labs/1.0"})
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

def fetch_birdeye() -> Optional[dict]:
    if not BIRDEYE_AVAILABLE: return None
    try:
        config = BirdeyeConfig.load()
        if not config.is_configured: return None
        config.chain = "avalanche"
        with BirdeyeClient(config) as client:
            overview = client.token_overview(AVAX_ADDRESS, "avalanche")
            if "error" in overview: return None
            security = client.token_security(AVAX_ADDRESS, "avalanche")
            trades = client.token_trade_data(AVAX_ADDRESS, "avalanche")
            return {
                "source": "birdeye",
                "price": float(overview.get("price", 0)),
                "liquidity_usd": float(overview.get("liquidity", 0)),
                "volume_24h": float(overview.get("volume24h", overview.get("v24h", 0))),
                "price_change_24h": float(overview.get("priceChange24h", overview.get("priceChange", 0))),
                "market_cap": float(overview.get("mc", overview.get("marketCap", 0))),
                "security_score": security.get("securityScore", security.get("score", None)) if "error" not in security else None,
                "buy_sell_ratio": _calc_buy_sell_ratio(trades) if "error" not in trades else None,
            }
    except Exception: return None

def _calc_buy_sell_ratio(trades: dict) -> Optional[float]:
    if "error" in trades: return None
    buys = trades.get("buys24h", trades.get("buy", 0))
    sells = trades.get("sells24h", trades.get("sell", 0))
    if sells and sells > 0: return round(buys / sells, 2)
    return None

# ── State Management ────────────────────────────────────────────────────────

def load_position() -> dict:
    try:
        with open(POSITION_FILE, "r") as f: return json.load(f)
    except Exception: return {"entry_total_usd": 83.92, "entry_avax": 3.762, "entry_usdc": 48.37}

def load_range() -> tuple:
    """Load range from tracker file (updated via screenshots). Falls back to defaults."""
    try:
        with open(POSITION_FILE, "r") as f:
            data = json.load(f)
        low = data.get("range_low", 9.10)
        high = data.get("range_high", 9.65)
        return (float(low), float(high))
    except Exception:
        return (9.10, 9.65)

def load_state() -> dict:
    default = {"out_of_range_since": None, "last_alert": None, "last_price": None, "last_check": None, "tracking_started": None, "total_fees_earned_usd": 0.0, "total_days_in_range": 0.0, "last_in_range_check": None, "current_milestone_idx": 0, "last_compound_date": None, "last_dca_date": None, "compound_events": [], "daily_fee_log": []}
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            for k, v in default.items(): state.setdefault(k, v)
            return state
    except Exception: return default

def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f: json.dump(state, f, indent=2)

# ── Analysis ────────────────────────────────────────────────────────────────

def calc_fee_efficiency(price: float, range_low: float, range_high: float) -> float:
    if price < range_low or price > range_high: return 0.0
    position = (price - range_low) / (range_high - range_low)
    return round(max(0, min(100, (1 - abs(position - 0.5) * 2) * 100)), 1)

def is_quiet_hours() -> bool:
    eastern = timezone(timedelta(hours=-4))
    now = datetime.now(eastern)
    return now.hour >= QUIET_START or now.hour < QUIET_END

def estimate_daily_fees(pool: dict, position_usd: float) -> float:
    fee_rate = 0.0005
    volume_24h = pool.get("volume_24h", 0)
    liquidity = pool.get("liquidity_usd", 1)
    if liquidity <= 0 or volume_24h <= 0: return 0.0
    return round((volume_24h * fee_rate) * (position_usd / liquidity), 4)

def calc_apr_from_volume(pool: dict) -> float:
    fee_rate = 0.0005
    volume_24h = pool.get("volume_24h", 0)
    liquidity = pool.get("liquidity_usd", 1)
    if liquidity <= 0: return 0.0
    return round(((volume_24h * fee_rate) / liquidity) * 100 * 365, 1)

def update_compound_tracking(state: dict, in_range: bool, est_fees: float) -> dict:
    eastern = timezone(timedelta(hours=-4))
    now = datetime.now(eastern)
    if state["tracking_started"] is None: state["tracking_started"] = now.isoformat()
    if in_range:
        state["total_days_in_range"] = round(state["total_days_in_range"] + (1.0/144.0), 4)
        state["total_fees_earned_usd"] = round(state["total_fees_earned_usd"] + (est_fees * (1.0/144.0)), 4)
    for i, ms in enumerate(MILESTONES):
        if est_fees >= ms["daily_fees"]: state["current_milestone_idx"] = i
        else: break
    return state

def format_report(price, in_range, efficiency, pool, state, birdeye, est_fees, apr, range_low, range_high) -> str:
    eastern = timezone(timedelta(hours=-4))
    now_str = datetime.now(eastern).strftime("%I:%M %p EDT")
    status = "🚨 OUT OF RANGE" if not in_range else ("⚠️ LOW EFFICIENCY" if efficiency < 75 else "✅ ALL GOOD")
    source_tag = "🐦 Birdeye" if birdeye else "📊 DexScreener"
    lines = [
        f"**AVAX/USDC LP Monitor** — {now_str}",
        f"Data: {source_tag}",
        f"",
        f"**Status:** {status}",
        f"**AVAX Price:** ${price:.4f}",
        f"**Your Range:** ${range_low:.2f} – ${range_high:.2f}",
        f"**Fee Efficiency:** {efficiency:.1f}%",
        f"",
        f"**Pool (24h):**",
        f"- Volume: ${pool['volume_24h']:,.0f}",
        f"- Liquidity: ${pool['liquidity_usd']:,.0f}",
        f"- Price Δ24h: {pool['price_change_24h']:+.1f}%",
        f"- Est. APR: {apr:.1f}%",
        f"",
        f"**Compound Tracker:**",
        f"- Est. Daily Fees: ${est_fees:.2f}",
        f"- Cumulative Fees: ${state['total_fees_earned_usd']:.2f}",
        f"- Days in Range: {state['total_days_in_range']:.1f}",
        f"- Current Milestone: {MILESTONES[state['current_milestone_idx']]['label']} ✅",
    ]
    return "\n".join(lines)

def main():
    if is_quiet_hours():
        print("QUIET_HOURS"); sys.exit(0)
    pos_data = load_position()
    p_usd = pos_data.get("entry_total_usd", 83.92)
    range_low, range_high = load_range()
    birdeye = fetch_birdeye()
    try: pool = fetch_dexscreener()
    except Exception:
        if birdeye: pool = { "source": "birdeye", "price": birdeye["price"], "volume_24h": birdeye["volume_24h"], "liquidity_usd": birdeye["liquidity_usd"], "price_change_24h": birdeye["price_change_24h"] }
        else: print("ERROR"); sys.exit(1)
    price = birdeye["price"] if birdeye else pool["price"]
    in_range = range_low <= price <= range_high
    efficiency = calc_fee_efficiency(price, range_low, range_high)
    state = load_state()
    apr = calc_apr_from_volume(pool)
    est_fees = estimate_daily_fees(pool, p_usd)
    state = update_compound_tracking(state, in_range, est_fees)
    report = format_report(price, in_range, efficiency, pool, state, birdeye, est_fees, apr, range_low, range_high)
    if not in_range or efficiency < 75:
        print("OK\n" + report)
    else:
        print("SILENT")
    save_state(state)

if __name__ == "__main__":
    main()
