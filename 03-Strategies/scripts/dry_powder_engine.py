#!/usr/bin/env python3
"""Dry Powder Mode — Crash Detection & Decision Engine

Monitors market conditions and signals when to convert LP positions to stables.
Designed for Jordan's 12hr Amazon shifts — agent protects capital autonomously.

Usage:
    python3 dry-powder-engine.py              # Single poll cycle
    python3 dry-powder-engine.py --watch      # Continuous monitoring (every 5 min)
    python3 dry-powder-engine.py --status     # Show current state

Config:     ../../config/dry-powder-config.json
State:      ~/.hermes/state/dry-powder-state.json
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
CONFIG_PATH = CONFIG_DIR / "dry-powder-config.json"
STATE_DIR = Path(os.path.expanduser("~/.hermes/state"))
STATE_PATH = STATE_DIR / "dry-powder-state.json"

# Default config (used if config file doesn't exist)
DEFAULT_CONFIG = {
    "mode": "advisory",
    "crash_threshold": 50,
    "recovery_threshold": 60,
    "min_withdraw_usd": 50,
    "max_withdraw_pct": 100,
    "stable_target": "USDC",
    "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
    "chain": "avalanche",
    "notification_channel": "telegram_hq",
    "poll_interval_seconds": 300,
    "watch_poll_interval_seconds": 60,
    "watchlist": [
        {"symbol": "AVAX",  "coingecko_id": "avalanche-2",  "weight": 1.0},
        {"symbol": "BTC",   "coingecko_id": "bitcoin",      "weight": 0.7},
        {"symbol": "SOL",   "coingecko_id": "solana",       "weight": 0.3},
    ],
    "price_drop_5min_threshold": -3.0,
    "price_drop_1h_threshold": -8.0,
    "volatility_spike_threshold": 2.0,
    "rsi_recovery_threshold": 35,
}

# ── Helpers ────────────────────────────────────────────────────────────────────


def load_config():
    """Load config file, creating with defaults if missing."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
            # Merge with defaults so new fields get filled in
            merged = dict(DEFAULT_CONFIG)
            merged.update(cfg)
            return merged
    # Create config dir if needed
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    return dict(DEFAULT_CONFIG)


def load_state():
    """Load runtime state, returning defaults on missing/corrupt file."""
    defaults = {
        "version": 1,
        "mode": "advisory",
        "status": "monitoring",
        "last_signal": "SAFE",
        "last_signal_score": 0,
        "last_checked": None,
        "triggers_today": 0,
        "last_trigger_date": None,
        "total_withdrawn_usd": 0,
        "total_redeployed_usd": 0,
        "position_before_crash": None,
        "current_stable_holdings": 0,
        "circuit_breaker_count": 0,
        "circuit_breaker_date": None,
    }
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH) as f:
                data = json.load(f)
                merged = dict(defaults)
                merged.update(data)
                return merged
        except (json.JSONDecodeError, OSError):
            pass
    return dict(defaults)


