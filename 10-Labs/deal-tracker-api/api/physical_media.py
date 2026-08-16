"""GenTech Physical Media Scarcity Tracker.

The scarcity play (Jordan-confirmed Aug 16): Sony ends new PlayStation game
discs Jan 2028, but physical media is simultaneously resurging (4K Blu-ray up
12% in 2025, vinyl crossed $1B US sales, Gen Z rediscovering discs, streaming
fatigue). This is a SCARCITY play, not a death play — physical media that is
out-of-print or limited-run appreciates.

This module tracks a curated watchlist of physical media (4K Blu-ray,
steelbooks, vinyl, boutique releases) with scarcity signals:
  - OOP (out of print) / limited-run status
  - Price trend (MSRP vs current street price)
  - Scarcity score (0-100) — how hard it is to find at a fair price
  - Alerts when a tracked title crosses a scarcity/price threshold

Data model: curated catalog + per-title scarcity state, persisted to JSON.
Live price checks use web_extract (Blu-ray.com / Discogs / eBay) as a fallback
when available; otherwise the curated catalog carries the intelligence.
"""
import json
import os
import time
from datetime import datetime, timedelta
from typing import Optional

# --- Persistence ---
DATA_DIR = os.environ.get(
    "PHYSICAL_MEDIA_DATA_DIR",
    "/root/vaults/gentech/10-Labs/deal-tracker-api/data",
)
CATALOG_FILE = os.path.join(DATA_DIR, "physical_media_catalog.json")
WATCH_FILE = os.path.join(DATA_DIR, "physical_media_watch.json")

# --- Scarcity score bands ---
# 0-39: widely available (reprint, in stock everywhere)
# 40-69: tightening (limited run, some retailers OOS)
# 70-89: scarce (OOP or near-OOP, secondary market premium)
# 90-100: critical (OOP, hard to find at fair price, appreciating)
SCARCITY_BANDS = [
    (90, "critical", "OOP / appreciating — buy now if you want it"),
    (70, "scarce", "Near-OOP — secondary market premium forming"),
    (40, "tightening", "Limited run — some retailers out of stock"),
    (0, "available", "Widely available — no urgency"),
]


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# --- Default curated catalog (seeded; extend as titles are evaluated) ---
# Each entry: title, format, label, msrp, scarcity signals.
DEFAULT_CATALOG = [
    {
        "id": "pm_4k_dune2",
        "title": "Dune: Part Two",
        "format": "4K UHD",
        "label": "Warner Bros",
        "msrp": 39.99,
        "scarcity": 35,
        "status": "available",
        "note": "Widely available; standard 4K reprint. Steelbook variant is the scarce one.",
        "source": "curated",
    },
    {
        "id": "pm_4k_oppenheimer",
        "title": "Oppenheimer",
        "format": "4K UHD",
        "label": "Universal",
        "msrp": 34.99,
        "scarcity": 30,
        "status": "available",
        "note": "Massive print run, still in stock everywhere. Not a scarcity play yet.",
        "source": "curated",
    },
    {
        "id": "pm_4k_interstellar",
        "title": "Interstellar (10th Anniversary)",
        "format": "4K UHD Steelbook",
        "label": "Paramount",
        "msrp": 44.99,
        "scarcity": 55,
        "status": "tightening",
        "note": "Anniversary steelbook limited run; secondary market already above MSRP.",
        "source": "curated",
    },
    {
        "id": "pm_4k_matrix",
        "title": "The Matrix (Ultimate Collection)",
        "format": "4K UHD",
        "label": "Warner Bros",
        "msrp": 79.99,
        "scarcity": 45,
        "status": "tightening",
        "note": "Box set going OOP as Warner trims physical catalog; individual discs still available.",
        "source": "curated",
    },
    {
        "id": "pm_vinyl_zeppelin",
        "title": "Led Zeppelin IV (2025 Reissue)",
        "format": "Vinyl LP",
        "label": "Atlantic",
        "msrp": 34.99,
        "scarcity": 25,
        "status": "available",
        "note": "Standard reissue, widely stocked. Colored variant is the collectible.",
        "source": "curated",
    },
    {
        "id": "pm_vinyl_taylor",
        "title": "Taylor Swift — The Tortured Poets Department (Collector)",
        "format": "Vinyl LP",
        "label": "Republic",
        "msrp": 49.99,
        "scarcity": 60,
        "status": "tightening",
        "note": "Collector variants sell out fast; resale premium on rare pressings.",
        "source": "curated",
    },
    {
        "id": "pm_4k_sony_ps5",
        "title": "PlayStation 5 Physical Game (Post-2028)",
        "format": "PS5 Disc",
        "label": "Sony",
        "msrp": 69.99,
        "scarcity": 80,
        "status": "scarce",
        "note": "Sony ends new PS5 game discs Jan 2028. Existing physical PS5 library becomes the last generation of disc games — scarcity play on the whole format.",
        "source": "curated",
    },
    {
        "id": "pm_4k_criterion",
        "title": "Criterion Collection — Out-of-Print Titles",
        "format": "4K UHD / Blu-ray",
        "label": "Criterion",
        "msrp": 49.99,
        "scarcity": 75,
        "status": "scarce",
        "note": "Criterion routinely lets licenses lapse; OOP titles command 2-3x on secondary market.",
        "source": "curated",
    },
]


