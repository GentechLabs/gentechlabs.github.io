#!/usr/bin/env python3
"""
DeFi Yield Rainbow — Live Data Generator
Computes rainbow band positions from live LP metrics.
Output: JSON consumed by the rainbow dashboard HTML.
"""

# ── wallet resolution (wired 2026-09-22) ────────────────────────────────────
# This file used to hardcode the operator's address. Fine for one person, catastrophic
# for a fleet: a second tenant running this script with their own config would still act
# on the FIRST tenant's wallet, and would do it silently. Resolve it instead - and prove
# it, because steward_identity.signer() refuses a key that does not match the resolved
# wallet, and asserts the tenant boundary before handing one back.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from steward_identity import wallet as _steward_wallet
import json
import os
import sys
import urllib.request
import time
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
CONFIG_FILE = "/root/.hermes/scripts/.lfj-aae-config.json"
POSITION_FILE = "/root/.hermes/scripts/.lfj-position-tracker.json"
OUTPUT_FILE = "/var/www/gentechlabs/yield-rainbow-data.json"

# ── Rainbow Bands ───────────────────────────────────────────────────────────
# Each band: name, emoji, color, efficiency range, description, farming advice
BANDS = [
    {
        "id": "euphoria",
        "name": "Euphoria",
        "emoji": "🔴",
        "color": "#e84142",
        "gradient": "linear-gradient(135deg, #e84142, #ff3366)",
        "efficiency_min": 90,
        "efficiency_max": 100,
        "apr_min": 1000,
        "description": "Maximum concentration. APR is unsustainable.",
        "advice": "⚠️ Time to take profits. Diversify into other pools or stablecoins.",
        "rainbow_position": 1  # top band
    },
    {
        "id": "peak_yield",
        "name": "Peak Yield",
        "emoji": "🟠",
        "color": "#f59e0b",
        "gradient": "linear-gradient(135deg, #f59e0b, #f97316)",
        "efficiency_min": 75,
        "efficiency_max": 90,
        "apr_min": 500,
        "description": "Sweet spot. Fees significantly outpace impermanent loss.",
        "advice": "✅ Hold strong. Compound rewards weekly. This is what we farm for.",
        "rainbow_position": 2
    },
    {
        "id": "harvest",
        "name": "Harvest Mode",
        "emoji": "🟡",
        "color": "#eab308",
        "gradient": "linear-gradient(135deg, #eab308, #facc15)",
        "efficiency_min": 60,
        "efficiency_max": 75,
        "apr_min": 200,
        "description": "Healthy farming. Fees are outpacing IL consistently.",
        "advice": "🌾 Keep farming. Consider increasing position size if conviction is high.",
        "rainbow_position": 3
    },
    {
        "id": "accumulation",
        "name": "Accumulation",
        "emoji": "🟢",
        "color": "#22c55e",
        "gradient": "linear-gradient(135deg, #22c55e, #16a34a)",
        "efficiency_min": 40,
        "efficiency_max": 60,
        "apr_min": 50,
        "description": "Smart money is quietly positioning. Fees starting to offset IL.",
        "advice": "🧠 DCA into position. Accumulate at these levels. Patience pays.",
        "rainbow_position": 4
    },
    {
        "id": "bleeding",
        "name": "Bleeding Edge",
        "emoji": "🔵",
        "color": "#3b82f6",
        "gradient": "linear-gradient(135deg, #3b82f6, #6366f1)",
        "efficiency_min": 20,
        "efficiency_max": 40,
        "apr_min": 10,
        "description": "Near range boundary. IL still outpaces fees.",
        "advice": "🩸 Micro-DCA only. Prepare to rebalance if price moves further.",
        "rainbow_position": 5
    },
    {
        "id": "panic",
        "name": "Panic Farm",
        "emoji": "🟣",
        "color": "#a855f7",
        "gradient": "linear-gradient(135deg, #a855f7, #7c3aed)",
        "efficiency_min": 0,
        "efficiency_max": 20,
        "apr_min": 0,
        "description": "Maximum fear. Everything is on fire. Historically: generational entry.",
        "advice": "🔥 Contrarian zone. Open new positions or widen ranges. Be greedy when others are fearful.",
        "rainbow_position": 6  # bottom band
    }
]

