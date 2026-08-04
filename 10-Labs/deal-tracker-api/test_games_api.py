"""Tests for the GenTech Games API (deal-tracker-api).

These test the module logic (preorder advisor, release radar, price-watch
state machine) without hammering CheapShark on every run. The live network
deals path is smoke-tested once separately (see test_search_deals_live).
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from api import games  # noqa: E402


def setup_function():
    games.WATCH_FILE = tempfile.mktemp(suffix=".json")


def test_preorder_advisor_gears():
    r = games.preorder_advisor("Gears of War: E-Day")
    assert r["verdict"] == "WAIT"
    assert r["confidence"] == "high"
    assert "wait_for_open_beta" in r["recommend"]
    assert len(r["reasons"]) >= 3


def test_preorder_advisor_unknown():
    r = games.preorder_advisor("Some Unknown Game 2077")
    assert r["verdict"] == "UNKNOWN"
    assert r["confidence"] == "low"


def test_release_radar():
    r = games.release_radar()
    assert r["count"] >= 1
    titles = [i["title"] for i in r["items"]]
    assert "Gears of War: E-Day" in titles


def test_price_watch_create_and_check():
    w = games.add_price_watch("Gears 5", 9.99)
    assert w["status"] == "created"
    assert w["watch"]["target_price"] == 9.99
    assert w["watch"]["status"] == "tracking"

    # Update path
    w2 = games.add_price_watch("Gears 5", 5.00)
    assert w2["status"] == "updated"
    assert w2["watch"]["target_price"] == 5.00

    check = games.check_price_watches()
    assert check["count"] == 1
    assert check["watches"][0]["title"] == "Gears 5"


def test_price_watch_dedupe():
    games.add_price_watch("Halo", 15.0)
    games.add_price_watch("Halo", 10.0)
    check = games.check_price_watches()
    assert check["count"] == 1


def test_search_deals_shape():
    # No network: empty query returns empty list shape (function still returns dict)
    r = games.search_deals("")
    assert "query" in r
    assert "count" in r
    assert "deals" in r
