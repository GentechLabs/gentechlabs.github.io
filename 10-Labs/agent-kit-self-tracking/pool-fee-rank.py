#!/usr/bin/env python3
"""pool-fee-rank.py — rank our candidate pools by FEE generation, not headline APY.

Jordan (2026-09-18):
  "the cron Job should check the pools we talked about getting into based on fee generation"

That is the right question and it is NOT the one a yield aggregator answers. A headline APY
mixes two completely different things:

    FEE APR      — paid by traders, every swap, durable, does not care what you think
    REWARD APR   — protocol emissions, staking-dependent, fragile, and it is somebody's
                   token being handed to you to sell

The standing rule is that the fee core is the priority. So this ranks on fees ONLY, and
shows emissions beside it purely so the difference is impossible to miss.

THE TRAP THIS GUARDS AGAINST: DefiLlama reports `apyBase=0%` for whole venue families
(both Black Hole CLMM and every Pharaoh pool). A zero there does NOT mean "no fees" — it
means the aggregator cannot compute them, and the entire headline is emissions. Ranking on
the headline would put a 856%-emissions pool first. Ranking on `apyBase` alone would put it
last. Neither is the truth, so we compute the fee line ourselves.

METHOD — per pool:
  turnover      = vol24 / TVL                       (how hard the pool works per dollar)
  fee APR       = apyBase when the aggregator reports one (it is the fee leg)
  implied rate  = fee APR x TVL / (vol24 x 365)     (back out the effective take rate)
  MEASURED      = where we have our own on-chain fee measurement, THAT WINS — because an
                  aggregator's arithmetic cannot see whether our ticks are in range.
                  Fresh measurements come from chain-fee-measurements.json (written hourly by
                  chain-fee-rank.py). A measurement older than STALE_HOURS is NOT allowed to
                  rank — it is printed beside the row instead. A measurement that never
                  expires reads exactly like a live one, which is how a stale constant got
                  reprinted as fact on 09-20.
  reported      = the aggregator's own apyBase, USED ONLY WHEN IT IS DATED AND FRESH. It gets the
                  same STALE_HOURS test as our own measurement, because an undated number outranking
                  dated ones is the same bug whichever source it came from. Age is read from the
                  pool's chart endpoint, which is what dates the /pools value; a lookup that fails
                  yields UNDATED, which does NOT rank (a failure must never read as fresh).

TWO NUMBERS THAT ARE NOT THE SAME THING (language correction from Jordan, 2026-09-18):

  "Fee generation and income from the pool are two different things. Because platforms are
   different."

  FEE GENERATION  — the POOL's total fee revenue = vol24 x take-rate. It describes the
                    PLATFORM: how much money changes hands there. It is their business.
  LP INCOME (APR) — what $1 of OUR liquidity earns = fee generation x 365 / TVL. This is the
                    only one of the two that pays us anything.

  THEY DIVERGE HARD, and the earlier version of this report labelled the APR column in a way
  that could be read as generation. A big pool can generate enormous fees and pay us poorly,
  because we would own a sliver of it. A small pool can pay well precisely BECAUSE it is small.
  Ranking a venue on absolute fee generation would put the largest pool first; ranking it on
  LP income answers the only question that matters to a depositor. Both are reported below,
  separately, because conflating them is how the wrong pool gets chosen.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "GenTech-Steward/1.0 (treasury research)"}
YIELDS = "https://yields.llama.fi/pools"

# Venues we have actually discussed for the treasury, plus the honest note on each.
CANDIDATES = {
    "blackhole-clmm": {"name": "Black Hole CLMM", "audit": "Ramses fork; partial 2022 Solidly/PeckShield"},
    "blackhole-amm":  {"name": "Black Hole AMM",  "audit": "same codebase family"},
    "pharaoh-v3":     {"name": "Pharaoh V3",      "audit": "NO Pharaoh-specific audit — x(3,3) review only"},
    "joe-v2.2":       {"name": "LFJ (Joe v2.2)",  "audit": "Trader Joe / LFJ, long-standing"},
    "joe-v2.1":       {"name": "LFJ (Joe v2.1)",  "audit": "Trader Joe / LFJ, long-standing"},
    "uniswap-v3":     {"name": "Uniswap V3",      "audit": "Uniswap, heavily audited"},
    "pangolin-v2":    {"name": "Pangolin V2",     "audit": "older Avalanche DEX"},
}

# Our OWN chain-decoded fee measurements — these override the aggregator's arithmetic.
# Reason: a fee APR computed from an aggregator's cached volume can be wildly off; ours decodes
# real Swap events and reads the tier from the pool contract. But note the limit: this is
# volume x NOMINAL tier, GROSS of protocol share — it is not observed accrual. Do not call it
# "actual accrual"; it still assumes every trade paid the nominal tier.
#
# TWO SOURCES, IN ORDER OF TRUST:
#   1. chain-fee-measurements.json — written hourly by chain-fee-rank.py from decoded Swap
#      events. Fresh, per-pool, has a timestamp. THIS is the real measurement.
#   2. FALLBACK_MEASURED below — a hardcoded constant. Kept only because a hardcoded belief is
#      better than nothing when the cache is missing, but it is a FROZEN number and must NEVER
#      be allowed to rank silently. That is the exact bug of 09-20: a 47.0% captured on 09-17
#      was reprinted as though live, and it read identically to a fresh measurement.
FALLBACK_MEASURED = {
    "blackhole-clmm|WAVAX-USDC": {"apr_pct": 47.0, "range": "44.6-49.3", "date": "2026-09-17",
                                  "note": "durable core from on-chain fee accrual"},
}

# How old a measurement may be before it is disqualified from ranking. chain-fee-rank.py runs
# hourly; 6h tolerates a missed run or two without letting a frozen constant masquerade as live.
# A stale number is still SHOWN, marked STALE and excluded from the ranking — never silently
# dropped (that would hide a broken measurement job) and never silently used.
STALE_HOURS = 6.0

# ── THE SAME RULE, APPLIED TO THE OTHER SOURCE (found 2026-09-28) ─────────────────────────────
# This file refused to rank OUR OWN measurement once it was older than STALE_HOURS — but it
# applied no freshness test at all to the aggregator's reported fee leg. So a DefiLlama row whose
# last sample was days old ranked exactly like a live one.
#
# Measured on 2026-09-28: joe-v2.1 WAVAX-USDC was ranked 7th at 2.2% on a reading frozen at
# 2026-09-22T23:01Z — 134h, 22x STALE_HOURS — and joe-v2.2's reported 103.41% was the same frozen
# sample. That is the 09-20 bug one source over: an undated number outranking dated ones. A guard
# that only watches one of its two inputs is not a guard; it is the half that happened to be built.
#
# THE AGE IS MEASURED, NOT INFERRED. DefiLlama's /pools object carries no timestamp of its own,
# but the per-pool chart endpoint's LAST sample IS the value /pools is serving — verified
# identical apyBase and TVL on both a fresh row (univ3 0.05%, 1.3h) and frozen ones (joe-v2.2 and
# joe-v2.1, 134.3h) — so that sample's timestamp dates the row. Do NOT substitute
# `apyPct1D is None` even though it correlates: it is a proxy, and a proxy that is usually right
# is exactly how a wrong number gets ranked in the case that matters.
STALE_SOURCES = ("STALE", "STALE-AGG", "UNDATED")


# WHERE THE CACHE LIVES. The ranking script exists in three enrolled copies (vault, repo, profile)
# and the CRON runs the REPO copy — but chain-fee-rank.py writes its cache into the PROFILE and
# mirrors it to the VAULT, and the repo can end up with none at all. Resolving the cache only
# relative to __file__ therefore lost the measurement in the exact path that production uses: the
# ranking silently fell back to aggregator arithmetic while looking correct from the vault copy.
# So search every enrolled location and keep the FRESHEST. A generated cache must never be the
# thing we trust by path luck.
CACHE_SEARCH_DIRS = [
    None,  # placeholder: the script's own directory, filled in at call time
    "/root/.hermes/profiles/gentech-treasury/scripts",
    "/root/vaults/gentech/10-Labs/agent-kit-self-tracking",
]

CHAIN_CACHE_NAMES = ["chain-fee-measurements.json"]

# How closely a chain-measured pool's TVL must match an aggregator row before we accept that the
# two describe the SAME pool. 10% is deliberately loose — TVL is a live number and the aggregator's
# copy lags ours by minutes — but tight enough to reject a duplicate row an order of magnitude off.
# Set this because the alternative (refuse whenever the aggregator lists more than one pool) turned
# our own fresh measurement of the ACTIVE venue into a STALE fallback constant.
TVL_MATCH_TOL = 0.10

# chain-fee-rank.py names venues differently from DefiLlama. Map explicitly rather than
# fuzzy-matching, so a measurement can never land on the wrong venue.
CHAIN_VENUE = {
    "uniswap-v3": "univ3",
    "joe-v2.2":   "lfj",     # the bin (liquidity-book) pools are the v2.2 ones
    # Wired 2026-09-22: chain-fee-rank.py now measures Black Hole's Algebra pool, so the ACTIVE
    # venue can finally be ranked on OUR number instead of the frozen 47% constant. Until this
    # line existed the venue we are pointed at was the only row with no live fee read.
    "blackhole-clmm": "blackhole",
    "blackhole-amm":  "blackhole",
}


def _read_cache(path: str):
    """Read one cache file. Returns (age_h, doc) or None if missing/undateable/unreadable."""
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            doc = json.load(f)
        measured_at = doc.get("measured_at")
        if not measured_at:
            return None                      # undateable: never use a measurement we cannot age
        ts = datetime.fromisoformat(measured_at)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600.0
        return age_h, doc
    except Exception:                                                 # noqa: BLE001
        return None


def load_chain_measurements() -> dict:
    """Read OUR on-chain fee measurements, from whichever enrolled copy holds the freshest cache.

    Returns {(chain_venue, normalised pair) -> {apr_pct, age_h, stale, ...}}. {} if no dated
    cache is found — the caller then falls back to the frozen constant, which it will mark stale.

    WHY FRESHEST-WINS RATHER THAN FIRST-FOUND: the three copies drift (one gets written, one gets
    mirrored, one gets neither), so "first path that exists" would sometimes select a stale copy
    while a fresh one sat beside it. Staleness is decided by the timestamp, never by path order.

    KEYED BY VENUE *AND* PAIR, SELECTED BY HIGHEST LIQUIDITY: the cache holds several pools per
    pair (three univ3 WAVAX/USDC tiers, four LFJ bins) that disagree wildly — on 09-21 the univ3
    0.05% pool measured 120.6% against the 1.00% pool's 80.5%. Pair-only keying would let
    iteration order pick the headline and let the decoy bins ($0.56 TVL carrying 5-15x higher
    fees) win. Same rule as the four-WAVAX/USDC-pairs trap and the remnant-NFT husk.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    best = None
    for d in CACHE_SEARCH_DIRS:
        d = here if d is None else d
        for name in CHAIN_CACHE_NAMES:
            got = _read_cache(os.path.join(d, name))
            if got is None:
                continue
            age_h, doc = got
            if best is None or age_h < best[0]:
                best = (age_h, doc)
    if best is None:
        return {}
    age_h, doc = best

    out = {}
    for p in doc.get("pools", []):
        venue = (p.get("venue") or "").strip().lower()
        pair = norm_symbol(p.get("pair"))
        if not venue or not pair:
            continue
        rec = {
            "apr_pct": float(p.get("fee_apr_pct") or 0.0),
            # The GROSS tier APR beside the LP-effective one. chain-fee-rank.py now reports the
            # LP-effective take in fee_apr_pct (protocol share deducted) and keeps the gross in
            # fee_apr_gross_pct. Without this, the venue-generation column below would be built
            # from the LP-effective rate and would UNDERSTATE the venue's business — the two
            # numbers this file exists to keep apart.
            "apr_gross_pct": float(p.get("fee_apr_gross_pct") or p.get("fee_apr_pct") or 0.0),
            "fee_tier_effective": p.get("fee_tier_effective"),
            "fee_source": p.get("fee_source"),
            "age_h": age_h,
            "stale": age_h > STALE_HOURS,
            "venue": venue,
            "tier": p.get("tier"),
            "addr": p.get("addr"),
            "tvl_usd": float(p.get("tvl_usd") or 0.0),
            "volume_24h_usd": float(p.get("volume_24h_usd") or 0.0),
            "swaps_24h": int(p.get("swaps_24h") or 0),
            "measured_at": doc.get("measured_at"),
        }
        key = (venue, pair)
        prev = out.get(key)
        # Highest liquidity wins. A pool with no swaps at all in the window is a decoy — its 0%
        # is 'no activity', not 'no yield', so it never displaces a real pool.
        if prev is None or rec["tvl_usd"] > prev["tvl_usd"]:
            out[key] = rec
    return out


