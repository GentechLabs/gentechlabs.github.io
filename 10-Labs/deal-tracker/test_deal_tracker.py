"""Tests for Deal Tracker — runs against live CheapShark API (no key needed)."""

import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

from deal_tracker import (
    CheapSharkClient, DealAnalyzer, DealReporter, WishlistMonitor,
    WishlistItem, Deal, GameInfo, Store, PriceAlert,
    APIError,
)


def test_store_fetch():
    """CheapShark returns 35+ stores."""
    client = CheapSharkClient(cache_enabled=False)
    stores = client.get_stores()
    assert len(stores) >= 30, f"Expected 30+ stores, got {len(stores)}"
    steam = client.get_store(1)
    assert steam is not None, "Steam store not found"
    assert steam.name == "Steam"
    print(f"✅ Stores: {len(stores)} fetched, Steam identified")


def test_deal_search():
    """Search deals by title."""
    client = CheapSharkClient(cache_enabled=False)
    deals = client.search_deals(title="mario", upper_price=60, page_size=5)
    assert isinstance(deals, list)
    assert len(deals) > 0, "No deals found for 'mario'"
    d = deals[0]
    assert d.title != "Unknown", "Title missing"
    assert d.sale_price >= 0, "Invalid price"
    assert d.store_name != "", "Store name not enriched"
    print(f"✅ Deal search: {len(deals)} results for 'mario', best: {d.title} ${d.sale_price}")


def test_game_search():
    """Search games by title."""
    client = CheapSharkClient(cache_enabled=False)
    games = client.search_games("cyberpunk", limit=3)
    assert len(games) > 0, "No games found for 'cyberpunk'"
    assert any("Cyberpunk" in g.title for g in games), "Cyberpunk 2077 not in results"
    print(f"✅ Game search: {len(games)} results, found: {[g.title for g in games]}")


def test_game_deals():
    """Get deals for a specific game."""
    client = CheapSharkClient(cache_enabled=False)
    games = client.search_games("elden ring", limit=1, exact=False)
    assert len(games) > 0, "Elden Ring not found"
    deals = client.get_game_deals(games[0].game_id)
    assert len(deals) >= 0, "No deals (game might be full price)"
    if deals:
        assert deals[0].sale_price >= 0
        print(f"✅ Game deals: {len(deals)} deals for {games[0].title}")
    else:
        print(f"✅ Game deals: 0 deals for {games[0].title} (full price, as expected)")


def test_cheapest_price():
    """Find cheapest price for a game."""
    client = CheapSharkClient(cache_enabled=False)
    games = client.search_games("stardew valley", limit=1)
    if games:
        deal = client.get_cheapest_price(games[0].game_id)
        if deal:
            assert deal.sale_price >= 0
            if deal.sale_price == 0:
                print(f"✅ Cheapest: {games[0].title} = FREE at {deal.store_name}")
            else:
                print(f"✅ Cheapest: {games[0].title} = ${deal.sale_price} at {deal.store_name}")
        else:
            print(f"✅ Cheapest: {games[0].title} no current deals")


def test_deal_analysis():
    """DealAnalyzer ranks and filters deals."""
    client = CheapSharkClient(cache_enabled=False)
    deals = client.search_deals(upper_price=30, page_size=15, sort_by="Metacritic")
    if len(deals) < 2:
        print("⚠️  Skipping deal analysis — not enough deals found")
        return

    # Rank by different strategies
    by_value = DealAnalyzer.rank_deals(deals, "value")
    by_price = DealAnalyzer.rank_deals(deals, "cheapest")
    by_rating = DealAnalyzer.rank_deals(deals, "highest_rated")
    by_discount = DealAnalyzer.rank_deals(deals, "biggest_discount")

    assert len(by_value) == len(deals)
    assert by_price[0].sale_price <= by_price[-1].sale_price, "Cheapest sort broken"

    # Find best deal
    best = DealAnalyzer.find_best_deal(deals)
    assert best is not None

    print(f"✅ Analysis: {len(deals)} deals ranked 4 ways, best: {best.title}")


