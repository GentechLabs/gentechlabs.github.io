#!/usr/bin/env python3
"""
Deal Tracker MVP — Runner Script

Searches for deals, checks wishlist prices, records history, outputs alerts.
Designed to be called by Hermes cron job — stdout is delivered to Telegram.

Uses WishlistMonitor for all persistence (watchlist.json with `items` key).

Usage:
  python3 deal_runner.py                    # Check wishlist prices
  python3 deal_runner.py search "elden ring" # Search for a game
  python3 deal_runner.py trend <game_id>     # Show price trend
  python3 deal_runner.py add <game_id> <title> <target_price>  # Add to wishlist
  python3 deal_runner.py remove <game_id>    # Remove from wishlist
  python3 deal_runner.py hot                 # Show today's hottest deals
  python3 deal_runner.py list                # List watchlist
"""

import sys
import os
import json
import time
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from deal_tracker import CheapSharkClient, DealAnalyzer, DealReporter, WishlistMonitor
from price_history import record_price, get_price_trend, format_trend

WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")


def get_monitor(client: CheapSharkClient = None) -> WishlistMonitor:  # type: ignore[assignment]
    """Get a WishlistMonitor with the shared watchlist file."""
    if client is None:
        client = CheapSharkClient(cache_enabled=True)
    return WishlistMonitor(client, state_file=WATCHLIST_FILE)


def cmd_check():
    """Check all wishlist items for price drops — single pass, minimal API calls."""
    client = CheapSharkClient(cache_enabled=True)
    monitor = get_monitor(client)

    if not monitor.items:
        print("📋 Watchlist is empty. Add games with: deal_tracker.py add <game_id> <title> <price>")
        return

    # Single pass: check prices, record history, detect alerts
    results = []
    for item in monitor.items:
        try:
            deal = client.get_cheapest_price(item.game_id, title=item.title)
        except Exception:
            deal = None
            pass

        if deal:
            # Record price history
            try:
                record_price(item.game_id, item.title, deal.sale_price, deal.store_name, deal.deal_id)
            except Exception:
                pass

            # Check if this is an alert
            is_alert = deal.sale_price <= item.target_price
            if is_alert and not item.notified:
                item.notified = True
                alert_type = "FREE!" if deal.sale_price == 0 else "below target"
                results.append({
                    "title": item.title,
                    "price": deal.sale_price,
                    "store": deal.store_name,
                    "target": item.target_price,
                    "deal_id": deal.deal_id,
                    "alert": True,
                    "alert_type": alert_type,
                })
            elif deal.sale_price > item.target_price:
                item.notified = False
                results.append({
                    "title": item.title,
                    "price": deal.sale_price,
                    "store": deal.store_name,
                    "target": item.target_price,
                    "alert": False,
                })
            else:
                # Already notified, just track status
                results.append({
                    "title": item.title,
                    "price": deal.sale_price,
                    "store": deal.store_name,
                    "target": item.target_price,
                    "alert": False,
                })
        else:
            results.append({
                "title": item.title,
                "price": None,
                "store": "N/A",
                "target": item.target_price,
                "alert": False,
            })

    # Save notified state
    monitor._save()

    # Build output
    alerts = [r for r in results if r.get("alert")]
    lines = ["🎮 Deal Tracker — Price Check\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"]

    if alerts:
        lines.append(f"🔔 {len(alerts)} PRICE ALERT(S):\n")
        for a in alerts:
            price_str = "FREE" if a["price"] == 0 else f"${a['price']:.2f}"
            lines.append(
                f"🎯 {a['title']}\n"
                f"   💰 {price_str} at {a['store']} ({a['alert_type']})\n"
                f"   🏷️ Target was: ${a['target']:.2f}\n"
                f"   🔗 https://www.cheapshark.com/open/deal?q={a['title'].replace(' ', '+')}\n"
            )

    lines.append(f"📊 Tracking {len(results)} game(s):\n")
    for r in results:
        icon = "🟢" if r.get("alert") else "⚪"
        current = f"${r['price']:.2f}" if r['price'] is not None else "N/A"
        target = f"${r['target']:.2f}"
        lines.append(f"  {icon} {r['title']}")
        lines.append(f"     Current: {current} at {r['store']}  |  Target: {target}")

    print("\n".join(lines))


