#!/usr/bin/env python3
"""
Game Release Intelligence — Track unreleased wishlist games for news & release dates.

Polls Steam News API + appdetails for each unreleased game on the wishlist.
Detects: new devlogs, release date announcements, trailer drops, status changes.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from deal_tracker import WishlistMonitor, CheapSharkClient

WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")
STATE_DIR = os.path.join(os.path.dirname(__file__), "..", ".patch-notes-state")
DEFAULT_CURRENCY = "us"  # USD default — override with --currency flag
STEAM_NEWS_BASE = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
STEAM_APPDETAILS = "https://store.steampowered.com/api/appdetails"

REQUEST_DELAY = 1.5


def load_state() -> dict:
    """Load previous state (last seen news IDs, release dates)."""
    state_file = os.path.join(STATE_DIR, "global-state.json")
    if os.path.exists(state_file):
        try:
            with open(state_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"games": {}, "last_run": ""}
def save_state(state: dict) -> None:
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state_file = os.path.join(STATE_DIR, "global-state.json")
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def get_app_details(appid: int, currency: str = "") -> dict | None:
    """Fetch Steam app details (release date, developer, type)."""
    cc = currency or DEFAULT_CURRENCY
    url = f"{STEAM_APPDETAILS}?appids={appid}&cc={cc}&filters=release_date,price_overview,basic"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DealTracker/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            app_data = data.get(str(appid), {})
            if app_data.get("success"):
                details = app_data.get("data", {})
                # Detect Early Access from description
                desc = details.get("detailed_description", "").lower()
                details["_is_early_access"] = "early access" in desc
                return details
    except Exception as e:
        print(f"  ⚠️ Failed to fetch appdetails for {appid}: {e}")
    return None


def get_steam_news(appid: int, count: int = 10) -> list[dict]:
    """Fetch recent Steam news/updates for a game."""
    url = f"{STEAM_NEWS_BASE}?appid={appid}&count={count}&maxlength=500"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DealTracker/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("appnews", {}).get("newsitems", [])
    except Exception as e:
        print(f"  ⚠️ Failed to fetch news for {appid}: {e}")
    return []


def detect_updates(appid: int, title: str, state: dict, currency: str = "") -> dict:
    """Check a single game for news and release date changes."""
    game_state = state["games"].get(str(appid), {})
    prev_news_ids = set(game_state.get("seen_news_ids", []))
    prev_release_date = game_state.get("release_date", "")

    # Fetch current data
    details = get_app_details(appid, currency=currency)
    time.sleep(REQUEST_DELAY)

    news_items = get_steam_news(appid)
    time.sleep(REQUEST_DELAY)

    result = {
        "appid": appid,
        "title": title,
        "new_items": [],
        "release_date_changed": False,
        "release_date": "",
        "developer": "",
        "coming_soon": False,
        "is_early_access": False,
        "current_price": None,
        "price_announcements": [],
    }
    if details:
        result["title"] = details.get("name", "")
        result["developer"] = ", ".join(details.get("developers", []))
        release_info = details.get("release_date", {})
        result["coming_soon"] = release_info.get("coming_soon", False)
        result["release_date"] = release_info.get("date", "TBA")
        result["is_early_access"] = details.get("_is_early_access", False)
        # Get current price for Early Access games
        if result["is_early_access"]:
            try:
                price_info = details.get("price_overview", {})
                if price_info:
                    result["current_price"] = {
                        "final": price_info.get("final_formatted", ""),
                        "discount": price_info.get("discount_percent", 0),
                    }
            except Exception:
                pass

        if prev_release_date and result["release_date"] != prev_release_date:
            result["release_date_changed"] = True
    # Detect new news items
    price_keywords = ["price", "cost", "$", "increase", "discount", "launch price", "1.0 price"]
    for item in news_items:
        gid = str(item.get("gid", ""))
        if gid and gid not in prev_news_ids:
            feed = item.get("feedname", "unknown")
            item_title = item.get("title", "")
            item_lower = item_title.lower()

            result["new_items"].append({
                "gid": gid,
                "title": item_title,
                "feed": feed,
                "is_dev_update": feed in {
                    "steam_community_announcements",
                    "steam_updates",
                    "steam_deck",
                    "steam_global",
                },
                "is_price_update": any(kw in item_lower for kw in price_keywords),
                "date": item.get("date", 0),
                "url": f"https://store.steampowered.com/news/app/{appid}?feed={feed}",
            })
    # Update state
    all_news_ids = list(prev_news_ids | {str(i.get("gid", "")) for i in news_items})
    # Keep last 50 IDs to prevent unbounded growth
    state["games"][str(appid)] = {
        "seen_news_ids": all_news_ids[-50:],
        "release_date": result["release_date"],
        "title": title,
        "last_checked": datetime.now(timezone.utc).isoformat(),
    }

    return result


def format_report(results: list[dict]) -> str:
    """Format results into a readable report."""
    lines = []
    has_news = [r for r in results if r["new_items"] or r["release_date_changed"]]
    unreleased = [r for r in results if r["coming_soon"] or r.get("is_early_access")]

    if not has_news and not unreleased:
        return "✅ No new updates on unreleased wishlist games."

    # Section 1: Breaking news
    if has_news:
        lines.append("🔔 GAME INTEL — New Updates")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for r in has_news:
            lines.append(f"")
            lines.append(f"🎮 {r['title']}")
            if r["developer"]:
                lines.append(f"   👨‍💻 {r['developer']}")

            if r["release_date_changed"]:
                lines.append(f"   📅 RELEASE DATE: {r['release_date']}")
                lines.append(f"   ⚡ Date changed from previous!")

            for item in r["new_items"]:
                date_str = datetime.fromtimestamp(item["date"], tz=timezone.utc).strftime("%b %d, %Y")
                dev_tag = " [DEV]" if item.get("is_dev_update") else ""
                price_tag = " 💰 PRICE" if item.get("is_price_update") else ""
                lines.append(f"   📰 {item['title']}{dev_tag}{price_tag}")
                lines.append(f"      {date_str} — {item['feed']}")
                lines.append(f"      🔗 {item['url']}")

            # Show current price for Early Access games
            if r.get("is_early_access") and r.get("current_price"):
                price = r["current_price"]
                discount = f" ({price['discount']}% off)" if price["discount"] > 0 else ""
                lines.append(f"   💵 Current EA Price: {price['final']}{discount}")
                lines.append(f"   ⚠️ Price may increase at 1.0 launch")
        lines.append("")

    # Section 2: Upcoming games summary
    if unreleased:
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"📅 UNRELEASED / EARLY ACCESS ({len(unreleased)} total)")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for r in unreleased[:15]:
            date_str = r["release_date"] or "TBA"
            ea_tag = " [Early Access]" if r.get("is_early_access") else ""
            lines.append(f"  • {r['title']} — {date_str}{ea_tag}")
        if len(unreleased) > 15:
            lines.append(f"  ... and {len(unreleased) - 15} more")
        lines.append("")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Game Release Intelligence")
    parser.add_argument("--unreleased-only", action="store_true", help="Only check games with coming_soon=true")
    parser.add_argument("--max", type=int, default=0, help="Max games to check (0=all)")
    parser.add_argument("--currency", type=str, default="", help="Currency: us, uk, eu, jp, etc. (default: us)")
    parser.add_argument("--user", type=str, default="", help="Steam ID to filter by (e.g., 76561198132811363)")
    args = parser.parse_args()

    # Load all watchlists (Jordan + users)
    import glob as _glob
    watchlist_dir = os.path.dirname(WATCHLIST_FILE)
    watchlist_files = [WATCHLIST_FILE] + sorted(_glob.glob(os.path.join(watchlist_dir, "watchlist-*.json")))

    all_games = []
    for wl_file in watchlist_files:
        try:
            with open(wl_file) as f:
                data = json.load(f)
            # Check if patch_notes is enabled for this user
            features = data.get("features", {})
            if features.get("patch_notes") is False:
                label = data.get("steam_id", os.path.basename(wl_file))
                print(f"⏭️ Skipping {label} — patch_notes disabled")
                continue
            # Filter by user if requested
            if args.user:
                steam_id = data.get("steam_id", "")
                if not steam_id:
                    # Try to extract from filename
                    fn = os.path.basename(wl_file)
                    if fn.startswith("watchlist-") and fn.endswith(".json"):
                        steam_id = fn[10:-5]
                if steam_id != args.user:
                    continue
            games = data.get("items", data.get("games", []))
            all_games.extend(games)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    if not all_games:
        print("❌ No watchlists found. Run deal_runner.py sync-steam first.")
        return
    games = all_games
    if not games:
        print("📋 All watchlists empty")
        return
    # Load state
    state = load_state()

    # Filter if requested
    if args.unreleased_only:
        games = [g for g in games if state.get("games", {}).get(str(g.get("steam_appid") or g.get("game_id", "")), {}).get("release_date", "") in ("", "TBA", "To be announced")]
        print(f"🔍 Checking {len(games)} unreleased games...")

    if args.max > 0:
        games = games[:args.max]
        print(f"🔍 Limited to {len(games)} games")

    if not args.unreleased_only and not args.max:
        print(f"🔍 Checking {len(games)} games for updates...")
    print()

    results = []
    for i, game in enumerate(games):
        appid = game.get("steam_appid") or game.get("game_id")
        if not appid or not str(appid).isdigit():
            continue

        appid = int(appid)
        title = game.get("title", "Unknown")
        print(f"  [{i+1}/{len(games)}] {title} (AppID: {appid})")

        result = detect_updates(appid, title, state, currency=args.currency)
        results.append(result)

    # Save state
    save_state(state)

    # Generate report
    report = format_report(results)
    print()
    print(report)


if __name__ == "__main__":
    main()
