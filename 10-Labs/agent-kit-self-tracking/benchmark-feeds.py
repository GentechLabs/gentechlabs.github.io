#!/usr/bin/env python3
"""Benchmark-feeds writer — live LP fee APR + live AVAX staking benchmark.

Writes two freshness-gated files that pool-reader.py consumes so the dashboard
never renders fabricated yield numbers again:

  staking-apr-live.json  — AVAX staking benchmark (Benqi sAVAX liquid staking)
  lp-fees-live.json      — the LP benchmark for the venue we ACTUALLY farm:
                           Blackhole CLMM WAVAX-USDC (our active rail)

Sep 15 2026 FIX: this file quoted joe-v2.2 WAVAX-USDC — the RETIRED LFJ venue we
left on Sep 8. A benchmark is supposed to measure ourselves; instead it measured
a venue we no longer use, so it never validated the number we report. Jordan
caught it. It now benchmarks Blackhole CLMM, and also records the field
(Pharaoh / UniV3 / sAVAX) so we can see whether our rail is actually competitive.

Source: DefiLlama yields API /pools listing. The single-pool endpoint 404s, so
we download the full listing and filter by pool id.
Usage: python3 benchmark-feeds.py   (idempotent; exit 0 on success)
"""
import json
import time
import urllib.request

# The staking benchmark is no longer a single pool id — it is the AVERAGE across AVAX staking
# providers, built by staking_benchmark.py (on-chain exchange rates where readable).
# The old single-protocol id is kept only so the history of this file is legible.
STAKING_POOL_ID = "3790c3e5-8644-4f6b-8feb-12434d8b99f9"  # RETIRED: benqi sAVAX only (one protocol != market)
# OUR ACTIVE FARM RAIL: LFJ (Trader Joe) v2.2 WAVAX-USDC — the pool we are actually in.
# This said "blackhole-clmm" and claimed that was "our active farm rail". It was not: we farm
# LFJ. So the benchmark measured a venue we are not in and could never validate our own number.
# Jordan's venue-scope rule: "let's only have the information for the pool that we're in."
LP_PROJECT = "joe-v2.2"
LP_SYMBOL = "WAVAX-USDC"
LP_POOL_ID = "e8e45a86-cd5f-4d8e-9614-0dbd178da741"        # retired LFJ instance, for reference
# Field comparison — so the benchmark says whether our rail is competitive.
FIELD = [("pharaoh-v3", "WAVAX-USDC"), ("uniswap-v3", "WAVAX-USDC"),
         ("blackhole-clmm", "WAVAX-USDC"), ("beefy", "WAVAX-USDC")]
OUT_STAKING = "/root/.hermes/profiles/gentech/scripts/staking-apr-live.json"
OUT_LP = "/root/.hermes/profiles/gentech/scripts/lp-fees-live.json"


