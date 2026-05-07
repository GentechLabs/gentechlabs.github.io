#!/usr/bin/env python3
"""
LP Range Monitor v3 — LFJ AVAX/USDC Pool
Milestone tracker + tiered breakout alerts.

New in v3:
  - Range updated to 9.44–9.74 (Bid-Ask shape)
  - Fee efficiency milestone tracker (cumulative fees, milestones)
  - Tiered alerts: ⚠️ light warning → 🔴 red alert (5-min escalation)
  - Breakout direction tracking (upside/downside)
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
RANGE_LOW = 9.45
RANGE_HIGH = 9.74
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-range-state.json")
POSITION_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-position-tracker.json")
MILESTONE_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-milestone-tracker.json")

# Fee milestones (USD thresholds)
FEE_MILESTONES = [0.50, 1.00, 2.00, 5.00, 10.00, 25.00, 50.00, 100.00]

# Birdeye config
AVAX_ADDRESS = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC_ADDRESS = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"

DEXSCREENER_URL = f"https://api.dexscreener.com/latest/dex/pairs/{CHAIN}/{POOL_ADDRESS}"

# Quiet hours (Eastern Time)
QUIET_START = 23
QUIET_END = 6

# Alert escalation
ALERT_COOLDOWN_MIN = 5  # Minutes between light warning and red alert

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
    """Fetch pool data from DexScreener."""
    req = urllib.request.Request(DEXSCREENER_URL, headers={"User-Agent": "Gentech-Labs/3.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    pair = data.get("pair", data.get("pairs", [{}])[0] if data.get("pairs") else {})
    return {
        "source": "dexscreener",
        "price": float(pair.get("priceNative", 0)),
        "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
        "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0)),
        "price_change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
        "txns_24h": pair.get("txns", {}).get("h24", {}),
    }


def fetch_birdeye() -> Optional[dict]:
    """Fetch enriched data from Birdeye."""
    if not BIRDEYE_AVAILABLE:
        return None
    try:
        config = BirdeyeConfig.load()
        if not config.is_configured:
            return None
        config.chain = "avalanche"
        with BirdeyeClient(config) as client:
            overview = client.token_overview(AVAX_ADDRESS, "avalanche")
            if "error" in overview:
                return None
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
                "top_holder_pct": _extract_top_holder_pct(security),
                "buy_sell_ratio": _calc_buy_sell_ratio(trades),
                "unique_traders_24h": trades.get("uniqueWallet24h", trades.get("uniqueTraders", None)) if "error" not in trades else None,
            }
    except Exception as e:
        print(f"Birdeye fetch failed: {e}", file=sys.stderr)
        return None


def _extract_top_holder_pct(security: dict) -> Optional[float]:
    if "error" in security:
        return None
    holders = security.get("holders", security.get("topHolders", []))
    if holders and isinstance(holders, list) and len(holders) > 0:
        return float(holders[0].get("percentage", holders[0].get("pct", 0)))
    return None


def _calc_buy_sell_ratio(trades: dict) -> Optional[float]:
    if "error" in trades:
        return None
    buys = trades.get("buys24h", trades.get("buy", 0))
    sells = trades.get("sells24h", trades.get("sell", 0))
    if sells and sells > 0:
        return round(buys / sells, 2)
    return None


# ── State Management ────────────────────────────────────────────────────────

def load_state() -> dict:
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "out_of_range_since": None,
            "last_alert": None,
            "last_price": None,
            "alert_level": None,         # None | "warning" | "red"
            "alert_direction": None,     # "above" | "below"
            "warning_sent_at": None,
        }


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ── Position Tracker ─────────────────────────────────────────────────────────

def load_position() -> dict:
    try:
        with open(POSITION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        default = {
            "entry_date": "2026-03-31",
            "entry_avax": 1.39,
            "entry_usdc": 18.85,
            "entry_avax_price": 8.85,
            "entry_total_usd": 31.16,
            "notes": "LFJ AVAX/USDC 5bps LP — concentrated range"
        }
        save_position(default)
        return default


def save_position(pos: dict):
    os.makedirs(os.path.dirname(POSITION_FILE), exist_ok=True)
    with open(POSITION_FILE, "w") as f:
        json.dump(pos, f, indent=2)


# ── Milestone Tracker ───────────────────────────────────────────────────────

def load_milestone() -> dict:
    """Load fee milestone tracking data."""
    try:
        with open(MILESTONE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "total_fees_earned": 0.0,
            "milestones_reached": [],
            "last_milestone": None,
            "fee_history": [],  # [{timestamp, fees, price, efficiency}]
            "session_start": datetime.now(timezone.utc).isoformat(),
        }


def save_milestone(data: dict):
    os.makedirs(os.path.dirname(MILESTONE_FILE), exist_ok=True)
    with open(MILESTONE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def update_milestone(fees: float, price: float, efficiency: float) -> Optional[float]:
    """Update milestone tracker, return newly reached milestone threshold if any."""
    data = load_milestone()
    data["total_fees_earned"] = round(fees, 4)

    # Add to history (keep last 100 entries)
    eastern = timezone(timedelta(hours=-4))
    now_str = datetime.now(eastern).strftime("%Y-%m-%d %H:%M EDT")
    data["fee_history"].append({
        "timestamp": now_str,
        "fees": round(fees, 4),
        "price": round(price, 4),
        "efficiency": round(efficiency, 1),
    })
    if len(data["fee_history"]) > 100:
        data["fee_history"] = data["fee_history"][-100:]

    # Check milestones
    new_milestone = None
    for m in FEE_MILESTONES:
        if fees >= m and m not in data["milestones_reached"]:
            data["milestones_reached"].append(m)
            data["last_milestone"] = m
            new_milestone = m

    save_milestone(data)
    return new_milestone


def format_milestone_report() -> str:
    """Format milestone tracker summary."""
    data = load_milestone()
    total = data["total_fees_earned"]
    reached = data["milestones_reached"]
    history = data.get("fee_history", [])

    lines = [
        "**Fee Milestone Tracker**",
        f"- Total Fees Earned: ${total:.4f}",
        f"- Milestones Hit: {len(reached)}/{len(FEE_MILESTONES)}",
    ]

    if reached:
        last = max(reached)
        next_ms = None
        for m in FEE_MILESTONES:
            if m > last:
                next_ms = m
                break
        lines.append(f"- Last Milestone: ${last:.2f}")
        if next_ms:
            pct = (total / next_ms) * 100
            lines.append(f"- Next: ${next_ms:.2f} ({pct:.0f}% there)")

    # Fee rate (last 24h estimate from history)
    if len(history) >= 2:
        first = history[0]
        last = history[-1]
        fee_delta = last["fees"] - first["fees"]
        lines.append(f"- Session Fees: +${fee_delta:.4f}")

    return "\n".join(lines)


# ── Analysis ────────────────────────────────────────────────────────────────

def calc_fee_efficiency(price: float) -> float:
    if price < RANGE_LOW or price > RANGE_HIGH:
        return 0.0
    position = (price - RANGE_LOW) / (RANGE_HIGH - RANGE_LOW)
    efficiency = (1 - abs(position - 0.5) * 2) * 100
    return round(max(0, min(100, efficiency)), 1)


def calc_impermanent_loss(entry_price: float, current_price: float) -> dict:
    if entry_price <= 0 or current_price <= 0:
        return {"il_pct": 0, "il_usd": 0}
    price_ratio = current_price / entry_price
    il_pct = (2 * (price_ratio ** 0.5) / (1 + price_ratio) - 1) * 100
    return {"il_pct": round(il_pct, 2), "price_ratio": round(price_ratio, 4)}


def calc_position_pnl(price: float, position: dict, fees_earned: float = 0) -> dict:
    entry = position.get("entry_total_usd", 31.16)
    entry_avax = position.get("entry_avax", 1.39)
    entry_usdc = position.get("entry_usdc", 18.85)
    entry_price = position.get("entry_avax_price", 8.85)

    hold_value = (entry_avax * price) + entry_usdc
    il = calc_impermanent_loss(entry_price, price)
    il_usd = hold_value * (il["il_pct"] / 100)
    lp_value = hold_value - abs(il_usd) + fees_earned
    net_pnl = lp_value - entry
    net_pnl_pct = (net_pnl / entry) * 100 if entry > 0 else 0
    hodl_value = (entry_avax * price) + entry_usdc
    vs_hodl = lp_value - hodl_value

    return {
        "entry_usd": round(entry, 2),
        "current_lp_value": round(lp_value, 2),
        "hold_value": round(hold_value, 2),
        "il_pct": il["il_pct"],
        "il_usd": round(il_usd, 2),
        "fees_earned": round(fees_earned, 2),
        "net_pnl": round(net_pnl, 2),
        "net_pnl_pct": round(net_pnl_pct, 2),
        "vs_hodl": round(vs_hodl, 2),
        "price_ratio": il["price_ratio"]
    }


def is_quiet_hours() -> bool:
    eastern = timezone(timedelta(hours=-4))
    now = datetime.now(eastern)
    hour = now.hour
    if hour >= QUIET_START or hour < QUIET_END:
        return True
    if hour == QUIET_END and now.minute < 30:
        return True
    return False


# ── Tiered Alert Logic ─────────────────────────────────────────────────────

def handle_out_of_range(price: float, state: dict, now_str: str) -> tuple:
    """
    Tiered alert logic:
    - First detection: mark it, send light warning
    - If still out after ALERT_COOLDOWN_MIN: red alert
    Returns (alert_level, alert_direction) or (None, None)
    """
    direction = "above" if price > RANGE_HIGH else "below"
    out_since = state.get("out_of_range_since")
    alert_level = state.get("alert_level")

    if out_since is None:
        # First detection — mark it, will alert on THIS check
        state["out_of_range_since"] = now_str
        state["alert_level"] = "warning"
        state["alert_direction"] = direction
        state["warning_sent_at"] = now_str
        return "warning", direction

    # Already tracked — check if escalation needed
    if alert_level == "warning":
        # Parse warning time and check cooldown
        try:
            warning_time = datetime.strptime(state["warning_sent_at"], "%H:%M EDT")
            current_time = datetime.strptime(now_str, "%H:%M EDT")
            diff_min = (current_time - warning_time).total_seconds() / 60
            if diff_min >= ALERT_COOLDOWN_MIN:
                state["alert_level"] = "red"
                return "red", direction
        except (ValueError, TypeError):
            # Can't parse time — escalate anyway
            state["alert_level"] = "red"
            return "red", direction

    return None, None


def handle_in_range(state: dict, now_str: str) -> bool:
    """Reset alert state when back in range. Returns True if was previously out."""
    was_out = state.get("out_of_range_since") is not None
    state["out_of_range_since"] = None
    state["alert_level"] = None
    state["alert_direction"] = None
    state["warning_sent_at"] = None
    if was_out:
        state["recovered_at"] = now_str
    return was_out


# ── Report Formatting ──────────────────────────────────────────────────────

def format_report(price: float, in_range: bool, efficiency: float, pool: dict,
                  state: dict, birdeye: Optional[dict], pnl: Optional[dict],
                  milestone_report: str, alert_level: Optional[str] = None,
                  alert_direction: Optional[str] = None) -> str:
    eastern = timezone(timedelta(hours=-4))
    now_str = datetime.now(eastern).strftime("%I:%M %p EDT")

    # Status emoji
    if alert_level == "red":
        status = "🔴 RED ALERT — OUT OF RANGE"
    elif alert_level == "warning":
        status = "⚠️ LIGHT WARNING — Testing Range Boundary"
    elif not in_range:
        status = "🚨 OUT OF RANGE"
    elif efficiency < 75:
        status = "⚠️ LOW EFFICIENCY"
    else:
        status = "✅ ALL GOOD"

    pct_from_low = ((price - RANGE_LOW) / RANGE_LOW) * 100
    pct_from_high = ((price - RANGE_HIGH) / RANGE_HIGH) * 100

    source = birdeye["source"] if birdeye else pool.get("source", "dexscreener")
    source_tag = "🐦 Birdeye" if source == "birdeye" else "📊 DexScreener"

    lines = [
        f"**AVAX/USDC LP Monitor v3** — {now_str}",
        f"Data: {source_tag}",
        "",
        f"**Status:** {status}",
        f"**AVAX Price:** ${price:.4f}",
        f"**Your Range:** ${RANGE_LOW:.2f} – ${RANGE_HIGH:.2f}",
        f"**Fee Efficiency:** {efficiency:.1f}%",
        "",
        "**Pool (24h):**",
        f"- Volume: ${pool['volume_24h']:,.0f}",
        f"- Liquidity: ${pool['liquidity_usd']:,.0f}",
        f"- Price Δ24h: {pool['price_change_24h']:+.1f}%",
    ]

    # Birdeye enrichment
    if birdeye and birdeye.get("source") == "birdeye":
        lines.append("")
        lines.append("**Birdeye Analytics:**")
        if birdeye.get("market_cap"):
            lines.append(f"- Market Cap: ${birdeye['market_cap']:,.0f}")
        if birdeye.get("security_score") is not None:
            score = birdeye["security_score"]
            emoji = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
            lines.append(f"- Security Score: {emoji} {score}/100")
        if birdeye.get("top_holder_pct") is not None:
            lines.append(f"- Top Holder: {birdeye['top_holder_pct']:.1f}%")
        if birdeye.get("buy_sell_ratio") is not None:
            ratio = birdeye["buy_sell_ratio"]
            arrow = "📈" if ratio > 1.2 else "📉" if ratio < 0.8 else "➡️"
            lines.append(f"- Buy/Sell Ratio: {arrow} {ratio}")

    # Position P&L
    if pnl:
        lines.append("")
        pnl_emoji = "📈" if pnl["net_pnl"] >= 0 else "📉"
        lines.append(f"**Position P&L** {pnl_emoji}")
        lines.append(f"- Entry: ${pnl['entry_usd']} (Mar 31)")
        lines.append(f"- LP Value: ${pnl['current_lp_value']}")
        lines.append(f"- IL: {pnl['il_pct']:+.2f}% (${pnl['il_usd']:+.2f})")
        lines.append(f"- Fees: +${pnl['fees_earned']:.2f}")
        lines.append(f"- **Net: ${pnl['net_pnl']:+.2f} ({pnl['net_pnl_pct']:+.1f}%)**")
        lines.append(f"- vs HODL: ${pnl['vs_hodl']:+.2f}")

    # Milestone tracker
    lines.append("")
    lines.append(milestone_report)

    # Out of range details
    if not in_range:
        lines.append("")
        if price < RANGE_LOW:
            lines.append(f"⬇️ Price is **{abs(pct_from_low):.1f}% below** lower bound")
        else:
            lines.append(f"⬆️ Price is **{abs(pct_from_high):.1f}% above** upper bound")
        if state.get("out_of_range_since"):
            lines.append(f"- Out of range since: {state['out_of_range_since']}")
        if alert_direction:
            lines.append(f"- Breakout direction: **{alert_direction}**")

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    if is_quiet_hours():
        print("QUIET_HOURS")
        sys.exit(0)

    # Fetch data
    birdeye = fetch_birdeye()
    try:
        pool = fetch_dexscreener()
    except Exception as e:
        if birdeye and birdeye.get("source") == "birdeye":
            pool = {
                "source": "birdeye",
                "price": birdeye["price"],
                "volume_24h": birdeye["volume_24h"],
                "liquidity_usd": birdeye["liquidity_usd"],
                "price_change_24h": birdeye["price_change_24h"],
            }
        else:
            print(f"ERROR: All data sources failed — {e}", file=sys.stderr)
            sys.exit(1)

    price = birdeye["price"] if birdeye and birdeye.get("source") == "birdeye" else pool["price"]
    in_range = RANGE_LOW <= price <= RANGE_HIGH
    efficiency = calc_fee_efficiency(price)
    state = load_state()
    position = load_position()
    pnl = calc_position_pnl(price, position)
    eastern = timezone(timedelta(hours=-4))
    now_str = datetime.now(eastern).strftime("%H:%M EDT")

    # Update state
    state["last_price"] = price
    state["last_check"] = now_str
    state["data_source"] = birdeye["source"] if birdeye else pool.get("source")

    # Update milestone tracker
    milestone = update_milestone(pnl["fees_earned"], price, efficiency)
    milestone_report = format_milestone_report()

    # Tiered alert logic
    alert_level = None
    alert_direction = None

    if not in_range:
        alert_level, alert_direction = handle_out_of_range(price, state, now_str)
    else:
        was_out = handle_in_range(state, now_str)

    report = format_report(price, in_range, efficiency, pool, state, birdeye,
                           pnl, milestone_report, alert_level, alert_direction)

    # Output handling
    if alert_level == "red":
        state["last_alert"] = now_str
        print(f"ALERT:red_breakout_{alert_direction}")
        print(report)
    elif alert_level == "warning":
        print(f"ALERT:light_warning_{alert_direction}")
        print(report)
    elif not in_range:
        # Shouldn't reach here with new logic, but safety net
        print(f"ALERT:out_of_range_{state.get('alert_direction', 'unknown')}")
        print(report)
    elif milestone:
        # Milestone reached — always announce
        print(f"MILESTONE:${milestone:.2f}")
        print(report)
    elif efficiency < 75:
        print("LOW_EFFICIENCY")
        print(report)
    elif in_range and efficiency >= 75:
        print("SILENT")
    else:
        print("OK")
        print(report)

    save_state(state)


if __name__ == "__main__":
    main()
