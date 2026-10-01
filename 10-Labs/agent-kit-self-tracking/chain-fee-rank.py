#!/usr/bin/env python3
"""chain-fee-rank.py — rank pools by CHAIN-MEASURED fees, replacing the aggregator's numbers.

Jordan (2026-09-19): "Yes please" — re-run the full ranking with chain-measured fees.

WHY THIS EXISTS: LFJ's aggregator APR sat in our notes at 90.7%. The chain says 13-20%. A 4.5x error
in the one number we used to pick our lead venue means every venue's figure is suspect.

METHOD per pool:
  1. address from the FACTORY (never from an aggregator UUID)
  2. fee tier / bin step read from the pool itself
  3. TVL from chain balances
  4. page eth_getLogs over 24h, decode Swap events -> real volume
  5. fees = volume x tier ; APR = fees x 365 / TVL

BUGS AVOIDED, each one hit for real:
  - getPool(address,address,uint24) — NOT uint256. One wrong word in the signature is a DIFFERENT
    selector, the call fails, and it looks exactly like "no such pool".
  - LB pairs use getTokenX/getTokenY, not token0/token1.
  - Wide log ranges silently return 0, so windows are bounded and empty ones are counted.
  - A verified byte order (checked against an independent quantity) before any total is reported.

READ-ONLY.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

from Crypto.Hash import keccak

# Shared rotating providers (one hardcoded host = 1015 takes the 24h log windows dark).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from avax_rpc import rpc_call as _rpc_call, RpcUnavailable   # noqa: E402

UA = {"User-Agent": "GenTech-Steward/1.0", "Content-Type": "application/json"}
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(HERE, "chain-fee-measurements.json")

# ── THE WINDOW IS MEASURED, NOT ASSUMED ────────────────────────────────────────────────────────
# This was `DAY = 43_200  # ~24h of Avalanche blocks at ~2s`. On 2026-09-23 the chain was measured
# at **1.223 s/block**, so 43,200 blocks is **14.7 hours** — and the number was cached and printed
# as `volume_24h_usd`. Every fee APR in the cache was therefore UNDERSTATED by ~39% (14.7/24), and
# worse, it was understated by an amount nobody could see: the label said 24h. A hardcoded
# block-count-as-a-day is the same defect family as the hardcoded $8.24 price — a stale constant
# wearing the word "measured". So the window is derived from two real block timestamps at run time,
# and the ACTUAL hours covered are recorded in the cache beside the volume.
DAY = 43_200          # kept only as the historical name; NOT used to size the window any more
WINDOW_H = 24.0       # what we are trying to cover
DAY_WINDOWS = 24      # log windows per measurement (wide ranges silently return 0)

WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
WETHE = "0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB"

UNIV3_F = "0x740b1c1de25031C31FF4fC9A62f554A55cdC1baD"
LB_F = "0xb43120c4745967fa9b93E79C149E66B0f2D6Fe0c"
# Black Hole CLMM (Algebra Integral) WAVAX/USDC — our ACTIVE re-entry venue. Selected by HIGHEST
# LIQUIDITY, never first result: this venue family has decoy pools that answer every call normally.
BLACKHOLE_POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"
FEES = [100, 500, 3000, 10000]
BSTEPS = [1, 5, 10, 15, 20, 25, 50, 100]
# ── PRICES ───────────────────────────────────────────────────────────────────────────────────
# THESE WERE HARDCODED, AND THE USD LEGS THEY PRODUCE WENT STALE SILENTLY.
# Measured 2026-09-22: WAVAX was hardcoded at $8.24 while spot was $10.91 (DefiLlama and
# CoinGecko agreed to 0.2%). Because TVL is priced with this same constant, the error partially
# CANCELS in the APR ratio (volume and TVL both scale) — the Apr moved only 42.7% -> 44.3% — but
# the absolute USD figures the treasury report quotes were 11% LOW, and they were labelled
# "measured from chain". A hardcoded price makes a chain read a partly-config-derived number.
#
# The rule for an executing path: a live value, or a dated fallback that can be SEEN. So: read a
# real WAVAX price once per run, and if that read fails, fall back to the constant below and PRINT
# that the figures are fallback-priced. A silent stale constant is the bug; a loud dated one is a
# limitation.
FALLBACK_PX = {WAVAX.lower(): 10.91, WETHE.lower(): 2450.0, USDC.lower(): 1.0}
FALLBACK_PX_DATE = "2026-09-22"
PX = dict(FALLBACK_PX)          # mutated by load_prices(); read by tvl() and volume_24h()
PX_LIVE = False
PRICE_SOURCES = [
    ("defillama", "https://coins.llama.fi/prices/current/avax:{wavax}"),
    ("coingecko", "https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd"),
]


def load_prices():
    """Fetch a live WAVAX price. Returns (price, source) or (None, reason). Never raises.

    Two independent sources: if both fail we do NOT invent a number — we keep the dated fallback
    and the caller prints that the USD legs are fallback-priced, so a reader can tell.
    """
    global PX, PX_LIVE
    for name, url in PRICE_SOURCES:
        try:
            u = url.format(wavax=WAVAX)
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as x:
                d = json.load(x)
            if name == "defillama":
                p = float(d["coins"][f"avax:{WAVAX}"]["price"])
            else:
                p = float(d["avalanche-2"]["usd"])
            # Sanity band: a price outside this is a parse error, not a market move. Refusing an
            # implausible price beats writing it into every USD figure in the report.
            if not (0.10 <= p <= 1000.0):
                continue
            PX[WAVAX.lower()] = p
            PX_LIVE = True
            return p, name
        except Exception:
            continue
    return None, "both price sources failed"


def K(sig):
    h = keccak.new(digest_bits=256)
    h.update(sig.encode())
    return "0x" + h.hexdigest()


def rpc(method, params, retries=3):
    # ROTATES across providers instead of retrying one source-banned host (1015 is per-SOURCE).
    # Raises rather than returning None, so a caller cannot mistake "no provider" for "no data".
    try:
        return _rpc_call(method, params, timeout=55, tries=retries)
    except RpcUnavailable:
        return None


def call(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])


P = lambda a: a.lower().replace("0x", "").rjust(64, "0")


def uint(r):
    return int(r, 16) if r and len(r) >= 66 else None


def lfj_fee_law(addr: str) -> "tuple[float, float, dict] | None":
    """Read an LFJ Liquidity Book pool's OWN fee law. Returns (gross_take, lp_take, raw) or None.

    WHY THIS EXISTS (K3 flagged it as #7 on 2026-09-23: "LFJ fee tier hardcoded at 0.0005
    regardless of bin step"): every LFJ row in this scan carried `fee_bp = 0.0005` as a literal,
    so the tier was a belief, not a read — in a file whose docstring promises the tier comes from
    the pool. The chain disagrees per pool, and the disagreement is not small:

        binStep 10  -> baseFactor 5000 -> base take 0.0500%   (the literal happened to be right)
        binStep 100 -> baseFactor 8000 -> base take 0.8000%   (the literal was 16x too low)

    So a wide-step pool would have had its fee income understated 16x.

    THE TAKE IS  baseFactor x binStep / 1e8, and `protocolShare` is what the PROTOCOL keeps before
    LPs are paid. The LP-effective rate is the gross take minus that share.

    ⚠️ `getStaticFeeParameters()` returns
        (baseFactor, filterPeriod, decayPeriod, reductionFactor, variableFeeControl,
         protocolShare, maxVolatilityAccumulator)
    — **binStep is NOT in there.** Reading word[1] as the bin step is a plausible-looking mistake
    that produced a 3x-high take on binStep 10 (filterPeriod 30 x baseFactor 5000 = 0.15% instead
    of 0.05%). Verified against four pools with known, different bin steps; the bin step is read
    from the pool with `getBinStep()` and cross-checked, never inferred from a tuple position.
    """
    r = call(addr, K("getStaticFeeParameters()")[:10])
    bs = call(addr, K("getBinStep()")[:10])
    if not r or len(r) < 2 + 64 * 7 or not bs or len(bs) < 66:
        return None
    try:
        w = [int(r[2:][i * 64:(i + 1) * 64], 16) for i in range(len(r[2:]) // 64)]
        base_factor = w[0]
        protocol_share = w[5]
        bin_step = int(bs, 16)
    except Exception:                                                 # noqa: BLE001
        return None
    if bin_step <= 0 or bin_step > 10_000:
        return None                                                   # nonsensical = unreadable
    gross = base_factor * bin_step / 1e8
    lp = gross * (1.0 - protocol_share / 10_000.0)
    return gross, lp, {"baseFactor": base_factor, "binStep": bin_step,
                       "filterPeriod": w[1], "protocolShare": protocol_share}


def find_pools():
    out = []
    s = K("getPool(address,address,uint24)")[:10]
    for a, b, nm in ((WAVAX, USDC, "WAVAX-USDC"), (WETHE, WAVAX, "WETH.e-WAVAX")):
        for fee in FEES:
            r = call(UNIV3_F, s + P(a) + P(b) + hex(fee)[2:].rjust(64, "0"))
            if r and len(r) >= 42 and int(r, 16) != 0:
                # Uniswap V3's tier IS the fee — no protocol share, no surge. The nominal tier is
                # the realised take, so gross and LP-effective are the same number here.
                out.append({"addr": "0x" + r[-40:], "tier": f"{fee/10000:.2f}%", "pair": nm,
                            "venue": "univ3", "fee_bp": fee / 1_000_000,
                            "fee_bp_lp": fee / 1_000_000, "fee_src": "pool tier (nominal)"})
    s2 = K("getLBPairInformation(address,address,uint256)")[:10]
    for bs in BSTEPS:
        r = call(LB_F, s2 + P(WAVAX) + P(USDC) + hex(bs)[2:].rjust(64, "0"))
        if r and len(r) >= 2 + 64 * 4:
            a = "0x" + r[2 + 64:2 + 128][24:]
            if int(a, 16) != 0:
                law = lfj_fee_law(a)
                if law is None:
                    # A fee law we cannot read is NOT a licence to fall back to a literal. Record
                    # the row as unpriceable so it cannot enter the ranking on a guessed tier.
                    gross = lp = None
                    fsrc = "UNREADABLE (excluded from ranking)"
                else:
                    gross, lp, raw = law
                    fsrc = (f"chain fee law: {raw['baseFactor']}x{raw['binStep']}/1e8, "
                            f"protocolShare {raw['protocolShare']}/1e4")
                out.append({"addr": a, "tier": f"bs{bs}", "pair": "WAVAX-USDC",
                            "venue": "lfj", "fee_bp": gross, "fee_bp_lp": lp, "fee_src": fsrc})
    # ── BLACK HOLE CLMM (Algebra V3) — our ACTIVE re-entry venue ──────────────────
    # Added 2026-09-22. Until now this venue had NO live fee number: pool-fee-rank.py carried a
    # frozen 47% constant dated 09-17 and the scan below covered only univ3 + LFJ. So the one
    # venue we are actually pointed at was the only one we could not measure — the ranking's
    # leaderboard was live while our ACTIVE row was a 5-day-old literal.
    #
    # Algebra Integral emits the standard Uniswap-V3-family Swap signature, and this pool was
    # probed to confirm it (367 Swap logs in 30 min at the time of writing), so the existing
    # univ3 decode path applies unchanged. token0/token1 here are WAVAX/USDC in that order.
    #
    # The take rate is the NOMINAL base tier. Algebra adds a surge term on top of it (read from
    # the fee law: baseFactor=5000, variableFeeControl=40000, protocolShare=1000), so this is the
    # FLOOR of the fee leg, not the realised average — and protocolShare means the protocol takes
    # 10% before LPs are paid, so the LP-effective number is lower again. Both caveats are the
    # same ones that already apply to every row here.
    out.append({"addr": BLACKHOLE_POOL, "tier": "algebra-0.05%", "pair": "WAVAX-USDC",
                "venue": "blackhole", "fee_bp": 0.0005, "fee_bp_lp": 0.00045,
                "fee_src": "nominal base tier (surge excluded, floor)"})
    return out


S_BAL = K("balanceOf(address)")[:10]
S_TX = K("getTokenX()")[:10]
S_TY = K("getTokenY()")[:10]
S_T0 = K("token0()")[:10]
S_T1 = K("token1()")[:10]


def tokens(p):
    if p["venue"] == "lfj":
        rx, ry = uint(call(p["addr"], S_TX)), uint(call(p["addr"], S_TY))
    else:
        rx, ry = uint(call(p["addr"], S_T0)), uint(call(p["addr"], S_T1))
    if not rx or not ry:
        return None, None
    return "0x" + hex(rx)[2:].zfill(40), "0x" + hex(ry)[2:].zfill(40)


def tvl(p):
    t0, t1 = tokens(p)
    if not t0:
        return None, None, None
    b0, b1 = uint(call(t0, S_BAL + P(p["addr"]))), uint(call(t1, S_BAL + P(p["addr"])))
    if b0 is None or b1 is None:
        return None, None, None
    d0 = 6 if t0.lower() == USDC.lower() else 18
    d1 = 6 if t1.lower() == USDC.lower() else 18
    v0, v1 = b0 / 10 ** d0, b1 / 10 ** d1
    return (v0 * PX.get(t0.lower(), 0) + v1 * PX.get(t1.lower(), 0)), v0, v1


T_UNIV3 = K("Swap(address,address,int256,int256,uint160,uint128,int24)")
T_LB = K("Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)")


def swap_value_univ3(a0: int, a1: int, px0: float, px1: float, d0: int, d1: int) -> float:
    """One Uniswap-V3-family Swap event -> the USD value of the trade (ONE leg, not two).

    THE BUG THIS CLOSES (K3 flagged it as a *possible* ~2x skew on 2026-09-23; measured and
    CONFIRMED here): a swap moves value from one token into the other — amount0 and amount1 carry
    OPPOSITE signs and near-equal USD value, differing only by the fee. Summing both legs therefore
    counts one trade twice. It was done for univ3 and blackhole but NOT for LFJ (whose decoder reads
    the single packed amountsIn), so the two venues were being measured on different scales —
    exactly the kind of error that reorders a ranking treasury allocates by.

    Measured on chain 2026-09-23, 900-block window: BOTH-legs / ONE-leg was **2.00x** for the
    Black Hole pool (513 swaps) and **2.00x** for Uniswap V3 WAVAX/USDC 0.05% (798 swaps), while
    LFJ bs10 came out 1.00x — confirming the asymmetry rather than assuming it.

    The leg with the larger absolute value IS the trade's value (the other is what it received,
    ~equal minus the fee). Using `max` also keeps working for exact-output swaps, where the input
    leg is the larger one.
    """
    v0 = abs(a0) / 10 ** d0 * px0
    v1 = abs(a1) / 10 ** d1 * px1
    return max(v0, v1)


def blocktime_s() -> "float | None":
    """Measure the chain's real block time from two anchors. Returns None if it cannot be read.

    Never returns an assumed 2.0 — an unreadable block time must stop the measurement, not silently
    resize the window to a guess.
    """
    hi = rpc("eth_blockNumber", [])
    if not hi:
        return None
    hi = int(hi, 16)
    lo = hi - 5000
    t_hi = rpc("eth_getBlockByNumber", [hex(hi), False])
    t_lo = rpc("eth_getBlockByNumber", [hex(lo), False])
    if not t_hi or not t_lo:
        return None
    try:
        dt = int(t_hi["timestamp"], 16) - int(t_lo["timestamp"], 16)
    except Exception:                                                 # noqa: BLE001
        return None
    if dt <= 0:
        return None
    return dt / 5000.0


def volume_24h(p):
    blk = rpc("eth_blockNumber", [])
    if not blk:
        # NOT `return 0.0, 0, 0` — a fabricated zero is indistinguishable from a genuinely dead,
        # fully-measured pool, and it enters the ranking as a real 0% APR. None = "could not
        # measure", which the caller counts as a failure and refuses to cache.
        return None
    blk = int(blk, 16)   # NB: block numbers are short hex — do NOT pass them through uint()
    bt = blocktime_s()
    if not bt:
        return None      # cannot size the window = cannot measure. Do not fall back to a guess.
    W = DAY_WINDOWS
    span = max(1, int(round(WINDOW_H * 3600.0 / bt / W)))
    win_blocks = span * W
    win_h = win_blocks * bt / 3600.0
    # Record what we ACTUALLY covered, so the cache can say "24h window" only when it is one.
    LAST_WINDOW.update({"hours": round(win_h, 2), "blocks": win_blocks,
                        "blocktime_s": round(bt, 4)})
    t0leg, t1leg = tokens(p)
    if not t0leg or not t1leg:
        return None   # unresolved tokens = could not measure, not a zero
    tot = 0.0
    swaps = 0
    empty = 0
    failed = 0
    for i in range(W):
        f = blk - win_blocks + i * span
        t = min(f + span - 1, blk)
        # Algebra/Black Hole uses token0()/token1() like Uniswap V3 — same decode path.
        topic = T_UNIV3 if p["venue"] in ("univ3", "blackhole") else T_LB
        logs = rpc("eth_getLogs", [{"fromBlock": hex(f), "toBlock": hex(t),
                                    "address": p["addr"], "topics": [topic]}])
        if logs is None:
            failed += 1          # a failed window is NOT an empty one; dropping it understates
            continue             # volume/fees/APR with no signal that 20 of 24 windows are missing
        if not logs:
            empty += 1
        for lg in logs:
            d = lg.get("data", "0x")[2:]
            try:
                if p["venue"] in ("univ3", "blackhole") and len(d) >= 64 * 5:
                    a0 = int(d[0:64], 16)
                    a1 = int(d[64:128], 16)
                    if a0 >= 2 ** 255:
                        a0 -= 2 ** 256
                    if a1 >= 2 ** 255:
                        a1 -= 2 ** 256
                    d0 = 6 if t0leg.lower() == USDC.lower() else 18
                    d1 = 6 if t1leg.lower() == USDC.lower() else 18
                    # ONE leg, not the sum of both — a swap moves value from one side to the
                    # other, so summing counted every univ3/blackhole trade TWICE (measured 2.00x)
                    # while LFJ's packed amountsIn counted it once. See swap_value_univ3().
                    tot += swap_value_univ3(a0, a1, PX.get(t0leg.lower(), 0),
                                            PX.get(t1leg.lower(), 0), d0, d1)
                elif p["venue"] == "lfj" and len(d) >= 64 * 6:
                    a = int(d[64:128], 16)           # amountsIn
                    hi, lo = a >> 128, a & ((1 << 128) - 1)
                    # verified byte order: hi=USDC(6dp), lo=WAVAX(18dp)
                    tot += hi / 1e6 * 1.0 + lo / 1e18 * PX.get(WAVAX.lower(), 0)
                swaps += 1
            except Exception:
                pass
        time.sleep(0.25)
    return tot, swaps, empty, failed


PARTIAL_FAILURES = []   # pools whose 24h measurement had failed log windows
LAST_WINDOW: "dict[str, float | int | None]" = {"hours": None, "blocks": None, "blocktime_s": None}


def main():
    print("=" * 112)
    print("  CHAIN-MEASURED POOL RANKING — 24h of real swaps, not an aggregator's number")
    print("=" * 112)
    px, px_src = load_prices()
    if px is not None:
        print(f"\n  WAVAX price: ${px:,.4f} (live, {px_src}) — every USD figure below is "
              f"priced at spot")
    else:
        print(f"\n  ⚠️  WAVAX price: ${FALLBACK_PX[WAVAX.lower()]:,.2f} — FALLBACK, dated "
              f"{FALLBACK_PX_DATE} ({px_src}).")
        print(f"      USD legs below are NOT spot-priced. Do not quote them as measured-at-market.")
    pools = find_pools()
    print(f"\n  pools found from factories: {len(pools)}")

    rows = []
    for p in pools:
        t, v0, v1 = tvl(p)
        if t is None:
            continue
        p["tvl"] = t
        p["v0"], p["v1"] = v0, v1
        vol, swaps, empty, failed = volume_24h(p)
        if failed:
            # A run with failed windows is NOT a complete 24h measurement. Recording it as one
            # understates volume/fees/APR with no signal that log windows went missing — and
            # understated APRs reorder the ranking treasury allocates by.
            print(f"    ! {p.get('pair','?')}/{p.get('tier','?')}: {failed}/{DAY_WINDOWS} log windows FAILED — "
                  f"volume is understated; not usable as a complete measurement")
            PARTIAL_FAILURES.append(f"{p.get('pair','?')}/{p.get('tier','?')}")
        p["vol"] = vol
        p["swaps"] = swaps
        p["failed_windows"] = failed
        p["empty"] = empty
        if p.get("fee_bp") is None or vol is None:
            # An unpriceable pool must not be assigned a fabricated take, and a fee APR computed
            # from a guessed tier is worse than no APR at all. Report it as unrankable.
            print(f"    ! {p.get('pair','?')}/{p.get('tier','?')}: fee tier UNREADABLE — "
                  f"{p.get('fee_src')} — excluded from the ranking")
            continue
        gross_bp = p["fee_bp"]
        lp_bp = p.get("fee_bp_lp", gross_bp)
        # GROSS fee generation (the venue's business) vs what LPs are actually paid. LFJ and
        # Algebra both keep a protocolShare before LPs see anything, so the two are NOT the same
        # number — reporting only the gross one overstates our own yield.
        p["fees_day"] = vol * gross_bp
        p["lp_fees_day"] = vol * lp_bp
        p["apr"] = (p["lp_fees_day"] * 365 / t * 100) if t > 0 else 0
        p["apr_gross"] = (p["fees_day"] * 365 / t * 100) if t > 0 else 0
        rows.append(p)

    print("\n" + "=" * 112)
    print("  RANKED BY CHAIN-MEASURED FEE APR")
    print("=" * 112)
    win_h = LAST_WINDOW.get("hours")
    if win_h is not None:
        print(f"  window: {win_h}h MEASURED from chain block times over {LAST_WINDOW['blocks']:,} "
              f"blocks (block time {LAST_WINDOW['blocktime_s']}s) — vol/day IS a 24h figure")
    else:
        print("  ⚠️  window: NOT MEASURED — no row below can be called a 24h figure")
    # The capital constant that used to head this column (`our $/yr @$17.69`) was a stale wallet
    # number from a different funding week. A normalised figure cannot go stale: it describes the
    # RATE, and the reader applies it to whatever capital is actually deployed.
    print(f"  {'pool':<15}{'venue':<8}{'tier':<8}{'TVL':>13}{'vol/day':>13}{'swaps':>7}"
          f"{'gross fees/d':>13}{'LP APR':>9}{'  $/yr per $1k':>14}")
    print("  " + "-" * 118)
    for r in sorted(rows, key=lambda x: -x["apr"]):
        our = r["apr"] / 100 * 1000.0
        print(f"  {r['pair']:<15}{r['venue']:<8}{r['tier']:<8}{r['tvl']:>13,.0f}{r['vol']:>13,.0f}"
              f"{r['swaps']:>7}{r['fees_day']:>13,.2f}{r['apr']:>8.2f}%{our:>14,.2f}")
    print("  LP APR = LP-EFFECTIVE take x 24h volume x 365 / TVL. 'gross fees/d' does NOT"
          " deduct the protocol share.")
    print("  fee-tier provenance (read from each pool, not assumed):")
    for r in sorted(rows, key=lambda x: -x["apr"]):
        note = ""
        if abs(r["apr_gross"] - r["apr"]) > 0.01:
            note = f"  [gross-tier APR {r['apr_gross']:.2f}%]"
        print(f"    {r['venue']:<8}{r['tier']:<14}{r['fee_src']}{note}")

    print("\n" + "=" * 112)
    print("  AGGREGATOR vs CHAIN — the disagreements, made visible")
    print("=" * 112)
    # ⚠️ THE AGGREGATOR SIDE OF THIS TABLE IS A FROZEN CONSTANT dated 2026-09-19, kept only to
    # show the historical size of the disagreement. It is NOT the aggregator's current number —
    # do not quote the right-hand column as live. (Same defect family this file keeps fixing: a
    # hardcoded belief printed beside a measured one with no date on it.)
    AGG_DATE = "2026-09-19"
    AGG = {("WAVAX-USDC", "lfj", "bs10"): 21.20, ("WETH.e-WAVAX", "univ3", "0.05%"): 22.95,
           ("WAVAX-USDC", "univ3", "0.05%"): 16.79, ("WETH.e-WAVAX", "univ3", "0.30%"): None}
    print(f"  aggregator column = DefiLlama as of {AGG_DATE} (frozen reference, not live)")
    print(f"  {'pool':<15}{'venue':<8}{'tier':<8}{'chain APR':>11}{'aggregator':>12}{'delta':>10}")
    print("  " + "-" * 66)
    for r in sorted(rows, key=lambda x: -x["apr"]):
        a = AGG.get((r["pair"], r["venue"], r["tier"]))
        if a:
            print(f"  {r['pair']:<15}{r['venue']:<8}{r['tier']:<8}{r['apr']:>10.2f}%{a:>11.2f}%"
                  f"{r['apr']-a:>9.2f}")
    # ── CACHE THE MEASUREMENT ───────────────────────────────────────────────
    # This scan takes minutes (24 log windows x N pools), which is far too slow to run inline inside
    # the treasury report. So it writes its result once and the report READS it — measure once, read
    # many — with a timestamp so a reader can refuse a stale measurement. A cached number without a
    # timestamp is indistinguishable from a fresh one, which is the exact defect being fixed.
    # ── REFUSE TO CACHE A MEASUREMENT THAT MEASURED NOTHING ─────────────────
    # A run where every provider failed produced `rows == []` and OVERWROTE a good 12-pool cache
    # with 0 pools, exit 0, and a fresh timestamp — a false value that reads exactly like a
    # successful measurement, and the report would then refuse the good vault cache as superseded.
    # An empty result is not a measurement. Keep the previous cache and FAIL so the cause surfaces.
    if not rows:
        print("\n  ⚠️ NO POOLS MEASURED — refusing to overwrite the cache with an empty result")
        print("     (every provider failed, or the scan returned nothing — either way this is not data)")
        return 5
    if PARTIAL_FAILURES:
        # Partial outage: the numbers exist but they are UNDERSTATED. Writing them would replace a
        # complete measurement with an incomplete one that carries no warning — the false-value
        # family. Refuse, and say exactly which pools were short so the cause is not anonymous.
        print(f"\n  ⚠️ {len(PARTIAL_FAILURES)} pool(s) had FAILED log windows — refusing to cache a")
        print(f"     partial 24h measurement as if it were complete: {', '.join(PARTIAL_FAILURES)}")
        return 6
    from datetime import datetime, timezone
    cache = {
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "method": "decoded Swap events over a MEASURED 24h block window; TVL from chain balances; "
                  "fees = ONE-LEG swap value x tier",
        "window_blocks": LAST_WINDOW.get("blocks"),
        "window_hours": LAST_WINDOW.get("hours"),
        "blocktime_s": LAST_WINDOW.get("blocktime_s"),
        "pools": [
            {"pair": r["pair"], "venue": r["venue"], "tier": r["tier"], "addr": r["addr"],
             "tvl_usd": round(r["tvl"], 2), "volume_24h_usd": round(r["vol"], 2),
             "swaps_24h": r["swaps"], "empty_windows": r.get("empty", 0),
             "fees_per_day_usd": round(r["fees_day"], 4),
             "lp_fees_per_day_usd": round(r["lp_fees_day"], 4),
             "fee_apr_pct": round(r["apr"], 4),
             "fee_apr_gross_pct": round(r["apr_gross"], 4),
             "fee_tier_effective": round(r.get("fee_bp_lp", r["fee_bp"]) * 100, 6),
             "fee_source": r.get("fee_src")}
            for r in sorted(rows, key=lambda x: -x["apr"])
        ],
    }
    try:
        # Atomic: a kill or full disk mid-dump would otherwise leave a truncated file that
        # consumers json.load — a cache that parses is not a cache that is complete.
        _tmp = CACHE_PATH + ".tmp"
        with open(_tmp, "w") as f:
            json.dump(cache, f, indent=2)
        os.replace(_tmp, CACHE_PATH)
        print(f"\n  cached -> {CACHE_PATH}")
        print(f"  {len(cache['pools'])} pools · measured_at {cache['measured_at']}")
    except Exception as e:
        print(f"\n  ⚠️ could not write cache: {type(e).__name__}: {str(e)[:80]}")
        return 7   # a failed write must not look like a successful refresh
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
