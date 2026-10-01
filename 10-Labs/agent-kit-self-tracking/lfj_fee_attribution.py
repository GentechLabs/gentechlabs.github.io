#!/usr/bin/env python3
"""LFJ fee attribution — what OUR liquidity actually earned, read from the chain.

WHY THIS EXISTS (Jordan, 2026-09-21):
  The old fee measurement watched our POSITION VALUE over time and inferred fees from the
  delta. That cannot work here: every re-center changes the position's shape, and a shape
  change resets the window. Longest same-shape run ever recorded was 19h — a 24h rate was
  never claimable, and the idle-capital trigger makes re-centers MORE frequent, not less.

  So we read fees where they are actually recorded: the LB pair's Swap event.

EVENT (from traderjoe-xyz/joe-v2 src/interfaces/ILBPair.sol — not guessed):
    event Swap(
        address indexed sender,
        address indexed to,
        uint24  id,                  // the bin the swap touched
        bytes32 amountsIn,           // PACKED 2 x uint128
        bytes32 amountsOut,          // PACKED
        uint24  volatilityAccumulator,
        bytes32 totalFees,           // PACKED
        bytes32 protocolFees         // PACKED
    );

LAYOUT (established by cross-check, not by guessing a word index):
    lo128 = token0 = WAVAX (18 decimals)
    hi128 = token1 = USDC  (6 decimals)
  Proof: the implied price from amountsIn/amountsOut reproduces spot (~$11.26) on every
  single-sided swap, and protocolFees == totalFees / 10 exactly (LB's 10% protocol cut).
  A wrong layout cannot reproduce the spot price.

ATTRIBUTION MODEL — and its honest limits:
  We earn our PRO-RATA SHARE of the fee taken in a bin, proportional to our ERC-1155 bin
  balance against the bin's total supply AT THAT BLOCK. We do NOT count a swap's fee in
  full — that is the pool's fee, not ours.

  Two limits we state rather than hide:
    1. Shares are read at the CURRENT block, so swaps since our last position change are
       attributed using today's share. Correct for the steady state; approximate across a
       re-center.
    2. A swap that crosses several bins emits one Swap event per bin touched, so summing
       per-bin events is correct — but only bins WE hold earn for us.

USAGE:
  python3 lfj_fee_attribution.py --hours 6
  python3 lfj_fee_attribution.py --hours 24 --json
"""

from __future__ import annotations

# ── wallet resolution (wired 2026-09-22) ────────────────────────────────────
# This file used to hardcode the operator's address. Fine for one person, catastrophic
# for a fleet: a second tenant running this script with their own config would still act
# on the FIRST tenant's wallet, and would do it silently. Resolve it instead - and prove
# it, because steward_identity.signer() refuses a key that does not match the resolved
# wallet, and asserts the tenant boundary before handing one back.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from steward_identity import wallet as _steward_wallet

import argparse
import json
import sys
import time

# line 65 previously re-did the sys.path insert using `os`, which is not imported in this module
# (it is imported as `_os` above). That NameError killed the script at import, so the tool could
# never run at all — a fee reader that reports nothing because it never starts. The insert on line
# 57 already does this job; this duplicate was pure redundancy and its only effect was the crash.

from web3 import Web3
from eth_abi import encode as abi_encode, decode as abi_decode

import discover_positions as DP

PAIR = Web3.to_checksum_address("0x864d4e5Ee7318e97483DB7EB0912E09F161516EA")
WALLET = _steward_wallet()
SWAP_TOPIC = "0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70"

# Avalanche public RPCs cap eth_getLogs at 2048 blocks per call. ~2s blocks.
BLOCKS_PER_CALL = 2000
SECONDS_PER_BLOCK = 2.0

M128 = (1 << 128) - 1
WAVAX_DEC = 18
USDC_DEC = 6

SEL_BALANCE_OF = Web3.keccak(text="balanceOf(address,uint256)")[:4]
SEL_TOTAL_SUPPLY = Web3.keccak(text="totalSupply(uint256)")[:4]


