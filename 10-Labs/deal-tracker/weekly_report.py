#!/usr/bin/env python3
"""
Deal Tracker Weekly Report Generator
Generates tiered discount report from watchlist data.
Supports multiple users (Jordan + others).
"""

import os
import sys
import json
import glob
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from deal_tracker import CheapSharkClient, Deal, WishlistMonitor

WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")


def get_all_watchlists() -> list[tuple[str, str]]:
    """Find all watchlist files (default + per-user).
    Returns list of (label, filepath) tuples.
    """
    watchlists = []
    watchlist_dir = os.path.dirname(WATCHLIST_FILE)

    # Default watchlist (Jordan)
    if os.path.exists(WATCHLIST_FILE):
        watchlists.append(("Jordan", WATCHLIST_FILE))

    # Per-user watchlists
    for path in sorted(glob.glob(os.path.join(watchlist_dir, "watchlist-*.json"))):
        fname = os.path.basename(path)
        steam_id = fname.replace("watchlist-", "").replace(".json", "")
        watchlists.append((f"User {steam_id}", path))

    return watchlists


def get_discount_tier(savings: float) -> str:
    """Classify discount into tier"""
    if savings >= 50:
        return "deep_cut"
    elif savings >= 25:
        return "solid_sale"
    elif savings >= 10:
        return "light_mark"
    else:
        return "barely"


def generate_report_for_watchlist(label: str, watchlist_file: str, client: CheapSharkClient) -> str:
    """Generate a tiered report for a single watchlist."""
    try:
        with open(watchlist_file) as f:
            data = json.load(f)
        # Check if deal_tracker is enabled for this user
        features = data.get("features", {})
        if features.get("deal_tracker") is False:
            return ""
    except FileNotFoundError:
        return ""

    games = data.get("items", data.get("games", []))
    if not games:
        return ""

    output = []
    watchlists = get_all_watchlists()
    if len(watchlists) > 1:
        output.append(f"👤 {label} ({len(games)} games)")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    deals_by_tier = {"deep_cut": [], "solid_sale": [], "light_mark": [], "barely": []}
    unreleased = []

    for game in games:
        game_id = game.get("game_id", "")
        title = game.get("title", "Unknown")
        steam_appid = game.get("steam_appid")

        try:
            deal = client.get_cheapest_price(game_id, title=title, steam_appid=steam_appid)
        except Exception:
            deal = None

        if deal is None:
            unreleased.append(title)
            continue

        normal_price = deal.normal_price
        sale_price = deal.sale_price

        if normal_price > 0 and sale_price < normal_price:
            savings_pct = ((normal_price - sale_price) / normal_price) * 100
        else:
            savings_pct = 0

        tier = get_discount_tier(savings_pct)
        store_name = deal.store_name or ""
        is_subscription = any(x in store_name.lower() for x in ["xp", "member"])

        deals_by_tier[tier].append({
            "title": title,
            "sale_price": sale_price,
            "normal_price": normal_price,
            "savings_pct": savings_pct,
            "store": store_name,
            "deal_id": deal.deal_id,
            "is_subscription": is_subscription,
        })

    # Render tiers
    for tier_key, emoji, label_text in [
        ("deep_cut", "🔥", "DEEP CUTS (50%+ off)"),
        ("solid_sale", "💰", "SOLID SALES (25-49% off)"),
        ("light_mark", "🏷️", "LIGHT MARKS (10-24% off)"),
        ("barely", "📉", "BARELY TOUCHING IT (<10%)"),
    ]:
        if deals_by_tier[tier_key]:
            output.append(f"{emoji} {label_text}")
            output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for d in sorted(deals_by_tier[tier_key], key=lambda x: x["savings_pct"], reverse=True):
                sub_tag = " [SUB]" if d["is_subscription"] else ""
                output.append(f"  {d['title']}")
                output.append(f"     ${d['sale_price']:.2f} (was ${d['normal_price']:.2f}) — {d['savings_pct']:.0f}% off at {d['store']}{sub_tag}")
                output.append("")

    if unreleased:
        output.append("🚨 UNRELEASED / UPCOMING")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for title in sorted(unreleased):
            output.append(f"  • {title}")
        output.append("")

    return "\n".join(output)


def main():
    """Generate reports for ALL watchlists (Jordan + users)."""
    watchlists = get_all_watchlists()

    if not watchlists:
        print("❌ No watchlists found")
        return

    print(f"🎮 DEAL TRACKER — Weekly Sweep")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📅 {datetime.now().strftime('%B %d, %Y')}")
    print(f"👥 Tracking {len(watchlists)} user(s)")
    print()

    client = CheapSharkClient(cache_enabled=True)

    total_games = 0
    for label, filepath in watchlists:
        report = generate_report_for_watchlist(label, filepath, client)
        if report:
            print(report)
            # Count games
            try:
                with open(filepath) as f:
                    data = json.load(f)
                total_games += len(data.get("items", data.get("games", [])))
            except Exception:
                pass

    # Summary
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 SUMMARY")
    print(f"  Users: {len(watchlists)}")
    print(f"  Total games tracked: {total_games}")


if __name__ == "__main__":
    main()
