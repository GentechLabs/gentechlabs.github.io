#!/usr/bin/env python3
"""
duty_cycle.py — UPTIME / DUTY CYCLE: how long the capital was actually in the pool and
earning, measured between rebalances.

Jordan, 2026-09-25: *"I have an idea for another statistic we can add to both my hub and my
cousin's hub. Why don't we add the amount of hours that we've been active inside the pool
between each rebalance? I think that would also show us the benefits of what we're doing
versus doing it manually because you're able to rebalance and do stuff autonomously now."*

That is the right question, because it isolates the only thing autonomy actually buys: a manual
operator cannot re-center at 3am, so their capital sits OUT of range (deployed, earning zero)
for hours; this machine re-centers within minutes. The ratio between the two IS the value of
autonomy, so the metric separates them rather than reporting a single "hours in the pool".

════════════════════════════════════════════════════════════════════════════════════════════
THE METRIC, PRECISELY
════════════════════════════════════════════════════════════════════════════════════════════
A DLMM (LFJ Liquidity Book) position earns ONLY while the pool's active bin sits inside the
bins we hold. So at every moment the book is in exactly one of three states:

  IN RANGE      — deployed AND spot inside our bin band   -> earning fees.
  OUT OF RANGE  — deployed AND spot outside our bin band  -> capital at work, earning ZERO.
  FLAT          — no position at all (capital withdrawn to the wallet) -> not even deployed.

The headline number is the IN-RANGE SHARE of DEPLOYED time. FLAT time is reported separately and
is deliberately NOT folded into "out of range": a book that was withdrawn is a different decision
from a book that drifted, and merging them cannot tell "we chose to sit out" from "we failed to
re-center".

WHAT COUNTS AS A REBALANCE (and how it was identified)
  A rebalance is a withdraw -> redeploy CYCLE, identified ON CHAIN from the tenant wallet's own
  transactions:
    * withdraw leg = a successful `removeLiquidity` (selector 0xc22159b6) sent by the wallet to
      the LFJ router 0x18556DA13313f3532c54711497A8FedAC273220E.
    * redeploy legs = the `addLiquidity` txs (0xa3c7271a) that follow it, whose decoded `to` /
      `refundTo` field is the tenant's own wallet.
  NOT counted: approvals (0x095ea7b3, 0xe584b654, 0xa22cb465) and swaps (0x2a443fae) — a swap
  funds a redeploy or compounds fees but does not move the book, so it is not a repositioning.
  Each `removeLiquidity` begins exactly one rebalance cycle; a curve is built as two single-sided
  legs, so a cycle normally contains one remove and two adds.

THE BAND IS READ FROM THE DEPLOY ITSELF, NOT FROM A CONFIG
  Every `addLiquidity` call carries its own geometry: `activeIdDesired` and `deltaIds`. The bins
  deployed are `activeIdDesired + deltaId`, so the band in force for an interval is the UNION of
  the bins deposited by the adds that built it, and its price edges come from the pool's own
  bin-price law using the `binStep` carried in that same calldata. Nothing is read from a config
  file or from a label that may have drifted.

THE PRICE PATH
  GeckoTerminal OHLCV for THIS POOL (the LFJ WAVAX/USDC pair), so the instrument measures the
  pool's own traded price rather than a proxy. Each candle is classified against the band in
  force over the part of its span that falls in that interval:
    * candle high/low entirely inside the band   -> IN RANGE for that span
    * entirely outside the band                  -> OUT OF RANGE
    * straddling a band edge                     -> UNRESOLVED — reported, never guessed
  A candle spanning a rebalance is split across the two intervals in proportion to the overlap.

  Because a straddle is genuinely unknowable at candle resolution, the share is reported as a
  BOUNDED range, not a single confident point: `in_range_share_low_pct` treats every unresolved
  span as out of range and `in_range_share_high_pct` treats it as in range, with the best
  estimate over RESOLVED spans in between. The unresolved share is always stated.

SOURCES, AND WHY THESE (durability is the point)
  * Rebalances — the CHAIN, via a block-explorer indexer (Snowtrace API, `api.routescan.io` as a
    configured alternate). This is the transaction record itself: it survives a machine restart,
    it cannot be silently rotated away like a cron log, and it is independent of any local state.
    There is NO existing local history file of rebalance timestamps — `.steward-recenter-state-
    <tenant>.json` carries a single `last_action_ts` and nothing else, so it cannot carry this
    metric. It is used only as a CROSS-CHECK, which is exactly what a one-point record is good
    for. The chain is the source.
  * Price path — GeckoTerminal OHLCV for the pool address (a public index of the pool's trades).
  * Current live band — the caller's own chain read, passed in, so the OPEN interval is the live
    book rather than a replay of the last decoded deploy.

HONEST LIMITS (part of the metric, not a footnote)
  * Candle resolution bounds precision. An excursion that both starts and ends inside one candle
    is invisible; that is what the unresolved share and the low/high bounds quantify. The
    resolution actually used is reported with every window.
  * Addresses are attributed by transaction TIME, so a withdraw and its redeploy minutes later are
    one cycle, and capital is counted FLAT only for whole candle spans.
  * Anyone signing with the tenant wallet counts as a "rebalance" by this definition — the metric
    does not distinguish the autonomous loop from a human running the same script.
  * `window_hours` is bounded by how far back the price source reaches, so the "since inception"
    window starts at the earliest pool candle, not necessarily at the first-ever rebalance.

FAIL CLOSED
  If the explorer or the price source cannot be read, this module returns {"status":"unknown",
  "error":...} and the hub renders an explicit UNKNOWN. It never returns zeros, and it never
  presents a stale cache entry as a live read.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(globals().get("__file__") or (sys.argv and sys.argv[0]) or "."))

# ── Sources ──────────────────────────────────────────────────────────────────────────────────
# An EXPLORER INDEX is not an RPC endpoint: this is the chain's own transaction record served by
# an indexer, and it is the only practical way to enumerate a wallet's FULL history (JSON-RPC has
# no "list my transactions" method, and a public node will not serve archive `eth_getLogs` across
# a 17-day block range — measured: the free getLogs endpoint truncates at 100 logs per query).
# Overridable so the honest-degradation path can be exercised deliberately.
EXPLORER = os.environ.get("DUTY_CYCLE_EXPLORER") or "https://api.snowtrace.io/api"
PRICE_BASE = os.environ.get("DUTY_CYCLE_PRICE_BASE") or "https://api.geckoterminal.com/api/v2"
OFFLINE = bool(os.environ.get("DUTY_CYCLE_OFFLINE"))

LFJ_ROUTER = "0x18556da13313f3532c54711497a8fedac273220e"
LFJ_PAIR = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
NETWORK = "avax"

SEL_ADD = "0xa3c7271a"        # addLiquidity((...)) liquidityParameters
SEL_REMOVE = "0xc22159b6"     # removeLiquidity(tokenX,tokenY,binStep,...,ids,amounts,to,deadline)

# ABI of the addLiquidity struct (verified against live calldata 2026-09-25: activeIdDesired
# 8363296, deltaIds -13..-2 (bid) and 1..13 (ask) = band 8363283..8363309, which is exactly the
# band the Position Watchdog reported for the same block).
_ADD_TYPES = ("(address,address,uint256,uint256,uint256,uint256,uint256,uint256,uint256,"
              "int256[],uint256[],uint256[],address,address,uint256)")

BIN_STEP_FALLBACK = 10        # only if the calldata itself somehow lacks it
MAX_TX_PAGES = 6              # 6 x 1000 txs: a full history, bounded
HTTP_TIMEOUT = 25
CACHE_TTL = int(os.environ.get("DUTY_CYCLE_CACHE_TTL") or 240)
CANDLE_SECONDS = {"minute": 60, "hour": 3600, "day": 86400}
_SERIES_MEMO: dict = {}       # (tf, aggregate, want_start, max_calls) -> (candles, covered, step)
# The public price index allows ~30 requests/minute. Pacing is a GLOBAL minimum interval between
# outgoing price calls, because a burst fails with 429 and a throttled read then has to become an
# UNKNOWN — which is honest but useless every ten minutes. Measured: 0.7s pacing (85/min) 429s.
_PRICE_MIN_INTERVAL = float(os.environ.get("DUTY_CYCLE_PRICE_INTERVAL") or 2.5)
_PRICE_LAST = [0.0]


def _throttle_price() -> None:
    gap = time.time() - _PRICE_LAST[0]
    if gap < _PRICE_MIN_INTERVAL:
        time.sleep(_PRICE_MIN_INTERVAL - gap)
    _PRICE_LAST[0] = time.time()


class _BudgetExpired(Exception):
    """The wall-clock budget for one tenant's measurement ran out."""