def _load_catalog():
    data = _load_json(CATALOG_FILE, None)
    if data is None:
        _save_json(CATALOG_FILE, {"catalog": DEFAULT_CATALOG, "updated": _now_iso()})
        return DEFAULT_CATALOG
    return data.get("catalog", DEFAULT_CATALOG)


def _load_watch():
    return _load_json(WATCH_FILE, {"watches": [], "updated": _now_iso()})


def _save_watch(watch_data):
    watch_data["updated"] = _now_iso()
    _save_json(WATCH_FILE, watch_data)


def _band_for(score):
    for threshold, key, desc in SCARCITY_BANDS:
        if score >= threshold:
            return {"key": key, "label": desc}
    return {"key": "available", "label": "Widely available"}


def search(title: str = "", limit: int = 20) -> dict:
    """Search the curated physical media catalog by title."""
    catalog = _load_catalog()
    q = title.strip().lower()
    results = []
    for item in catalog:
        if q and q not in item["title"].lower():
            continue
        band = _band_for(item["scarcity"])
        results.append(
            {
                "id": item["id"],
                "title": item["title"],
                "format": item["format"],
                "label": item["label"],
                "msrp": item["msrp"],
                "scarcity_score": item["scarcity"],
                "scarcity_band": band["key"],
                "scarcity_label": band["label"],
                "status": item["status"],
                "note": item["note"],
            }
        )
    results = sorted(results, key=lambda r: -r["scarcity_score"])
    return {"query": title, "count": len(results), "items": results[:limit]}


def scarcity_leaderboard(limit: int = 10) -> dict:
    """Top-scarcity titles — the 'buy now' list."""
    catalog = _load_catalog()
    ranked = sorted(catalog, key=lambda i: -i["scarcity"])
    items = []
    for item in ranked[:limit]:
        band = _band_for(item["scarcity"])
        items.append(
            {
                "id": item["id"],
                "title": item["title"],
                "format": item["format"],
                "scarcity_score": item["scarcity"],
                "scarcity_band": band["key"],
                "status": item["status"],
                "note": item["note"],
            }
        )
    return {"count": len(items), "items": items}


def add_watch(title: str, target_score: int = 70) -> dict:
    """Track a title; alert when its scarcity score crosses target_score."""
    catalog = _load_catalog()
    match = next((i for i in catalog if i["title"].lower() == title.strip().lower()), None)
    if not match:
        return {"status": "error", "detail": f"Title '{title}' not in catalog. Add it first."}

    watch_data = _load_watch()
    watches = watch_data["watches"]
    key = title.strip().lower()
    for w in watches:
        if w["title"].strip().lower() == key:
            w["target_score"] = target_score
            w["updated"] = _now_iso()
            _save_watch(watch_data)
            return {"status": "updated", "watch": w}

    watch = {
        "id": f"pmw_{int(time.time())}",
        "title": match["title"],
        "target_score": target_score,
        "current_score": match["scarcity"],
        "created": _now_iso(),
        "status": "tracking",
    }
    watches.append(watch)
    _save_watch(watch_data)
    return {"status": "created", "watch": watch}


def check_watches() -> dict:
    """Scan watched titles; flag any whose scarcity score crossed the target."""
    watch_data = _load_watch()
    watches = watch_data["watches"]
    if not watches:
        return {"count": 0, "watches": [], "alerts": []}

    catalog = _load_catalog()
    alerts = []
    for w in watches:
        match = next((i for i in catalog if i["title"].lower() == w["title"].strip().lower()), None)
        if not match:
            continue
        current = match["scarcity"]
        w["current_score"] = current
        band = _band_for(current)
        hit = current >= w["target_score"]
        alerts.append(
            {
                "watch_id": w["id"],
                "title": w["title"],
                "current_score": current,
                "target_score": w["target_score"],
                "scarcity_band": band["key"],
                "alert": hit,
            }
        )
    _save_watch(watch_data)
    return {"count": len(watches), "watches": alerts, "alerts": [a for a in alerts if a["alert"]]}


def add_title(
    title: str,
    format: str,
    label: str,
    msrp: float,
    scarcity: int,
    note: str = "",
) -> dict:
    """Add a new title to the catalog (curated intelligence)."""
    catalog = _load_catalog()
    key = title.strip().lower()
    if any(i["title"].strip().lower() == key for i in catalog):
        return {"status": "error", "detail": f"Title '{title}' already in catalog."}

    item = {
        "id": f"pm_{int(time.time())}",
        "title": title,
        "format": format,
        "label": label,
        "msrp": msrp,
        "scarcity": max(0, min(100, int(scarcity))),
        "status": _band_for(max(0, min(100, int(scarcity))))["key"],
        "note": note,
        "source": "curated",
    }
    catalog.append(item)
    _save_json(CATALOG_FILE, {"catalog": catalog, "updated": _now_iso()})
    return {"status": "created", "item": item}