def cmd_search(query: str):
    """Search for deals matching a query."""
    client = CheapSharkClient(cache_enabled=True)
    deals = client.search_deals(title=query, upper_price=60, page_size=10)

    if not deals:
        print(f"❌ No deals found for '{query}'")
        return

    ranked = DealAnalyzer.rank_deals(deals, "value")
    report = DealReporter.format_comparison(ranked, f"Deals for '{query}'")
    print(report)


def cmd_hot():
    """Show today's hottest deals across all stores."""
    client = CheapSharkClient(cache_enabled=True)
    deals = client.search_deals(upper_price=30, page_size=20, sort_by="Deal Rating")

    if not deals:
        print("❌ No hot deals found right now")
        return

    ranked = DealAnalyzer.rank_deals(deals, "value")
    report = DealReporter.format_comparison(ranked, "🔥 Today's Hottest Deals (Under $30)")
    print(report)


def cmd_trend(game_id: str):
    """Show price trend for a game."""
    trend = get_price_trend(game_id)
    print(format_trend(trend))


def cmd_add(game_id: str, title: str, target_price: str):
    """Add a game to the watchlist."""
    try:
        price = float(target_price)
    except ValueError:
        print(f"❌ Invalid price: {target_price}")
        return

    monitor = get_monitor()
    for item in monitor.items:
        if item.game_id == game_id:
            item.target_price = price
            monitor._save()
            print(f"✅ Updated {title} target price to ${price:.2f}")
            return

    monitor.add(game_id, title, price)
    print(f"✅ Added {title} (ID: {game_id}) — alert when ≤ ${price:.2f}")


def cmd_remove(game_id: str):
    """Remove a game from the watchlist."""
    monitor = get_monitor()
    if monitor.remove(game_id):
        print(f"✅ Removed game {game_id} from watchlist")
    else:
        print(f"❌ Game {game_id} not found in watchlist")


def cmd_list():
    """List all games in the watchlist."""
    monitor = get_monitor()
    if not monitor.items:
        print("📋 Watchlist is empty")
        return

    print(f"📋 Watchlist ({len(monitor.items)} games):\n")
    for item in monitor.items:
        print(f"  • {item.title} (ID: {item.game_id}) — target: ${item.target_price:.2f}")


