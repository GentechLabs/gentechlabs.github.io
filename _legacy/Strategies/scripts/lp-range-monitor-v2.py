#!/usr/bin/env python3
"""
Enhanced LP Range Monitor — LFJ AVAX/USDC Pool (Birdeye Edition)
Phase 1: Birdeye x402 data source with security analytics + DexScreener fallback.

New features over v1:
  - Birdeye token security score + holder distribution
  - Buy/sell pressure analysis
  - Token metadata enrichment
  - Graceful fallback to DexScreener if Birdeye unavailable
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional

# ── Config ──────────────────────────────────────────────────────────────────
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
CHAIN = "avalanche"
RANGE_LOW = 9.30
RANGE_HIGH = 9.60
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-range-state.json")
POSITION_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-position-tracker.json")

# Birdeye config (Avalanche AVAX wrapped token)
AVAX_ADDRESS = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"  # WAVAX
USDC_ADDRESS = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"  # USDC on AVAX

# Data source priority
DEXSCREENER_URL = f"https://api.dexscreener.com/latest/dex/pairs/{CHAIN}/{POOL_ADDRESS}"

# Quiet hours (Eastern Time)
QUIET_START = 23  # 11 PM
QUIET_END = 6     # 6:30 AM

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
    """Fetch pool data from DexScreener (free, no key)."""
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
        "txns_24h": pair.get("txns", {}).get("h24", {}),
    }


def fetch_birdeye() -> Optional[dict]:
    """Fetch enriched data from Birdeye. Returns None if unavailable."""
    if not BIRDEYE_AVAILABLE:
        return None

    try:
        config = BirdeyeConfig.load()
        if not config.is_configured:
            return None

        # Override chain to avalanche for this pool
        config.chain = "avalanche"

        with BirdeyeClient(config) as client:
            # Get token overview for WAVAX
            overview = client.token_overview(AVAX_ADDRESS, "avalanche")
            if "error" in overview:
                print(f"Birdeye overview error: {overview['error']}", file=sys.stderr)
                return None

            # Get security data
            security = client.token_security(AVAX_ADDRESS, "avalanche")

            # Get trade data
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
    """Extract top holder concentration from security data."""
    if "error" in security:
        return None
    holders = security.get("holders", security.get("topHolders", []))
    if holders and isinstance(holders, list) and len(holders) > 0:
        return float(holders[0].get("percentage", holders[0].get("pct", 0)))
    return None


def _calc_buy_sell_ratio(trades: dict) -> Optional[float]:
    """Calculate buy/sell ratio from trade data."""
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
        return {"out_of_range_since": None, "last_alert": None, "last_price": None}


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ── Position Tracker ─────────────────────────────────────────────────────────

def load_position() -> dict:
    """Load position entry data. Create default if missing."""
    try:
        with open(POSITION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default: Jordan's Mar 31 entry
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


def calc_impermanent_loss(entry_price: float, current_price: float) -> dict:
    """Calculate IL given entry and current price."""
    if entry_price <= 0 or current_price <= 0:
        return {"il_pct": 0, "il_usd": 0}
    price_ratio = current_price / entry_price
    # IL formula for 50/50 LP
    il_pct = (2 * (price_ratio ** 0.5) / (1 + price_ratio) - 1) * 100
    return {
        "il_pct": round(il_pct, 2),
        "price_ratio": round(price_ratio, 4)
    }


def calc_position_pnl(price: float, position: dict, fees_earned: float = 0) -> dict:
    """Full P&L breakdown for LP position."""
    entry = position.get("entry_total_usd", 31.16)
    entry_avax = position.get("entry_avax", 1.39)
    entry_usdc = position.get("entry_usdc", 18.85)
    entry_price = position.get("entry_avax_price", 8.85)

    # Current holdings if held (no LP)
    hold_value = (entry_avax * price) + entry_usdc

    # IL calculation
    il = calc_impermanent_loss(entry_price, price)
    il_usd = hold_value * (il["il_pct"] / 100)

    # LP value = hold value - IL
    lp_value = hold_value - abs(il_usd) + fees_earned

    # Net P&L
    net_pnl = lp_value - entry
    net_pnl_pct = (net_pnl / entry) * 100 if entry > 0 else 0

    # vs HODL benchmark
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


# ── Analysis ────────────────────────────────────────────────────────────────

def calc_fee_efficiency(price: float) -> float:
    if price < RANGE_LOW or price > RANGE_HIGH:
        return 0.0
    position = (price - RANGE_LOW) / (RANGE_HIGH - RANGE_LOW)
    efficiency = (1 - abs(position - 0.5) * 2) * 100
    return round(max(0, min(100, efficiency)), 1)


def is_quiet_hours() -> bool:
    eastern = timezone(timedelta(hours=-4))
    now = datetime.now(eastern)
    hour = now.hour
    if hour >= QUIET_START or hour < QUIET_END:
        return True
    if hour == QUIET_END and now.minute < 30:
        return True
    return False


def format_report(price: float, in_range: bool, efficiency: float, pool: dict, state: dict, birdeye: Optional[dict], pnl: Optional[dict] = None) -> str:
    """Format status report with Birdeye enrichment and position P&L."""
    eastern = timezone(timedelta(hours=-4))
    now_str = datetime.now(eastern).strftime("%I:%M %p EDT")

    # Status
    if not in_range:
        status = "🚨 OUT OF RANGE"
    elif efficiency < 75:
        status = "⚠️ LOW EFFICIENCY"
    else:
        status = "✅ ALL GOOD"

    # Price position
    pct_from_low = ((price - RANGE_LOW) / RANGE_LOW) * 100
    pct_from_high = ((price - RANGE_HIGH) / RANGE_HIGH) * 100

    # Data source indicator
    source = birdeye["source"] if birdeye else pool.get("source", "dexscreener")
    source_tag = "🐦 Birdeye" if source == "birdeye" else "📊 DexScreener"

    lines = [
        f"**AVAX/USDC LP Monitor** — {now_str}",
        f"Data: {source_tag}",
        f"",
        f"**Status:** {status}",
        f"**AVAX Price:** ${price:.4f}",
        f"**Your Range:** ${RANGE_LOW:.2f} – ${RANGE_HIGH:.2f}",
        f"**Fee Efficiency:** {efficiency:.1f}%",
        f"",
        f"**Pool (24h):**",
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
        if birdeye.get("unique_traders_24h"):
            lines.append(f"- Unique Traders: {birdeye['unique_traders_24h']:,}")

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

    # Out of range details
    if not in_range:
        if price < RANGE_LOW:
            lines.append(f"- Price is **{abs(pct_from_low):.1f}% below** lower bound")
        else:
            lines.append(f"- Price is **{abs(pct_from_high):.1f}% above** upper bound")
        if state.get("out_of_range_since"):
            lines.append(f"- Out of range since: {state['out_of_range_since']}")

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    if is_quiet_hours():
        print("QUIET_HOURS")
        sys.exit(0)

    # Fetch data — try Birdeye first, fall back to DexScreener
    birdeye = fetch_birdeye()
    try:
        pool = fetch_dexscreener()
    except Exception as e:
        if birdeye and birdeye.get("source") == "birdeye":
            # Use Birdeye as primary if DexScreener fails
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

    # Use best available price (prefer Birdeye if available)
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

    # Alert logic (same as v1)
    should_alert = False
    alert_reason = ""

    if not in_range:
        if state.get("out_of_range_since") is None:
            state["out_of_range_since"] = now_str
            state["out_of_range_first_check"] = True
            print("OUT_OF_RANGE_CONFIRMING")
            save_state(state)
            sys.exit(0)
        elif state.get("out_of_range_first_check"):
            should_alert = True
            alert_reason = "out_of_range_confirmed"
            state["out_of_range_first_check"] = False
    else:
        was_out = state.get("out_of_range_since") is not None
        state["out_of_range_since"] = None
        state["out_of_range_first_check"] = False

        if efficiency < 75:
            should_alert = True
            alert_reason = "low_efficiency"
        elif was_out:
            state["recovered_at"] = now_str

    report = format_report(price, in_range, efficiency, pool, state, birdeye, pnl)

    if should_alert:
        state["last_alert"] = now_str
        print(f"ALERT:{alert_reason}")
        print(report)
    elif in_range and efficiency >= 75:
        print("SILENT")
    else:
        print("OK")
        print(report)

    save_state(state)


if __name__ == "__main__":
    main()
