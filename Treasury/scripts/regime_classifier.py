#!/usr/bin/env python3
"""
Market Regime Classifier — AAE Hybrid Strategy Engine
Classifies current market conditions into regimes for strategy allocation.

Regimes:
  BULL_TRENDING    — Price up, volume increasing, momentum strong
  BEAR_TRENDING    — Price down, volume increasing, momentum weak
  RANGE_BOUND      — Price oscillating, volume normal, no clear trend
  HIGH_VOLATILITY  — Price whipsawing, volume spikes, unclear direction
  ACCUMULATION     — Price flat after dump, volume declining
  PRICE_DISCOVERY  — New highs/lows, no historical reference
"""

import json
import os
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

# ── Config ──────────────────────────────────────────────────────────────────

STATE_DIR = os.path.expanduser("~/.hermes/scripts")
REGIME_STATE_FILE = os.path.join(STATE_DIR, ".aae-regime-state.json")
PRICE_HISTORY_FILE = os.path.join(STATE_DIR, ".aae-price-history.json")

# Regime classification thresholds
THRESHOLDS = {
    "bull_momentum": 0.10,        # 7d price change > 10% = trending
    "bear_momentum": -0.10,       # 7d price change < -10% = trending
    "volume_spike": 1.3,          # volume > 1.3x average = spike
    "volume_low": 0.8,            # volume < 0.8x average = declining
    "high_volatility": 0.08,      # ATR/price > 8% = high volatility
    "range_bound_max_momentum": 0.05,  # |momentum| < 5% = range
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "rsi_neutral_low": 40,
    "rsi_neutral_high": 60,
    "consolidation_hours": 48,    # hours in narrow range = accumulation
}

# Price history window (days to keep)
PRICE_HISTORY_DAYS = 30


# ── Data Fetching ───────────────────────────────────────────────────────────

