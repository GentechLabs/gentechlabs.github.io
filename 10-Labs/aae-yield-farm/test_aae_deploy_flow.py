"""Tests for AAE Yield Farm — Config-First Deploy Flow."""
import json
import os
import tempfile
import pytest
from aae_deploy_flow import (
    YieldFarmConfig,
    FeeProjection,
    render_preview_card,
    write_config,
    read_config,
    verify_position,
    VerificationResult,
)


class TestYieldFarmConfig:
    def test_valid_config(self):
        cfg = YieldFarmConfig(
            shape="CURVE",
            range_low=6.40,
            range_high=6.55,
            entry_price=6.48,
            amount_usd=24.42,
        )
        assert cfg.validate() == []

    def test_invalid_shape(self):
        cfg = YieldFarmConfig(shape="INVALID", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=100)
        errors = cfg.validate()
        assert any("Shape" in e for e in errors)

    def test_range_low_above_high(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=7.0, range_high=6.0, entry_price=6.5, amount_usd=100)
        errors = cfg.validate()
        assert any("low" in e and "high" in e for e in errors)

    def test_entry_outside_range(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.0, range_high=7.0, entry_price=7.5, amount_usd=100)
        errors = cfg.validate()
        assert any("within range" in e for e in errors)

    def test_negative_amount(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=-10)
        errors = cfg.validate()
        assert any("Amount" in e for e in errors)

    def test_bid_ask_is_valid(self):
        cfg = YieldFarmConfig(shape="BID-ASK", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=100)
        assert cfg.validate() == []

    def test_case_insensitive_shape(self):
        cfg = YieldFarmConfig(shape="curve", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=100)
        assert cfg.validate() == []

    def test_invalid_pool_address(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=100, pool_address="not-a-valid-address")
        errors = cfg.validate()
        assert any("Pool" in e for e in errors)

    def test_to_dict_roundtrip(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.40, range_high=6.55, entry_price=6.48, amount_usd=24.42)
        d = cfg.to_dict()
        restored = YieldFarmConfig.from_dict(d)
        assert restored.shape == cfg.shape
        assert restored.range_low == cfg.range_low
        assert restored.amount_usd == cfg.amount_usd


class TestFeeProjection:
    def test_in_range_estimate(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=100)
        fees = FeeProjection.estimate(cfg, pool_volume_24h=1_000_000, pool_liquidity=500_000, current_price=6.5)
        assert fees.daily_fees_usd > 0
        assert fees.estimated_apr_pct > 0
        assert fees.position_share_pct == 0.02  # 100 / 500000 = 0.0002 = 0.02%

    def test_out_of_range_estimate(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=100)
        fees = FeeProjection.estimate(cfg, pool_volume_24h=1_000_000, pool_liquidity=500_000, current_price=8.0)
        assert fees.daily_fees_usd == 0.0
        assert fees.estimated_apr_pct == 0.0

    def test_zero_liquidity(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=100)
        fees = FeeProjection.estimate(cfg, pool_volume_24h=1_000_000, pool_liquidity=0, current_price=6.5)
        assert fees.position_share_pct == 0.0
        assert fees.daily_fees_usd == 0.0


class TestPreviewCard:
    def test_render_preview_card(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.40, range_high=6.55, entry_price=6.48, amount_usd=24.42)
        fees = FeeProjection(daily_fees_usd=0.06, estimated_apr_pct=8.0, daily_volume_usd=918000, pool_liquidity_usd=397000, position_share_pct=0.006)
        card = render_preview_card(cfg, fees, wallet_balance=36.63)
        assert "CURVE" in card
        assert "$6.40" in card
        assert "$6.55" in card
        assert "$24.42" in card
        assert "0.0600" in card or "0.06" in card
        assert "8.0%" in card


class TestConfigIO:
    def test_write_and_read_config(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.40, range_high=6.55, entry_price=6.48, amount_usd=24.42)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            write_config(cfg, path)
            restored = read_config(path)
            assert restored is not None
            assert restored.shape == cfg.shape
            assert restored.amount_usd == cfg.amount_usd
        finally:
            os.unlink(path)

    def test_read_nonexistent_config(self):
        assert read_config("/nonexistent/path.json") is None

    def test_read_corrupt_config(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json")
            path = f.name
        try:
            assert read_config(path) is None
        finally:
            os.unlink(path)


class TestVerification:
    def test_verify_pass(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.40, range_high=6.55, entry_price=6.48, amount_usd=24.42)
        onchain = {
            "shape": "CURVE",
            "range_low": 6.40,
            "range_high": 6.55,
            "totalValue": 24.42,
        }
        result = verify_position(cfg, onchain)
        assert result.passed
        assert result.mismatches == []

    def test_verify_shape_mismatch(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.40, range_high=6.55, entry_price=6.48, amount_usd=24.42)
        onchain = {
            "shape": "BID-ASK",
            "range_low": 6.40,
            "range_high": 6.55,
            "totalValue": 24.42,
        }
        result = verify_position(cfg, onchain)
        assert not result.passed
        assert any("Shape" in m for m in result.mismatches)

    def test_verify_range_mismatch(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.40, range_high=6.55, entry_price=6.48, amount_usd=24.42)
        onchain = {
            "shape": "CURVE",
            "range_low": 6.80,
            "range_high": 7.00,
            "totalValue": 24.42,
        }
        result = verify_position(cfg, onchain)
        assert not result.passed
        assert any("Range" in m for m in result.mismatches)

    def test_verify_with_nested_onchain(self):
        """Test with defi-data.json style nested structure."""
        cfg = YieldFarmConfig(shape="BID-ASK", range_low=6.78, range_high=7.00, entry_price=6.90, amount_usd=45.24)
        onchain = {
            "lpPosition": {
                "shape": "bid-ask",
                "rangeMin": 6.7861,
                "rangeMax": 7.0067,
                "totalValueUSD": 45.24,
            }
        }
        # Flatten for our verifier
        flat = onchain["lpPosition"]
        flat["range_low"] = flat.pop("rangeMin")
        flat["range_high"] = flat.pop("rangeMax")
        result = verify_position(cfg, flat)
        assert result.passed

    def test_verify_amount_mismatch(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.40, range_high=6.55, entry_price=6.48, amount_usd=24.42)
        onchain = {
            "shape": "CURVE",
            "range_low": 6.40,
            "range_high": 6.55,
            "totalValue": 50.00,
        }
        result = verify_position(cfg, onchain)
        assert not result.passed
        assert any("Amount" in m for m in result.mismatches)

    def test_verify_bool_coercion(self):
        cfg = YieldFarmConfig(shape="CURVE", range_low=6.0, range_high=7.0, entry_price=6.5, amount_usd=100)
        onchain_pass = {"shape": "CURVE", "range_low": 6.0, "range_high": 7.0, "totalValue": 100}
        onchain_fail = {"shape": "BID-ASK", "range_low": 6.0, "range_high": 7.0, "totalValue": 100}
        assert bool(verify_position(cfg, onchain_pass)) is True
        assert bool(verify_position(cfg, onchain_fail)) is False