def _cache_path(name: str) -> str:
    return os.path.join(HERE, f".duty-cycle-cache-{name}.json")


_CACHE_ERRORS: list = []      # cache files that could not be parsed, surfaced in the payload


def _cache_get(name: str, ttl: int = CACHE_TTL):
    """A cached blob, or None.

    A cache MISS is safe: it means re-read the actual source. A cache file that EXISTS but cannot
    be parsed is a different thing and is recorded rather than ignored — silently treating a
    corrupt reading as "no reading" is how a damaged instrument becomes invisible.
    """
    if ttl <= 0:
        return None
    p = _cache_path(name)
    if not os.path.exists(p):
        return None
    try:
        blob = json.load(open(p))
        if time.time() - float(blob.get("_at") or 0) <= ttl:
            return blob.get("data")
    except Exception as e:                                            # noqa: BLE001
        _CACHE_ERRORS.append(f"{os.path.basename(p)}: {type(e).__name__}: {e}")
        return None                                                   # re-read the real source
    return None


def _cache_put(name: str, data) -> None:
    try:
        json.dump({"_at": time.time(), "data": data}, open(_cache_path(name), "w"))
    except Exception:
        pass


def _get_json(url: str, tries: int = 3, timeout: int = HTTP_TIMEOUT, max_wait: float = 8.0):
    """GET + parse. RAISES on failure — a caller must never mistake an unreadable source for an
    empty one (the 'instrument failure rendered as a zero' family).

    429-aware, and BOUNDED: the public price index is rate-limited, and a rate limit is a
    CAPABILITY limit, not an answer. It backs off (honouring Retry-After when offered, capped at
    `max_wait` per attempt) and then still RAISES, so a throttled read becomes an explicit UNKNOWN
    instead of an empty series. The cap matters as much as the retry: an unbounded backoff inside a
    hub build is what turns one throttled call into a timed-out page.
    """
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "gentech-treasury/1",
                                                       "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if r.status != 200:
                    raise RuntimeError(f"HTTP {r.status}")
                return json.loads(r.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as e:                          # noqa: PERF203
            last = e
            if e.code == 429:
                wait = 0.0
                try:
                    wait = float(e.headers.get("Retry-After") or 0)
                except Exception:                                    # noqa: BLE001
                    wait = 0.0
                time.sleep(min(max(wait, 1.5 * (i + 1)), max_wait))
            else:
                time.sleep(min(0.8 * (i + 1), max_wait))
        except Exception as e:                                        # noqa: BLE001
            last = e
            time.sleep(min(0.8 * (i + 1), max_wait))
    raise RuntimeError(f"source unreadable: {type(last).__name__}: {last}")


# ── 1. The rebalance record (chain) ──────────────────────────────────────────────────────────

def fetch_wallet_txs(wallet: str, use_cache: bool = True) -> list:
    """Every tx the tenant wallet has ever sent, from the chain's own index."""
    if OFFLINE:
        raise RuntimeError("rebalance source forced offline (DUTY_CYCLE_OFFLINE)")
    key = f"txs-{wallet.lower()}"
    if use_cache:
        hit = _cache_get(key)
        if hit is not None:
            return hit
    out, page = [], 1
    while page <= MAX_TX_PAGES:
        q = urllib.parse.urlencode({"module": "account", "action": "txlist", "address": wallet,
                                    "page": page, "offset": 1000, "sort": "asc"})
        d = _get_json(f"{EXPLORER}?{q}")
        res = d.get("result")
        # An explorer ERROR is not an empty history: "No transactions found" is the empty case,
        # anything else (a bad key, a rate limit) must abort rather than read as "no rebalances".
        if isinstance(res, dict) or res is None:
            msg = str(d.get("message") or "")
            if "no transactions found" in msg.lower():
                res = []
            else:
                raise RuntimeError(f"explorer returned no tx list: {msg[:120]}")
        out.extend(res)
        if len(res) < 1000:
            break
        page += 1
    if use_cache:
        _cache_put(key, out)
    return out


def position_mutating_txs(txs: list, wallet: str) -> list:
    """Successful txs from this wallet that MOVE the book: addLiquidity / removeLiquidity."""
    w = wallet.lower()
    out = []
    for t in txs:
        try:
            if str(t.get("txreceipt_status", "1")) == "0" or str(t.get("isError") or "0") == "1":
                continue
            if (t.get("from") or "").lower() != w:
                continue
            if (t.get("to") or "").lower() != LFJ_ROUTER:
                continue
            sel = (t.get("methodId") or (t.get("input") or "0x")[:10] or "").lower()
            if sel not in (SEL_ADD, SEL_REMOVE):
                continue
            ts = int(t.get("timeStamp") or 0)
            if ts <= 0:
                continue
            out.append({"ts": ts, "kind": "add" if sel == SEL_ADD else "remove",
                        "hash": t.get("hash"), "block": int(t.get("blockNumber") or 0),
                        "input": t.get("input") or ""})
        except Exception:                                            # noqa: BLE001
            continue
    out.sort(key=lambda x: x["ts"])
    return out


def decode_add(input_hex: str):
    """activeIdDesired / deltaIds / binStep / LP recipient from addLiquidity calldata.
    None when the call cannot be decoded — a decode failure is NOT treated as 'no band'."""
    try:
        from eth_abi import decode as _decode
        raw = bytes.fromhex(input_hex[10:] if input_hex.startswith("0x") else input_hex)
        v = _decode([_ADD_TYPES], raw)[0]
        return {"binStep": int(v[2]), "activeIdDesired": int(v[7]),
                "deltaIds": [int(x) for x in v[9]],
                "to": str(v[12]).lower(), "refundTo": str(v[13]).lower()}
    except Exception:                                                # noqa: BLE001
        return None


def bin_price(bin_id: int, bin_step: int) -> float:
    """LFJ bin price: (1 + step/1e4)^(id - 2^23) * 10^(decX - decY) — WAVAX 18dp, USDC 6dp.
    The same law the hub's own collector uses (`price_of`), deliberately not re-derived."""
    return (1 + bin_step / 10000.0) ** (bin_id - 8388608) * (10 ** (18 - 6))


def build_timeline(muts: list, wallet: str):
    """Deployed intervals + rebalance cycles from the on-chain record.

    An interval runs from the completion of a deploy to the next withdraw. The book is FLAT
    between a withdraw that was not followed by a redeploy and the next deploy.
    """
    intervals, cycles = [], []
    cur_band = None
    open_start = None
    last_step = None
    cur_cycle = None

    for tx in muts:
        if tx["kind"] == "remove":
            if open_start is not None:
                intervals.append({"start": open_start, "end": tx["ts"],
                                  "band": cur_band, "closed_by": tx["hash"]})
                open_start = None
            cur_band = None
            cur_cycle = {"start": tx["ts"], "remove_tx": tx["hash"], "remove_block": tx["block"],
                         "adds": 0, "end": None, "band": None}
            cycles.append(cur_cycle)
        else:                                   # add = a redeploy leg, or a top-up
            dec = decode_add(tx["input"])
            if dec is None:
                # Cannot read this leg's geometry: never invent a band for it.
                if open_start is None:
                    open_start = tx["ts"]
                if cur_cycle:
                    cur_cycle["adds"] += 1
                    cur_cycle["end"] = tx["ts"]
                continue
            if dec["to"] != wallet.lower() and dec["refundTo"] != wallet.lower():
                continue                        # not this book's liquidity
            bins = [dec["activeIdDesired"] + d for d in dec["deltaIds"]] \
                or [dec["activeIdDesired"]]
            step = dec["binStep"] or BIN_STEP_FALLBACK
            last_step = step
            if cur_band is None:
                cur_band = [min(bins), max(bins), step]
            else:
                cur_band = [min(cur_band[0], min(bins)), max(cur_band[1], max(bins)), step]
            if open_start is None:
                open_start = tx["ts"]
            if cur_cycle:
                cur_cycle["adds"] += 1
                cur_cycle["end"] = tx["ts"]
                cur_cycle["band"] = {"lo_bin": cur_band[0], "hi_bin": cur_band[1],
                                     "bin_step": step, "bins": cur_band[1] - cur_band[0] + 1}

    now = int(time.time())
    if open_start is not None:
        intervals.append({"start": open_start, "end": now, "band": cur_band,
                          "closed_by": None, "open": True})
    for iv in intervals:
        # the range's true top is the UPPER edge of the top bin, p(max+1) — the hub has always
        # used max+1, and two definitions of the same range would be two truths.
        iv["lo_px"] = bin_price(iv["band"][0], iv["band"][2]) if iv["band"] else None
        iv["hi_px"] = bin_price(iv["band"][1] + 1, iv["band"][2]) if iv["band"] else None
    return intervals, cycles, (last_step or BIN_STEP_FALLBACK)


# ── 2. The price path (this pool's own candles) ──────────────────────────────────────────────

def fetch_candles(timeframe: str = "minute", aggregate: int = 1, limit: int = 1000,
                  before_ts: int | None = None):
    """OHLCV for THIS pool from GeckoTerminal. [ts, o, h, l, c], oldest first."""
    if OFFLINE:
        raise RuntimeError("price source forced offline (DUTY_CYCLE_OFFLINE)")
    limit = min(int(limit), 1000)
    key = f"candles-{NETWORK}-{timeframe}-{aggregate}-{limit}-{before_ts or 'now'}"
    # A page fetched with before_timestamp is HISTORY: those candles can never change, so it is
    # cached long. The head page is cached for 15 minutes — this metric is a 7-day duty cycle and
    # does not need to be fresher than the hub's own 10-minute cadence, and every extra fetch is
    # one more chance of a 429 on a rate-limited public index.
    hit = _cache_get(key, ttl=(900 if before_ts is None else 6 * 3600))
    if hit is not None:
        return hit
    url = (f"{PRICE_BASE}/networks/{NETWORK}/pools/{LFJ_PAIR}/ohlcv/{timeframe}"
           f"?aggregate={aggregate}&limit={limit}")
    if before_ts:
        url += f"&before_timestamp={int(before_ts)}"
    _throttle_price()
    d = _get_json(url)
    lst = (((d or {}).get("data") or {}).get("attributes") or {}).get("ohlcv_list") or []
    lst = [[int(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4])] for c in lst]
    lst.sort(key=lambda c: c[0])
    if not lst:
        raise RuntimeError("price source returned no candles")
    _cache_put(key, lst)
    return lst