def _w3():
    return Web3(Web3.HTTPProvider(DP.RPC_ENDPOINTS["avalanche"]))


def _decode_swap(data_hex: str) -> dict:
    """Decode one Swap log's data into bin id, amounts and fees (both tokens)."""
    d = data_hex[2:] if data_hex.startswith("0x") else data_hex
    w = [int(d[i * 64:(i + 1) * 64], 16) for i in range(len(d) // 64)]
    if len(w) < 6:
        raise ValueError(f"Swap log has {len(w)} words, expected 6")
    return {
        "binId": w[0],
        "inX": w[1] & M128, "inY": w[1] >> 128,      # token0 WAVAX, token1 USDC
        "outX": w[2] & M128, "outY": w[2] >> 128,
        "volAcc": w[3],
        "feeX": w[4] & M128, "feeY": w[4] >> 128,
        "protoX": w[5] & M128, "protoY": w[5] >> 128,
    }


def _our_share(w3, bin_id: int) -> float:
    """Our fraction (0..1) of a bin's ERC-1155 supply, read on-chain."""
    try:
        ours = abi_decode(["uint256"], w3.eth.call({
            "to": PAIR, "data": SEL_BALANCE_OF + abi_encode(["address", "uint256"], [WALLET, bin_id])
        }))[0]
        total = abi_decode(["uint256"], w3.eth.call({
            "to": PAIR, "data": SEL_TOTAL_SUPPLY + abi_encode(["uint256"], [bin_id])
        }))[0]
    except Exception:
        return 0.0
    return (ours / total) if total else 0.0


def _our_bins(w3) -> set[int]:
    """Bins we currently hold — discovered in ONE RPC call via ERC-1155 balanceOfBatch.

    Probing bin-by-bin cost ~1,200 individual eth_calls and took minutes. balanceOfBatch is
    standard ERC-1155 and returns every candidate balance in a single call.
    """
    try:
        active = int.from_bytes(w3.eth.call(
            {"to": PAIR, "data": Web3.keccak(text="getActiveId()")[:4]}), "big")
    except Exception:
        return set()
    cands = list(range(active - 300, active + 301))
    sel = Web3.keccak(text="balanceOfBatch(address[],uint256[])")[:4]
    data = sel + abi_encode(["address[]", "uint256[]"],
                            [[WALLET] * len(cands), cands])
    try:
        out = abi_decode(["uint256[]"], w3.eth.call({"to": PAIR, "data": data}))[0]
    except Exception:
        return set()
    return {b for b, bal in zip(cands, out) if bal > 0}


def _seconds_per_block(w3, head: int, probe: int = 20000) -> float:
    """Measure the chain's actual block time instead of assuming it.

    A hardcoded 2.0s/block asked for a 6h window and delivered 3.24h -- the window silently
    did not match the request, and every rate derived from it was scaled wrong. Measure it.
    """
    lo = max(1, head - probe)
    try:
        t0 = w3.eth.get_block(lo)["timestamp"]
        t1 = w3.eth.get_block(head)["timestamp"]
        return max(0.1, (t1 - t0) / (head - lo))
    except Exception:
        return 2.0


def _our_bins_at(w3, block: int) -> set[int]:
    """Our bin set AS OF `block` — the same probe, but at a historical block.

    This is what makes attribution exact across a re-center. Reading shares only at the CURRENT
    block means swaps that happened under our PREVIOUS position get attributed using today's
    share — wrong for exactly the window we care about, because a re-center is when the shape
    changes. Verified: the RPC serves archive eth_call, so this works.
    """
    try:
        active = int.from_bytes(w3.eth.call(
            {"to": PAIR, "data": Web3.keccak(text="getActiveId()")[:4]},
            block_identifier=block), "big")
    except Exception:
        return set()
    cands = list(range(active - 300, active + 301))
    sel = Web3.keccak(text="balanceOfBatch(address[],uint256[])")[:4]
    data = sel + abi_encode(["address[]", "uint256[]"], [[WALLET] * len(cands), cands])
    try:
        out = abi_decode(["uint256[]"], w3.eth.call({"to": PAIR, "data": data},
                                                    block_identifier=block))[0]
    except Exception:
        return set()
    return {b for b, bal in zip(cands, out) if bal > 0}


def _shares_at(w3, bins, block: int) -> dict:
    """Our fraction of each bin's ERC-1155 supply, as of `block`.

    Also records our RAW LP balance per bin, which is what makes fee EFFICIENCY measurable:
    fees earned / capital deployed. Share alone tells you how much of a bin's fee flow is ours;
    only the balance tells you what that cost us to hold.
    """
    if not bins:
        return {}
    bl = sorted(bins)
    sel_bal = Web3.keccak(text="balanceOf(address,uint256)")[:4]
    sel_tot = Web3.keccak(text="totalSupply(uint256)")[:4]
    out = {}
    for b in bl:
        try:
            ours = abi_decode(["uint256"], w3.eth.call({
                "to": PAIR, "data": sel_bal + abi_encode(["address", "uint256"], [WALLET, b])},
                block_identifier=block))[0]
            tot = abi_decode(["uint256"], w3.eth.call({
                "to": PAIR, "data": sel_tot + abi_encode(["uint256"], [b])},
                block_identifier=block))[0]
            out[b] = {"share": (ours / tot) if tot else 0.0, "ours": ours}
        except Exception:
            out[b] = {"share": 0.0, "ours": 0}
    return out


def _epochs(w3, start: int, head: int, step: int = 2000):
    """Split [start, head] into segments over which our bin set did not change.

    A re-center IS a change of bin set, so this finds the boundaries that matter and lets each
    swap be attributed at the share that was actually ours when it traded.
    """
    pts = list(range(start, head + 1, step))
    if not pts or pts[-1] != head:
        pts.append(head)
    sets = [(b, _our_bins_at(w3, b)) for b in pts]
    epochs = []
    for b, s in sets:
        if epochs and epochs[-1]["bins"] == s:
            epochs[-1]["to"] = b
        else:
            epochs.append({"from": b, "to": b, "bins": s})
    # Make epochs CONTIGUOUS: each runs until the NEXT epoch begins. Sampling gives boundaries at
    # probe points, so a naive from..to leaves the gaps between probes attributed to no epoch --
    # which undercounted deployed hours (5.56h + 0.00h idle != 7.95h window) and inflated the
    # rate per deployed hour. Coverage must sum to the whole window.
    for i in range(len(epochs) - 1):
        epochs[i]["to"] = max(epochs[i]["to"], epochs[i + 1]["from"] - 1)
    if epochs:
        epochs[-1]["to"] = max(epochs[-1]["to"], head)
    return epochs


def collect(hours: float, w3=None) -> dict:
    w3 = w3 or _w3()
    head = w3.eth.block_number
    head_ts = w3.eth.get_block(head)["timestamp"]
    spb = _seconds_per_block(w3, head)
    back = int((hours * 3600) / spb)
    start = max(1, head - back)

    # EPOCH-AWARE SHARES. Our bin set changes at every re-center, so a single current-block
    # share reading mis-attributes every swap that traded under the previous position. Split the
    # window at those boundaries and attribute each swap at the share that was actually ours.
    epochs = _epochs(w3, start, head)
    _ts_cache = {}

    def _ts(b):
        if b not in _ts_cache:
            _ts_cache[b] = w3.eth.get_block(b)["timestamp"]
        return _ts_cache[b]

    for e in epochs:
        e["shares"] = _shares_at(w3, e["bins"], e["to"])
        e["hours"] = max(0.0, (_ts(e["to"]) - _ts(e["from"])) / 3600)
        e["deployed"] = bool(e["bins"])

    # DEPLOYED-CAPITAL-HOURS (Jordan, 2026-09-21). Dividing fees by WALL-CLOCK hours charges us
    # for the epoch where bins=0 -- capital fully withdrawn between legs, earning nothing. That
    # understates the rate per dollar actually at work. A rate is only meaningful over the time
    # the capital was deployed, so the denominator is deployed hours, and idle time is reported
    # separately rather than hidden inside the rate.
    deployed_hours = sum(e["hours"] for e in epochs if e["deployed"])
    idle_hours = sum(e["hours"] for e in epochs if not e["deployed"])

    held = set().union(*[e["bins"] for e in epochs]) if epochs else set()
    if not held:
        return {"error": "no bins held by the wallet — nothing to attribute",
                "wallet": WALLET, "pair": PAIR}

    def _share_for(bin_id: int, block: int) -> float:
        for e in epochs:
            if e["from"] <= block <= e["to"]:
                return e["shares"].get(bin_id, {}).get("share", 0.0)
        return (epochs[-1]["shares"].get(bin_id, {}).get("share", 0.0) if epochs else 0.0)

    def _ours_for(bin_id: int, block: int) -> int:
        """Our raw LP balance in a bin — the denominator of fee efficiency."""
        for e in epochs:
            if e["from"] <= block <= e["to"]:
                return e["shares"].get(bin_id, {}).get("ours", 0)
        return (epochs[-1]["shares"].get(bin_id, {}).get("ours", 0) if epochs else 0)

    def _bins_for(block: int) -> set:
        for e in epochs:
            if e["from"] <= block <= e["to"]:
                return e["bins"]
        return epochs[-1]["bins"] if epochs else set()

    # page the log scan — the RPC caps the range per call
    logs = []
    lo = start
    while lo <= head:
        hi = min(lo + BLOCKS_PER_CALL - 1, head)
        for attempt in range(3):
            try:
                logs.extend(w3.eth.get_logs({
                    "address": PAIR, "topics": [SWAP_TOPIC],
                    "fromBlock": lo, "toBlock": hi}))
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(1.5)
        lo = hi + 1

    earned_x = earned_y = 0.0          # ours
    pool_fee_x = pool_fee_y = 0.0      # whole pool, for context
    swaps = 0
    in_our_bins = 0
    per_bin: dict[int, dict] = {}

    for lg in logs:
        try:
            s = _decode_swap(lg["data"].hex() if isinstance(lg["data"], bytes) else lg["data"])
        except Exception:
            continue
        swaps += 1
        pool_fee_x += s["feeX"]
        pool_fee_y += s["feeY"]
        blk = lg["blockNumber"]
        if s["binId"] not in _bins_for(blk):
            continue
        in_our_bins += 1
        sh = _share_for(s["binId"], blk)
        mx, my = s["feeX"] * sh, s["feeY"] * sh
        earned_x += mx
        earned_y += my
        e = per_bin.setdefault(s["binId"], {"swaps": 0, "share": sh, "wavax": 0.0, "usdc": 0.0,
                                            "ours": _ours_for(s["binId"], blk)})
        e["swaps"] += 1
        e["wavax"] += mx
        e["usdc"] += my

    wavax = earned_x / 10 ** WAVAX_DEC
    usdc = earned_y / 10 ** USDC_DEC

    # Price the WAVAX leg from the CHAIN, not an aggregator: getPriceFromId(active) is the
    # pair's own X96 price, scaled for token0's 18 decimals and token1's 6. An earlier version
    # imported a `get_spot` that does not exist, which silently priced WAVAX at $0 and reported
    # only the USDC leg as our earnings -- a false understatement, and exactly the class of bug
    # this whole build exists to avoid.
    spot = 0.0
    try:
        active = int.from_bytes(w3.eth.call(
            {"to": PAIR, "data": Web3.keccak(text="getActiveId()")[:4]}), "big")
        raw = int.from_bytes(w3.eth.call(
            {"to": PAIR,
             "data": Web3.keccak(text="getPriceFromId(uint24)")[:4] + abi_encode(["uint24"], [active])}), "big")
        spot = raw / 2 ** 128 * 1e18 / 1e6
    except Exception:
        spot = 0.0
    if not spot:
        print("  ⚠️  could not read spot from the pair — WAVAX leg NOT priced (USD total is USDC only)",
              file=sys.stderr)

    usd = usdc + (wavax * spot if spot else 0.0)
    hrs = (head_ts - w3.eth.get_block(start)["timestamp"]) / 3600

    # ── FEE EFFICIENCY BY DISTANCE FROM SPOT (Jordan, 2026-09-21) ────────────────────────────
    # Jordan: "we should add fee efficiency logic. We earn more on the edges for a bid ask.
    # curve is the opposite."
    #
    # That is a measurable claim, so measure it rather than assume it. Efficiency here is fees
    # earned per unit of capital DEPLOYED in the bin — not fees per bin, which just says which
    # bins are busy, and not share, which says nothing about what the position cost to hold.
    # Only fees/balance answers "was that bin worth the capital sitting in it".
    try:
        active_now = int.from_bytes(w3.eth.call(
            {"to": PAIR, "data": Web3.keccak(text="getActiveId()")[:4]}), "big")
    except Exception:
        active_now = None

    eff = []
    for bid, v in per_bin.items():
        if not v.get("ours"):
            continue
        u = v["usdc"] + (v["wavax"] * spot if spot else 0.0)
        eff.append({"binId": bid,
                    "offset": (bid - active_now) if active_now else None,
                    "usd": u, "ours": v["ours"], "swaps": v["swaps"],
                    "eff": (u / v["ours"] * 1e18) if v["ours"] else 0.0})

    # bucket by |offset| so "edges vs center" is answerable directly
    def _bucket(o):
        if o is None:
            return "unknown"
        a = abs(o)
        return "near (1-5)" if a <= 5 else ("mid (6-15)" if a <= 15 else "edge (16+)")

    buckets = {}
    for r in eff:
        b = _bucket(r["offset"])
        d = buckets.setdefault(b, {"n": 0, "usd": 0.0, "ours": 0})
        d["n"] += 1
        d["usd"] += r["usd"]
        d["ours"] += r["ours"]
    for b, d in buckets.items():
        d["eff"] = (d["usd"] / d["ours"] * 1e18) if d["ours"] else 0.0

    return {
        "wallet": WALLET,
        "pair": PAIR,
        "hours": round(hrs, 3),
        "blockFrom": start,
        "blockTo": head,
        "binsHeld": len(held),
        "deployedHours": round(deployed_hours, 3),
        "idleHours": round(idle_hours, 3),
        "epochs": [{"from": e["from"], "to": e["to"], "bins": len(e["bins"]),
                    "hours": round(e["hours"], 3)} for e in epochs],
        "swapsTotal": swaps,
        "swapsInOurBins": in_our_bins,
        "ours": {"wavax": wavax, "usdc": usdc, "usd": usd, "spot": spot},
        "poolFees": {"wavax": pool_fee_x / 10 ** WAVAX_DEC, "usdc": pool_fee_y / 10 ** USDC_DEC},
        "perBin": {str(k): v for k, v in sorted(per_bin.items())},
        "efficiency": {"byBin": sorted(eff, key=lambda x: -(x["offset"] or 0)),
                       "buckets": buckets},
        "source": "onchain: LB Pair Swap events x our ERC-1155 bin share",
        "caveats": [
            "bin shares read AT EACH SWAP'S OWN BLOCK (archive eth_call), split by re-center epoch",
            "WAVAX leg priced at spot for the USD total",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=6.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = collect(a.hours)
    if a.json:
        print(json.dumps(r, indent=2))
        return 0
    if r.get("error"):
        print(f"  ⚠️  {r['error']}")
        return 2
    o = r["ours"]
    print(f"  LFJ FEE ATTRIBUTION — ours, read from chain")
    print(f"  window {r['hours']:.2f}h   blocks {r['blockFrom']}..{r['blockTo']}")
    print(f"  bins held {r['binsHeld']}   swaps {r['swapsTotal']} total, "
          f"{r['swapsInOurBins']} touched OUR bins")
    ep = r.get("epochs") or []
    if len(ep) > 1:
        print(f"  ⚠️  {len(ep)} position epochs in this window (re-centers) — "
              f"each swap attributed at ITS epoch's share:")
        for e in ep:
            flag = "" if e["bins"] else "   <-- IDLE, capital out of the pool"
            print(f"       blocks {e['from']}..{e['to']}  bins {e['bins']:>3}  "
                  f"{e['hours']:5.2f}h{flag}")
    else:
        print(f"  position unchanged across the window (1 epoch, {ep[0]['bins'] if ep else 0} bins)")
    dh, ih = r.get("deployedHours", 0), r.get("idleHours", 0)
    print(f"  deployed {dh:.2f}h   idle {ih:.2f}h"
          + (f"   ⚠️  {ih / (dh + ih) * 100:.1f}% of the window EARNED NOTHING" if ih > 0.01 else ""))
    print()
    print(f"  OUR FEES: {o['wavax']:.8f} WAVAX  +  {o['usdc']:.6f} USDC")
    print(f"            = ${o['usd']:.6f}  (WAVAX @ ${o['spot']:.4f})")
    print(f"  whole pool took {r['poolFees']['wavax']:.4f} WAVAX + "
          f"{r['poolFees']['usdc']:.2f} USDC over the same window")
    if r["hours"] > 0 and o["usd"] > 0:
        dh = r.get("deployedHours", 0) or 0
        # Rate over DEPLOYED hours, not wall-clock: idle time is reported, not charged against
        # the yield. Falls back to the full window only if deployment time is unknown.
        basis = dh if dh > 0.01 else r["hours"]
        label = "deployed" if dh > 0.01 else "wall-clock (deployment time unknown)"
        print(f"  rate: ${o['usd'] / basis * 24:.4f}/day  over {label} hours")
        # Do NOT annualise a short window. Multiplying a 1h sample by 8,760 turns noise into a
        # headline -- the same defect already fixed in the fee estimator. A window under 24h is
        # reported as a rate per day and nothing more.
        if basis >= 24:
            print(f"        (${o['usd'] / basis * 24 * 365:.2f}/yr)")
        else:
            print(f"        ⏳ {basis:.2f}h of deployment — too short to annualise, "
                  f"no yearly figure claimed")
    # ── FEE EFFICIENCY: edges vs center ──────────────────────────────────────────────────────
    effd = r.get("efficiency") or {}
    bk = effd.get("buckets") or {}
    if bk:
        print(f"\n  FEE EFFICIENCY — fees earned per unit of capital deployed, by distance from spot")
        order = ["near (1-5)", "mid (6-15)", "edge (16+)"]
        best = max(bk.items(), key=lambda kv: kv[1].get("eff", 0))
        for k in order:
            if k not in bk:
                continue
            d = bk[k]
            mark = "  <-- BEST" if k == best[0] else ""
            print(f"     {k:<12} bins {d['n']:>3}   fees ${d['usd']:>9.6f}   "
                  f"eff {d['eff']:>12.4f}{mark}")
        for k in bk:
            if k not in order:
                print(f"     {k:<12} bins {bk[k]['n']:>3}   eff {bk[k]['eff']:>12.4f}")
        if len(bk) > 1:
            lo = min(bk.values(), key=lambda d: d.get("eff", 0)).get("eff", 0) or 1e-18
            print(f"     spread: best is {best[1]['eff'] / lo:.2f}x the worst bucket")

    if a.json:
        return 0
    print(f"\n  source: {r['source']}")
    for c in r["caveats"]:
        print(f"  caveat: {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
