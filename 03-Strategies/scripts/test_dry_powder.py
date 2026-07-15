#!/usr/bin/env python3
"""Tests for Dry Powder Mode — Crash Detection & Decision Engine.

Run: pytest test_dry_powder.py -v
"""

from dry_powder_engine import CrashDetector

# ── Default config (matches engine defaults) ─────────────────────────────────

DEFAULT_CFG = {
    "mode": "advisory",
    "crash_threshold": 50,
    "recovery_threshold": 60,
    "min_withdraw_usd": 50,
    "max_withdraw_pct": 100,
    "stable_target": "USDC",
    "chain": "avalanche",
    "price_drop_5min_threshold": -3.0,
    "price_drop_1h_threshold": -8.0,
    "volatility_spike_threshold": 2.0,
    "rsi_recovery_threshold": 35,
}


def make_detector(**overrides):
    cfg = dict(DEFAULT_CFG)
    cfg.update(overrides)
    return CrashDetector(cfg)


# ═══════════════════════════════════════════════════════════════════════════════
# Crash Detection Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestScoreCrash:
    """score_crash() — weighted crash score 0–100, signal SAFE/WATCH/CRASH"""

    def test_safe_signal(self):
        """Stable prices should produce SAFE (score < 25)"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 10.0, "change_24h": 0.5},
            volatility=0.01,
            price_history_5min=[9.99, 10.01, 10.00],
            price_history_1h=[9.95, 10.05, 10.00],
        )
        assert result["signal"] == "SAFE"
        assert result["score"] < 25

    def test_watch_signal(self):
        """Moderate drop should produce WATCH (score 25–49)"""
        det = make_detector(crash_threshold=50)
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 9.2, "change_24h": -6.0},
            volatility=0.04,
            price_history_5min=[9.80, 9.50, 9.20],
            price_history_1h=[10.0, 9.6, 9.2],
        )
        assert result["signal"] == "WATCH", f"Expected WATCH got {result['signal']} ({result['score']})"
        assert 20 <= result["score"] <= 54

    def test_crash_signal(self):
        """Sharp price drop should produce CRASH (score >= 50)"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 8.50, "change_24h": -15.0},
            volatility=0.12,
            price_history_5min=[9.50, 8.90, 8.50],
            price_history_1h=[10.50, 9.50, 8.50],
        )
        assert result["signal"] == "CRASH", f"Expected CRASH got {result['signal']} ({result['score']})"
        assert result["score"] >= 50

    def test_max_score_high_under_extreme_drop(self):
        """Even extreme drops should produce very high score (engine caps at 85)"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 1.0, "change_24h": -90.0},
            volatility=0.50,
            price_history_5min=[10.0, 5.0, 1.0],
            price_history_1h=[20.0, 10.0, 1.0],
        )
        assert result["score"] >= 80

    def test_returns_factors_list(self):
        """Factors list should contain all triggered factor details"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 8.0, "change_24h": -20.0},
            volatility=0.15,
            price_history_5min=[9.0, 8.50, 8.0],
            price_history_1h=[10.0, 9.0, 8.0],
        )
        assert isinstance(result["factors"], list)
        assert len(result["factors"]) > 0
        for f in result["factors"]:
            assert "factor" in f
            assert "score" in f
            assert "max" in f
            assert 0 <= f["score"] <= f["max"]

    def test_small_fluctuation_is_safe(self):
        """Normal market noise (<1% drop) should not trigger anything"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 10.0, "change_24h": -1.0},
            volatility=0.015,
            price_history_5min=[10.05, 10.02, 10.00],
            price_history_1h=[10.10, 10.05, 10.00],
        )
        assert result["signal"] == "SAFE"

    def test_consecutive_negative_candles_contributes(self):
        """4 consecutive negative 5min candles should add factor score"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 9.0, "change_24h": -8.0},
            volatility=0.06,
            price_history_5min=[10.0, 9.7, 9.4, 9.0],
            price_history_1h=[10.0, 9.5, 9.0],
        )
        factors = {f["factor"]: f for f in result["factors"]}
        assert "negative_candle_streak" in factors

    def test_insufficient_history_graceful(self):
        """Less than 2 prices in 5min history should not crash"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 10.0, "change_24h": 0.0},
            volatility=0.01,
            price_history_5min=[10.0],  # Only 1 point
            price_history_1h=[10.0],
        )
        assert result["signal"] == "SAFE"
        assert result["score"] >= 0


# ═══════════════════════════════════════════════════════════════════════════════
# Recovery Detection Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestScoreRecovery:
    """score_recovery() — recovery score 0–100"""

    def test_still_crashed(self):
        """Price still dropping → STILL_CRASHED"""
        det = make_detector()
        result = det.score_recovery(
            price_info={"symbol": "AVAX", "price": 8.0, "change_24h": -12.0},
            current_rsi=25,
        )
        assert result["signal"] == "STILL_CRASHED"
        assert result["score"] < 30

    def test_recovering(self):
        """Price stabilizing after crash — still in recovery zone"""
        det = make_detector()
        result = det.score_recovery(
            price_info={"symbol": "AVAX", "price": 9.0, "change_24h": -4.0,
                        "low_24h": 8.2},
            current_rsi=36,
        )
        assert result["signal"] == "RECOVERING", f"Expected RECOVERING got {result['signal']} ({result['score']})"

    def test_safe_to_redeploy(self):
        """Price recovered strongly → SAFE_TO_REDEPLOY"""
        det = make_detector()
        result = det.score_recovery(
            price_info={"symbol": "AVAX", "price": 11.0, "change_24h": 2.0,
                        "low_24h": 8.0},
            current_rsi=55,
        )
        assert result["signal"] == "SAFE_TO_REDEPLOY", f"Expected SAFE_TO_REDEPLOY got {result['signal']} ({result['score']})"
        assert result["score"] >= 60

    def test_max_score_high_under_full_recovery(self):
        """Full recovery should produce high score"""
        det = make_detector()
        result = det.score_recovery(
            price_info={"symbol": "AVAX", "price": 20.0, "change_24h": 5.0,
                        "low_24h": 8.0},
            current_rsi=75,
        )
        assert result["score"] >= 80

    def test_low_rsi_alone_not_enough(self):
        """Low RSI without price stability should stay crashed"""
        det = make_detector()
        result = det.score_recovery(
            price_info={"symbol": "AVAX", "price": 8.0, "change_24h": -15.0,
                        "low_24h": 7.5},
            current_rsi=32,  # Above threshold but price still dropping
        )
        assert result["signal"] == "STILL_CRASHED"


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge cases and robustness"""

    def test_empty_price_history_does_not_crash(self):
        """Empty price lists should not raise exceptions"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 10.0, "change_24h": 0.0},
            volatility=0.01,
            price_history_5min=[],
            price_history_1h=[],
        )
        assert result["score"] == 0
        assert result["signal"] == "SAFE"

    def test_zero_volatility_does_not_crash(self):
        """Zero volatility should be handled gracefully"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 10.0, "change_24h": 0.0},
            volatility=0.0,
            price_history_5min=[10.0, 10.0, 10.0],
            price_history_1h=[10.0, 10.0, 10.0],
        )
        assert result["signal"] == "SAFE"

    def test_negative_price_does_not_break_scoring(self):
        """Price near zero should not cause math errors — produces high score"""
        det = make_detector()
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 0.01, "change_24h": -99.0},
            volatility=0.80,
            price_history_5min=[1.0, 0.10, 0.01],
            price_history_1h=[3.0, 0.50, 0.01],
        )
        assert result["score"] >= 80
        assert result["signal"] == "CRASH"

    def test_custom_thresholds(self):
        """Lower crash threshold should trigger CRASH sooner with strong drop"""
        det = make_detector(crash_threshold=30)
        result = det.score_crash(
            price_info={"symbol": "AVAX", "price": 8.5, "change_24h": -12.0},
            volatility=0.06,
            price_history_5min=[9.80, 9.10, 8.50],
            price_history_1h=[10.50, 9.50, 8.50],
        )
        assert result["signal"] == "CRASH", f"Expected CRASH at threshold 30, got {result['signal']}"

    def test_custom_recovery_threshold(self):
        """Lower recovery threshold should trigger SAFE_TO_REDEPLOY sooner"""
        det = make_detector(recovery_threshold=40)
        result = det.score_recovery(
            price_info={"symbol": "AVAX", "price": 10.0, "change_24h": 0.5,
                        "low_24h": 9.0},
            current_rsi=45,
        )
        assert result["signal"] == "SAFE_TO_REDEPLOY"