# Populated in main() AFTER norm_symbol is defined — a module-level call here would raise
# NameError, since load_chain_measurements() depends on a helper defined further down.
CHAIN_MEASURED: dict = {}

PAIRS = ["WAVAX-USDC", "WAVAX/USDC", "USDC-WAVAX", "WAVAX-USDC.E"]

# Capital we would actually deploy — used ONLY to translate an APR into dollars/day and to
# show what share of the pool we would be. Override with --capital.
#
# THIS WAS A HARDCODED WALLET NUMBER, and it went stale exactly the way the frozen 47% did:
# on 2026-09-23 it still read $139.55 (a figure from the 09-20 funding week) while the chain said
# $123.61 — a 13% overstatement of every dollar figure in the "OUR $/day" column. A constant that
# describes a MOVING quantity is a belief, not a measurement, so it is now read live from the
# treasury's own hub data (refreshed twice an hour, valued by withdraw-simulation on chain), and
# the fallback below is only used when that read fails — loudly.
OUR_CAPITAL_USD = 139.55   # FALLBACK ONLY — superseded at runtime by live_capital_usd()
CAPITAL_SOURCE = "hardcoded fallback (live read failed)"
CAPITAL_DATE = "2026-09-20"
CAPITAL_FILES = [
    "/root/repos/gentechlabs.github.io/DeFi/defi-data-jordan.json",
    "/var/www/gentechlabs/DeFi/defi-data-jordan.json",
]

