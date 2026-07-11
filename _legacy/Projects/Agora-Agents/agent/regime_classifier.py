#!/usr/bin/env python3
"""
Market Regime Classifier — Adapted from LP Monitor for Agora Agents

Classifies market conditions into 6 regimes for portfolio allocation:
  BULL_TRENDING, BEAR_TRENDING, RANGE_BOUND,
  HIGH_VOLATILITY, ACCUMULATION, PRICE_DISCOVERY

Source: Ported from LP Monitor's regime_classifier.py (AAE Hybrid Strategy Engine)
"""

import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

# ── Config ──────────────────────────────────────────────────────────────────

STATE_DIR = os.path.expanduser("~/.hermes/scripts")
REGIME_STATE_FILE = os.path.join(STATE_DIR, ".agora-regime-state.json")
PRICE_HISTORY_FILE = os.path.join(STATE_DIR, ".agora-price-history.json")

# Regime classification thresholds (ported from LP Monitor)
THRESHOLDS = {
    "bull_momentum": 0.10,
    "bear_momentum": -0.10,
    "volume_spike": 1.3,
    "volume_low": 0.8,
    "high_volatility": 0.08,
    "range_bound_max_momentum": 0.05,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "rsi_neutral_low": 40,
    "rsi_neutral_high": 60,
    "consolidation_hours": 48,
}

PRICE_HISTORY_DAYS = 30


# ── Data Fetching ───────────────────────────────────────────────────────────

def fetch_json(url: str, headers: Optional[Dict] = None, timeout: int = 15) -> Optional[Dict]:
    """Fetch JSON from URL with error handling."""
    default_headers = {"User-Agent": "Agora-Portfolio/1.0"}
    if headers:
        default_headers.update(headers)
    try:
        req = urllib.request.Request(url, headers=default_headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[regime] fetch error: {e}", flush=True)
        return None


def fetch_dexscreener_data(token_address: str, chain: str = "base") -> Optional[Dict]:
    """Fetch price/volume data from DexScreener."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    data = fetch_json(url)
    if not data or "pairs" not in data or not data["pairs"]:
        return None

    # Find the most liquid pair
    pairs = sorted(data["pairs"], key=lambda p: float(p.get("liquidity", {}).get("usd", 0)), reverse=True)
    if not pairs:
        return None

    pair = pairs[0]
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


# ── Price History ───────────────────────────────────────────────────────────

def load_price_history() -> List[Dict]:
    try:
        with open(PRICE_HISTORY_FILE) as f:
            return json.load(f).get("history", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_price_history(history: List[Dict]):
    os.makedirs(os.path.dirname(PRICE_HISTORY_FILE), exist_ok=True)
    cutoff = time.time() - (PRICE_HISTORY_DAYS * 86400)
    history = [h for h in history if h.get("timestamp", 0) > cutoff]
    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump({"history": history, "last_updated": datetime.now(timezone.utc).isoformat()}, f, indent=2)


def record_price(price: float, volume_24h: float, token: str = "default"):
    history = load_price_history()
    history.append({
        "timestamp": time.time(),
        "price": price,
        "volume_24h": volume_24h,
        "token": token,
    })
    save_price_history(history)


# ── Technical Indicators ────────────────────────────────────────────────────

def compute_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    if len(prices) < period + 1:
        return None
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def compute_atr(closes: List[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None
    trs = [abs(closes[i] - closes[i - 1]) for i in range(1, len(closes))]
    if len(trs) < period:
        return None

    atr = sum(trs[:period]) / period
    for i in range(period, len(trs)):
        atr = (atr * (period - 1) + trs[i]) / period
    return atr


def compute_momentum(prices: List[float], lookback: int) -> Optional[float]:
    if len(prices) < lookback + 1:
        return None
    return (prices[-1] - prices[-lookback - 1]) / prices[-lookback - 1]


# ── Regime Classification ──────────────────────────────────────────────────

def classify_regime(
    price_7d_change: Optional[float],
    volume_24h: float,
    volume_avg: float,
    rsi_14: Optional[float],
    atr_pct: Optional[float],
    price_history: List[float],
) -> Tuple[str, float, Dict[str, Any]]:
    """
    Classify current market regime.
    Returns: (regime, confidence, details)
    """
    T = THRESHOLDS
    details = {}

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
        if rsi < T["rsi_oversold"] or (
            len(price_history) > 20
            and min(price_history[-20:]) / max(price_history[-20:]) > 0.95
        ):
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
        if len(price_history) > 0 and (
            max(price_history[-20:]) / min(price_history[-20:]) > 1.15
            if len(price_history) >= 20
            else False
        ):
            regime = "PRICE_DISCOVERY"
            confidence = 0.5
            details["reason"] = f"Strong move, wide range, momentum {momentum:.1%}"
        else:
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


# ── Public API ──────────────────────────────────────────────────────────────

def classify_current_market(
    token_address: str = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC on Base
    chain: str = "base",
) -> Dict[str, Any]:
    """
    Classify the current market regime for a token.
    Returns structured regime data.
    """
    # 1. Fetch price/volume from DexScreener
    dex = fetch_dexscreener_data(token_address, chain)
    if not dex:
        return {"error": "Failed to fetch data", "regime": "UNKNOWN", "confidence": 0}

    price = dex["price_usd"]
    volume_24h = dex["volume_24h"]
    price_change_7d = dex.get("price_change_7d")

    # 2. Record price
    record_price(price, volume_24h, token_address)

    # 3. Load history for indicators
    raw_history = load_price_history()
    prices = [h["price"] for h in raw_history]
    volumes = [h["volume_24h"] for h in raw_history[-7:]] if len(raw_history) >= 7 else [volume_24h]
    volume_avg = sum(volumes) / len(volumes) if volumes else volume_24h

    # 4. Compute indicators
    rsi = compute_rsi(prices) if len(prices) >= 15 else None
    atr = compute_atr(prices) if len(prices) >= 15 else None
    atr_pct = atr / price if atr and price > 0 else None

    # 5. Classify
    regime, confidence, details = classify_regime(
        price_7d_change=price_change_7d,
        volume_24h=volume_24h,
        volume_avg=volume_avg,
        rsi_14=rsi,
        atr_pct=atr_pct,
        price_history=prices[-20:] if prices else [],
    )

    # 6. Check previous regime
    prev_regime = "UNKNOWN"
    try:
        with open(REGIME_STATE_FILE) as f:
            prev_regime = json.load(f).get("regime", "UNKNOWN")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # 7. Save state
    result = {
        "regime": regime,
        "confidence": confidence,
        "prev_regime": prev_regime,
        "regime_changed": regime != prev_regime and prev_regime != "UNKNOWN",
        "details": details,
        "price": price,
        "volume_24h": volume_24h,
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


class RegimeClassifier:
    """Wrapper class for the regime classifier."""

    def __init__(self, token_address: str = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", chain: str = "base"):
        self.token_address = token_address
        self.chain = chain

    def classify(self) -> Dict[str, Any]:
        return classify_current_market(self.token_address, self.chain)


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    token = sys.argv[1] if len(sys.argv) > 1 else "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    chain = sys.argv[2] if len(sys.argv) > 2 else "base"
    result = classify_current_market(token, chain)
    print(json.dumps(result, indent=2))
