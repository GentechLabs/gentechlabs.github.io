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

STATE_DIR = "/root/.hermes/scripts"  # absolute — expanduser() broke under profile HOME (audit Aug 29)
REGIME_STATE_FILE = os.path.join(STATE_DIR, ".aae-regime-state.json")
# ── ONE FILE, TWO WRITERS, TWO ASSETS (fixed 2026-09-26) ──────────────────────────────────
# The BTC path below wrote the SAME file as the AVAX path. Nothing was "wrong" locally — the
# series-split fix gave each asset its own HISTORY, but both classification entry points still
# ended at one shared STATE file. The consequence was measured live, in full:
#     one regime-watch.sh tick
#       step 1  regime_classifier.py <LFJ pool>  -> AVAX  -> BULL_TRENDING  (price 10.8)
#       step 2  aae-hybrid-signal.py             -> BTC   -> RANGE_BOUND    (price 84132)
#     ...so whoever wrote LAST decided the file. BTC writes last, every tick, forever.
# WHY THAT IS EXPENSIVE: shape_for(BULL_TRENDING) = BID_ASK (45 bins) and
# shape_for(RANGE_BOUND) = CURVE (25 bins). A consumer cannot tell a stable regime from one
# that flipped seconds ago, and `shape_mismatch` bypasses the cooldown by design — so each
# flip commissioned a full withdraw + rebuild of the book:
#     10:15  25 bins curve -> SHAPE REBUILD -> 45 bins bid-ask
#     10:48  45 bins -> back to 25 bins curve   (the bid-ask lasted 33 minutes)
# The treasury's own LFJ book was being shaped by BTC, and the churn was billed to us.
# Fix: BTC gets its OWN state file. The AVAX/pool file keeps the original path, because the
# treasury money paths (steward_rebalance, lfj_recenter, challenger, steward-council,
# steward_state, arb_log) all point there and every one of them is positioning an AVAX pool.
# This changes NO caller — it makes the shared file's single writer match its readers.
BTC_REGIME_STATE_FILE = os.path.join(STATE_DIR, ".aae-btc-regime-state.json")
# SERIES-SPLIT FIX (Sep 4, 2026): BTC and AVAX used to share ONE history file.
# Mixed series ($81k next to $7.49) produced ATR 1323% → false HIGH_VOLATILITY
# → wrong LP shape (BID_ASK). Each asset now gets its own series file. The old
# mixed file is legacy AVAX data (its AVAX-era entries predate the BTC cron).
PRICE_HISTORY_FILE = os.path.join(STATE_DIR, ".aae-price-history.json")      # AVAX (legacy)
BTC_HISTORY_FILE = os.path.join(STATE_DIR, ".aae-btc-price-history.json")    # BTC (market leader)


def _history_file_for(series: str) -> str:
    return BTC_HISTORY_FILE if series == "btc" else PRICE_HISTORY_FILE

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


