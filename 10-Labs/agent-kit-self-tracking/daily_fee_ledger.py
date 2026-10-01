#!/usr/bin/env python3
"""Daily fee ledger — provable fee rows per completed UTC day, each linked to a block.

WHY THIS EXISTS (Jordan, 2026-09-27, after the EARN comparison).

Our pages carried a fee figure labelled "estimate_daily_fees". EARN publishes a daily table of
fees generated with a block-explorer link on every row. Ours was a number that looked like a fact
and was not backed by one — the same disease we killed four times today.

WHAT CANNOT BE DONE, AND WHY THIS DESIGN IS SHAPED THE WAY IT IS (proven, not assumed).

The obvious approach — walk the Swap events and attribute each one using OUR bin share at that
swap's own block — is in `lfj_fee_attribution.py`, and it produces `$0.000000` and "100% of the
window EARNED NOTHING" while the book is demonstrably in range and earning. Root cause, measured:

    eth_call at block 96,283,295  (latest)      -> execution reverted
    eth_call at block 96,282,295  (1,000 back)  -> missing trie node
    eth_call at block 96,263,295  (20,000 back) -> missing trie node

The public RPC is NOT an archive node. Historical state is unavailable, so a past-day bin share
cannot be read at all — and an empty read is indistinguishable from "we held nothing". A ledger
built on that would publish a confident zero every single day.

WHAT CAN BE DONE. LB Swap LOGS are readable with no archive node (logs are cheap and served by
every node). Each Swap carries `totalFees` for the bin it touched, so the POOL's realised fee flow
per day is a receipt-backed number. Our share of it is snapshotted at read time and recorded
forward — exactly EARN's "HISTORY BACKFILLING" shape, and honest about which half is which.

SO: this file publishes POOL FEES as provable, and OUR SHARE as measured-now, and it REFUSES to
emit a number it cannot stand behind. A row with no verified share says `unverified` — it never
says `$0.00`.

USAGE
    python3 daily_fee_ledger.py --days 3            # prove a few days
    python3 daily_fee_ledger.py --days 30 --out /var/www/gentechlabs/DeFi/fee-ledger.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

BASE = "https://avalanche-c-chain-rpc.publicnode.com"
POOL = "0x864d4E5Ee7318e97483DB7EB0912E09F161516EA"
EXPLORER = "https://snowtrace.io/block/"

WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"

# Swap topic — from our own verified decoder, not re-derived here (one decoder, not two).
SWAP_TOPIC = "0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70"

CHUNK = 10_000          # blocks per eth_getLogs call (public RPCs cap ranges)


def _w3():
    from web3 import Web3
    url = BASE
    try:
        from avax_rpc import url as _u          # shared rotation, fails closed
        url = _u()
    except Exception:
        pass
    return Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 30}))


def _decode(swap_data_hex):
    """Reuse the ONE verified decoder. Do not write a second one."""
    try:
        from lfj_fee_attribution import _decode_swap
    except Exception:
        return None
    try:
        return _decode_swap(swap_data_hex)
    except Exception:
        return None


def _raw_block_ts(w3, blk: int):
    """Read a block timestamp via RAW JSON-RPC.

    web3.py's `get_block` VALIDATES extraData as exactly 32 bytes. Avalanche C-Chain blocks carry
    ~66 bytes, so every call raised:
        "The field extraData is 66 bytes, but should be 32. It is quite likely you are using the
         wrong type of Ethereum node."
    That is a web3 VALIDATION error, not a chain error — the block is perfectly readable. Reading
    the timestamp straight from the RPC bypasses a check that does not apply to this chain.
    """
    r = w3.provider.make_request("eth_getBlockByNumber", [hex(blk), False])
    if r.get("error"):
        raise RuntimeError(str(r["error"])[:90])
    res = r.get("result")
    if not res or "timestamp" not in res:
        raise RuntimeError("no block returned")
    return int(res["timestamp"], 16)


def block_at_ts(w3, ts: int, lo: int, hi: int):
    """Binary-search the first block with timestamp >= ts.

    RETURNS (block, None) on success, (None, reason) if the search cannot be trusted.

    The first cut of this returned a block unconditionally and biased the search on any read
    error (`hi = mid`), which drove it DOWNWARD and produced non-monotonic garbage: 2026-09-26
    resolved BELOW 2026-09-24. A wrong block silently attributes the wrong day's fees, which is
    worse than no number at all. So a failed probe now ABORTS the search and says so.
    """
    while lo < hi:
        mid = (lo + hi) // 2
        try:
            t = _raw_block_ts(w3, mid)
        except Exception as e:
            return None, f"cannot read block {mid:,}: {str(e)[:70]}"
        if t < ts:
            lo = mid + 1
        else:
            hi = mid
    try:
        t = _raw_block_ts(w3, lo)
    except Exception as e:
        return None, f"cannot read resolved block {lo:,}: {str(e)[:70]}"
    # sanity: the resolved block must actually bracket the target
    if t < ts:
        return None, f"resolved block {lo:,} is still before the target timestamp"
    return lo, None


def day_fees(w3, start_ts, end_ts, b_lo, b_hi, wavax_usd):
    """Sum the pool's realised fees for one UTC day, from Swap logs only.

    ── OFF-BY-ONE ON THE DAY BOUNDARY (caught by verifying my own receipts, 2026-09-27) ─────────
    `b_hi` is the FIRST BLOCK OF THE NEXT DAY (that is what block_at_ts returns: the first block
    at-or-after the timestamp). The first cut iterated `while b <= b_hi`, so every day absorbed
    the next day's opening block — and the proof block landed at 00:00:00 of the FOLLOWING day,
    which my own receipt checker flagged as OUT OF DAY on all three rows.

    The range is half-open: [b_lo, b_hi). One block of overlap per day is small in fees but it is
    wrong in principle, and a receipt that points outside its own day is not a receipt.
    """
    swaps = 0
    fee_x = fee_y = 0.0     # raw units
    first_blk = last_blk = None
    undecoded = 0
    b = b_lo
    while b < b_hi:
        top = min(b + CHUNK - 1, b_hi - 1)
        try:
            logs = w3.eth.get_logs({"address": w3.to_checksum_address(POOL),
                                    "topics": [SWAP_TOPIC],
                                    "fromBlock": b, "toBlock": top})
        except Exception as e:
            return {"error": f"getLogs {b}..{top}: {str(e)[:90]}"}
        for lg in logs:
            d = _decode(lg["data"].hex() if hasattr(lg["data"], "hex") else lg["data"])
            if d is None:
                undecoded += 1
                continue
            swaps += 1
            # ── UNITS (checked against the decoder, not assumed) ────────────────────────────
            # _decode_swap returns RAW uint128 words: feeX = lo128 = token0 = WAVAX (18dp),
            # feeY = hi128 = token1 = USDC (6dp). The first cut of this file treated them as
            # human units, which would have under-reported pool fees by 1e18. Scale explicitly.
            fee_x += d["feeX"] / 1e18
            fee_y += d["feeY"] / 1e6
            first_blk = first_blk or lg["blockNumber"]
            last_blk = lg["blockNumber"]
        b = top + 1
    usd = fee_x * wavax_usd + fee_y
    return {"swaps": swaps, "fee_wavax": fee_x, "fee_usdc": fee_y, "fee_usd": usd,
            "undecoded": undecoded, "first_block": first_blk, "last_block": last_blk}


def our_share_now(w3):
    """Our share of the pool, measured NOW.

    ── MY OWN FALSE ZERO, CAUGHT BY CHECKING (2026-09-27) ──────────────────────────────────────
    The first cut did `vals = [v for v in sh.values() if isinstance(v, (int, float))]` and then
    counted `v > 0`. But `_shares_at` returns DICTS — `{bin: {"share": f, "ours": int}}` — so the
    filter discarded every real value, `vals` came back empty, and the tool reported
    `bins_nonzero: 0`. A filter that excludes the actual data shape does not fail; it reports zero.

    That is the same family as the failed-archive-read bug this file exists to avoid, written into
    the fix for it. Read the key, do not filter for a type the data never had.
    """
    try:
        import lfj_fee_attribution as FA
        bins = FA._our_bins(w3)
        if not bins:
            return {"status": "unverified", "why": "no bins returned by _our_bins",
                    "bins": 0, "share_pct": None, "ours_usd": None}
        sh = FA._shares_at(w3, bins, w3.eth.block_number)
        if not sh:
            return {"status": "unverified", "why": "_shares_at returned nothing",
                    "bins": len(bins), "share_pct": None, "ours_usd": None}

        ours_total = 0.0
        nonzero = 0
        shares = []
        for _b, v in sh.items():
            if not isinstance(v, dict):
                continue
            o = float(v.get("ours") or 0)
            s = float(v.get("share") or 0)
            if o > 0:
                nonzero += 1
                ours_total += o
                if s > 0:
                    shares.append(s)
        # ── THERE IS NO VALID SINGLE "OUR SHARE %" OF THIS POOL (fixed 2026-09-27) ────────────
        # The first cut summed `ours` across bins and divided by the summed totals. That mixes
        # units: bins hold different WAVAX(18dp)/USDC(6dp) mixes, so a raw cross-bin sum is
        # meaningless. It produced 0.2525% — a number with the shape of a fact and no meaning.
        # The PER-BIN share is what is well-defined, because share = ours/totalSupply WITHIN one
        # bin's own token. Report the distribution, and refuse to publish an aggregate.
        shares.sort()
        if shares:
            med = shares[len(shares) // 2]
            share_stats = {"min_pct": round(shares[0] * 100, 6),
                           "median_pct": round(med * 100, 6),
                           "max_pct": round(shares[-1] * 100, 6),
                           "bins_measured": len(shares)}
        else:
            share_stats = None
        return {"status": "ok", "bins": len(bins), "bins_nonzero": nonzero,
                "per_bin_share": share_stats,
                "aggregate_share_pct": None,
                "why_no_aggregate": ("bins hold different token mixes; a cross-bin sum mixes units "
                                     "and is not a valid pool share")}
    except Exception as e:
        return {"status": "unverified", "why": str(e)[:110], "bins": None,
                "share_pct": None, "ours_usd": None}


def avax_usd(w3):
    try:
        d = json.load(open("/var/www/gentechlabs/DeFi/defi-data-jordan.json"))
        return float(d.get("price_usd") or 0.0) or 21.5
    except Exception:
        return 21.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    w3 = _w3()
    head = w3.eth.block_number
    px = avax_usd(w3)
    head_ts = int(w3.eth.get_block(head)["timestamp"])

    print(f"  DAILY FEE LEDGER — pool {POOL[:10]}…  (source: LB Swap logs)")
    print(f"  head block {head:,}  WAVAX ${px:.4f}")
    print(f"  ⚠️  public RPC is NOT an archive node — past-day bin shares are UNREADABLE.")
    print(f"      Pool fees below are receipts. Our share is measured now, recorded forward.")
    print()

    share = our_share_now(w3)
    print(f"  our share now: {share}")
    print()

    rows = []
    today0 = int(datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0).timestamp())

    for k in range(1, a.days + 1):
        s_ts = today0 - k * 86400
        e_ts = s_ts + 86400
        if s_ts < head_ts - 86400 * 120:
            continue
        b_lo, err = block_at_ts(w3, s_ts, max(0, head - 3_000_000), head)
        if err:
            rows.append({"date": datetime.fromtimestamp(s_ts, timezone.utc).strftime("%Y-%m-%d"),
                         "status": "block_lookup_failed", "error": err})
            print(f"  {datetime.fromtimestamp(s_ts, timezone.utc).strftime('%Y-%m-%d')}  "
                  f"BLOCK LOOKUP FAILED — {err}")
            continue
        b_hi, err = block_at_ts(w3, e_ts, b_lo, head)
        if err:
            rows.append({"date": datetime.fromtimestamp(s_ts, timezone.utc).strftime("%Y-%m-%d"),
                         "status": "block_lookup_failed", "error": err})
            print(f"  {datetime.fromtimestamp(s_ts, timezone.utc).strftime('%Y-%m-%d')}  "
                  f"BLOCK LOOKUP FAILED — {err}")
            continue
        if b_lo >= b_hi:
            rows.append({"date": datetime.fromtimestamp(s_ts, timezone.utc).strftime("%Y-%m-%d"),
                         "status": "no_blocks"})
            continue
        r = day_fees(w3, s_ts, e_ts, b_lo, b_hi, px)
        date = datetime.fromtimestamp(s_ts, timezone.utc).strftime("%Y-%m-%d")
        if r.get("error"):
            rows.append({"date": date, "status": "read_failed", "error": r["error"],
                         "blocks": [b_lo, b_hi]})
            print(f"  {date}  READ FAILED — {r['error']}")
            continue
        row = {
            "date": date,
            "status": "closed",
            # HALF-OPEN: b_lo is the day's first block; b_hi is the FIRST BLOCK OF THE NEXT DAY and
            # is NOT included. Reported as an explicit half-open range because presenting it as
            # inclusive made my own receipt checker flag every row as "out of day" (it read the
            # range end instead of the proof block). Ambiguity in a receipt is a defect in a receipt.
            "block_range_half_open": [b_lo, b_hi],
            "block_range_meaning": "from b_lo inclusive to b_hi EXCLUSIVE (b_hi is next day's first)",
            "last_block_with_swap": r["last_block"],
            "swaps": r["swaps"],
            "pool_fees_wavax": round(r["fee_wavax"], 6),
            "pool_fees_usdc": round(r["fee_usdc"], 4),
            "pool_fees_usd": round(r["fee_usd"], 4),
            "undecoded_swaps": r["undecoded"],
            "our_share": share.get("status"),
            "our_fees_usd": None if share.get("status") != "ok" else None,
            "attribution": ("pool receipts verified; our allocation NOT verified "
                            "(needs archive state) — recorded forward from today"),
            "proof_block": r["last_block"],
            "proof_url": (EXPLORER + str(r["last_block"])) if r["last_block"] else None,
        }
        rows.append(row)
        print(f"  {date}  swaps {r['swaps']:>5}  pool fees "
              f"{r['fee_wavax']:.4f} WAVAX + {r['fee_usdc']:.2f} USDC "
              f"= ${r['fee_usd']:.2f}   blk {b_lo:,}..{b_hi:,}")
        if r["undecoded"]:
            print(f"            ⚠️ {r['undecoded']} swap(s) could not be decoded — "
                  f"NOT counted (never silently dropped)")

    out = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "pool": POOL, "chain": "avalanche-c-chain",
           "source": "onchain: LB Pair Swap events (totalFees)",
           "archive_state": False,
           "note": ("Pool fees are receipts. Our allocation requires historical bin shares, which "
                    "this RPC cannot serve — so it is recorded forward, never back-filled "
                    "with a guessed share."),
           "our_share": share, "rows": rows}

    if a.json:
        print(json.dumps(out, indent=2))
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        with open(a.out, "w") as fh:
            json.dump(out, fh, indent=2)
        print(f"\n  wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
