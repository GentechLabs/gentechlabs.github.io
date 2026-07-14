"""
Price History Tracker — periodic snapshots for trend analysis.

CheapShark has no history endpoint, so we build our own.
Saves snapshots to Gaming/deals/price-history.json.
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

HISTORY_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "Gaming", "deals", "price-history.json"
)
SNAPSHOT_INTERVAL = 3600  # 1 hour between snapshots per game


def _load_history() -> dict[str, Any]:
    """Load price history from disk."""
    if not os.path.exists(HISTORY_FILE):
        return {"games": {}, "snapshots": []}
    try:
        with open(HISTORY_FILE) as f:
            data = json.load(f)
            if "games" not in data:
                data["games"] = {}
            if "snapshots" not in data:
                data["snapshots"] = []
            return data
    except (json.JSONDecodeError, OSError):
        return {"games": {}, "snapshots": []}


def _save_history(data: dict[str, Any]) -> None:
    """Save price history to disk."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record_price(game_id: str, title: str, price: float, store: str, deal_id: str = "") -> bool:
    """
    Record a price observation for a game.
    Returns True if a new snapshot was recorded (not duplicate within interval).
    """
    data = _load_history()
    now = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Initialize game entry
    if game_id not in data["games"]:
        data["games"][game_id] = {
            "title": title,
            "observations": [],
            "lowest_price": price,
            "lowest_store": store,
            "lowest_date": now_iso,
        }

    game = data["games"][game_id]
    game["title"] = title  # update title if changed

    # Check if last snapshot is within interval (dedup)
    observations = game["observations"]
    if observations:
        last = observations[-1]
        last_time = last.get("timestamp", 0)
        if isinstance(last_time, str):
            # Parse ISO timestamp
            try:
                last_ts = datetime.fromisoformat(last_time.replace("Z", "+00:00")).timestamp()
            except ValueError:
                last_ts = 0
        else:
            last_ts = float(last_time)
        if now - last_ts < SNAPSHOT_INTERVAL:
            return False  # too soon, skip

    # Record observation
    observation = {
        "price": price,
        "store": store,
        "deal_id": deal_id,
        "timestamp": now_iso,
    }
    observations.append(observation)

    # Keep only last 500 observations per game (prevents unbounded growth)
    if len(observations) > 500:
        game["observations"] = observations[-500:]

    # Update all-time low
    if price < game["lowest_price"]:
        game["lowest_price"] = price
        game["lowest_store"] = store
        game["lowest_date"] = now_iso

    # Add to global snapshots list
    data["snapshots"].append({
        "game_id": game_id,
        "title": title,
        "price": price,
        "store": store,
        "timestamp": now_iso,
    })

    # Keep only last 2000 global snapshots
    if len(data["snapshots"]) > 2000:
        data["snapshots"] = data["snapshots"][-2000:]

    _save_history(data)
    return True


def get_price_trend(game_id: str, days: int = 30) -> dict[str, Any]:
    """
    Get price trend for a game over the last N days.
    Returns stats: min, max, avg, current, trend direction.
    """
    data = _load_history()
    game = data["games"].get(game_id)
    if not game:
        return {"error": "No history for this game"}

    cutoff = time.time() - (days * 86400)
    recent = []
    for obs in game["observations"]:
        ts = obs.get("timestamp", "")
        if isinstance(ts, str):
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except ValueError:
                continue
        else:
            t = float(ts)
        if t >= cutoff:
            recent.append(obs)

    if not recent:
        return {"error": "No observations in this period"}

    prices = [o["price"] for o in recent]
    first_price = prices[0]
    last_price = prices[-1]

    if first_price > 0:
        change_pct = ((last_price - first_price) / first_price) * 100
    else:
        change_pct = 0

    trend = "↓ dropping" if change_pct < -5 else "↑ rising" if change_pct > 5 else "→ stable"

    return {
        "title": game["title"],
        "observations": len(recent),
        "min": min(prices),
        "max": max(prices),
        "avg": round(sum(prices) / len(prices), 2),
        "current": last_price,
        "all_time_low": game["lowest_price"],
        "all_time_low_store": game["lowest_store"],
        "trend": trend,
        "change_pct": round(change_pct, 1),
        "period_days": days,
    }


def format_trend(trend: dict[str, Any]) -> str:
    """Format a price trend for Telegram display."""
    if "error" in trend:
        return f"❌ {trend['error']}"

    return (
        f"📈 {trend['title']} — Price Trend ({trend['period_days']}d)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Current: ${trend['current']:.2f}\n"
        f"📉 Low: ${trend['min']:.2f}  |  📊 High: ${trend['max']:.2f}\n"
        f"📊 Average: ${trend['avg']:.2f}\n"
        f"🏷️ All-time low: ${trend['all_time_low']:.2f} at {trend['all_time_low_store']}\n"
        f"{'📉' if trend['change_pct'] < 0 else '📈'} Trend: {trend['trend']} ({trend['change_pct']:+.1f}%)\n"
        f"🔍 Based on {trend['observations']} observations"
    )