def fetch_btc_data() -> Optional[Dict]:
    """Fetch BTC price/volume — CoinGecko primary, CMC fallback (Sep 4, 2026:
    CoinGecko 429s left the regime UNKNOWN on random ticks; CMC key lives in
    /root/.hermes/scripts/cmc_config.json and is already used by the buylist)."""
    url = ("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
           "?vs_currency=usd&days=30&interval=daily")
    data = fetch_json(url)
    if not data or "prices" not in data or not data["prices"]:
        data = None
    if data:
        prices = data["prices"]
        # CoinGecko returns [[ts, price], ...] oldest first
        price = prices[-1][1]
        # 7d change from 7 days ago
        price_7d_ago = prices[-8][1] if len(prices) >= 8 else prices[0][1]
        price_change_7d = (price - price_7d_ago) / price_7d_ago if price_7d_ago else None
        # 24h change from 1 day ago (daily interval -> last two points)
        price_24h_ago = prices[-2][1] if len(prices) >= 2 else price
        price_change_24h = (price - price_24h_ago) / price_24h_ago if price_24h_ago else 0
        # Volume proxy: use total_volumes series if present
        volume_24h = 0.0
        if "total_volumes" in data and data["total_volumes"]:
            volume_24h = float(data["total_volumes"][-1][1])
        return {
            "price_usd": price,
            "volume_24h": volume_24h,
            "price_change_24h": price_change_24h,
            "price_change_7d": price_change_7d,
            "source": "coingecko-btc",
        }
    # ── CMC fallback (live quote; 24h/7d changes from the quote itself) ──
    try:
        key = ""
        try:
            with open(os.path.join(STATE_DIR, "cmc_config.json")) as f:
                key = json.load(f).get("coinmarketcap_api_key", "")
        except Exception:
            key = os.environ.get("CMC_API_KEY", "")
        if not key:
            return None
        req = urllib.request.Request(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id=1&convert=USD",
            headers={"X-CMC_PRO_API_KEY": key, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            q = json.load(r)["data"]["1"]["quote"]["USD"]
        return {
            "price_usd": float(q["price"]),
            "volume_24h": float(q.get("volume_24h") or 0),
            "price_change_24h": float(q.get("percent_change_24h") or 0) / 100,
            "price_change_7d": float(q.get("percent_change_7d") or 0) / 100,
            "source": "cmc-btc-fallback",
        }
    except Exception:
        return None


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

def load_price_history(series: str = "avax") -> List[Dict]:
    """Load price history from state file (per-series: 'avax' or 'btc')."""
    try:
        with open(_history_file_for(series)) as f:
            data = json.load(f)
            return data.get("history", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_price_history(history: List[Dict], series: str = "avax") -> None:
    """Save price history to state file (per-series: 'avax' or 'btc')."""
    path = _history_file_for(series)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Trim to last N days
    cutoff = time.time() - (PRICE_HISTORY_DAYS * 86400)
    history = [h for h in history if h.get("timestamp", 0) > cutoff]
    with open(path, "w") as f:
        json.dump({"history": history, "last_updated": datetime.now(timezone.utc).isoformat()}, f, indent=2)


def record_price(price: float, volume_24h: float, timestamp: Optional[float] = None,
                 series: str = "avax"):
    """Record a price data point (per-series: 'avax' or 'btc')."""
    history = load_price_history(series)
    history.append({
        "timestamp": timestamp or time.time(),
        "price": price,
        "volume_24h": volume_24h,
    })
    save_price_history(history, series)


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

    # ── MISSING DATA IS NOT A NEUTRAL READING ───────────────────────────────
    # This block used to be "Defaults if data missing" and it manufactured a bland, confident
    # market out of nothing:
    #     momentum -> 0      (reads as "no trend")
    #     vol      -> 1.0    (reads as "normal volume")
    #     rsi      -> 50     (reads as "neutral")
    #     atr      -> 0.05   (reads as "high volatility")
    # A live run then reported RANGE_BOUND at 0.65 confidence with reason "Momentum 0.0% (range)"
    # while price_7d_change was NULL and the asset had moved +8.95% in 24h with RSI 71.6. The
    # classifier did not measure a range; it measured its own default. And it fired regime_changed
    # on it. So: track what was actually OBSERVED, and never let a placeholder masquerade as data.
    missing = []
    if price_7d_change is None:
        missing.append("momentum_7d")
    if rsi_14 is None:
        missing.append("rsi_14")
    if atr_pct is None:
        missing.append("atr_pct")
    if not (volume_avg > 0):
        missing.append("volume_avg")

    # Momentum is the load-bearing input. Without it there is no regime — only a guess.
    momentum = price_7d_change
    vol_ratio = (volume_24h / volume_avg) if volume_avg > 0 else None
    rsi = rsi_14 if rsi_14 is not None else 50
    atr_p = atr_pct if atr_pct is not None else 0.05

    details["data_quality"] = "complete" if not missing else f"INCOMPLETE — missing: {','.join(missing)}"
    details["observed"] = {
        "momentum_7d": (round(momentum, 4) if momentum is not None else None),
        "volume_ratio": (round(vol_ratio, 2) if vol_ratio is not None else None),
        "rsi_14": (round(rsi, 1) if rsi_14 is not None else None),
        "atr_pct": (round(atr_p, 4) if atr_pct is not None else None),
    }
    # kept for backward compatibility with consumers that read these keys, but they are now honest
    details["momentum_7d"] = (round(momentum, 4) if momentum is not None else None)
    details["volume_ratio"] = (round(vol_ratio, 2) if vol_ratio is not None else None)
    details["rsi_14"] = round(rsi, 1)
    details["atr_pct"] = round(atr_p, 4)

    # ── HARD STOP: no momentum, no regime ───────────────────────────────────
    # Refusing to classify is the correct answer. UNKNOWN is a real verdict and the safest one
    # available, because every downstream consumer maps UNKNOWN to a conservative posture while it
    # maps RANGE_BOUND to the MOST aggressive LP allocation in the table (lp: 40). A fabricated
    # RANGE_BOUND is therefore worse than an honest UNKNOWN by a wide margin.
    if momentum is None:
        details["reason"] = (
            "momentum UNAVAILABLE (7d price change missing) — refusing to classify rather than "
            "defaulting to zero. A missing input is not a flat market."
        )
        if rsi_14 is not None:
            details["reason"] += f" RSI {rsi:.0f} was readable."
        return "UNKNOWN", 0.0, details

    # vol_ratio missing degrades confidence but does not block classification
    if vol_ratio is None:
        vol_ratio = 1.0
        details["volume_ratio"] = None

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

def fetch_pool_7d_change() -> Optional[float]:
    """7-day price change from a source that actually HAS a 7-day window.

    WHY THIS EXISTS (2026-09-22): the pipeline read 7d momentum from DexScreener's
    `pair.priceChange.h7d`. That field does not exist. DexScreener returns exactly
    ['m5','h1','h6','h24'] for BOTH our LFJ pool and the Blackhole pool — verified
    live — so `price_change_7d` was ALWAYS None. Momentum is the load-bearing input,
    so classify_regime() correctly refused on every tick and the regime was
    PERMANENTLY UNKNOWN. Downstream, `REGIME_SHAPE.get(unknown, "CURVE")` silently
    returned CURVE forever, and the up/down tilt silently returned its neutral
    fallback: a dead rail that looked calm rather than broken.

    The refusal was right; the starvation was the bug. Momentum must come from a
    source with real 7-day history. AVAX is the pool's base asset, so we read AVAX
    (not BTC): CoinGecko daily closes, then the same (prices[-1] - prices[-8]) / prices[-8]
    the BTC path already uses.

    ── IT STARVED AGAIN, AND THE FIX IS TO SHARE THE RESILIENT READER (fixed 2026-09-26) ───────
    This function kept its OWN single-source CoinGecko call, so it re-introduced exactly the
    fragility the note above was written about. Measured live at 22:05: the regime flipped to
    **UNKNOWN** with `"reason": "momentum UNAVAILABLE (7d price change missing) — refusing to
    classify"`, because that one call was rate-limited — while three OTHER sources were answering
    200 and the treasury's own `volatility_tracker.price_series()` was returning **721 closes**
    happily, cached and multi-source.

    So the answer was already on the box, in a reader that had just been hardened for precisely
    this failure. **A second implementation of one read is not redundancy — it is a second place
    to break.** This now asks `volatility_tracker.price_series()` FIRST (cached, four sources, and
    the same numbers the shape decision uses), and only falls back to its own fetch if that module
    is unavailable. One read, one source of truth, one cache.
    """
    # 1. THE SHARED RESILIENT READER — same data the shape layer uses, so the two can never
    #    disagree about which direction AVAX moved.
    try:
        import volatility_tracker as _VT
        closes = _VT.price_series(30)
        if closes and len(closes) >= 8:
            then_p, now_p = float(closes[-8]), float(closes[-1])
            if then_p > 0:
                return (now_p - then_p) / then_p
    except Exception:
        pass                      # fall through to the direct read below rather than give up

    # 2. DIRECT FALLBACK, kept only for the case where the shared module cannot be imported.
    url = ("https://api.coingecko.com/api/v3/coins/avalanche-2/market_chart"
           "?vs_currency=usd&days=30&interval=daily")
    data = fetch_json(url)
    prices = (data or {}).get("prices") or []
    if len(prices) < 8:
        return None
    try:
        now_p, then_p = float(prices[-1][1]), float(prices[-8][1])
        if then_p <= 0:
            return None
        return (now_p - then_p) / then_p
    except (TypeError, ValueError, IndexError):
        return None


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
    momentum_source = "dexscreener-h7d"
    # DexScreener does not publish h7d (verified live: only m5/h1/h6/h24), so this is
    # effectively always the fallback. Kept in that order so the moment they DO ship a
    # pool-level 7d figure we prefer it — it is the pool's own number, not the asset's.
    if price_change_7d is None:
        price_change_7d = fetch_pool_7d_change()
        momentum_source = "coingecko-avax-7d" if price_change_7d is not None else "UNAVAILABLE"

    # 2. Record price in history
    record_price(price, volume_24h, series="avax")

    # 3. Load price history for indicators
    raw_history = load_price_history("avax")
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
        "momentum_source": momentum_source,
    }

    os.makedirs(os.path.dirname(REGIME_STATE_FILE), exist_ok=True)
    with open(REGIME_STATE_FILE, "w") as f:
        json.dump(result, f, indent=2)

    return result


def run_btc_classification() -> Dict[str, Any]:
    """Run regime classification on BTC (the market leader) instead of the AVAX pool.

    In a BTC-led bull market the regime label should read BTC, not a single
    AVAX pool. This is the entry point the cron uses (Jordan, Aug 19 2026).
    """
    btc = fetch_btc_data()
    if not btc:
        return {"error": "Failed to fetch BTC data", "regime": "UNKNOWN", "confidence": 0}

    price = btc["price_usd"]
    volume_24h = btc["volume_24h"]
    price_change_24h = btc["price_change_24h"]
    price_change_7d = btc.get("price_change_7d")

    # Record price in history (BTC series — SEPARATE from AVAX, series-split fix Sep 4 2026)
    record_price(price, volume_24h, series="btc")

    raw_history = load_price_history("btc")
    prices = [h["price"] for h in raw_history]

    volumes = [h["volume_24h"] for h in raw_history[-7:]] if len(raw_history) >= 7 else [volume_24h]
    volume_avg = sum(volumes) / len(volumes) if volumes else volume_24h

    rsi = compute_rsi(prices) if len(prices) >= 15 else None
    atr = compute_atr(prices, prices, prices) if len(prices) >= 15 else None
    atr_pct = atr / price if atr and price > 0 else None

    regime, confidence, details = classify_regime(
        price_7d_change=price_change_7d,
        volume_24h=volume_24h,
        volume_avg=volume_avg,
        rsi_14=rsi,
        atr_pct=atr_pct,
        price_history=prices[-20:] if prices else [],
    )

    prev_regime = "UNKNOWN"
    try:
        # reads BTC's OWN file now — reading the AVAX state here made the two assets' change
        # flags bleed into each other (see the one-file-two-writers note at the top).
        with open(BTC_REGIME_STATE_FILE) as f:
            state = json.load(f)
            prev_regime = state.get("regime", "UNKNOWN")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

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
        "source": "coingecko-btc",
    }

    os.makedirs(os.path.dirname(BTC_REGIME_STATE_FILE), exist_ok=True)
    with open(BTC_REGIME_STATE_FILE, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ── CLI Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    pool = sys.argv[1] if len(sys.argv) > 1 else "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
    result = run_classification(pool)
    print(json.dumps(result, indent=2))
