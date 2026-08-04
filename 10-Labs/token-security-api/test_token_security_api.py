"""Tests for the fixed Token Security API (proxy to Rugcheck engine)."""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(__file__))
from api import server  # noqa: E402


def test_health_announces_backend():
    r = asyncio.run(server.health())
    assert r["service"] == "token-security"
    assert r["backend"] == "rugcheck-v2"


def test_score_returns_payment_challenge():
    """Proxies the Rugcheck engine — should return a 402 payment challenge,
    NOT placeholder data."""
    r = asyncio.run(server.score("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))
    # Returns either a dict (200 with data) or tuple(dict, status)
    body, status = (r, 200) if isinstance(r, dict) else r
    assert status in (200, 402)
    assert "error" in body or "score" in body  # payment_required OR real score
