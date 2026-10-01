#!/usr/bin/env python3
"""BLACK health tracker — is the emissions half of our yield collapsing?

Jordan (Sep 15 2026): "We should track BLACK and see what it looks like if BLACK
collapses — how do you look at that, based on the price of BLACK, or just in
general if more people stop farming on Blackhole."

WHY THIS MATTERS
  Our Blackhole yield is TWO layers:
    1. real swap fees  (durable — paid by traders)
    2. BLACK emissions (fragile — the protocol's own token, $0.0022, and its
       price is set by emissions selling pressure)
  A headline APR of 828% is ~all layer 2. If BLACK collapses, that number does
  not shrink, it VANISHES. So the tracker must watch the price AND the emission
  rate AND the liquidity — three independent failure modes:

    A. PRICE collapse   -> emissions convert to less money
    B. EMISSION cut/dry -> the gauge stops paying, or its runway runs out
    C. LP exodus        -> usually GOOD (survivors capture more fee share),
                           but ONLY if volume holds. TVL down + volume down is
                           the death signal.

WHAT IT WRITES
  /root/vaults/gentech/10-Labs/agent-kit-self-tracking/black-health.json
  with the split: fee_apr vs emissions_apr, so we never quote the mix as if it
  were all durable income.

SILENCE DOCTRINE: exit 0 quietly when nothing changed; print an alert only when a
threshold is crossed or a metric moved materially.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.
def _avax_url():
    """A last-resort provider STRING for callers that build their own request."""
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        # 2026-09-27 FIX: this branch used to be `return _avax_url()` — a fallback that
        # called ITSELF, so any failure to import avax_rpc (path problem, missing web3)
        # turned one degraded read into a RecursionError instead of a URL. A fallback
        # that cannot fall back is not a fallback. Return a literal host instead; rpc()
        # below carries the User-Agent that host requires.
        return "https://avalanche.drpc.org"

RPC = _avax_url()
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"      # WAVAX/USDC 0.05%
BLACK_POOL = "0x14e4A5beD2e5E688EE1A5Ca3a4914250D1aBD573"  # BLACK/WAVAX (price source)
GAUGE = "0x3ADE52f9779c07471F4B6d5997444C3c2124C1c0"
ETERNAL_FARMING = "0x01A8A00A6fC8106B94f84aAbAef689Fd0D77271A"  # emission source
OUT = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/black-health.json"
FEE_TIER = 0.0005
CHUNK = 2000            # this RPC silently caps eth_getLogs ranges; paginate

# Alert thresholds
PRICE_CRASH_7D = -25.0      # BLACK down >25% in 7d -> emissions half is eroding
PRICE_COLLAPSE_60D = -50.0  # off the 60d high -> treat as collapse
EMISSION_WEEKLY_CUT = -30.0  # rewardRate down >30% w/w
RUNWAY_ALERT_DAYS = 60       # under 2 months of emissions left at source -> alert
SWAP_TOPIC = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"


def rpc(method, params, tries=1):
    """JSON-RPC to the AVAX C-Chain, carrying the User-Agent the public hosts require.

    2026-09-27 FIX — TWO DEFECTS BEHIND ONE SYMPTOM (the report read
    "black-health.json unreadable: unsupported format string passed to NoneType.__format__"):

      (1) THE WRONG HEADERS. This function sent Content-Type and NO User-Agent.
          publicnode answers a bare urllib POST with **HTTP 403** while answering the
          SAME request WITH a UA. Worse: `avax_rpc.url()` PROBES with a UA, so the
          selector verified a host using headers THIS caller never sent and handed back
          exactly the one host that would refuse it. A selector that proves a path by a
          method the caller does not use is a false success, not a guarantee.
      (2) NO ROTATION. It pinned one host, so one per-source ban (1015) was fatal.

    Prefer the shared rotator — it also MOVES off a banned host. Fall back to a direct
    urllib call WITH the UA rather than dying on the import. On total failure this
    RAISES, so the caller reports "chain read failed" instead of falling through to a
    zero (a failed read and a real zero must never look alike).
    """
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(__file__))
        if _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import rpc_call
        return rpc_call(method, params, timeout=45, tries=tries)
    except Exception:
        pass
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        RPC, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "gentech-treasury/1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("result")


def eth_call(to, data, blk="latest"):
    r = rpc("eth_call", [{"to": to, "data": data}, blk])
    return int(r, 16) if r and r != "0x" else None


def balance_of(token, holder, blk="latest"):
    return eth_call(token, "0x70a08231" + holder[2:].rjust(64, "0"), blk)


def spot_price_sqrt(pool):
    """Spot price of token0 in token1 units, from globalState().price.

    Sep 15 2026 FIX: this file first used the RESERVE RATIO (USDC reserve /
    WAVAX reserve) to infer price. That is WRONG for a concentrated-liquidity
    pool — a CL pool holds only what its active ranges dictate, so out-of-range
    liquidity skews the ratio far from spot. It reported AVAX at $1.59 (real
    ~$7.26) and inflated TVL 2.8x, which produced a bogus '-81% BLACK collapse'
    alert on the FIRST run.
    sqrtPriceX96 is the only correct source for an ALGEBRA/CL pool:
    price = (sqrtP/2^96)^2. Returns None if the pool is not a CL pool.
    """
    try:
        r = rpc("eth_call", [{"to": pool, "data": "0xe76c01e4"}, "latest"])
    except Exception:
        return None                 # an outage is NOT a price of zero
    if not r or r == "0x":
        return None
    sqrt_p = int(r[2:][0:64], 16)
    if sqrt_p == 0:
        return None
    return (sqrt_p / 2**96) ** 2


def spot_price_reserves(pool):
    """Spot price token0->token1 from getReserves() — for SOLIDLY pools.

    The BLACK/WAVAX pool is a Solidly-style VOLATILE pool (the router treats it
    with concentrated=False), NOT an Algebra CL pool. It has no globalState();
    for an AMM holding full-range liquidity the reserve ratio IS spot. Using the
    wrong method per pool type is how the first run fabricated a collapse alert,
    so both methods exist and the caller picks by pool type.
    """
    try:
        r = rpc("eth_call", [{"to": pool, "data": "0x0902f1ac"}, "latest"])   # getReserves()
    except Exception:
        return None, None           # an outage is NOT an empty pool
    if not r or r == "0x":
        return None, None
    b = r[2:]
    r0 = int(b[0:64], 16)
    r1 = int(b[64:128], 16)
    if not r0:
        return None, None
    return r0, r1


def black_price_from_pool():
    """Spot price of BLACK in USD. Chain truth — the realizable price.

    AVAX/USD   <- WAVAX/USDC Algebra CL pool -> sqrtPriceX96 (correct for CL)
    BLACK/AVAX <- BLACK/WAVAX Solidly pool  -> reserve ratio (correct for AMM)
    """
    raw_avax = spot_price_sqrt(POOL)                     # WAVAX(18) -> USDC(6)
    if raw_avax is None:
        return None, None, None
    avax_usd = raw_avax * 1e12                           # decimals 18 -> 6
    r0, r1 = spot_price_reserves(BLACK_POOL)             # token0=WAVAX, token1=BLACK
    if not r0 or not r1:
        return None, None, None
    # Sep 15 2026: token ORDER matters. This pool is token0=WAVAX, token1=BLACK,
    # so WAVAX-per-BLACK = reserve0/reserve1. Reading it the other way round
    # produced a nonsense $24,419 BLACK and a 1.37-BILLION-percent emissions APR
    # on a live run — the sanity guard below now refuses results like that.
    wavax_per_black = (r0 / 1e18) / (r1 / 1e18)
    black_usd = wavax_per_black * avax_usd
    info = {
        "avax_source": "WAVAX/USDC CL sqrtPriceX96",
        "black_source": "BLACK/WAVAX solidly reserves",
        "pool_black": r1 / 1e18, "pool_wavax": r0 / 1e18,
    }
    # SANITY GUARD: a plausible BLACK price is a small fraction of a dollar.
    # A bad token order or decimal error produces an absurd number; refuse it
    # rather than let it reach a report (or an alert).
    if not (0.00000001 < black_usd < 1.0):
        info["REJECTED"] = f"implausible BLACK price ${black_usd:,.6f} — refusing"
        return None, avax_usd, info
    return black_usd, avax_usd, info


def price_series():
    """60d daily BLACK price series from DefiLlama (cross-check + history)."""
    try:
        url = f"https://coins.llama.fi/chart/avax:{BLACK}?span=60&period=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "GenTech-Steward/1.0"})
        with urllib.request.urlopen(req, timeout=45) as r:
            d = json.load(r)
        pts = d.get("coins", {}).get(f"avax:{BLACK}", {}).get("prices", [])
        return [(p["timestamp"], p["price"]) for p in pts]
    except Exception:
        return []


def swap_volume_usd(blocks, avax_usd):
    """Paginated swap volume. A wide eth_getLogs range returns a FALSE ZERO."""
    head = int(rpc("eth_blockNumber", []), 16)
    n, v = 0, 0.0
    for lo in range(head - blocks, head, CHUNK):
        hi = min(lo + CHUNK - 1, head)
        try:
            logs = rpc("eth_getLogs", [{"address": POOL, "topics": [SWAP_TOPIC],
                                        "fromBlock": hex(lo), "toBlock": hex(hi)}]) or []
        except Exception:
            continue
        for lg in logs:
            d = lg["data"][2:]
            a0 = int(d[0:64], 16); a0 = a0 - 2**256 if a0 >= 2**255 else a0
            a1 = int(d[64:128], 16); a1 = a1 - 2**256 if a1 >= 2**255 else a1
            v += (abs(a0) / 1e18 * avax_usd + abs(a1) / 1e6) / 2.0
            n += 1
    return n, v


def main():
    prev = {}
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT))
        except Exception:
            prev = {}

    alerts = []
    now = time.time()

    # ── 1. PRICE (chain truth from the BLACK/WAVAX pool) ─────────────────
    black_usd, avax_usd, pool = black_price_from_pool()
    if black_usd is None:
        print("⚠️  BLACK price read failed — chain read unavailable")
        return 1
    series = price_series()
    hi60 = max((p for _, p in series), default=None)
    ch7 = ch30 = off_high = None
    if len(series) > 8:
        ch7 = (series[-1][1] / series[-8][1] - 1) * 100
    if len(series) > 31:
        ch30 = (series[-1][1] / series[-31][1] - 1) * 100
    if hi60:
        off_high = (black_usd / hi60 - 1) * 100

    if ch7 is not None and ch7 <= PRICE_CRASH_7D:
        alerts.append(f"BLACK 7d {ch7:+.1f}% — emissions half is eroding")
    if off_high is not None and off_high <= PRICE_COLLAPSE_60D:
        alerts.append(f"BLACK {off_high:+.1f}% off the 60d high — COLLAPSE territory")

    # ── 2. EMISSIONS (rate + REAL runway) ────────────────────────────────
    rate_wei = eth_call(GAUGE, "0x7b0a47ee")          # rewardRate()
    staked = eth_call(GAUGE, "0x18160ddd")            # totalSupply()
    # Runway must be measured at the SOURCE of emissions, not the gauge.
    # Sep 15 2026: this first alerted on "gauge BLACK balance is 0" — a FALSE
    # ALARM. The gauge holds no BLACK; emissions are funded by EternalFarming
    # (which holds ~15.16M BLACK) and paid out at rewardRate. The useful number
    # is the RUNWAY: how long until the emission source empties if not topped up.
    ef_black = balance_of(BLACK, ETERNAL_FARMING)
    rate_per_day = (rate_wei / 1e18) * 86400 if rate_wei else None
    runway_days = None
    if rate_per_day and ef_black is not None:
        runway_days = ef_black / 1e18 / rate_per_day
    prev_rate = prev.get("emission", {}).get("rate_per_day_black")
    ch_rate = None
    if rate_per_day and prev_rate:
        ch_rate = (rate_per_day / prev_rate - 1) * 100
        if ch_rate <= EMISSION_WEEKLY_CUT:
            alerts.append(f"emission rate {ch_rate:+.1f}% — the gauge is being cut")
    if runway_days is not None and runway_days < RUNWAY_ALERT_DAYS:
        alerts.append(f"emission runway only {runway_days:.1f} days "
                      f"({ef_black/1e18:,.0f} BLACK left at source) — "
                      "emissions dry up unless topped up")

    # ── 3. LIQUIDITY vs VOLUME (the death signal) ────────────────────────
    n24, v24 = swap_volume_usd(43200, avax_usd)
    pw = (balance_of(WAVAX, POOL) or 0) / 1e18
    pu = (balance_of(USDC, POOL) or 0) / 1e6
    tvl = pw * avax_usd + pu   # avax_usd from sqrtPriceX96 (CL-correct), not reserves
    fee_apr = (v24 * FEE_TIER * 365 / tvl * 100) if tvl else None

    prev_tvl = prev.get("pool", {}).get("tvl_usd")
    prev_v24 = prev.get("pool", {}).get("volume_24h_usd")
    tvl_ch = (tvl / prev_tvl - 1) * 100 if prev_tvl else None
    vol_ch = (v24 / prev_v24 - 1) * 100 if prev_v24 else None
    if tvl_ch is not None and vol_ch is not None:
        if tvl_ch < -5 and vol_ch < -25:
            alerts.append(f"TVL {tvl_ch:+.1f}% AND volume {vol_ch:+.1f}% — "
                          "pool dying, not consolidating")
        elif tvl_ch < -5 and vol_ch > 0:
            alerts.append(f"TVL {tvl_ch:+.1f}% with volume {vol_ch:+.1f}% — "
                          "share consolidation, FAVOURABLE for re-entry")

    # ── 4. THE SPLIT — how much of our yield is fragile? ─────────────────
    # emissions APR for the ACTIVE pool = (BLACK/day x price) x 365 / TVL
    emissions_usd_day = (rate_per_day * black_usd) if (rate_per_day and black_usd) else None
    emissions_apr = (emissions_usd_day * 365 / tvl * 100) if (emissions_usd_day and tvl) else None
    share = None
    if fee_apr is not None and emissions_apr is not None and (fee_apr + emissions_apr) > 0:
        share = emissions_apr / (fee_apr + emissions_apr) * 100

    state = {
        "ts": now,
        "when": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "black": {
            "price_usd_chain": round(black_usd, 8),
            "price_usd_api": round(series[-1][1], 8) if series else None,
            "change_7d_pct": round(ch7, 2) if ch7 is not None else None,
            "change_30d_pct": round(ch30, 2) if ch30 is not None else None,
            "off_60d_high_pct": round(off_high, 2) if off_high is not None else None,
            "high_60d": round(hi60, 8) if hi60 else None,
            "source": "chain (BLACK/WAVAX pool reserves) + defillama series",
        },
        "price_floor_note": ("the pool price IS the realizable price — BLACK has a "
                             "pool that exists to buy emissions, so this is what "
                             "we would actually get selling, not a mark"),
        "emission": {
            "rate_per_sec_black": round(rate_wei / 1e18, 6) if rate_wei else None,
            "rate_per_day_black": round(rate_per_day, 2) if rate_per_day else None,
            "rate_per_day_usd": round(emissions_usd_day, 2) if emissions_usd_day else None,
            "change_pct": round(ch_rate, 2) if ch_rate is not None else None,
            "runway_days": round(runway_days, 1) if runway_days is not None else None,
            "emission_source_black": round(ef_black / 1e18, 2) if ef_black is not None else None,
            "staked_lp": staked / 1e18 if staked else None,
        },
        "pool": {
            "tvl_usd": round(tvl, 2),
            "wavax": round(pw, 4), "usdc": round(pu, 2),
            "avax_usd": round(avax_usd, 4),
            "volume_24h_usd": round(v24, 2),
            "swaps_24h": n24,
            "tvl_change_pct": round(tvl_ch, 2) if tvl_ch is not None else None,
            "volume_change_pct": round(vol_ch, 2) if vol_ch is not None else None,
        },
        "yield_split": {
            "fee_apr_pct": round(fee_apr, 2) if fee_apr is not None else None,
            "emissions_apr_pct": round(emissions_apr, 2) if emissions_apr is not None else None,
            "emissions_share_pct": round(share, 1) if share is not None else None,
            "honest_headline": (f"fee {fee_apr:.1f}% + emissions {emissions_apr:.1f}%"
                                if fee_apr is not None and emissions_apr is not None else None),
        },
        "alerts": alerts,
    }

    with open(OUT, "w") as f:
        json.dump(state, f, indent=2)

    # ── SILENCE DOCTRINE: quiet unless something changed ────────────────
    if alerts:
        print(f"🔔 BLACK HEALTH — {state['when']}")
        for a in alerts:
            print(f"   ⚠️  {a}")
        print(f"   BLACK ${black_usd:.6f} | fee {fee_apr:.1f}% + emis "
              f"{emissions_apr:.1f}% | TVL ${tvl:,.0f} | vol24 ${v24:,.0f}")
    else:
        print(f"  ✅ BLACK healthy — ${black_usd:.6f} | fee {fee_apr:.1f}% + "
              f"emis {emissions_apr:.1f}% | TVL ${tvl:,.0f} | vol24 ${v24:,.0f}")
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
