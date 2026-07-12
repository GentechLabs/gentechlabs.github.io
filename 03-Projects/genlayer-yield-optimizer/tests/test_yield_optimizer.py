# { "Depends": "py-genlayer:test" }

"""
Tests for DeFi Yield Optimizer Intelligent Contract.
Run with: gltest (requires GenLayer Studio running)
"""

import pytest
from genlayer import *


class TestYieldOptimizer:
    """Integration tests for the YieldOptimizer contract."""

    @pytest.fixture
    def optimizer(self, deployed_contract):
        """Get the deployed YieldOptimizer contract instance."""
        return deployed_contract

    def test_initial_state(self, optimizer):
        """Contract should start with zero state."""
        stats = optimizer.get_total_stats()
        assert stats["total_rebalances"] == 0
        assert stats["total_gas_deposited_eth"] == 0.0
        assert stats["active_vaults"] == 0
        print("   ✅ Initial state correct")

    def test_scan_yields(self, optimizer):
        """Should fetch yield data from DeFi Llama."""
        result = optimizer.scan_yields("")

        assert result["status"] == "success"
        assert result["pools_fetched"] > 0
        assert result["pools_cached"] > 0
        assert len(result["top_yields"]) > 0
        assert result["top_yields"][0]["apy"] > 0
        print(f"   ✅ Fetched {result['pools_fetched']} pools, cached {result['pools_cached']}")

    def test_scan_yields_filtered(self, optimizer):
        """Should filter yields by protocol."""
        result = optimizer.scan_yields("aave")

        assert result["status"] == "success"
        assert result["protocol_filter"] == "aave"
        # All returned pools should be Aave
        for pool in result["top_yields"]:
            assert "aave" in pool["protocol"].lower()
        print(f"   ✅ Filtered to {result['pools_fetched']} Aave pools")

    def test_yield_comparison(self, optimizer):
        """Should return cached yield comparison."""
        optimizer.scan_yields("")
        comparison = optimizer.get_yield_comparison()

        assert comparison["cached_pools"] > 0
        assert comparison["protocol_count"] > 0
        assert len(comparison["protocols"]) > 0
        # Protocols should be sorted by best APY
        protocols = comparison["protocols"]
        for i in range(len(protocols) - 1):
            assert protocols[i]["best_apy"] >= protocols[i + 1]["best_apy"]
        print(f"   ✅ {comparison['protocol_count']} protocols tracked, {comparison['cached_pools']} pools cached")

    def test_get_recommendation_no_position(self, optimizer):
        """Should get recommendation without existing position."""
        result = optimizer.get_recommendation()

        assert result["status"] == "success"
        assert "recommendation" in result
        assert "best_yield" in result
        assert result["best_yield"] > 0
        assert result["gas_status"] == "no_vault"
        print(f"   ✅ Best yield: {result['best_yield']}%, recommendation available")

    def test_get_recommendation_with_position(self, optimizer):
        """Should get recommendation with existing position context."""
        result = optimizer.get_recommendation(
            current_protocol="aave",
            current_pool="test-pool-id",
            current_chain="ethereum",
            current_apy=3.5,
            value_usd=10000.0,
        )

        assert result["status"] == "success"
        assert "recommendation" in result
        # Should show improvement potential
        assert "improvement_pct" in result
        print(f"   ✅ Current: {result['current_yield']}%, Best: {result['best_yield']}%")

    def test_gas_status_no_vault(self, optimizer):
        """Should return no vault status for new user."""
        status = optimizer.get_gas_status()

        assert status["has_vault"] is False
        assert "No gas vault" in status["message"]
        print("   ✅ No vault returns correct status")

    def test_total_stats(self, optimizer):
        """Should return global statistics."""
        optimizer.scan_yields("")
        stats = optimizer.get_total_stats()

        assert "total_rebalances" in stats
        assert "active_vaults" in stats
        assert "cached_pools" in stats
        assert stats["cached_pools"] > 0
        print(f"   ✅ Stats: {stats['cached_pools']} pools, {stats['active_vaults']} vaults")

    def test_yield_data_structure(self, optimizer):
        """Yield data should have correct structure."""
        result = optimizer.scan_yields("")

        for pool in result["top_yields"]:
            assert "protocol" in pool
            assert "symbol" in pool
            assert "chain" in pool
            assert "apy" in pool
            assert "tvl_usd" in pool
            assert "stablecoin" in pool
            assert pool["apy"] > 0
            assert pool["tvl_usd"] > 0
        print("   ✅ All yield data has correct structure")

    def test_protocol_risk_scores(self, optimizer):
        """Known protocols should have correct risk scores."""
        comparison = optimizer.get_yield_comparison()

        risk_map = {}
        for proto in comparison["protocols"]:
            risk_map[proto["protocol"].lower()] = proto["risk_score"]

        # Blue-chip protocols should have high scores
        if "aave" in risk_map:
            assert risk_map["aave"] >= 80
        if "compound" in risk_map:
            assert risk_map["compound"] >= 80
        if "curve" in risk_map:
            assert risk_map["curve"] >= 70

        print(f"   ✅ Risk scores validated: {list(risk_map.keys())[:5]}")