def fetch_json(url: str, headers: Optional[Dict] = None, timeout: int = 15) -> Optional[Dict]:
    """Fetch JSON from URL with error handling."""
    default_headers = {"User-Agent": "Mozilla/5.0 (AAE-Hybrid/1.0)"}
    if headers:
        default_headers.update(headers)
    try:
        req = urllib.request.Request(url, headers=default_headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[regime] fetch error: {e}", flush=True)
        return None


def fetch_dexscreener_data(pool_address: str) -> Optional[Dict]:
    """Fetch price/volume data from DexScreener."""
    url = f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{pool_address}"
    data = fetch_json(url)
    if not data or "pairs" not in data or not data["pairs"]:
        return None
    pair = data["pairs"][0]
    return {
        "price_usd": float(pair.get("priceUsd", 0)),
        "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
        "volume_6h": float(pair.get("volume", {}).get("h6", 0)),
        "volume_1h": float(pair.get("volume", {}).get("h1", 0)),
        "price_change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
        "price_change_7d": float(pair.get("priceChange", {}).get("h7d", 0)) if pair.get("priceChange", {}).get("h7d") else None,
        "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0)),
        "fdv": float(pair.get("fdv", 0)),
    }


def fetch_defillama_yields(protocol: str = "benqi") -> Optional[Dict]:
    """Fetch staking/lending APR from DeFiLlama Yields API."""
    url = "https://yields.llama.fi/pools"
    data = fetch_json(url)
    if not data or "data" not in data:
        return None

    results = {}
    for pool in data["data"]:
        if pool.get("project", "").lower() == protocol.lower() and pool.get("chain", "").lower() == "avalanche":
            symbol = pool.get("symbol", "")
            results[symbol] = {
                "apy": pool.get("apy", 0),
                "tvl_usd": pool.get("tvlUsd", 0),
                "pool": pool.get("pool", ""),
                "symbol": symbol,
                "reward_tokens": pool.get("rewardTokens", []),
                "stablecoin": pool.get("stablecoin", False),
            }
    return results if results else None


# ── Price History ───────────────────────────────────────────────────────────

def load_price_history() -> List[Dict]:
    """Load price history from state file."""
    try:
        with open(PRICE_HISTORY_FILE) as f:
            data = json.load(f)
            return data.get("history", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_price_history(history: List[Dict]):
    """Save price history to state file."""
    os.makedirs(os.path.dirname(PRICE_HISTORY_FILE), exist_ok=True)
    # Trim to last N days
    cutoff = time.time() - (PRICE_HISTORY_DAYS * 86400)
    history = [h for h in history if h.get("timestamp", 0) > cutoff]
    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump({"history": history, "last_updated": datetime.now(timezone.utc).isoformat()}, f, indent=2)


def record_price(price: float, volume_24h: float, timestamp: Optional[float] = None):
    """Record a price data point."""
    history = load_price_history()
    history.append({
        "timestamp": timestamp or time.time(),
        "price": price,
        "volume_24h": volume_24h,
    })
    save_price_history(history)


# ── Technical Indicators ────────────────────────────────────────────────────

def compute_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Compute RSI from price list (oldest first)."""
    if len(prices) < period + 1:
        return None

    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    # Wilder's smoothing
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def compute_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[float]:
    """Compute Average True Range. With only close prices, approximate using daily ranges."""
    if len(closes) < period + 1:
        return None

    # Approximate TR using close-to-close changes
    trs = [abs(closes[i] - closes[i-1]) for i in range(1, len(closes))]
    if len(trs) < period:
        return None

    atr = sum(trs[:period]) / period
    for i in range(period, len(trs)):
        atr = (atr * (period - 1) + trs[i]) / period
    return atr


def compute_momentum(prices: List[float], lookback: int) -> Optional[float]:
    """Compute momentum as percentage change over lookback periods."""
    if len(prices) < lookback + 1:
        return None
    return (prices[-1] - prices[-lookback - 1]) / prices[-lookback - 1]


# ── Regime Classification ──────────────────────────────────────────────────

def classify_regime(
    price_7d_change: Optional[float],
    volume_24h: float,
    volume_avg: float,
    rsi_14: Optional[float],
    atr_pct: Optional[float],  # ATR as % of price
    price_history: List[float],
) -> Tuple[str, float, Dict[str, Any]]:
    """
    Classify current market regime.

    Returns: (regime, confidence, details)
    """
    T = THRESHOLDS
    details = {}

    # Defaults if data missing
    momentum = price_7d_change if price_7d_change is not None else 0
    vol_ratio = volume_24h / volume_avg if volume_avg > 0 else 1.0
    rsi = rsi_14 if rsi_14 is not None else 50
    atr_p = atr_pct if atr_pct is not None else 0.05

    details["momentum_7d"] = round(momentum, 4)
    details["volume_ratio"] = round(vol_ratio, 2)
    details["rsi_14"] = round(rsi, 1)
    details["atr_pct"] = round(atr_p, 4)

    # Classification logic (priority order)
    if atr_p > T["high_volatility"]:
        # High volatility — price whipsawing
        regime = "HIGH_VOLATILITY"
        confidence = min(0.9, 0.5 + (atr_p - T["high_volatility"]) * 5)
        details["reason"] = f"ATR {atr_p:.1%} exceeds {T['high_volatility']:.0%} threshold"

    elif momentum > T["bull_momentum"] and vol_ratio > T["volume_spike"] and rsi > T["rsi_neutral_high"]:
        regime = "BULL_TRENDING"
        confidence = min(0.95, 0.6 + abs(momentum) * 2 + (vol_ratio - 1) * 0.2)
        details["reason"] = f"Momentum +{momentum:.1%}, volume {vol_ratio:.1f}x, RSI {rsi:.0f}"

    elif momentum < T["bear_momentum"] and vol_ratio > T["volume_spike"] and rsi < T["rsi_neutral_low"]:
        regime = "BEAR_TRENDING"
        confidence = min(0.95, 0.6 + abs(momentum) * 2 + (vol_ratio - 1) * 0.2)
        details["reason"] = f"Momentum {momentum:.1%}, volume {vol_ratio:.1f}x, RSI {rsi:.0f}"

    elif abs(momentum) < T["range_bound_max_momentum"] and vol_ratio < 1.0:
        # Low momentum + low volume = range or accumulation
        # Check if we're near a bottom (accumulation) or just ranging
        if rsi < T["rsi_oversold"] or (len(price_history) > 20 and min(price_history[-20:]) / max(price_history[-20:]) > 0.95):
            regime = "ACCUMULATION"
            confidence = 0.6
            details["reason"] = f"Low momentum ({momentum:.1%}), low volume, RSI {rsi:.0f}"
        else:
            regime = "RANGE_BOUND"
            confidence = 0.7
            details["reason"] = f"Momentum {momentum:.1%}, volume {vol_ratio:.1f}x"

    elif abs(momentum) < T["range_bound_max_momentum"]:
        regime = "RANGE_BOUND"
        confidence = 0.65
        details["reason"] = f"Momentum {momentum:.1%} (range)"

    else:
        # Trending but not strongly — could be price discovery
        if len(price_history) > 0 and (max(price_history[-20:]) / min(price_history[-20:]) > 1.15 if len(price_history) >= 20 else False):
            regime = "PRICE_DISCOVERY"
            confidence = 0.5
            details["reason"] = f"Strong move, wide range, momentum {momentum:.1%}"
        else:
            # Default to the dominant trend
            if momentum > 0:
                regime = "BULL_TRENDING"
                confidence = 0.5
                details["reason"] = f"Moderate bullish momentum {momentum:.1%}"
            else:
                regime = "BEAR_TRENDING"
                confidence = 0.5
                details["reason"] = f"Moderate bearish momentum {momentum:.1%}"

    details["confidence"] = round(confidence, 2)
    return regime, confidence, details


# ── Main Classification Pipeline ───────────────────────────────────────────

def run_classification(pool_address: str = "0x864d4e5ee7318e97483db7eb0912e09f161516ea") -> Dict[str, Any]:
    """
    Run full regime classification pipeline.
    Returns structured regime data.
    """
    # 1. Fetch current price/volume from DexScreener
    dex = fetch_dexscreener_data(pool_address)
    if not dex:
        return {"error": "Failed to fetch DexScreener data", "regime": "UNKNOWN", "confidence": 0}

    price = dex["price_usd"]
    volume_24h = dex["volume_24h"]
    price_change_24h = dex["price_change_24h"]
    price_change_7d = dex.get("price_change_7d")

    # 2. Record price in history
    record_price(price, volume_24h)

    # 3. Load price history for indicators
    raw_history = load_price_history()
    prices = [h["price"] for h in raw_history]

    # Compute volume average from history
    volumes = [h["volume_24h"] for h in raw_history[-7:]] if len(raw_history) >= 7 else [volume_24h]
    volume_avg = sum(volumes) / len(volumes) if volumes else volume_24h

    # 4. Compute indicators
    rsi = compute_rsi(prices) if len(prices) >= 15 else None
    atr = compute_atr(prices, prices, prices) if len(prices) >= 15 else None
    atr_pct = atr / price if atr and price > 0 else None

    # 5. Classify regime
    regime, confidence, details = classify_regime(
        price_7d_change=price_change_7d,
        volume_24h=volume_24h,
        volume_avg=volume_avg,
        rsi_14=rsi,
        atr_pct=atr_pct,
        price_history=prices[-20:] if prices else [],
    )

    # 6. Load previous regime for change detection
    prev_regime = "UNKNOWN"
    try:
        with open(REGIME_STATE_FILE) as f:
            state = json.load(f)
            prev_regime = state.get("regime", "UNKNOWN")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # 7. Save current regime state
    result = {
        "regime": regime,
        "confidence": confidence,
        "prev_regime": prev_regime,
        "regime_changed": regime != prev_regime and prev_regime != "UNKNOWN",
        "details": details,
        "price": price,
        "volume_24h": volume_24h,
        "volume_avg_7d": round(volume_avg, 2),
        "price_change_24h": price_change_24h,
        "price_change_7d": price_change_7d,
        "rsi_14": rsi,
        "atr_pct": atr_pct,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_points": len(prices),
    }

    os.makedirs(os.path.dirname(REGIME_STATE_FILE), exist_ok=True)
    with open(REGIME_STATE_FILE, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ── CLI Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    pool = sys.argv[1] if len(sys.argv) > 1 else "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
    result = run_classification(pool)
    print(json.dumps(result, indent=2))
