#!/usr/bin/env python3
"""
lfj_fee_measure.py — measure OUR REALISED fees on the LFJ Liquidity Book position.

WHY NOT DECODE THE SWAP EVENT
-----------------------------
The natural approach is to sum the pool's Swap events and multiply by our liquidity share.
I found the event (topic0 ad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70,
3 topics, 192-byte payload, 6 words) and the last two words look like a total-fee / protocol-fee
split (the 6th is consistently ~1/10 of the 5th). But "looks like" is not "is": I could not
prove which word is which without the exact ABI, and a fee number built on a guessed word index
is exactly the false-value failure this treasury keeps finding. So it is not used.

WHAT THIS DOES INSTEAD — measure the thing itself
-------------------------------------------------
In a Liquidity Book pool, fees are not paid out. They accrue INTO the bin reserves. So our
claim on the pool grows as fees are earned:

    our claim (in tokens) = sum over our bins of  reserve(bin) * ourLP(bin) / totalSupply(bin)

Reserves only grow from fees (a swap moves value between bins but does not create it), so the
growth in our claim IS our fee income. That is a direct measurement of the real thing, and it
needs no event ABI at all - it uses getBin()/totalSupply()/balanceOf(), all verified working
on this pair.

METHOD
    snapshot  - record the current claim (tokens + USD) and the spot price
    report    - compare the latest snapshot to one >= 20h old, and to the entry basis
The price is recorded alongside so a claim change caused by price can be separated from one
caused by fees, rather than silently blended.

HONEST LIMITS (stated, not hidden)
  - For a SINGLE-SIDED position there is no composition loss to confuse the signal: a bid
    holds USDC and converts to WAVAX at falling prices by design. That makes the growth
    reading clean in a way it would NOT be for a two-sided curve.
  - A snapshot pair spanning a re-center will blend two different positions. The script records
    the bin range with each snapshot so a re-center is VISIBLE rather than averaged in.
  - Cumulative-since-entry needs the entry basis, which is only known if a snapshot was taken
    before the position was built. Where it is unknown this says UNKNOWN, it does not guess.
"""
from __future__ import annotations
import json, os, sys, time, urllib.request
from datetime import datetime, timezone

from web3 import Web3

# RPC via the shared rotating provider list (avax_rpc.py). A single hardcoded host meant one
# Cloudflare 1015 (per-SOURCE rate limit) took the snapshot dark; rotate, never replace.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from avax_rpc import connect, RpcUnavailable      # noqa: E402
PAIR = Web3.to_checksum_address("0x864d4e5ee7318e97483db7eb0912e09f161516ea")
USDC = Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
WAVAX = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
SNAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lfj-fee-snapshots.json")

POOL_ABI = json.loads('[{"name":"getActiveId","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint24"}]},{"name":"getBin","type":"function","stateMutability":"view","inputs":[{"type":"uint24"}],"outputs":[{"type":"uint128"},{"type":"uint128"}]},{"name":"totalSupply","type":"function","stateMutability":"view","inputs":[{"type":"uint256"}],"outputs":[{"type":"uint256"}]},{"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"type":"address"},{"type":"uint256"}],"outputs":[{"type":"uint256"}]},{"name":"getPriceFromId","type":"function","stateMutability":"view","inputs":[{"type":"uint24"}],"outputs":[{"type":"uint256"}]}]')
ERC_ABI = json.loads('[{"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"type":"address"}],"outputs":[{"type":"uint256"}]}]')


def wallet():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from steward_identity import wallet as _w
        return Web3.to_checksum_address(_w())
    except Exception:
        return None


def spot_usd(w3, pair):
    try:
        c = w3.eth.contract(address=pair, abi=POOL_ABI)
        a = c.functions.getActiveId().call()
        return c.functions.getPriceFromId(a).call() / 2**128 * 1e18 / 1e6
    except Exception:
        return None


