"""
Tests for the AAE Claim Evaluator (Phase A — data-side verification rail).

Covers:
  - Verdict correctness on known directional claims (bottom / top calls)
  - Feed-missing fallback (each rail degrades to None, not a crash)
  - Stale-feed guard (old lastUpdated -> confidence penalty + STALE flag)
  - Input length bounds (ReDoS / resource guard on claim text)
  - Verdict schema shape (layer values surfaced for demo value)
"""
import json
import os
import sys
import unittest
from unittest import mock

# Allow running from repo root or from the package dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claim_evaluator import (
    ClaimEvaluator,
    _dir_stance,
    _parse_claim_direction,
    _regime_direction,
    _trend_direction,
    _narrative_direction,
)


# ── Fixtures ────────────────────────────────────────────────────────────

REGIME_YIELD = {
    "mode": "YIELD", "label": "YIELD / LP HARVEST", "regime": "RANGE_BOUND",
    "confidence": 0.65, "action": "HOLD", "winner": "LENDING",
    "updated_at": "Aug 06 · 11:17 UTC", "last_regime_change": False,
}
REGIME_BULL = {
    "mode": "RISK-ON / GROWTH", "regime": "BULL_TRENDING",
    "confidence": 0.8, "action": "HOLD", "updated_at": "Aug 10 · 12:00 UTC",
}
REGIME_BEAR = {
    "mode": "DEFENSIVE / YIELD", "regime": "BEAR_TRENDING",
    "confidence": 0.8, "action": "DEFENSIVE", "updated_at": "Aug 10 · 12:00 UTC",
}

ROTATION_CLEAN = {
    "lastUpdated": "2026-08-11T04:02:36Z",
    "btc": {"price": 64071.71, "change_7d": 0.52},
    "narratives": [
        {"rank": 1, "name": "DeFi Blue Chips", "score": -0.0, "zone": "Warm",
         "coins": "UNI ↑5%, AAVE ↑4%, LINK ↑2%", "sentiment_score": 1.0},
        {"rank": 2, "name": "AI & Data", "score": -8.1, "zone": "Cold",
         "coins": "FET ↓7%", "sentiment_score": -2.0},
    ],
}

ARB_STATE = {
    "last_scan": "2026-08-04T18:00:31+00:00",
    "opportunities": [
        {"symbol": "ETH", "basis_bps": 8.59, "perp": 1869.55, "spot": 1867.945},
        {"symbol": "BTC", "basis_bps": 3.1, "perp": 64000.0, "spot": 63990.0},
    ],
}

# Live BTC 30d (flat-ish). [ts, price] pairs.
PRICES_BTC_FLAT = [
    [1783900800000, 63746.65],
    [1786400000000, 64087.19],  # ~+0.5%
]
PRICES_BTC_UP = [
    [1783900800000, 50000.0],
    [1786400000000, 64087.19],  # ~+28%
]
PRICES_BTC_DOWN = [
    [1783900800000, 70000.0],
    [1786400000000, 64087.19],  # ~-8.4%
]


def _feed_map(regime=None, rotation=None, arb=None, prices=None):
    return {
        "regime": regime,
        "rotation": rotation,
        "arb": arb,
        "price": prices,
    }


class TestDirectionParsing(unittest.TestCase):
    def test_bullish_claims(self):
        for c in ["crypto bottom is in", "BTC will pump", "bottom confirmed",
                  "we are going up", "this is the low", "accumulate here"]:
            d = _parse_claim_direction(c)
            self.assertIs(d, "bull", f"{c!r} should be bull, got {d}")

    def test_bearish_claims(self):
        for c in ["top is in", "market is crashing", "dump incoming",
                  "we are going down", "sell everything", "bear market begins"]:
            d = _parse_claim_direction(c)
            self.assertIs(d, "bear", f"{c!r} should be bear, got {d}")

    def test_neutral_claims(self):
        for c in ["BTC is flat today", "market sideways", "what is the price"]:
            self.assertIsNone(_parse_claim_direction(c))


class TestLayerDirection(unittest.TestCase):
    def test_regime_direction(self):
        self.assertEqual(_regime_direction(REGIME_YIELD), "neutral")
        self.assertEqual(_regime_direction(REGIME_BULL), "bull")
        self.assertEqual(_regime_direction(REGIME_BEAR), "bear")
        self.assertIsNone(_regime_direction(None))

    def test_trend_direction(self):
        self.assertEqual(_trend_direction(0.5), "flat")
        self.assertEqual(_trend_direction(28.0), "bull")
        self.assertEqual(_trend_direction(-8.4), "bear")
        self.assertIsNone(_trend_direction(None))

    def test_narrative_direction(self):
        # Claimed asset BTC is not explicitly in a narrative list -> neutral
        self.assertEqual(_narrative_direction(ROTATION_CLEAN, "BTC"), "neutral")
        # A DeFi asset maps to the DeFi narrative -> warm -> mildly bull
        self.assertEqual(_narrative_direction(ROTATION_CLEAN, "LINK"), "bull")
        # An AI asset maps to the cold AI narrative -> bear-ish
        self.assertEqual(_narrative_direction(ROTATION_CLEAN, "FET"), "bear")
        self.assertIsNone(_narrative_direction(None, "BTC"))