def load_config():
    """Load position config."""
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def load_position_state():
    """Load position tracker state."""
    try:
        with open(POSITION_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def fetch_avax_price():
    """Get AVAX/USD from DexScreener."""
    url = f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{POOL_ADDRESS}"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-Labs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        pair = data.get("pairs", [{}])[0] if data.get("pairs") else {}
        return {
            "price": float(pair.get("priceUsd", 0)),
            "change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
            "volume_24h": float(pair.get("volume", {}).get("h24", 0)),
            "tvl": float(pair.get("liquidity", {}).get("usd", 0)),
        }
    except Exception as e:
        # 2026-09-22: MUST be None, never a zero-filled dict. The old all-zero
        # return fed calc_efficiency -> 0.0 -> the bottom band, so a failed HTTP
        # call was published PUBLICLY (HTTP 200) as "Panic Farm / Open new
        # positions or widen ranges. Be greedy when others are fearful." A dead
        # feed is not a market signal.
        print(f"yield-rainbow: market feed unavailable: {e}", file=sys.stderr)
        return None

def calc_efficiency(price, low, high, shape="curve"):
    """Calculate LP efficiency — shape-aware."""
    if price < low or price > high:
        return 0.0
    pos = (price - low) / (high - low)
    if shape == "bid-ask":
        # Bid-Ask: max at edges, min at center
        return round(max(0, min(100, abs(pos - 0.5) * 2 * 100)), 1)
    elif shape == "spot":
        return 100.0
    else:  # curve
        return round(max(0, min(100, (1 - abs(pos - 0.5) * 2) * 100)), 1)

def calc_daily_fees(volume_24h, tvl, position_usd, fee_bps=5):
    """Estimate daily fees from pool volume and position size."""
    if tvl <= 0 or volume_24h <= 0:
        return 0.0
    return round((volume_24h * fee_bps / 10000) * (position_usd / tvl), 4)

def classify_band(efficiency, daily_fees, position_usd):
    """Classify current position into a rainbow band."""
    apr = (daily_fees * 365 / position_usd * 100) if position_usd > 0 else 0
    
    for band in BANDS:
        if band["efficiency_min"] <= efficiency < band["efficiency_max"]:
            if apr >= band["apr_min"]:
                return band, apr
    
    # Fallback: use efficiency only
    for band in BANDS:
        if band["efficiency_min"] <= efficiency < band["efficiency_max"]:
            return band, apr
    
    # Edge case: efficiency 100 exactly
    if efficiency >= 90:
        return BANDS[0], apr
    
    # Default to panic
    return BANDS[-1], apr

def build_history(config, position_state, current_efficiency):
    """Build simulated historical efficiency for the rainbow chart line."""
    # Use real data if available, otherwise generate a reasonable history
    history = position_state.get("efficiency_history", [])
    
    # If no history, create a 30-day simulated path
    if len(history) < 7:
        import random
        random.seed(int(time.time() / 86400))  # Same seed per day
        base = current_efficiency
        history = []
        for i in range(30):
            # Random walk around current efficiency
            noise = random.gauss(0, 8)
            val = max(0, min(100, base + noise + (i - 15) * 0.5))
            history.append(round(val, 1))
        # Ensure last value matches current
        history[-1] = current_efficiency
    
    return history[-30:]  # Last 30 days

def main():
    config = load_config()
    position_state = load_position_state()
    
    # Get live data
    market = fetch_avax_price()
    if market is None:
        # Refuse to compute a band from a dead feed. Carry forward the last
        # known good payload (flagged) rather than inventing a market signal.
        try:
            with open(OUTPUT_FILE) as _f:
                prev = json.load(_f)
        except Exception:
            prev = None
        if prev and prev.get("currentBand"):
            _m = prev.setdefault("meta", {})
            _m["feedStatus"] = "unavailable"
            _m["feedNote"] = ("Market feed failed on this run. Values shown are the "
                              "LAST KNOWN GOOD snapshot, not a fresh measurement.")
            with open(OUTPUT_FILE, "w") as _f:
                json.dump(prev, _f, indent=2)
            print("⚠️  market feed unavailable — re-published last known good "
                  f"({prev.get('lastUpdated')}); no band recomputed.")
            return 0
        print("❌ market feed unavailable and no prior payload to fall back on — "
              "nothing published.", file=sys.stderr)
        return 1
    _FEED_OK = True
    
    # Position data from config
    pos = config.get("position", {})
    range_info = pos.get("range", {})
    range_low = range_info.get("low", 6.04)
    range_high = range_info.get("high", 6.196)
    position_usd = pos.get("total_usd", 43.12)
    
    price = market["price"]
    if price <= 0:
        price = pos.get("entry_price", 6.30)
    
    shape = pos.get("shape", "curve")

    # ── CHAIN TRUTH FIRST (Jordan, Sep 3 2026) ──────────────────────────
    # The .lfj-aae-config + .lfj-position-tracker files are hand-maintained
    # and went stale (July 22 values looping into the dashboard). Live LP
    # read via discover_positions — the same reader the watchdogs and farm
    # report use. File values kept only as fallback.
    try:
        reader_dir = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking"
        if reader_dir not in sys.path:
            sys.path.insert(0, reader_dir)
        from discover_positions import discover_positions
        _dd = discover_positions(
            "avalanche", _steward_wallet())
        # Pick the pool we are ACTUALLY in -- never just the first error-free entry.
        # positions[0] is the Blackhole husk (positionUsd 0.0), so the old `next(...)` read the
        # empty remnant and the council reported "LP Position: FLAT — no open position" while our
        # funded LFJ position sat below it in the list. Select by VALUE.
        _ok = [x for x in _dd.get("positions", []) if "error" not in x]
        _p = max(_ok, key=lambda x: float(x.get("positionUsd") or 0.0)) if _ok else None
        if _p:
            range_low = _p.get("rangeLow", range_low)
            range_high = _p.get("rangeHigh", range_high)
            # A reported 0.0 means "cannot value", NOT "worth zero". `.get(key, fallback)`
            # returns the 0.0 because it IS a real value, so it silently clobbers the fallback
            # and the feed publishes a phantom-flat position. Only a POSITIVE read may overwrite.
            _pv = _p.get("positionUsd")
            if _pv and float(_pv) > 0:
                position_usd = float(_pv)
            shape = "curve"
            _lp = _p.get("livePriceUsd", 0)
            if _lp and _lp > 0:
                price = _lp
        else:
            # ── READ SUCCEEDED AND THERE IS NO POSITION (fixed Sep 30 2026) ───────────
            # Every owned NFT is an empty remnant, so `_ok` is empty and `_p` is None. The old
            # code fell straight through and KEPT the file's last-known values — so once the
            # position closed, this feed went on republishing it forever. The council then
            # reported "LP Position: $24.32 — OUT · 0% eff · Panic Farm" for a wallet that holds
            # none, and that $24.32 drove a dissent in the verdict. Measured: both of jordan's
            # NFT slots read "no position" / "all owned NFTs are empty remnants".
            # A CONFIRMED-EMPTY book is a FACT, not a gap, so publish it as empty. The
            # `except` branch below still keeps the file fallback for a FAILED read — unknown
            # is not the same as empty, and the two must never collapse into each other.
            position_usd = 0.0
            range_low = 0.0
            range_high = 0.0
    except Exception:
        pass  # keep file-based values
    
    # Calculate metrics
    efficiency = calc_efficiency(price, range_low, range_high, shape)
    daily_fees = calc_daily_fees(market["volume_24h"], market["tvl"], position_usd)
    band, apr = classify_band(efficiency, daily_fees, position_usd)
    
    # Build history
    history = build_history(config, position_state, efficiency)
    
    # Build rainbow data
    rainbow_data = {
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "pool": {
            "name": "AVAX/USDC",
            "chain": "Avalanche",
            "dex": "LFJ",
            "feeTier": "5bps",
            "poolAddress": POOL_ADDRESS
        },
        "position": {
            "currentPrice": price,
            "rangeLow": range_low,
            "rangeHigh": range_high,
            "rangeCenter": round((range_low + range_high) / 2, 4),
            "positionUsd": position_usd,
            "entryPrice": pos.get("entry_price", 6.30)
        },
        "metrics": {
            "efficiency": efficiency,
            "dailyFees": daily_fees,
            "weeklyFees": round(daily_fees * 7, 4),
            "monthlyFees": round(daily_fees * 30, 4),
            "annualizedApr": round(apr, 1),
            "volume24h": market["volume_24h"],
            "tvl": market["tvl"],
            "priceChange24h": market["change_24h"]
        },
        "currentBand": {
            "id": band["id"],
            "name": band["name"],
            "emoji": band["emoji"],
            "color": band["color"],
            "description": band["description"],
            "advice": band["advice"],
            "position": band["rainbow_position"]
        },
        "bands": BANDS,
        "history": history,
        "meta": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "bandsCount": len(BANDS),
            "dataSources": ["DexScreener", "LFJ Config"],
            "disclaimer": "Not financial advice. Rainbow charts are for visualization only."
        }
    }
    
    # Write output
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(rainbow_data, f, indent=2)
    
    print(f"✅ Yield Rainbow data updated: {band['emoji']} {band['name']} (efficiency: {efficiency}%, APR: {apr:.1f}%)")

if __name__ == "__main__":
    main()
