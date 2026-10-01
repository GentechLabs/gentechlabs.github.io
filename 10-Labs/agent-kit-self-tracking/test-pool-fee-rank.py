#!/usr/bin/env python3
"""test-pool-fee-rank.py — regression checks for the pool fee ranker.

WHY THIS EXISTS: the ranker's two most-quoted columns are "POOL FEES/day" and "OUR $/day".
On 2026-09-22 both were being filled for a row whose fee leg the script itself DISQUALIFIES
(the frozen 47% constant), so the report printed an authoritative `$61` and `$0.1797/day`
sourced from a number it refused to rank on. That is the same bug class as 09-20 (a frozen
constant reprinted as a live measurement) surviving in the two columns that answer the
depositor's question. The APR column did the same thing one column over.

The bug was found by reading output, not by running a check — so these checks now exist.

Run: python3 test-pool-fee-rank.py     (exit 0 = all pass, 1 = failure)

Tests run against the REAL module's own constants and code paths where possible, so a change to
the disqualification rule is caught rather than silently agreed with.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "pool-fee-rank.py")

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}" + (f"  -- {detail}" if detail else ""))


def load_module():
    spec = importlib.util.spec_from_file_location("pool_fee_rank", TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = load_module()

    print("test-pool-fee-rank — disqualification must reach the ANSWER columns, not just the ranking")
    print("-" * 96)

    # ── 1. The rule itself is present and says what we think it says ────────────────
    src = open(TARGET).read()
    check("STALE_HOURS is a real threshold", mod.STALE_HOURS == 6.0,
          f"got {mod.STALE_HOURS!r}")
    check("a hardcoded STALE constant still exists to test against",
          any(v.get("apr_pct") == 47.0 for v in mod.FALLBACK_MEASURED.values()),
          f"keys={list(mod.FALLBACK_MEASURED)}")
    check("the render path guards the APR column with a stale marker",
          "}%*" in src and 'fee_src"] in STALE_SOURCES' in src,
          "expected a '*'-suffixed APR cell for STALE rows")
    check("the render path computes rankable",
          'rankable = (source not in STALE_SOURCES)' in src,
          "the rankable guard is missing or bypasses STALE_SOURCES")

    # ── 2. THE BUG: a STALE row must carry NO derivable dollars ─────────────────────
    # Reproduce the exact scoring the module runs, with the cache removed so the frozen
    # constant is the only source available — this is the production path that printed $61.
    saved_dirs = mod.CACHE_SEARCH_DIRS
    saved_names = mod.CHAIN_CACHE_NAMES
    try:
        mod.CACHE_SEARCH_DIRS = ["/nonexistent-so-the-frozen-constant-is-used"]
        mod.CHAIN_CACHE_NAMES = ["nope.json"]
        measured = mod.load_chain_measurements()
    finally:
        mod.CACHE_SEARCH_DIRS = saved_dirs
        mod.CHAIN_CACHE_NAMES = saved_names
    check("no chain cache found -> frozen constant path is what we are exercising",
          measured == {}, f"got {measured!r}")

    # A synthetic DefiLlama row for the venue the frozen constant belongs to. The required
    # schema fields below are taken from the module's own candidate filter so the fixture
    # cannot silently stop matching (a fixture that stops matching makes every assertion below
    # vacuously pass or fail for the wrong reason).
    row = {"project": "blackhole-clmm", "symbol": "WAVAX-USDC", "chain": "Avalanche",
           "tvlUsd": 47_051.0, "volumeUsd1d": 336_975.0, "apyBase": 0, "apyReward": 554_248.0,
           "apy": 554_248.0, "rewardTokens": []}

    out = io.StringIO()
    saved_fetch = mod.fetch_pools
    saved_cat, saved_chain = mod.load_catalog, mod.load_chain_measurements
    try:
        mod.fetch_pools = lambda retries=3: [row]
        mod.load_catalog = lambda: {}
        # Force the frozen-constant path by hiding every cache again.
        mod.load_chain_measurements = lambda: {}
        mod.CHAIN_MEASURED = {}
        with contextlib.redirect_stdout(out):
            rc = mod.main()
    finally:
        mod.fetch_pools = saved_fetch
        mod.load_catalog, mod.load_chain_measurements = saved_cat, saved_chain
    text = out.getvalue()

    check("ran against a synthetic STALE row (rc=0)", rc == 0, f"rc={rc}")
    check("the row is marked STALE", "STALE" in text, "no STALE label in output")

    # Select the TABLE row, precisely. A sloppy selector (any line mentioning the venue) picks up
    # the "WHAT THIS SAYS" summary instead of the data row, and then asserts against a line that
    # never had the bug — a check that passes for the wrong reason. The table row is the one with
    # the STALE source column and no prose.
    stale_lines = [ln for ln in text.splitlines()
                   if "Black Hole CLMM" in ln and "STALE" in ln
                   and "headline" not in ln and "frozen" not in ln and "not used to rank" not in ln]
    check("a STALE data row was rendered", bool(stale_lines),
          "could not locate the rendered STALE row")

    if stale_lines:
        line = stale_lines[0]
        check("selector picked the TABLE row, not a prose line",
              "554248%" in line.replace(" ", ""),
              f"selector is weak, got: {line!r}")
        check("STALE row: POOL FEES/day is NOT a dollar figure",
              "—" in line, f"line={line!r}")
        check("STALE row: OUR $/day carries no invented dollar amount",
              line.count("$") == 0,
              f"a '$' survived in the disqualified row: {line!r}")
        check("STALE row: APR cell carries the disqualification marker",
              "47.0%*" in line, f"line={line!r}")
        # And the frozen number must still be VISIBLE in the STALE block (a broken
        # measurement job must not be able to hide), with its date attached.
        check("frozen number is still shown, with its date, in the STALE block",
              "frozen 47.0% dated 2026-09-17" in text,
              "the disqualified number vanished instead of being shown-with-caveat")

    # ── 3. The refusing direction: a FRESH measurement must still pay ───────────────
    # A guard that blocks everything is as broken as one that blocks nothing.
    #
    # TWO FIXTURE DEFECTS WERE FIXED HERE (2026-09-24), because this check could not be trusted:
    #  (a) It asserted the literal "$0.3" — a substring of `f"${our_daily:.4f}"` ONLY while our
    #      capital happened to sit near $139.55. Once the ranker began reading real capital
    #      ($121.46) the cell became "$0.2995", the substring stopped matching, and the check
    #      FAILED while the ranker was correct. A green/red light wired to the wallet's SIZE
    #      cannot report on the ranker's BEHAVIOUR.
    #  (b) It let main() read the live hub file, so the outcome depended on a moving quantity.
    # The capital is now pinned, and the expected dollar is COMPUTED the way the ranker computes
    # it — so the check tests the ranker, not today's balance.
    CAP = 100_000.0
    fresh = {"apr_pct": 90.0, "range": "", "date": "", "age_h": 1.0, "stale": False,
             "venue": "lfj", "tier": "bs10", "addr": "0x" + "1" * 40,
             "tvl_usd": 700_000.0, "volume_24h_usd": 4_000_000.0, "swaps_24h": 3000,
             "measured_at": "2026-09-22T12:00:00+00:00"}
    row2 = {"project": "joe-v2.2", "symbol": "WAVAX-USDC", "chain": "Avalanche",
            "tvlUsd": 700_000.0, "volumeUsd1d": 4_000_000.0, "apyBase": 42.7,
            "apyReward": 0, "apy": 42.7, "rewardTokens": []}
    expected_cell = f"${CAP * (fresh['apr_pct'] / 100.0) / 365.0:.4f}"   # e.g. $246.5753
    out2 = io.StringIO()
    saved_live_capital = mod.live_capital_usd
    try:
        mod.fetch_pools = lambda retries=3: [row2]
        mod.load_catalog = lambda: {}
        mod.load_chain_measurements = lambda: {("lfj", "WAVAX-USDC"): fresh}
        mod.live_capital_usd = lambda: (CAP, "test fixture")
        with contextlib.redirect_stdout(out2):
            rc2 = mod.main()
    finally:
        mod.fetch_pools, mod.load_catalog, mod.load_chain_measurements = (
            saved_fetch, saved_cat, saved_chain)
        mod.live_capital_usd = saved_live_capital
    t2 = out2.getvalue()
    lfj_lines = [ln for ln in t2.splitlines() if "LFJ (Joe v2.2)" in ln and "$" in ln]
    check("fresh MEASURED row still renders dollars (refusing direction not over-blocked)",
          bool(lfj_lines), f"no LFJ dollar row in output rc={rc2}")
    if lfj_lines:
        check("fresh row labelled MEASURED, not STALE",
              "MEASURED" in lfj_lines[0], f"line={lfj_lines[0]!r}")
        check("fresh row shows OUR $/day at the computed value, not a hardcoded constant",
              expected_cell in lfj_lines[0],
              f"expected {expected_cell!r} on a ${CAP:,.0f} book; line={lfj_lines[0]!r}")

    # ── 4. THE OTHER SOURCE: the aggregator's reported leg needs the SAME freshness test ────
    # Found 2026-09-28: the ranker disqualified OUR stale measurement but ranked DefiLlama's
    # reported leg at ANY age. Measured live — joe-v2.1 sat 7th at 2.2% on a reading frozen
    # 134.4h earlier. A guard that watches one of two inputs is the half that got built.
    #
    # Both directions are asserted, because a freshness guard that blocks everything is as
    # broken as one that blocks nothing.
    def reported_row(pid):
        return {"project": "joe-v2.1", "symbol": "WAVAX-USDC", "chain": "Avalanche",
                "tvlUsd": 222_812.0, "volumeUsd1d": 6_737.0, "apyBase": 40.0,
                "apyReward": 0, "apy": 40.0, "rewardTokens": [], "pool": pid}

    saved_age = mod.chart_age_hours
    saved_cache = mod._CHART_AGE_CACHE

    def run_reported(age_h, last_iso, pid="p-fresh"):
        out = io.StringIO()
        try:
            mod.chart_age_hours = lambda pool_id, now=None: ((age_h, last_iso) if age_h is not None
                                                             else (None, None))
            mod._CHART_AGE_CACHE = {}
            mod.fetch_pools = lambda retries=3: [reported_row(pid)]
            mod.load_catalog = lambda: {}
            mod.load_chain_measurements = lambda: {}
            mod.live_capital_usd = lambda: (CAP, "test fixture")
            with contextlib.redirect_stdout(out):
                rc = mod.main()
        finally:
            mod.fetch_pools, mod.load_catalog, mod.load_chain_measurements = (
                saved_fetch, saved_cat, saved_chain)
            mod.live_capital_usd = saved_live_capital
        return rc, out.getvalue()

    # (a) FRESH reported leg -> still ranks, still pays dollars.
    rc_f, t_fresh = run_reported(1.0, "2026-09-28T12:00:00Z")
    row_fresh = [ln for ln in t_fresh.splitlines() if "LFJ (Joe v2.1)" in ln and "$" in ln]
    exp = f"${CAP * 0.40 / 365.0:.4f}"
    check("fresh REPORTED leg still ranks and pays (refusing direction not over-blocked)",
          bool(row_fresh) and exp in row_fresh[0], f"want {exp!r} in {row_fresh[:1]!r}")
    check("fresh reported leg is labelled 'reported', not stale",
          bool(row_fresh) and "reported" in row_fresh[0],
          f"line={row_fresh[:1]!r}")

    # (b) STALE reported leg -> disqualified, and carries NO dollar anywhere.
    rc_s, t_stale = run_reported(200.0, "2026-09-20T00:00:00Z")
    row_stale = [ln for ln in t_stale.splitlines()
                 if "LFJ (Joe v2.1)" in ln and "STALE-AGG" in ln and "frozen" not in ln]
    check("stale REPORTED leg is marked STALE-AGG, not 'reported'",
          "STALE-AGG" in t_stale, "no STALE-AGG label in output")
    check("stale REPORTED row renders a data row carrying the marker",
          bool(row_stale), f"could not locate it; tail={t_stale.splitlines()[-6:]!r}")
    if row_stale:
        check("stale REPORTED row: POOL FEES/day is NOT a dollar figure",
              "—" in row_stale[0], f"line={row_stale[0]!r}")
        check("stale REPORTED row: OUR $/day carries no invented dollar amount",
              row_stale[0].count("$") == 0, f"a '$' survived: {row_stale[0]!r}")
    check("stale REPORTED row is excluded from the PURE-FEE list",
          "LFJ (Joe v2.1)" not in
          [ln for ln in t_stale.splitlines()
           if "fee APR" in ln and "LFJ (Joe v2.1)" in ln] or
          "PURE-FEE POOLS" not in t_stale,
          "a disqualified row reappeared as a comparable")

    # (c) UNREADABLE chart -> UNDATED -> does NOT rank. A lookup failure must not read as fresh.
    rc_u, t_und = run_reported(None, None)
    check("undated reported leg is marked UNDATED and does NOT rank",
          "UNDATED" in t_und, "no UNDATED label in output")
    und_row = [ln for ln in t_und.splitlines() if "LFJ (Joe v2.1)" in ln and "UNDATED" in ln]
    check("undated reported row carries no dollars",
          bool(und_row) and und_row[0].count("$") == 0,
          f"line={und_row[:1]!r}")

    # (d) The rule is a SHARED constant, not three scattered string literals — otherwise a new
    # source name silently ranks again, which is how this defect arrived in the first place.
    check("stale-source names are one shared tuple read by every consumer",
          mod.STALE_SOURCES == ("STALE", "STALE-AGG", "UNDATED")
          and src.count("STALE_SOURCES") >= 5,
          f"got {mod.STALE_SOURCES!r}, STALE_SOURCES references={src.count('STALE_SOURCES')}")
    check("no consumer still tests a single bare 'STALE' literal",
          'fee_src"] != "STALE"' not in src and 'fee_src"] == "STALE"' not in src,
          "a consumer bypasses STALE_SOURCES")

    mod.chart_age_hours, mod._CHART_AGE_CACHE = saved_age, saved_cache

    print("-" * 96)
    print(f"  {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
