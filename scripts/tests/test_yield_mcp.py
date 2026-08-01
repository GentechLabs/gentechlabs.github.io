"""Tests for yield_mcp — offline unit tests + one live smoke test."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from yield_mcp import YieldMCP, YieldMCPError, _sanitize, rank  # noqa: E402


class TestSanitize(unittest.TestCase):
    def test_strips_newlines_and_bounds(self):
        self.assertEqual(_sanitize("a\nb\rc"), "abc")
        self.assertEqual(len(_sanitize("x" * 500, 10)), 10)


class TestRank(unittest.TestCase):
    def _item(self, apy, tvl, **kw):
        d = {"rewardRate": apy, "tvlUsd": str(tvl), "status": {"enter": True}}
        d.update(kw)
        return d

    def test_sorts_desc_and_filters(self):
        items = [self._item(0.01, 1e9), self._item(0.09, 1e9), self._item(0.5, 100)]
        out = rank(items, min_tvl=1e6)
        self.assertEqual([i["rewardRate"] for i in out], [0.09, 0.01])

    def test_skips_unhealthy(self):
        items = [
            self._item(0.5, 1e9, deprecated=True),
            self._item(0.4, 1e9, underMaintenance=True),
            {"rewardRate": 0.3, "tvlUsd": "1e9", "status": {"enter": False}},
            self._item(0.2, 1e9),
        ]
        self.assertEqual(len(rank(items)), 1)

    def test_bad_numbers_skipped(self):
        self.assertEqual(rank([{"rewardRate": "abc", "tvlUsd": "x", "status": {"enter": True}}]), [])

    def test_min_apy(self):
        self.assertEqual(len(rank([self._item(0.01, 1e9)], min_apy=0.05)), 0)


class TestTransport(unittest.TestCase):
    def test_error_response_raises(self):
        c = YieldMCP()
        c._rpc = lambda *a, **k: (_ for _ in ()).throw(YieldMCPError("boom"))
        with self.assertRaises(YieldMCPError):
            c.call_tool("yields_get_all")

    def test_call_tool_parses_text_block(self):
        c = YieldMCP()
        c._rpc = lambda *a, **k: {"content": [{"type": "text", "text": json.dumps({"items": [1]})}]}
        self.assertEqual(c.call_tool("x"), {"items": [1]})

    def test_yields_clamps_limit(self):
        c = YieldMCP()
        seen = {}

        def fake(name, arguments=None):
            seen.update(arguments or {})
            return {"items": []}

        c.call_tool = fake
        c.yields(limit=9999, networks=["ba\nse"])
        self.assertEqual(seen["limit"], 200)
        self.assertEqual(seen["networks"], ["base"])


class TestLive(unittest.TestCase):
    def test_live_yields(self):
        c = YieldMCP()
        items = c.yields(networks=["base"], limit=5)
        self.assertTrue(items, "live endpoint returned no items")
        self.assertTrue(all(i.get("network") == "base" for i in items))


if __name__ == "__main__":
    unittest.main(verbosity=2)