def cmd_sync_steam(steam_id: str = ""):
    """Pull live Steam wishlist and update watchlist.json.

    Usage: python3 deal_runner.py sync-steam [steam_id_or_vanity_url]

    Examples:
      python3 deal_runner.py sync-steam                    # Jordan's default
      python3 deal_runner.py sync-steam 76561198068413360  # numeric Steam ID
      python3 deal_runner.py sync-steam Vanito              # vanity URL
    """
    import urllib.request

    # Default to Jordan's Steam ID
    if not steam_id:
        steam_id = "76561198068413360"

    # Resolve vanity URL to numeric ID if needed
    if not steam_id.isdigit():
        print(f"🔄 Resolving vanity URL: {steam_id}")
        try:
            vanity_url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?vanityurl={steam_id}"
            req = urllib.request.Request(vanity_url, headers={"User-Agent": "DealTracker/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                response = data.get("response", {})
                if response.get("success") == 1:
                    steam_id = response["steamid"]
                    print(f"✅ Resolved to Steam ID: {steam_id}")
                else:
                    print(f"❌ Could not resolve vanity URL: {steam_id}")
                    return
        except Exception as e:
            print(f"❌ Failed to resolve vanity URL: {e}")
            return

    # Per-user watchlist file
    watchlist_dir = os.path.dirname(WATCHLIST_FILE)
    user_watchlist = os.path.join(watchlist_dir, f"watchlist-{steam_id}.json")

    # Use default watchlist for Jordan, per-user files for others
    if steam_id == "76561198068413360":
        target_file = WATCHLIST_FILE
    else:
        target_file = user_watchlist

    STEAM_URL = f"https://api.steampowered.com/IWishlistService/GetWishlist/v1/?steamid={steam_id}"

    print(f"🔄 Syncing Steam wishlist for {steam_id}...")

    try:
        req = urllib.request.Request(STEAM_URL, headers={"User-Agent": "DealTracker/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"❌ Failed to fetch Steam wishlist: {e}")
        return

    items = data.get("response", {}).get("items", [])
    if not items:
        print("❌ No items found — is your wishlist public?")
        return

    appids = [item.get("appid") for item in items if item.get("appid")]
    print(f"📥 Found {len(appids)} games on Steam wishlist")

    # Resolve app IDs to names (batch, with rate limiting)
    resolved = []
    for i, appid in enumerate(appids):
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            req = urllib.request.Request(url, headers={"User-Agent": "DealTracker/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                app_data = json.loads(resp.read())
                if str(appid) in app_data and app_data[str(appid)]["success"]:
                    name = app_data[str(appid)]["data"]["name"]
                    resolved.append({"appid": appid, "title": name})
        except Exception:
            pass
        if i % 10 == 9:
            time.sleep(1)  # rate limit every 10

    print(f"✅ Resolved {len(resolved)}/{len(appids)} game names")

    # Load existing watchlist to preserve target prices
    existing = {}
    try:
        with open(WATCHLIST_FILE) as f:
            old_data = json.load(f)
            for g in old_data.get("games", []):
                existing[g.get("game_id", "")] = g.get("target_price", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Build new watchlist
    new_games = []
    for r in resolved:
        game_id = str(r["appid"])
        new_games.append({
            "game_id": game_id,
            "title": r["title"],
            "target_price": existing.get(game_id, 0),  # preserve existing targets
            "steam_appid": r["appid"],
        })

    # Save
    watchlist_data = {
        "steam_id": steam_id,
        "synced": datetime.now(timezone.utc).isoformat(),
        "features": {
            "patch_notes": True,
            "deal_tracker": True,
        },
        "games": new_games,
    }
    with open(target_file, "w") as f:
        json.dump(watchlist_data, f, indent=2)

    print(f"✅ Watchlist updated: {len(new_games)} games")
    added = len(new_games) - len(existing)
    removed = len([g for g in existing if g not in [str(r["appid"]) for r in resolved]])
    if added > 0:
        print(f"   ➕ {added} new games added")
    if removed > 0:
        print(f"   ➖ {removed} games removed")


def cmd_toggle_feature(steam_id: str, feature: str, enabled: str):
    """Toggle a feature for a user's watchlist.
    Usage: python3 deal_runner.py toggle <steam_id> <feature> <on|off>
    Features: patch_notes, deal_tracker
    """
    watchlist_dir = os.path.dirname(WATCHLIST_FILE)
    if steam_id == "76561198068413360":
        target_file = WATCHLIST_FILE
    else:
        target_file = os.path.join(watchlist_dir, f"watchlist-{steam_id}.json")

    if not os.path.exists(target_file):
        print(f"❌ No watchlist found for {steam_id}")
        return

    try:
        with open(target_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"❌ Invalid watchlist for {steam_id}")
        return

    # Initialize features dict if missing
    if "features" not in data:
        data["features"] = {"patch_notes": True, "deal_tracker": True}

    if feature not in ("patch_notes", "deal_tracker"):
        print(f"❌ Unknown feature: {feature}. Use 'patch_notes' or 'deal_tracker'")
        return

    data["features"][feature] = enabled.lower() in ("on", "true", "1", "yes")

    with open(target_file, "w") as f:
        json.dump(data, f, indent=2)

    status = "✅ ON" if data["features"][feature] else "❌ OFF"
    print(f"{status} {feature} for {steam_id}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        cmd_check()
    elif args[0] == "search" and len(args) > 1:
        cmd_search(" ".join(args[1:]))
    elif args[0] == "hot":
        cmd_hot()
    elif args[0] == "trend" and len(args) > 1:
        cmd_trend(args[1])
    elif args[0] == "add" and len(args) > 3:
        cmd_add(args[1], args[2], args[3])
    elif args[0] == "remove" and len(args) > 1:
        cmd_remove(args[1])
    elif args[0] == "list":
        cmd_list()
    elif args[0] == "sync-steam":
        steam_id = args[1] if len(args) > 1 else ""
        cmd_sync_steam(steam_id)
    elif args[0] == "toggle" and len(args) > 3:
        cmd_toggle_feature(args[1], args[2], args[3])
    else:
        print(__doc__)
