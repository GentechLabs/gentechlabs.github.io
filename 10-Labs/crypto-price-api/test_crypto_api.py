"""Tests for the fixed Crypto Price API (no network in unit tests)."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from api import server  # noqa: E402


def test_stablecoin_peg():
    """USDC/USDT/DAI should return ~$1.00 via the stablecoin fast-path."""
    r = server._fetch_coingecko("USDC")
    assert r is not None and abs(r - 1.00) < 0.05


def test_cmc_key_loader():
    """CMC key should load from the config file."""
    key = server._load_cmc_key()
    assert key, "expected a CMC API key"


def test_coingecko_fallback_fails_gracefully():
    """When CMC is forced to fail, fallback should return None not crash."""
    original = server._fetch_cmc
    server._fetch_cmc = lambda s, k: (_ for _ in ()).throw(Exception("forced"))
    try:
        r = server._get_price("DEFINITELY_NOT_A_COIN_XYZ")
        # May return coingecko None; should not raise
        assert isinstance(r, dict)
    finally:
        server._fetch_cmc = original
