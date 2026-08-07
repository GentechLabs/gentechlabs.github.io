"""GenTech Games API — deal search, price-watch, release radar, preorder advisor.

Wires the CheapShark engine (10-Labs/deal-tracker/deal_tracker.py) into the
live deal-tracker FastAPI app as real, data-backed endpoints.
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

# Make the CheapShark engine importable from its sibling 10-Labs/deal-tracker dir.
_ENGINE_DIR = "/root/vaults/gentech/10-Labs/deal-tracker"
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from deal_tracker import CheapSharkClient  # noqa: E402

# --- price-watch in-memory store (per-process; production should use Redis/DB) ---
WATCH_FILE = os.environ.get(
    "PRICE_WATCH_FILE", "/root/vaults/gentech/10-Labs/deal-tracker-api/data/price_watch.json"
)

# Preorder-advisor signals (curated; extend as games are evaluated).
# Each entry: known titles keyed by lowercase, with launch + verdict.
PREORDER_HINTS = {}


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_watches():
    try:
        with open(WATCH_FILE) as f:
            return json.load(f).get("watches", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_watches(watches):
    os.makedirs(os.path.dirname(WATCH_FILE), exist_ok=True)
    with open(WATCH_FILE, "w") as f:
        json.dump({"watches": watches, "updated": _now_iso()}, f, indent=2)


def search_deals(title: str, upper_price: float = 9999, limit: int = 10) -> dict:
    client = CheapSharkClient()
    results = client.search_deals(title, upper_price=upper_price)
    deals = []
    for r in results[:limit]:
        deals.append(
            {
                "title": r.title,
                "sale_price": r.sale_price,
                "normal_price": r.normal_price,
                "savings": r.savings,
                "store": r.store_name,
                "steam_appid": r.steam_appid,
                "deal_id": r.deal_id,
            }
        )
    return {"query": title, "count": len(deals), "deals": deals}


def add_price_watch(title: str, target_price: float, max_price: float = 9999) -> dict:
    watches = _load_watches()
    # Dedupe by normalized title.
    key = title.strip().lower()
    for w in watches:
        if w["title"].strip().lower() == key:
            w["target_price"] = target_price
            w["max_price"] = max_price
            w["updated"] = _now_iso()
            _save_watches(watches)
            return {"status": "updated", "watch": w}

    watch = {
        "id": f"pw_{int(time.time())}",
        "title": title,
        "target_price": target_price,
        "max_price": max_price,
        "created": _now_iso(),
        "status": "tracking",
    }
    watches.append(watch)
    _save_watches(watches)
    return {"status": "created", "watch": watch}


def check_price_watches() -> dict:
    """Scan all watched titles for a deal at/below target price."""
    watches = _load_watches()
    if not watches:
        return {"count": 0, "watches": [], "alerts": []}

    client = CheapSharkClient()
    alerts = []
    for w in watches:
        try:
            deals = client.search_deals(w["title"], upper_price=w["max_price"], )
        except Exception:
            continue
        if not deals:
            continue
        best = deals[0]  # sorted by savings desc
        hit = best.sale_price <= w["target_price"]
        alerts.append(
            {
                "watch_id": w["id"],
                "title": w["title"],
                "current_best": best.sale_price,
                "target_price": w["target_price"],
                "store": best.store_name,
                "deal_url": f"https://www.cheapshark.com/redirect?dealID={best.deal_id}" if best.deal_id else None,
                "alert": hit,
            }
        )
    return {"count": len(watches), "watches": alerts, "alerts": [a for a in alerts if a["alert"]]}


# --- Release radar ---
def release_radar(notes: Optional[str] = None) -> dict:
    """Titles to watch for beta windows / launch — lightweight curated list."""
    items = [
        {
            "title": "Gears of War: E-Day",
            "kind": "beta-window",
            "date": "2026-08-13",
            "window": "2026-08-13 to 2026-08-17",
            "note": "Open Beta (Versus 4v4 + Horde Siege). Free — no preorder needed.",
            "source": "X @SASxSH4DOWZ",
        },
        {
            "title": "Gears of War: E-Day",
            "kind": "release",
            "date": "2026-08-13",
            "window": None,
            "note": "Open Beta start. Evaluate after playing before committing to purchase.",
            "source": "X @SASxSH4DOWZ",
        },
    ]
    return {"count": len(items), "items": items, "notes": notes}


# --- Preorder advisor ---
def preorder_advisor(title: str) -> dict:
    key = title.strip().lower()
    # Built-in judgments from GenTech evaluations.
    if key in ("gears of war: e-day", "gears of war e-day", "gears e-day", "gears of war eday"):
        return {
            "title": "Gears of War: E-Day",
            "verdict": "WAIT",
            "confidence": "high",
            "summary": (
                "Do NOT pre-order for beta access. Early Access (Aug 6) is Horde-only PVE. "
                "The competitive Versus 4v4 mode is free in the Open Beta Aug 13-17 for everyone. "
                "Pre-order perk is weak — you'd pay for 3 days of a mode you don't play. "
                "Try the Open Beta first, then decide."
            ),
            "reasons": [
                "Early Access perk only covers Horde Siege (PVE), not Versus",
                "Versus (the draw) is free in the Open Beta for all",
                "Xbox Game Pass Ultimate members get the same early-access perk as pre-orders",
                "Community backlash confirms pre-order value is low (top comments negative)",
            ],
            "recommend": "wait_for_open_beta",
        }

    return {
        "title": title,
        "verdict": "UNKNOWN",
        "confidence": "low",
        "summary": (
            f"No pre-order evaluation on file for '{title}'. "
            "Supply release date, included modes, and bonus tiers for a verdict."
        ),
        "reasons": [],
        "recommend": "unknown",
    }