def save_state(state):
    """Atomic write of state file."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    tmp.replace(STATE_PATH)


def fetch_price(symbol: str, coingecko_id: str) -> dict:
    """Fetch current price + 24h change from BlockRun Price (free tier).

    Returns dict with {symbol, price, change_24h, source} or raises on failure.
    """
    # Primary: BlockRun Price API (crypto, free)
    try:
        url = f"https://api.blockrun.ai/v1/price?category=crypto&symbol={symbol}-USD"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, dict) and "price" in data:
                return {
                    "symbol": symbol,
                    "price": float(data["price"]),
                    "change_24h": float(data.get("change_24h_pct", 0)),
                    "source": "blockrun",
                }
    except Exception:
        pass

    # Fallback: DexScreener via BlockRun DEX (free)
    try:
        url = f"https://api.blockrun.ai/v1/dex/search?query={symbol}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            pairs = data.get("pairs", [])
            if pairs:
                p = pairs[0]
                return {
                    "symbol": symbol,
                    "price": float(p.get("priceUsd", 0)),
                    "change_24h": float(p.get("priceChange", {}).get("h24", 0)),
                    "source": "dexscreener",
                }
    except Exception:
        pass

    # Fallback: CoinGecko (free, no key)
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd&include_24hr_change=true"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            coin = data.get(coingecko_id, {})
            if "usd" in coin:
                return {
                    "symbol": symbol,
                    "price": float(coin["usd"]),
                    "change_24h": float(coin.get("usd_24h_change", 0)),
                    "source": "coingecko",
                }
    except Exception:
        pass

    raise RuntimeError(f"Could not fetch price for {symbol}")


def calculate_volatility(prices: list[float]) -> float:
    """Simple volatility: coefficient of variation (std/mean).
    Higher = more volatile. Used to detect spikes vs baseline.
    """
    if len(prices) < 3:
        return 0.0
    mean = sum(prices) / len(prices)
    if mean == 0:
        return 0.0
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    return (variance ** 0.5) / mean


# ── Scoring ─────────────────────────────────────────────────────────────────────


class CrashDetector:
    """Crash detection engine. Stateless — pass prices per call."""

    def __init__(self, config: dict):
        self.cfg = config

    def score_crash(self, price_info: dict, volatility: float,
                    price_history_5min: list[float],
                    price_history_1h: list[float]) -> dict:
        """Calculate weighted crash score (0-100) and signal.

        Returns {
            score: int 0-100,
            signal: "SAFE" | "WATCH" | "CRASH",
            factors: [...]  # individual factor scores
        }
        """
        factors = []
        total = 0

        # Factor 1: Price drop 5-minute window (weight: 30)
        if len(price_history_5min) >= 2:
            pct_5min = ((price_history_5min[-1] - price_history_5min[0])
                        / price_history_5min[0] * 100)
            if pct_5min <= self.cfg["price_drop_5min_threshold"]:
                severity = min(30, int(abs(pct_5min) * 3))
                total += severity
                factors.append({
                    "factor": "price_drop_5min",
                    "value": round(pct_5min, 2),
                    "score": severity,
                    "max": 30,
                })

        # Factor 2: Price drop 24h change (weight: 25)
        change_24h = price_info.get("change_24h", 0)
        if change_24h <= self.cfg["price_drop_1h_threshold"]:
            severity = min(25, int(abs(change_24h) * 2))
            total += severity
            factors.append({
                "factor": "price_drop_24h",
                "value": round(change_24h, 2),
                "score": severity,
                "max": 25,
            })

        # Factor 3: Volatility spike (weight: 20)
        if volatility > 0:
            baseline_vol = 0.02  # Normal crypto vol ~2%
            spike_ratio = volatility / baseline_vol
            if spike_ratio >= self.cfg["volatility_spike_threshold"]:
                severity = min(20, int((spike_ratio - 1) * 10))
                total += severity
                factors.append({
                    "factor": "volatility_spike",
                    "value": round(volatility, 4),
                    "ratio": round(spike_ratio, 2),
                    "score": severity,
                    "max": 20,
                })

        # Factor 4: Consecutive negative candles (weight: 15)
        if len(price_history_5min) >= 3:
            candles = [(price_history_5min[i+1] - price_history_5min[i])
                       for i in range(len(price_history_5min) - 1)]
            neg_streak = 0
            for c in reversed(candles):
                if c < 0:
                    neg_streak += 1
                else:
                    break
            if neg_streak >= 3:
                severity = min(15, neg_streak * 5)
                total += severity
                factors.append({
                    "factor": "negative_candle_streak",
                    "value": neg_streak,
                    "score": severity,
                    "max": 15,
                })

        # Factor 5: Magnitude of drop (weight: 10)
        if change_24h < -5:
            severity = min(10, int(abs(change_24h)))
            total += severity
            factors.append({
                "factor": "drop_magnitude",
                "value": round(change_24h, 2),
                "score": severity,
                "max": 10,
            })

        # Cap at 100
        total = min(100, total)

        # Determine signal
        if total >= self.cfg["crash_threshold"]:
            signal = "CRASH"
        elif total >= self.cfg["crash_threshold"] * 0.5:
            signal = "WATCH"
        else:
            signal = "SAFE"

        return {
            "score": total,
            "signal": signal,
            "factors": factors,
        }

    def score_recovery(self, price_info: dict,
                       current_rsi: float) -> dict:
        """Calculate recovery score (0-100).

        Returns {
            score: int 0-100,
            signal: "STILL_CRASHED" | "RECOVERING" | "SAFE_TO_REDEPLOY",
            factors: [...]
        }
        """
        factors = []
        total = 0

        # Factor 1: RSI recovery (weight: 35)
        if current_rsi >= self.cfg["rsi_recovery_threshold"]:
            severity = min(35, int(current_rsi - 20) * 2)
            total += severity
            factors.append({
                "factor": "rsi_recovery",
                "rsi": current_rsi,
                "score": severity,
                "max": 35,
            })

        # Factor 2: 24h change stabilizing (weight: 25)
        change_24h = price_info.get("change_24h", 0)
        if -2 <= change_24h <= 2:
            total += 25
            factors.append({
                "factor": "price_stabilized",
                "value": round(change_24h, 2),
                "score": 25,
                "max": 25,
            })
        elif 2 < change_24h <= 5:
            total += 15
            factors.append({
                "factor": "price_mildly_up",
                "value": round(change_24h, 2),
                "score": 15,
                "max": 25,
            })

        # Factor 3: Not in freefall (weight: 20)
        if change_24h > -5:
            total += 20
            factors.append({
                "factor": "no_freefall",
                "value": round(change_24h, 2),
                "score": 20,
                "max": 20,
            })

        # Factor 4: Price above recent low (weight: 20)
        # If price is > 5% above the 24h low, we're recovering
        low_24h = price_info.get("low_24h", price_info["price"] * 0.95)
        if price_info["price"] > low_24h * 1.05:
            severity = min(20, int((price_info["price"] / low_24h - 1) * 50))
            total += severity
            factors.append({
                "factor": "above_low",
                "price_vs_low_pct": round(
                    (price_info["price"] / low_24h - 1) * 100, 2
                ),
                "score": severity,
                "max": 20,
            })

        total = min(100, total)

        if total >= self.cfg["recovery_threshold"]:
            signal = "SAFE_TO_REDEPLOY"
        elif total >= self.cfg["recovery_threshold"] * 0.5:
            signal = "RECOVERING"
        else:
            signal = "STILL_CRASHED"

        return {"score": total, "signal": signal, "factors": factors}


# ── Monitoring Loop ─────────────────────────────────────────────────────────────


def poll(config: dict, state: dict) -> dict:
    """Run one poll cycle. Returns updated state."""
    print(f"🔍 Dry Powder — Poll at {datetime.now():%H:%M:%S}")
    print(f"   Mode: {config['mode']} | Status: {state['status']}")

    # Fetch prices for watchlist
    prices = {}
    errors = []
    for coin in config["watchlist"]:
        try:
            info = fetch_price(coin["symbol"], coin["coingecko_id"])
            prices[coin["symbol"]] = info
            print(f"   {coin['symbol']}: ${info['price']:.2f} "
                  f"({info['change_24h']:+.2f}%) [{info['source']}]")
        except RuntimeError as e:
            errors.append(str(e))
            print(f"   ⚠ {coin['symbol']}: {e}")

    if not prices:
        print("   ❌ No prices fetched — skipping cycle")
        state["last_checked"] = datetime.now(tz=timezone.utc).isoformat()
        save_state(state)
        return state

    # Calculate volatility from primary asset history
    primary = config["watchlist"][0]
    sym = primary["symbol"]
    price_info = prices.get(sym, {})
    if not price_info:
        print("   ⚠ Primary asset price unavailable")
        state["last_checked"] = datetime.now(tz=timezone.utc).isoformat()
        save_state(state)
        return state

    # Use basic volatility estimate from 24h change magnitude
    vol = abs(price_info.get("change_24h", 0)) / 100
    if vol < 0.01:
        vol = 0.02  # noise floor

    # Simulate 5-min price history from 24h change (single poll — no cache yet)
    # In production, this would read from a rolling price cache
    current_price = price_info["price"]
    simulated_5min = [current_price * (1 - price_info.get("change_24h", 0) / 100
                                       * 0.01),
                      current_price]
    simulated_1h = [current_price * (1 - price_info.get("change_24h", 0) / 100
                                     * 0.02),
                    current_price]

    detector = CrashDetector(config)

    # Crash scoring
    crash = detector.score_crash(price_info, vol, simulated_5min, simulated_1h)
    print(f"\n   📊 Crash Score: {crash['score']}/100 → {crash['signal']}")
    for f in crash["factors"]:
        print(f"      • {f['factor']}: {f.get('value', '')} = {f['score']}pts")

    # If crashed or watching, also calculate recovery
    recovery = None
    if state.get("status") in ("crashed", "withdrawn"):
        # Simulate RSI from 24h change (rough estimate)
        rsi = 50 + (price_info.get("change_24h", 0) * 1.5)
        rsi = max(0, min(100, rsi))
        recovery = detector.score_recovery(price_info, rsi)
        print(f"   📈 Recovery Score: {recovery['score']}/100 → "
              f"{recovery['signal']} (est. RSI: {rsi:.0f})")

    # Update state
    state["last_signal"] = crash["signal"]
    state["last_signal_score"] = crash["score"]
    state["last_checked"] = datetime.now(tz=timezone.utc).isoformat()

    today_str = datetime.now().strftime("%Y-%m-%d")
    if state.get("last_trigger_date") != today_str:
        state["triggers_today"] = 0
        state["last_trigger_date"] = today_str

    # Handle CRASH signal
    if crash["signal"] == "CRASH":
        state["triggers_today"] += 1
        state["circuit_breaker_count"] += 1
        state["circuit_breaker_date"] = today_str

        # Circuit breaker: max 5 triggers/day
        if state["circuit_breaker_count"] >= 5:
            print("\n   ⛔ Circuit breaker engaged! Max 5 triggers/day.")
            print("   Auto-disabled until reset.")
            state["status"] = "circuit_breaker"
            save_state(state)
            return state

        print(f"\n   🚨 CRASH DETECTED! Trigger #{state['triggers_today']} today.")

        if config["mode"] == "auto":
            print("   🔄 AUTO MODE — Would execute withdrawal")
            # TODO: Phase 2 — LP withdrawal logic
            state["status"] = "withdrawn"
        else:
            print("   📋 ADVISORY MODE — Would send Telegram recommendation")
            print("     '🚨 Crash detected: withdraw AVAX/USDC LP → USDC?'")
            state["status"] = "crash_advisory"

    elif crash["signal"] == "WATCH":
        state["status"] = "watching"
    else:
        # Only go back to monitoring if not in withdrawn/advisory state
        if state["status"] in ("monitoring", "watching"):
            state["status"] = "monitoring"

    # Handle recovery
    if recovery and recovery["signal"] == "SAFE_TO_REDEPLOY":
        print("\n   ✅ SAFE TO REDEPLOY — Conditions normalized")
        if config["mode"] == "auto":
            print("   🔄 AUTO MODE — Would execute redeployment")
            # TODO: Phase 5 — redeployment logic
            state["status"] = "redeployed"
        else:
            print("   📋 ADVISORY MODE — Would send Telegram recommendation")
            print("     '✅ Market recovered: redeploy USDC → LP?'")

    save_state(state)
    return state


def show_status(config, state):
    """Print current state as a readable report."""
    print("=" * 50)
    print("  DRY POWDER MODE — Status Report")
    print("=" * 50)
    print(f"  Mode:        {config['mode']}")
    print(f"  Status:      {state['status']}")
    print(f"  Last Signal: {state['last_signal']} ({state['last_signal_score']}/100)")
    print(f"  Last Check:  {state['last_checked'] or 'never'}")
    print(f"  Triggers Today: {state['triggers_today']}")
    print(f"  CB Counter:  {state.get('circuit_breaker_count', 0)}")
    print(f"  Withdrawn:   ${state.get('total_withdrawn_usd', 0)}")
    print(f"  Redeployed:  ${state.get('total_redeployed_usd', 0)}")
    print(f"  Stables:     ${state.get('current_stable_holdings', 0)}")
    print()
    print("  Pool:        " + config["pool_address"][:20] + "..." + config["pool_address"][-6:])
    print("  Chain:       " + config["chain"])
    print("  Threshold:   crash >=" + str(config["crash_threshold"]) +
          " | recovery >=" + str(config["recovery_threshold"]))
    print("=" * 50)


# ── Main ────────────────────────────────────────────────────────────────────────


def main():
    config = load_config()
    state = load_state()

    if "--status" in sys.argv:
        show_status(config, state)
        return 0

    if "--watch" in sys.argv:
        interval = (config["watch_poll_interval_seconds"]
                    if state.get("status") == "watching"
                    else config["poll_interval_seconds"])
        print(f"📡 Dry Powder Watch — polling every {interval}s (Ctrl+C to stop)")
        try:
            while True:
                state = poll(config, state)
                # Dynamic interval: poll faster when watching
                if state.get("status") == "watching":
                    interval = config["watch_poll_interval_seconds"]
                else:
                    interval = config["poll_interval_seconds"]
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 Watch stopped")
        return 0

    # Single poll
    state = poll(config, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
