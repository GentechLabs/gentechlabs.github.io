#!/usr/bin/env python3
"""Test suite for the Mastercard red/blue-team demo."""

import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import red_team as red
import blue_team as blue


class TestRedTeam(unittest.TestCase):
    def test_catalog_has_all_attacks(self):
        self.assertEqual(len(red.ATTACK_TYPES), 7)

    def test_generate_attack_sets_type(self):
        for t in red.ATTACK_TYPES:
            a = red.generate_attack(t)
            self.assertEqual(a.attack_type, t)
            self.assertTrue(a.intent_id.startswith("atk_"))

    def test_injection_contains_marker(self):
        a = red.generate_attack("injection")
        self.assertTrue(blue._injection_marker(a.request_text))

    def test_batch_reproducible_with_seed(self):
        def _strip(d):
            # intent_id uses secrets (crypto-random); compare the deterministic fields
            d = dict(d)
            d.pop("intent_id", None)
            d.pop("timestamp_utc", None)
            return d
        b1 = [_strip(i.to_dict()) for i in red.generate_batch(5, seed=99)]
        b2 = [_strip(i.to_dict()) for i in red.generate_batch(5, seed=99)]
        self.assertEqual(b1, b2)


class TestBlueTeam(unittest.TestCase):
    def test_injection_blocks(self):
        a = red.generate_attack("injection")
        v = blue.evaluate(a)
        self.assertEqual(v.decision, "BLOCK")
        self.assertIn("injection", v.rules)

    def test_identity_spoof_blocks(self):
        a = red.generate_attack("identity_spoof")
        v = blue.evaluate(a)
        self.assertEqual(v.decision, "BLOCK")
        self.assertIn("identity_spoof", v.rules)

    def test_out_of_policy_blocks(self):
        a = red.generate_attack("out_of_policy")
        v = blue.evaluate(a)
        self.assertEqual(v.decision, "BLOCK")

    def test_amount_anomaly_flags(self):
        a = red.generate_attack("amount_anomaly")
        v = blue.evaluate(a)
        self.assertEqual(v.decision, "FLAG")
        self.assertIn("amount_anomaly", v.rules)

    def test_velocity_flags(self):
        a = red.generate_attack("velocity_spike")
        v = blue.evaluate(a)
        self.assertEqual(v.decision, "FLAG")

    def test_clean_allows(self):
        # Build a fully-legitimate intent manually
        payer = red._payer_profile()
        a = red.PaymentIntent(
            intent_id="atk_clean",
            payer=payer["payer"],
            payee=payer["beneficiaries"][0],
            amount_usd=100.0,
            chain="base",
            beneficiary_listed=True,
            payer_identity_match=True,
            velocity_ok=True,
            amount_within_ticket=True,
            request_text="Approved vendor invoice for standard services.",
            attack_type=None,
        )
        v = blue.evaluate(a)
        self.assertEqual(v.decision, "ALLOW")


if __name__ == "__main__":
    unittest.main(verbosity=2)
