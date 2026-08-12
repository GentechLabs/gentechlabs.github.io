#!/usr/bin/env python3
"""
Test suite for the Avalanche Bridge Adapter (Base → Avalanche USDC rail).

Verifies:
1. Live quote from Across API (Base→Avalanche USDC) — real network call.
2. Fee math correctness (fee_pct, fee_amount, output_amount, GenTech fee).
3. EVM→bytes32 conversion.
4. Fallback estimate when API is unreachable.
5. Config bridge_fee_bps loading.

Run: python3 test_avax_bridge.py
"""

import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from avax_bridge_adapter import AvalancheBridgeAdapter, BridgeQuote


class TestAvaxBridgeAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = AvalancheBridgeAdapter()

    def test_evm_to_bytes32(self):
        """EVM address → left-padded bytes32."""
        addr = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
        b = self.adapter._evm_to_bytes32(addr)
        self.assertEqual(len(b), 32)
        # First 12 bytes zero-padded, last 20 = address
        self.assertEqual(b[:12], b"\x00" * 12)
        self.assertEqual(b[12:].hex(), addr.lower().replace("0x", ""))

    def test_bridge_fee_bps_loaded(self):
        """bridge_fee_bps loads from vault config (default 20)."""
        self.assertEqual(self.adapter.bridge_fee_bps, 20)

    def test_estimate_quote_math(self):
        """Fallback estimate fee math is correct."""
        q = self.adapter._estimate_quote(1_000_000)  # $1.00
        self.assertEqual(q.protocol, "across")
        self.assertEqual(q.source_chain, "base")
        self.assertEqual(q.destination_chain, "avalanche")
        # 0.08% of $1.00 = 800 units
        self.assertEqual(q.fee_amount, 800)
        self.assertAlmostEqual(q.fee_pct, 0.08, places=4)
        # GenTech fee = 20 bps = 0.20% = 2000 units
        self.assertEqual(q.gen_tech_fee, 2000)
        self.assertEqual(q.output_amount, 1_000_000 - 800)
        self.assertEqual(q.source, "estimate")

    def test_estimate_quote_zero_amount(self):
        """Zero amount doesn't divide by zero."""
        q = self.adapter._estimate_quote(0)
        self.assertEqual(q.fee_pct, 0.0)
        self.assertEqual(q.fee_amount, 0)

    def test_live_quote(self):
        """Live Across API quote for Base→Avalanche USDC (real network)."""
        q = self.adapter.get_quote(1_000_000)  # $1.00
        self.assertIsInstance(q, BridgeQuote)
        self.assertEqual(q.protocol, "across")
        self.assertEqual(q.source_chain, "base")
        self.assertEqual(q.destination_chain, "avalanche")
        self.assertEqual(q.amount, 1_000_000)
        # Fee should be small (< 1% for a $1 bridge)
        self.assertLess(q.fee_pct, 1.0)
        # Output should be less than input (fee deducted)
        self.assertLess(q.output_amount, q.amount)
        self.assertGreater(q.output_amount, 0)
        # GenTech fee = 20 bps of amount
        self.assertEqual(q.gen_tech_fee, 2000)
        # Fill time should be positive
        self.assertGreater(q.estimated_time_seconds, 0)
        self.assertEqual(q.source, "live")

    def test_live_quote_larger_amount(self):
        """Live quote for a larger amount ($1000)."""
        q = self.adapter.get_quote(1_000_000_000)  # $1000
        self.assertEqual(q.amount, 1_000_000_000)
        self.assertLess(q.fee_pct, 1.0)
        self.assertGreater(q.output_amount, 0)
        self.assertEqual(q.gen_tech_fee, 2_000_000)  # 20 bps of $1000

    def test_api_failure_falls_back_to_estimate(self):
        """If the API is unreachable, fall back to estimate (no crash)."""
        with patch("urllib.request.urlopen", side_effect=Exception("network down")):
            q = self.adapter.get_quote(1_000_000)
        self.assertEqual(q.source, "estimate")
        self.assertEqual(q.fee_amount, 800)  # 0.08% estimate

    def test_to_dict_serializable(self):
        """Quote serializes to JSON (for reporting)."""
        q = self.adapter._estimate_quote(1_000_000)
        d = self.adapter.to_dict(q)
        json.dumps(d)  # must not raise
        self.assertEqual(d["protocol"], "across")
        self.assertEqual(d["gen_tech_fee"], 2000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