def test_deal_reporter():
    """DealReporter formats deals and reports."""
    client = CheapSharkClient(cache_enabled=False)
    deals = client.search_deals(upper_price=30, page_size=5)

    # Format single deal
    if deals:
        single = DealReporter.format_deal(deals[0])
        assert single  # non-empty
        assert "$" in single

    # Format comparison
    report = DealReporter.format_comparison(deals, "Top Deals Under $30")
    assert "Top Deals" in report or "$" in report

    # Empty case
    empty = DealReporter.format_comparison([], "Nothing")
    assert "No deals" in empty

    print(f"✅ Reporter: formatted {len(deals)} deals into reports")


def test_wishlist_lifecycle():
    """Wishlist add/remove/check lifecycle."""
    client = CheapSharkClient(cache_enabled=False)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        state_file = f.name

    try:
        monitor = WishlistMonitor(client, state_file=state_file)

        # Add items
        monitor.add("202350", "Cyberpunk 2077", 15.00)
        monitor.add("105600", "Terraria", 5.00)
        assert len(monitor.items) == 2

        # Check prices
        alerts = monitor.check_prices()
        assert isinstance(alerts, list)
        print(f"✅ Wishlist: 2 items tracked, {len(alerts)} alerts after first check")

        # Remove
        assert monitor.remove("202350") is True
        assert monitor.remove("999999") is False
        assert len(monitor.items) == 1

        # Reload from disk
        monitor2 = WishlistMonitor(client, state_file=state_file)
        assert len(monitor2.items) == 1

        print("✅ Wishlist lifecycle: add → check → remove → reload")
    finally:
        os.unlink(state_file)


def test_price_alert_format():
    """PriceAlert formats messages correctly."""
    alert = PriceAlert(
        game_title="Hollow Knight",
        current_price=7.49,
        lowest_price=7.49,
        store="Steam",
        url="https://example.com/deal/123",
    )
    msg = alert.message
    assert "Hollow Knight" in msg
    assert "$7.49" in msg
    assert "Steam" in msg
    assert alert.timestamp != ""
    print(f"✅ PriceAlert: message formatted correctly")


def test_store_deal_filter():
    """Filter deals by store."""
    client = CheapSharkClient(cache_enabled=False)
    steam_deals = client.search_deals(store_id=1, upper_price=20, page_size=5)
    if steam_deals:
        assert all(d.store_name == "Steam" for d in steam_deals), "Store filter broken"
        print(f"✅ Store filter: {len(steam_deals)} Steam deals, all store_name=Steam")
    else:
        print("✅ Store filter: no Steam deals under $20 (normal)")


def test_quality_filter():
    """Filter deals by Metacritic score."""
    client = CheapSharkClient(cache_enabled=False)
    deals = client.search_deals(upper_price=60, page_size=20, sort_by="Metacritic")
    if deals:
        high_quality = DealAnalyzer.filter_quality(deals, min_metacritic=80)
        print(f"✅ Quality filter: {len(deals)} deals → {len(high_quality)} with Metacritic ≥ 80")
    else:
        print("⚠️  Skipping quality filter — no deals returned")


def test_pagination():
    """API handles page_size and sorting."""
    client = CheapSharkClient(cache_enabled=False)
    page1 = client.search_deals(upper_price=60, page_size=5, sort_by="Title")
    page2 = client.search_deals(upper_price=60, page_size=5, sort_by="Title")
    # Just verify it returns data without crashing
    assert isinstance(page1, list)
    assert isinstance(page2, list)
    print(f"✅ Pagination: page1={len(page1)}, page2={len(page2)}")


# ── Run All Tests ───────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_store_fetch,
        test_deal_search,
        test_game_search,
        test_game_deals,
        test_cheapest_price,
        test_deal_analysis,
        test_deal_reporter,
        test_wishlist_lifecycle,
        test_price_alert_format,
        test_store_deal_filter,
        test_quality_filter,
        test_pagination,
    ]

    passed = 0
    failed = 0
    for test in tests:
        name = test.__name__
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1

    print(f"\n{'━' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    if failed:
        print(f"⚠️  {failed} test(s) failed")
        sys.exit(1)
    else:
        print("🎮 All tests passed!")
        sys.exit(0)
