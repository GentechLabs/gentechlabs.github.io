#!/usr/bin/env python3
"""volatility_tracker.py — measure VOLATILITY and STABILITY, and say what to do about it.

Jordan (2026-09-23), the design:

    "We're out of the pool. We need to rebalance now of course. We have the intelligence to look
     and see, okay, what should we rebalance TO — or is it time to get OUT of the pool? ...
     once we start going up to an unseeable amount, past five or ten, maybe 20%, to where it's
     harder to reach, at that point we should look into withdrawing from the pool and switching
     over to the ASSET and holding until we can understand some type of stability.
     If we can track volatility, we can track stability. For it was the volatility that gave us
     the bid-ask strategy — because as it goes up and down rapidly, you're earning a lot more
     because a lot of the time you are going between edges."

So there are THREE answers to "what now", and they are keyed on two measurable things:

    ran far      -> EXIT to the asset and wait for stability   (the run is hard to extend)
    volatile     -> BID-ASK                                    (crossing edges earns)
    stable       -> CURVE                                      (chop around the centre earns)

VOLATILITY is measured where it actually pays us: how often the price CROSSES A BIN EDGE. That
is not a proxy — the pool charges a volatility-driven variable fee, and sitting near spot while
price walks back and forth over the edges is what a bid-ask is FOR. Two independent readings:

  * EDGE CROSSINGS — count how many times the active bin changes over a window. This is the
    literal "going between edges". Read from the chain, not from a chart.
  * REALIZED VOL — stdev of returns over the same window, so a single wild print cannot decide it.

STABILITY is the absence of both: few crossings AND small dispersion.

And the RUN-UP is measured against a reference the strategy actually cares about — the window's
LOW (how far have we come off the floor), because "harder to reach" is about what is left, not
about where we started.

NOTHING HERE MOVES MONEY. It is a reading + a verdict. The exit it may recommend is a CAPITAL
ACTION and is proposed, never taken (see exit_plan.py / hold_trigger.py).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ── thresholds (Jordan's to tune; the ladder he named is 5 / 10 / 20%) ──────────────────────
RUNUP_LADDER = (5.0, 10.0, 20.0)   # % off the window low at which leaving gets attractive
RUNUP_EXIT_PCT = 10.0              # default: propose exiting the pool at +10% off the floor
# The pool's own accumulator is the preferred reading; these are its bands.
DEFAULT_PAIR = "0x864d4E5Ee7318e97483DB7EB0912E09F161516EA"   # LFJ WAVAX/USDC, binStep 10
# ── A SUSTAINED MOVE IS VOLATILITY TOO (Jordan, 2026-09-23) ────────────────────────────
# The pool's accumulator DECAYS (decayPeriod 600 = 10 minutes). It answers "is price crossing
# edges RIGHT NOW", not "has the tape moved". A slow, one-directional 7% pullback crosses few
# edges per 10 minutes, so the accumulator reads quiet — and the tracker returned STABLE -> curve
# in the middle of the biggest move of the week.
# Caught by Jordan, watching AVAX fall $11.20 -> $10.42: "we should be doing the bid-ask because
# market conditions are saying that this is a big pullback." He was reading the MARKET; the
# instrument was reading the last ten minutes. A pullback that is still inside a bullish trend is
# the bid-ask's home turf — a WIDE band is what absorbs a directional move; a narrow curve is for
# range-bound chop.
# So a large SUSTAINED move counts as volatile in EITHER direction. Down is not "stability".
DISPLACEMENT_VOLATILE = 4.0        # |net move| >= 4% over the lookback => volatile => bid-ask

POOL_VOLATILE = 0.55               # >=55% of the accumulator ceiling => volatile => bid-ask
POOL_STABLE = 0.20

# ── THE DAILY-CLOSE CACHE (2026-09-26) ─────────────────────────────────────────────────────────
# price_series() supplies the trend input that decides LP SHAPE, and it was being called every
# 15 minutes against a rate-limited public API -- 10/10 consecutive calls returned HTTP 429 while
# the shape verdict flipped curve/bid-ask on identical pool data. Daily closes move once a day,
# so cache them for a few hours: it removes the rate-limit failure mode entirely and cannot make
# the data stale in any way that matters. See price_series() for the full failure story.
_CLOSES_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".aae-daily-closes.json")
_CLOSES_TTL_S = 4 * 3600
                 # <=20% of the ceiling => stable => curve
# Fallbacks used only when the pool read is unavailable.
EDGE_CROSS_VOLATILE = 0.60         # >=60% of samples changing bin => volatile, use a bid-ask
EDGE_CROSS_STABLE = 0.20           # <=20% of samples changing bin => stable, use a curve
MIN_SAMPLES = 8                    # below this we say UNKNOWN, never guess a regime


def _rpc():
    """Use the shared rotating reader — never hardcode an RPC (avax_rpc)."""
    import avax_rpc
    return avax_rpc.connect(timeout=45)


# ── THE POOL'S OWN VOLATILITY MEASURE (2026-09-23) ───────────────────────────────────────────
# A stopwatch over a couple of dozen samples cannot tell you what the tape has been doing for
# hours. The POOL can: LFJ keeps a `volatilityAccumulator` — a decayed running count of bin
# crossings, i.e. LITERALLY "going between edges", the thing Jordan says the bid-ask is paid for
# — and charges its variable fee in proportion to it. Reading it is better than sampling because
# it is (a) the chain's own number, (b) decayed over `decayPeriod` so it reflects recent history
# rather than this instant, and (c) the SAME number that sets what we get paid.
#
# Recovered volatility level = volatilityAccumulator / maxVolatilityAccumulator, in 0..1.
# ⚠️ MEASURED SHAPES (probed against the live pair, 2026-09-23) — do not trust a guessed ABI:
#   getStaticFeeParameters()   -> 7 words: baseFactor 5000, filterPeriod 30, decayPeriod 600,
#                                 reductionFactor 5000, variableFeeControl 40000,
#                                 protocolShare 1000, maxVolatilityAccumulator 350000
#   getVariableFeeParameters() -> 4 words: [volatilityAccumulator, volatilityReference, ...,
#                                 lastUpdated]  (e.g. 13602, 3602, ..., a unix timestamp)
# The accumulator's first word is the fee-driving quantity; the ceiling comes from the STATIC
# params. The values above are self-consistent (5000/40000/1000 match the known pool config),
# which is how the shape was confirmed rather than assumed.
STATIC_FEE_ABI = [
    {"name": "getStaticFeeParameters", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [
         {"name": "baseFactor", "type": "uint16"},
         {"name": "filterPeriod", "type": "uint16"},
         {"name": "decayPeriod", "type": "uint16"},
         {"name": "reductionFactor", "type": "uint16"},
         {"name": "variableFeeControl", "type": "uint16"},
         {"name": "protocolShare", "type": "uint16"},
         {"name": "maxVolatilityAccumulator", "type": "uint32"}]},
]
VARIABLE_FEE_SEL_ABI = [
    {"name": "getVariableFeeParameters", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [
         {"name": "volatilityAccumulator", "type": "uint24"},
         {"name": "volatilityReference", "type": "uint24"},
         {"name": "unused", "type": "uint40"},
         {"name": "lastUpdated", "type": "uint40"}]},
]


def pool_volatility(w3, pair_addr: str) -> dict:
    """The pool's OWN volatility read: accumulator vs its ceiling, plus the fee it implies.

    A decode failure is NOT a missing function (and vice versa), so this reads the two structs by
    their measured shapes and REFUSES to report a level it cannot sanity-check. An accumulator
    above its own ceiling, or a zero ceiling, means the parse is wrong — not that the pool is
    calm. Reporting a plausible-looking level from a bad parse is the whole false-value family.
    """
    from web3 import Web3
    from eth_abi import decode as abi_decode
    pair = Web3.to_checksum_address(pair_addr)
    try:
        sel_s = bytes(Web3.keccak(text="getStaticFeeParameters()")[:4])
        sel_v = bytes(Web3.keccak(text="getVariableFeeParameters()")[:4])
        raw_s = w3.eth.call({"to": pair, "data": sel_s})
        raw_v = w3.eth.call({"to": pair, "data": sel_v})
        (base_factor, filt, decay, red, var_ctl, proto,
         max_vol) = abi_decode(["uint16"] * 6 + ["uint32"], raw_s)
        words = [int.from_bytes(raw_v[i*32:(i+1)*32], "big") for i in range(len(raw_v) // 32)]
        if not words or max_vol == 0:
            return {"error": "static/var fee params not decodable into a usable shape", "level": None}
        vol_acc = words[0]
        vol_ref = words[1] if len(words) > 1 else None
        # ── SANITY GUARD: the accumulator cannot exceed its own ceiling. ──────────────────────
        if vol_acc > max_vol:
            return {"error": (f"accumulator {vol_acc:,} exceeds ceiling {max_vol:,} — the parse "
                              f"shape is wrong; refusing to report a level"), "level": None}
        level = vol_acc / max_vol
        # the fee this implies, from the pool's own law
        bin_step = int.from_bytes(w3.eth.call(
            {"to": pair, "data": bytes(Web3.keccak(text="getBinStep()")[:4])}), "big")
        base_fee = base_factor * bin_step * 10**10
        var_fee = ((vol_acc * bin_step) ** 2 * var_ctl) // 100
        return {"volatility_accumulator": int(vol_acc), "max_volatility_accumulator": int(max_vol),
                "volatility_reference": int(vol_ref) if vol_ref is not None else None,
                "decay_period": int(decay), "variable_fee_control": int(var_ctl),
                "base_fee_pct": base_fee / 1e18 * 100, "variable_fee_pct": var_fee / 1e18 * 100,
                "level": level}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "level": None}


def edge_crossings(w3, pair_addr: str, samples: int = 24, gap_s: float = 2.5) -> dict:
    """How often does the ACTIVE BIN change? That is price crossing a bin edge, literally.

    This is the measurement the bid-ask strategy is built on, so it is read from the pool
    itself. The active bin id is integer and monotone in price, so a change of id = a crossing.
    """
    from web3 import Web3
    pair = Web3.to_checksum_address(pair_addr)
    sel = Web3.keccak(text="getActiveId()")[:4]
    ids: list[int] = []
    for i in range(samples):
        try:
            ids.append(int.from_bytes(w3.eth.call({"to": pair, "data": sel}), "big"))
        except Exception:
            pass
        if i < samples - 1:
            time.sleep(gap_s)
    if len(ids) < MIN_SAMPLES:
        return {"n": len(ids), "crossings": 0, "cross_rate": None}
    moves = [abs(b - a) for a, b in zip(ids, ids[1:])]
    changes = sum(1 for m in moves if m > 0)
    return {"n": len(ids),
            "crossings": changes,
            "cross_rate": changes / max(1, len(moves)),
            "max_jump_bins": max(moves) if moves else 0,
            "net_bins": ids[-1] - ids[0]}


def realized_vol(closes: list[float]) -> float | None:
    """Stdev of log returns, in %, over whatever series is handed in."""
    if len(closes) < 3:
        return None
    import math
    rets = [math.log(b / a) for a, b in zip(closes, closes[1:]) if a > 0 and b > 0]
    if len(rets) < 2:
        return None
    mu = sum(rets) / len(rets)
    var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
    return (var ** 0.5) * 100.0


def book_range(w3, pair_addr: str, wallet: str | None) -> dict:
    """Read OUR deployed band in PRICE terms — the anchor the escape reading needs.

    Held bins are the only witness that cannot be stale (the tenant record says what we ASKED
    for; see lfj-bin-shape-recenter). Returns {lo, hi} as prices, or {error} — never a default.
    """
    if not wallet:
        return {"error": "no wallet given (set STEWARD_WALLET or --wallet)"}
    try:
        from web3 import Web3
        import fee_efficiency as FE
        pair = Web3.to_checksum_address(pair_addr)
        w = Web3.to_checksum_address(wallet)
        act = int.from_bytes(w3.eth.call(
            {"to": pair, "data": Web3.keccak(text="getActiveId()")[:4]}), "big")
        sel = Web3.keccak(text="balanceOf(address,uint256)")[:4]
        held = []
        for b in range(act - 90, act + 91):
            data = sel + bytes.fromhex(w[2:].rjust(64, "0")) + b.to_bytes(32, "big")
            if int.from_bytes(w3.eth.call({"to": pair, "data": data}), "big") > 0:
                held.append(b)
        if not held:
            return {"error": "no bins held — the book is flat, so there is no range to escape"}
        # fee_efficiency._price_at is the ONE bin->price source of truth (the hub and the
        # recenter both use it); a second copy here would eventually disagree with it.
        return {"lo": FE._price_at(w3, min(held)), "hi": FE._price_at(w3, max(held) + 1),
                "bins": len(held)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def escape_distance(spot: float, range_lo: float, range_hi: float) -> dict:
    """How far has price RUN PAST the range we can actually earn in?

    THE ANCHOR IS THE RANGE, NOT A PRICE LOW (Jordan, 2026-09-23).

    He first framed the bullish mode as *"when the market takes off or keeps escaping our
    rebalances to the up side"*, and now as going *"up to an unseeable amount ... past five or
    ten, maybe 20%, to where it's HARDER TO REACH"*. Those are the same signal: **harder to
    reach = further past the top of where we can earn.** Measured off a price low instead, a
    week-old grind reads as +47% and the tracker proposed exiting the pool — while the actual
    tape was chopping between 11.03 and 11.30 for fourteen hours, which is exactly the chop a
    curve is paid to harvest.

    So: 0% while spot is inside the band (we are earning, nothing to reach), and the escape
    percentage once spot is above range_hi. Below the band is NOT this signal — that is a bid
    ladder buying the dip, a different decision.
    """
    if not range_lo or not range_hi or spot is None:
        return {"pct": None, "inside": None}
    inside = range_lo <= spot <= range_hi
    pct = 0.0 if inside else ((spot / range_hi - 1) * 100 if spot > range_hi else 0.0)
    return {"pct": pct, "inside": inside, "range_lo": range_lo, "range_hi": range_hi,
            "above": None if inside else spot > range_hi}


def runup(series: list[float], window: int = 7) -> dict:
    """How far off a RECENT base are we — and is the move FRESH?

    Jordan (2026-09-23): *"once we start going up to an unseeable amount ... past five or ten,
    maybe 20%, to where it's HARDER TO REACH"* — that is about a FRESH vertical move running out
    of room, not about distance travelled from a month ago. Measured off the 30-day low, AVAX read
    +57.8% and the tracker proposed exiting the pool — while the actual tape was chopping between
    11.03 and 11.30 for fourteen hours. A month-old grind is not a run.

    So: anchor on the recent window's low, and report HOW RECENT the run is. A run whose high is
    days old has already been digested; only a fresh one leaves us near the hard part.
    """
    if not series:
        return {"pct": None, "fresh_hours": None, "base": None}
    tail = series[-window:] if len(series) >= window else series
    base = min(tail)
    last = tail[-1]
    pct = (last / base - 1) * 100 if base > 0 else None
    try:
        idx_hi = max(range(len(tail)), key=lambda i: tail[i])
        fresh_hours = (len(tail) - 1 - idx_hi)      # samples since the high; 0 = at the high now
    except Exception:
        fresh_hours = None
    return {"pct": pct, "fresh_hours": fresh_hours, "base": base,
            "high": max(tail), "window": len(tail)}


def price_series(days: int = 30) -> list[float]:
    """Daily AVAX closes. Uses the same public source the hold gate uses; never invents data.

    ── CACHED, WITH A FALLBACK (fixed 2026-09-26) ───────────────────────────────────────────────
    THIS CALL DECIDED OUR LP SHAPE, AND IT WAS FAILING. Measured live: **10 consecutive calls all
    raised HTTP 429**, and **30 consecutive shape reads returned curve x28 / bid-ask x2** — with
    the pool accumulator IDENTICAL (0.038211) through every one of them.

    The mechanism, and it is the false-value family in a new costume:
      * this function supplies `move_pct` to classify();
      * when it fails, `move_pct` becomes None, so the 4%-displacement branch is SKIPPED;
      * the verdict then falls through to the pool-accumulator branch, which reads 3.8% of its
        ceiling and returns CURVE.
    So **a failed off-chain price read silently became "the market is calm"**, and the shape of the
    live book flipped between curve and bid-ask depending on whether a third-party API rate-limited
    us. That is the churn: same inputs, two different books, no market event in between.

    Daily closes change at most once a day, so caching is not a compromise — it is the correct
    resolution for the data. A second source means "no answer" stops being the common case, and a
    stale cache still beats a silent shape change.
    """
    import urllib.request

    def _fetch(url: str) -> list[float]:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        return [float(p[1]) for p in d.get("prices", []) if p and p[1]]

    def _cached() -> list[float] | None:
        try:
            with open(_CLOSES_CACHE) as f:
                c = json.load(f)
            v = [float(x) for x in (c.get("closes") or [])]
            return v if len(v) > 2 else None
        except Exception:
            return None

    # 1. A FRESH CACHE WINS — the data only moves daily, so refetching it every 15 minutes buys
    #    nothing and is exactly what got us rate-limited.
    try:
        with open(_CLOSES_CACHE) as f:
            c = json.load(f)
        if (time.time() - float(c.get("at") or 0)) < _CLOSES_TTL_S:
            v = [float(x) for x in (c.get("closes") or [])]
            if len(v) > 2:
                return v
    except Exception:
        pass

    # 2. A CHAIN OF REAL SOURCES. Measured on this box: CoinGecko 429s, Binance returns 451
    #    (geo-blocked), CryptoCompare 401s, Bybit 403s — while Kraken, Coinbase and OKX all
    #    answer 200. The old single-source read was one rate limit away from silently telling the
    #    treasury the market was calm.
    def _kraken(raw):
        r = (raw.get("result") or {})
        for k, v in r.items():
            if k != "last" and isinstance(v, list) and v:
                return [float(row[4]) for row in v]              # [time,o,h,l,close,...]
        return []

    def _coinbase(raw):
        # [[time, low, high, open, close, volume], ...] newest first
        return [float(row[4]) for row in reversed(raw)] if isinstance(raw, list) else []

    def _okx(raw):
        # [["ts","o","h","l","c",...], ...] newest first
        return [float(row[4]) for row in reversed(raw.get("data") or [])]

    sources = [
        (f"https://api.coingecko.com/api/v3/coins/avalanche-2/market_chart"
         f"?vs_currency=usd&days={days}&interval=daily", _fetch),
        (f"https://api.kraken.com/0/public/OHLC?pair=AVAXUSD&interval=1440", _kraken),
        (f"https://api.exchange.coinbase.com/products/AVAX-USD/candles?granularity=86400",
         _coinbase),
        (f"https://www.okx.com/api/v5/market/candles?instId=AVAX-USDT&bar=1D"
         f"&limit={max(days, 30)}", _okx),
    ]
    for _u, _parse in sources:
        try:
            _raw = json.loads(urllib.request.urlopen(
                urllib.request.Request(_u, headers={"User-Agent": "Mozilla/5.0"}),
                timeout=30).read())
            closes = _parse(_raw)
            if len(closes) > 2:
                try:
                    tmp = _CLOSES_CACHE + ".tmp"
                    with open(tmp, "w") as f:
                        json.dump({"at": time.time(), "closes": closes,
                                   "src": _u.split("/")[2]}, f)
                    os.replace(tmp, _CLOSES_CACHE)
                except Exception:
                    pass
                return closes
        except Exception:
            continue

    # 3. STALE CACHE BEATS A SILENT SHAPE CHANGE. A day-old daily close is still a daily close.
    old = _cached()
    if old:
        return old
    raise RuntimeError("no daily closes from any source and no cache — refusing to imply calm")


def recent_tape(hours: int = 12, repo: str = "/root/repos/gentechlabs.github.io") -> dict:
    """What is the tape doing NOW? (Jordan, 2026-09-23)

    The 2-day 'sustained move' answers where price HAS been. It cannot answer whether price is
    STILL going somewhere -- and that distinction is the whole game:
        a -9% move that finished days ago  -> the market has CONSOLIDATED -> a curve's home turf
        a -9% move still in progress       -> real trend                -> a wide bid-ask
    Jordan hit exactly this: the 2-day memory kept demanding a bid-ask while the tape chopped
    mid-band, where a bid-ask earns ~20% and a curve earns ~80%.

    Source: the hub publishes `price_usd` on every refresh, and every refresh is a commit -- so
    the repo's own history IS an intraday price series, for free, at the page's cadence. Reading
    it back costs nothing and needs no new oracle.

    Returns {} when it cannot tell. An empty answer must never read as 'flat'.
    """
    import json as _json, os, glob, time as _time
    # ── WHERE THE TAPE ACTUALLY COMES FROM (fixed on write, 2026-09-23) ──────────────────
    # First draft read the hub JSON's GIT HISTORY, assuming every refresh was a commit. It is
    # not: `git log -- DeFi/defi-data-jordan.json` returns ZERO commits -- the file is
    # regenerated in place and never versioned. A whole invented data source, caught only by
    # asking the repo instead of assuming. (Same lesson as the $0.41 gas figure, same day.)
    #
    # So the tape is RECORDED rather than borrowed:
    #   1. the local append-only tape the hub refresh writes every 10 minutes (primary)
    #   2. the fee ledger's 15-minute snapshots (already running, so this works today)
    # Neither is a new oracle; both are this fleet's own published numbers read back.
    path = []
    tp = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".price-tape.json")
    try:
        raw = _json.load(open(tp))
        if isinstance(raw, list):
            cutoff = _time.time() - hours * 3600
            path = [float(s["p"]) for s in raw
                    if isinstance(s, dict) and s.get("p") and s.get("t", 0) >= cutoff]
    except Exception:
        path = []
    if len(path) < 3:
        # fall back to the fee ledger, which has been snapping price since it was built
        try:
            for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            ".fee-ledger-*.json")):
                snaps = (_json.load(open(f)) or {}).get("snapshots") or []
                cutoff = _time.time() - hours * 3600
                series = [float(s["price"]) for s in snaps
                          if isinstance(s, dict) and s.get("price") and s.get("t", 0) >= cutoff]
                if len(series) > len(path):
                    path = series
        except Exception:
            pass
    if len(path) < 3:
        return {}
    hi, lo, last = max(path), min(path), path[-1]
    rng = (hi / lo - 1) * 100
    net = (last / path[0] - 1) * 100
    return {"n": len(path), "high": hi, "low": lo, "range_pct": rng, "net_pct": net,
            "hours": hours}


def recent_is_rangebound(tape: dict, band_span_pct: float | None = None) -> bool | None:
    """True when the recent tape has gone nowhere: a small range AND a small net move.

    ── THE BAND IS THE WRONG UNIT, AND THE DOCSTRING ALREADY SAID SO (fixed 2026-09-26) ────────
    A hardcoded 2% absolute threshold was being compared against a tape measured over the WHOLE
    12-HOUR WINDOW, while the book we deploy is only ~5% wide. A 12h range of 5.44% with a net move
    of +0.10% is a tape that went up and came all the way back — CHOP — but 5.44% > 2% made it read
    as "still moving", so every trend test stayed armed and the shape stayed a bid-ask.

    Jordan, looking at exactly that tape: *"when I looked on the web page ... we were in the middle
    which means we're not earning as much at all and we would need to pivot to a curve immediately
    ... right now, where we're not really moving too much."* He was right and the rule was wrong.

    The docstring above already stated the correct test — *"a small NET with a large RANGE is chop
    (fine for either shape); a large NET with a small range is a slow drift (still directional).
    Only when neither the range nor the net is meaningful has the market genuinely gone quiet"* —
    but the code below it ANDed two absolute numbers, so a large-range chop could never be declared
    rangebound. **The rule was written down, correct, and not implemented** — the same family as the
    fee ledger's dead rebuild flag and the efficiency trigger that detected but never acted.

    The correction takes the docstring literally:
      * a MEANINGFULLY-LARGE net move  -> not rangebound (a real drift; a curve would sit on the
        wrong side of it)
      * a small net + a small range    -> rangebound (genuinely quiet)
      * a small net + a LARGE range    -> rangebound (CHOP — price is oscillating inside a band,
        which is the curve's home turf, and this is the case the old test could not see)

    `limit` stays tied to the band the caller deploys (`band_span_pct`), because "large" can only
    mean "large relative to what we are farming".
    """
    if not tape or tape.get("n", 0) < 3:
        return None                      # cannot tell -> say so, never assume calm
    rng = abs(tape.get("range_pct") or 0)
    net = abs(tape.get("net_pct") or 0)
    limit = band_span_pct if band_span_pct else 2.0
    # A real drift is what a curve cannot survive; a wide range with no net progress is chop.
    if net > limit:
        return False
    return bool(rng <= limit or net <= (limit / 2))


def classify(cross: dict, vol_pct: float | None, runup_pct: float | None,
             pool_level: float | None = None, fresh_hours: int | None = None,
             move_pct: float | None = None) -> dict:
    """The three answers, in priority order. Refuses to guess on thin data.

    The pool's own decayed accumulator (`pool_level`) is preferred for the volatility call: it
    is the chain's number, it covers recent history rather than this instant, and it is the same
    quantity that sets what we are paid. The stopwatch `cross_rate` is the fallback when the
    pool read is unavailable.

    The exit needs a run that is BOTH large AND FRESH. A month-old grind whose high is long
    digested is not "harder to reach" — it is a new base, and the tape above it may be chop we
    can still earn on. `fresh_hours` is samples since the run's high (0 = making the high now).
    """
    rate = cross.get("cross_rate")
    if pool_level is None and rate is None:
        return {"verdict": "UNKNOWN", "shape": None, "action": "NONE",
                "why": "neither the pool's accumulator nor a sampling run could be read — "
                       "a missing value is never a regime"}

    # 1. Has it run so far — and RECENTLY — that the next move is the hard part?
    #    Freshness matters as much as distance: a high set days ago has been digested, and what
    #    is left above it is often chop a curve can still earn on. Only a fresh vertical move
    #    means we are sitting at the hard part of the climb.
    RUNUP_FRESH_SAMPLES = 3          # high within the last 3 daily samples = still fresh
    if (runup_pct is not None and runup_pct >= RUNUP_EXIT_PCT
            and fresh_hours is not None and fresh_hours <= RUNUP_FRESH_SAMPLES):
        nxt = next((x for x in RUNUP_LADDER if runup_pct < x), None)
        return {"verdict": "RAN_FAR", "shape": None, "action": "PROPOSE_EXIT_HOLD_ASSET",
                "why": (f"up {runup_pct:+.1f}% off the recent base and the high is only "
                        f"{fresh_hours} sample(s) old — a FRESH vertical move with little room "
                        f"left above it (ladder {'/'.join(str(int(x)) for x in RUNUP_LADDER)}%; "
                        f"next rung {nxt if nxt else 'past the top'}). The pool's fee core no "
                        f"longer pays for the directional risk. Withdraw and hold the ASSET until "
                        f"stability, per the bullish mode. CAPITAL ACTION — proposed, never taken.")}
    runup_note = None
    if runup_pct is not None and runup_pct >= RUNUP_EXIT_PCT:
        runup_note = (f"up {runup_pct:+.1f}% off the base, but the high is {fresh_hours} samples "
                      f"old — digested, not a fresh run, so this is NOT an exit signal")

    # 2. Volatile => a bid-ask, because crossing edges is what pays.
    if pool_level is not None and pool_level >= POOL_VOLATILE:
        return {"verdict": "VOLATILE", "shape": "bid-ask", "action": "FARM_BID_ASK",
                "why": (f"the pool's own volatility accumulator is at {pool_level*100:.0f}% of "
                        f"its ceiling — it is charging the variable fee precisely because price "
                        f"is walking between edges, which is what a bid-ask is paid for")}
    if pool_level is None and rate is not None and rate >= EDGE_CROSS_VOLATILE:
        return {"verdict": "VOLATILE", "shape": "bid-ask", "action": "FARM_BID_ASK",
                "why": (f"pool accumulator unavailable; sampled crossing rate {rate*100:.0f}% "
                        f"({cross['crossings']}/{max(1,cross['n']-1)} samples, max jump "
                        f"{cross.get('max_jump_bins')} bins) — price is crossing edges")}

    # 2b. A SUSTAINED MOVE OUTRANKS A QUIET ACCUMULATOR (Jordan, 2026-09-23).
    #     This branch exists because the two branches around it both ask the same 10-minute
    #     question, and a directional trend is invisible to it. It runs BEFORE the stable branch
    #     so that "quiet right now" can never override "the tape has moved 7%".
    #     Direction is irrelevant here: a wide band catches a fall the same way it catches a
    #     rise. What matters is that price is GOING somewhere rather than chopping in place.
    #     ── BUT A FINISHED MOVE IS NOT A VOLATILE MARKET (fixed 2026-09-23) ────────────────────
    #     As written, this branch fired on the 2-day move ALONE and ran before the stable branch,
    #     so it always won. Jordan: "the auto balancer is not rebalancing ... stuck in the middle
    #     of our bid-ask ... why aren't the rules being honored?" Answer: the -9% fall of two days
    #     ago kept demanding a wide bid-ask while price chopped mid-band in ~1%, where a bid-ask
    #     earns ~20% and a curve earns ~80%. The memory of a move outlived the move.
    #     This is the MIRROR of the bug it was written to fix (a 10-min gauge blind to a 2-day
    #     trend). Both are the same error: a rule that cannot see the timescale it is asked about.
    #     Now the branch must also see the tape STILL moving. A rangebound tape overrides it.
    _tape = recent_tape()
    _rangebound = recent_is_rangebound(_tape)
    if _rangebound is True:
        return {"verdict": "STABLE", "shape": "curve", "action": "FARM_CURVE",
                "why": (f"the {move_pct:+.1f}% move of the last lookback is FINISHED: the recent "
                        f"tape has gone rangebound over {_tape.get('hours')}h "
                        f"(range {_tape.get('range_pct',0):.2f}%, net {_tape.get('net_pct',0):+.2f}%, "
                        f"{_tape.get('n')} reads). A move that has stopped is not a volatile market "
                        f"-- price is chopping where a CURVE earns on the centre.")}

    if move_pct is not None and abs(move_pct) >= DISPLACEMENT_VOLATILE:
        _dir = "down" if move_pct < 0 else "up"
        return {"verdict": "VOLATILE", "shape": "bid-ask", "action": "FARM_BID_ASK",
                "why": (f"the tape has moved {move_pct:+.1f}% over the lookback ({_dir}) while the "
                        f"10-minute accumulator reads "
                        f"{(pool_level*100 if pool_level is not None else float('nan')):.0f}% of its "
                        f"ceiling. The accumulator DECAYS in 10 minutes — it cannot see a trend. "
                        f"A sustained move in either direction is bid-ask work: a wide band absorbs "
                        f"it, a narrow curve would sit on the wrong side of it. "
                        f"(threshold {DISPLACEMENT_VOLATILE:.0f}%)")}

    # 3. Stable => a curve, which earns on small chop around the centre.
    if pool_level is not None and pool_level <= POOL_STABLE:
        return {"verdict": "STABLE", "shape": "curve", "action": "FARM_CURVE",
                "why": (f"the pool's accumulator sits at {pool_level*100:.0f}% of its ceiling"
                        + (f" and realized vol is {vol_pct:.2f}%" if vol_pct is not None else "")
                        + " — no edges being crossed to earn on, so a curve earns on chop "
                          "around the centre instead"
                        + (f". NOTE: {runup_note}" if runup_note else ""))}
    if pool_level is None and rate is not None and rate <= EDGE_CROSS_STABLE:
        return {"verdict": "STABLE", "shape": "curve", "action": "FARM_CURVE",
                "why": (f"pool accumulator unavailable; sampled crossing rate only "
                        f"{rate*100:.0f}% — no edges being crossed to earn on")}

    shown = f"{pool_level*100:.0f}%" if pool_level is not None else f"{(rate or 0)*100:.0f}%"
    return {"verdict": "IN_BETWEEN", "shape": None, "action": "HOLD_SHAPE",
            "why": (f"volatility reads {shown} — between the volatile "
                    f"({POOL_VOLATILE*100:.0f}%) and stable ({POOL_STABLE*100:.0f}%) thresholds. "
                    f"That is not a regime change: stay in the shape you hold"
                    + (f". NOTE: {runup_note}" if runup_note else ""))}


def main() -> int:
    ap = argparse.ArgumentParser(description="measure volatility/stability and say what to do")
    ap.add_argument("--pair", default="0x864d4E5Ee7318e97483DB7EB0912E09F161516EA",
                    help="LFJ pair (default: our WAVAX/USDC book)")
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--gap", type=float, default=2.5, help="seconds between bin samples")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--move-days", type=int, default=2,
                    help="lookback for the SUSTAINED move (net % over N daily closes). Default 2: "
                         "long enough to see a pullback, short enough that a month-old grind is "
                         "not mistaken for one")
    ap.add_argument("--runup-window", type=int, default=7,
                    help="samples back to anchor the fallback run-up (daily closes)")
    ap.add_argument("--wallet", default=None,
                    help="wallet whose deployed band anchors the escape reading "
                         "(default: $STEWARD_WALLET)")
    ap.add_argument("--range-lo", type=float, default=None,
                    help="bottom of OUR earning range (price) — anchors the escape reading")
    ap.add_argument("--range-hi", type=float, default=None,
                    help="top of OUR earning range (price) — the 'harder to reach' anchor")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    w3 = _rpc()
    if a.wallet is None:
        import os
        a.wallet = os.environ.get("STEWARD_WALLET")
    pool = pool_volatility(w3, a.pair)          # the preferred reading: the pool's own number
    cross = edge_crossings(w3, a.pair, a.samples, a.gap)   # fallback + a live confirmation

    # ── the anchor that matters: how far past OUR RANGE is price? ─────────────────────────────
    lo, hi = a.range_lo, a.range_hi
    if lo is None or hi is None:
        book = book_range(w3, a.pair, a.wallet)
        lo, hi = book.get("lo"), book.get("hi")
        if lo is None:
            print(f"  ⚠️  could not read the deployed range ({book.get('error')}) — the escape "
                  f"reading needs OUR band, so it will fall back to the weaker price-window "
                  f"anchor rather than guess")
    vol_pct, ru = None, {"pct": None, "fresh_hours": None}
    esc = {"pct": None, "inside": None}
    move_pct = None
    try:
        closes = price_series(a.days)
        spot = closes[-1] if closes else None
        # ── THE SUSTAINED MOVE (Jordan, 2026-09-23) ───────────────────────────────────
        # The pool's accumulator decays in 10 minutes, so a slow trend is invisible to it. This
        # is the reading Jordan was making by eye when he called the pullback. Guarded: a short
        # series must read None, and None never classifies — a missing value is not a regime.
        if spot and len(closes) > a.move_days:
            base = closes[-1 - a.move_days]
            if base:
                move_pct = (spot / base - 1) * 100
        if move_pct is None:
            print(f"  ⚠️  sustained-move lookback unreadable ({len(closes) if closes else 0} closes "
                  f"for {a.move_days}d) — not classifying on an absent value", file=sys.stderr)
        if lo and hi and spot:
            esc = escape_distance(spot, lo, hi)
        vol_pct = realized_vol(closes)
        ru = runup(closes, a.runup_window)
        runup_pct = esc["pct"] if esc.get("pct") is not None else ru.get("pct")
    except Exception as e:
        runup_pct = None
        print(f"  ⚠️  price series unavailable ({type(e).__name__}) — run-up and realized vol "
              f"will read UNKNOWN rather than guessed", file=sys.stderr)

    v = classify(cross, vol_pct, runup_pct, pool.get("level"), ru.get("fresh_hours"),
                 move_pct=move_pct)
    out = {"pool": pool, "cross": cross, "realized_vol_pct": vol_pct,
           "runup": ru, "runup_from_low_pct": runup_pct,
           "move_pct": move_pct, "move_days": a.move_days, **v}
    if a.json:
        print(json.dumps(out, indent=2))
        return 0

    print("=" * 92)
    print("  VOLATILITY / STABILITY — and what to do about it")
    print("=" * 92)
    if pool.get("level") is not None:
        print(f"  [window {pool.get('decay_period', '?')}s — a ~10-MINUTE reading, "
              f"NOT a trend reading]")
        print(f"  POOL volatility  {pool['level']*100:5.1f}% of ceiling"
              f"   (accumulator {pool['volatility_accumulator']:,} / max "
              f"{pool['max_volatility_accumulator']:,}, decay {pool['decay_period']})"
              f"   <- the pool's OWN measure; this is what sets the variable fee")
    else:
        print(f"  POOL volatility  UNREADABLE ({pool.get('error')})")
    print(f"  edge crossings   {cross['crossings']}/{max(1, cross['n']-1)} samples changed bin"
          f"   rate {('%.0f%%' % (cross['cross_rate']*100)) if cross['cross_rate'] is not None else 'n/a'}"
          f"   max jump {cross.get('max_jump_bins')} bins   net {cross.get('net_bins'):+d} bins")
    print(f"  realized vol     {('%.2f%%' % vol_pct) if vol_pct is not None else 'UNKNOWN'}"
          f"   over {a.days}d of daily closes")
    # ── EVERY NUMBER CARRIES ITS WINDOW (2026-09-23) ─────────────────────────────────
    # Four defects in one day came from a confident number measured over the WRONG WINDOW: a
    # 24-second stopwatch judging a day, a 10-minute accumulator judging a 2-day trend, a month-low
    # anchor judging a fresh run. A number whose output cannot say what PERIOD it measured WILL be
    # read as the period the reader cares about. That is not a bug in the reader — it is a missing
    # field in the output. See instrument_contract.py, which proves each instrument can read BOTH
    # low and high and refuses to let one answer a question longer than its window.
    print(f"  sustained move   {('%.2f%%' % move_pct) if move_pct is not None else 'UNKNOWN'}"
          f"   net over {a.move_days}d   "
          + (f"<- >= {DISPLACEMENT_VOLATILE:.0f}% either way = a TREND the accumulator cannot see"
             if (move_pct is not None and abs(move_pct) >= DISPLACEMENT_VOLATILE)
             else "(inside the quiet band)"))
    # Show the anchor that actually decides: distance past OUR band. The price-window run-up is
    # only the fallback, and printing it as the headline is how it proposed an exit on a tape
    # that was quietly chopping (2026-09-23).
    if esc.get("inside") is not None:
        state = ("INSIDE our band — earning, nothing escaping"
                 if esc["inside"] else
                 ("ABOVE our band by %.1f%%" % esc["pct"]) if esc.get("above")
                 else "below our band (a bid ladder buying the dip)")
        print(f"  escape vs band   {state}   "
              f"band ${esc.get('range_lo'):.4f}–${esc.get('range_hi'):.4f}"
              f"   (exit ladder {'/'.join(str(int(x)) for x in RUNUP_LADDER)}%, "
              f"proposes exit at +{RUNUP_EXIT_PCT:.0f}% ABOVE the band)")
        if esc["inside"] and runup_pct is not None and runup_pct >= RUNUP_EXIT_PCT:
            print(f"  (fallback price-window run-up {runup_pct:+.1f}% off {ru.get('window')}d low "
                  f"is NOT used — it measures a month-old grind, not room left above us)")
    else:
        print(f"  run-up off {ru.get('window')}d low  "
              f"{('%.1f%%' % runup_pct) if runup_pct is not None else 'UNKNOWN'}"
              f"   (NO band read — falling back to the weaker anchor; exit ladder "
              f"{'/'.join(str(int(x)) for x in RUNUP_LADDER)}%)")
    print()
    print(f"  VERDICT   {v['verdict']}   ->   shape {v['shape'] or '—'}   action {v['action']}")
    print(f"    {v['why']}")
    print()
    if v["action"] == "PROPOSE_EXIT_HOLD_ASSET":
        print("  ⚠️  This is a CAPITAL ACTION. Nothing here moves money — it is a proposal, and")
        print("      Jordan owns it. exit_plan.py --mode HOLD_TOKEN is the rehearsed sequence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
