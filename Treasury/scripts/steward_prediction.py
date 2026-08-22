#!/usr/bin/env python3
"""
The Steward — Prediction-Arb Rail (Phase 1 · DRY-RUN, no live orders).

Consumes prediction-market data from Polymarket (Gamma API) and Kalshi
(trade-api) to detect cross-venue arb edges on the same event. Writes a
state file (`.steward-prediction.json`) that feeds the fused Steward report
as a "🎯 Prediction" producer block.

Read-only + keyless (both public endpoints return HTTP 200 without auth).
No orders are placed — this is the edge DETECTOR. Phase 2 (agentic
flash-loan executor) will act on the flagged edge once funded + approved.

Edge types:
  1. Intra-venue: Polymarket YES + NO prices sum != ~1.0 (arbitrageable).
  2. Cross-venue: Polymarket vs Kalshi disagree on the same event by > threshold.

Usage:
  python3 steward_prediction.py            # detect edges, write state
  python3 steward_prediction.py --show     # print state to stdout (cron)
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ── Sources (keyless reads) ──────────────────────────────────────────────
POLY_SEARCH = "https://gamma-api.polymarket.com/public-search"
KALSHI_MARKETS = "https://api.elections.kalshi.com/trade-api/v2/markets"
KALSHI_EVENTS = "https://api.elections.kalshi.com/trade-api/v2/events"

# ── Tunables ─────────────────────────────────────────────────────────────
CROSS_VENUE_MIN_EDGE = 0.05   # 5pt minimum price disagreement to flag
INTRA_VENUE_TOLERANCE = 0.02  # |YES+NO - 1| above this = flag
MAX_MARKETS = 6
STATE_PATH = "/root/vaults/gentech/Treasury/.steward-prediction.json"


def fetch_json(url: str, timeout: int = 15) -> dict | None:
    """Fetch a JSON payload from a URL, tolerating network/HTTP errors."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (steward-prediction-rail)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:  # noqa: BLE001
        print(f"[steward_prediction] fetch failed {url}: {e}", file=sys.stderr)
        return None


def fmt_pct(v: float | None) -> str:
    return "n/a" if v is None else f"{v * 100:.1f}%"


def poly_search(q: str) -> list[dict]:
    """Search Polymarket for an event, return normalized market summaries."""
    out = []
    url = f"{POLY_SEARCH}?q={urllib.parse.quote(q)}&limit={MAX_MARKETS}"
    data = fetch_json(url)
    if not data:
        return out
    for e in data.get("events", [])[:MAX_MARKETS]:
        m = (e.get("markets") or [{}])[0]
        try:
            prices = json.loads(m.get("outcomePrices")) if isinstance(m.get("outcomePrices"), str) else m.get("outcomePrices")
        except Exception:  # noqa: BLE001
            prices = None
        yes = float(prices[0]) if prices and len(prices) > 0 else None
        no = float(prices[1]) if prices and len(prices) > 1 else None
        out.append({
            "venue": "polymarket",
            "title": e.get("title"),
            "slug": e.get("slug"),
            "yes": yes,
            "no": no,
            "liquidity": e.get("liquidity"),
            "url": f"https://polymarket.com/event/{e.get('slug')}",
        })
    return out


def kalshi_markets(q: str | None = None) -> list[dict]:
    """Fetch Kalshi markets; optionally filter by query term."""
    url = f"{KALSHI_MARKETS}?limit={MAX_MARKETS}"
    if q:
        url += f"&query={urllib.parse.quote(q)}"
    data = fetch_json(url)
    out = []
    if not data:
        return out
    for m in (data.get("markets") or [])[:MAX_MARKETS]:
        if m.get("status") != "active":
            continue
        yes_bid = m.get("yes_bid")
        yes_ask = m.get("yes_ask")
        # Mid-price as a proxy for the market's implied probability
        mid = None
        if isinstance(yes_bid, (int, float)) and isinstance(yes_ask, (int, float)):
            mid = (yes_bid + yes_ask) / 2 / 100.0  # Kalshi prices in cents
        out.append({
            "venue": "kalshi",
            "ticker": m.get("ticker"),
            "title": m.get("title"),
            "yes_bid": yes_bid,
            "yes_ask": yes_ask,
            "mid": mid,
            "url": f"https://kalshi.com/markets/{m.get('ticker')}",
        })
    return out


def detect_intra_venue(markets: list[dict]) -> list[dict]:
    """Flag Polymarket markets where YES + NO prices diverge from 1.0."""
    flags = []
    for m in markets:
        if m["venue"] != "polymarket" or m["yes"] is None or m["no"] is None:
            continue
        diff = abs(m["yes"] + m["no"] - 1.0)
        if diff > INTRA_VENUE_TOLERANCE:
            flags.append({**m, "edge_type": "intra_venue", "edge": round(diff, 4)})
    return flags


def detect_cross_venue(poly: list[dict], kalshi: list[dict]) -> list[dict]:
    """Naive cross-venue signal: report the largest spreads for manual review.
    Real cross-venue arb needs an exact event match (titles/slugs/IDs) — that
    mapping is a Phase-2 step. Phase 1 reports candidate spreads, not orders.
    """
    edges = []
    # Kalshi mid-price vs Polymarket YES price for any market whose title
    # contains a shared keyword — Phase 1 is exploratory, flags for review.
    for km in kalshi:
        if km["mid"] is None:
            continue
        for pm in poly:
            shared = None
            for kw in ("fed", "bitcoin", "btc", "mars", "nato", "pope"):
                if kw in (km.get("title") or "").lower() and kw in (pm.get("title") or "").lower():
                    shared = kw
                    break
            if shared:
                edge = pm["yes"] - km["mid"] if pm["yes"] is not None else 0
                if abs(edge) >= CROSS_VENUE_MIN_EDGE:
                    edges.append({
                        "venue": "cross_venue",
                        "shared_keyword": shared,
                        "polymarket_title": pm["title"],
                        "polymarket_yes": pm["yes"],
                        "kalshi_title": km["title"],
                        "kalshi_mid": km["mid"],
                        "edge": round(edge, 4),
                        "note": "REVIEW — requires exact event-id mapping (Phase 2)",
                    })
    return edges


def main() -> int:
    show = "--show" in sys.argv
    report = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "status": "dry_run",
        "edges": [],
        "markets_scanned": 0,
        "sources": {"polymarket": "ok", "kalshi": "ok"},
    }

    # Scan a few high-signal queries across both venues.
    queries = ["fed rate", "bitcoin"]
    poly_all, kalshi_all = [], []
    for q in queries:
        poly_all += poly_search(q)
        kalshi_all += kalshi_markets(q)

    if not poly_all:
        report["sources"]["polymarket"] = "error"
    if not kalshi_all:
        report["sources"]["kalshi"] = "error"

    report["markets_scanned"] = len(poly_all) + len(kalshi_all)
    report["edges"] = detect_intra_venue(poly_all) + detect_cross_venue(poly_all, kalshi_all)
    report["polymarket_preview"] = poly_all[:3]
    report["kalshi_preview"] = kalshi_all[:3]

    try:
        with open(STATE_PATH, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    except Exception as e:  # noqa: BLE001
        print(f"[steward_prediction] could not write state: {e}", file=sys.stderr)
        return 1

    if show or not report["edges"]:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"[steward_prediction] {len(report['edges'])} edge(s) found → {STATE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
