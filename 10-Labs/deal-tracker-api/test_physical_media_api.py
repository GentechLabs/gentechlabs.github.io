"""Tests for the GenTech Physical Media Scarcity Tracker.

Tests the module logic (search, leaderboard, watch state machine, title add)
without network calls. Uses temp files for persistence.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from api import physical_media  # noqa: E402


def setup_function():
    tmpdir = tempfile.mkdtemp()
    physical_media.DATA_DIR = tmpdir
    physical_media.CATALOG_FILE = os.path.join(tmpdir, "catalog.json")
    physical_media.WATCH_FILE = os.path.join(tmpdir, "watch.json")


def test_search_returns_catalog():
    r = physical_media.search()
    assert r["count"] >= 1
    assert "items" in r
    # Sorted by scarcity desc — PS5 post-2028 should be near top
    assert r["items"][0]["scarcity_score"] >= 70


def test_search_filters_by_title():
    r = physical_media.search("Interstellar")
    assert r["count"] == 1
    assert r["items"][0]["title"] == "Interstellar (10th Anniversary)"


def test_search_no_match():
    r = physical_media.search("Nonexistent Title XYZ")
    assert r["count"] == 0
    assert r["items"] == []


def test_scarcity_leaderboard():
    r = physical_media.scarcity_leaderboard(limit=3)
    assert r["count"] == 3
    scores = [i["scarcity_score"] for i in r["items"]]
    assert scores == sorted(scores, reverse=True)


def test_add_watch_create_and_check():
    w = physical_media.add_watch("Interstellar (10th Anniversary)", 50)
    assert w["status"] == "created"
    assert w["watch"]["target_score"] == 50
    assert w["watch"]["current_score"] == 55

    # Update path
    w2 = physical_media.add_watch("Interstellar (10th Anniversary)", 60)
    assert w2["status"] == "updated"
    assert w2["watch"]["target_score"] == 60

    check = physical_media.check_watches()
    assert check["count"] == 1
    assert check["watches"][0]["title"] == "Interstellar (10th Anniversary)"


def test_add_watch_unknown_title():
    w = physical_media.add_watch("Not In Catalog", 70)
    assert w["status"] == "error"


def test_add_watch_alert_fires():
    # PS5 post-2028 is scarcity 80; target 70 → alert fires
    w = physical_media.add_watch("PlayStation 5 Physical Game (Post-2028)", 70)
    assert w["status"] == "created"
    check = physical_media.check_watches()
    assert len(check["alerts"]) == 1
    assert check["alerts"][0]["alert"] is True


def test_add_title():
    r = physical_media.add_title("Test Boutique Release", "4K UHD", "Test Label", 59.99, 85)
    assert r["status"] == "created"
    assert r["item"]["scarcity"] == 85
    assert r["item"]["status"] == "scarce"

    # Duplicate rejected
    r2 = physical_media.add_title("Test Boutique Release", "4K UHD", "Test Label", 59.99, 85)
    assert r2["status"] == "error"


def test_add_title_clamps_score():
    r = physical_media.add_title("Clamp Test", "Vinyl LP", "Test", 20.0, 150)
    assert r["item"]["scarcity"] == 100
    r2 = physical_media.add_title("Clamp Test 2", "Vinyl LP", "Test", 20.0, -5)
    assert r2["item"]["scarcity"] == 0