def fetch_all():
    url = "https://yields.llama.fi/pools"
    req = urllib.request.Request(url, headers={"User-Agent": "GenTech-Steward/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r).get("data", [])


def mean_apy(pool_id: str, days: int = 30):
    """Mean apyBase over `days` from DefiLlama's chart — the HONEST figure.

    WHY (Jordan, 2026-09-21): the listing's `apy` field is a POINT-IN-TIME snapshot. Our own
    rail read 243.78% as a snapshot while its 30d mean was 55.08% — a 4.4x gap, with nothing in
    the payload saying which one you were getting. A benchmark that quotes the hot snapshot will
    make every strategy look like it is failing, and it will read as OUR yield in any report
    that consumes this file. Same class of error as the Blackhole APR that drove the
    venue-scope fix: a number about someone else's moment presented as our performance.

    Returns (mean, n) or (None, 0) — never a fabricated number.
    """
    try:
        req = urllib.request.Request(f"https://yields.llama.fi/chart/{pool_id}",
                                     headers={"User-Agent": "GenTech-Steward/1.0"})
        ch = json.load(urllib.request.urlopen(req, timeout=45)).get("data", [])
    except Exception:
        return None, 0
    vals = [x["apyBase"] for x in ch[-(days * 4):] if x.get("apyBase") is not None]
    if not vals:
        return None, 0
    return sum(vals) / len(vals), len(vals)


def main():
    now = time.time()
    pools = fetch_all()

    # ── STAKING BENCHMARK: THE AVERAGE STAKER, NOT ONE PROTOCOL (Jordan, 2026-09-21) ────────
    # Jordan: "when we're comparing staking, we want to look for the average staker, not just
    # from SAVAX or BENQI. We kind of want to get a measurement of all the staking platforms and
    # kind of get an average."
    #
    # This used to pin STAKING_POOL_ID to a SINGLE pool (benqi sAVAX) and report that one number
    # as "staking". One protocol is not the market — measured 2026-09-21 the field spanned 0.08%
    # to 6.32%/yr. The average now comes from staking_benchmark.py, which prefers a direct
    # on-chain read of each provider's exchange rate (the reward actually passed through, which
    # incentive tokens cannot inflate) and says which providers were measured vs sourced.
    try:
        import staking_benchmark as SB
        st = SB.measure()
    except Exception as e:
        print(f"❌ staking benchmark unavailable ({str(e)[:80]}) — keeping previous file")
        st = None

    # our live rail: the LFJ (Trader Joe) v2.2 WAVAX-USDC pool we ACTUALLY farm.
    # This previously benchmarked Blackhole CLMM — a venue we are not in — so it measured
    # someone else's pool and never validated the number we report (Jordan's venue-scope rule:
    # "let's only have the information for the pool that we're in").
    cands = [x for x in pools if x.get("project") == LP_PROJECT and x.get("symbol") == LP_SYMBOL]
    p = max(cands, key=lambda x: x.get("tvlUsd") or 0) if cands else None
    if not p:
        print(f"❌ LP pool not found in listing (project={LP_PROJECT} symbol={LP_SYMBOL}) — keeping previous files")
        return 1

    lapy = p.get("apy")
    if lapy is None:
        print("❌ missing LP APY field — keeping previous files")
        return 1

    if st:
        json.dump(st, open(OUT_STAKING, "w"), indent=2)
        print(f"✅ staking benchmark: {st['apr']:.2f}% APY — average of {st['n']} live providers "
              f"(median {st['median']:.2f}%, spread {st['spread']['min']:.2f}-{st['spread']['max']:.2f}%)")
        for r in st["providers"]:
            tag = "EXCLUDED" if r.get("dormant") else (f"{r['apr']:.2f}%" if r.get("apr") is not None else "n/a")
            print(f"     {r['name']:<24}{tag:>10}   {r['source'][:56]}")

    # field comparison — each entry: project/symbol -> apy
    field = []
    for proj, sym in FIELD:
        m = [x for x in pools if x.get("project") == proj and x.get("symbol") == sym]
        if m:
            b = max(m, key=lambda x: x.get("tvlUsd") or 0)
            field.append({"project": proj, "symbol": sym, "apy": b.get("apy"),
                          "apyBase": b.get("apyBase"), "apyReward": b.get("apyReward"),
                          "tvlUsd": b.get("tvlUsd")})

    # Quote the 30d MEAN as the benchmark, not the point-in-time snapshot. Keep both so the
    # consumer can see the gap rather than being handed one number with no provenance.
    mean30, n30 = mean_apy(p.get("pool"), 30)
    bench = mean30 if mean30 is not None else lapy
    bench_basis = ("30d mean apyBase" if mean30 is not None
                   else "SNAPSHOT (30d mean unavailable — treat as a moment, not a rate)")

    json.dump({"apy": round(bench, 2), "apyBasis": bench_basis,
               "apySnapshot": round(lapy, 2), "apyBase": p.get("apyBase"),
               "apyMean30d": (round(mean30, 2) if mean30 is not None else None),
               "mean30dSamples": n30,
               "apyReward": p.get("apyReward"), "ts": now,
               "source": f"defillama:{LP_PROJECT} {LP_SYMBOL} (our active rail)",
               "symbol": p.get("symbol"), "project": p.get("project"),
               "tvlUsd": p.get("tvlUsd"), "field": field},
              open(OUT_LP, "w"), indent=2)
    print(f"✅ LP benchmark (our rail): {LP_PROJECT} {LP_SYMBOL} {bench:.2f}% APY  [{bench_basis}]")
    print(f"     snapshot {lapy:.2f}%  vs  30d mean "
          f"{f'{mean30:.2f}%' if mean30 is not None else 'n/a'}  "
          f"(TVL ${p.get('tvlUsd'):,.0f}, {n30} samples)")
    for f in sorted(field, key=lambda x: -(x.get("apy") or 0)):
        print(f"     field: {f['project']:<14}{f['symbol']:<14}{f['apy']:>8.1f}%  "
              f"${f['tvlUsd']:>12,.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())