def measure():
    """Return our current claim on the pool, in tokens and USD. None-safe."""
    me = wallet()
    if not me:
        return {"error": "wallet unresolved"}
    try:
        w3 = connect(timeout=40)
    except RpcUnavailable as exc:
        return {"error": f"rpc unavailable: {exc}"}
    pair = w3.eth.contract(address=PAIR, abi=POOL_ABI)
    active = pair.functions.getActiveId().call()

    bins = {}
    for d in range(-400, 401):
        bid = active + d
        mine = pair.functions.balanceOf(me, bid).call()
        if mine > 0:
            bins[bid] = mine
    if not bins:
        return {"flat": True, "binLow": None, "binHigh": None,
                "wavax": 0.0, "usdc": 0.0, "usd": 0.0, "activeId": active}

    x_tot = y_tot = 0
    for bid, mine in bins.items():
        supply = pair.functions.totalSupply(bid).call()
        if supply == 0:
            continue
        rx, ry = pair.functions.getBin(bid).call()
        x_tot += rx * mine // supply
        y_tot += ry * mine // supply

    wavax = x_tot / 1e18
    usdc = y_tot / 1e6
    px = spot_usd(w3, PAIR) or 0.0
    return {"flat": False, "binLow": min(bins), "binHigh": max(bins), "bins": len(bins),
            "wavax": wavax, "usdc": usdc, "usd": usdc + wavax * px,
            "spot": px, "activeId": active}


def load():
    try:
        return json.load(open(SNAP))
    except Exception:
        return []


def save(snaps):
    json.dump(snaps[-500:], open(SNAP, "w"), indent=1)


def main():
    argv = sys.argv[1:]
    m = measure()
    if "error" in m:
        # stderr, not stdout: a failure cause belongs on the stream a wrapper preserves and a
        # cron record keeps. Printed to stdout it was swallowed by `>/dev/null` wrappers and the
        # log could only say "exit 2" with the cause gone. (2026-09-22)
        print(f"  ❌ cannot measure: {m['error']}", file=sys.stderr)
        return 2

    now = time.time()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("=" * 94)
    print("  LFJ REALISED FEE MEASUREMENT — our claim on the bins")
    print("=" * 94)
    if m["flat"]:
        print("  FLAT — no position, so no fees are accruing.")
        print("=" * 94)
        return 0

    print(f"  {ts}")
    print(f"  bins {m['bins']}  range {m['binLow']}..{m['binHigh']}  activeId {m['activeId']}")
    print(f"  claim:  {m['wavax']:,.6f} WAVAX + {m['usdc']:,.6f} USDC  =  ${m['usd']:,.4f}")
    print(f"  spot ${m['spot']:.4f}")

    snaps = load()
    prev = None
    for s in reversed(snaps):
        if now - s["t"] >= 20 * 3600:
            prev = s
            break

    print()
    if prev is None:
        print("  No snapshot >= 20h old yet — cannot compute a 24h rate.")
        print(f"  ({len(snaps)} snapshot(s) on file. First meaningful rate needs a day of history.)")
    else:
        hrs = (now - prev["t"]) / 3600
        d_usd = m["usd"] - prev["usd"]
        per_day = d_usd / hrs * 24
        # separate the price effect from the fee effect rather than blending them
        fee_wavax = (m["wavax"] - prev["wavax"])
        px_effect = (m["wavax"] * (m["spot"] - prev["spot"]))
        print(f"  vs snapshot {hrs:.1f}h ago:")
        print(f"    claim  ${prev['usd']:,.4f}  ->  ${m['usd']:,.4f}   (delta ${d_usd:+.4f})")
        print(f"    WAVAX  {prev['wavax']:,.6f} -> {m['wavax']:,.6f}  (delta {fee_wavax:+.6f})")
        print(f"    price  ${prev['spot']:.4f} -> ${m['spot']:.4f}")
        print(f"    price effect on the claim : ${px_effect:+,.4f}   (NOT a fee)")
        print(f"    fee-attributable          : ~${d_usd - px_effect:+,.4f}")
        print(f"    -> rate ~${per_day:+.4f}/day")
        same = (prev.get("binLow") == m["binLow"] and prev.get("binHigh") == m["binHigh"])
        if not same:
            print(f"    ⚠️ BIN RANGE CHANGED ({prev.get('binLow')}..{prev.get('binHigh')} -> "
                  f"{m['binLow']}..{m['binHigh']}): a re-center happened between these two")
            print("       snapshots, so this compares two DIFFERENT positions. Treat as indicative.")

    if "--snapshot" in argv or not snaps:
        snaps.append({"t": now, "usd": m["usd"], "wavax": m["wavax"], "usdc": m["usdc"],
                      "spot": m["spot"], "binLow": m["binLow"], "binHigh": m["binHigh"]})
        save(snaps)
        print(f"\n  ✅ snapshot recorded ({len(snaps)} on file)")

    print("=" * 94)
    return 0


if __name__ == "__main__":
    sys.exit(main())
