#!/usr/bin/env python3
"""
fee_ledger.py — what is this position actually EARNING? (Jordan, 2026-09-23)

WHY THIS EXISTS:
    Jordan, looking at the hub: "Fee efficiency should be zero".
    He was right to ask, and right about the cause: the tile said "Fee efficiency — is this
    shape earning?", so he read it as EARNINGS. It is not. `fee_efficiency.py` scores where
    spot sits INSIDE the band -- a placement score. At dead centre a bid-ask reads 0%, at
    the edge 90%; nothing in that number is a dollar.
    And on LFJ V2.2 there is no per-position fee counter to read, because **fees are
    auto-compounded straight into the bins**. They arrive as the position holding MORE, not
    as a separate claimable balance.
    So "how much have we earned" had no reader at all. This is that reader.

HOW IT ISOLATES FEES FROM PRICE:
    The position's underlying holdings (our_wavax, our_usdc) change for two reasons: the
    price moves, and fees accrue. Measuring the raw total would conflate them -- exactly the
    "confident number from the wrong quantity" failure this fleet keeps finding.
    An LP's claim factorises as value = 2*sqrt(x*y*P) for the constant-product region, where
    only the sqrt(x*y) term grows with fees. So this records the **fee factor**:

        fee_factor = sqrt(our_wavax * our_usdc)

    which is INVARIANT to price by construction. Any growth in it is fees (it can only move
    if the position genuinely holds more of both sides). Reported as a rate once it has
    enough history.
    We also store the raw amounts and the price, so the arithmetic stays auditable and a
    later reviewer can recompute rather than trust this file's summary.

HONEST NULL:
    With fewer than 2 snapshots spanning real time it reports NO HISTORY, never a number.
    An instrument that cannot yet measure must not output something that looks like a
    measurement -- the whole point of today.

CLI: python3 fee_ledger.py --tenant jordan [--json] [--reset]
Exit 0 always.
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PAIR = "0x864d4E5Ee7318e97483DB7EB0912E09F161516EA"
MAX_SNAPSHOTS = 4000

# ── SEGMENTATION THRESHOLDS (2026-09-26) ────────────────────────────────────────────────────────
# A fee rate may only be measured across a run of readings that a FEE could have produced.
# REBUILD_JUMP: a single reading-to-reading move in the fee factor larger than this is a rebuild,
#   not income. Fees accumulate multiplicatively and slowly; a 10% one-step jump on this book is
#   far outside anything a fee does in one 15-minute sample (measured: 26% of the historical steps
#   exceed 20%, all of them rebuilds).
# MAX_GAP_S: a gap longer than this between readings means we cannot know what happened in
#   between, so the run ends rather than bridging the unknown. Matches the 15-min snapshot cron
#   with generous headroom.
# MIN_SEG_H: a run shorter than this spans too little time for a fee rate to be distinguishable
#   from noise, so it is reported as unusable rather than extrapolated to a daily figure.
REBUILD_JUMP = 0.10          # 10% one-step move in fee factor = rebuild
MAX_GAP_S = 2 * 3600         # readings more than 2h apart cannot be bridged
MIN_SEG_H = 2.0              # a run must span at least 2h to yield a rate


def ledger_path(tenant):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        f".fee-ledger-{tenant}.json")


def load(tenant):
    try:
        with open(ledger_path(tenant)) as f:
            d = json.load(f)
        if isinstance(d, dict) and isinstance(d.get("snapshots"), list):
            return d
    except Exception:
        pass
    return {"snapshots": []}


def save(tenant, d):
    d["snapshots"] = d["snapshots"][-MAX_SNAPSHOTS:]
    tmp = ledger_path(tenant) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, ledger_path(tenant))


def read_position(tenant):
    """Our holdings in the pool, bin by bin, valued from the bin reserves -- the chain, not config."""
    import avax_rpc
    import fee_efficiency as FE
    import tenant_guard as TG
    from web3 import Web3

    rec = TG.registered(tenant) or {}
    wallet = rec.get("wallet")
    if not wallet:
        return None, "no wallet registered for this tenant"

    w3 = avax_rpc.connect(timeout=45)
    pair = Web3.to_checksum_address(PAIR)
    act = int.from_bytes(w3.eth.call({"to": pair,
                                      "data": Web3.keccak(text="getActiveId()")[:4]}), "big")
    price = float(FE._price_at(w3, act))

    bal_sel = Web3.keccak(text="balanceOf(address,uint256)")[:4]
    bin_sel = Web3.keccak(text="getBin(uint24)")[:4]
    sup_sel = Web3.keccak(text="totalSupply(uint256)")[:4]
    W = Web3.to_checksum_address(wallet)

    our_x = our_y = 0.0
    bins = 0
    for b in range(act - 120, act + 121):
        try:
            raw = w3.eth.call({"to": pair,
                               "data": bal_sel + bytes.fromhex(W[2:].rjust(64, "0")) + b.to_bytes(32, "big")})
            bal = int.from_bytes(raw, "big") if raw else 0
            if bal <= 0:
                continue
            # ── getBin RETURNS TWO WORDS, NOT THREE (fixed 2026-09-23, same minute) ─────
            # `getBin(uint24)` returns (uint128 reserveX, uint128 reserveY). I read a third word
            # as the supply, reusing the ABI that DOESN'T exist -- so every bin failed my
            # `supply == 0` test, all 46 were skipped, and the tool reported "no position held"
            # on a book with 45 bins. Identical in shape to the false-flat this fleet has been
            # burned by before: A DECODE FAILURE IS NOT A MISSING POSITION.
            # totalSupply is a separate call taking the bin id (verified against the working
            # reader in defi_hub_data.py, which uses exactly this pair of calls).
            raw = w3.eth.call({"to": pair, "data": bin_sel + b.to_bytes(32, "big")})
            if not raw or len(raw) < 64:
                return None, f"getBin returned {len(raw) if raw else 0} bytes — cannot decode"
            rx = int.from_bytes(raw[0:32], "big")
            ry = int.from_bytes(raw[32:64], "big")
            supply = int.from_bytes(
                w3.eth.call({"to": pair, "data": sup_sel + b.to_bytes(32, "big")}), "big")
            if supply == 0:
                continue
            our_x += rx * bal / supply / 1e18
            our_y += ry * bal / supply / 1e6
            bins += 1
        except Exception:
            continue

    if bins == 0:
        return {"flat": True, "price": price, "bins": 0, "our_wavax": 0.0, "our_usdc": 0.0}, None
    return {"flat": False, "price": price, "bins": bins,
            "our_wavax": our_x, "our_usdc": our_y}, None


def main():
    ap = argparse.ArgumentParser(description="What is the position actually earning?")
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--reset", action="store_true")
    a = ap.parse_args()

    if a.reset:
        save(a.tenant, {"snapshots": []})
        print("  ledger reset")
        return 0

    pos, err = read_position(a.tenant)
    if err:
        print(f"  \u26a0\ufe0f  cannot read the position: {err}")
        return 0
    assert pos is not None      # narrowed: the error path returned above

    d = load(a.tenant)
    now = int(time.time())

    if pos["flat"]:
        # A FLAT BOOK HAS NO FEE LEDGER. Say so rather than record a zero that reads as "no fees".
        print(f"  no position held \u2014 a flat book earns nothing and is not a fee reading "
              f"(price ${pos['price']:.4f})")
        return 0

    x, y = pos["our_wavax"], pos["our_usdc"]
    fee_factor = math.sqrt(x * y) if (x > 0 and y > 0) else 0.0
    snap = {"t": now, "price": pos["price"], "bins": pos["bins"],
            "our_wavax": x, "our_usdc": y, "fee_factor": fee_factor,
            "value_usd": x * pos["price"] + y}
    # ── A REDEPLOY IS NOT AN EARNING (Jordan, 2026-09-23) ───────────────────────────
    # The fee factor is sqrt(wavax * usdc). Fees raise it. But a REBUILD also moves it -- changing
    # the shape (45->25 bins) or the ratio (70/30->50/50) changes the mix, so the factor jumps with
    # no fee earned at all. Measured tonight: 17.546 -> 18.867 across two rebuilds, which would have
    # reported a fat fake APR. So mark the rebuild and let the rate be computed only WITHIN a
    # rebuild-free segment -- the same refusal-to-guess principle as "no history, no number".
    prev = d["snapshots"][-1] if d["snapshots"] else None
    snap["rebuild"] = bool(prev and prev.get("bins") != snap.get("bins"))
    d["snapshots"].append(snap)
    save(a.tenant, d)

    snaps = d["snapshots"]
    out = {"tenant": a.tenant, "snapshots": len(snaps), "now": snap}

    if len(snaps) < 2:
        if a.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"\n  \U0001F4D2 FEE LEDGER \u2014 {a.tenant}")
            print(f"  {'-'*60}")
            print(f"  position   {pos['bins']} bins   {x:.6f} WAVAX + {y:.4f} USDC")
            print(f"  value      ${snap['value_usd']:.2f}   at AVAX ${pos['price']:.4f}")
            print(f"  fee factor {fee_factor:.6f}   (sqrt of the two sides \u2014 price-invariant)")
            print(f"  {'-'*60}")
            print("  NO HISTORY YET \u2014 one snapshot. This cannot report a fee rate until it has")
            print("  two readings spanning real time. It will not guess one in the meantime.")
            print(f"  {'-'*60}\n")
        return 0

    first = snaps[0]
    span_hr = max((now - first["t"]) / 3600.0, 1e-9)

    # ── THE RATE IS MEASURED PER CONTINUOUS DEPLOYMENT SEGMENT (fixed 2026-09-26) ────────────
    # THE DEFECT, and it reported a wildly false number: this computed
    #     rel = (fee_factor - first["fee_factor"]) / first["fee_factor"]
    # i.e. the WHOLE history's first reading against its last, and called the difference fees. But
    # a withdraw/redeploy is not an earning, and today's book was rebuilt many times: across 241
    # snapshots the fee factor hit EXACTLY 0.0000 on 20 of them (the position was empty mid-rebuild)
    # and 55 of 208 step changes exceeded +/-20% (worst -97.5%, best +16515%). Measured across all
    # of that, jordan's ledger printed:
    #     "+13.7592% compounded = +4.572%/day (+1668.7% APR)"
    # while the house's own independent estimator said ~$0.18/day. The APR was a REBUILD ARTIFACT.
    #
    # Worse, the fix was already WRITTEN in this file ~30 lines above -- "mark the rebuild and let
    # the rate be computed only WITHIN a rebuild-free segment" -- and it failed twice over:
    #   (a) nothing ever READ the `rebuild` flag when computing the rate; and
    #   (b) it defined a rebuild as `prev["bins"] != snap["bins"]`, but our rebuilds KEEP 45 bins
    #       (a 45-bin bid-ask redeploys as a 45-bin bid-ask), so the flag never fired. Verified on
    #       today's data: value_usd stepped $144.68 -> $43.50 -> $145.90 in ~20 minutes with `bins`
    #       unchanged at 45 throughout.
    # This is the "written down, correct, and dead" family. The rate now comes from contiguous
    # runs that a fee could plausibly have produced, and it refuses to invent one when there are
    # no such runs.
    def _segments(rows):
        segs, cur = [], []
        for s in rows:
            ff = float(s.get("fee_factor") or 0)
            if ff <= 0:
                if len(cur) >= 2:
                    segs.append(cur)
                cur = []                              # empty position: the run ends here
                continue
            if cur:
                p = float(cur[-1].get("fee_factor") or 0)
                gap = s.get("t", 0) - cur[-1].get("t", 0)
                if (cur[-1].get("bins") != s.get("bins")
                        or (p > 0 and abs(ff / p - 1) > REBUILD_JUMP)
                        or gap > MAX_GAP_S):
                    if len(cur) >= 2:
                        segs.append(cur)              # a jump = a rebuild between readings
                    cur = []
            cur.append(s)
        if len(cur) >= 2:
            segs.append(cur)
        return segs

    segs = _segments(snaps)
    rates = []
    for seg in segs:
        hrs = (seg[-1]["t"] - seg[0]["t"]) / 3600.0
        a0, a1 = float(seg[0]["fee_factor"]), float(seg[-1]["fee_factor"])
        if hrs < MIN_SEG_H or a0 <= 0:
            continue
        rel_seg = (a1 / a0 - 1.0) * 100.0
        rates.append({"rel_pct": rel_seg, "hours": hrs, "per_day": rel_seg / (hrs / 24.0),
                      "from": seg[0]["t"], "to": seg[-1]["t"], "n": len(seg)})

    if not rates:
        # No continuous run long enough to attribute. SAY SO — never fall back to the
        # whole-history subtraction that produced the false APR.
        if a.json:
            print(json.dumps({"tenant": a.tenant, "snapshots": len(snaps),
                              "segments": len(segs), "rate": None,
                              "reason": "no rebuild-free segment long enough to measure"},
                             indent=2))
            return 0
        print(f"\n  \U0001F4D2 FEE LEDGER \u2014 {a.tenant}")
        print(f"  {'-'*60}")
        print(f"  history    {len(snaps)} snapshots over {span_hr:.1f}h")
        print(f"  segments   {len(segs)} rebuild-free runs, none longer than {MIN_SEG_H:.0f}h")
        print(f"  {'-'*60}")
        print("  NO RATE \u2014 every continuous deployment run was too short to measure a fee rate.")
        print("  (A withdraw/redeploy moves the fee factor without earning anything, so a rate")
        print("  computed across one is an artifact, not income. Refusing to print it.)")
        print(f"  {'-'*60}\n")
        return 0

    per_days = sorted(r["per_day"] for r in rates)
    mid = per_days[len(per_days) // 2] if len(per_days) % 2 else \
        (per_days[len(per_days) // 2 - 1] + per_days[len(per_days) // 2]) / 2.0

    # ── A NEGATIVE FEE RATE IS IMPOSSIBLE, AND DISAGREEING SEGMENTS MEAN NO MEASUREMENT ───────
    # LP fees are non-negative by construction — a pool can pay you nothing, never a negative
    # amount. So a NEGATIVE rate is not a small earning, it is the instrument reporting its own
    # noise, and the same "false-value" family this file already refuses elsewhere ("no history, no
    # number").
    #
    # MEASURED on jordan's real history (2026-09-26): 34 rebuild-free runs, 5 long enough to use,
    # giving per-day rates of **-115.8%, -0.45% and +33.7%**. A spread of that size across
    # segments of the SAME position means the segments are not measuring a common rate, so their
    # median is not a rate either. (The fee factor's own premise checks out — within rebuild-free
    # runs its correlation with price is +0.046, i.e. genuinely price-invariant — so the residual
    # noise is the position's bin COMPOSITION changing as price crosses bins, which moves
    # sqrt(x*y) without any fee being earned. That is a flaw in the metric, not in the sampling.)
    #
    # Rather than print a confidently wrong second number — the first was +1668.7% APR — this now
    # refuses and NAMES the open defect. A trustworthy earnings figure has to come from fees
    # observed per unit of deployed capital over time; it cannot be read off this factor yet.
    if per_days[-1] > 0 and per_days[0] < 0 and (per_days[-1] - per_days[0]) > 1.0:
        if a.json:
            print(json.dumps({"tenant": a.tenant, "snapshots": len(snaps),
                              "segments": len(segs), "segments_used": len(rates),
                              "rate": None,
                              "reason": "segments disagree in sign — not a measurement",
                              "rate_per_day_segments": [round(x, 4) for x in per_days]}, indent=2))
            return 0
        print(f"\n  \U0001F4D2 FEE LEDGER \u2014 {a.tenant}")
        print(f"  {'-'*60}")
        print(f"  position   {pos['bins']} bins   {x:.6f} WAVAX + {y:.4f} USDC")
        print(f"  value      ${snap['value_usd']:.2f}   at AVAX ${pos['price']:.4f}")
        print(f"  history    {len(snaps)} snapshots over {span_hr:.1f}h")
        print(f"  segments   {len(segs)} rebuild-free runs, {len(rates)} long enough to use")
        print(f"  {'-'*60}")
        print("  NO TRUSTWORTHY RATE \u2014 the segments disagree in SIGN:")
        print(f"    {', '.join(f'{v:+.2f}%/day' for v in per_days)}")
        print("  LP fees are never negative, so the negative readings are the instrument's own")
        print("  noise, not a loss. sqrt(wavax*usdc) moves when price crosses bins and changes the")
        print("  position's COMPOSITION, with no fee earned \u2014 so this factor cannot isolate fees")
        print("  yet. Refusing to publish a rate rather than print a second wrong one.")
        print("  For $/day use compound_status (pool_economics / house_estimator), which measure")
        print("  fees directly and are already on the hub.")
        print(f"  {'-'*60}\n")
        return 0

    # Back-compat: the old keys, now carrying the MEDIAN SEGMENT rate rather than the
    # whole-history subtraction, so any caller reading them gets the honest number.
    rel = mid * (span_hr / 24.0)
    per_day = mid

    out.update({"span_hours": span_hr, "fee_factor_change_pct": rel,
                "compounded_pct_per_day": per_day,
                "segments": len(segs), "segments_used": len(rates),
                "rate_source": "median of rebuild-free segments",
                "rate_per_day_min": per_days[0], "rate_per_day_max": per_days[-1],
                "rate_per_day_median": mid})
    if a.json:
        print(json.dumps(out, indent=2))
        return 0

    print(f"\n  \U0001F4D2 FEE LEDGER \u2014 {a.tenant}")
    print(f"  {'-'*60}")
    print(f"  position   {pos['bins']} bins   {x:.6f} WAVAX + {y:.4f} USDC")
    print(f"  value      ${snap['value_usd']:.2f}   at AVAX ${pos['price']:.4f}")
    print(f"  history    {len(snaps)} snapshots over {span_hr:.1f}h")
    print(f"  {'-'*60}")
    print(f"  fee factor {first['fee_factor']:.6f} -> {fee_factor:.6f}")
    print(f"  COMPOUNDED {rel:+.4f}%  =  {per_day:+.3f}% per day  ({per_day*365:+.1f}% APR)")
    print(f"  {'-'*60}")
    print("  This is the EARNINGS number. The 'Band placement' tile on the hub is a different")
    print("  question (where spot sits inside the shape) -- it is not this.")
    print(f"  {'-'*60}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