# ── the catalog: bookmarks, with the decisions attached ──────────────────────
# Read so the ranking can mark which pools we have already ruled on. Without this the
# ranking re-invents opinions every run, and a venue we REJECTED can top the table and
# look attractive again with no memory of why we said no.
def live_capital_usd():
    """Read the treasury's ACTUAL capital from the hub data. Returns (usd, source) or (None, why).

    Read from the same JSON the DeFi hubs serve (rebuilt twice an hour, each tenant valued by
    withdraw-simulation against the chain), so the number behind every "OUR $/day" cell is the
    treasury's real size rather than a constant from a funding week.
    """
    best = None
    for p in CAPITAL_FILES:
        try:
            with open(p) as f:
                d = json.load(f)
            if d.get("tenant") != "jordan":
                continue
            cap = float(d.get("capital_usd") or 0)
            if cap <= 0:
                continue
            ts = d.get("updated_at")
            if not ts:
                continue
            age_h = (datetime.now(timezone.utc)
                     - datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds() / 3600.0
            if best is None or age_h < best[0]:
                best = (age_h, cap, p, ts)
        except Exception:                                             # noqa: BLE001
            continue
    if best is None:
        return None, "no readable hub data"
    age_h, cap, p, ts = best
    # A capital figure older than a day is not "our capital now" — refuse it rather than
    # quietly pricing tomorrow's report off yesterday's wallet.
    if age_h > 24:
        return None, f"hub data is {age_h:.1f}h old ({ts})"
    return cap, f"hub {os.path.basename(p)} @ {ts}"


def load_catalog() -> dict:
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pool-catalog.json")
    try:
        with open(p) as f:
            ents = json.load(f).get("entries", [])
    except Exception:                                                 # noqa: BLE001
        return {}
    out = {}
    for e in ents:
        key = f"{norm_symbol(e.get('venue',''))}|{norm_symbol(e.get('pair',''))}"
        out[key] = e
    return out


CATALOG_BY_ID = {}
CATALOG_BY_NAME = {}


def catalog_lookup(venue_name: str, sym: str):
    """Find a catalog entry for this row, matching on venue display name + pair."""
    for e in CATALOG_BY_ID.values():
        if norm_symbol(e.get("venue", "")) == norm_symbol(venue_name) and \
           norm_symbol(e.get("pair", "")) == norm_symbol(sym):
            return e
    return None


def fetch_pools(retries: int = 3):
    """DefiLlama yields. Retries and returns the error rather than hiding it."""
    last = ""
    for i in range(retries):
        try:
            req = urllib.request.Request(YIELDS, headers=UA)
            raw = urllib.request.urlopen(req, timeout=60).read()
            return json.loads(raw).get("data", [])
        except Exception as e:                                        # noqa: BLE001
            last = f"{type(e).__name__}: {str(e)[:100]}"
            time.sleep(2 * (i + 1))
    print(f"  ⚠️ pools fetch failed: {last}")
    return []


# ── DATING THE AGGREGATOR'S OWN NUMBER ────────────────────────────────────────────────────────
# /pools is a live snapshot of what DefiLlama BELIEVES, not of what it has RECENTLY measured, and
# it dates nothing. The per-pool chart endpoint does: its last sample is both the value /pools is
# serving and the moment that value was taken. So the age is read from the chart, per pool.
#
# FAILURE DIRECTION IS DELIBERATE. If the chart cannot be read we return None — an UNKNOWN age —
# and the row is marked UNDATED, which does NOT rank (see STALE_SOURCES). A lookup failure must
# never read as "fresh": that is the same silent pass this guard exists to close. It is also why
# this is a separate call per pool rather than a field read — the honest cost of a real date.
CHART = "https://yields.llama.fi/chart/"
_CHART_AGE_CACHE: dict = {}


def chart_age_hours(pool_id: str, now=None):
    """Hours since the LAST chart sample for this pool — i.e. how old its reported number is.

    Returns (age_hours, last_sample_iso) or (None, None) when it cannot be established.
    """
    if not pool_id:
        return None, None
    if pool_id in _CHART_AGE_CACHE:
        return _CHART_AGE_CACHE[pool_id]
    out = (None, None)
    for attempt in range(2):
        try:
            req = urllib.request.Request(CHART + pool_id, headers=UA)
            data = json.loads(urllib.request.urlopen(req, timeout=30).read()).get("data") or []
            if data:
                ts = data[-1].get("timestamp")
                t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                now = now or datetime.now(timezone.utc)
                out = ((now - t).total_seconds() / 3600.0, str(ts))
                break
        except Exception:                                             # noqa: BLE001
            if attempt == 0:
                time.sleep(1.5)
    _CHART_AGE_CACHE[pool_id] = out
    return out



def norm_symbol(s: str) -> str:
    return str(s or "").upper().replace("/", "-").replace(" ", "")


def main() -> int:
    print("=" * 100)
    print(f"  POOL FEE RANK — candidate venues, ranked by FEE GENERATION "
          f"({datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC)")
    print("=" * 100)

    rows = fetch_pools()
    if not rows:
        print("  no data — aborting rather than reporting an empty table as a ranking")
        return 1

    # Date lookups are per-run, not per-process: main() can be invoked more than once in one
    # interpreter (the regression suite does exactly that with different fixtures), and a cache
    # that survives the run would let the first fixture's age decide the second one's ranking.
    _CHART_AGE_CACHE.clear()

    global CATALOG_BY_ID, CHAIN_MEASURED, OUR_CAPITAL_USD, CAPITAL_SOURCE
    CATALOG_BY_ID = load_catalog()
    CHAIN_MEASURED = load_chain_measurements()
    cap, cap_src = live_capital_usd()
    CAPITAL_SOURCE = cap_src if cap else f"{cap_src} — FALLBACK ${OUR_CAPITAL_USD:,.2f} dated {CAPITAL_DATE}"
    if cap:
        OUR_CAPITAL_USD = cap

    av = [r for r in rows if r.get("chain") == "Avalanche"]
    cands = [r for r in av if r.get("project") in CANDIDATES
             and norm_symbol(r.get("symbol")) in [norm_symbol(p) for p in PAIRS]]
    if not cands:
        print("  no candidate pools matched — check the pair filter")
        return 1

    # ── score each ───────────────────────────────────────────────────────────
    # How many candidate rows share each (venue, pair)? Used to decide whether a per-tier chain
    # measurement can be attributed to a row at all. DefiLlama aggregates Uniswap fee tiers into
    # ONE row, while chain-fee-rank.py measures each tier separately — so a single tier's APR must
    # never be stamped onto an aggregated row (that made three different Uniswap pools all report
    # the 0.05% tier's number).
    pair_counts = {}
    for r in cands:
        k = (r.get("project"), norm_symbol(r.get("symbol")))
        pair_counts[k] = pair_counts.get(k, 0) + 1

    out = []
    for r in cands:
        tvl = float(r.get("tvlUsd") or 0)
        vol = float(r.get("volumeUsd1d") or 0)
        apy_base = r.get("apyBase")
        apy_rew = r.get("apyReward") or 0.0
        project = r.get("project")
        sym = norm_symbol(r.get("symbol"))
        key = f"{project}|{sym}"

        turnover = vol / tvl if tvl else 0.0

        # the fee leg, in order of trust: FRESH on-chain measurement > aggregator base >
        # frozen fallback constant (shown but NOT allowed to rank).
        chain = CHAIN_MEASURED.get((CHAIN_VENUE.get(project, ""), sym))
        fallback = FALLBACK_MEASURED.get(key)
        reported_base = float(apy_base) if isinstance(apy_base, (int, float)) else None
        # The GROSS-tier APR, where we have one. Only a chain measurement can carry it (a
        # protocol share is a venue-specific fact we read from the pool); aggregator rows have
        # no notion of it, so they fall back to their own single rate just below.
        fee_apr_for_gen = None

        # CAN THIS MEASUREMENT BE ATTRIBUTED TO *THIS* ROW?
        # The old test was blanket: "the aggregator shows more than one pool for this
        # (venue, pair), so refuse". That refused far more than it should — DefiLlama reports TWO
        # Black Hole rows (one a 0-volume duplicate) and THREE Uniswap tiers, so our freshly
        # measured ACTIVE venue was blocked by a duplicate row and fell through to the frozen
        # constant. A guard that cannot tell "duplicate" from "the same pool" is not a guard, it
        # is an outage.
        #
        # The real question is "is this row the pool we measured?" — and we can answer it with TVL.
        # Measured Black Hole TVL $534,738 vs row TVL $531,044 = 0.7% (same pool, matched);
        # vs the duplicate row's $47,051 = 11x off (not the same pool). Uniswap 0.05% measured at
        # $1.0M matches none of its reported rows ($64K / $3.74M / $23K), so it still refuses.
        # The check must be able to say BOTH yes and no to be worth anything.
        chain_tvl = (chain.get("tvl_usd") or 0.0) if chain else 0.0
        chain_tvl_ok = True
        if chain is not None and chain_tvl > 0 and tvl > 0:
            chain_tvl_ok = abs(tvl - chain_tvl) / chain_tvl <= TVL_MATCH_TOL

        chain_used = (chain is not None and not chain["stale"]
                      and chain["swaps_24h"] > 0 and chain_tvl_ok)
        stale_note = None
        ambiguous_note = None

        if chain is not None and not chain["stale"] and not chain_tvl_ok:
            multi = pair_counts.get((project, sym), 0) > 1
            where = ("aggregator row spans multiple pools" if multi
                     else "single aggregator row")
            ambiguous_note = (f"{where}; our measured pool ({chain['tier']}, "
                              f"TVL ${chain_tvl:,.0f} = {chain['apr_pct']:.1f}%) does not match "
                              f"this row's TVL ${tvl:,.0f} — different pool")

        if chain_used and chain is not None:
            fee_apr = chain["apr_pct"]
            # The VENUE's own generation must be computed from the GROSS tier, not the LP-effective
            # one — otherwise the column that describes the platform's business is silently reduced
            # by our protocol share and no longer measures the platform at all.
            fee_apr_for_gen = chain.get("apr_gross_pct") or chain["apr_pct"]
            source = "MEASURED"
            measured_at = chain["measured_at"]
            measure_age_h = chain["age_h"]
            # Use OUR measured volume for the venue-generation column too. Leaving it "—" beside a
            # MEASURED APR is the same defect as the frozen-row dollars: an answer column that
            # cannot answer while the data to answer it exists. The aggregator reports 0 volume for
            # this Black Hole row, so without this the LEADER showed a blank where its $6.3M of
            # daily fee flow should be.
            if chain.get("volume_24h_usd"):
                vol_for_gen = chain["volume_24h_usd"]
        elif fallback:
            # A frozen constant. We print it because the belief is real, but it does not rank:
            # an undated number that outranks live data is how the 09-20 stale-47% bug worked.
            fee_apr = fallback["apr_pct"]
            source = "STALE"
            measured_at = fallback.get("date")
            measure_age_h = None
            days = None
            try:
                d0 = datetime.strptime(fallback["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                days = (datetime.now(timezone.utc) - d0).days
            except Exception:                                         # noqa: BLE001
                pass
            stale_note = (f"frozen {fallback['apr_pct']:.1f}% dated {fallback.get('date')}"
                          + (f" ({days}d old)" if days is not None else "")
                          + " — not used to rank")
        elif reported_base:
            # THE AGGREGATOR GETS THE SAME FRESHNESS TEST WE APPLY TO OURSELVES. Without this the
            # reported leg ranked at any age (found 2026-09-28: joe-v2.1 ranked on a 134h-old
            # sample). Age comes from the row's own chart, never from a proxy field.
            agg_age_h, agg_last = chart_age_hours(r.get("pool"))
            fee_apr = reported_base
            measured_at = agg_last
            measure_age_h = agg_age_h
            if agg_age_h is None:
                # UNDATED, NOT FRESH. A lookup failure must not silently pass as live.
                source = "UNDATED"
                stale_note = ("reported leg could not be dated (chart unreadable) — not used to rank")
            elif agg_age_h > STALE_HOURS:
                source = "STALE-AGG"
                stale_note = (f"aggregator sample frozen {agg_age_h:.1f}h old "
                              f"(last {agg_last}) — not used to rank")
            else:
                source = "reported"

        else:
            # apyBase is 0 or missing: we cannot know the fee leg from here.
            fee_apr = None
            source = "UNKNOWN"
            measured_at = None
            measure_age_h = None

        # fee_apr and apy_* come back as PERCENTAGES (e.g. 90.7), so every rate must be
        # divided by 100 before it is used as a fraction. The first version of this script
        # did not, and reported an "implied take" of 5.428% for LFJ — absurd on its face,
        # because real DEX take rates are 0.01-0.30%. Caught by sanity-checking the output
        # rather than trusting it. A 100x error in a rate is exactly the kind of thing that
        # looks plausible enough to survive review.
        # A STALE (frozen-constant) fee leg is DISQUALIFIED from the ranking — so it must not be
        # allowed to fill the two answer columns either. Deriving "POOL FEES/day" and "OUR $/day"
        # from a number we refuse to rank on prints an authoritative, live-looking dollar figure
        # sourced from a disqualified constant: the 09-20 bug (a frozen 47% reprinted as a live
        # measurement) surviving in the exact two columns that answer the depositor's question.
        # A row whose fee leg is not rankable has no derivable dollars — show "—" and leave the
        # disqualified number visible only in the STALE block, where its date and age are attached.
        rankable = (source not in STALE_SOURCES)


        fee_frac = (fee_apr / 100.0) if (fee_apr and rankable) else None
        implied_rate = (fee_frac * tvl / (vol * 365)) if (fee_frac and vol) else None

        # ── THE TWO NUMBERS, KEPT APART ──────────────────────────────────────
        # FEE GENERATION: the pool's total daily fee revenue. vol24 x GROSS take-rate. This is the
        # platform's business figure — how much money moves through the venue. It must use the
        # GROSS take, because the protocol share never reaches an LP and is still the platform's
        # revenue on the way past.
        gen_frac = None
        if rankable and vol:
            gen_frac = ((fee_apr_for_gen if fee_apr_for_gen else fee_apr) or 0) / 100.0 or None
        gen_rate = (gen_frac * tvl / (vol * 365)) if gen_frac else None
        gen_usd_day = (vol * gen_rate) if (vol and gen_rate) else None
        # LP INCOME: what OUR capital earns. This is the only one that pays us.
        our_daily = (OUR_CAPITAL_USD * (fee_apr / 100.0) / 365.0) if (fee_apr and rankable) else None
        # What share of the pool we would be — because at small TVL our own deposit moves
        # the denominator and dilutes the very APR we are chasing.
        our_share_pct = (OUR_CAPITAL_USD / tvl * 100.0) if tvl else None

        cat = catalog_lookup(CANDIDATES[project]["name"], sym)
        out.append({
            "venue": CANDIDATES[project]["name"], "project": project, "sym": sym,
            "tvl": tvl, "vol": vol, "turnover": turnover,
            "fee_apr": fee_apr, "fee_src": source,
            "measured_at": measured_at, "measure_age_h": measure_age_h,
            "stale_note": stale_note, "ambiguous_note": ambiguous_note,
            "apy_rew": float(apy_rew), "apy": float(r.get("apy") or 0),
            "implied_rate": implied_rate, "outlier": bool(r.get("outlier")),
            "reward_tokens": r.get("rewardTokens") or [],
            "audit": CANDIDATES[project]["audit"],
            "cat_status": (cat.get("status") if cat else None),
            "cat_id": (cat.get("id") if cat else None),
            "cat_note": (cat.get("note") if cat else None),
            "gen_usd_day": gen_usd_day,
            "our_daily": our_daily,
            "our_share_pct": our_share_pct,
        })

    # A STALE row is excluded from the ranking (key -1) but still printed, so the broken
    # measurement shows up instead of quietly disappearing.
    ranked = sorted(out, key=lambda x: (
        -(x["fee_apr"] if (x["fee_apr"] is not None and x["fee_src"] not in STALE_SOURCES) else -1)))


    # ── the table ────────────────────────────────────────────────────────────
    # TWO HEADLINE COLUMNS ON PURPOSE. "POOL FEES/day" is the venue's business. "LP APR" is
    # what we earn, and "OUR $/day" is that APR on our actual capital. A venue can top the
    # first column and be a poor choice; only the last two answer our question.
    MARK = {"ACTIVE": "🟢ACTIVE", "WATCH": "👁️WATCH", "RETIRED": "⚪RETIRED", "AVOID": "🚫AVOID"}
    print(f"  capital considered: ${OUR_CAPITAL_USD:,.2f}   [{CAPITAL_SOURCE}]\n")
    print(f"  {'venue':<16}{'TVL':>11}{'vol24':>11}{'POOL FEES/day':>15}{'LP APR':>9}"
          f"{'OUR $/day':>11}{'our share':>11}  {'src':<9}{'EMISS':>7}  CATALOG")
    print("  " + "-" * 118)
    for r in ranked:
        # A disqualified fee leg must not render as an ANSWER in any answer column. The APR
        # column is one of them ("what $1 of OUR liquidity earns") — a bare "47.0%" beside a
        # STALE tag two columns away still reads as a live yield on a glance. The number stays
        # visible (a broken measurement must stay visible) but carries its disqualification with
        # it, so it cannot be quoted without the caveat.
        stale = (r["fee_src"] in STALE_SOURCES)

        if r["fee_apr"] is None:
            fee = "n/a"
        elif stale:
            # ASCII marker, not an emoji: this table is fixed-width and a wide glyph shifts
            # every column after it. The marker carries the disqualification into the cell.
            fee = f"{r['fee_apr']:.1f}%*"
        else:
            fee = f"{r['fee_apr']:.1f}%"
        gen = f"${r['gen_usd_day']:,.0f}" if r["gen_usd_day"] is not None else "—"
        ours = f"${r['our_daily']:.4f}" if r["our_daily"] is not None else "—"
        share = f"{r['our_share_pct']:.4f}%" if r["our_share_pct"] is not None else "—"
        em = f"{r['apy_rew']:.0f}%" if r["apy_rew"] else "0%"
        cm = MARK.get(r["cat_status"], "") if r["cat_status"] else ""
        print(f"  {r['venue']:<16}{r['tvl']:>11,.0f}{r['vol']:>11,.0f}{gen:>15}"
              f"{fee:>9}{ours:>11}{share:>11}  {r['fee_src']:<9}{em:>7}  {cm}")

    print("\n  POOL FEES/day = the VENUE's business (vol x take-rate). LP APR = what $1 of OUR")
    print("  liquidity earns. OUR $/day = that APR applied to our actual capital. Only the last")
    print("  two answer the depositor's question — the first describes somebody else's platform.")

    # A stale measurement must be VISIBLE AND DISQUALIFIED. Silently dropping it would hide a
    # broken measurement job; silently using it is how a frozen 47% got reprinted as live.
    stale_rows = [r for r in ranked if r.get("fee_src") in STALE_SOURCES]
    if stale_rows:
        print("\n  🕰️  STALE MEASUREMENT — shown, but NOT allowed to rank:")
        for r in stale_rows:
            print(f"     {r['venue']:<16} {r['stale_note']}")
        print(f"     A measurement older than {STALE_HOURS:.0f}h cannot set the headline. "
              f"Re-measure to rank it. A '*" + "' in the LP APR column marks a disqualified row: "
              f"its APR is a frozen number, NOT a live yield — and it earns no derivable dollars.")
        print("     This applies to BOTH sources: our on-chain measurement AND the aggregator's")
        print("     reported leg. An undated or frozen number does not rank, wherever it came from.")


    # A measurement we hold but cannot attribute to this row is UNRANKABLE for it — saying so beats
    # silently borrowing a neighbouring tier's number.
    ambigu = [r for r in ranked if r.get("ambiguous_note")]
    if ambigu:
        seen = set()
        print("\n  ❓ MEASUREMENT NOT ATTRIBUTABLE (row aggregates several pools):")
        for r in ambigu:
            if r["ambiguous_note"] in seen:
                continue
            seen.add(r["ambiguous_note"])
            print(f"     {r['venue']:<16} {r['ambiguous_note']}")
        print("     Ranked on the aggregator's reported fee leg instead. Needs a per-pool read "
              "to replace.")

    # A pool we ruled against must not be silently re-proposed by a ranking.
    avoided = [r for r in ranked if r.get("cat_status") == "AVOID"]
    if avoided:
        print("\n  🚫 CATALOGUED AS AVOID — flagged so a ranking cannot quietly re-propose it:")
        for r in avoided:
            reason = (r.get("cat_note") or "")[:150]
            print(f"     {r['venue']} {r['sym']}: {reason}")

    # ── the finding that matters ─────────────────────────────────────────────
    print("\n" + "=" * 100)
    print("  WHAT THIS SAYS")
    print("=" * 100)

    # Where apyBase is 0, DefiLlama sets apyReward to the ENTIRE headline, so it is not
    # saying "100% of this is emissions" — it is saying "we could not compute a fee leg, so
    # we are attributing all of it to rewards". Those are different sentences. Where we hold
    # our own measurement, we say plainly that the aggregator and the chain DISAGREE.
    emission_led = [r for r in ranked if r["apy_rew"] > 0 and (r["fee_apr"] or 0) < r["apy_rew"]]
    if emission_led:
        print("  ⚠️  HEADLINES CARRYING EMISSIONS WEIGHT — compare the fee leg, not the headline:")
        for r in emission_led:
            leg = r["fee_src"] if r.get("fee_src") in STALE_SOURCES else (
                ('%.1f%%' % r['fee_apr']) if r['fee_apr'] is not None else 'UNKNOWN')

            if r["fee_src"] == "MEASURED":
                print(f"     {r['venue']:<16} DefiLlama headline {r['apy']:>8.0f}% "
                      f"(fee leg {r['fee_apr']:.0f}%)")
                print(f"     {'':<16} .. but DefiLlama reports apyBase=0 and attributes the whole")
                print(f"     {'':<16} .. headline to rewards. WE MEASURED the fee core on-chain at")
                print(f"     {'':<16} .. {r['fee_apr']:.0f}%. The aggregator's model and the chain DISAGREE,")
                print(f"     {'':<16} .. and the on-chain accrual wins. Treat the headline as emissions.")
            elif r["fee_src"] in STALE_SOURCES:

                print(f"     {r['venue']:<16} headline {r['apy']:>8.0f}%  fee leg {leg:>8}"
                      f"  → emissions {r['apy_rew']:.0f}%  (fee leg is a frozen number, not live)")
            else:
                print(f"     {r['venue']:<16} headline {r['apy']:>8.0f}%  fee leg {leg:>8}"
                      f"  → emissions {r['apy_rew']:.0f}%")
        print("     Emissions are staking-dependent and must be sold immediately if taken.")
        print("     Per standing rule we quote the FEE CORE, never the headline.")

    # STALE rows are excluded here too: a frozen number must not be presented as a live yield.
    pure = [r for r in ranked if r["fee_apr"] is not None and r["apy_rew"] == 0
            and r.get("fee_src") not in STALE_SOURCES]

    if pure:
        print("\n  ✅ PURE-FEE POOLS (no emissions in the reported APY):")
        for r in pure:
            print(f"     {r['venue']:<16} fee APR {r['fee_apr']:>6.1f}%   "
                  f"turnover {r['turnover']:.2f}x   implied take {'%.3f%%' % (r['implied_rate']*100) if r['implied_rate'] else 'n/a'}")
        print("     These are the honest comparables — the number IS the yield, no token needed.")

    unknown = [r for r in ranked if r["fee_apr"] is None]
    if unknown:
        print("\n  ❓ FEE LEG UNKNOWN (aggregator reports 0 or nothing, no measurement of ours):")
        for r in unknown:
            print(f"     {r['venue']:<16} — a 0 here means 'cannot compute', NOT 'no fees'. "
                  f"Needs an on-chain read before it can be ranked.")

    top = ranked[0] if ranked else None
    if top and top["fee_apr"] is not None:
        # The old label said "HIGHEST FEE GENERATION" while printing the fee APR — exactly the
        # conflation Jordan corrected on 09-18 (generation is the venue's, APR is ours). Named
        # for what it actually ranks on, with the measurement's age attached.
        age = ""
        if top.get("measure_age_h") is not None:
            age = f", measured {top['measure_age_h']:.1f}h ago"
        elif top.get("measured_at"):
            age = f", dated {top['measured_at']}"
        print(f"\n  🏆 HIGHEST FEE APR: {top['venue']} at {top['fee_apr']:.1f}% "
              f"({top['fee_src']}{age}) on ${top['tvl']:,.0f} TVL")

    print("\n  📋 VENUE NOTES (security is a risk parameter, not a disqualifier)")
    for r in ranked:
        flag = " ⚠️ OUTLIER-FLAGGED" if r["outlier"] else ""
        print(f"     {r['venue']:<16} {r['audit']}{flag}")

    print("\n  ⚠️ fee APR is not a promise. It is volume x take-rate / TVL, and volume moves.")
    # The chain-decoded measurement is volume x the pool's NOMINAL fee tier, read from the pool
    # contract against real decoded Swap volume. That is stronger than aggregator arithmetic
    # (the tier is read from the contract, not assumed), but it is still NOT observed accrual —
    # it assumes every trade paid the nominal tier, and it is GROSS of protocol share. Saying
    # "actual accrual" would claim more than we measured.
    print("     Where we have our own chain-decoded measurement (real Swap volume x the tier read")
    print("     from the pool contract), that number is used instead. It is GROSS and assumes the")
    print("     nominal tier was paid — it is not observed accrual, and a fee law's protocol share")
    print("     is not yet deducted.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main())