def coingecko_prices(days: int, step_hint: int) -> list:
    """SECOND, INDEPENDENT PRICE INDEX — CoinGecko AVAX/USD, as [ts, p,p,p,p, span].

    Why a fallback exists at all: the per-pool candle index 429s under load (measured: a 1000-candle
    request and a 5-candle request three seconds apart, one 200 and one 429), and a rate limit is a
    CAPABILITY limit, not a reading — it must never become "no data", and it must never become the
    only reason the hub cannot show the statistic. A different index answering the same question is
    the fix, and which one answered is recorded in the payload rather than silently swapped.

    This is AVAX/USD rather than the pool's own candle, and it is a POINT SAMPLE (no OHLC), so a
    stroke between samples is invisible. `span` therefore carries the real gap to the next sample,
    and the payload says which index was used and at what resolution.
    """
    days = max(1, min(90, int(days)))
    key = f"cg-{days}"
    hit = _cache_get(key, ttl=900)
    if hit is not None:
        return hit
    _throttle_price()
    d = _get_json(f"https://api.coingecko.com/api/v3/coins/avalanche-2/market_chart"
                  f"?vs_currency=usd&days={days}")
    pts = [[int(t) // 1000, float(p)] for t, p in (d.get("prices") or [])]
    pts.sort(key=lambda x: x[0])
    if not pts:
        raise RuntimeError("CoinGecko returned no prices")
    # A sample stands for the time until the NEXT sample — its REAL gap, not a nominal step. The
    # first attempt capped every span at the requested step, and where the API returned hourly data
    # for a 30-minute request that silently discarded HALF the window (measured: 541h accounted of
    # an 1083h window). A cap is still needed so one hole in the series cannot claim a day, so the
    # cap is twice the MEDIAN gap, which is a property of the data rather than of the request.
    gaps = [pts[i + 1][0] - pts[i][0] for i in range(len(pts) - 1)] or [step_hint]
    med = sorted(gaps)[len(gaps) // 2]
    cap = max(60, min(4 * med, 6 * 3600))
    out = []
    for i, (ts, p) in enumerate(pts):
        nxt = pts[i + 1][0] if i + 1 < len(pts) else ts + med
        out.append([ts, p, p, p, p, max(1, min(nxt - ts, cap))])
    _cache_put(key, out)
    return out


_PRICE_NOTE: list = [None]      # what actually answered: recorded, never assumed


def candle_series(timeframe: str, aggregate: int, want_start: int, max_calls: int = 4):
    """The pool's OHLCV series back to (at least) want_start: (candles, covered, step).

    Primary source = GeckoTerminal candles for THIS pool. If it cannot be read, the second index
    (CoinGecko AVAX/USD) answers instead and the substitution is recorded in _PRICE_NOTE.

    COST IS THE POINT HERE. Walking 1000-candle pages backwards costs one HTTP call each (and the
    public index rate-limits), so the assembled history is cached SEPARATELY from the head:

      * the assembled series is cached for 6h — candles older than the newest page cannot change;
      * each build re-reads at most the HEAD page (15-minute TTL) and merges it in.

    Coverage is REPORTED, never assumed: if the source will not reach back far enough the window
    shrinks and says so.
    """
    memo_key = (timeframe, aggregate, want_start, max_calls)
    if memo_key in _SERIES_MEMO:
        return _SERIES_MEMO[memo_key]
    step = CANDLE_SECONDS[timeframe] * aggregate
    gt_key = f"series-gt-{timeframe}-{aggregate}"
    cg_key = f"series-cg-{timeframe}-{aggregate}"
    try:
        # ── PRIMARY: this pool's own candles ─────────────────────────────────────────────────
        by_ts = {}
        for c in (_cache_get(gt_key, ttl=6 * 3600) or []):
            by_ts[c[0]] = c
        head = fetch_candles(timeframe, aggregate, 1000, None)
        for c in head:
            by_ts[c[0]] = [c[0], c[1], c[2], c[3], c[4], step]
        covered = min(by_ts)
        calls = 1
        while covered is not None and covered > want_start and calls < max_calls:
            chunk = fetch_candles(timeframe, aggregate, 1000, covered)
            calls += 1
            for c in chunk:
                by_ts[c[0]] = [c[0], c[1], c[2], c[3], c[4], step]
            covered = min(by_ts)
            if len(chunk) < 1000:
                break                               # source has no more history
            if calls < max_calls:
                time.sleep(0.7)
        _PRICE_NOTE[0] = _PRICE_NOTE[0] or {
            "index": "GeckoTerminal", "instrument": f"pool {LFJ_PAIR} own OHLCV",
            "shape": "OHLC (high/low known, so band-edge straddles are measured)"}
        _cache_put(gt_key, [by_ts[k] for k in sorted(by_ts)])
    except Exception as e_gt:                                        # noqa: BLE001
        # ── SECOND, INDEPENDENT INDEX ────────────────────────────────────────────────────────
        # A rate limit is a capability limit, not an absence of data, so the other index answers
        # before the metric is declared unmeasurable — and which one answered is recorded.
        #
        # SINGLE-SOURCED, never blended: the fallback REPLACES the cached candle history rather
        # than merging into it. Two indices have different sample grids and different resolutions,
        # and a series stitched from both has a provenance nobody can state — which is exactly the
        # kind of number that looks precise and is not.
        try:
            days = max(1, int((time.time() - want_start) / 86400) + 1)
            by_ts = {c[0]: c for c in coingecko_prices(days, 3600 if days >= 2 else 300)}
            covered = min(by_ts)
            _PRICE_NOTE[0] = {"index": "CoinGecko (fallback — GeckoTerminal unavailable)",
                              "instrument": "AVAX/USD market prices",
                              "shape": ("point samples, so an excursion that starts and ends "
                                        "between samples is invisible"),
                              "why": str(e_gt)[:120]}
            _cache_put(cg_key, [by_ts[k] for k in sorted(by_ts)])
        except Exception as e_cg:                                    # noqa: BLE001
            raise RuntimeError(f"both price indices failed — per-pool candles: {e_gt}; "
                               f"market prices: {e_cg}")
    out = [by_ts[k] for k in sorted(by_ts)]
    _SERIES_MEMO[memo_key] = (out, covered, step)
    return _SERIES_MEMO[memo_key]


def classify(candle, lo_px, hi_px) -> str:
    """IN / OUT / UNRESOLVED for one candle span against one band. Uses the candle's own
    high/low, so an excursion inside the candle is caught when the candle reaches past the edge."""
    if lo_px is None or hi_px is None:
        return "flat"
    h, l = candle[2], candle[3]         # index 5 is the candle's own span; never assume a shape
    if l >= lo_px and h <= hi_px:
        return "in"
    if h < lo_px or l > hi_px:
        return "out"
    return "unresolved"


def measure(intervals, candles, step: int, win_start: int, win_end: int,
            live_band=None) -> dict:
    """Attribute candle spans to IN / OUT / UNRESOLVED / FLAT across a window.

    A candle carries its OWN span at index 5 when the series is not uniformly spaced (the fallback
    index is point-sampled, so a sample stands for the gap until the next one). Using a single
    assumed step there would attribute the wrong amount of time to the wrong state.
    """
    durs = {"in": 0.0, "out": 0.0, "unresolved": 0.0, "flat": 0.0}
    ivs = sorted(intervals, key=lambda i: i["start"])
    # SLOT GRID, not an interval walk. Each slot is filled by exactly ONE candle (first writer
    # wins), so overlapping candles — a 1-minute series merged with a 5-minute fallback, say —
    # cannot attribute the same minute to two states. The interval walk this replaced could, and
    # did: one window reported 108.3% of its own span.
    slots: dict = {}
    for c in candles:
        sp = int(c[5]) if len(c) > 5 and c[5] else step
        c0, c1 = c[0], c[0] + sp
        if c1 <= win_start or c0 >= win_end:
            continue
        t = max(c0, win_start) - (max(c0, win_start) % step)
        while t < min(c1, win_end):
            key = t
            if key not in slots:
                iv = next((i for i in ivs if i["start"] <= key < i["end"]), None)
                if iv is None:
                    slots[key] = "flat"          # withdrawn: not in any deployed interval
                else:
                    lo_px, hi_px = iv["lo_px"], iv["hi_px"]
                    if iv.get("open") and live_band:
                        lo_px, hi_px = live_band  # the live book, not a replayed decode
                    slots[key] = classify(c, lo_px, hi_px)
            t += step
    for key, st in slots.items():
        # CLIPPED to the window: a slot straddling either edge contributes only its in-window
        # part, so a bucket can never be credited time that is not in the window
        w = min(key + step, win_end) - max(key, win_start)
        if w > 0:
            durs[st] += w
    deployed = durs["in"] + durs["out"] + durs["unresolved"]
    # ACCOUNTING, not decoration. Every second of the window must land in exactly one bucket; if
    # the candles do not span it, the remainder shows up here instead of quietly shrinking the
    # denominator (this check is what caught the fallback index attributing 541h of a 1083h
    # window, because every sample's span had been capped to a step the API was not using).
    accounted = deployed + durs["flat"]
    span = max(0, win_end - win_start)

    def pct(x):
        return round(100.0 * x / deployed, 1) if deployed > 0 else None

    return {
        "hours_in_range": round(durs["in"] / 3600.0, 2),
        "hours_out_of_range": round(durs["out"] / 3600.0, 2),
        "hours_unresolved": round(durs["unresolved"] / 3600.0, 2),
        "hours_flat": round(durs["flat"] / 3600.0, 2),
        "deployed_hours": round(deployed / 3600.0, 2),
        "hours_accounted": round(accounted / 3600.0, 2),
        "window_hours": round(span / 3600.0, 2),
        "accounting_covers_pct": (round(100.0 * accounted / span, 1) if span > 0 else None),
        # best estimate: share of RESOLVED deployed time (in / (in+out))
        "in_range_share_pct": pct(durs["in"]),
        # honest bounds: everything unresolved counted against, then for, the book
        "in_range_share_low_pct": (round(100.0 * durs["in"] / deployed, 1)
                                   if deployed > 0 else None),
        "in_range_share_high_pct": (round(100.0 * (durs["in"] + durs["unresolved"]) / deployed, 1)
                                    if deployed > 0 else None),
        "unresolved_share_pct": pct(durs["unresolved"]),
        "share_basis": ("in_range_share_pct = in / (in + out) over RESOLVED spans; the low/high "
                        "bounds treat every unresolved (straddling) candle as out / as in"),
    }


def _cycles_in_window(cycles, a, b):
    return [c for c in cycles if a <= c["start"] < b]


def _gaps(cycles):
    ts = sorted(c["start"] for c in cycles)
    return [(ts[i + 1] - ts[i]) / 3600.0 for i in range(len(ts) - 1)]


def compute(tenant: str, wallet: str, live_band=None, live_bin_step: int | None = None) -> dict:
    """The full per-tenant duty-cycle payload, BOUNDED IN TIME.

    The hub this feeds is refreshed by a wrapper that kills the whole build at 280s, so a slow
    price index must not be able to take the page down with it. A wall-clock budget (default 120s,
    DUTY_CYCLE_BUDGET_S) wraps the measurement: on expiry the caller gets an explicit UNKNOWN with
    the reason — never a partial number, and never a silent stall of the rest of the hub.
    """
    budget = int(os.environ.get("DUTY_CYCLE_BUDGET_S") or 120)
    armed = False
    if budget > 0:
        try:
            import signal
            def _expired(_sig, _frm):                                # noqa: ANN001
                raise _BudgetExpired()
            signal.signal(signal.SIGALRM, _expired)
            signal.alarm(budget)
            armed = True
        except Exception:                                            # noqa: BLE001
            armed = False                       # not in the main thread: run unbudgeted
    try:
        return _compute(tenant, wallet, live_band=live_band, live_bin_step=live_bin_step)
    except _BudgetExpired:
        return {"status": "unknown", "tenant": tenant, "updated_at": None,
                "error": (f"measurement exceeded its {budget}s budget (the price index or the "
                          f"explorer is slow) — refusing to publish a partial duty cycle")}
    finally:
        if armed:
            try:
                import signal
                signal.alarm(0)
            except Exception:                                        # noqa: BLE001
                pass


def _compute(tenant: str, wallet: str, live_band=None, live_bin_step: int | None = None) -> dict:
    """The full per-tenant duty-cycle payload. Returns {"status":"unknown", "error":...} rather
    than zeros when anything cannot be read."""
    try:
        txs = fetch_wallet_txs(wallet)
    except Exception as e:                                            # noqa: BLE001
        return {"status": "unknown", "tenant": tenant,
                "error": f"rebalance record unreadable: {e}", "updated_at": None}
    muts = position_mutating_txs(txs, wallet)
    if not muts:
        return {"status": "unknown", "tenant": tenant, "updated_at": None,
                "error": ("no position-mutating transactions found for this wallet on the LFJ "
                          "router — refusing to report a duty cycle for a book with no history")}
    intervals, cycles, bin_step = build_timeline(muts, wallet)
    now = int(time.time())
    if live_bin_step:
        bin_step = live_bin_step

    out = {"status": "ok", "tenant": tenant, "updated_at": now,
           "source": {"rebalances": f"on-chain tx list via {EXPLORER.split('/')[2]} "
                                    f"(removeLiquidity {SEL_REMOVE} on {LFJ_ROUTER})",
                      "price": f"GeckoTerminal OHLCV for the pool {LFJ_PAIR}",
                      "current_band": ("live chain read (caller)" if live_band
                                       else "decoded from the last deploy")},
           "definition": ("IN RANGE = deployed with spot inside the held bin band (earning); "
                          "OUT OF RANGE = deployed with spot outside the band (earning zero); "
                          "FLAT = withdrawn. One rebalance = one removeLiquidity -> "
                          "addLiquidity cycle from this wallet."),
           "rebalance_count": len(cycles),
           "last_rebalance_utc": None, "last_rebalance_tx": None, "last_rebalance_block": None,
           "current_streak_hours": None, "deployed_now": None, "bin_step": bin_step}

    if cycles:
        last = cycles[-1]
        out["last_rebalance_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last["start"]))
        out["last_rebalance_tx"] = last["remove_tx"]
        out["last_rebalance_block"] = last["remove_block"]

    # The current streak is time since the book was last REBUILT (deploy completed), not since the
    # withdraw — a withdrawn book has no streak at all.
    open_iv = next((i for i in intervals if i.get("open")), None)
    out["deployed_now"] = bool(open_iv)
    if open_iv:
        out["current_streak_hours"] = round((now - open_iv["start"]) / 3600.0, 2)
        if live_band:
            open_iv["lo_px"], open_iv["hi_px"] = live_band

    try:
        # TWO series, at the coarsest resolution that still sees a real exit. Every extra candle is
        # payload on a rate-limited public index, and the bounds published with the share already
        # carry the cost of the resolution. (Measured: a 1000-candle request is what trips the 429.)
        #   15-min  -> 10.4 days per call: covers the 7-day window AND the open interval
        #   30-min  -> 20.8 days per call: reaches this book's inception
        fifteens, fifteen_cov, fifteen_step = candle_series("minute", 15, now - 7 * 86400,
                                                            max_calls=2)
        thirties, thirty_cov, thirty_step = candle_series("minute", 30, 0, max_calls=4)
        # 1-min, ONE page only (~16h): the current interval is the LIVE number and this book
        # re-centres roughly every 20 minutes, so 15-minute candles would give it two readings.
        ones, one_cov, one_step = candle_series("minute", 1, now - 6 * 3600, max_calls=1)
    except Exception as e:                                            # noqa: BLE001
        d = dict(out)
        d.update({"status": "unknown",
                  "error": f"price path unreadable, so in-range time cannot be measured: {e}"})
        return d

    series = [
        # "7d" — 15-minute candles (fine enough to see a real exit at this cadence)
        {"key": "7d", "label": "last 7 days @ 15m candles", "candles": fifteens,
         "step": fifteen_step, "start": max(now - 7 * 86400, fifteen_cov), "tf": "15-min"},
        # "all" — the reach of the price source, but never before this book's first deploy:
        # "since inception" means since THIS book went live, not since the candles begin.
        {"key": "all", "label": "since inception @ 30m candles", "candles": thirties,
         "step": thirty_step,
         "start": max(thirty_cov, (min(i["start"] for i in intervals) if intervals else now)),
         "tf": "30-min"},
        # "now" — the OPEN interval, from the finer series that reaches back to its start
        {"key": "now", "label": "current interval @ 1m candles", "candles": ones, "step": one_step,
         "start": max((open_iv["start"] if open_iv else now - 3600), one_cov), "tf": "1-min"},
    ]
    res = {}
    for w in series:
        st, en, step = w["start"], now, w["step"]
        m = measure(intervals, w["candles"], step, st, en, live_band=live_band)
        cyc = _cycles_in_window(cycles, st, en)
        gaps = _gaps(cyc)
        iv_in = [i for i in intervals if i["start"] < en and i["end"] > st]
        longest = max(((min(i["end"], en) - max(i["start"], st)) / 3600.0 for i in iv_in), default=0.0)
        m.update({
            "window_label": w["label"],
            "candle_tf": w["tf"],
            "window_start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st)),
            "window_end_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(en)),
            "window_hours": round((en - st) / 3600.0, 2),
            "candles": len([c for c in w["candles"] if c[0] + step > st and c[0] < en]),
            "rebalances": len(cyc),
            "avg_hours_between_rebalances": (round(sum(gaps) / len(gaps), 2) if gaps else None),
            "longest_stretch_hours": round(longest, 2),
        })
        res[w["key"]] = m
    out["windows"] = res
    out["band_now"] = ({"lo_px": live_band[0], "hi_px": live_band[1]} if live_band else None)
    # WHICH index actually answered — recorded, never assumed. The precision of the estimate
    # depends on it, so a reader (and a future debugger) must be able to see the substitution.
    if _PRICE_NOTE[0]:
        out["source"]["price"] = f"{_PRICE_NOTE[0]['index']} — {_PRICE_NOTE[0]['instrument']}"
        out["price_shape"] = _PRICE_NOTE[0].get("shape")
        if _PRICE_NOTE[0].get("why"):
            out["price_fallback_reason"] = _PRICE_NOTE[0]["why"]
    if _CACHE_ERRORS:
        # a damaged local cache is reported, not swallowed: it does not change the answer (the
        # real source is re-read) but it must not be invisible either
        out["cache_errors"] = _CACHE_ERRORS[-5:]
    return out


def _fmt(d: dict) -> str:
    if d.get("status") != "ok":
        return f"UNKNOWN — {d.get('error')}"
    L = [f"DUTY CYCLE — {d['tenant']}",
         f"  rebalances on record : {d['rebalance_count']}"
         f"   last: {d['last_rebalance_utc']} ({d['last_rebalance_tx']})",
         f"  deployed right now   : {d['deployed_now']}"
         f"   current streak: {d['current_streak_hours']} h",
         f"  source               : {d['source']['rebalances']}"]
    for name in ("now", "7d", "all"):
        w = d["windows"][name]
        L.append(f"  [{name}] {w['window_label']}  ({w['window_start_utc']} → {w['window_end_utc']}, "
                 f"{w['window_hours']}h, {w['candles']} candles)")
        L.append(f"      in range {w['hours_in_range']}h | out {w['hours_out_of_range']}h | "
                 f"unresolved {w['hours_unresolved']}h | flat {w['hours_flat']}h")
        L.append(f"      in-range share {w['in_range_share_pct']}% of deployed "
                 f"{w['deployed_hours']}h  (bounds {w['in_range_share_low_pct']}-"
                 f"{w['in_range_share_high_pct']}%, unresolved {w['unresolved_share_pct']}%)")
        L.append(f"      rebalances {w['rebalances']} | avg between "
                 f"{w['avg_hours_between_rebalances']}h | longest stretch "
                 f"{w['longest_stretch_hours']}h")
    return "\n".join(L)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Duty cycle / uptime between rebalances")
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--wallet", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    a = ap.parse_args()
    if a.no_cache:
        global CACHE_TTL
        CACHE_TTL = 0
    d = compute(a.tenant, a.wallet)
    print(json.dumps(d, indent=2) if a.json else _fmt(d))
    return 0 if d.get("status") == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