class TestDirStance(unittest.TestCase):
    def test_agree(self):
        self.assertEqual(_dir_stance("bull", "bull"), "AGREE")

    def test_diverge(self):
        # claim bullish, layer neutral -> divergence, conclusion ahead of data
        self.assertEqual(_dir_stance("bull", "neutral"), "DIVERGE")

    def test_contradict(self):
        self.assertEqual(_dir_stance("bull", "bear"), "CONTRADICT")

    def test_confirm(self):
        # claim bullish AND data layer strongly supports -> CONFIRMED
        self.assertEqual(_dir_stance("bull", "bull", strong=True), "CONFIRMED")

    def test_unknown_claim(self):
        self.assertIsNone(_dir_stance(None, "bull"))


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.ev = ClaimEvaluator()

    def test_divergence_on_btc_bottom(self):
        """The spec's canonical example: bottom call on BTC while regime is
        RANGE_BOUND and BTC 30d is flat -> DIVERGE / HOLD."""
        feeds = _feed_map(
            regime=REGIME_YIELD,
            rotation=ROTATION_CLEAN,
            arb=ARB_STATE,
            prices=PRICES_BTC_FLAT,
        )
        verdict = self.ev.evaluate("crypto bottom is in", "BTC", feeds=feeds)
        self.assertEqual(verdict["verdict"], "DIVERGE")
        self.assertEqual(verdict["action"], "HOLD")
        self.assertIn("layers", verdict)          # demo value surfaced
        self.assertIn("regime", verdict["layers"])

    def test_confirmed_on_bull_trend(self):
        """Bull claim + BULL_TRENDING regime + strong up-trend -> CONFIRMED."""
        feeds = _feed_map(
            regime=REGIME_BULL,
            rotation=ROTATION_CLEAN,
            arb=ARB_STATE,
            prices=PRICES_BTC_UP,
        )
        verdict = self.ev.evaluate("bottom is in", "BTC", feeds=feeds)
        self.assertEqual(verdict["verdict"], "CONFIRMED")
        self.assertEqual(verdict["action"], "ACCUM")

    def test_contradict_on_bear_trend(self):
        """Bull claim + BEAR_TRENDING + down-trend -> CONTRADICT / DEFENSIVE."""
        feeds = _feed_map(
            regime=REGIME_BEAR,
            rotation=ROTATION_CLEAN,
            arb=ARB_STATE,
            prices=PRICES_BTC_DOWN,
        )
        verdict = self.ev.evaluate("bottom is in", "BTC", feeds=feeds)
        self.assertEqual(verdict["verdict"], "CONTRADICT")
        self.assertEqual(verdict["action"], "DEFENSIVE")

    def test_feed_missing_falls_back_to_none(self):
        """A missing rail must not crash the whole evaluation."""
        feeds = _feed_map(regime=None, rotation=None, arb=None, prices=None)
        verdict = self.ev.evaluate("crypto bottom is in", "BTC", feeds=feeds)
        self.assertEqual(verdict["verdict"], "UNKNOWN")
        self.assertEqual(verdict["action"], "NEUTRAL")
        # No rails available -> all layer values None
        self.assertTrue(verdict["layers"]["regime"] is None)
        self.assertTrue(verdict["layers"]["price_trend"] is None)

    def test_individual_rail_failure(self):
        """One bad feed doesn't prevent the others from loading."""
        feeds = _feed_map(
            regime="this is not valid json",     # broken rail
            rotation=ROTATION_CLEAN,
            arb=ARB_STATE,
            prices=PRICES_BTC_FLAT,
        )
        verdict = self.ev.evaluate("crypto bottom is in", "BTC", feeds=feeds)
        # regime degraded to None, but others still loaded
        self.assertIsNone(verdict["layers"]["regime"])
        self.assertIsNotNone(verdict["layers"]["narrative"])
        self.assertEqual(verdict["verdict"], "DIVERGE")

    def test_input_length_bounds(self):
        """Over-long claim text is rejected, not processed (resource guard)."""
        long_claim = "bottom " * 100000  # ~600KB
        with self.assertRaises(ValueError):
            self.ev.evaluate(long_claim, "BTC")

    def test_stale_feed_flag(self):
        """Old rotation timestamp -> confidence penalty + STALE flag surfaced."""
        stale_rotation = dict(ROTATION_CLEAN)
        stale_rotation["lastUpdated"] = "2026-07-01T00:00:00Z"  # ~41 days old
        feeds = _feed_map(regime=REGIME_YIELD, rotation=stale_rotation,
                          arb=ARB_STATE, prices=PRICES_BTC_FLAT)
        verdict = self.ev.evaluate("crypto bottom is in", "BTC", feeds=feeds)
        self.assertTrue(verdict["layers"]["narrative"]["stale"])
        # confidence reflects the penalty
        self.assertLess(verdict["confidence"], 0.65)


class TestFileLoading(unittest.TestCase):
    def test_loads_from_disk_regime(self):
        ev = ClaimEvaluator(
            regime_file="/root/.hermes/profiles/gentech/scripts/.clarity-mode-state.json"
        )
        r = ev._load_regime()
        self.assertIsInstance(r, dict)
        self.assertIn("mode", r)

    def test_loads_from_disk_arb(self):
        ev = ClaimEvaluator(
            arb_file="/root/.hermes/profiles/gentech/scripts/.gta-arb-state.json"
        )
        a = ev._load_arb()
        self.assertIsInstance(a, dict)
        self.assertIn("opportunities", a)

    def test_missing_file_returns_none(self):
        ev = ClaimEvaluator(
            regime_file="/nonexistent/regime.json",
            arb_file="/nonexistent/arb.json",
        )
        self.assertIsNone(ev._load_regime())
        self.assertIsNone(ev._load_arb())


if __name__ == "__main__":
    unittest.main(verbosity=2)
