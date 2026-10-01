#!/usr/bin/env python3
"""Tests for GTA Execution Engine. Runs with NO API key — dry-run only.

FIXTURE FRESHNESS (Sep 15 2026): `_sample_state()` now stamps `last_scan` with
NOW. The fixture used a hardcoded 2026-08-03 timestamp; once the executor grew
the fresh-scan truth guard (ARB_STATE_MAX_AGE_H = 6h, Aug 31), that frozen
timestamp made `decide()` return SKIP / `stale_scan_data` BEFORE it ever ranked
an opportunity — so 4 tests failed for a reason unrelated to their assertion.
A test fixture must not age: a constant timestamp is a memo of the past.
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

# Ensure executor importable from sibling
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Keep tests OUT of the production agent-flow journal. The executor logs every
# decision to agent-flow.jsonl on append; running the suite must not inject
# synthetic decisions into a file the 4-hourly Decisions Report reads.
os.environ.setdefault(
    "GTA_AGENT_FLOW_LOG",
    os.path.join(tempfile.gettempdir(), "gta-test-agent-flow.jsonl"),
)

import gta_executor as ex

# Ensure real mode never fires in tests
os.environ.pop("GTA_HL_KEY", None)


def _fresh_ts():
    return datetime.now(timezone.utc).isoformat()


def _sample_state(opportunities, age_hours=0.0):
    """A scan state that is FRESH by construction (age_hours=0).

    Pass age_hours>6 to exercise the stale-scan truth guard.
    """
    ts = datetime.now(timezone.utc).timestamp() - age_hours * 3600.0
    stamp = datetime.fromtimestamp(ts, timezone.utc).isoformat()
    return {"last_scan": stamp, "opportunities": opportunities}


class TestDecision(unittest.TestCase):
    def test_execute_threshold(self):
        """Basis >= 10 bps and < stop-loss => ENTER."""
        opp = {"symbol": "PAXG", "basis_bps": 10.04, "perp": 4051.35, "spot": 4047.28}
        d = ex.decide(_sample_state([opp]))
        self.assertEqual(d["action"], "ENTER")
        self.assertEqual(d["symbol"], "PAXG")
        self.assertIn("tradeable", d["reasons"])

    def test_report_not_tradeable(self):
        """Basis 5-10 bps => HOLD/report, not ENTER."""
        opp = {"symbol": "BTC", "basis_bps": 6.11, "perp": 63506.5, "spot": 63467.7}
        d = ex.decide(_sample_state([opp]))
        self.assertEqual(d["action"], "REPORT")
        self.assertIn("below_execute", d["reasons"])

    def test_skip_below_report(self):
        """Basis < 5 bps => SKIP."""
        opp = {"symbol": "LINK", "basis_bps": 3.7, "perp": 8.20, "spot": 8.20}
        d = ex.decide(_sample_state([opp]))
        self.assertEqual(d["action"], "SKIP")

    def test_stale_scan_is_skip(self):
        """A scan older than the truth guard threshold is NO DATA, not live."""
        opp = {"symbol": "PAXG", "basis_bps": 40.0, "perp": 4051.35, "spot": 4047.28}
        d = ex.decide(_sample_state([opp], age_hours=7.0))
        self.assertEqual(d["action"], "SKIP")
        self.assertIn("stale_scan_data", d["reasons"])

    # ── DIRECTION FIX regressions (Sep 15 2026) ─────────────────────────────
    # Edge is a MAGNITUDE. A backwardation leg is negative basis and is just as
    # tradeable as contango — the sign picks the direction, not the ranking.

    def test_backwardation_executes(self):
        """Negative basis clears the EXECUTE line on magnitude (was unreachable)."""
        opp = {"symbol": "AVAX", "basis_bps": -12.2, "perp": 7.6112, "spot": 7.6205}
        d = ex.decide(_sample_state([opp]))
        self.assertEqual(d["action"], "ENTER")
        self.assertEqual(d["symbol"], "AVAX")
        self.assertIn("tradeable", d["reasons"])

    def test_magnitude_beats_signed_max(self):
        """-12.2 backwardation must rank above +10.6 contango (signed max lost)."""
        opps = [
            {"symbol": "ONDO", "basis_bps": 10.6, "perp": 0.359335, "spot": 0.358955},
            {"symbol": "AVAX", "basis_bps": -12.2, "perp": 7.6112, "spot": 7.6205},
        ]
        d = ex.decide(_sample_state(opps))
        self.assertEqual(d["action"], "ENTER")
        self.assertEqual(d["symbol"], "AVAX")

    def test_backwardation_order_plan_reverses(self):
        """Backwardation => long perp + sell spot (the previously dead branch)."""
        opp = {"symbol": "AVAX", "basis_bps": -12.2, "perp": 7.6112, "spot": 7.6205}
        plan = ex.build_order_plan(opp)
        self.assertEqual(plan["perp_side"], "long")
        self.assertEqual(plan["spot_side"], "sell")
        self.assertEqual(plan["symbol"], "AVAX")

    def test_stop_loss_wide(self):
        """Open position where spread widened > 50 bps from entry => CLOSE."""
        pos = {"symbol": "BTC", "entry_spread_bps": 10.0}
        cur_spread = 70.0  # +60 bps widen
        d = ex.decide(_sample_state([]), position=pos, current_spread_bps=cur_spread)
        self.assertEqual(d["action"], "CLOSE")
        self.assertIn("stop_loss", d["reasons"])

    def test_stop_loss_wide_backwardation(self):
        """A widening BACKWARDATION leg is stop-loss too (sign must not hide it)."""
        pos = {"symbol": "AVAX", "entry_spread_bps": -10.0}
        cur_spread = -70.0  # widened 60 bps in the negative direction
        d = ex.decide(_sample_state([]), position=pos, current_spread_bps=cur_spread)
        self.assertEqual(d["action"], "CLOSE")
        self.assertIn("stop_loss", d["reasons"])

    def test_close_on_normalize(self):
        """Spread normalized < 3 bps => CLOSE (take profit)."""
        pos = {"symbol": "BTC", "entry_spread_bps": 12.0}
        d = ex.decide(_sample_state([]), position=pos, current_spread_bps=2.0)
        self.assertEqual(d["action"], "CLOSE")
        self.assertIn("normalized", d["reasons"])

    def test_close_on_normalize_negative(self):
        """A backwardation leg that normalizes to -2 bps is take-profit, not hold."""
        pos = {"symbol": "AVAX", "entry_spread_bps": -12.0}
        d = ex.decide(_sample_state([]), position=pos, current_spread_bps=-2.0)
        self.assertEqual(d["action"], "CLOSE")
        self.assertIn("normalized", d["reasons"])

    def test_max_hold(self):
        """Position older than 7 days => CLOSE regardless of spread."""
        pos = {"symbol": "BTC", "entered_at": "2026-07-01T00:00:00+00:00"}
        d = ex.decide(_sample_state([]), position=pos, current_spread_bps=8.0)
        self.assertEqual(d["action"], "CLOSE")
        self.assertIn("max_hold", d["reasons"])


class TestOrderPlan(unittest.TestCase):
    """ENTER-path tests. The MODE GATE (Aug 21) downgrades ENTER to HELD unless
    the council has the treasury in TRADE mode, so these tests patch
    `can_trade` to reach the plan/execute path they are actually asserting on.
    TestModeGate below covers the gate itself."""

    def setUp(self):
        self._orig_can_trade = ex.can_trade
        ex.can_trade = lambda s=None: True

    def tearDown(self):
        ex.can_trade = self._orig_can_trade

    def test_dry_run_no_funds(self):
        """Dry-run produces a plan and moves no funds."""
        opp = {"symbol": "PAXG", "basis_bps": 10.04, "perp": 4051.35, "spot": 4047.28}
        state = _sample_state([opp])
        result = ex.run(state, dry_run=True, position=None, current_spread_bps=10.04)
        self.assertEqual(result["mode"], "DRY_RUN")
        self.assertEqual(result["order_plan"]["symbol"], "PAXG")
        # contango => short perp + long spot
        self.assertEqual(result["order_plan"]["perp_side"], "short")
        self.assertEqual(result["order_plan"]["spot_side"], "buy")
        self.assertFalse(result.get("executed"), "dry-run must not execute")

    def test_dry_run_backwardation_plan(self):
        """A backwardation ENTER builds the reversed plan end-to-end."""
        opp = {"symbol": "AVAX", "basis_bps": -12.2, "perp": 7.6112, "spot": 7.6205}
        result = ex.run(_sample_state([opp]), dry_run=True, position=None,
                        current_spread_bps=-12.2)
        self.assertEqual(result["decision"]["action"], "ENTER")
        self.assertEqual(result["order_plan"]["perp_side"], "long")
        self.assertEqual(result["order_plan"]["spot_side"], "sell")
        self.assertFalse(result.get("executed"))

    def test_real_mode_no_key_fails(self):
        """Real mode without GTA_HL_KEY must fail loudly, not silently."""
        opp = {"symbol": "PAXG", "basis_bps": 10.04, "perp": 4051.35, "spot": 4047.28}
        state = _sample_state([opp])
        with self.assertRaises(ex.NoExecutionKeyError):
            ex.run(state, dry_run=False, position=None, current_spread_bps=10.04)


class TestModeGate(unittest.TestCase):
    """The council's mode gate: out of TRADE mode, no ENTER may reach a plan
    or the execution path — no funds, and no key error either (it never got
    that far). This is the safety that keeps the arb leg off the farm."""

    def setUp(self):
        self._orig_can_trade = ex.can_trade
        ex.can_trade = lambda s=None: False

    def tearDown(self):
        ex.can_trade = self._orig_can_trade

    def test_yield_farm_holds_enter_dry(self):
        opp = {"symbol": "PAXG", "basis_bps": 10.04, "perp": 4051.35, "spot": 4047.28}
        result = ex.run(_sample_state([opp]), dry_run=True, position=None,
                        current_spread_bps=10.04)
        self.assertEqual(result["decision"]["action"], "HELD")
        self.assertIsNone(result["order_plan"])
        self.assertFalse(result.get("executed"))

    def test_yield_farm_holds_enter_real_no_funds(self):
        """Even asked for REAL, the gate returns before the execution path."""
        opp = {"symbol": "PAXG", "basis_bps": 10.04, "perp": 4051.35, "spot": 4047.28}
        result = ex.run(_sample_state([opp]), dry_run=False, position=None,
                        current_spread_bps=10.04)
        self.assertEqual(result["decision"]["action"], "HELD")
        self.assertIsNone(result["order_plan"])
        self.assertFalse(result.get("executed"))


class TestPersistence(unittest.TestCase):
    def test_state_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "pos.json"
            pos = {"symbol": "PAXG", "entry_spread_bps": 10.04, "entered_at": "2026-08-03T22:22:00+00:00"}
            ex.save_position(pos, p)
            loaded = ex.load_position(p)
            self.assertEqual(loaded["symbol"], "PAXG")
            self.assertEqual(loaded["entry_spread_bps"], 10.04)


class TestCloseDispatch(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("AAE_CLOSE_REAL", None)

    def test_close_dry_run_marks_dispatch_not_executed(self):
        """CLOSE decision in dry-run surfaces dispatch intent, no funds move."""
        pos = {"symbol": "PAXG", "entry_spread_bps": 12.0}
        result = ex.run(_sample_state([]), dry_run=True, position=pos, current_spread_bps=2.0)
        self.assertEqual(result["decision"]["action"], "CLOSE")
        self.assertEqual(result["order_plan"], {"close": True, "symbol": "PAXG"})
        self.assertEqual(result.get("close_dry_run"), "dispatch-to-close-executor")
        self.assertFalse(result.get("executed"))

    def test_close_real_without_flag_reports_not_executed(self):
        """Real CLOSE without AAE_CLOSE_REAL surfaces failure, not fake success."""
        os.environ.pop("AAE_CLOSE_REAL", None)
        pos = {"symbol": "PAXG", "entry_spread_bps": 12.0}
        result = ex.run(_sample_state([]), dry_run=False, position=pos, current_spread_bps=2.0)
        # The dispatch should NOT report executed=True when the close executor
        # refuses (no flag/creds). It returns a close_result with executed False.
        self.assertFalse(result.get("executed"))
        self.assertIn("close_result", result)
        self.assertFalse(result["close_result"].get("executed"))


if __name__ == "__main__":
    unittest.main()
