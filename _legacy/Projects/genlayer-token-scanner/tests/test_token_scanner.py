# { "Depends": "py-genlayer:test" }

"""
Tests for Token Scanner Intelligent Contract.
Run with: gltest (requires GenLayer Studio running)
"""

import json
import pytest
from genlayer import *


class TestTokenScanner:
    """Integration tests for the TokenScanner contract."""

    @pytest.fixture
    def scanner(self, deployed_contract):
        """Get the deployed TokenScanner contract instance."""
        return deployed_contract

    def test_initial_state(self, scanner):
        """Contract should start with zero scans."""
        result = scanner.get_total_scans()
        assert result == 0

    def test_scan_known_token(self, scanner):
        """Scanning a known token should return valid assessment."""
        # USDC on Ethereum mainnet
        result = scanner.scan_token("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

        assert "risk_score" in result
        assert "risk_level" in result
        assert 0 <= result["risk_score"] <= 100
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert result["token_symbol"] == "USDC"
        print(f"   ✅ USDC scored {result['risk_score']}/100 ({result['risk_level']})")

    def test_scan_returns_risk_factors(self, scanner):
        """Assessment should include risk factors list."""
        result = scanner.scan_token("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

        assert "risk_factors" in result
        assert isinstance(result["risk_factors"], list)
        print(f"   ✅ Risk factors: {result['risk_factors']}")

    def test_get_assessment(self, scanner):
        """Should retrieve stored assessment by token address."""
        token_addr = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        scanner.scan_token(token_addr)

        assessment = scanner.get_assessment(token_addr)
        assert assessment["token_address"] == token_addr
        assert "risk_score" in assessment
        assert "scan_timestamp" in assessment
        print(f"   ✅ Assessment retrieved: {assessment['risk_level']}")

    def test_scan_count_increments(self, scanner):
        """Each scan should increment the total count."""
        token_addr = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

        scanner.scan_token(token_addr)
        count1 = scanner.get_total_scans()

        scanner.scan_token(token_addr)
        count2 = scanner.get_total_scans()

        assert count2 == count1 + 1
        print(f"   ✅ Scan count: {count1} → {count2}")

    def test_is_safe_check(self, scanner):
        """is_safe should return True for safe tokens."""
        token_addr = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        scanner.scan_token(token_addr)

        # USDC should be safe
        assert scanner.is_safe(token_addr) == True
        print("   ✅ USDC classified as safe")

    def test_is_honeypot_check(self, scanner):
        """is_honeypot should return False for legitimate tokens."""
        token_addr = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        scanner.scan_token(token_addr)

        assert scanner.is_honeypot(token_addr) == False
        print("   ✅ USDC not classified as honeypot")

    def test_get_risk_level(self, scanner):
        """get_risk_level should return proper classification."""
        token_addr = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        scanner.scan_token(token_addr)

        level = scanner.get_risk_level(token_addr)
        assert level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        print(f"   ✅ Risk level: {level}")

    def test_unscanned_token(self, scanner):
        """Unscanned token should return appropriate defaults."""
        assert scanner.is_safe("0x0000000000000000000000000000000000000001") == False
        assert scanner.is_honeypot("0x0000000000000000000000000000000000000001") == False
        assert scanner.get_risk_level("0x0000000000000000000000000000000000000001") == "NOT_SCANNED"
        print("   ✅ Unscanned token returns correct defaults")

    def test_batch_scan(self, scanner):
        """Batch scan should process multiple tokens."""
        tokens = [
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        ]
        results = scanner.scan_batch(tokens)

        assert len(results) == 2
        for r in results:
            assert "risk_score" in r
            assert "risk_level" in r
        print(f"   ✅ Batch scan: {len(results)} tokens assessed")

    def test_get_all_assessments(self, scanner):
        """Should return all stored assessments."""
        scanner.scan_token("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

        all_assessments = scanner.get_all_assessments()
        assert len(all_assessments) >= 1
        print(f"   ✅ Total assessments stored: {len(all_assessments)}")
